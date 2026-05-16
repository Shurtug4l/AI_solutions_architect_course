# Environments and Version Control

## TL;DR

A reproducible ML system rests on three layered version controls: **environment** (Python interpreter + libraries + system packages), **code** (Git), and **artefacts** (datasets, trained models, configs). All three must move together, or the artefact you ship is not the artefact you tested. The default Python isolation tool is **`venv`** (stdlib, lightweight, fine for pure Python). **`conda`** wins when the project needs binary scientific stacks (CUDA, MKL, GDAL) that ship outside PyPI, and is the de facto choice in ML research. **`poetry`** and **`uv`** are the modern dependency managers with lockfiles, dependency resolution, and a single config file (`pyproject.toml`); `uv` is essentially a faster `pip` + `pip-tools` written in Rust and is becoming the new default. The **lockfile** (`poetry.lock`, `uv.lock`, `requirements.lock.txt`) is what makes an environment reproducible; without it `pip install -r requirements.txt` will silently pick newer minor versions and break in six months.

**Git** is non-negotiable for code. The mental model that matters in practice: a Git **repository** is a content-addressed graph of **commits**; each commit points to a **tree** (a snapshot of the working directory) and to one or more parent commits; **branches** are just movable labels on commits, **tags** are immovable ones, **HEAD** is the "where you are now" pointer. Most day-to-day commands (`add`, `commit`, `push`, `pull`, `merge`, `rebase`) become predictable once that graph is internalised. The collaboration pattern is feature-branch → pull request → review → merge to `main`, with `main` always deployable. ML-specific issues are: notebooks generate huge diffs (use `nbstripout` or `jupytext`), and binary artefacts do not belong in Git (use `.gitignore` + cloud storage + DVC / `git-lfs`).

**Versioning the model** is the third layer and the one MLOps adds. A trained model is the output of a stochastic process over data, so versioning the *file* is not enough; you need lineage from the artefact back to the **(data, code, hyperparameters)** that produced it. The **model registry** is the standard structure: a model has a name and a sequence of *versions*, each version has metadata (training metrics, parameters, lineage), and *stages* (Staging / Production / Archived) move versions through a promotion workflow. The OSS reference is **MLflow Model Registry**; managed equivalents are **Vertex Model Registry**, **SageMaker Model Registry**, **Azure ML Model Registry**, and **Hugging Face Hub** (for open-source distribution). The registry is the API between the data scientist who trains and the ML engineer who deploys; without it, the handoff degrades into shared files.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **`venv`** | Standard-library virtual environment, pure Python | Default for a quick service |
| **`conda`** | Cross-language environment manager, binary packages | Default when CUDA / scientific stack is needed |
| **`poetry`** | Modern dep manager with lockfile + `pyproject.toml` | Standard for libraries with PEP 517 build |
| **`uv`** | Rust-based, ultra-fast pip / pip-tools replacement | Becoming the new default; backwards compatible with pip |
| **`pip` + `requirements.txt`** | The default, no resolver, no lockfile by default | Fine if you also pin with `pip freeze > requirements.lock.txt` |
| **Lockfile** | Exact resolved versions of all transitive deps | The contract of reproducibility |
| **`pyproject.toml`** | PEP 518/621 project config | Replaces `setup.py`, `setup.cfg`, `requirements.txt` in modern projects |
| **Git commit** | Snapshot + parent pointer | Immutable atom in the history graph |
| **Branch** | Movable label on a commit | Where in-progress work lives |
| **`main`** | The deployable branch | Should always be releasable |
| **Pull request** | Request to merge a branch into another | The place reviews and CI gates run |
| **`.gitignore`** | Files Git should not track | Always exclude artefacts, large data, secrets |
| **`nbstripout`** | Strips notebook outputs at commit time | Mandatory for collaborative notebooks |
| **`git-lfs`** | Pointer + remote storage for large files | When you must keep binaries in Git |
| **DVC** | Git for data, on top of S3/GCS/Azure Blob | The pragmatic data-versioning entry point |
| **MLflow Model Registry** | OSS model catalogue with stages | The reference implementation |
| **Model stage** | Lifecycle marker on a version | Staging → Production → Archived |
| **Model lineage** | Pointer from artefact to training data + code commit | What lets you reproduce a model six months later |

---

## Environment isolation: the levels

> An "environment" is a set of installed Python interpreter version + libraries + (sometimes) system packages. Isolation prevents your project's installs from polluting other projects or the system Python.

### Level 0 — system Python

The default `python3` shipped with the OS. Installing libraries into it is what you do as a learner; in any real project it leads to conflicts, permission errors (`sudo pip`), and broken upgrades.

**Rule: never use the system Python for projects.**

### Level 1 — `venv` (stdlib)

```bash
python3 -m venv .venv
source .venv/bin/activate     # on macOS / Linux
.venv\Scripts\activate.bat    # on Windows
pip install -r requirements.txt
deactivate
```

What `venv` actually does: creates a directory `.venv/` with a Python interpreter symlink and a `site-packages/` of its own. Activating it prepends `.venv/bin` to `PATH` so `python` and `pip` point to the venv copies. Nothing magical.

What `venv` does *not* solve:
- Binary dependencies outside PyPI (CUDA, system libraries).
- Cross-platform reproducibility (a `requirements.txt` built on macOS may not resolve identically on Linux).
- Dependency resolution (pip's resolver is now decent but doesn't produce a lockfile by default).

### Level 2 — `conda` / `mamba` / `micromamba`

`conda` is a package manager *and* an environment manager. It can install non-Python binaries (CUDA, MKL, GDAL, GEOS, FFmpeg) from the `conda-forge` channel, which `pip` cannot do cleanly.

```bash
conda create -n myproj python=3.11
conda activate myproj
conda install -c conda-forge numpy scikit-learn pytorch
```

Where `conda` matters: ML research projects with GPU stacks, geospatial libraries, or anything that needs ABI-compatible compiled wheels. `mamba` and `micromamba` are faster reimplementations; the CLI is mostly the same.

The trap: mixing `conda install` and `pip install` in the same environment can create inconsistencies. Rule of thumb: install everything you can via conda first; only fall back to pip for libraries that are not on conda-forge.

### Level 3 — modern dependency managers (`poetry`, `uv`)

These wrap `pip`/`pip-tools` and add:
- A single project config file (`pyproject.toml`) per PEP 518/621.
- A real dependency resolver.
- A lockfile pinning the full transitive graph.
- Subcommands for adding/removing/updating dependencies.

**Poetry** example:

```bash
poetry init                       # one-time, generates pyproject.toml
poetry add fastapi pydantic       # add runtime deps
poetry add --group dev pytest     # add dev deps
poetry install                    # install from lock
poetry run python -m myapp        # run inside the env
poetry shell                      # activate the env
```

**uv** example (functionally similar, much faster):

```bash
uv venv                           # create .venv
uv pip install -r requirements.txt
uv pip compile requirements.in    # produces a lockfile
uv pip sync requirements.lock.txt # exact install
```

`uv` is roughly 10–100× faster than `pip` + `pip-tools` and is drop-in compatible. Many teams are migrating in 2025.

### Picking between them

| Need | Pick |
|---|---|
| Quick script, pure Python, no deps that need CUDA | `venv` + `pip` |
| ML research, CUDA, scientific stack | `conda` / `mamba` (often `conda-forge`) |
| Library / service with clean dependency management | `poetry` |
| Speed and modern UX, drop-in pip replacement | `uv` |
| Cross-platform reproducibility | Whatever you pick, *commit a lockfile* |

---

## The lockfile is the contract

> A `requirements.txt` without exact versions and without `--hashes` is **not** a lockfile. It is a wishlist.

Without a lockfile, two installs at different times resolve to different transitive dependencies. Six months later your CI fails because a transitive dep released a major version with a breaking change.

**With `pip` alone**:

```bash
pip install -r requirements.in    # high-level deps
pip freeze > requirements.lock.txt # exact resolved versions
pip install -r requirements.lock.txt # reproducible install
```

This is the manual lockfile pattern. `pip-tools` (`pip-compile`) automates it.

**With Poetry / uv**, the lockfile is built in and updated automatically by `poetry lock` / `uv pip compile`.

Always commit:
- `pyproject.toml` (or `requirements.in`) — the high-level intent.
- The lockfile — the exact resolution.

Never commit:
- The `.venv` directory itself — large, OS-specific, regenerable.

---

## Git: the model that makes commands predictable

> The vast majority of Git confusion comes from not having a clear mental model of the underlying graph. With the graph internalised, every command becomes "move this pointer here".

### The four objects

| Object | What it is | Identified by |
|---|---|---|
| **Blob** | A file's content | SHA-1 hash of content |
| **Tree** | A directory snapshot (mapping from name to blob/tree) | SHA-1 |
| **Commit** | A snapshot (tree) + metadata (author, date, message) + parent(s) | SHA-1 |
| **Tag** | An immovable label on a commit | The tag name |

### The pointers

| Pointer | What it is |
|---|---|
| **Branch** | A movable name pointing to a commit. `main`, `develop`, `feature/login` are all branches. |
| **HEAD** | The "you are here" pointer. Normally points to a branch (e.g., `main`); when detached it points directly at a commit. |
| **Remote** | A named pointer to another repo (`origin` by default). `origin/main` is a *remote-tracking* branch — a local cache of where `main` was on `origin` at the last fetch. |

### The graph operations

```
                                       │
A ───► B ───► C  (main)                ▼ C'  ◄── HEAD (detached) after checkout C'
              │                        
              └── D ───► E  (feature)  
```

- `git add` stages a change into the index (staging area).
- `git commit` creates a new commit on the current branch, with HEAD's commit as parent.
- `git checkout <branch>` moves HEAD to point at that branch and updates the working directory.
- `git merge <other>` creates a *merge commit* with two parents (or fast-forwards if no divergence).
- `git rebase <other>` replays your commits on top of `<other>` — rewrites history.
- `git pull` = `git fetch` + `git merge` (or `--rebase` for the rebase variant).
- `git push` updates the remote branch to match your local one.

The reason `rebase` and `merge` are different is the resulting *graph shape*: merge preserves the divergence as two parents, rebase linearises history. The team convention picks one; both are valid.

### The collaboration pattern

```
   main                                main
    │                                   │
    ▼                                   ▼
    A ────────────────────────────────► A ──► M   (merge commit)
                                                ▲
    A ──► B ──► C (feature/login)              /
                                              /
                              push → PR → review → merge ────────┘
```

1. Branch off `main`: `git checkout -b feature/something`.
2. Commit small, focused changes.
3. Push and open a pull request.
4. CI runs tests; reviewers comment; you push more commits.
5. Merge into `main` (squash, merge commit, or rebase depending on the team's choice).

`main` is always deployable; only merge in once CI is green.

### What goes in `.gitignore`

For an ML project:

```
# Environment
.venv/
__pycache__/
*.pyc

# Notebook outputs
.ipynb_checkpoints/

# OS junk
.DS_Store

# Editor
.vscode/
.idea/

# Models and large data — these live in cloud storage + DVC
*.pkl
*.pt
*.onnx
*.safetensors
data/raw/
data/processed/
models/

# Secrets
.env
*.key
```

The rule: **anything regenerable, large, or sensitive should not be in Git.** Code, configs, notebooks (stripped), and metadata stay.

### ML-specific Git pain

| Pain | Symptom | Fix |
|---|---|---|
| Notebook diffs | Every commit changes JSON metadata and image bytes | `nbstripout` filter (commits stripped) or `jupytext` (sync `.ipynb` with `.py`) |
| Large model files | `git push` is enormous, history bloats | `.gitignore` + cloud storage + DVC pointer files |
| Datasets in repo | Same as above, plus PII risk | Move data out; reference by URI |
| Merge conflicts in notebooks | Almost unresolvable | Strip outputs; prefer one author per notebook or pair sessions |
| Secrets committed by accident | Surfaces in history forever | `git-secrets` / pre-commit hooks; rotate the secret if exposed |

---

## Versioning the model

> The model file is one piece of the artefact. Without lineage to its inputs, it is not reproducible — and not auditable.

### What "versioning a model" requires

| Field | Why |
|---|---|
| **Artefact** (`.pkl`, `.pt`, `.onnx`) | The serialised model |
| **Code commit** | The training script that produced it |
| **Data version** | The exact dataset version (hash or DVC pointer) |
| **Hyperparameters** | Learning rate, seeds, batch size, etc. |
| **Environment** | Python version, library lockfile, CUDA version |
| **Metrics** | Training and held-out evaluation metrics |
| **Signature** | Input/output schema (often Pydantic / MLflow signature) |
| **Stage** | Staging, Production, Archived |
| **Approvals** | Who signed off, when |

A bare `.pkl` on a shared drive carries none of this. A model registry stores all of it as a single record indexed by `(model_name, version)`.

### Model registry: the abstraction

```
registry/
   └── my-recommender/
         ├── v1   (Archived)   trained 2024-11-03, AUC 0.81, commit a1b2c3
         ├── v2   (Production) trained 2025-02-14, AUC 0.84, commit d4e5f6
         └── v3   (Staging)    trained 2025-03-22, AUC 0.86, commit 7g8h9i
```

The deploy pipeline reads from `(my-recommender, Production)`; promotion is a metadata change, not a file copy. Rollback is "set v2 back to Production". Audit is "show me what was deployed on a given date".

### MLflow Model Registry — the OSS reference

```python
import mlflow

# Training run logs metrics, params, artefacts
with mlflow.start_run() as run:
    mlflow.log_param("lr", 0.001)
    mlflow.log_metric("auc", 0.86)
    mlflow.sklearn.log_model(model, artifact_path="model")

# Register the artefact as a new version of the model
mlflow.register_model(
    model_uri=f"runs:/{run.info.run_id}/model",
    name="my-recommender",
)

# Promote to Production
client = mlflow.MlflowClient()
client.transition_model_version_stage(
    name="my-recommender",
    version=3,
    stage="Production",
    archive_existing_versions=True,
)
```

The deploy job then loads `models:/my-recommender/Production` — never a path on disk.

### Managed equivalents

| Provider | Registry |
|---|---|
| AWS | SageMaker Model Registry |
| GCP | Vertex Model Registry |
| Azure | Azure ML Model Registry |
| OSS / hybrid | MLflow Model Registry (self-hosted or via Databricks) |
| Open distribution | Hugging Face Hub |

All of them implement the same contract: `(name, version, stage, metadata, artefact URI)`. The choice follows the rest of the cloud stack.

### Data versioning (DVC, briefly)

DVC stores small **pointer files** (`.dvc`) in Git, and the actual data in a remote (S3, GCS, Azure Blob). The pointer files contain a content hash, so the dataset version is part of the commit.

```bash
dvc init
dvc remote add -d storage s3://my-bucket/dvc
dvc add data/raw/train.csv     # creates train.csv.dvc, ignores train.csv
git add data/raw/train.csv.dvc .gitignore
git commit -m "Add training data v1"
dvc push                        # uploads data to S3

# Later
dvc pull                        # fetches data referenced by the current commit
```

This binds the data version to the code commit. The model version stored in the registry then references both the code commit and the DVC-tracked data version, closing the lineage loop.

---

## Putting the three layers together

```
   Code commit (Git)
        │
        ├── pinned environment (lockfile)
        │
        ├── training data version (DVC / lakeFS / pointer)
        │
        ▼
   Training run (MLflow logged)
        │
        ▼
   Artefact + metrics + lineage
        │
        ▼
   Model Registry (versioned, staged)
        │
        ▼
   Deploy (pulls from registry, builds Docker image, ships)
```

If any of the three (code, env, data) is missing from the lineage, the deployed model cannot be reproduced. This is what L1 maturity buys you and L0 does not.

---

## Common workflows

| Workflow | Steps |
|---|---|
| **Start a new ML repo** | `git init`, write `pyproject.toml`, add `.gitignore`, scaffold `src/`, `tests/`, `notebooks/`, `data/.gitkeep` |
| **Add a dependency** | `poetry add foo` (or `uv pip install foo` + update lockfile), commit `pyproject.toml` + lockfile |
| **Daily branch-and-PR** | `git checkout -b feature/x` → work → `git push -u origin feature/x` → open PR → review → merge |
| **Pin a working environment for reproducibility** | Generate a lockfile, commit it, install with `--no-deps` from the lockfile in CI/Docker |
| **Version a new model** | Train inside an MLflow run, log artefacts and metrics, `register_model` with metadata, transition to Staging, run validation, promote to Production |
| **Roll back a model** | `transition_model_version_stage` of the prior version back to Production; the deploy job picks it up on next reconcile |
| **Clean a notebook before commit** | `nbstripout` filter installed once; `git add` strips outputs automatically |

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| System `pip install foo` | Permission errors, broken system Python | Always a virtual environment |
| `requirements.txt` without pinned versions | "It worked yesterday" failures | Lockfile + `pip install -r requirements.lock.txt` in CI/Docker |
| Mixing `conda install` and `pip install` | Inconsistent ABIs, segfaults | Prefer conda for everything possible; isolate pip-only deps with care |
| Committing `.venv/` | Bloated repo, OS-specific binaries in Git | `.gitignore` it |
| Committing models or datasets | Multi-GB repo, slow clones | Cloud storage + DVC / `git-lfs`, never raw files |
| Notebook diffs the size of an essay | Noisy reviews, merge conflicts | `nbstripout` or `jupytext` |
| Secret committed by mistake | Credential leak | Rotate immediately; rewrite history with `git filter-repo`; install pre-commit secret scanner |
| Model file on a shared drive, no metadata | "Which version is in prod?" is unanswerable | Adopt a model registry; gate deploys on registry-only |
| `main` directly pushed to, no PR | Untested code in production | Branch protection: require PR + CI green |
| Data drift but no data version tracked | Cannot reproduce yesterday's training | DVC or equivalent; data version pinned in model lineage |
| Rebasing a shared branch | "My history is gone" | Only rebase your own branches; never rebase what others have based work on |
| Force-pushing `main` | Wiped commits, lost work | Branch protection; never `--force` on shared branches |

---

## When to use what

| Need | Pick | Why |
|---|---|---|
| Isolated env for a Python service | `venv` or `uv venv` | Stdlib, fast, no extra installation |
| ML research with CUDA + scientific binaries | `conda` / `mamba` (`conda-forge`) | Binary deps outside PyPI |
| Modern dep management with lockfile | `poetry` or `uv` | Lockfile, resolver, clean `pyproject.toml` |
| Source control | `git` + GitHub / GitLab | Universal default |
| Notebook collaboration | `nbstripout` or `jupytext` | Tame diffs |
| Data versioning | DVC | Pragmatic entry point; lakeFS / Delta for warehouse scale |
| Model versioning | MLflow Model Registry | OSS reference; Vertex/SageMaker/Azure MR are the managed twins |
| Sharing open-source models | Hugging Face Hub | The standard distribution channel |
| Large binary files in Git | `git-lfs` | Only if they must live in Git; otherwise external storage |

---

## See also

### Other notes
- [01_mlops_foundations.md](01_mlops_foundations.md) — why versioning matters in the MLOps maturity model
- [07_containerization_with_docker.md](07_containerization_with_docker.md) — the next layer of reproducibility (system packages, runtime)
- [08_ci_cd_pipelines.md](08_ci_cd_pipelines.md) — how the lockfile + registry plug into CI/CD

### Cross-module
- Module 01 [09_model_selection.md](../../01_machine_learning/notes/09_model_selection.md) — the experimental workflow that experiment tracking digitises
- Module 02 [07_rag_production.md](../../02_large_language_models/notes/07_rag_production.md) — versioning concerns specific to LLM RAG systems (embedding model versions, index versions)
- Module 05 [02_aws_ai_ml_stack.md](../../05_AI_cloud_services/notes/02_aws_ai_ml_stack.md) — SageMaker Model Registry, the managed twin of MLflow on AWS
