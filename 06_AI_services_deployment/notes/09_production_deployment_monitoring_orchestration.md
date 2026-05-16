# Production Deployment, Monitoring, and Orchestration

## TL;DR

A production ML deployment has three concerns that the development setup does not: a **production-grade serving stack** (not `uvicorn --reload`), a **monitoring stack** (not `print()`), and a **pipeline orchestrator** (not "I'll run the training script next month"). The serving stack splits responsibilities: a **WSGI/ASGI worker** (Gunicorn + Uvicorn workers for FastAPI, Gunicorn alone for Flask) runs the Python app with multiple processes and proper signal handling; a **reverse proxy** (NGINX, Caddy, Traefik, or the cloud's managed load balancer) terminates TLS, applies routing rules, enforces rate limits, and shields the Python workers from slow clients and large bodies. For Python on Linux the canonical pair is **NGINX → Gunicorn(Uvicorn workers) → FastAPI**, each layer doing one job well.

**Deployment options for Python APIs** fall on a spectrum from "you operate everything" to "platform operates everything". **Bare VMs** (EC2, Compute Engine, Azure VM) give full control and the most operational burden. **Container orchestrators** (Kubernetes, ECS, Nomad) automate scheduling, scaling, and self-healing but require platform expertise. **Serverless containers** (Cloud Run, AWS App Runner, Azure Container Apps) run a container with autoscaling-to-zero behind a managed load balancer — usually the right default for stateless inference services with bursty traffic. **PaaS-style** (Vercel, Render, Fly.io, Heroku, Railway) bundle the deploy story with primitives that fit web apps; Vercel is the Next.js / serverless-function story most often used for the frontend, but supports Python functions in a more limited shape. Fully **managed ML endpoints** (SageMaker Endpoint, Vertex Endpoint, Azure ML Online Endpoint, Hugging Face Inference Endpoints) abstract the serving stack entirely — you provide the model and the inference handler, the platform provides everything else.

**Monitoring in production** has four layers. **Infrastructure** (CPU, memory, disk, network) — the operating-system metrics, scraped by node exporters and visualised in dashboards. **Application** (request rate, latency percentiles, error rate, in-flight requests) — emitted by the FastAPI app via Prometheus instrumentation. **Business / model** (prediction distribution, accuracy on ground truth, drift signals) — emitted by custom metrics and processed by drift libraries (Evidently, NannyML) or the cloud's managed offering. **Tracing** (distributed traces across services) — emitted with OpenTelemetry, collected by Jaeger / Tempo / Datadog / Honeycomb. The reference open-source stack is **Prometheus + Grafana + Loki + Tempo** ("the PLG stack"), all run in containers via **`docker compose`** for development. For production the same stack runs in Kubernetes or as a managed service (Grafana Cloud, Datadog, Honeycomb, New Relic).

**Pipeline orchestration** sits one layer above the deployed services: it runs the workflows that periodically *produce* what the services consume — training pipelines, evaluation runs, batch inference jobs, data refreshes. The two patterns are **time-based** (cron-like: run nightly) and **event-driven** (run when new data arrives, when drift is detected, when a model is registered). Tools: **Airflow** is the elder statesman, Python-first, mature, heavy; **Prefect** is the modern Python-first, lighter, "negative engineering" focus; **Dagster** is asset-centric (the data, not the task, is the unit); **Kubeflow Pipelines** and the cloud-native **Vertex / SageMaker / Azure ML Pipelines** are Kubernetes-native, ML-focused. For most ML teams in 2025, the choice is between Prefect (lean) and the cloud's native pipeline service (integrated). Airflow remains the default at large organisations with existing investment.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **WSGI / ASGI server** | The Python process running the app | Gunicorn (WSGI) or Gunicorn+Uvicorn workers (ASGI) |
| **Reverse proxy** | The HTTP layer in front of the Python app | NGINX, Caddy, Traefik, cloud LB |
| **TLS termination** | Decrypting HTTPS at the edge | At the proxy, not in the Python app |
| **Worker process** | One copy of the Python app | One per CPU is a starting heuristic |
| **Graceful shutdown** | Drain in-flight requests on SIGTERM | Avoid 502s on deploys |
| **Liveness probe** | "Is the process up?" | `/health` |
| **Readiness probe** | "Is the model loaded and ready to serve?" | `/ready` |
| **Autoscaling** | Horizontal pod / instance scaling on load | HPA in K8s, target CPU/QPS metric |
| **Blue-green / canary / rolling** | Deploy strategies | See note 08 |
| **Cloud Run / App Runner / Container Apps** | Serverless containers | Scales to zero, simple deploy |
| **Vercel / Render / Fly.io** | Developer-friendly PaaS | Quick deploys, fewer ML knobs |
| **Managed ML endpoint** | The cloud runs the serving stack | SageMaker / Vertex / Azure ML |
| **Prometheus** | Time-series database + scrape model | The de facto metrics standard |
| **Grafana** | Visualisation + alerting on top of Prometheus | The dashboard layer |
| **Loki** | Log aggregation, label-based | The PLG L |
| **Tempo / Jaeger** | Distributed tracing backend | The trace layer |
| **OpenTelemetry** | Vendor-neutral instrumentation | The standard SDK and protocol |
| **Docker Compose** (in prod context) | Multi-container local-or-single-host orchestration | Fine for self-hosted monitoring stack; not a multi-host scheduler |
| **Airflow / Prefect / Dagster** | Workflow orchestrators | For training pipelines and batch jobs |
| **Cron** | Time-based scheduler | The minimum viable orchestrator |
| **Event-driven trigger** | Run on drift/data/model events | EventBridge, Pub/Sub, Webhooks |

---

## The serving stack from edge to model

```
  HTTPS client
       │
       ▼
   ┌──────────────────────────┐
   │   Cloud Load Balancer    │   (or DNS direct to the proxy)
   └──────────────────────────┘
       │
       ▼
   ┌──────────────────────────┐
   │   NGINX                  │   TLS termination
   │                          │   request body size limits
   │                          │   path routing
   │                          │   gzip
   │                          │   rate limiting at edge
   └──────────────────────────┘
       │ HTTP (loopback or private)
       ▼
   ┌──────────────────────────┐
   │   Gunicorn               │   process manager
   │   (Uvicorn workers)      │   N worker processes
   │                          │   timeouts, graceful shutdown
   └──────────────────────────┘
       │
       ▼
   ┌──────────────────────────┐
   │   FastAPI app            │   business logic
   │                          │   loads model at startup
   │                          │   /health, /ready, /metrics
   └──────────────────────────┘
       │
       ▼
   ┌──────────────────────────┐
   │   Model (in-memory)      │   inference
   └──────────────────────────┘
```

Each layer does one job. Skipping NGINX is fine for low-stakes services on Cloud Run (the platform replaces it), but on a VM or in a pod with a public-facing port, NGINX (or equivalent) is non-negotiable for production.

---

## Gunicorn + Uvicorn for FastAPI

> Gunicorn is the WSGI process manager. Uvicorn workers turn it into an ASGI-capable runner. Together they run FastAPI in production.

### The command

```bash
gunicorn \
    -k uvicorn.workers.UvicornWorker \
    -w 4 \
    --bind 0.0.0.0:8000 \
    --timeout 60 \
    --graceful-timeout 30 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile - \
    src.api:app
```

| Flag | Purpose |
|---|---|
| `-k uvicorn.workers.UvicornWorker` | The ASGI worker class; required for FastAPI |
| `-w 4` | Number of worker processes |
| `--bind 0.0.0.0:8000` | Listen on the port |
| `--timeout 60` | Kill a worker stuck on a single request for >60s |
| `--graceful-timeout 30` | On shutdown, give workers 30s to drain |
| `--keep-alive 5` | Hold idle connections this long |
| `--max-requests 1000` | Restart a worker after N requests (mitigates memory leaks) |
| `--max-requests-jitter 100` | Randomness so workers don't restart in lockstep |
| `--access-logfile -` | Access logs to stdout |

### How many workers

| Workload | Rule of thumb |
|---|---|
| CPU-bound (sklearn predict, ONNX, light PyTorch) | `2 × CPU + 1` |
| Memory-heavy (large model in memory) | Fewer, to fit RAM; consider `--preload` to share memory |
| GPU-bound | `1` per GPU; batching inside |
| I/O-bound (calling LLM APIs) | Async handlers + more workers, profile to find the knee |

### `--preload`

```bash
gunicorn -k uvicorn.workers.UvicornWorker -w 4 --preload src.api:app
```

Loads the app in the master before forking workers. Workers share memory pages with the master (copy-on-write), so the model is loaded *once* into RAM and shared. Critical for large models where loading per-worker would OOM.

The cost: changes to the app require restarting Gunicorn; signal handling becomes more subtle. For ML serving, the trade is usually worth it.

### Graceful shutdown

On `SIGTERM`:
1. Gunicorn stops accepting new connections.
2. Existing requests have `--graceful-timeout` seconds to finish.
3. Workers are killed.

The orchestrator (Kubernetes, ECS, Cloud Run) sends SIGTERM and waits up to its own deregistration timeout. Set `--graceful-timeout` to be shorter than the orchestrator's, so workers exit cleanly within the window.

Without this, every deploy produces 502 errors on in-flight requests.

---

## NGINX as the reverse proxy

> The mature default. Caddy and Traefik are modern alternatives with simpler config; the architectural role is identical.

### A minimal config for a FastAPI service

```nginx
# /etc/nginx/conf.d/api.conf

upstream api_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    ssl_certificate     /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    client_max_body_size 5M;
    proxy_read_timeout 60s;

    gzip on;
    gzip_types application/json text/plain;

    location /health {
        access_log off;
        proxy_pass http://api_backend;
    }

    location / {
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Request-Id      $request_id;
        proxy_http_version 1.1;
        proxy_pass http://api_backend;
    }
}

server {
    listen 80;
    server_name api.example.com;
    return 301 https://$host$request_uri;
}
```

What this gives you:
- HTTPS with HTTP/2 enabled, HTTP→HTTPS redirect.
- Body size limit (prevents OOM by huge payloads).
- Timeouts.
- Gzip compression.
- The standard forwarded-proxy headers so the app sees the real client IP and protocol.
- `/health` log-silenced to avoid drowning logs with probe noise.

### Streaming responses

For SSE (LLM token streaming), disable buffering on the streaming endpoint:

```nginx
location /chat/stream {
    proxy_pass http://api_backend;
    proxy_buffering off;
    proxy_cache off;
    proxy_read_timeout 1h;
}
```

Without `proxy_buffering off`, NGINX buffers the whole response and the client sees a sudden dump instead of incremental tokens.

### Rate limiting at NGINX

```nginx
limit_req_zone $binary_remote_addr zone=perip:10m rate=10r/s;

server {
    location / {
        limit_req zone=perip burst=20 nodelay;
        proxy_pass http://api_backend;
    }
}
```

Per-IP rate limit, 10 req/s steady, 20 burst. For per-user limits you need a key derived from a header (the JWT subject), set in application config.

### TLS certificate management

- **Let's Encrypt** (free) with **Certbot** or **acme.sh**. Renews automatically every 60 days.
- Cloud-managed certificates (ACM on AWS, Google-managed certs, Azure Managed Certificate) when the load balancer terminates TLS.
- **Traefik** and **Caddy** do ACME automatically; one fewer thing to wire up.

---

## Deployment options compared

| Option | What you operate | What the platform operates | Right for |
|---|---|---|---|
| **Bare VM** (EC2, GCE, Azure VM) | OS, NGINX, Gunicorn, systemd, monitoring | Hardware, network | Full control, regulatory edge cases, custom setups |
| **VM with auto-scaling group** | Same + scaling config | Replaces unhealthy VMs | Stable predictable workloads |
| **Kubernetes** (EKS, GKE, AKS, self-managed) | App container, manifests, helm charts, K8s knowledge | Cluster control plane, infra reconciliation | Multi-service platforms with platform team |
| **ECS (EC2 or Fargate)** | Task definitions, service definitions | Schedulers, networking | AWS-centric workloads, less K8s complexity |
| **Cloud Run / App Runner / Container Apps** | Container image, env config | Scaling, TLS, ingress, autoscale-to-zero | Stateless services with spiky traffic |
| **PaaS** (Render, Fly.io, Railway, Heroku) | App code + minimal config | Everything else | Small services, fast time-to-market |
| **Vercel** | Frontend; serverless Python functions in limited shape | The entire serving stack | Frontends; some Python APIs |
| **Managed ML endpoint** (SageMaker, Vertex, Azure ML, HF Inference Endpoints) | Model + inference handler | Serving stack, scaling, monitoring | When the cloud's stack already fits |

### Picking

| Need | Pick |
|---|---|
| One small service, fast to ship, OK with cloud lock-in | Cloud Run / App Runner / Container Apps |
| Many services, real platform team | Kubernetes |
| Existing AWS-centric stack, no K8s appetite | ECS Fargate |
| Prototype / hackathon | Render / Fly.io / Hugging Face Spaces |
| Production ML inference on a managed surface | SageMaker / Vertex / Azure ML endpoints |
| LLM-specific managed inference | HF Inference Endpoints, OpenAI's hosted models, Anthropic's hosted models |
| Front-end + light backend | Vercel (frontend) + Cloud Run / Render (Python backend) |
| Complex orchestration and state | Kubernetes; don't fight Cloud Run for what it isn't |

### Notes on Vercel for Python APIs

Vercel is genuinely excellent for Next.js frontends. For Python it supports serverless functions via a `/api/` directory or by deploying ASGI apps, but:
- Cold start matters more than for long-running container deployments.
- Memory limits are stricter (the free / hobby tier in particular).
- Large model files in a serverless function are an anti-pattern.
- For an ML inference API, Cloud Run / App Runner / Container Apps is usually a better fit; Vercel is a fine target for the frontend that calls them.

The course's deployment exercise on Vercel works because the demo model is small; for production ML serving, expect to graduate.

---

## Production checklist for serving a Python API

- [ ] Containerised, image pinned by digest in deploy config.
- [ ] Runs as non-root inside the container.
- [ ] Liveness probe on `/health`, readiness on `/ready`.
- [ ] TLS terminated at the proxy/load balancer.
- [ ] Body size limit + rate limits at the proxy.
- [ ] Gunicorn `--graceful-timeout` shorter than the orchestrator's deregistration timeout.
- [ ] `--max-requests` set to mitigate slow leaks.
- [ ] Structured logging to stdout, scraped by a log aggregator.
- [ ] Prometheus `/metrics` endpoint exposed.
- [ ] OpenTelemetry tracing wired up (even if you only export to stdout in dev).
- [ ] Secrets injected at runtime, not baked into the image.
- [ ] Autoscaling rules with min and max bounds.
- [ ] Documented rollback procedure.
- [ ] On-call runbook with the top 3 alerts and their playbooks.

---

## Monitoring: what to watch

### Infrastructure layer

| Metric | Why |
|---|---|
| CPU usage per container | Saturation drops throughput, raises latency |
| Memory usage per container | OOM-killed pods reset state |
| Disk I/O / disk full | Logs filling disk, model artefacts not cleaned |
| Network I/O | Egress is metered; spikes are bills |
| Container restarts | If frequent, something is crashing |

The cloud's managed monitoring (CloudWatch, Cloud Monitoring, Azure Monitor) covers this; in self-hosted, the **node_exporter** + Prometheus combination is standard.

### Application layer

| Metric | Why |
|---|---|
| Request rate (RPS) per endpoint | Traffic shape, capacity planning |
| Latency: p50, p95, p99 | The tail is what users feel |
| Error rate (4xx / 5xx) per endpoint | Health of business logic |
| In-flight requests | Saturation indicator |
| Inference time per request | The ML-specific latency component |
| Worker process restarts | Memory leaks, bugs |

`prometheus-fastapi-instrumentator` gives you the first four out of the box; the rest you instrument.

### Business / model layer

| Metric | Why |
|---|---|
| Prediction value distribution (binned histogram) | Detect output drift |
| Class prediction proportions | Detect label drift |
| Feature distribution (per feature, binned) | Detect input drift |
| Accuracy on ground-truth labels (when available, lagged) | The ultimate quality signal |
| Model version label on all metrics | So you can compare versions |

The drift libraries (Evidently, NannyML, WhyLabs) compute these from a stream of inputs and predictions, compared to a reference window.

### Tracing layer

A trace shows a request's full path: API gateway → FastAPI handler → DB query → upstream API → response. Latency hot spots become obvious. The standard:

- Instrument with **OpenTelemetry** (OTel) SDK.
- Send to a backend: Jaeger (open source), Tempo (Grafana, S3-backed), Datadog, Honeycomb.

```python
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

FastAPIInstrumentor.instrument_app(app)
```

Every endpoint emits a span automatically; sub-spans for DB queries, HTTP calls, etc. are picked up by the matching OTel instrumentation libraries.

---

## The reference monitoring stack: Prometheus + Grafana + (Loki) + (Tempo)

> Open source, self-hostable, the de facto standard. The same configs run on a laptop via `docker compose` or in production via Kubernetes.

### Prometheus: metrics

Scrape-based: Prometheus pulls `/metrics` endpoints on a schedule, stores time series locally. The application *exposes* metrics; Prometheus *scrapes* them.

```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)   # /metrics endpoint
```

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'fastapi-app'
    scrape_interval: 15s
    static_configs:
      - targets: ['api:8000']
```

### Grafana: dashboards

Reads from Prometheus (and Loki, Tempo, others). Dashboards are JSON; teams commit them to Git for versioning.

A baseline dashboard for a model API:
- Request rate by endpoint.
- p50/p95/p99 latency by endpoint.
- Error rate by status code.
- Inference time histogram.
- Model version distribution (label-based).
- In-flight requests.

### Loki: logs

Log aggregation, label-based (not full-text indexing) — far cheaper than ELK at scale. Apps send logs via stdout to a sidecar (Promtail, Fluent Bit, Vector) which ships them to Loki.

### Tempo: traces

OTel traces in, queryable trace UI in Grafana. The PLG stack with Tempo added is the OSS pattern that covers all four observability pillars.

### Running it locally with Docker Compose

```yaml
# docker-compose.monitoring.yml
services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    volumes:
      - grafana-data:/var/lib/grafana

  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"

  tempo:
    image: grafana/tempo:latest
    command: [ "-config.file=/etc/tempo.yaml" ]
    volumes:
      - ./tempo.yaml:/etc/tempo.yaml

volumes:
  grafana-data:
```

```bash
docker compose -f docker-compose.yml -f docker-compose.monitoring.yml up
```

The development monitoring stack is now one command. The same compose file (with persistence volumes) runs the monitoring stack on a single-host self-hosted setup; for production at scale the same stack runs as charts on Kubernetes.

### Alerts

Alerts live in Prometheus (or Grafana, recently). Express conditions in PromQL; route via Alertmanager to Slack / PagerDuty / email.

```yaml
# alerts.yml
groups:
  - name: api
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: page
        annotations:
          summary: "5xx error rate > 5%"
      - alert: PredictionLatencyP99
        expr: histogram_quantile(0.99, rate(prediction_latency_seconds_bucket[5m])) > 0.5
        for: 10m
        labels:
          severity: warn
        annotations:
          summary: "p99 prediction latency > 500ms"
```

Two alerts you should not skip:
- **Error rate** above the SLO budget.
- **Readiness probe failures** (means the orchestrator is restarting pods).

---

## Pipeline orchestration

> The serving stack runs the model online. The orchestrator runs the workflows that produce the model and its evaluations offline.

### Why a dedicated orchestrator (not cron)

Cron schedules jobs. An orchestrator does more:
- DAG dependencies (training waits for feature pipeline).
- Retries with backoff.
- State across runs (last run timestamp, partition watermark).
- Backfills.
- A UI for run history and failure inspection.
- Triggers beyond time (events, sensors, manual).

For one-off scripts cron is fine. For "feature engineering → training → evaluation → registration → deploy" with dependencies, an orchestrator pays back fast.

### The contenders

| Tool | Style | Pros | Cons |
|---|---|---|---|
| **Airflow** | Python DAGs, mature ecosystem | Battle-tested, huge community | Heavy, scheduler complexity, opinionated |
| **Prefect** | Python flows, decorator-driven | Lighter, modern UX, hybrid execution (cloud + local) | Smaller ecosystem, somewhat newer abstractions |
| **Dagster** | Asset-centric, "the data is the unit" | Strong typing, great for data-heavy ML | Different mental model, learning curve |
| **Kubeflow Pipelines** | K8s-native, ML-focused | Cloud-portable, ML primitives | K8s required, heavier |
| **Vertex Pipelines** | GCP-native | Managed, integrated with Vertex ML | GCP lock-in |
| **SageMaker Pipelines** | AWS-native | Managed, integrated with SageMaker | AWS lock-in |
| **Azure ML Pipelines** | Azure-native | Managed, integrated | Azure lock-in |
| **Argo Workflows** | K8s-native, YAML | Lightweight, flexible | More DIY |
| **Step Functions** (AWS) | State machines | Serverless, simple | Less ML-specific |
| **Cron** | Time-based shell | Trivial | No state, no DAG, no retry |

### A minimal Prefect flow

```python
from prefect import flow, task
import datetime as dt

@task(retries=3, retry_delay_seconds=60)
def extract_features(date: dt.date) -> str:
    # ... pull features, write to a partition ...
    return f"s3://features/{date}.parquet"

@task
def train(features_path: str) -> str:
    # ... train, log to MLflow ...
    return "models:/my-model/3"

@task
def evaluate(model_uri: str) -> dict:
    # ... evaluate on holdout, return metrics ...
    return {"auc": 0.87}

@task
def maybe_promote(model_uri: str, metrics: dict) -> None:
    if metrics["auc"] >= 0.85:
        # transition to Production
        ...

@flow(name="daily-retrain")
def daily_retrain(date: dt.date | None = None):
    date = date or dt.date.today() - dt.timedelta(days=1)
    features_path = extract_features(date)
    model_uri = train(features_path)
    metrics = evaluate(model_uri)
    maybe_promote(model_uri, metrics)

if __name__ == "__main__":
    daily_retrain()
```

Deploy the flow with a Prefect schedule and it runs daily. Failures are retried. Logs and lineage land in the Prefect UI.

### Triggers

| Trigger | Pattern |
|---|---|
| **Schedule** | "Daily at 03:00 UTC" |
| **Sensor / poll** | "When `s3://data/raw/{date}.parquet` exists" |
| **Event** | "When the drift alert fires" (EventBridge / Pub/Sub) |
| **Manual** | "Operator clicks Run" |
| **Upstream completion** | "When the upstream pipeline completes" |

Wiring an event-driven retrain on drift: monitoring detects drift → emits an event → orchestrator triggers the retrain flow → flow runs the standard pipeline → registry updated → deploy job promotes the new version.

---

## Common patterns

| Pattern | Notes |
|---|---|
| **Health-aware load balancing** | LB removes unhealthy pods automatically based on readiness |
| **Autoscaling on QPS or queue depth** | Scale based on the work, not just CPU |
| **Scale-to-zero** for cold paths | Free serverless containers when not serving |
| **Sidecar log shipper** | Promtail / Fluent Bit reads container logs, ships to Loki |
| **GitOps for K8s manifests** | Argo CD watches the manifest repo, reconciles cluster state |
| **Helm charts** for service manifests | Templated, parameterised, versioned |
| **Pre-warmed canary** | Start the canary, wait for `/ready`, then route traffic |
| **Pipeline-of-pipelines** | An orchestrator running other orchestrators (e.g., Prefect kicking off Vertex Pipelines) |
| **Idempotent pipelines** | Re-runs are safe and produce the same result |
| **Pipeline-as-code, manifests-as-code** | Everything in Git |

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Running `uvicorn --reload` in prod | Process restarts on file change, slow, single-process | Gunicorn + Uvicorn workers |
| Single worker on multi-core host | CPU underused | Tune `-w`; for GPU, use 1 worker + batching |
| No `--graceful-timeout` | 502s on every deploy | Set it shorter than the orchestrator's drain |
| `proxy_buffering on` for SSE | Streaming UX is dead | Disable for streaming routes |
| TLS in the app process (not the proxy) | Slow, missing TLS features | Terminate at NGINX / load balancer |
| `client_max_body_size` default 1M | Big requests 413 | Bump if you really need it; otherwise document the limit |
| Probes hitting `/predict` | Slow, wakes the model | Cheap dedicated `/health` |
| Cloud Run with model loaded at request time | Cold start = full model load | Load at startup; use min-instances if cold starts hurt |
| Monitoring only CPU | Quality degrading silently | Model-quality metrics, drift signals |
| Alerts on infrastructure only | Bad model, no alert | Alerts on application + model layers too |
| Alert fatigue | On-call ignores alarms | Tune thresholds; consolidate; remove the noisy ones |
| Logs without request ID | Tracing through services impossible | Inject + propagate `X-Request-Id` |
| Cron job that "should be" a pipeline | Failures silent, no DAG, no retries | Use an orchestrator |
| Orchestrator running the heavy work inline | Tasks contending for the same worker | Offload heavy tasks to a container/cluster, the orchestrator just coordinates |
| Long-lived secrets in pipeline runner | Compromise spreads | Short-lived credentials, workload identity |
| Pipeline depending on a fragile API | Random failures | Retries with backoff, idempotent steps |

---

## When to use what

| Need | Pick | Why |
|---|---|---|
| Run FastAPI in production | **Gunicorn (Uvicorn workers)** + **NGINX** or cloud LB | Standard, predictable |
| Reverse proxy | **NGINX** (mature), **Caddy** (auto-TLS), **Traefik** (k8s-native) | Pick by ecosystem fit |
| Self-hosted ML inference | Container behind NGINX on VM, or K8s for many services | Operational scale |
| Spiky/bursty inference, stateless | **Cloud Run / App Runner / Container Apps** | Scale-to-zero |
| Stable predictable inference | VM auto-scaling group or K8s with min replicas | Avoid cold starts |
| Managed ML serving | **SageMaker Endpoint / Vertex Endpoint / Azure ML Online Endpoint** | When the platform fits |
| LLM serving | **HF Inference Endpoints**, **vLLM / TGI** on K8s, or provider APIs (OpenAI, Anthropic) | Match the model |
| Monitoring stack, OSS | **Prometheus + Grafana + Loki + Tempo** | Battle-tested, vendor-neutral |
| Monitoring stack, managed | **Datadog / Honeycomb / Grafana Cloud / New Relic** | When ops headcount is the bottleneck |
| Drift monitoring | **Evidently** / **NannyML** / cloud-managed | Pick by ecosystem |
| Pipeline orchestration, OSS | **Prefect** (modern), **Airflow** (existing investment), **Dagster** (asset-first) | Pick by team's stack |
| Pipeline orchestration, cloud-managed | **Vertex / SageMaker / Azure ML Pipelines** | When tied to that cloud |
| Trigger retrains on drift | Orchestrator hooked to monitoring events | Event-driven L1 pattern |
| Front-end + Python backend | Vercel (frontend) + Cloud Run / Render (backend) | Right tool per layer |

---

## See also

### Other notes
- [01_mlops_foundations.md](01_mlops_foundations.md) — the MLOps maturity model that monitoring + orchestration operationalise
- [04_model_serving_with_fastapi.md](04_model_serving_with_fastapi.md) — the serving code this stack runs in production
- [06_api_security_and_authentication.md](06_api_security_and_authentication.md) — TLS termination and auth at the proxy
- [07_containerization_with_docker.md](07_containerization_with_docker.md) — the image that ends up behind the proxy
- [08_ci_cd_pipelines.md](08_ci_cd_pipelines.md) — the pipeline that pushes images and triggers deploys

### Cross-module
- Module 02 [07_rag_production.md](../../02_large_language_models/notes/07_rag_production.md) — production patterns specific to LLM/RAG endpoints (caching, streaming, autoscaling)
- Module 03 [07_deployment.md](../../03_agentic_ai/notes/07_deployment.md) — running stateful agents in production
- Module 05 [02_aws_ai_ml_stack.md](../../05_AI_cloud_services/notes/02_aws_ai_ml_stack.md) — SageMaker Endpoints and the AWS monitoring stack
- Module 05 [07_hybrid_and_multi_cloud_patterns.md](../../05_AI_cloud_services/notes/07_hybrid_and_multi_cloud_patterns.md) — when production deployment spans clouds and what changes
