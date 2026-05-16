# Model Serving with FastAPI

## TL;DR

Serving a model is taking a trained artefact and exposing it as a callable, reliable, observable service. The dominant pattern in Python is a **FastAPI** application that loads the model once at startup, validates the input with a **Pydantic** schema, runs inference, and returns a structured response. The full picture has more moving parts than the demo: a **reverse proxy** in front (NGINX) handling TLS and routing, a **WSGI/ASGI process manager** (Gunicorn with Uvicorn workers) running the Python app, a **container** wrapping the runtime (Docker), and a **monitoring layer** capturing latency, error rate, and prediction distributions. The model itself is loaded from a **model registry** (MLflow, SageMaker MR, Vertex MR, HF Hub) — never from a path on a developer's laptop.

The **synchronous vs asynchronous** decision for the prediction handler is decided by the workload shape, not by preference. For **CPU- or GPU-bound inference** (sklearn, PyTorch forward pass, ONNX Runtime), the handler should be a plain `def`: FastAPI runs it in a threadpool and the event loop stays free for other I/O. For **inference that fans out to remote services** (LLM API, embedding API, vector DB, feature store), `async def` with `httpx` / `asyncpg` is a real win because the handler spends most of its time waiting. The trap is `async def` with blocking calls inside, which gives you nothing and silently stalls the event loop. The rule: `async def` only when you `await`; otherwise sync.

**Batching** is the single biggest performance lever for ML inference. Most frameworks are far more efficient processing 32 inputs at once than 32 sequential single-input calls (matrix kernels amortise overhead). At low traffic, single-request serving is fine. At higher traffic, two patterns dominate: **dynamic batching** at the server (collect requests for a few milliseconds, batch them, return individual responses — Triton and BentoML do this natively) and **batch endpoints** (`POST /predict/batch` accepting an array, used for offline or near-real-time pipelines). The API design pattern that fits both: accept either a single instance or a list and return matching shape.

**Production model serving** has shape-distinct concerns beyond a working endpoint. **Cold start** (first request after deploy is slow because the model is not loaded) — solved by loading at startup, not lazily. **Memory footprint** (a 7B-parameter LLM is 14 GB in fp16) — solved by picking the right serving infra and quantising. **Concurrency** (`workers × threads_per_worker` for Gunicorn) — tuned to CPU count and inference cost. **Resilience** (a single slow request must not block others) — solved by timeouts and a process manager that recycles workers. **Observability** — `/health`, `/ready`, structured logs, request IDs, latency histograms exposed to Prometheus. Real serving is "model + API + supervisor + proxy + observability", not "FastAPI + `model.pkl`".

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **Inference endpoint** | The HTTP entry point that runs the model | Usually `POST /predict` or `POST /predictions` |
| **Cold start** | First-request latency caused by lazy loading | Always load model at startup |
| **Load-at-startup** | `lifespan` / `on_event("startup")` | The single right place to load the model |
| **Pydantic request/response** | Typed I/O schema | Validation + OpenAPI + clarity |
| **Sync handler (`def`)** | Runs in a threadpool | Right default for CPU/GPU-bound inference |
| **Async handler (`async def`)** | Yields during I/O | Use only with `await` calls (httpx, asyncpg, LLM SDKs) |
| **Batching** | Process N inputs in one model call | Largest single lever for throughput |
| **Dynamic batching** | Server-side batching across concurrent requests | Triton, BentoML, vLLM do it for you |
| **Batch endpoint** | `POST /predict/batch` accepting a list | Pragmatic alternative to dynamic batching |
| **Workers** | OS processes running the app (Gunicorn `-w`) | Tune to `2 × CPU + 1` for CPU-bound; 1 for GPU |
| **Threads** | Threads per worker | Useful for I/O-bound, less for CPU-bound |
| **`/health`** | Liveness probe | "Is the process up?" |
| **`/ready`** | Readiness probe | "Is the model loaded and serving?" |
| **Request ID** | Per-request identifier propagated through logs | Mandatory for tracing |
| **Streaming response** | Send chunks before the full result | LLM token streaming, large CSV exports |
| **Model registry pull** | Load model by `(name, stage)` not by file path | The L1 baseline |

---

## The minimum viable serving app

```python
# app.py
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
import joblib
import numpy as np

# --- Schemas -------------------------------------------------------

class PredictRequest(BaseModel):
    features: list[float] = Field(min_length=10, max_length=10)

class PredictResponse(BaseModel):
    prediction: float
    label: str
    model_version: str

# --- Lifecycle -----------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = joblib.load("artifacts/model.pkl")
    app.state.model_version = "v2.1.0"
    yield
    # cleanup if needed

app = FastAPI(title="Tabular model API", version="1.0", lifespan=lifespan)

# --- Dependencies --------------------------------------------------

def get_model(app: FastAPI = Depends(lambda: app)):
    return app.state.model

# --- Health --------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    if not hasattr(app.state, "model"):
        raise HTTPException(status_code=503, detail="model not loaded")
    return {"status": "ready", "model_version": app.state.model_version}

# --- Inference -----------------------------------------------------

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    x = np.array(req.features).reshape(1, -1)
    proba = float(app.state.model.predict_proba(x)[0, 1])
    label = "positive" if proba >= 0.5 else "negative"
    return PredictResponse(
        prediction=proba,
        label=label,
        model_version=app.state.model_version,
    )
```

This is roughly the smallest serving app that is honest about production. It has:
- Load-at-startup via `lifespan`.
- Validated request schema.
- Typed response schema for OpenAPI.
- Separate `/health` (process up) and `/ready` (model loaded).
- Version reported in the response (so downstream systems can attribute predictions).

Running it:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 1   # dev
gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000 app:app   # prod-ish
```

For real production this still sits behind NGINX and inside Docker — see notes 07 and 09.

---

## Load the model at startup, always

> The single most common ML serving mistake is loading the model inside the handler.

Three variations and what they cost:

| Pattern | First request | Subsequent requests | When |
|---|---|---|---|
| **Load inside the handler** | OK | Slow (reload every time) | Never |
| **Lazy-load on first hit** | Slow (cold start) | OK | Acceptable for rare endpoints |
| **Load at startup** (`lifespan`) | OK | OK | Default for any real service |

The cost of loading at startup is a slower deploy (the process needs the model in memory before it accepts traffic) — which is *exactly* what `/ready` is for. The orchestrator should not route traffic to a pod until `/ready` returns 200.

For large models (LLMs, big embedding models), startup time is in the minutes. Use a readiness probe with generous timeouts and document the expected boot time.

---

## Loading from a model registry, not a file path

```python
import mlflow.sklearn

@asynccontextmanager
async def lifespan(app: FastAPI):
    # The deploy-time contract: this version is what's currently "Production"
    app.state.model = mlflow.sklearn.load_model("models:/my-recommender/Production")
    app.state.model_version = mlflow.MlflowClient().get_latest_versions(
        name="my-recommender", stages=["Production"]
    )[0].version
    yield
```

What this buys you:
- Rollback is a registry stage transition, not a redeploy.
- Audit ("what was in prod on 2025-04-12?") is one query.
- The deploy job has no knowledge of the file path; the registry is the indirection.

For HF models the equivalent is `transformers.AutoModel.from_pretrained("org/model", revision="commit-hash")`. Always pin the revision; never load from `main`.

---

## Sync vs async: deciding per endpoint

### Pure model inference, sync

```python
@app.post("/predict")
def predict(req: PredictRequest):
    # CPU/GPU-bound: FastAPI runs this in a threadpool
    return {"prediction": model.predict(req.features)}
```

### Inference that calls remote services, async

```python
import httpx

@app.post("/rag/answer")
async def rag_answer(req: QuestionRequest):
    async with httpx.AsyncClient(timeout=30) as client:
        # Three I/O-bound calls happening sequentially
        embedding = await client.post(EMBED_URL, json={"text": req.question})
        chunks = await vector_db.aquery(embedding.json()["vector"], k=5)
        answer = await client.post(LLM_URL, json={"prompt": build_prompt(req.question, chunks)})
    return {"answer": answer.json()["text"]}
```

### Fan-out: doing the I/O concurrently

```python
import asyncio

@app.post("/multi_model_predict")
async def multi(req: PredictRequest):
    results = await asyncio.gather(
        client.post(MODEL_A_URL, json=req.dict()),
        client.post(MODEL_B_URL, json=req.dict()),
        client.post(MODEL_C_URL, json=req.dict()),
    )
    return ensemble([r.json() for r in results])
```

The async pattern here cuts latency from sum-of-3 to max-of-3 — a real, measurable gain.

### What *not* to do

```python
@app.post("/bad")
async def bad(req: PredictRequest):
    # WRONG: blocking call inside async, stalls the event loop
    response = requests.post(REMOTE_URL, json=req.dict())
    return response.json()
```

Either switch to `httpx`, or change the handler to `def` and let FastAPI use the threadpool.

---

## Batching: the throughput multiplier

> A sklearn `predict` over a batch of 1000 rows is hundreds of times faster than 1000 calls of 1 row each.

### Batch endpoint pattern

```python
class BatchPredictRequest(BaseModel):
    instances: list[list[float]] = Field(min_length=1, max_length=1024)

class BatchPredictResponse(BaseModel):
    predictions: list[float]
    model_version: str

@app.post("/predict/batch", response_model=BatchPredictResponse)
def predict_batch(req: BatchPredictRequest):
    X = np.array(req.instances)
    preds = app.state.model.predict_proba(X)[:, 1].tolist()
    return BatchPredictResponse(predictions=preds, model_version=app.state.model_version)
```

The trade-off: a single oversized batch causes a head-of-line blocking problem (one slow request blocks others on the same worker). Cap the batch size (`max_length=1024`) and document it.

### Accept either single or list

```python
class PredictRequest(BaseModel):
    instances: list[list[float]] | list[float]   # one or many

@app.post("/predict")
def predict(req: PredictRequest):
    if isinstance(req.instances[0], list):
        X = np.array(req.instances)
    else:
        X = np.array(req.instances).reshape(1, -1)
    preds = model.predict_proba(X)[:, 1]
    return {"predictions": preds.tolist()}
```

This is the pragmatic compromise: same endpoint serves both real-time single-instance and small-batch use cases.

### Dynamic batching at the server

For high-traffic inference, the right tool is a model server that does **dynamic batching**: collect concurrent requests for a few milliseconds, run them as one batch, return individual responses. Options:
- **NVIDIA Triton Inference Server** — multi-framework, gRPC + HTTP, production-grade.
- **BentoML** — Python-first, integrates batching into the framework.
- **vLLM** / **TGI** — LLM-specific with continuous batching tuned to autoregressive generation.

When traffic is low enough that single-request serving meets latency targets, skip the complexity.

---

## Streaming responses

For LLM inference (token-by-token), large CSV exports, or any work where the result is generated incrementally, `StreamingResponse` is the right primitive:

```python
from fastapi.responses import StreamingResponse

@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    async def token_generator():
        async for token in llm.stream(req.prompt):
            yield f"data: {token}\n\n"   # SSE format
        yield "data: [DONE]\n\n"
    return StreamingResponse(token_generator(), media_type="text/event-stream")
```

The browser / client reads the stream incrementally; perceived latency drops from "the full response time" to "time to first token", which is a much better UX for chat-style products.

---

## Resource shape: workers, threads, GPU

> The right `gunicorn -w` is workload-dependent. Default rules of thumb help, but profile before believing them.

### CPU-bound inference

```bash
gunicorn -k uvicorn.workers.UvicornWorker -w $((2 * $(nproc) + 1)) -b 0.0.0.0:8000 app:app
```

Workers run in separate processes; each gets a copy of the model in memory. If the model is 500 MB and you have 4 workers, that's 2 GB of RAM just for weights. Beyond a point, fewer workers with more threads (`--threads 4`) is better.

### GPU-bound inference

```bash
gunicorn -k uvicorn.workers.UvicornWorker -w 1 -b 0.0.0.0:8000 app:app
```

One worker. A GPU is a single resource; multiple workers fighting for it produce out-of-memory errors and worse throughput, not better. Use dynamic batching (Triton / vLLM) to get parallelism inside the single process.

### Concurrent connections

`--worker-connections` (or the framework's equivalent) sets the upper bound on concurrent connections per worker. The hard limit usually comes from file descriptors on the host (`ulimit -n`).

### Timeouts

```bash
gunicorn ... --timeout 60 --graceful-timeout 30
```

- `--timeout`: kill a worker stuck on a single request for longer than this. Set to the 99th-percentile expected inference time + safety margin.
- `--graceful-timeout`: how long Gunicorn waits for in-flight requests during a restart.

Without timeouts, a single slow request can hang a worker indefinitely.

---

## Observability

### `/health` vs `/ready`

| Endpoint | Returns 200 when | Used by |
|---|---|---|
| `/health` | The process is responsive | Liveness probe — restart the container if this fails |
| `/ready` | The model is loaded and dependencies are reachable | Readiness probe — route traffic only when this is 200 |

Without the split, restarts cause traffic to hit a not-yet-loaded process and produce errors.

### Request IDs

```python
import uuid
from fastapi import Request

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    rid = request.headers.get("X-Request-Id") or str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-Id"] = rid
    # log lines should include rid via contextvars or structlog
    return response
```

Propagate the ID to upstream services in their request headers; the same ID appears in every log line of the request's path. This is the cheapest, most-impactful tracing primitive.

### Prometheus metrics

```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)  # exposes /metrics
```

Out of the box you get request count, latency histograms, and in-flight requests broken down by route and status. Add custom metrics for ML-specific things:
- Distribution of prediction values (binned histogram).
- Distribution of input features (for drift detection).
- Model version label on all metrics.

---

## Putting it together for an ML model deployment

The slides at the end of the module (61–63) describe the canonical "deploy an ML model" pattern:

1. **Train** the model offline; log to MLflow / W&B / SageMaker Experiments; register in the model registry.
2. **Wrap** the artefact in a FastAPI app with:
   - `lifespan` loading the model from the registry.
   - Pydantic schemas for request and response, including the version field.
   - `/health` and `/ready`.
3. **Containerise** with a `Dockerfile` (see note 07): base image, install dependencies from lockfile, copy code, set CMD to `gunicorn ... -k uvicorn.workers.UvicornWorker app:app`.
4. **CI/CD** (see note 08): on merge to `main`, build the image, run integration tests against the container, push to a registry, deploy.
5. **Deploy** behind a reverse proxy with TLS termination (NGINX, see note 09). Configure liveness/readiness probes against `/health` and `/ready`.
6. **Monitor** with Prometheus + Grafana for system metrics, plus ML-specific drift metrics computed from logged predictions vs eventual ground truth.

The shape of the FastAPI app does not change much for different model types; the surrounding infrastructure does (GPU for LLMs, autoscaling for spiky traffic, async fan-out for RAG).

---

## Common patterns

| Pattern | When |
|---|---|
| **Single instance + batch endpoint on same model** | Mixed real-time and offline use cases |
| **Async fan-out** to embedding + vector DB + LLM | RAG inference |
| **Streaming SSE response** | Chat / LLM token generation |
| **Two-stage model** (`/score` cheap → `/explain` expensive) | Conserve resources by skipping the explain step on most calls |
| **Shadow endpoint** (`/predict?shadow=true`) | Send a copy of traffic to a candidate model without affecting users |
| **Canary deploy** (split traffic 10/90 between versions at the proxy layer) | Validate a new model under real load |
| **Idempotent batch with request ID** | Retries do not double-bill or double-write |

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Model loaded in handler | Latency spikes, memory waste | `lifespan` / `on_event("startup")` |
| `async def` with blocking calls | Event loop stalled, mysterious latency | Use async clients or sync handlers |
| Path-based model load | Cannot rollback, no lineage | Load from model registry by `(name, stage)` |
| Same endpoint for sync and batch with no size cap | OOM on a maliciously large request | Cap with `max_length` in Pydantic |
| Multiple Gunicorn workers on GPU | OOM, throughput collapse | 1 worker per GPU; use dynamic batching |
| No request timeout | One slow request hangs a worker | `--timeout` in Gunicorn |
| `/health` returns 200 before model is loaded | Orchestrator sends traffic prematurely | Separate `/health` and `/ready` |
| Logs without request ID | Tracing impossible across services | Middleware that injects `X-Request-Id` |
| Returning huge arrays | Slow serialisation, memory pressure | Stream with `StreamingResponse` or paginate |
| Missing model version in response | Cannot attribute predictions in monitoring | Add `model_version` to the response model |
| `requirements.txt` not pinned in serving image | "Works in dev, fails in prod" | Build the image from the lockfile |
| GPU inference inside `async def` | Loop blocked anyway | Run in `def`, optionally `run_in_executor` |

---

## When to use what

| Need | Pick | Why |
|---|---|---|
| Default ML inference endpoint | FastAPI + Pydantic, sync handler, load at startup | The right baseline |
| RAG / multi-service fan-out | FastAPI + async handler + `httpx` + `asyncio.gather` | Real async win on I/O |
| High-throughput inference on GPU | Triton / vLLM / TGI behind FastAPI gateway | Dynamic batching matters |
| LLM chat streaming | FastAPI `StreamingResponse` SSE | Time-to-first-token UX |
| Mixed batch + single | Single endpoint accepting both shapes | Pragmatic; minimal API surface |
| Long inference (>30s) | Job pattern (`POST /jobs` → `GET /jobs/{id}`) | Don't hold HTTP connections |
| Autoscaling required | Container behind a managed service (Cloud Run, ECS, K8s with HPA) | Stateless containers scale horizontally |
| Multiple model versions for A/B | Two deployments + traffic split at proxy | Cleaner than version flag in URL |

---

## See also

### Other notes
- [03_apis_and_web_frameworks.md](03_apis_and_web_frameworks.md) — HTTP, REST, Flask vs FastAPI primitives
- [07_containerization_with_docker.md](07_containerization_with_docker.md) — packaging the serving app into a deployable artefact
- [09_production_deployment_monitoring_orchestration.md](09_production_deployment_monitoring_orchestration.md) — NGINX, Gunicorn, monitoring, the runtime side

### Cross-module
- Module 01 [09_model_selection.md](../../01_machine_learning/notes/09_model_selection.md) — the offline evaluation that precedes serving
- Module 02 [07_rag_production.md](../../02_large_language_models/notes/07_rag_production.md) — production patterns specific to RAG endpoints (caching, streaming, scaling)
- Module 03 [07_deployment.md](../../03_agentic_ai/notes/07_deployment.md) — exposing agentic workflows through APIs
- Module 05 [02_aws_ai_ml_stack.md](../../05_AI_cloud_services/notes/02_aws_ai_ml_stack.md) — SageMaker Endpoints, the managed twin of this pattern on AWS
