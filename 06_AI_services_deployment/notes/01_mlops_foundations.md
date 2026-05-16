# MLOps Foundations

## TL;DR

MLOps is the discipline of running ML systems in production. It exists because the workflow that ships software does not work for models: a model's behaviour depends on *data* as much as on code, training drifts over time, the codebase is multi-language (Python notebook + serving container + infra YAML), and the artefact (`.pkl`, `.pt`, `.onnx`) is not the source of truth. The source of truth is the **(data, code, hyperparameters)** tuple. MLOps borrows DevOps primitives (version control, CI/CD, monitoring) and extends them with three ML-specific concerns: **data versioning** (the dataset is part of the artefact and silently changes when the source system changes), **model versioning and registry** (trained weights need provenance, lineage and approval workflows), and **drift monitoring** (the model degrades when the live data distribution shifts away from the training distribution).

The **MLOps maturity model** (Google / Microsoft framing) ranks teams on three levels. **L0** is a notebook a person runs by hand and a model that gets emailed around — fragile, irreproducible, the default for early-stage teams. **L1** introduces an automated ML pipeline (training, evaluation, deployment) with data and model registry as first-class citizens — the productive plateau for most teams. **L2** adds CI/CD on the pipeline itself: every change to the code, data, or feature pipeline triggers automated retraining and deployment — the rare configuration for high-frequency retraining workloads (recommendation systems, fraud detection, ad ranking). Climbing the levels costs engineering time; the right level is the one that matches the *retraining cadence* and the *blast radius* of a bad model, not what looks impressive.

The **ML engineer / data scientist split** is institutional, not skill-based. The data scientist owns the model (feature engineering, training, evaluation, model card). The ML engineer owns the *system around the model* (data pipelines, serving infrastructure, monitoring, retraining triggers). The handoff is the model artefact plus the metadata needed to reproduce it. In small teams a single person wears both hats; in scaled organisations the split formalises and the friction concentrates at the handoff — the **model registry** (MLflow, SageMaker Model Registry, Vertex Model Registry, Weights & Biases) is the standard interface for managing it.

The **MLOps toolchain** is layered: Python + Jupyter for experimentation; Git + GitHub + **Codespaces** for code collaboration and reproducible dev environments; **Hugging Face** as the de facto registry for open-source models, datasets and Spaces; Docker for shipping the runtime; GitHub Actions for CI/CD; MLflow / W&B for experiment tracking; FastAPI / Flask for serving; Prometheus / Grafana for monitoring; Airflow / Prefect for orchestration. The trap is using an L2 stack at L0 (overengineering) or running L2 workloads on L0 tooling (silent risk): the maturity of the tooling must match the maturity of the team and the criticality of the workload.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **MLOps** | DevOps + data + model lifecycle management | The team that "runs the model in prod", not the one that trains it |
| **Reproducibility envelope** | The (data, code, hyperparameters) needed to recreate a model | If you cannot point to all three, the model is not reproducible |
| **Model artefact** | The serialised trained weights + metadata | `.pkl`, `.pt`, `.onnx`, `.safetensors` |
| **Model registry** | Versioned catalogue with promotion workflow | MLflow, SageMaker MR, Vertex MR, W&B |
| **Data versioning** | Tracking dataset versions like code commits | DVC, lakeFS, Delta Lake |
| **Drift** | The live data distribution moves away from the training one | Accuracy drops without code changes |
| **MLOps L0** | Manual, notebook-driven | "Send me the .pkl on Slack" |
| **MLOps L1** | Automated training/deployment pipeline | A pipeline triggers retraining, registry is canonical |
| **MLOps L2** | CI/CD on the pipeline itself | Every code/data change runs an automated retrain+deploy |
| **Data scientist** | Owns the model | Feature engineering, evaluation, model card |
| **ML engineer** | Owns the system around the model | Pipelines, serving, monitoring, retraining |
| **Codespaces** | GitHub-hosted dev environment from a `.devcontainer` | Reproducible developer environment, one click |
| **Hugging Face Hub** | The "GitHub of models" | Pretrained weights, datasets, Spaces (live demos) |
| **HF Spaces** | Hosted apps backed by HF infra | Quick demos, Gradio/Streamlit, free CPU tier |
| **Experiment tracking** | Logging runs, metrics, params, artefacts | MLflow, W&B, Neptune |

---

## Why MLOps exists

> Shipping a model is not shipping software. The artefact you put in production is the *output* of a stochastic process running over data you do not fully control.

A traditional software change is deterministic: same code + same inputs → same outputs. A model change is probabilistic and has at least three moving parts you must version together to reproduce it:

1. **Code** — the training script, preprocessing, model definition.
2. **Data** — the exact dataset version used for training and evaluation.
3. **Configuration** — hyperparameters, random seeds, environment versions (Python, CUDA, libraries).

If any of the three drifts, the artefact you ship is no longer the artefact you tested. The classic incident is "the model passed offline evaluation last month but is now broken in prod"; nine times out of ten the cause is a change in the upstream data, not the code.

**Three failure modes** DevOps does not handle out of the box:

| Failure mode | What happens | What MLOps adds |
|---|---|---|
| **Training–serving skew** | Features computed differently at training and inference | Shared feature pipeline, feature store, contract tests |
| **Concept drift** | The relationship between input and output changes (e.g., user behaviour shifts) | Drift monitors on predictions/labels, automated retrain triggers |
| **Data drift** | The input distribution changes (e.g., a new source system emits different values) | Drift monitors on input features, alerting before the model accuracy drops |

The cost of *not* doing MLOps is paid in incidents and silent degradation. The cost of doing it is paid in engineering time.

---

## The MLOps maturity model

> Three levels, originally a Google whitepaper, popularised by Microsoft. They describe what is automated and where the boundary between humans and machines sits.

### Level 0 — Manual process

```
Data scientist              ML engineer / nobody
─────────────              ────────────────────
   notebook ─── .pkl ───►  copies into a repo
                          ▼
                          wraps in Flask
                          ▼
                          deploys by hand to a VM
```

What is true at L0:
- The training step is a notebook that someone runs by hand.
- The model is handed off as a file (often over chat).
- There is no automated retraining.
- Monitoring, if it exists, is on infrastructure (CPU, memory) not on the model.
- "Reproducibility" depends on whether the notebook author still works there.

L0 is fine for **exploration** and **single-shot models** that do not need to be retrained. It is a problem the moment the model needs to be updated or audited.

### Level 1 — ML pipeline automation

```
   Git commit
       │
       ▼
   Trigger: scheduled / event-driven
       │
       ▼
   Feature pipeline ── data versioning ──┐
       │                                 │
       ▼                                 │
   Training job ── experiment tracking ──┤
       │                                 │
       ▼                                 │
   Model evaluation                      │
       │                                 │
       ▼                                 │
   Model Registry  ◄─────────────────────┘
       │
       ▼
   Deployment (canary / shadow / blue-green)
       │
       ▼
   Monitoring (latency, drift, quality)
```

What changes at L1:
- The pipeline is **defined declaratively** (Airflow, Prefect, Kubeflow, Vertex Pipelines, SageMaker Pipelines).
- The **model registry** is the canonical place models exist; deployments pull from it.
- **Data versioning** is enforced (DVC, lakeFS, or the cloud provider's equivalent).
- **Experiment tracking** records every run.
- **Retraining is triggered** (schedule, drift alarm, data arrival) and runs without humans in the loop.

L1 is the productive plateau for **most** production ML systems. It buys you reproducibility, automated retraining, and a clean rollback path. The cost is real but bounded.

### Level 2 — CI/CD pipeline automation

L2 puts **the pipeline itself** under CI/CD. A change to the feature pipeline, the training code, or the dataset triggers automated build, test, and deployment of the *pipeline*, which then trains, evaluates, registers, and deploys the model.

When L2 is worth the cost:
- The **retraining cadence is high** (daily or sub-daily) and humans cannot keep up.
- The **business cost of a stale model is high** (recommendation systems, fraud detection, ad ranking).
- The **team is large enough** to maintain the infrastructure (typically a dedicated MLOps platform team).

When L2 is overengineering:
- Models are retrained quarterly or less.
- The team is fewer than ~5 ML engineers total.
- Audit and compliance demand human approval gates anyway.

---

## ML engineer vs data scientist

> Same toolchain, different responsibilities. The split is institutional, and the artefact handed off is the contract.

| Dimension | Data Scientist | ML Engineer |
|---|---|---|
| **Goal** | Maximise model quality on the business metric | Make the model run reliably in production |
| **Owns** | Feature engineering, training code, evaluation | Data pipelines, serving infrastructure, monitoring, retraining triggers |
| **Output** | Trained model + evaluation report + model card | Live endpoint + observability + on-call runbook |
| **Tools** | Pandas, scikit-learn, PyTorch / TF, Jupyter, MLflow | Docker, Kubernetes, Airflow / Prefect, FastAPI, Prometheus, Terraform |
| **Mindset** | Statistical, experimental | Systems, reliability |

The **handoff** is the model artefact plus the metadata the engineer needs to reproduce, deploy, and monitor it:
- Serialised model file (`.pkl`, `.pt`, `.onnx`).
- Inference signature: input/output schema (Pydantic-friendly).
- Preprocessing code (same code path as training).
- Evaluation metrics on the held-out set.
- Resource requirements: CPU/GPU, RAM, expected latency, expected throughput.

The **model registry** is the right place to attach all of the above to the artefact, so the handoff happens through a stable interface rather than a Slack message.

In small teams (≤5 people) one person typically does both. The split formalises around 10-20 ML people. At scale (50+) the ML engineer role splits further into *ML platform engineer* (builds the MLOps platform) and *ML production engineer* (operates models on it).

---

## The MLOps toolchain

> Layered, swappable, and chosen to match the maturity level. There is no canonical stack.

### The layers

| Layer | What it does | Open source default | Managed cloud default |
|---|---|---|---|
| **Experimentation** | Notebooks, EDA, prototypes | Jupyter / VS Code | Vertex Workbench, SageMaker Studio, Azure ML Studio |
| **Source control** | Code versioning, collaboration | Git + GitHub / GitLab | Same |
| **Dev environments** | Reproducible developer setup | Docker, `.devcontainer`, Codespaces | Same |
| **Data versioning** | Track dataset versions | DVC, lakeFS, Delta Lake | LakeFS-on-S3, Delta on Databricks |
| **Experiment tracking** | Log runs, metrics, params | MLflow, W&B (free tier) | Vertex Experiments, SageMaker Experiments |
| **Pipeline orchestration** | Schedule and run the training pipeline | Airflow, Prefect, Dagster, Kubeflow | Vertex Pipelines, SageMaker Pipelines, Azure ML Pipelines |
| **Model registry** | Versioned model catalogue | MLflow Registry, HF Hub | Vertex Model Registry, SageMaker Model Registry |
| **Serving** | Expose the model as an API | FastAPI, Flask, TorchServe, BentoML, Triton | Vertex Endpoints, SageMaker Endpoints, Azure ML Endpoints |
| **Containerisation** | Package the runtime | Docker | Same |
| **CI/CD** | Build, test, deploy on change | GitHub Actions, GitLab CI | Cloud Build, CodePipeline, Azure DevOps |
| **Monitoring** | Latency, errors, drift, quality | Prometheus + Grafana, Evidently | CloudWatch, Vertex Model Monitoring, Azure Monitor |

### GitHub + Codespaces in this stack

**GitHub** is the code and CI/CD backbone for the majority of teams (the alternative is GitLab, with equivalent features). Beyond `git push`, the relevant primitives are:

- **Pull requests** with required reviews and status checks — the natural place to gate model changes.
- **GitHub Actions** — CI/CD runner; the standard for ML pipelines that are simple enough to live inside a workflow file (training inside Actions is fine for small models; for larger workloads, Actions triggers the cloud pipeline).
- **Codespaces** — managed cloud dev environments defined by `.devcontainer/devcontainer.json`. One click opens a containerised VS Code with the exact Python version, dependencies, and tooling specified by the repo. The point is *eliminating the "works on my machine" failure mode* for collaborative ML projects, where setup is otherwise painful.

A minimal `.devcontainer/devcontainer.json` for an ML repo:

```json
{
  "name": "ML dev",
  "image": "mcr.microsoft.com/devcontainers/python:3.11",
  "postCreateCommand": "pip install -r requirements.txt && pip install -e .",
  "features": {
    "ghcr.io/devcontainers/features/git:1": {}
  },
  "customizations": {
    "vscode": {
      "extensions": ["ms-python.python", "ms-toolsai.jupyter"]
    }
  }
}
```

### Hugging Face in this stack

**Hugging Face Hub** is the de facto registry for open-source models, datasets, and demos. Three primitives:

| Primitive | What it is | When you use it |
|---|---|---|
| **Models** | Versioned model repositories | Pull a pretrained model, push your own fine-tuned weights, share across the team |
| **Datasets** | Versioned dataset repositories | Use a published dataset; publish your own for collaboration or replication |
| **Spaces** | Hosted apps (Gradio, Streamlit, static, Docker) | Live demos, quick UIs, shareable artefacts |

What HF buys you, in this module's context:
- A canonical place to pull pretrained models with versioning and reproducible checkpoints (`transformers.AutoModel.from_pretrained("…", revision="…")`).
- A free-tier model registry alternative to MLflow/SageMaker MR for the early stages.
- A zero-infra way to ship a demo: push to Spaces, get a live URL.
- Inference Endpoints (paid) for managed serving of HF models without standing up your own infra — the HF equivalent of SageMaker Endpoints.

What HF is *not*:
- A complete MLOps platform. There is no pipeline orchestration, drift monitoring, or feature store. It coexists with the rest of the stack.

---

## A canonical L1 pipeline

This is the pipeline pattern that recurs across cloud providers (Vertex, SageMaker, Azure ML) and OSS orchestrators (Airflow, Prefect).

```
[ raw data ] ─┐
              ├─► [ feature pipeline ] ─► [ training data on storage ]
              │                                       │
[ feature    ]│                                       ▼
[ definitions]│                              [ training job ]
              │                                       │
              ▼                                       ▼
   [ feature store ]                       [ evaluation ]
                                                      │
                                                      ▼
                                            [ model registry ]
                                                      │
                            ┌─────────────────────────┤
                            ▼                         ▼
                  [ canary / shadow deploy ]   [ rollback target ]
                            │
                            ▼
                  [ production endpoint ]
                            │
                            ▼
                  [ monitoring + drift ]
                            │
                            ▼
                  (drift breach → trigger retrain)
```

This is the architecture every cloud sells in slightly different boxes. Build it once on any platform and the pattern translates.

---

## Common patterns

| Pattern | When to use it | Trade-off |
|---|---|---|
| **Notebook-to-prod** | Single-shot model, no retraining needed | Fast, but the next change will be painful |
| **Pipeline-driven** (L1) | Most production ML | Pays back from the second retraining onwards |
| **Pipeline-of-pipelines** (L2) | High-frequency retraining, large teams | Real platform-engineering investment |
| **Champion-challenger** | Comparing a new model against the live one | Requires shadow-deploy infrastructure |
| **Feature store** | Many models share features, training-serving skew is a known pain | Adds operational complexity, only pays off at multi-model scale |

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Notebook-only workflow at L0 stays at L0 forever | Every retraining is a one-off project | Promote the notebook to a script and a pipeline as soon as it is stable |
| Model artefact shipped without metadata | Cannot reproduce, cannot audit | Always register; never deploy a model not in the registry |
| Training–serving skew | Offline metrics good, online metrics bad | Share preprocessing code between training and serving (same Python module, same Docker image) |
| Data drift not monitored | Silent accuracy degradation | Statistical tests on inputs (PSI, KL divergence) + alarms wired to retraining |
| Monitoring only infra metrics | Endpoint is healthy, predictions are wrong | Add model-quality metrics (accuracy on ground truth, distribution of predictions) |
| Tools chosen for L2 at L0 | Team drowns in YAML | Pick the simplest stack that solves the next bottleneck, not the most complete one |
| Registry exists but is not enforced | Some deploys come from the registry, others from a developer's laptop | CI gate: only the registry can deploy |
| Codespaces but no `.devcontainer` | Codespaces opens but the environment is still custom | The `.devcontainer` is the dev environment spec; commit it like code |
| HF Spaces used for production traffic | Free tier rate-limits, no SLA | Use Spaces for demos; production needs Inference Endpoints or your own infra |
| ML engineer hires before L1 exists | Engineer has nothing to operate, ends up writing pipelines from scratch | Hire when there is *something* in production worth operating |

---

## When to use what

| Need | Pick | Why |
|---|---|---|
| First production model, single retraining cadence | L0 → L1 path | Build the minimum pipeline once a retraining is needed |
| Multi-model platform, daily retraining | L2 | Justified by retraining cadence |
| Track experiments | MLflow (OSS) or W&B (managed) | MLflow if everything stays on-prem, W&B for the better UI on free tier |
| Version datasets | DVC | The simplest entry point; lakeFS / Delta Lake for warehouse-scale data |
| Serve a model | FastAPI behind Docker, then a managed endpoint | Build the serving layer first; managed only when scale demands it |
| Share open-source models | Hugging Face Hub | The standard place; reduces friction enormously |
| Quick demo for stakeholders | HF Spaces (Gradio / Streamlit) | Zero infra, public URL |
| Reproducible dev env across the team | GitHub Codespaces + `.devcontainer` | One click, no setup README that goes stale |
| Trigger retraining on drift | Pipeline orchestrator + monitoring alarm | The L1 default |

---

## See also

### Other notes
- [02_environments_and_version_control.md](02_environments_and_version_control.md) — the practical version-control layer underneath MLOps (Git, venv, model registries)
- [04_model_serving_with_fastapi.md](04_model_serving_with_fastapi.md) — how the registered model becomes a live endpoint
- [08_ci_cd_pipelines.md](08_ci_cd_pipelines.md) — the automation layer that climbs from L0 to L1 to L2
- [09_production_deployment_monitoring_orchestration.md](09_production_deployment_monitoring_orchestration.md) — monitoring, orchestration, and the runtime side of MLOps

### Cross-module
- Module 04 [02_kpis_lifecycle_drift.md](../../04_business_case_AIPM/notes/02_kpis_lifecycle_drift.md) — the business view of model drift and lifecycle that this note frames technically
- Module 05 [02_aws_ai_ml_stack.md](../../05_AI_cloud_services/notes/02_aws_ai_ml_stack.md) — how SageMaker concretises the L1 pipeline pattern on AWS
- Module 05 [06_paas_vs_iaas_vs_oss_decision_framework.md](../../05_AI_cloud_services/notes/06_paas_vs_iaas_vs_oss_decision_framework.md) — when a managed MLOps platform is the right pick vs building your own
