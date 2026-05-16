# CI/CD Pipelines

## TL;DR

**CI/CD** is two distinct disciplines under one acronym. **CI** (Continuous Integration) means every change is merged frequently into a shared branch and automatically validated: lint, type check, unit tests, integration tests, build, security scan. **CD** is overloaded — it can mean **Continuous Delivery** (every green build produces a deployable artefact, deploy itself is one-click) or **Continuous Deployment** (every green build *is* deployed automatically). The pipeline that runs all of this is the **deployment pipeline**: a directed sequence of stages, each gating the next, run on every push by a **CI runner**. The standard for modern teams is **GitHub Actions** (or GitLab CI, Azure Pipelines, Jenkins, CircleCI, Argo Workflows for Kubernetes-native, Cloud Build / CodePipeline for cloud-tied) — they differ in syntax, not in the underlying pattern.

A canonical CI/CD pipeline for an ML service has roughly seven stages: **(1) check out code**, **(2) lint + format + type-check**, **(3) unit tests**, **(4) integration tests** (FastAPI `TestClient` + mocked dependencies), **(5) build the Docker image** (with cache reuse), **(6) scan the image** for CVEs + scan code for secrets, **(7) push the image** to a registry, **(8) deploy** to staging, **(9) run smoke tests** against staging, **(10) promote to production**. The first 7 are CI; the last 3 are CD. The transition from "CI green" to "production live" is where most teams park a manual approval gate, especially for ML where a new model version can change behaviour subtly.

**ML pipelines have concerns standard software CI/CD does not**: the model is part of the artefact and changes independently of code; the data version is part of the lineage; performance gates (AUC ≥ 0.85 on the frozen test set) are part of the pass/fail criteria; some models cost money to retrain or are too large for CI runners. The pragmatic split: **code CI** runs on every push (fast, no GPU, mocks the model); **model CI** runs on model-related changes or on a schedule (slow, can use GPU, runs full training + evaluation); **deploy CD** is gated on both, plus on the model registry stage. Tools that fit this pattern: GitHub Actions for code CI; Vertex / SageMaker / Kubeflow pipelines for model CI; Argo CD / Flux / Spinnaker for declarative GitOps-style deploys.

The **branch and release strategy** decides how changes flow to production. **GitHub Flow** (one long-lived `main`, feature branches, deploy from `main`) is the simplest and the default for most teams; it pairs with continuous deployment naturally. **GitFlow** (separate `develop`, `release/*`, `hotfix/*` branches) is heavier and suits teams with formal release windows. **Trunk-based development** (everyone commits to `main` daily, short-lived branches if any) requires high test coverage but unlocks the fastest deployment cadence. For ML, the choice tracks the model retraining cadence: trunk-based suits L2 maturity; GitHub Flow is the right default for L1; GitFlow appears in regulated environments with mandatory release approvals.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **CI** | Continuous Integration | Frequent merge + automated validation |
| **Continuous Delivery** | Every green build is releasable | Manual approval to actually ship |
| **Continuous Deployment** | Every green build is shipped | No manual approval |
| **Pipeline** | Sequence of stages run automatically | YAML in the repo |
| **Stage / job / step** | Pipeline subdivisions | Stage = phase; job = parallelisable unit; step = atomic command |
| **Runner** | The machine executing the pipeline | GitHub-hosted, self-hosted, K8s-based |
| **Artifact** | Output of a stage, consumed by later ones | Built image, test report, coverage XML |
| **Cache** | Persistent storage across runs | pip wheels, Docker layers, node_modules |
| **Matrix** | Run the same job in N variants | `python: [3.10, 3.11, 3.12]` |
| **Gate** | Conditional that must pass to proceed | Tests, scans, approvals |
| **Trigger** | What starts the pipeline | Push, PR, schedule, tag, manual |
| **Environment** | Named deploy target with secrets and rules | `staging`, `production` |
| **Reusable workflow** | A workflow called by other workflows | DRY across many services |
| **GitHub Flow** | One main + feature branches + deploy from main | Default for most teams |
| **GitFlow** | develop + release + hotfix branches | Formal release model |
| **Trunk-based dev** | Everyone on main, very short branches | High-cadence teams |
| **Blue-green deploy** | Two environments, switch traffic atomically | Fast rollback, costlier |
| **Canary deploy** | Send small % of traffic to new version | Catch regressions on a fraction |
| **Rolling deploy** | Replace instances gradually | Default Kubernetes pattern |
| **Feature flag** | Toggle code paths without deploying | Decouples deploy from release |

---

## What CI/CD buys you

> The cost is real (pipeline maintenance, runner minutes, CI debugging). The payback is in not shipping broken software.

Without CI:
- "Works on my machine" is the modal failure mode.
- Regressions caught by users in production.
- Merging feels risky, so it happens rarely, so conflicts accumulate.

With CI:
- Every change is validated before merge.
- The quality gate is in code, not in convention.
- Merges happen often because they are cheap.

Without CD:
- Deploys are events, planned, with humans involved.
- Releases bundle many changes, so when one breaks, all are suspect.
- Rollback is harder because state-since-last-release has drifted.

With CD:
- Deploys are routine, frequent, small.
- Bisecting a regression is easier (each change shipped alone).
- Rollback is "redeploy the previous image", routine.

The deeper benefit: **the deployment pipeline becomes the place where engineering standards are enforced**. Test coverage, type safety, security scans, performance benchmarks — anything you put in a gate is what the team actually does.

---

## Anatomy of a pipeline

> Roughly the same shape across tools. Names differ, primitives don't.

```
   git push
        │
        ▼
   ┌──────────────────┐
   │   Trigger        │   on: push to main / PR / tag / schedule
   └──────────────────┘
        │
        ▼
   ┌──────────────────┐
   │   Checkout       │   git clone of the repo
   └──────────────────┘
        │
        ▼
   ┌──────────────────┐
   │   Setup          │   Python, deps cache restore
   └──────────────────┘
        │
        ▼
   ┌──────────────────┐
   │   Lint + Format  │   ruff check, ruff format --check
   └──────────────────┘
        │
        ▼
   ┌──────────────────┐
   │   Type-check     │   mypy
   └──────────────────┘
        │
        ▼
   ┌──────────────────┐
   │   Test (unit)    │   pytest -m "not slow"
   └──────────────────┘
        │
        ▼
   ┌──────────────────┐
   │   Test (integ.)  │   pytest -m integration
   └──────────────────┘
        │
        ▼
   ┌──────────────────┐
   │   Build image    │   docker buildx build with cache
   └──────────────────┘
        │
        ▼
   ┌──────────────────┐
   │   Scan           │   trivy image + gitleaks
   └──────────────────┘
        │
        ▼
   ┌──────────────────┐
   │   Push           │   docker push to registry
   └──────────────────┘
        │
        ▼
   ┌──────────────────┐
   │   Deploy staging │   kubectl apply / terraform apply
   └──────────────────┘
        │
        ▼
   ┌──────────────────┐
   │   Smoke test     │   curl /health and /predict
   └──────────────────┘
        │
        ▼
   ┌──────────────────┐
   │   Approval gate  │   manual or automated
   └──────────────────┘
        │
        ▼
   ┌──────────────────┐
   │   Deploy prod    │   same artefact, different env
   └──────────────────┘
```

Stages can run in parallel where they don't depend on each other (e.g., lint and unit tests). The runner orchestrates that.

---

## GitHub Actions: the modern default

> Workflows in `.github/workflows/*.yml`. Triggered by events. Each job runs in a fresh runner.

### A minimal workflow

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip
      - run: pip install -r requirements.lock.txt
      - run: ruff check src tests
      - run: ruff format --check src tests
      - run: mypy src
      - run: pytest --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v4
        with:
          file: coverage.xml
```

What's happening:
- `on:` declares triggers. Both pushes to `main` and any PR run the workflow.
- `runs-on:` specifies the runner OS.
- Steps run sequentially in the runner's working directory.
- `actions/setup-python@v5` includes caching for pip.
- Each `run:` is a shell command.

### Adding a Docker build

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    needs: test                            # only if tests pass
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/myorg/myapp
          tags: |
            type=ref,event=branch
            type=sha,prefix=sha-
            type=semver,pattern={{version}}
      - uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

What's new:
- `needs: test` makes this job wait for the test job.
- Login to GHCR using the auto-provisioned `GITHUB_TOKEN`.
- `metadata-action` generates sensible tags from the git ref.
- `build-push-action` builds with BuildKit, caches layers in GitHub Actions cache, pushes.

### Image scan + secret scan

```yaml
  scan:
    runs-on: ubuntu-latest
    needs: build
    steps:
      - uses: actions/checkout@v4
      - name: Run Trivy on image
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ghcr.io/myorg/myapp:sha-${{ github.sha }}
          severity: CRITICAL,HIGH
          exit-code: 1
      - name: Gitleaks (secret scan)
        uses: gitleaks/gitleaks-action@v2
```

### Deploy job with environment

```yaml
  deploy-staging:
    runs-on: ubuntu-latest
    needs: scan
    environment:
      name: staging
      url: https://staging.api.example.com
    steps:
      - run: echo "Deploy to staging…"
      # kubectl / helm / terraform / cloud-run / ECS update goes here

  deploy-prod:
    runs-on: ubuntu-latest
    needs: deploy-staging
    environment:
      name: production           # has required reviewers configured in repo settings
    steps:
      - run: echo "Deploy to prod…"
```

The **environment** is a GitHub concept that adds gates: required reviewers, wait timers, branch restrictions, environment-specific secrets. It's the right place to put the human approval before production.

### Reusable workflows

For many services with the same pattern:

```yaml
# .github/workflows/python-ci.yml (reusable)
on:
  workflow_call:
    inputs:
      python-version:
        type: string
        default: "3.11"

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ inputs.python-version }}
      - run: pip install -r requirements.lock.txt
      - run: pytest
```

```yaml
# In a service repo
jobs:
  ci:
    uses: myorg/.github/.github/workflows/python-ci.yml@main
    with:
      python-version: "3.12"
```

This is how a platform team enforces "every service uses our standard pipeline" without copy-paste sprawl.

---

## Branching and release strategies

### GitHub Flow

```
main ────────────────────────────────────────────►
   ├── feature/x  ──►   PR ──►   merge
   └── feature/y  ──►   PR ──►   merge
```

- One long-lived `main`.
- Feature branches off `main`, PR back into `main`.
- Deploy from `main`.

Best for: most teams, especially with CD. The simplest workflow that works.

### GitFlow

```
main ──────────────────────────────────────────► (production)
develop ───────────────────────────────────────► (integration)
  ├── feature/x ──► develop
  ├── release/1.2 ──► main + develop
  └── hotfix/bug ──► main + develop
```

- `develop` is the integration branch.
- `release/*` for stabilising before production.
- `hotfix/*` for emergency fixes off `main`.

Best for: regulated environments, formal release windows, multiple released versions to support. Heavier than most teams need.

### Trunk-based development

- Everyone commits to `main` daily (or branches for at most a day).
- Feature flags decouple deploy from release.
- Requires high test coverage to keep `main` always green.

Best for: high-cadence teams, large monorepos, mature CI.

### Picking the right one

| Question | Pointing to |
|---|---|
| How many environments / versions in support? | Many → GitFlow. One → GitHub Flow or trunk-based. |
| Are deploys events or routine? | Events → GitFlow. Routine → trunk-based. |
| Test coverage and confidence in CI? | High → trunk-based. Moderate → GitHub Flow. Low → fix that first. |
| Regulated environment with manual gates? | GitFlow or GitHub Flow with environment approvals. |

---

## Deploy strategies

> The risk-versus-cost dial.

| Strategy | What | When |
|---|---|---|
| **Recreate** | Stop old, start new | Dev / non-critical, very fast |
| **Rolling** | Replace instances one at a time | Default for Kubernetes; mild risk on partial state |
| **Blue-green** | Two environments, switch the router | Fast rollback, doubles infra cost during cutover |
| **Canary** | Route a small % of traffic to new | Catch regressions on a fraction of users; needs metrics |
| **Shadow** | Mirror real traffic to new without affecting users | Safe latency / correctness validation; needs idempotent calls |
| **Feature-flagged** | Deploy code dark, enable for cohorts | Decouples deploy from release |

For ML services, canary + shadow is the gold standard for a new model version: shadow first (verify it produces sensible outputs), then canary (verify production metrics), then ramp.

---

## ML-specific CI/CD

> Two pipelines, not one. Code ships fast; models ship gated.

### The split

| Pipeline | Triggered by | Runs | Pass criteria |
|---|---|---|---|
| **Code CI** | Push to any branch / PR | Lint, type, unit, integration with mocked model | Standard software quality gates |
| **Model CI** | Push to model code / data / on schedule | Training, evaluation, registry push to Staging | Performance thresholds on frozen evaluation set + slice tests + drift checks |
| **Deploy CD** | New image OR new model Production stage | Build, scan, push image, deploy with new model | Smoke tests on staging, approval gate, prod deploy |

The deploy pipeline pulls **both** the image and the model registry version; either can roll forward independently.

### Performance gates in CI

The test from `05_testing_strategy.md`:

```python
def test_holdout_auc_meets_minimum(model):
    auc = roc_auc_score(y_holdout, model.predict_proba(X_holdout)[:, 1])
    assert auc >= 0.85
```

Wire it as a gate in the model CI workflow. The job fails if the metric drops; the registry transition is blocked until a human looks.

### Model registry transitions in CI

```yaml
- name: Promote model
  if: success()
  run: |
    python scripts/promote.py \
      --name my-recommender \
      --version ${{ steps.train.outputs.version }} \
      --stage Production
```

`promote.py` calls the registry API. The promotion is itself an artefact of the pipeline run, audit-trail-friendly.

### Data versioning in CI

DVC integrates with GitHub Actions via `iterative/setup-dvc`:

```yaml
- uses: iterative/setup-dvc@v1
- run: dvc pull data/train.csv
```

The data version pulled is the one tied to the current commit's `.dvc` files.

### GPU runners

GitHub-hosted runners have no GPU. Options:
- **Self-hosted runners** on a GPU machine (you manage it).
- **Cloud Build / Vertex / SageMaker Pipelines** for the model CI, triggered from GitHub Actions.
- **Hosted GPU runners** (GitHub now offers Linux x64 GPU runners on Enterprise tiers; CircleCI and others have always had them).

For most teams the right pattern is: GitHub Actions runs the orchestration; the heavy training step is offloaded to the cloud's ML pipeline service.

---

## Caches that actually matter

| Cache | What |
|---|---|
| **pip / wheel cache** | Avoid re-downloading and re-resolving deps. `actions/setup-python` does it from the lockfile hash. |
| **Docker layer cache** (GHA cache, registry cache, or `--cache-from`) | Massive wins on rebuilds when deps haven't changed |
| **pytest cache** | Skip re-running tests that haven't changed (`pytest --cache-show`) |
| **mypy cache** | Avoid re-checking unchanged files |

The first two are the highest-value. Wiring them correctly cuts pipeline times from 10 minutes to 2.

---

## Secrets in CI

> Secrets live in the CI provider's secret store, never in the workflow file.

### GitHub Actions secrets

```yaml
- name: Login to AWS
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789012:role/github-actions
    aws-region: eu-west-1
```

For AWS / GCP / Azure, the modern pattern is **OIDC federation**: GitHub Actions presents a signed OIDC token, the cloud verifies it, exchanges it for short-lived credentials. No long-lived keys stored in GitHub. Standard for any new setup.

### Environment-scoped secrets

```yaml
jobs:
  deploy-prod:
    environment: production    # production environment's secrets are available here
```

`production` environment has its own secret values (different from `staging`), and reviewer requirements. The same workflow file safely promotes through environments.

### Never

- Print a secret to the log (`echo ${{ secrets.MY_SECRET }}` is masked but `aws sts get-caller-identity` and inspect responses isn't).
- Pass secrets via the URL (logs, history).
- Commit `.env` files; install `gitleaks` as a pre-commit hook.

---

## Common patterns

| Pattern | Notes |
|---|---|
| **PR preview environments** | Deploy each PR to a temporary URL for visual review |
| **Required status checks** on `main` | The PR cannot merge unless CI is green |
| **Required reviews** on `main` | Code review is enforced, not customary |
| **Conventional Commits + semantic-release** | Commit format drives automatic versioning and changelogs |
| **Mergify / GitHub Auto-merge** | Merge PRs automatically once gates pass |
| **Bot-driven dependency updates** (Dependabot, Renovate) | Keep deps current; tests gate the updates |
| **Test impact analysis** | Run only tests affected by the diff (large monorepos) |
| **Scheduled nightly jobs** | Run slow tests, refresh model evaluations, prune stale branches |
| **Workflow concurrency control** | `concurrency:` cancels superseded runs on the same PR |

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Pipeline takes too long, team disables on PRs | Quality decay | Cache, parallelise, split fast and slow tiers |
| `latest` tag deployed to prod | Different deploys point to different bytes | Pin by SHA or digest in deploy config |
| Same secrets across all environments | Compromise of staging key is also a prod compromise | Environment-scoped secrets |
| Long-lived cloud keys in GitHub | Rotation forgotten, key leaks | OIDC federation to AWS/GCP/Azure |
| Tests rely on network or order | Flaky failures | Isolate, mock external calls in unit tier |
| CI runs forever on a stuck step | Burned runner minutes | Set `timeout-minutes` on every job |
| `actions/checkout@main` (unpinned) | Supply-chain risk | Pin actions to a tag or SHA |
| Docker image rebuilt from scratch every run | 10-minute pipelines | Layer cache via GHA cache or registry cache |
| Production deploys triggered on every push | Half-tested code in prod | Gate on the `production` environment with reviewers |
| Skipping hooks with `--no-verify` | Pre-commit hooks bypassed, broken code lands | Hard policy: never `--no-verify`; CI catches it anyway |
| ML performance test always passing | Threshold set lower than current model | Set thresholds at "current minus a small margin"; review on retraining |
| Pipeline writes to shared state without locking | Concurrent runs corrupt the model registry | Concurrency control; idempotent operations |
| Deploy job uses kubectl with admin token | Blast radius too large | Service account with namespace-scoped RBAC |
| No rollback tested | First time you try, it doesn't work | Practice rollbacks; have them in runbooks |

---

## When to use what

| Need | Pick | Why |
|---|---|---|
| CI for a GitHub repo | **GitHub Actions** | Native, generous free tier, ecosystem |
| CI for GitLab | **GitLab CI** | Native |
| Multi-language enterprise | **Jenkins**, **Azure DevOps**, **TeamCity** | When mandated; otherwise overkill |
| Kubernetes-native CI | **Argo Workflows**, **Tekton** | Pipelines as K8s resources |
| Cloud-tied | **CodePipeline + CodeBuild** (AWS), **Cloud Build** (GCP), **Azure Pipelines** | When the org is single-cloud and the rest of the stack is there |
| GitOps deploy | **Argo CD**, **Flux** | Manifests in Git as source of truth; cluster reconciles |
| Release management | **GitFlow** | Heavy, formal |
| Default flow | **GitHub Flow** | Simplest viable |
| High-cadence | **Trunk-based** | Demands the test discipline to match |
| Container scan | **Trivy** | Open source, fast, default |
| Secret scan | **gitleaks** | Same |
| Dep update bot | **Renovate** (more configurable) or **Dependabot** (native) | Either; pick one |
| OIDC to cloud | **Native OIDC federation** (`aws-actions/configure-aws-credentials`, `google-github-actions/auth`) | Replace long-lived keys |
| ML pipeline trigger | GitHub Action triggers **Vertex / SageMaker / Kubeflow** pipeline | CI orchestrates, ML pipeline executes |

---

## See also

### Other notes
- [01_mlops_foundations.md](01_mlops_foundations.md) — the maturity model that CI/CD operationalises
- [05_testing_strategy.md](05_testing_strategy.md) — the gates that run in CI
- [06_api_security_and_authentication.md](06_api_security_and_authentication.md) — secret scanning and dependency vulnerabilities in CI
- [07_containerization_with_docker.md](07_containerization_with_docker.md) — the build and push that CI automates
- [09_production_deployment_monitoring_orchestration.md](09_production_deployment_monitoring_orchestration.md) — what CD ultimately hands off to

### Cross-module
- Module 04 [07_project_management_methodologies.md](../../04_business_case_AIPM/notes/07_project_management_methodologies.md) — release cadence and the trade-offs between waterfall, agile, and trunk-based shipping
- Module 05 [02_aws_ai_ml_stack.md](../../05_AI_cloud_services/notes/02_aws_ai_ml_stack.md) — managed pipeline runners (SageMaker Pipelines) and how they integrate with GitHub Actions
