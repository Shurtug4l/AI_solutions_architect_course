# IaaS, Open Source AI, and On-Premises Deployment

## TL;DR

Not every AI workload belongs on a managed PaaS. The alternative path runs through **IaaS** (the cloud provider sells you raw infrastructure, you bring everything else) and **OSS** (open-source models, frameworks, and tooling running on infrastructure you control, cloud or on-prem). The deployment options for an AI service collapse into three tiers: **fully-managed PaaS** (highest abstraction, highest lock-in), **manual deploy on cloud IaaS** (the cloud provider runs the hardware, you run the software), and **on-premises** (you run both: maximum privacy and control, highest operational cost). A second axis cuts orthogonally: **third-party APIs**, paid or free, that you compose into your application regardless of where the rest runs. The **definition of Open Source AI** is sharper than people assume: for classical ML and DL, the source code, datasets, and hyperparameters must be public; for LLMs (which cannot realistically be retrained from scratch), the **weights** must be publicly distributable. The benefits are open innovation, reduced proprietary lock-in, and lower cost-of-switching; the costs are non-automatic scaling, expensive hardware (especially for DL and LLMs), and security responsibility shifted onto you. The on-prem deployment toolchain has stabilised around a known stack: **Docker** for packaging, **Kubernetes or Docker Compose** for orchestration (Compose for small static deployments, K8s for production with autoscaling and cross-platform portability), **FastAPI** for serving, **MLflow** for experiment and model lifecycle tracking, **Prometheus + Grafana** for metrics and dashboards. Hugging Face has become the de facto registry: pre-trained models for classical ML, transformers, vision, and LLMs are downloaded and run locally with a few lines of code, often with a base image like `python:3.11-slim` and an environment-variable contract for configuration (the sentiment-analysis exercise pattern: choose IT or EN model at container start via the `LANG` env var).

## Cheatsheet

| Concept | One-line | When it shows up |
|---|---|---|
| **IaaS** | Cloud provider sells hardware/VMs, you run the rest | Cost control, custom stack |
| **OSS AI** | Open-source models, code, and weights | Reduce lock-in, full control |
| **Fully-managed deploy** | PaaS endpoint, provider runs everything | Fastest TTM, highest lock-in |
| **Manual cloud deploy** | Your code on the provider's VMs/containers | Cost control + flexibility |
| **On-prem deploy** | Hardware you own | Maximum privacy, predictable cost |
| **Third-party APIs (paid)** | OpenAI, Anthropic, Mistral cloud, etc. | Best-of-breed without owning the model |
| **Third-party APIs (free)** | Hugging Face Inference, public endpoints | Prototyping, low volume |
| **OSS LLMs** | Llama (4.x), Mistral (Large 2, Small 3, Mixtral), Gemma, Qwen | Run frontier-class models locally |
| **HF Transformers** | Library for NLP/vision models | Industry default |
| **Diffusion models** | Stable Diffusion family | OSS image generation |
| **scikit-learn** | Classical ML on tabular data | Baseline + production-ready pipelines |
| **Docker** | Containerise the model + deps + serving code | Reproducibility, portability |
| **Docker Compose** | Multi-container declarative orchestration | Small static deployments |
| **Kubernetes** | Container orchestration at scale | Production with autoscaling |
| **FastAPI** | REST framework for Python serving | The Python serving default |
| **MLflow** | Experiment tracking, model registry | Lifecycle governance, OSS alternative to managed registries |
| **Prometheus** | Metrics collection | Hardware + software metrics |
| **Grafana** | Dashboards on top of metrics | Visual observability |
| **Hugging Face** | Models + datasets registry | The OSS distribution hub |

---

## The deploy spectrum: PaaS, IaaS, on-prem

> Three discrete points on a single axis: **how much of the stack do you operate yourself?**

| Tier | What the provider owns | What you own | Privacy | Cost shape |
|---|---|---|---|---|
| **Fully-managed PaaS** | Infrastructure + runtime + scaling + model | Application code + data + integration | Bound by provider contract | OPEX, per-call |
| **Manual on cloud IaaS** | Hardware + virtualisation | OS + dependencies + deployment + scaling + serving | Bound by provider physical location | OPEX, per-VM |
| **On-premises** | Nothing | Everything | Maximum | CAPEX + OPEX |

The choice is not abstract: it determines who you call when something breaks, where your data is at rest, how fast you can scale, and how much engineering bandwidth disappears into operations.

A subtlety: **IaaS does not mean "no managed services"**. You can run a SageMaker job from an EC2 box, or a Vertex AI endpoint from a custom GKE cluster. The label refers to the **primary unit** you operate; you compose managed services into it as it makes sense.

### Where third-party APIs fit

Even fully-managed and self-managed deployments rarely build everything from scratch. They call out to **third-party APIs** for capabilities they do not want to own:

| Category | Examples | Free? |
|---|---|---|
| **Frontier LLMs** | OpenAI, Anthropic, Mistral, Cohere | Mostly paid |
| **Specialised models** | OCR services, translation, code search | Paid |
| **OSS inference services** | Hugging Face Inference, Replicate, Together | Free tier + paid |
| **Free or community APIs** | Public Hugging Face endpoints, model demos | Yes, with rate limits |

The architecture is **not closed**: a "self-hosted" service can still depend on a third-party API for a specific capability (e.g., GPT-4 for the hardest reasoning while a local model handles the rest).

---

## What "Open Source AI" means

> **OSS AI**: any AI system where models, tools, source code, and datasets are publicly accessible and can be used, modified, and redistributed freely, without proprietary constraints.

The definition has nuance based on the **kind** of model.

| Family | What "open source" requires |
|---|---|
| **Classical ML** | Source code public; training data and hyperparameters public; models can be retrained from scratch |
| **Deep Learning** | Source code public; training data and hyperparameters public; pretrained weights commonly distributed |
| **LLMs** | Retraining from scratch is impractical for most consumers (compute prohibitive), so the **weights must be publicly distributable** for the model to be meaningfully open source |

The LLM nuance is why people argue over what "open" means. A model with public weights but undisclosed training data is **weights-open**, not fully open source. The course's definition treats public weights as the minimum bar for LLMs while keeping the stronger bar for ML and DL.

### Why it matters

| Benefit | Detail |
|---|---|
| **Open innovation** | Developers and companies contribute, improve, customise the technology |
| **Reduced lock-in** | Not dependent on a single proprietary vendor |
| **Lower switching cost** | Migrating between providers is a deployment change, not a rewrite |
| **Audit and transparency** | The model can be inspected, fine-tuned, and debugged |

### The costs

| Cost | Detail |
|---|---|
| **Non-automatic scaling** | You build the autoscaling, the load balancing, the failover |
| **Hardware** | DL and LLMs often need GPUs; the bill is real, especially for fine-tuning |
| **Security** | The patch cycle, the supply-chain audit, the runtime isolation are all yours |
| **Operations** | Monitoring, alerting, on-call, incident response |

The OSS path **wins long-term at scale** because per-unit cost is lower than per-call APIs. It **loses short-term at small scale** because the fixed cost of running the stack is non-trivial.

### The OSS toolbox

| Tool / Model | Used for |
|---|---|
| **scikit-learn** | Classical ML on tabular data; the default Python ML library |
| **Llama 4.x, Mistral (Large 2, Small 3, Mixtral), Gemma, Qwen** | Open-weights LLM families spanning 1B to 400B parameters, runnable on consumer-to-enterprise hardware |
| **Stable Diffusion** | Image generation, runnable on a single GPU |
| **HF Transformers** | NLP and vision models from BERT to LLaMA, with a uniform API |
| **Hugging Face Hub** | The registry: 1M+ pre-trained models, datasets, model cards |

Hugging Face is the centre of gravity: it is where most OSS models are published, where the most common Python interface (`transformers`) lives, and where downstream tools (LangChain, Ollama) source models from.

---

## The on-premises deployment toolchain

> **The toolchain has stabilised**. The same five categories of tools cover most production on-prem ML deployments.

| Category | Default tool | Why |
|---|---|---|
| **Deploy / packaging** | **Docker** | Reproducibility, dependency isolation, portability |
| **Orchestration** | **Kubernetes** (production) / **Docker Compose** (simple) | Scaling, resource management |
| **Training core** | Python (scikit-learn, PyTorch, TensorFlow) | The model code itself |
| **Observability** | **Prometheus** + **Grafana** | Metrics + dashboards |
| **Serving** | **FastAPI** | REST framework for Python ML services |
| **Tracking** | **MLflow** | Experiment tracking, model registry, lifecycle |

### Docker: the packaging layer

| Benefit | Detail |
|---|---|
| **Identical behaviour** across OSes and Python versions | The same image runs on dev laptops, staging, prod, on-prem and cloud |
| **Dependency management** | Critical for ML: PyTorch/TensorFlow versions, CUDA, numpy pin everything |
| **Deploy as code** | The `Dockerfile` is the deployment specification |
| **Public ecosystem** | The HF, NVIDIA, and Python base images cover most needs |

A typical AI service Dockerfile starts from `python:3.11-slim`, installs the model dependencies, copies the FastAPI app, and exposes the serving port. Environment variables parameterise the runtime (e.g., the `LANG` variable in the section 5 exercise that selects between an Italian and an English sentiment model).

### Compose vs Kubernetes

| Tool | When to pick it |
|---|---|
| **Docker Compose** | Small deployments, no autoscaling, a handful of containers, single host |
| **Kubernetes** | Production with autoscaling, multi-host, rolling deploys, advanced networking, cross-platform portability |

The decision is not "Compose if small, K8s if big": it is about **operational complexity vs. capability**. K8s gives autoscaling, self-healing, and declarative deployment; in exchange, it demands an operator who actually understands it. Compose is sufficient for any workload that fits on a single machine and does not need elastic scaling.

### FastAPI: the serving layer

| Property | Detail |
|---|---|
| **Why FastAPI** | Async by default, automatic OpenAPI docs, type-checked with Pydantic, fast (Starlette + Uvicorn) |
| **Typical pattern** | One endpoint per model, request/response schemas, async handler that calls the model |
| **Production hardening** | Run with Uvicorn workers behind a reverse proxy (Nginx, Traefik), set timeouts and request limits |

Alternatives exist (Flask, BentoML, TorchServe, Triton), but FastAPI is the default in OSS Python ML stacks because it is fast to build, easy to read, and integrates cleanly with the rest of the toolchain.

### MLflow: the lifecycle layer

The OSS answer to SageMaker / Vertex AI's model registries. Tracks experiments (parameters, metrics, artefacts), versions models, supports deployment to multiple targets.

The minimum value: **reproducibility**. With MLflow, the team can answer "what data, code, and parameters produced this model?" months later. Without it, that question is unanswerable, and the project becomes brittle.

### Prometheus + Grafana: the observability layer

| Tool | Role |
|---|---|
| **Prometheus** | Pulls metrics from instrumented services and infrastructure |
| **Grafana** | Dashboards and alerting on top of Prometheus (and other sources) |

For an ML service:
- **Hardware metrics** (CPU, RAM, GPU utilisation) from node exporters.
- **Software metrics** (request rate, latency, errors) from FastAPI middleware.
- **ML metrics** (prediction distribution, confidence drift) from custom exporters.

The stack is the OSS default because it is free, mature, and integrates with every modern container runtime.

---

## Designing an on-prem AI service: the section-5 pattern

The exercise (sentiment analysis, IT/EN, multi-lingual) makes the standard pattern concrete:

| Component | Implementation |
|---|---|
| **Model** | HuggingFace: `MilaNLProc/feel-it-italian-sentiment` (IT), `distilbert-base-uncased-finetuned-sst-2-english` (EN) |
| **Serving** | FastAPI app, single `/predict` endpoint |
| **Containerisation** | Base image `python:3.11-slim`, internal port 5000, external port 5012 |
| **Configuration** | `LANG` environment variable (`IT` or `EN`) selected at container start |
| **Run** | `docker run -e LANG=IT -p 5012:5000 ...` |

This pattern generalises: most OSS deployments look like **HF model + FastAPI + Dockerfile + env-var config**. The variations are which model and which extras (vector store, prompt template, post-processing) the application layer adds on top.

---

## Deploying the image: cloud vs on-prem registries

The image built locally is identical to the image that runs in production; the question is **where it gets pulled from**. Two options:

| Option | Detail |
|---|---|
| **Cloud container registry** | Docker Hub, AWS ECR, Azure ACR, GCP Artifact Registry. The image lives in the registry; the runtime (cloud or on-prem) pulls it |
| **Local / private registry** | An OSS registry inside the organisation's network. Required when the image itself contains weights or code that should not leave the perimeter |

The "deploy of an image on cloud" exercise in section 5 is the bridge between **building locally** and **running in production**: the same Dockerfile that ran on the developer's laptop pushes to a registry and pulls onto a cloud VM, with no code change.

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Picking OSS without estimating ops cost | The model works but operations burn the team | TCO over 12-24 months, including on-call and retraining cycles |
| Docker without GPU passthrough on a GPU host | Model runs on CPU silently, slow | Use `--gpus all` on Docker, or NVIDIA's container runtime |
| Kubernetes for a workload that fits on one host | Operational overhead exceeds benefit | Use Compose; switch to K8s when scaling/HA requirements become real |
| FastAPI in production without Uvicorn workers | Single-threaded, falls over under load | `uvicorn --workers N`, behind a reverse proxy |
| MLflow not used; no experiment tracking | Cannot reproduce a model six months later | Wire MLflow from day one, even for solo work |
| Prometheus configured but no alerts wired | Dashboards full of red, nobody paged | Alertmanager rules tied to a real notification channel (Slack, PagerDuty) |
| HF weights downloaded at request time | Cold start of tens of seconds, unstable behaviour | Bake the model into the image or volume-mount it |
| `python:3.11` instead of `python:3.11-slim` | Bloated images (1+ GB), slow pulls | Use slim base, multi-stage builds for compile dependencies |
| Hard-coding model paths and tokens | Cannot rotate secrets, cannot reuse the image | Environment variables for all config and secrets |
| Mixing IT and EN model in one container | Memory bloat, both loaded for nothing | One container per language (or per model), select via env var as per the exercise |
| "Open source" used loosely | A model with hidden training data is treated as fully open | Check the model card: weights, code, training data, license all matter |

---

## When to use what

| Need | Pick |
|---|---|
| Fast prototype, no ops team | **Managed PaaS** (SageMaker, Vertex AI, Azure ML) |
| Cost control at scale on cloud hardware | **Manual deploy on IaaS** + OSS stack |
| Maximum privacy, regulated data | **On-prem** with OSS models |
| Best-of-breed capability the OSS world does not have | **Third-party API** (OpenAI, Anthropic) called from your stack |
| Reduce vendor dependency | **OSS model** + portable container |
| Tabular ML on internal data | **scikit-learn + FastAPI + Docker** |
| NLP or vision on internal data | **HF Transformers + FastAPI + Docker** |
| LLM with frontier capability, on-prem | **Llama / Mistral** on GPU hosts |
| Image generation | **Stable Diffusion** |
| Container orchestration, small | **Docker Compose** |
| Container orchestration, production | **Kubernetes** |
| Experiment tracking and model registry, OSS | **MLflow** |
| Observability, OSS | **Prometheus + Grafana** |
| Avoid sending sensitive data to a third party | OSS model in your perimeter |
| Multi-tenant SaaS with cost control | OSS model + per-tenant rate limits |

---

## See also

### Other notes
- [01_aiaas_and_cloud_architecture_fundamentals.md](01_aiaas_and_cloud_architecture_fundamentals.md) — the abstract layers that on-prem stacks reimplement in OSS form
- [02_aws_ai_ml_stack.md](02_aws_ai_ml_stack.md), [03_azure_ai_ecosystem.md](03_azure_ai_ecosystem.md), [04_google_cloud_vertex_ai_data_first.md](04_google_cloud_vertex_ai_data_first.md) — the PaaS alternatives this note compares against
- [06_paas_vs_iaas_vs_oss_decision_framework.md](06_paas_vs_iaas_vs_oss_decision_framework.md) — direct comparison: when each model wins
- [07_hybrid_and_multi_cloud_patterns.md](07_hybrid_and_multi_cloud_patterns.md) — most real systems mix at least PaaS and OSS

### Cross-module
- Module 02 [02_introduction_llm.md](../../02_large_language_models/notes/02_introduction_llm.md) and the rest of module 02 — the OSS LLMs (Llama, Mistral) referenced here
- Module 03 [04_frameworks.md](../../03_agentic_ai/notes/04_frameworks.md) — LangChain / LangGraph deployments often follow the FastAPI + Docker pattern
- Module 03 [07_deployment.md](../../03_agentic_ai/notes/07_deployment.md) — agent deployment overlap (container, secrets, stateless serving)
- Module 02 PRJ `02_large_language_models/_PRJ_rag_system_for_company_knowledge/` — a concrete OSS local stack: Ollama, ChromaDB, BM25, no paid APIs
