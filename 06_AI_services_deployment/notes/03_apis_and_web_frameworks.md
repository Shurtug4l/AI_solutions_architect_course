# APIs and Web Frameworks: HTTP, REST, Flask, FastAPI

## TL;DR

An **API** (Application Programming Interface) is a contract: a caller invokes a procedure, parameters cross a boundary, a result comes back. On the public web that boundary is **HTTP**: a stateless request/response protocol where requests carry a **method** (verb), a **URL** (resource address), **headers** (metadata), and an optional **body** (payload). The dominant convention for web APIs is **REST** (Representational State Transfer), which maps **resources** to URLs and **operations** to HTTP methods (`GET` retrieve, `POST` create, `PUT` replace, `PATCH` update, `DELETE` remove). REST is a *style*, not a spec — pragmatic implementations relax the purist constraints. An **endpoint** is the concrete URL+method that exposes one operation (e.g., `POST /predict`). Status codes carry the outcome: 2xx success, 3xx redirect, 4xx client error, 5xx server error.

In Python, two web frameworks dominate ML serving: **Flask** and **FastAPI**. **Flask** is the older minimalist micro-framework (2010); routing is done with decorators, request/response is plain dictionaries, the runtime is **WSGI** (synchronous). It is small, well-documented, and has a huge ecosystem of extensions; the downside is that you build everything around it (validation, OpenAPI, async) by hand. **FastAPI** (2018) is the modern alternative: it sits on **ASGI** (async-capable), uses **Pydantic** for request/response validation via Python type hints, and generates **interactive OpenAPI / Swagger UI** automatically. The combination of type-driven validation, async support, and free OpenAPI documentation makes FastAPI the de facto choice for new model-serving APIs. Flask still wins on simplicity and for projects already invested in its ecosystem.

**Pydantic** is the core that makes FastAPI ergonomic. You declare request and response schemas as Python classes inheriting from `BaseModel`; FastAPI uses them to (1) parse and validate incoming JSON, (2) serialise outgoing responses, (3) generate the OpenAPI spec, (4) populate the interactive docs at `/docs`. Validation errors become structured 422 responses automatically. The pattern eliminates the boilerplate that Flask requires (`request.get_json()`, manual key checking, manual type coercion).

**Async functions** (`async def`) matter when the server spends most of its time *waiting* for I/O — database queries, HTTP calls to other services, LLM inference over network, message-queue reads. Async lets one worker handle many concurrent requests by yielding control during I/O waits. They do *not* help for **CPU-bound** work (numerical training, heavy numpy/PyTorch inference); for that you use synchronous endpoints (which FastAPI runs in a threadpool) or offload to a worker process / model server. The rule: `async def` when you `await` something, plain `def` when you do not.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **API** | Contract for procedure invocation across a boundary | Anything you call and get a structured reply |
| **HTTP** | Stateless request/response protocol over TCP | The transport for ~all web APIs |
| **HTTP method** | The verb describing the operation | `GET`, `POST`, `PUT`, `PATCH`, `DELETE` |
| **URL** | Resource address (scheme://host:port/path?query) | `https://api.example.com/v1/users/42?fields=name` |
| **Headers** | Key/value metadata about the request or response | `Content-Type`, `Authorization`, `Accept` |
| **Body** | Payload, usually JSON | The data being sent or returned |
| **Status code** | Three-digit outcome | 200 OK, 201 Created, 400 Bad Request, 404 Not Found, 500 Internal Server Error |
| **REST** | Style that maps resources to URLs and operations to methods | The dominant API style |
| **Endpoint** | Concrete URL + method | `POST /predict` |
| **OpenAPI** | Machine-readable spec of an API | The standard for documentation and codegen |
| **Swagger UI** | Interactive web UI generated from OpenAPI | `/docs` in FastAPI by default |
| **WSGI** | Sync Python web server interface (PEP 3333) | What Flask runs on |
| **ASGI** | Async Python web server interface | What FastAPI runs on |
| **Flask** | Minimalist sync framework | Pre-2018 default, still common |
| **FastAPI** | Modern async framework with Pydantic | New default for ML APIs |
| **Pydantic** | Data validation via Python type hints | The "schemas" of FastAPI |
| **`async def`** | Coroutine, can `await` I/O | Use when the work is I/O-bound |
| **CORS** | Cross-Origin Resource Sharing | Required if a browser frontend on another origin calls the API |

---

## HTTP in 5 minutes

> HTTP is stateless: each request stands alone, the server keeps no memory of prior requests from the same client (statefulness is reconstructed via cookies, tokens, or session storage *on top* of HTTP).

### Anatomy of a request

```
POST /v1/predict HTTP/1.1
Host: api.example.com
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiI...
Accept: application/json

{"features": [1.2, 3.4, 5.6]}
```

- **Method**: `POST` — describes the intent.
- **Path**: `/v1/predict` — what resource/operation.
- **Headers**: `Content-Type` describes the body, `Authorization` carries credentials, `Accept` says what the client wants back.
- **Body**: JSON payload.

### Anatomy of a response

```
HTTP/1.1 200 OK
Content-Type: application/json
X-Request-Id: 4f8e2c1a

{"prediction": 0.87, "label": "positive"}
```

- **Status code**: 200 — success.
- **Headers**: response metadata.
- **Body**: the returned payload.

### Methods and what they imply

| Method | Intent | Idempotent? | Safe? |
|---|---|---|---|
| `GET` | Retrieve | Yes | Yes (no side effects) |
| `POST` | Create / process | No | No |
| `PUT` | Replace (idempotent create-or-update) | Yes | No |
| `PATCH` | Partial update | Often yes | No |
| `DELETE` | Remove | Yes | No |
| `HEAD` | Like GET but no body | Yes | Yes |
| `OPTIONS` | Discover allowed methods, CORS preflight | Yes | Yes |

*Safe* = no server-side state change. *Idempotent* = N identical calls have the same effect as 1.

For an ML inference endpoint, `POST /predict` is conventional even though predicting is "safe" (no state change), because the body cannot fit in a URL.

### Status codes worth knowing

| Code | Meaning | When |
|---|---|---|
| 200 | OK | Successful GET/PUT/PATCH/DELETE |
| 201 | Created | POST that created a resource |
| 204 | No Content | Success with empty body (often DELETE) |
| 301 / 302 | Redirect | Resource moved |
| 400 | Bad Request | Malformed input |
| 401 | Unauthorized | Missing or invalid credentials |
| 403 | Forbidden | Authenticated but not allowed |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | Resource state conflicts (concurrent edit, duplicate) |
| 422 | Unprocessable Entity | Validation failed (FastAPI default for Pydantic errors) |
| 429 | Too Many Requests | Rate-limited |
| 500 | Internal Server Error | Unhandled exception |
| 502 / 503 / 504 | Upstream / unavailable / timeout | Infrastructure issues |

The discipline: do not respond with 200 for an error and a `{"error": "..."}` body. Use the right status code; clients (and proxies, and monitoring) rely on them.

---

## REST as a style

> REST is a *set of conventions*, not a protocol. The conventions exist because they map naturally to HTTP and produce predictable APIs.

### The core ideas

1. **Resources** are the nouns; URLs name them.
2. **Operations** are HTTP methods, applied to a resource.
3. **State** lives on the server; the client transitions it by sending representations.
4. **Stateless** requests; the server does not retain client session state between requests.
5. **Uniform interface**: same verbs, same JSON shape conventions across resources.

### A REST design for users

```
GET    /users                list users
POST   /users                create a user
GET    /users/{id}           retrieve a user
PUT    /users/{id}           replace a user
PATCH  /users/{id}           update a user
DELETE /users/{id}           delete a user
GET    /users/{id}/orders    list a user's orders
```

The URL is a hierarchy of nouns. Verbs in URLs (`/getUser`, `/createUser`) are an anti-pattern; the HTTP method is the verb.

### REST for ML serving

For inference, the resource model is awkward — a prediction is not really a "resource" you GET. Three common pragmatic patterns:

| Pattern | Endpoint | Notes |
|---|---|---|
| **Action endpoint** | `POST /predict` | The pragmatic default. Not strictly REST but understood by everyone. |
| **Resource semantics** | `POST /predictions` (returns 201 with a prediction object) | More REST-ful, useful when you want to GET a prediction back by ID later |
| **Async / job-based** | `POST /jobs` → 202, then `GET /jobs/{id}` | When the inference is long-running (LLM batch, video processing) |

For a single-model service the action-endpoint pattern is the right default. The job pattern emerges naturally when responses take more than a few seconds.

---

## Flask: the minimalist baseline

> Flask is "Werkzeug + Jinja2 + a routing decorator". It does nothing you do not ask it to do.

### Hello world

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/predict", methods=["POST"])
def predict():
    payload = request.get_json()
    if "features" not in payload:
        return jsonify({"error": "missing 'features'"}), 400
    features = payload["features"]
    # ... call the model ...
    return jsonify({"prediction": 0.87})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```

### Key concepts

| Concept | What |
|---|---|
| `Flask(__name__)` | The app object; routes attach to it |
| `@app.route(path, methods=...)` | Register a function as the handler for a path/method |
| `request` | A globals-like object (proxy) holding the current request |
| `request.get_json()` | Parse the JSON body |
| `jsonify(...)` | Serialise a dict to a JSON response |
| Return tuple | `(body, status_code)` for custom status codes |
| `app.run(...)` | Built-in dev server — never use in production (use Gunicorn / uWSGI) |

### Strengths

- Tiny core; you understand the whole framework in an afternoon.
- Mature ecosystem: Flask-SQLAlchemy, Flask-Login, Flask-Restful, Flask-Migrate, etc.
- Synchronous code, easy to reason about and debug.

### Weaknesses

- **Validation is manual**. Every endpoint repeats `if "key" not in payload: return error`.
- **No automatic documentation**. To get OpenAPI you bolt on `flask-smorest`, `apispec`, etc.
- **WSGI only**. Async support exists since Flask 2.0 but the underlying server is sync.
- **Serving ML models with large response payloads or long inference times** runs into the sync model; you end up putting it behind Celery anyway.

Flask is still a fine pick for a small internal service or when the team's existing skill is Flask.

---

## FastAPI: the modern default for ML serving

> FastAPI is "Starlette + Pydantic + type-driven OpenAPI". The combination is what makes it ergonomic.

### Hello world

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="My model API", version="1.0")

class PredictRequest(BaseModel):
    features: list[float]

class PredictResponse(BaseModel):
    prediction: float
    label: str

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest) -> PredictResponse:
    # `req` is already a validated PredictRequest at this point
    x = req.features
    pred = 0.87  # call the model here
    return PredictResponse(prediction=pred, label="positive")
```

What just happened:
- Hit `POST /predict` with `{"features": [1, 2, 3]}` and you get the validated dataclass.
- Hit it with `{"features": "not a list"}` and you get a structured 422 with the validation error, without writing any check.
- Visit `/docs` and you get an interactive Swagger UI generated from the types.
- Visit `/openapi.json` for the spec.

### Pydantic in one example

```python
from pydantic import BaseModel, Field, field_validator
from typing import Literal

class PredictRequest(BaseModel):
    features: list[float] = Field(min_length=10, max_length=10, description="10-dim feature vector")
    threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    model_version: Literal["v1", "v2"] = "v2"

    @field_validator("features")
    @classmethod
    def features_finite(cls, v):
        if any((x != x) or (abs(x) == float("inf")) for x in v):
            raise ValueError("features must be finite")
        return v
```

What you get for free:
- Type coercion (`"0.5"` → `0.5`).
- Range validation (`ge`, `le`).
- Length constraints (`min_length`, `max_length`).
- Enum-like via `Literal`.
- Custom validators with `@field_validator`.
- Auto-generated docs for every field via `description`.

### Path, query, header, and body parameters

```python
from fastapi import FastAPI, Path, Query, Header

app = FastAPI()

@app.get("/users/{user_id}")
def get_user(
    user_id: int = Path(..., ge=1),                # path param
    fields: list[str] = Query(default=[]),         # query param
    x_request_id: str | None = Header(default=None),  # header
):
    ...
```

FastAPI distinguishes parameter sources automatically based on names and `Path` / `Query` / `Header` annotations. The body is anything declared with a Pydantic model.

### Dependency injection

A clean pattern for shared logic (DB sessions, auth, model loading):

```python
from fastapi import Depends

def get_model():
    return app.state.model  # loaded at startup

@app.post("/predict")
def predict(req: PredictRequest, model = Depends(get_model)):
    return {"prediction": model.predict(req.features)}
```

The same pattern is used for authentication (a `Depends(verify_token)` that yields the current user or raises 401).

### Startup / shutdown lifecycle

```python
from contextlib import asynccontextmanager
import joblib

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = joblib.load("model.pkl")  # startup
    yield
    # cleanup on shutdown (close connections, etc.)

app = FastAPI(lifespan=lifespan)
```

Loading the model once at startup is the right pattern; loading it on every request is the trap that destroys latency.

---

## Async functions

> Async helps when the server *waits* for something. It does not magically speed up CPU-bound work.

### The model

A sync endpoint blocks a worker thread for the duration of the request:

```python
@app.get("/slow")
def slow():
    time.sleep(5)  # blocks the thread
    return {"done": True}
```

An async endpoint releases the thread while waiting:

```python
import asyncio

@app.get("/slow_async")
async def slow_async():
    await asyncio.sleep(5)  # cooperatively yields
    return {"done": True}
```

With async, one worker can handle thousands of concurrent slow-but-waiting requests; with sync, the throughput is limited by the worker pool size.

### When to use `async def`

| Workload | Choice | Reason |
|---|---|---|
| I/O-bound: DB query, HTTP call, message queue, file read | `async def` + `await` | Yields the loop during the wait |
| CPU-bound: numpy matmul, PyTorch inference, image processing | plain `def` | FastAPI runs it in a threadpool; async would block the event loop |
| Mixed: model inference on GPU is technically "I/O" to the GPU | plain `def`, or async + `run_in_executor` | Simpler to keep sync unless you have a measured reason |

The trap: declaring an endpoint `async def` and then calling a *blocking* library (sync `requests`, sync `psycopg2`, sync sklearn predict) — the event loop blocks and async gives you nothing. Either use async clients (`httpx`, `asyncpg`) or keep the endpoint sync.

### Async clients to know

| Sync | Async equivalent |
|---|---|
| `requests` | `httpx` (also has a sync API) |
| `psycopg2` | `asyncpg` or `psycopg[async]` |
| `redis` | `redis.asyncio` |
| `boto3` | `aioboto3` |

---

## Flask vs FastAPI

| Axis | Flask | FastAPI |
|---|---|---|
| Year / runtime | 2010 / WSGI sync | 2018 / ASGI async-capable |
| Validation | Manual | Pydantic, automatic |
| OpenAPI | Manual or via extension | Built-in |
| Swagger UI | Manual | Built-in at `/docs` |
| Async | Limited (WSGI) | Native |
| Performance | Decent, sync-bound | Among the fastest Python frameworks (close to Node/Go) |
| Ecosystem | Huge, mature | Younger but rich (Starlette, Pydantic, SQLModel) |
| Learning curve | Tiny | Small, but type hints become important |
| Best for | Existing Flask codebases, small internal services | New ML APIs, projects with type discipline, async I/O |

### Side-by-side: a prediction endpoint

```python
# Flask
@app.route("/predict", methods=["POST"])
def predict_flask():
    payload = request.get_json()
    if not payload or "features" not in payload:
        return jsonify({"error": "missing features"}), 400
    features = payload["features"]
    if not isinstance(features, list) or len(features) != 10:
        return jsonify({"error": "features must be a 10-dim list"}), 400
    pred = model.predict([features])[0]
    return jsonify({"prediction": float(pred)})

# FastAPI
class PredictReq(BaseModel):
    features: list[float] = Field(min_length=10, max_length=10)

@app.post("/predict")
def predict_fastapi(req: PredictReq):
    pred = model.predict([req.features])[0]
    return {"prediction": float(pred)}
```

The FastAPI version is shorter, validated, documented, and typed. This compounds across an API with twenty endpoints.

---

## CORS and other production niceties

If a browser frontend on `app.example.com` calls an API on `api.example.com`, the browser enforces **CORS** (Cross-Origin Resource Sharing): the API must respond to the preflight `OPTIONS` request with the right headers. FastAPI's middleware:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com"],
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)
```

Other middleware worth knowing: GZip compression, request ID injection, rate limiting (via `slowapi`), tracing (OpenTelemetry).

---

## Common patterns

| Pattern | Notes |
|---|---|
| **Versioned paths** (`/v1/predict`, `/v2/predict`) | Lets you introduce breaking changes without breaking existing clients |
| **Pagination** (`?page=2&page_size=50` or cursor-based) | Always paginate list endpoints; never return unbounded lists |
| **Idempotency keys** for POST | Let clients retry safely; the server deduplicates by `Idempotency-Key` header |
| **Health (`/health`, `/ready`)** | Liveness probe + readiness probe for orchestrators |
| **OpenAPI as the source of truth** | Generate clients (Python, TS) from the spec instead of writing by hand |
| **Background tasks** | `BackgroundTasks` in FastAPI for fire-and-forget post-response work (logging, async cache warm) |

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| `app.run()` in production | Single-threaded dev server, poor performance | Run with Gunicorn (Flask) or Uvicorn workers (FastAPI) behind a reverse proxy |
| `async def` with blocking calls | Event loop stalls, latency spikes | Use async clients or drop `async def` |
| Loading the model inside the handler | Cold start on every request | Load in `lifespan` / `@app.on_event("startup")` |
| Returning 200 with an error body | Monitoring and clients cannot tell success from failure | Use the correct status code |
| Hard-coded CORS `allow_origins=["*"]` with credentials | Security risk, browser will refuse | List specific origins or accept that credentials are not used |
| No request size limit | A 1 GB payload OOMs the worker | Set a max body size at the reverse proxy or framework level |
| No timeout on outbound HTTP | A slow upstream hangs your endpoint indefinitely | Always pass `timeout=` to client libraries |
| Sync DB driver inside async endpoint | Blocks the event loop | `asyncpg` / `psycopg[async]`, or a sync endpoint |
| Validation logic duplicated in handlers | Drift between endpoints | Centralise in Pydantic models |
| OpenAPI spec drifts from code | Generated clients are wrong | Use FastAPI's auto-generation; never hand-edit the spec |
| Returning huge JSON arrays | Latency, memory pressure | Stream with `StreamingResponse`, paginate, or use NDJSON |
| Missing `Content-Type: application/json` on the request | FastAPI returns 422; clients confused | Verify client serialisation; FastAPI is strict on purpose |

---

## When to use what

| Need | Pick | Why |
|---|---|---|
| New ML inference API | **FastAPI** | Pydantic validation, OpenAPI, async support |
| Existing Flask codebase | **Flask** | Don't rewrite working code |
| Strict typing across the API | **FastAPI** | Types are load-bearing in FastAPI |
| Heavy CPU-bound inference | FastAPI **with `def`** (threadpool) | Async would block the event loop |
| Many I/O-bound calls per request | FastAPI **with `async def`** + `httpx` / `asyncpg` | Async pays off here |
| Quick internal admin page with HTML | Flask + Jinja2, or Streamlit | FastAPI is API-first, not HTML-first |
| Auto-documented public API | **FastAPI** | `/docs` is free |
| Long-running inference | Job pattern (`POST /jobs` → `GET /jobs/{id}`) on either framework | Don't tie up HTTP connections |

---

## See also

### Other notes
- [04_model_serving_with_fastapi.md](04_model_serving_with_fastapi.md) — applying these primitives to actual model inference endpoints
- [06_api_security_and_authentication.md](06_api_security_and_authentication.md) — securing the endpoints designed here
- [07_containerization_with_docker.md](07_containerization_with_docker.md) — packaging the API for shipping

### Cross-module
- Module 02 [07_rag_production.md](../../02_large_language_models/notes/07_rag_production.md) — production patterns for RAG endpoints (streaming, async fan-out)
- Module 03 [07_deployment.md](../../03_agentic_ai/notes/07_deployment.md) — exposing agentic systems via APIs and the stateful/stateless tradeoff
- Module 05 [02_aws_ai_ml_stack.md](../../05_AI_cloud_services/notes/02_aws_ai_ml_stack.md) — managed inference endpoints (SageMaker Endpoint) that abstract the framework choice
