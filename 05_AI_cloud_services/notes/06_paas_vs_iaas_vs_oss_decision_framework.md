# PaaS vs IaaS vs OSS: the Decision Framework

## TL;DR

The three service models are not points on a quality scale; they are three different tradeoffs on the same five axes: **cost shape**, **time-to-market**, **vendor lock-in**, **scalability/latency**, and **security/compliance**. **PaaS** (Azure AI Services / Azure AI Foundry, Google Vertex AI, AWS SageMaker / Bedrock) hides the infrastructure and gives you days-to-market with high lock-in: best for fast validation, small-to-medium volumes, teams without ML/DevOps headcount. **IaaS + third-party APIs** (cloud VMs running your code, calling OpenAI/Anthropic/Cohere) is the middle ground: 1-3 weeks to ship, medium lock-in, suited to SaaS products that integrate AI as a feature. **OSS** (self-hosted Llama, Mistral, Gemma) gives full control and low lock-in but demands real expertise; it wins on long-term cost at volume and on latency-critical/privacy-critical workloads. The **break-even** rule is approximate but useful: **<100K req/month → PaaS**, **100K-1M → case-by-case**, **>1M → OSS becomes cheaper on TCO**. Latency adds another axis: **<50 ms** essentially forces **OSS on-premise** because no managed cloud service guarantees sub-50ms over the public internet. Compliance flips the answer again: a PaaS provider already certified for HIPAA/GDPR may beat a self-built stack that needs to be audited from scratch. The decision framework therefore is **multivariate**, not a single switch; the right model emerges from the intersection of volume, time pressure, team capability, vendor-risk tolerance, latency SLO, and compliance posture. A concrete case study (e-commerce chatbot, 100K AI messages/month) is the pedagogical anchor: under those numbers PaaS costs ~$20/month, IaaS+API ~$410/month, OSS ~$400/month, but the cost-per-message gap inverts as volumes grow.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **PaaS** | Managed AI platform, you bring code | Days to ship, high lock-in |
| **IaaS + API** | VMs + third-party APIs, you wire it | Weeks to ship, medium lock-in |
| **OSS** | Self-hosted open-source models | Days to months depending on managed-vs-bare, low lock-in |
| **Break-even <100K req/mo** | PaaS wins on cost and effort | Validation, MVP, SMB |
| **Break-even 100K-1M** | Depends on team, growth, latency | Case-by-case |
| **Break-even >1M** | OSS cheaper in TCO | Mature SaaS, predictable volumes |
| **Latency <50 ms** | OSS on-premise effectively mandatory | Trading, IoT, gaming |
| **Latency 100-300 ms** | IaaS + API acceptable | Most SaaS chat features |
| **Latency 150-500 ms** | PaaS typical | Internal tools, async UX |
| **Latency 10-150 ms (OSS)** | Self-hosted, predictable cost | Production at volume |
| **Compliance (PaaS)** | Works if provider is certified for your sector | Standard SaaS in regulated industry |
| **Compliance (IaaS+API)** | Requires deep audit of API path | Mixed-risk products |
| **Compliance (OSS)** | Max privacy, max effort to certify | Healthcare, finance, public administration |
| **TTM: PaaS** | Days | API key + integration |
| **TTM: IaaS+API** | 1-3 weeks | VM provisioning + DevOps + integration |
| **TTM: OSS** | Variable: days (HF/Replicate managed) to months (full cluster) | Depends on managed-vs-bare |
| **Lock-in mitigation** | Abstraction layers, wrappers, multi-provider | Important even if you do not plan to switch |

---

## The three models on five axes

### 1. Cost shape

| Model | Cost pattern | Predictability |
|---|---|---|
| **PaaS** | Per-call, variable, scales with usage | Low: a viral feature blows the bill |
| **IaaS + API** | VM (fixed) + API (variable) + DevOps (fixed) | Mixed: the VM is predictable, the API is not |
| **OSS** | GPU/hardware (fixed) + ops (fixed) | High: scaling is the only variable |

**Break-even rule of thumb**:

| Monthly volume | Cheapest |
|---|---|
| **<100K requests** | PaaS |
| **100K-1M requests** | Case-by-case (depends on team, growth curve, latency) |
| **>1M requests** | OSS, in TCO over 12+ months |

The variance under the rule is large. A workload with very small payloads at 5M req/month may still be cheaper on PaaS if the operations cost would consume an FTE. A workload with large payloads or expensive model calls at 200K req/month may already favour OSS.

### 2. Time-to-market

| Model | TTM | Skills needed |
|---|---|---|
| **PaaS** | Days (account + API key + integration) | Basic developer |
| **IaaS + API** | 1-3 weeks (VM provisioning + system config + API integration) | Dev + basic DevOps |
| **OSS, managed** (HF Inference, Replicate, Together) | Days | Basic developer |
| **OSS, self-hosted simple** | 1-2 weeks | Dev + Docker |
| **OSS, enterprise cluster** | 2-4 months | DevOps + ML engineer + ops team |

The **MVP strategy** pattern: prototype on PaaS (or managed OSS) to validate the use case, then migrate progressively to OSS once volume and the cost picture justifies the operations.

### 3. Vendor lock-in

| Model | Lock-in level | Source of lock-in |
|---|---|---|
| **PaaS** | **High** | Vendor-specific APIs, request/response shapes, integration patterns; migrating from Azure to GCP usually requires substantial rewriting |
| **IaaS + API** | **Medium** | Portable infrastructure (standard VMs, Docker, K8s), replaceable APIs (OpenAI → Anthropic with moderate effort) |
| **OSS** | **Low** | Models and code are fully portable on-prem, multi-cloud, edge. The only lock-in is on **internal skills** |

**Lock-in is not always bad**: if PaaS saves 3-6 months of development, the tradeoff can be worth it. The problem only materialises when you actually want to change provider.

**When lock-in becomes critical**:
- Public-sector contracts with portability clauses.
- Multinationals with multi-region regulatory requirements.
- Startups in late-stage funding rounds that may be acquired (the acquirer may require platform-agnostic code).

**Mitigation**: even if you commit to PaaS, isolate the dependency behind a wrapper. The cost of writing the abstraction once is small; the cost of refactoring three years of vendor-coupled code is enormous.

### 4. Scalability and latency

| Latency target | Realistic model |
|---|---|
| **<50 ms (real-time)** | **OSS on-premise** effectively mandatory. Trading, gaming, IoT, industrial control. No managed cloud service can guarantee sub-50ms across the public internet |
| **100-300 ms (responsive UX)** | IaaS + API is the sweet spot; great for sudden traffic spikes, unpredictable costs |
| **150-500 ms (interactive but tolerant)** | PaaS typical; tradeoff between control and automation |
| **10-150 ms with fixed predictable cost** | OSS on managed infrastructure |

The pattern: **the harder the latency requirement, the closer the model has to run to the user, and the less benefit you get from PaaS abstraction**.

### 5. Security and compliance

| Model | Compliance posture | When it works |
|---|---|---|
| **PaaS** | Inherited from provider certifications (Azure HIPAA, GCP HIPAA, AWS SOC 2) | The provider's certifications cover your use case |
| **IaaS + API** | Mixed: VM provider is certified, but the third-party API path needs separate audit | Mid-risk products that combine controlled VMs with external AI |
| **OSS** | Maximum privacy possible (data never leaves), but **the certification effort is yours** | Healthcare, finance, public administration with hard data-residency rules |

A concrete case: Italian hospitals choose **OSS on-premise** for patient data under strict GDPR interpretation, even though running an LLM locally is harder than calling an API. The audit cost is one-time; the data-leak risk if patient data went to a public API would be career-ending.

---

## The decision framework

> **The model picks itself once you list the constraints honestly.**

### Pick PaaS if

- **Time-to-market** is the highest priority.
- The team has **no dedicated ML or DevOps** capacity.
- Monthly volumes are **<500K requests**.
- **Variable budget** is acceptable (no need for fixed cost predictability).
- **Standard compliance** is sufficient (no special regulations).
- The project is in **MVP / validation** phase.

**Typical profile**: startup (seed/Series A), SMB adding AI to an existing product, internal corporate pilot.

### Pick IaaS + API if

- The product needs **specific proprietary models** (GPT-4, Claude, top frontier LLMs).
- You need **infrastructure flexibility** beyond what PaaS exposes.
- The workflow involves **integrating multiple APIs** (e.g., GPT + Whisper + a vision API).
- There is at least **one DevOps engineer** on the team.
- Volumes are **medium** and PaaS bills are starting to hurt.

**Typical profile**: SaaS company integrating AI as a feature (think Notion AI), tech company on OpenAI/Anthropic, product with complex multi-step AI workflows.

### Pick OSS if

- **Privacy or compliance** is critical (healthcare, finance, public administration).
- Volumes are **medium-to-high** (>500K req/month).
- You need **predictable fixed costs**.
- **Internal technical capacity** is available (DevOps + ML).
- You need **deep model customisation** (fine-tuning, distillation, architectural changes).
- **<50 ms latency** is required (on-premise).
- **Vendor lock-in is unacceptable** for strategic reasons.

**Typical profile**: banks, insurance, hospitals, public administration; mature SaaS at scale; edge/IoT computing.

---

## A concrete cost study: e-commerce chatbot

> **Scenario**: 50,000 monthly orders, customer-service chatbot handling 100,000 AI messages/month.

Operational details: 15,000 conversations/month (30% of orders), 20 messages each, 30% requiring real AI (the rest answered by deterministic FAQ), average 100 tokens per message.

### Option 1: PaaS (Azure OpenAI)

| Item | Cost |
|---|---|
| API: 100K msg × 100 tokens × $0.002 / 1K | $20/month |
| Backend infrastructure (serverless functions) | $0 |
| Setup | 1-2 days of development |
| Maintenance | near zero |
| **Cost per message** | **$0.0002** |

### Option 2: IaaS + OpenAI API

| Item | Cost |
|---|---|
| OpenAI API | $20/month |
| Small VM | $40/month |
| Load balancer | $30/month |
| Monitoring | $20/month |
| Part-time DevOps | $300/month |
| **Total** | **~$410/month** |
| **Cost per message** | **$0.0041** |

Pro: infrastructure control. Contra: people costs dominate.

### Option 3: OSS (Mistral 7B self-hosted)

| Item | Cost |
|---|---|
| GPU cloud (spot, 12 h/day) | $120/month |
| Storage + networking | $30/month |
| Kubernetes orchestration | $0 (OSS) |
| Initial setup | 1 week of developer time |
| Maintenance (part-time developer) | $250/month |
| **Total** | **~$400/month** |
| **Cost per message** | **$0.004** |

Pro: fixed costs, privacy, customisable. Contra: setup + maintenance.

### Reading the table

At **100K req/month**, PaaS is dramatically cheaper because the API price is low and there is no overhead. The other two options are close to each other (the VM + DevOps roughly balances the GPU + ops).

The inversion happens at higher volumes:

| Volume | PaaS cost | IaaS+API cost | OSS cost | Cheapest |
|---|---|---|---|---|
| 100K | $20 | $410 | $400 | **PaaS** |
| 1M | $200 | $590 | $400 | **OSS** (assuming the OSS GPU can handle 1M with same hardware) |
| 10M | $2,000 | $2,180 | $400-$1,000 (likely scaled GPU) | **OSS** |

The crossing point is around **500K-1M requests/month** for this workload shape, after which OSS dominates. For workloads with bigger messages (longer tokens, multi-modal) the crossover shifts left; for tiny messages it shifts right.

The lesson is not "OSS is cheaper". It is **the cost function has different shape**: PaaS scales linearly with usage from zero, OSS has a fixed floor that pays back as volumes grow.

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Picking PaaS for an MVP, never re-evaluating | At 2M req/month the bill becomes unsustainable | Plan the migration path before adopting; set a volume trigger that revisits the decision |
| Adopting OSS too early | Engineering bandwidth burns on ops instead of product | Stay on PaaS until volumes or compliance force the move |
| Lock-in ignored "because we will not migrate" | Acquisition or compliance push happens, refactor is huge | Always wrap PaaS calls behind an internal interface |
| Choosing on cost-per-message alone | Hidden costs (DevOps, monitoring, maintenance) ignored | Total cost over 12 months, including people |
| Assuming all PaaS providers have the same compliance | Wrong certification for the sector | Verify the specific certificate (HIPAA, GDPR, FedRAMP) before committing |
| Self-hosted OSS without GPU sizing | OOM at first real traffic | Capacity-plan with realistic batch and concurrency assumptions |
| IaaS + API but no rate limiting / circuit breaker on the API | Upstream incident takes the product down | Implement retries, timeouts, fallbacks, and a graceful degradation path |
| OSS in production without drift monitoring | Performance silently degrades | The same MLOps discipline applies; OSS does not exempt you |
| Switching from PaaS to OSS for the wrong reason ("we want control") | Years of avoidable operations cost | The reason must be cost, compliance, or latency; "control" is rarely worth it |

---

## When to use what (the field guide)

| Profile | Pick |
|---|---|
| MVP, validation, <100K req/month, no ML team | **PaaS** (Azure AI Services / Vertex AI / SageMaker / Azure OpenAI / Bedrock) |
| SaaS product, AI as a feature, need GPT-4 quality, ~500K req/month | **IaaS + third-party API** (OpenAI / Anthropic) |
| Mature SaaS, >1M req/month, predictable workload | **OSS** on cloud GPUs |
| Healthcare, finance, PA, sensitive data | **OSS on-premise** |
| Latency-critical real-time (trading, IoT, gaming) | **OSS on-premise** |
| Need cutting-edge frontier models, not OSS-comparable | **IaaS + API** (call the frontier API from your stack) |
| Multi-region with different residency rules | Multi-cloud PaaS or OSS, see [07_hybrid_and_multi_cloud_patterns.md](07_hybrid_and_multi_cloud_patterns.md) |
| Strategic risk of vendor lock-in | **OSS** or PaaS-with-abstraction |
| Multi-modal product (LLM + vision + speech) on cloud | **IaaS + multiple APIs** |
| Strict cost cap and predictable budget | **OSS** with fixed-capacity hardware |

---

## See also

### Other notes
- [01_aiaas_and_cloud_architecture_fundamentals.md](01_aiaas_and_cloud_architecture_fundamentals.md) — the abstractions this note compares
- [02_aws_ai_ml_stack.md](02_aws_ai_ml_stack.md), [03_azure_ai_ecosystem.md](03_azure_ai_ecosystem.md), [04_google_cloud_vertex_ai_data_first.md](04_google_cloud_vertex_ai_data_first.md) — the PaaS implementations
- [05_iaas_open_source_and_on_prem_deployment.md](05_iaas_open_source_and_on_prem_deployment.md) — the IaaS / OSS stack in depth
- [07_hybrid_and_multi_cloud_patterns.md](07_hybrid_and_multi_cloud_patterns.md) — mixing models within one architecture is usually the answer

### Cross-module
- Module 04 [01_identifying_ai_problems_and_feasibility.md](../../04_business_case_AIPM/notes/01_identifying_ai_problems_and_feasibility.md) — 3-year TCO discipline applied to the choice
- Module 04 [05_roadmap_and_prioritization.md](../../04_business_case_AIPM/notes/05_roadmap_and_prioritization.md) — the "PaaS first, migrate when justified" pattern is a roadmap pattern
- Module 04 [06_product_lifecycle_poc_to_scale.md](../../04_business_case_AIPM/notes/06_product_lifecycle_poc_to_scale.md) — scaling from PoC to production maps onto migrating from PaaS to OSS
