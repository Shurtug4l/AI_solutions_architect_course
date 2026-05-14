# Hybrid and Multi-Cloud Architecture Patterns

## TL;DR

**Hybrid** and **multi-cloud** sound similar and refer to different things. **Hybrid architecture** = mixing **service models** (PaaS + IaaS + OSS) in the same solution, possibly within a single cloud provider. **Multi-cloud** = using **multiple cloud providers** (AWS + Azure + GCP) in the same architecture. The two can stack: a system can be hybrid (mixed models) and multi-cloud (mixed providers) at the same time. **Five strategic motivations** justify either pattern: **cost optimisation** (mixing PaaS for non-core features and OSS for high-volume cuts bills), **compliance and privacy** (sensitive data on-prem, non-sensitive on cloud), **best-of-breed** (each provider has services nobody else matches: BigQuery for analytics, Azure for Office integration, AWS for breadth), **redundancy and DR** (failover between providers for mission-critical systems), **geographic expansion** (cloud presence in regions a single provider does not serve well, e.g., Alibaba Cloud for China). Four **recurring patterns** in the wild: **"MVP → Scale"** (start 100% PaaS, evolve to hybrid PaaS+OSS as volume grows), **"Core vs Edge"** (proprietary algorithms on OSS for control, generic features on PaaS for speed), **"Geographic regions"** (right provider for each region), **"Dev vs Prod"** (cheap PaaS or local OSS in development, optimised mix in production). The **hidden costs** are non-trivial: operational complexity (+30-50% headcount), cross-cloud networking ($0.08-0.12/GB), unified tooling licences (Datadog, Splunk, Prisma Cloud), debugging across providers, governance gaps between IAM systems, and loss of volume discounts when spend is split. **The market reality**: ~80% of companies run **single-cloud hybrid** (one provider, PaaS+OSS), ~15% run **specific multi-cloud** for compliance or best-of-breed, only ~5% run **full multi-cloud replication** (Netflix, Uber scale). The advice that scales: **start simple, add complexity only when concrete metrics justify it.**

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **Hybrid architecture** | Mix of service models (PaaS + IaaS + OSS), can be single-cloud | Cost or compliance optimisation |
| **Multi-cloud** | Mix of providers (AWS + Azure + GCP) | Redundancy, best-of-breed, geo |
| **Single-cloud hybrid** | One provider, mixed models | The most common architecture (~80%) |
| **MVP → Scale pattern** | 100% PaaS → PaaS+IaaS → OSS at scale | Startup growth curve |
| **Core vs Edge pattern** | OSS for proprietary core, PaaS for non-core features | Enterprise differentiation strategy |
| **Geographic pattern** | Right provider for each region (AWS US, Azure EU, GCP APAC) | Multinational deployments |
| **Dev vs Prod pattern** | Cheap PaaS or local OSS in dev, optimised mix in prod | Cost control during development |
| **Cross-cloud networking** | $0.08-0.12/GB egress | The silent cost killer |
| **Unified tooling cost** | Datadog, Splunk, Prisma Cloud | Required for multi-cloud observability |
| **Workload separation** | Different providers for different workloads | Simplest multi-cloud strategy |
| **Active-active replication** | Same app on multiple clouds, real-time replica | Highest cost, zero downtime |
| **Kubernetes multi-cloud** | EKS + AKS + GKE managed by the same control plane | Maximum portability, max expertise required |
| **Architecture Decision Record (ADR)** | Document explaining each cloud/service choice | Indispensable when architecture spans providers |
| **Distributed tracing** | Jaeger, OpenTelemetry across cloud boundaries | Required for cross-cloud debugging |

---

## Definitions: hybrid vs multi-cloud

> The two terms are often conflated. They mean **different things** and have **different reasons** for adopting them.

| Term | What it mixes | Example |
|---|---|---|
| **Hybrid architecture** | Service models (PaaS, IaaS, OSS) inside the same solution | E-commerce: Azure AI Services (PaaS) + Llama OSS for high-volume LLM calls |
| **Multi-cloud** | Cloud providers | Startup: AWS US + Azure EU + GCP analytics |

The two can combine: a system that runs **Azure AI Services in EU, Llama OSS in EU, and AWS S3 for archival** is both hybrid and multi-cloud.

### Concrete examples by sector

**Hybrid architectures**:
- **E-commerce**: Azure AI Services (vision and language APIs) + Llama OSS (chatbot, high volume).
- **FinTech**: OpenAI API (general LLM) + on-premise fraud detection models (regulated data).
- **B2B SaaS**: Google Vertex AI (managed ML platform) + custom OSS models (vertical-specific).

**Multi-cloud architectures**:
- **Global startup**: AWS US + Azure EU + GCP for analytics.
- **Enterprise**: Azure for Office 365 + AWS for SageMaker.
- **Media**: GCP for video processing + AWS for storage.

---

## Five strategic motivations

> Architectures cost complexity. The decision to adopt one is justified by these five drivers.

### 1. Cost optimisation

The strongest driver in early-stage growth. A SaaS startup combining PaaS for non-core features and OSS for high-volume cuts costs typically by **~40%**.

Concrete example: a workload going from **€2,000/month (full PaaS)** to **€1,200/month (hybrid PaaS+OSS)** = €9,600 saved annually. At scale, the gap widens further (see [06_paas_vs_iaas_vs_oss_decision_framework.md](06_paas_vs_iaas_vs_oss_decision_framework.md) for the break-even logic).

### 2. Compliance and privacy

Sensitive data lives where regulations require it (often on-prem); non-sensitive workloads exploit the cloud for speed.

Concrete example: hospitals run **OSS on-premise** for patient data (GDPR) while using **PaaS cloud** for non-critical features (scheduling, anonymised analytics). Full compliance without sacrificing time-to-market on the parts where it does not matter.

### 3. Best-of-breed

Each cloud has services nobody else matches:

| Provider | Best-of-breed for |
|---|---|
| **GCP** | BigQuery analytics, TensorFlow ecosystem, Vision AI |
| **Azure** | Office 365 integration, enterprise Active Directory, Azure OpenAI |
| **AWS** | Catalogue breadth, S3 economics, mature DevOps tooling |

Enterprise analytics platforms commonly combine **BigQuery** (analytics) + **Azure** (Office 365 integration) + **AWS S3** (economical archival).

### 4. Redundancy and disaster recovery

Mission-critical fintech and payments systems implement **automatic failover between AWS and Azure**, reducing potential downtime from hours to minutes during an outage.

The cost is roughly **2x infrastructure** for active-active. For most products this is overkill; for systems where downtime costs more than the duplicate infra, it is the right pattern.

### 5. Geographic expansion

Expanding into a region a single provider does not serve well. The canonical example: SaaS companies entering **China** use AWS/Azure for US/EU but **Alibaba Cloud** for China, respecting local legal requirements and optimising latency.

---

## Four recurring architectural patterns

### Pattern 1: "MVP → Scale"

The most common pattern in startups. Architecture evolves with business maturity.

| Phase | Months | Architecture | Cost range |
|---|---|---|---|
| **MVP** | 0-6 | 100% PaaS for fast TTM | €50-500/month |
| **PMF** | 6-18 | PaaS + IaaS for API-specific workloads | €500-3,000/month |
| **Scale** | 18+ | Core on OSS, secondary features on PaaS | €3,000-10,000/month with 10x volumes |

The lesson: **the architecture that wins at scale would have been wrong at MVP**, and vice versa. Building the OSS cluster on day one delays the product; staying on PaaS forever overpays.

### Pattern 2: "Core vs Edge"

Used by mature companies that have proprietary algorithms.

| Layer | Where it runs | Why |
|---|---|---|
| **Core** | OSS | Proprietary algorithms, fraud detection, pricing engines: total control, no leak to a vendor |
| **Edge** | PaaS | OCR, speech-to-text, sentiment: fast to implement, generic capabilities |

The principle: **own what differentiates, buy what does not**.

### Pattern 3: "Geographic regions"

| Region | Preferred provider | Reason |
|---|---|---|
| **US / Americas** | AWS | Data centre dominance |
| **EU** | Azure | Tight GDPR alignment, Microsoft enterprise penetration |
| **Asia-Pacific** | GCP | Google network optimisation |
| **China** | Alibaba Cloud | Legal compliance |

For products with worldwide users, single-cloud often loses on latency or compliance in some region.

### Pattern 4: "Dev vs Prod"

Cost optimisation across the dev cycle.

| Environment | Stack | Cost |
|---|---|---|
| **Development** | PaaS or local OSS (Ollama) | Near zero |
| **Production** | Optimised mix, OSS GPU cluster for the heavy workloads | ~€2,000/month savings vs full-PaaS prod |

The pattern is: **non-production environments are cost centres** without revenue offset; pick the cheapest combination that maintains parity with production behaviour.

### Distribution of patterns

| Pattern | Adopted by |
|---|---|
| **MVP → Scale** | Most common in startups |
| **Core vs Edge** | Enterprises with differentiation strategy |
| **Geographic regions** | Multinationals |
| **Dev vs Prod** | Mature teams cost-conscious about non-prod |

---

## Multi-cloud strategy: when it makes sense

### When yes

- **Multi-regional compliance**: EU data in EU, US in US (legal requirement, not preference).
- **Best-of-breed critical**: a specific service (BigQuery for analytics) is irreplaceable.
- **Existing enterprise contracts**: Azure for Office 365 already in place + AWS SageMaker for ML.
- **Gradual migration**: transitional phase while moving between providers.

### When no

- **Theoretical lock-in**: if you never actually plan to switch, complexity exceeds benefit.
- **Early-stage startups**: focus on product, not on multi-cloud infrastructure.
- **Small teams (<10 people)**: operational overhead unsustainable.
- **Standard workloads**: a single provider covers everything required.

The general principle: **multi-cloud is a means, not an end**. Adopting it without a concrete reason is paying for complexity that delivers nothing.

### Three multi-cloud implementation strategies

| Strategy | What it is | Pro / con |
|---|---|---|
| **Workload separation** | Different providers for different workloads (GCP for data warehouse, AWS for web app) | Simple, but **cross-cloud networking costs** |
| **Active-active replication** | Same app on multiple clouds with real-time replication, AWS primary + Azure failover | Zero downtime, but **2x infrastructure cost** |
| **Kubernetes multi-cloud** | Container orchestration across EKS, AKS, GKE with unified control plane | Maximum portability, but **advanced K8s expertise required** |

---

## The hidden costs of complex architectures

> **Operational complexity is the part nobody quotes upfront**. It is also the part that determines whether the architecture is worth its supposed savings.

### Operational complexity

| Impact | Detail |
|---|---|
| Onboarding | From 2 weeks (single-cloud) to 2 months (multi-cloud) |
| Headcount cost | +30-50% |
| Dedicated ops headcount | A startup with 5 developers needs 1 full-time on infrastructure (20% of the team) |

What you have to know:
- 2-3 clouds instead of 1.
- Different monitoring and logging tooling per provider.
- Multi-provider networking and security.

### Hidden costs

| Item | Cost |
|---|---|
| **Cross-cloud networking** | €0.08-0.12/GB egress = €80-120/month per 1 TB transferred |
| **Unified tooling**: Datadog | €15-30 per host |
| **Splunk** (logging) | €100-500/month |
| **Prisma Cloud** (security) | €1,000+/month |
| **Licence duplication**: databases, K8s, observability across multiple clouds | Variable |

Invisible costs commonly represent **30-40% of the total architecture cost**.

### Cross-cloud debugging

Tracing a bug across **AWS API Gateway → GCP BigQuery → Azure Function** requires **distributed tracing** with tooling like **Jaeger** or **OpenTelemetry**. The setup is non-trivial and adds further cost.

### Unified governance

Each cloud has its own IAM system:
- AWS roles
- Azure RBAC
- GCP IAM

Applying uniform security policies across them creates **security gap risks** and makes audits more complex. Tools like HashiCorp Vault or unified IAM platforms reduce the gap but add their own cost and learning curve.

### Vendor relationship

Splitting €50K/month between AWS (€25K) and GCP (€25K) loses **volume discounts** on both. Vendor support is **fragmented** and **responsibility is unclear** in cross-cloud incidents.

---

## Best practices: how to actually do this

### 1. Start simple, scale if necessary

Start with **single-cloud PaaS**, evolve to **hybrid PaaS/OSS**, consider multi-cloud only if compliance, best-of-breed, or team expertise justifies it. **Do not adopt multi-cloud for fashion.**

### 2. Abstract to avoid dependencies

| Tool | Function |
|---|---|
| **Kubernetes** | Container portability |
| **Terraform** | Infrastructure as Code |
| **API wrappers** | Cloud-specific services hidden behind internal interfaces |
| **Unified monitoring**: Datadog or Prometheus | Single observability layer |

### 3. Separate workloads

Different cloud per workload: GCP for analytics, AWS for web app. **Avoid full replication of the same app across providers** unless redundancy is the explicit goal.

### 4. Continuously monitor costs

| Tool | Provider |
|---|---|
| **AWS Cost Explorer** | AWS |
| **Azure Cost Management** | Azure |
| **GCP Billing** | GCP |
| **CloudHealth, Apptio** | Multi-cloud |

Set budget alerts and monitor cross-cloud networking costs in particular: they are the silent killer.

### 5. Document everything

With multi-cloud, **written documentation is indispensable**:
- **Architecture Decision Records (ADR)**: why AWS here and GCP there.
- **Runbooks** for disaster recovery.
- **Architecture diagrams** kept up to date.

If the architecture is not documented, the only person who understands it is the architect, and the day they leave, the system becomes unmaintainable.

---

## Market reality: distribution of architectures

> Most companies do not run anything fancy. The advice "start simple" matches the market.

| Architecture | Adopted by | Why |
|---|---|---|
| **Single-cloud hybrid** | **~80%** | Most companies use one provider with a PaaS + OSS mix for operational simplicity |
| **Specific multi-cloud** | **~15%** | Banks, large enterprises with mission-critical compliance |
| **Full multi-cloud** | **~5%** | Only companies at extreme scale (Netflix, Uber) with complete cross-provider replication |

**Implication**: full multi-cloud is the exception, not the rule. Single-cloud hybrid is the default; multi-cloud is justified by specific drivers.

**Final piece of advice**: the majority of companies thrive with single-cloud hybrid architectures. **Start simple, add complexity only when necessary and justified by concrete business metrics.**

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Multi-cloud adopted "because everyone does it" | High operational cost, no compliance/best-of-breed/DR justification | Verify the concrete driver; if there is none, stay single-cloud |
| Cross-cloud networking ignored | Surprise bill, slow inter-service calls | Co-locate by region; minimise egress; monitor `data transferred between regions/providers` metric |
| ADRs not maintained | After 6 months, nobody understands the architecture | Update ADR every time a service is added or changed |
| Unified IAM postponed | Security gap exposed by an audit | Implement HashiCorp Vault, Okta, or similar from the start |
| Active-active without active testing | Failover does not work when needed | Periodic disaster recovery drills (chaos engineering) |
| Kubernetes multi-cloud without ops expertise | Cluster broken, application down, knowledge gap | Either hire the expertise or stay on managed services |
| Datadog / Splunk costs underestimated | The unified observability bill exceeds half the cloud bill | Capacity plan and apply rate limits to log emission |
| Tracing not configured between clouds | Cross-cloud bugs take days to debug | Wire OpenTelemetry from day one |
| Discounts lost across providers | Total spend > sum of best individual deals | Concentrate spend with a primary provider when possible; commit-based discounts go to volume |
| Migration from PaaS to OSS done abruptly | Production failures during transition | Run both in parallel, route gradually, fall back if needed |

---

## When to use what

| Need | Pick |
|---|---|
| AI feature in MVP | **Single-cloud PaaS** (one provider, one model) |
| Cost reduction at medium scale | **Single-cloud hybrid** (PaaS for non-core, OSS for high-volume) |
| Differentiation on proprietary algorithm | **Core vs Edge** (OSS core, PaaS edge) |
| Sensitive data + non-sensitive features | **Hybrid on-prem + cloud** (OSS on-prem, PaaS cloud) |
| Multinational with regional compliance | **Geographic multi-cloud** |
| Mission-critical zero-downtime | **Active-active multi-cloud** (only if budget justifies it) |
| Maximum container portability | **Kubernetes multi-cloud** (K8s expertise required) |
| Best-of-breed: BigQuery for analytics + Office 365 | **Specific multi-cloud** |
| Avoid vendor lock-in for strategic reasons | **OSS hybrid** (low lock-in, controlled by you) |
| Cost control on development environments | **Dev vs Prod** (cheap stack in dev, optimised in prod) |
| Unified observability across providers | **Datadog / Prometheus + Grafana** as unified layer |
| Audit and documentation of complex architecture | **Architecture Decision Records** + diagrams kept up to date |

---

## See also

### Other notes
- [01_aiaas_and_cloud_architecture_fundamentals.md](01_aiaas_and_cloud_architecture_fundamentals.md) — the basic primitives that mix in hybrid architectures
- [02_aws_ai_ml_stack.md](02_aws_ai_ml_stack.md), [03_azure_ai_ecosystem.md](03_azure_ai_ecosystem.md), [04_google_cloud_vertex_ai_data_first.md](04_google_cloud_vertex_ai_data_first.md) — the providers being combined here
- [05_iaas_open_source_and_on_prem_deployment.md](05_iaas_open_source_and_on_prem_deployment.md) — the OSS leg of hybrid architectures
- [06_paas_vs_iaas_vs_oss_decision_framework.md](06_paas_vs_iaas_vs_oss_decision_framework.md) — when each model wins; hybrid means picking the right one per workload

### Cross-module
- Module 04 [05_roadmap_and_prioritization.md](../../04_business_case_AIPM/notes/05_roadmap_and_prioritization.md) — the "MVP → Scale" architectural pattern matches the product-roadmap pattern
- Module 04 [06_product_lifecycle_poc_to_scale.md](../../04_business_case_AIPM/notes/06_product_lifecycle_poc_to_scale.md) — scaling from PoC to production aligns with the architectural evolution
- Module 04 [01_identifying_ai_problems_and_feasibility.md](../../04_business_case_AIPM/notes/01_identifying_ai_problems_and_feasibility.md) — TCO over 3 years is the right horizon for evaluating hybrid/multi-cloud
