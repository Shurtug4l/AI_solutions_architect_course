# AI-as-a-Service and Cloud Architecture Fundamentals

## TL;DR

**AI as a Service (AIaaS)** is the umbrella for any AI capability consumed through a cloud provider (pretrained API, custom-model platform, managed LLM) under a pay-as-you-go contract. It splits the operational surface in two: the **provider** owns the model and the infrastructure; the **consumer** owns integration, data, application security, and MLOps-of-consumption (versioning the prompts, the wrappers, the monitoring). The democratisation gain (a four-person team gets vision and NLP without owning GPUs) is paid back in **vendor lock-in**, **black-box observability**, and **data residency** constraints that hit hard under GDPR. The choice **cloud vs on-premises** is not "better or worse" but a tradeoff of axes: cloud wins on elasticity, time-to-market, and access to accelerators; on-prem wins on deterministic latency, full architectural control, data sovereignty, and predictable cost at scale. An **ML system in the cloud** is a pipeline with five layers (**data → feature engineering → training → serving → observability**), each with its own design choice (multi-tenant storage strategy, online vs batch serving, classical metrics vs ML-specific drift signals). The discipline that holds the pipeline together is **MLOps**, with three "C"s: **CI** (versioning code, data, models; tests on transformations), **CD** (automated rollout across dev/staging/prod), and **CT** (continuous training triggered by data or model drift).

## Cheatsheet

| Concept | One-line | When it shows up |
|---|---|---|
| **AIaaS** | Cloud-delivered AI consumed via API or managed platform | Every "we add AI to product X" project |
| **Pretrained API** | Ready models behind REST, pay-per-call | Fast time-to-market, generic tasks |
| **Custom-model platform** | Managed training of your own models | When generic APIs are not enough |
| **Shared responsibility** | Provider owns infra/model, consumer owns data/integration | Every PaaS contract |
| **Vendor lock-in** | Cost of switching provider | The strategic risk of AIaaS |
| **Cloud strengths** | Elasticity, accelerators on-demand, fast TTM | Variable demand, MVPs, GenAI |
| **On-prem strengths** | Deterministic latency, sovereignty, predictable cost | Regulated data, edge, low-latency SLAs |
| **Multi-tenancy** | Multiple customers share infra with isolated data | Storage design in SaaS-style products |
| **ML pipeline (5 layers)** | Data → features → training → serving → observability | Every production AI system |
| **MLOps 3 Cs** | CI (code/data/model), CD (release), CT (retrain) | The lifecycle that keeps a model alive |
| **Sync online serving** | Low latency, request/response | Chat, classification at request time |
| **Async serving** | Queue-based, more resilient, higher latency | Heavy inference, OCR pipelines |
| **Batch/offline serving** | Predictions on big windows, cheaper | Nightly scoring, recommendations refresh |
| **Classical observability** | Latency, throughput, error rate | Standard SRE practice |
| **ML observability** | Data drift, concept drift, feature freshness | Specific to ML systems |

---

## AI as a Service: definition and shape

> **AIaaS**: access AI capabilities (ML, predictive analytics, vision, NLP) through APIs or managed platforms, without owning the AI infrastructure, on a pay-as-you-go contract.

The category is broad and worth unpacking.

| Sub-type | What you consume | Examples |
|---|---|---|
| **Frontier LLM via chat/API** | Pretrained generative models | ChatGPT, Claude, DeepSeek |
| **Task-specific pretrained APIs** | NLP (classification, NER, translation), vision (OCR, detection), speech, recommendations | Vision API, Translation API, Comprehend |
| **Managed ML platforms** | Training, AutoML, feature engineering, experiment tracking, model registry | SageMaker, Vertex AI, Azure ML |

### The structural distinction: pretrained API vs custom-model platform

**Pretrained APIs** trade control for speed: you get a working model with a documented contract, integrated in hours, billed per call. The cost is **opaqueness** (you cannot inspect or improve the model) and **drift you cannot fix** (the provider updates the model on their schedule).

**Custom-model platforms** trade speed for control: you bring data and own the training loop, the artefacts, and the deployment. The cost is the team you need to operate them (data engineers, MLOps, observability).

The wrong choice in each direction is expensive: building a custom-vision model when Vision API would do is a year of wasted engineering; using a generic API when the domain needs a fine-tuned model produces a feature nobody can rely on.

### Strengths

- **Democratisation**: small teams and SMEs get capabilities (vision, speech, LLMs) that previously required a dedicated R&D function.
- **Time-to-market**: a working prototype in days, not quarters.
- **Elastic scaling**: capacity grows and shrinks with traffic.
- **Continuous improvement**: models behind the API often improve transparently as the provider retrains them.

### Weaknesses (the strategic ones)

- **Vendor lock-in** on API contract and model specifics. Migrating from one provider to another usually means a non-trivial rewrite. In thin markets (frontier LLMs) the lock-in is also a **pricing monopoly**.
- **Observability is limited**: you cannot inspect the model, only its outputs. This forces **contract testing** and **regression suites** to detect silent degradation.
- **Data privacy and GDPR**: every request leaves your perimeter. Where the data is stored matters. Some providers train on user data unless explicitly disabled (this is the practical reason behind Azure OpenAI, AWS Bedrock, Vertex AI's "your data is not used for training" guarantees).
- **Recurring spend grows with success**: a popular feature becomes a runaway bill.

### Shared responsibility in practice

The contract is not "the provider does AI for you". It is a split:

| Side | Owns |
|---|---|
| **Provider** | The model, the underlying infra, capacity, base SLAs, model updates |
| **Consumer** | Application integration, prompts/inputs, data governance, business-level monitoring, retry/timeout strategy, regression tests against the API |

The consumer's MLOps is **MLOps of consumption**, not of training: you version your wrappers, your prompt templates, your input schemas, and you test that the upstream model has not silently changed under you.

---

## Cloud vs on-premises: the real axes

> **Premise**: there is no universally right answer. The choice depends on which constraints bind in your context.

| Axis | Cloud | On-premises |
|---|---|---|
| **Elasticity** | Strong: scale GPUs/TPUs on demand | Weak: capacity is what you bought |
| **Time-to-market** | Days | Weeks to months |
| **Hardware management** | None: provider absorbs it | Full: you own the lifecycle |
| **Latency control** | Best-effort, network-bound | Deterministic, single-network |
| **Data sovereignty** | Constrained by provider regions | Total |
| **Cost shape** | OPEX, variable | CAPEX upfront + OPEX maintenance |
| **Regulatory friction** | Higher (GDPR, sector rules) | Lower (data never leaves) |
| **Customisation** | Bounded by provider abstractions | Total |

### Choose cloud when

- Demand is **variable** or **bursty** (campaigns, seasonal traffic).
- **Time-to-market matters more than per-unit cost** (validation phase).
- You need **accelerators on demand** without owning a GPU fleet.
- There are no hard SLAs on latency or jurisdiction.
- The team has cloud expertise but no hardware/data-center expertise.

### Choose on-premises when

- **Data sovereignty** is non-negotiable (healthcare records, government, finance under specific regulators).
- **Deterministic latency** is required (algorithmic trading, real-time control, telco edge).
- The workload is **stable and high-volume**: long-term TCO often beats cloud for stable production traffic.
- You need **architectural customisation** that no managed service exposes.

### The legal subtlety: cloud and GDPR

A cloud contract is a **shared responsibility model**: physical location of the data centres matters as much as the provider's name. EU-region deployments are a workable answer for European GDPR, but only if the contract makes the residency guarantee explicit and the provider does not move workloads transparently. This is also why hyperscalers run regional clouds (Azure EU, AWS Europe, GCP europe-west) and why some sensitive workloads still go on-prem despite the cost.

---

## The ML system architecture in the cloud

> **The pipeline**: data → features → training → deployment → serving → observability.

Each layer is an architectural decision with its own tradeoffs.

### Data layer

This is the layer most affected by **privacy/GDPR**. In complex architectures the decision is taken **independently of the rest of the system** (you can change storage strategy without rewriting the training code).

**Multi-tenant storage strategies**:

| Strategy | What it is | Cost | Isolation |
|---|---|---|---|
| **Physically separated** | One database/bucket per tenant | High | Maximum |
| **Logically separated, shared infra** | One service, isolated tenant configuration and data within it | Low | Strong if implemented correctly |

A **tenant** in a cloud database is an entity (user, group, organisation) that shares the underlying infrastructure but has isolated data and configuration from other tenants. The right strategy depends on regulatory pressure: physical separation for healthcare and finance, logical for typical B2B SaaS.

### Feature engineering and storage

Where preprocessing happens, where features are materialised. The discipline of a **feature store** (Vertex AI Feature Store, SageMaker Feature Store, Feast) prevents **training-serving skew**: the same feature definitions get used during training and during online inference, eliminating the bugs where the model worked offline but failed in production.

### Training and deployment

Where the model is trained (managed cluster, custom job) and how the artefact reaches an endpoint. The deployment options correspond to the serving choice below.

### Serving

Three patterns, picked based on latency, cost, and throughput:

| Pattern | Latency | Resilience | Use cases |
|---|---|---|---|
| **Synchronous online** | Low, mini-batches | Bounded by traffic spikes | Chat, classification at request, real-time recommendations |
| **Asynchronous** | Higher (queue) | High: decoupled from spikes | OCR pipelines, document analysis, heavy inference |
| **Offline / batch** | High (minutes to hours) | Maximum, cheap | Nightly scoring, CRM segmentation, periodic refresh |

The wrong choice is expensive: synchronous serving on a workload that does not need it pays GPU bills for idle capacity; batch serving on a real-time use case fails the user.

### Observability

Two layers, both needed.

**Classical SRE observability**: latency, throughput, error rate, end-to-end tracing across services. This is the part the platform team already knows how to do.

**ML-specific observability**:

| Signal | What it detects | How to act |
|---|---|---|
| **Data drift** | Input distribution shifts vs training | Trigger retraining, refresh features |
| **Concept drift** | Output relationships change (label distribution, target meaning) | Retrain on fresh labels, redesign feature set |
| **Per-segment quality** | Model works overall, fails on a specific cohort | Per-segment retraining, fairness review |
| **Feature freshness** | Features become stale (e.g., recent activity not yet ingested) | Pipeline SLO on feature delay |

This is the layer most often missing from "we deployed an AI feature" projects. Without it, the model silently degrades and nobody notices until the business KPI moves the wrong way.

---

## MLOps: the three Cs

> **What MLOps does**: automate integration, release, and retraining so that models in production are **reproducible, traceable, reliable**.

| C | What it covers | Concretely |
|---|---|---|
| **CI** | Continuous Integration: version code, data, models; build containers; test transformations and features | Git for code, DVC/MLflow for data and models, unit tests on feature definitions |
| **CD** | Continuous Delivery/Deployment: automated rollout to dev/staging/prod, image deploy to compute targets | GitHub Actions / Azure DevOps / Cloud Build pipelines, blue-green deploys |
| **CT** | Continuous Training: trigger retraining on data/model drift; orchestrated re-evaluation | Drift detector → pipeline run → registry promotion → endpoint update |

CT is the one that distinguishes "MLOps" from "DevOps applied to ML". A model is not built once and shipped; it is a perishable artefact. The team owns the feedback loop that keeps it fresh.

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Treating an LLM API as a static contract | Output quality changes silently, downstream tests fail | Regression test suite hitting the API on a fixed input set, on a schedule |
| Forgetting GDPR data residency | Audit finding, contract violation | Always check region settings, contract clauses, sub-processors before launch |
| Optimising for "the AI model" only | Pipeline fails because data ingestion or feature freshness is broken | Treat the full 5-layer pipeline as the system; observability covers all of it |
| Choosing on-prem because "it is cheaper" without TCO | Hardware refresh, operations team cost, downtime, capacity stranded | 3-year TCO with all hidden costs (see module 04 note 01) |
| Synchronous serving on batch workloads | Idle GPU hours, runaway bill | Use batch endpoints for non-time-critical predictions |
| No drift monitoring | Performance degrades silently for months | Wire data and concept drift signals from day one; if budget is tight, at least input statistics |
| Multi-tenant DB without tenant isolation | Cross-tenant data leak in a query | Schema-level isolation enforced by the framework, audited regularly |
| "We have AI now" without versioned prompts/wrappers | Cannot reproduce yesterday's behaviour | Treat prompts and post-processing as code: in git, tagged, deployed |
| MLOps reduced to CI/CD only | Model degrades, nobody retrains | Add CT with drift-based triggers; otherwise the system is incomplete |

---

## When to use what

| Need | Pattern | Why |
|---|---|---|
| Quick AI capability in an existing product | Pretrained API (AIaaS, PaaS) | Fastest path; lock-in is acceptable for MVP |
| Domain-specific accuracy beyond what generic APIs give | Custom-model platform (SageMaker / Vertex AI / Azure ML) | Control over training, still managed infra |
| Hard data-residency or latency SLA | On-prem or sovereign cloud region | The constraint dominates the choice |
| Real-time, latency-bound use case | Synchronous online serving | The contract is request/response |
| Heavy non-time-critical inference | Asynchronous serving | Better resilience, lower cost |
| Periodic refresh on big windows | Batch / offline serving | Cheapest per-prediction at volume |
| Stable production model | CI + CD pipeline | Reproducible deploys |
| Live model in a changing world | Add CT with drift triggers | Without it, the model decays |
| Multi-customer SaaS data | Logical multi-tenancy with strict isolation | Costs less, scales better than physical separation |
| Regulated multi-customer data | Physical separation per tenant | The audit overhead of logical isolation is not worth it |

---

## See also

### Other notes
- [02_aws_ai_ml_stack.md](02_aws_ai_ml_stack.md) — these primitives instantiated on AWS (S3, DynamoDB, Aurora, SageMaker)
- [03_azure_ai_ecosystem.md](03_azure_ai_ecosystem.md) — Azure's pyramid of services, from Cognitive Services to Azure ML
- [04_google_cloud_vertex_ai_data_first.md](04_google_cloud_vertex_ai_data_first.md) — GCP's data-first take, BigQuery + Vertex AI
- [05_iaas_open_source_and_on_prem_deployment.md](05_iaas_open_source_and_on_prem_deployment.md) — what changes if you skip the managed platform
- [06_paas_vs_iaas_vs_oss_decision_framework.md](06_paas_vs_iaas_vs_oss_decision_framework.md) — comparison and decision criteria across all three models
- [07_hybrid_and_multi_cloud_patterns.md](07_hybrid_and_multi_cloud_patterns.md) — when one cloud or one model is not enough

### Cross-module
- Module 04 [01_identifying_ai_problems_and_feasibility.md](../../04_business_case_AIPM/notes/01_identifying_ai_problems_and_feasibility.md) — total cost of ownership, the hidden costs that determine cloud vs on-prem TCO
- Module 04 [02_kpis_lifecycle_drift.md](../../04_business_case_AIPM/notes/02_kpis_lifecycle_drift.md) — the drift signals that drive Continuous Training
