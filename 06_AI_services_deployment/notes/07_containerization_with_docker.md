# Containerization with Docker

## TL;DR

A **container** is a process (or group of processes) isolated from the host using Linux kernel features — **namespaces** for visibility (PID, network, mount, user, IPC, UTS) and **cgroups** for resource limits (CPU, memory, IO). It packages the application together with its dependencies (libraries, system binaries, configuration) into an **image**, which is a read-only filesystem snapshot. The runtime then starts a writable layer on top of the image and runs the entrypoint. Containers are not virtual machines: they share the host kernel and start in milliseconds, but they are isolated enough that "it works on my machine" stops being a meaningful sentence. **Docker** is the tool that built the mainstream developer experience around containers; the underlying runtime is now usually `containerd` / `runc`, and Kubernetes coordinates them at scale.

A **Dockerfile** is a sequence of instructions that produce an image. Each instruction creates a **layer** (cached, content-addressed). The order of instructions matters for cache reuse: put rarely-changing things first (system packages, dependencies) and frequently-changing things last (your code). For Python ML services, the canonical pattern is **multi-stage builds**: a "builder" stage installs dependencies and (optionally) compiles wheels; a "runtime" stage copies only what is needed onto a slim base image. The result is a smaller, less-vulnerable image — typically 200–500 MB instead of 1.5+ GB. **`.dockerignore`** is the partner of `.gitignore`: it tells the daemon which files in the build context to ignore, which keeps builds fast and prevents shipping secrets or virtual environments into the image.

**Building, registering, and instantiating** are the three verbs. **`docker build`** turns a Dockerfile + context into an image. **`docker push`** uploads it to a **registry** (Docker Hub, GitHub Container Registry, ECR, GCR, ACR) where it gets an immutable digest and human-readable tags. **`docker run`** instantiates a container from an image — passing port mappings, volume mounts, environment variables, and resource limits. In CI/CD the loop is build → tag with the commit SHA → push to a registry → the deploy job pulls by digest and runs. **`docker compose`** orchestrates multiple containers locally (app + DB + redis + message queue) from a `docker-compose.yml`; it is a development primitive, not a production one — Kubernetes (or managed equivalents like ECS, Cloud Run) handles production.

For ML serving the layer that matters is **what goes in the image and what does not**. Code, lockfile, the model artefact (or a script that pulls it from the registry), and a runtime command. **Not** in the image: secrets (injected as env vars or via a secret store at runtime), data (mounted as a volume or read from cloud storage), credentials. **Not in the same image**: training code and serving code, when they have very different dependency footprints — the serving image should be minimal, the training image can be fat. **Base image** choice matters: `python:3.11-slim` is the right default; `python:3.11` is fat (full Debian); `python:3.11-alpine` is small but breaks compiled wheels (musl libc vs glibc); `nvidia/cuda:12.X-cudnn-runtime` is the starting point for GPU inference. The image is the deployment artefact; treat it like a versioned, signed, scanned product.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **Container** | Isolated process using namespaces + cgroups | Light, fast, shares the host kernel |
| **Image** | Read-only filesystem snapshot + metadata | The build output, what gets pushed |
| **Layer** | Filesystem diff produced by one Dockerfile instruction | Cached and reused across builds |
| **Dockerfile** | Recipe for building an image | Lives at repo root, named `Dockerfile` |
| **`.dockerignore`** | Files excluded from the build context | Like `.gitignore` for builds |
| **Multi-stage build** | Use multiple `FROM` stages, copy only what's needed into the final | Slim images, no build deps in runtime |
| **Base image** | The starting image for `FROM` | `python:3.11-slim` for Python, `nvidia/cuda:...` for GPU |
| **`docker build`** | Build an image from Dockerfile + context | `docker build -t myapp:v1 .` |
| **Build context** | The directory sent to the Docker daemon at build time | Use `.dockerignore` to keep it small |
| **`docker run`** | Start a container from an image | `docker run --rm -p 8000:8000 myapp:v1` |
| **`docker push`** | Upload to a registry | After `docker login` to the registry |
| **Registry** | Storage for images | Docker Hub, ECR, GCR, ACR, GHCR, Harbor |
| **Tag** | Human-readable label on an image | `v1.2.3`, `latest`, `commit-abc123` |
| **Digest** | Content-addressed identifier | `sha256:...`, immutable |
| **`docker compose`** | Multi-container local orchestration | `docker compose up`, dev only |
| **Volume** | Persistent storage outside the container's writable layer | For data, logs, models |
| **Bind mount** | Map a host directory into a container | Common in dev, avoid in prod |
| **`ENTRYPOINT` / `CMD`** | What the container runs | Together they form `argv` |
| **Healthcheck** | Probe defined in the image | Used by orchestrators |
| **Image scan** | Vulnerability scan against CVE databases | Trivy, Grype |
| **BuildKit** | Modern Docker builder | Faster, cached, default in modern Docker |
| **OCI** | Open Container Initiative spec | Image and runtime standard |

---

## Containers vs VMs

> Both isolate workloads. They differ in *what* they virtualise.

| Dimension | VM | Container |
|---|---|---|
| Virtualises | Hardware (CPU, memory, devices) | OS process tree |
| Kernel | Each VM has its own | Shared with the host |
| Boot time | Seconds–minutes | Milliseconds |
| Image size | GB | MB (sometimes GB for ML) |
| Density per host | 10s | 100s–1000s |
| Isolation strength | Strong (separate kernel) | Strong-but-not-perfect (shared kernel — kernel-level vulnerabilities cross the boundary) |
| Use case | Multi-tenant infra, untrusted workloads, different OSes on one host | App packaging and shipping; consistent dev/staging/prod |

Containers won the application packaging space because they are lightweight and reproducible. VMs (or VM-like sandboxes — Firecracker, gVisor) still matter when isolation strength has to be hard, e.g., running untrusted user code.

---

## What "isolated" actually means

> The container experience comes from a handful of Linux kernel features. Docker stitches them together.

### Namespaces (what the process sees)

| Namespace | Isolates | Effect |
|---|---|---|
| **pid** | Process IDs | Inside the container, PID 1 is your entrypoint; the host's PIDs are invisible |
| **net** | Network interfaces, routing | Container has its own `eth0`, `lo`; ports are explicitly published |
| **mnt** | Mount points | Container has its own filesystem view |
| **uts** | Hostname | Container can have a different hostname |
| **ipc** | Shared memory, semaphores | Isolated IPC |
| **user** | UID/GID mapping | Container's `root` can be mapped to non-root on host |
| **cgroup** | The cgroup hierarchy | Newer namespace, hides the host's cgroup layout |

### Control groups (cgroups) — resource limits

```bash
docker run --memory=2g --cpus=1.5 --pids-limit=200 myapp:v1
```

Without cgroups, one runaway container can starve the host. The hard limits are non-negotiable in production.

---

## The Dockerfile

> A sequence of layered instructions. The order is load-bearing for cache hit rate.

### Anatomy

```dockerfile
# 1. Base image
FROM python:3.11-slim AS runtime

# 2. Metadata
LABEL org.opencontainers.image.source="https://github.com/me/myapp"

# 3. System dependencies (changes rarely → cached)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. Python dependencies (changes when lockfile changes → cached most days)
WORKDIR /app
COPY requirements.lock.txt ./
RUN pip install --no-cache-dir -r requirements.lock.txt

# 5. Application code (changes every commit → cached rarely)
COPY src ./src
COPY artifacts ./artifacts

# 6. Non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# 7. Network and runtime config
EXPOSE 8000
ENV PYTHONUNBUFFERED=1

# 8. Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -fs http://localhost:8000/health || exit 1

# 9. Entrypoint
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "2", "-b", "0.0.0.0:8000", "src.api:app"]
```

### Instructions worth understanding

| Instruction | What |
|---|---|
| `FROM` | Base image. Can have `AS <stage>` for multi-stage. |
| `RUN` | Run a command at build time, produce a new layer. |
| `COPY` | Copy from build context into the image. Source paths are *relative to the context root*. |
| `ADD` | Like COPY but also extracts archives and can fetch URLs. Prefer `COPY` + explicit fetches. |
| `WORKDIR` | Set the working directory for subsequent instructions and at runtime. |
| `ENV` | Set environment variables (build-time and runtime). |
| `ARG` | Build-time variable (`docker build --build-arg FOO=bar`). |
| `EXPOSE` | Document a port the container listens on (does not actually publish it). |
| `USER` | Switch to a non-root user. |
| `ENTRYPOINT` | The "command that always runs" (often a wrapper script or the binary). |
| `CMD` | The default arguments to ENTRYPOINT (or the command, if no ENTRYPOINT). |
| `HEALTHCHECK` | Probe that the orchestrator uses to gauge container health. |
| `VOLUME` | Declare a path as a mount point (helpful for documentation, but explicit `-v` at run time is more common). |

### Cache layering: ordering is load-bearing

If you put `COPY src ./src` before `pip install`, every code change busts the dependency cache and rebuilds the entire pip layer. The right order is:
1. Base image.
2. System deps.
3. Dependency manifest (`requirements.lock.txt`, `pyproject.toml` + `poetry.lock`).
4. Dependency install.
5. Code.

The cost is one rebuild every time you change deps, which is rare. The win is fast iteration on code changes.

---

## Multi-stage builds

> Build in one image, run in another. Ship only what's needed.

### Example: Python with compiled wheels

```dockerfile
# ===== Builder stage =====
FROM python:3.11 AS builder

WORKDIR /build
COPY requirements.lock.txt ./
# Build wheels for all dependencies (some may need compilers)
RUN pip wheel --wheel-dir /wheels -r requirements.lock.txt

# ===== Runtime stage =====
FROM python:3.11-slim AS runtime

WORKDIR /app
COPY --from=builder /wheels /wheels
COPY requirements.lock.txt ./
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.lock.txt \
    && rm -rf /wheels

COPY src ./src
COPY artifacts ./artifacts

RUN useradd --create-home app && chown -R app:app /app
USER app

EXPOSE 8000
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "2", "-b", "0.0.0.0:8000", "src.api:app"]
```

Why bother:
- The runtime image does not include `gcc`, `g++`, headers, or any of the build chain.
- Smaller image → faster pulls, smaller attack surface, lower egress cost.
- The builder can install dev tools without polluting the runtime.

### Example: ML model with PyTorch

```dockerfile
FROM python:3.11-slim AS builder
RUN apt-get update && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /build
COPY requirements.lock.txt .
RUN pip install --user --no-cache-dir -r requirements.lock.txt

FROM python:3.11-slim AS runtime
COPY --from=builder /root/.local /home/app/.local
ENV PATH=/home/app/.local/bin:$PATH
WORKDIR /app
COPY src ./src
COPY artifacts/model.pkl ./artifacts/
RUN useradd --create-home app && chown -R app:app /app /home/app
USER app
EXPOSE 8000
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

### Example: GPU inference with CUDA

```dockerfile
FROM nvidia/cuda:12.4.0-cudnn-runtime-ubuntu22.04 AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.11 python3-pip \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.lock.txt .
RUN pip install --no-cache-dir -r requirements.lock.txt
COPY src ./src
COPY artifacts ./artifacts
EXPOSE 8000
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Run with `docker run --gpus all ...` to expose the host GPU to the container.

---

## `.dockerignore`

> Same idea as `.gitignore`, but for the build context. Skipping this is how `.venv` ends up shipped to prod.

```
# Version control
.git
.gitignore

# Local env
.venv/
__pycache__/
*.pyc
.pytest_cache/
.mypy_cache/
.ruff_cache/

# Notebooks
*.ipynb
.ipynb_checkpoints/

# Data and models too large to ship
data/raw/
data/processed/
# Note: keep artifacts/ if the model goes in the image

# OS
.DS_Store

# Secrets
.env
*.key
*.pem
```

A tight `.dockerignore` shrinks the build context (faster builds, less data sent to remote builders) and prevents accidental shipping of secrets, venvs, or development cruft.

---

## Build, register, instantiate

### Build

```bash
docker build -t myorg/myapp:v1.2.3 -t myorg/myapp:latest -f Dockerfile .
```

- `-t` tags the resulting image. Multiple `-t`s are fine.
- The final `.` is the build context.
- `-f` selects a non-default Dockerfile (`Dockerfile.gpu`, etc.).

In CI, tag with the commit SHA so every build is uniquely identifiable:

```bash
docker build -t myorg/myapp:$(git rev-parse --short HEAD) .
```

### Register (push to a registry)

```bash
docker login ghcr.io                 # auth to the registry
docker push myorg/myapp:v1.2.3
docker push myorg/myapp:latest       # the floating tag
```

Registries you'll meet:

| Registry | Provider |
|---|---|
| Docker Hub | Default; rate-limited on free tier |
| GitHub Container Registry (`ghcr.io`) | GitHub-integrated |
| Amazon ECR | AWS |
| Google Artifact Registry / Container Registry | GCP |
| Azure Container Registry | Azure |
| Harbor | Self-hosted OSS |

Choose one consistent with the rest of the cloud stack.

**Always pull by digest in production**:

```yaml
image: myorg/myapp@sha256:abcd1234...
```

A tag like `latest` is a moving pointer; digests are immutable. Tags for humans, digests for deploys.

### Instantiate

```bash
docker run --rm -d \
    --name myapp \
    -p 8000:8000 \
    -e MODEL_VERSION=v2 \
    -e DATABASE_URL=postgres://... \
    --memory=4g --cpus=2 \
    --read-only --tmpfs /tmp \
    -v /var/log/myapp:/app/logs \
    myorg/myapp:v1.2.3
```

What each flag does:

| Flag | Purpose |
|---|---|
| `--rm` | Remove the container when it exits |
| `-d` | Detached |
| `--name` | A name to use instead of the random adjective_animal |
| `-p host:container` | Publish a port |
| `-e KEY=VALUE` | Environment variable |
| `--memory`, `--cpus` | cgroup limits |
| `--read-only --tmpfs /tmp` | Root filesystem read-only, writable temp |
| `-v host:container` | Bind mount; `--volume` for named volumes |
| `--restart unless-stopped` | Restart policy (good for local dev) |

In production these come from the orchestrator config (Kubernetes manifest, ECS task definition, Cloud Run service spec), not from a `docker run` CLI invocation. The principles transfer.

---

## docker compose: multi-container dev

> A YAML file describing several containers and their wiring. Local dev primitive. Not production.

### `docker-compose.yml`

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgres://postgres:postgres@db:5432/app
      REDIS_URL: redis://cache:6379
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started

  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: postgres
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s

  cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  pgdata:
```

```bash
docker compose up --build       # build and start everything
docker compose logs -f api      # tail logs
docker compose exec api bash    # shell into the api container
docker compose down -v          # stop and remove volumes
```

The killer feature: services reference each other by service name (`db`, `cache`) — Compose puts them on a private network and provides DNS. Newcomers' setup goes from "twelve services on twelve ports" to `docker compose up`.

Why **not** in production: no autoscaling, no rolling updates, no health-aware load balancing, single-host. Compose is to development what Kubernetes is to production.

---

## Image hygiene for ML services

### Pin everything

- Base image: `python:3.11-slim-bookworm` not `python:3` not `python:latest`.
- Or by digest: `python@sha256:...` (the strongest pin).
- Dependencies: from a lockfile.
- Apt packages: pin versions for reproducibility (`apt-get install foo=1.2.3-1`) when supply-chain matters.

### Minimise the image

- Multi-stage build to drop build tools.
- `pip install --no-cache-dir` to avoid the wheel cache.
- `rm -rf /var/lib/apt/lists/*` after `apt-get install`.
- `pip install --no-deps` only if you already pin the full transitive graph.
- Combine related `RUN` commands with `&&` to reduce layer count (no longer critical with BuildKit, still good hygiene).

### Run as non-root

```dockerfile
RUN useradd --create-home --shell /bin/bash app
USER app
```

If a process is compromised, the non-root user limits the blast radius. Most orchestrators (Kubernetes PodSecurity, OpenShift) enforce non-root by default.

### Scan the image

```bash
trivy image myorg/myapp:v1.2.3
grype myorg/myapp:v1.2.3
```

These tools cross-check installed packages against CVE databases. Wire into CI; fail the build on high/critical findings (with a documented allowlist for known-noisy false positives).

### Sign the image

For high-stakes deployments, sign with **cosign** (Sigstore):

```bash
cosign sign --key cosign.key myorg/myapp@sha256:...
cosign verify --key cosign.pub myorg/myapp@sha256:...
```

The deploy pipeline then verifies signature before pulling. Stops a compromised registry from serving a poisoned image.

---

## ML-specific patterns

### Where the model lives

| Pattern | When |
|---|---|
| **Model baked into the image** (`COPY artifacts/model.pkl`) | Small models, deterministic version-to-image binding, simplest deploy |
| **Model pulled at startup** from a registry (MLflow, S3, GCS) | Decouples model release from image release; supports rollback by registry stage |
| **Model mounted as a volume** from a shared filesystem | Large models, multi-pod sharing; orchestrator wires the volume |

The baked-in pattern is the simplest. The startup-pull pattern is the L1 default once the model registry exists.

### Separate training and serving images

The dependencies for training (`scikit-learn`, `pandas`, `matplotlib`, `mlflow`, `wandb`, plotting) are not the same as for serving (`scikit-learn` predict path only, FastAPI, joblib). Two images keep the serving image small and the training image isolated.

```
Dockerfile.train        # full deps, runs the training pipeline
Dockerfile.serve        # minimal deps, runs FastAPI
```

### CPU vs GPU

The image is different. The host runtime is different (`--gpus all`, `nvidia-container-toolkit`). The orchestrator request is different (`nvidia.com/gpu: 1` in a K8s manifest, `Tesla T4` in a Cloud Run config).

Cleanest path: separate `Dockerfile.serve.cpu` and `Dockerfile.serve.gpu`, with the same code mounted into both. The CI matrix builds both.

---

## Common patterns

| Pattern | Notes |
|---|---|
| **Distroless base** (`gcr.io/distroless/python3`) | Smaller, no shell, harder to debug but harder to attack |
| **Init container** (in K8s) | Pulls the model from the registry into a shared volume before the main container starts |
| **Sidecar container** | Auxiliary process alongside the main (log shipper, proxy, model server) |
| **Single binary in scratch** | For Go/Rust services; not applicable to Python |
| **Reproducible builds** | Pinned base image digest + pinned deps + frozen build context |
| **Buildx multi-arch** | Build for `linux/amd64` and `linux/arm64` in one go |
| **Layer warm-up cache** | CI step that pre-pulls the base image and dependency layer |

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Code copied before deps installed | Every code edit busts the dep cache | COPY lockfile first, install, then COPY code |
| Build context with `.venv` / `node_modules` / `data` | Slow builds, huge images | Tight `.dockerignore` |
| `FROM python:3.11` (full image) | 1+ GB image | Use `slim` (or `distroless` if you can do without a shell) |
| `apt-get install` without cleanup | 100s of MB in apt lists | `&& rm -rf /var/lib/apt/lists/*` |
| Running as root | Privilege escalation on container breakout | Create and `USER` a non-root user |
| Storing secrets in the image | `docker history` exposes them | Inject at runtime via env vars or secret store |
| Forgetting `-p` | Container runs, nothing reachable | Map ports explicitly |
| Bind-mounting `.` in prod | Host filesystem changes leak into the container | Bind mounts are dev only |
| Tag drift (`latest`) | "Same image" deploys differently a week apart | Pin by digest in deploy manifests |
| `ENTRYPOINT ["python", "app.py"]` with `CMD ["--debug"]` | Combinations get confusing | Pick one pattern; document; usually `CMD` only |
| Image scan with no policy | Reports CVEs nobody acts on | Fail CI on high/critical with a documented allowlist |
| GPU image without `--gpus all` | `nvidia-smi` not found | Pass `--gpus`, install `nvidia-container-toolkit` on the host |
| Compose used in production | No autoscaling, no rolling updates | Use a real orchestrator |
| `python:3.11-alpine` for PyTorch | Wheels fail to install (musl libc) | Use `slim` for Python ML; alpine is for Go/static binaries |
| Missing `PYTHONUNBUFFERED=1` | Logs disappear (Python buffers stdout) | Set it in `ENV` |

---

## When to use what

| Need | Pick | Why |
|---|---|---|
| Default Python base image | **`python:3.11-slim`** | Smallest with glibc, compatible with PyTorch/TF wheels |
| GPU inference base image | **`nvidia/cuda:X.Y.Z-cudnn-runtime-...`** | Matches CUDA + cuDNN to the model's requirements |
| Smaller and more secure | **Distroless** | When the team can do without a shell |
| Multi-container local dev | **`docker compose`** | Standard, simple |
| Multi-container production | **Kubernetes**, **ECS**, **Cloud Run**, **App Service**, **Nomad** | Real orchestration |
| Registry | The one matching your cloud (ECR / GAR / ACR), or **GHCR** if CI is on GitHub | Networking, IAM, cost |
| Image scanning | **Trivy** (default), **Grype** (alternate) | Industry standard |
| Image signing | **cosign** (Sigstore) | Open standard |
| Build cache speed | **BuildKit** + remote cache (registry / Buildx) | Faster CI |
| Multi-arch builds | **`docker buildx`** | Single command for amd64 + arm64 |
| Model in image vs registry | Bake for small/single-version; pull at startup for L1 lifecycle | Tradeoff between simplicity and decoupling |

---

## See also

### Other notes
- [02_environments_and_version_control.md](02_environments_and_version_control.md) — the lockfile that goes into the image
- [04_model_serving_with_fastapi.md](04_model_serving_with_fastapi.md) — the app the image wraps
- [08_ci_cd_pipelines.md](08_ci_cd_pipelines.md) — where build, scan, push, and sign happen
- [09_production_deployment_monitoring_orchestration.md](09_production_deployment_monitoring_orchestration.md) — running the image behind NGINX/Gunicorn in production

### Cross-module
- Module 05 [01_aiaas_and_cloud_architecture_fundamentals.md](../../05_AI_cloud_services/notes/01_aiaas_and_cloud_architecture_fundamentals.md) — containerised AI services on cloud platforms
- Module 05 [05_iaas_open_source_and_on_prem_deployment.md](../../05_AI_cloud_services/notes/05_iaas_open_source_and_on_prem_deployment.md) — containers in the IaaS / on-prem deployment story
- Module 03 [07_deployment.md](../../03_agentic_ai/notes/07_deployment.md) — containerising agentic systems (with tool sandboxing concerns)
