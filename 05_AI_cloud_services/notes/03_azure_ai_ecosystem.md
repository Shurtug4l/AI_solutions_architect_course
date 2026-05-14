# Azure AI Ecosystem

## TL;DR

Azure is the second-largest cloud after AWS but the leader in **enterprise** adoption, driven by tight integration with Microsoft's existing stack (Office 365, Active Directory, Dynamics 365) and a deep portfolio of **compliance certifications** (GDPR, ISO 27001, HIPAA, SOC 2). The AI offering is organised as a **three-level pyramid** that maps directly onto the build-vs-buy tradeoff: **Level 1 (Cognitive Services)** is ready-to-use REST APIs for vision, speech, language, decision, integrated in days; **Level 2 (Custom Vision, LUIS)** is no-code customisation of those same models on your data, weeks-to-months; **Level 3 (Azure Machine Learning)** is full custom ML with code, months and a real ML team. The Cognitive Services portfolio covers four families (**Vision**, **Speech**, **Language**, **Decision**) and is the fastest path from "we need AI" to "we have AI". **Azure OpenAI Service** is the enterprise-safe wrapper around GPT-4 / GPT-3.5 / DALL-E with three contractual guarantees that public OpenAI does not give: your data is not used to train models, it stays in your Azure region, and the service holds the same compliance certifications as the rest of Azure. **Azure Machine Learning** has four faces (Designer no-code drag-and-drop, AutoML, Notebooks code-first, MLOps for production) on the same underlying platform. The **Power Platform** (Power BI, Power Apps, Power Automate) sits above all of this and democratises AI for citizen developers. The Azure data foundation is the usual quartet: **Blob Storage** (unstructured), **Azure SQL Database** (relational), **Cosmos DB** (global low-latency NoSQL), **Data Lake** (petabyte analytics). Pricing optimisation follows the standard cloud playbook: **batch processing (-50%)**, **result caching (-70%)**, **reserved instances (-40%)**, **auto-scaling (-50%)**.

## Cheatsheet

| Service / Concept | One-line | Pyramid level |
|---|---|---|
| **Pyramid Level 1** | Pre-built REST APIs, days to integrate | Cognitive Services |
| **Pyramid Level 2** | No-code customisation on your data | Custom Vision, LUIS |
| **Pyramid Level 3** | Full custom ML, code-first | Azure Machine Learning |
| **Cognitive Services / Vision** | Computer Vision, Face API, Custom Vision, Document Intelligence | Lv 1 |
| **Cognitive Services / Speech** | Speech-to-Text, Text-to-Speech, Speech Translation | Lv 1 |
| **Cognitive Services / Language** | Text Analytics, Translator, LUIS, QnA Maker | Lv 1 |
| **Cognitive Services / Decision** | Personalizer, Anomaly Detector | Lv 1 |
| **Azure OpenAI Service** | GPT-4, GPT-3.5, DALL-E on Azure with enterprise guarantees | Across all levels |
| **Azure ML Designer** | Drag-and-drop pipeline builder | Lv 3 (no-code) |
| **Azure ML AutoML** | Automated algorithm + hyperparameter search | Lv 3 (no-code) |
| **Azure ML Notebooks** | Jupyter + VS Code integrated, GPU and Spark access | Lv 3 (code-first) |
| **Azure ML MLOps** | Endpoints, monitoring, drift detection, Model Registry | Lv 3 (production) |
| **Blob Storage** | Object storage, ~$0.02/GB/month | Data foundation |
| **Cosmos DB** | Global NoSQL, <10 ms latency, multi-model | Data foundation |
| **Azure SQL Database** | Managed relational with ACID | Data foundation |
| **Data Lake** | Petabyte-scale storage for analytics | Data foundation |
| **Power Platform** | Power BI + Apps + Automate, citizen-developer AI | Above the pyramid |

---

## Azure's position in the market

Azure is the **second cloud provider globally** but the **leader in regulated enterprise** segments. The reason is structural, not technical:

- **Microsoft ecosystem integration**: Office 365, Windows, Active Directory, Dynamics 365 all interoperate natively with Azure. Adoption inside an organisation already running on Microsoft tools is mostly contractual, not migrational.
- **Compliance certifications**: GDPR, ISO 27001, HIPAA, SOC 2. For banking, healthcare, public administration, these are the gating requirements, not nice-to-haves.
- **Mature enterprise support**: large account managers, regional partnerships, established procurement processes.

The implication for AI workloads: Azure is the **lowest-friction choice when the organisation already runs on Microsoft** and when the workload sits in a regulated sector. The other reasons (best-of-breed analytics, frontier AI research, lowest cost) point elsewhere (GCP for the first, OpenAI/Anthropic/AWS for the second, depends for the third).

---

## The pyramid of Azure AI services

> Three levels, each calibrated for a different tradeoff between **time, budget, and competence**.

### Level 1: Cognitive Services (ready-to-use APIs)

REST APIs pre-configured for the most common AI tasks. You authenticate, you call the endpoint, you get a result.

| Property | Detail |
|---|---|
| **Time-to-market** | Days to weeks |
| **Skills needed** | Basic developer; no ML expertise required |
| **When to use** | Speed matters, generic models are good enough |
| **What you give up** | Customisation on your specific data, deep integration into your domain |

### Level 2: No-code customisation

The Cognitive Services line includes products (**Custom Vision** for vision, **LUIS** for language understanding) that let you upload your own labelled data through a UI and get a fine-tuned version of the underlying model.

| Property | Detail |
|---|---|
| **Time-to-market** | Weeks to months |
| **Skills needed** | Developer + business analyst; no data scientist required |
| **When to use** | Base models are not accurate enough; team lacks ML expertise |
| **What you give up** | Algorithm-level control, custom architectures |

### Level 3: Azure Machine Learning (full custom)

Code-first ML platform. You bring data, write training code, control the algorithm and the hyperparameters, deploy with full MLOps.

| Property | Detail |
|---|---|
| **Time-to-market** | Months |
| **Skills needed** | Data science team + MLOps |
| **When to use** | Specific requirements, the model is a competitive advantage |
| **What you give up** | The simplicity of an API |

### The decision question

For every candidate use case, the four questions to answer:
1. **How much time do I have?** (Days → Lv 1; weeks → Lv 2; months → Lv 3)
2. **What is my budget?** (Low → Lv 1; medium → Lv 2; high → Lv 3)
3. **What skills do I have?** (Developers only → Lv 1 or 2; ML team → Lv 3)
4. **How critical is the project?** (Tactical feature → Lv 1; differentiator → Lv 3)

The wrong answer in either direction is expensive: building a Level-3 custom-vision model when Custom Vision would do is a quarter of wasted work; relying on the generic Computer Vision API for a domain it does not cover is a feature that nobody trusts.

---

## Cognitive Services: the four families

The cleanest way to remember the catalogue is by family.

### Vision

| Service | Capability |
|---|---|
| **Computer Vision** | Image analysis, OCR, scene description |
| **Face API** | Face detection, recognition, emotion, estimated age |
| **Custom Vision** | Train your own classifier or detector, no code |
| **Document Intelligence** | Structured extraction from invoices, receipts, forms |

### Speech

| Service | Capability |
|---|---|
| **Speech-to-Text** | Transcription, real-time and batch |
| **Text-to-Speech** | Natural-sounding voices in 100+ languages |
| **Speech Translation** | Real-time voice translation for multilingual apps |

### Language

| Service | Capability |
|---|---|
| **Text Analytics** | Sentiment, key phrases, Named Entity Recognition |
| **LUIS** | Intent recognition from natural language |
| **Translator** | Text translation across 100+ languages |
| **QnA Maker** | Build FAQ chatbots from a knowledge base |

### Decision

| Service | Capability |
|---|---|
| **Personalizer** | Reinforcement-learning-style recommendations based on user behaviour |
| **Anomaly Detector** | Outlier detection on time series, proactive monitoring |

### What this stack is for

Cognitive Services is the **fastest path from idea to working feature**. The right question is not "is the model state-of-the-art?" but "is it good enough for this use case?". For document OCR, sentiment on customer reviews, and basic image classification, the answer is almost always yes, and the project ships in days.

The wrong question is "can I match GPT-4 with LUIS?". You cannot, and you should not try; if the use case needs LLM capability, the right Azure answer is **Azure OpenAI Service**.

---

## Azure OpenAI Service: GPT inside Azure

> The most capable OpenAI models (GPT-4, GPT-3.5 Turbo, DALL-E) running on Azure infrastructure, with enterprise contractual guarantees.

This is not "OpenAI repackaged". It is **the same models** with three differences that matter to enterprises.

| Guarantee | What public OpenAI does | What Azure OpenAI does |
|---|---|---|
| **Training on your data** | May use prompts to improve service (opt-out available) | Never uses your data for training |
| **Data residency** | US-based by default | Stays in your selected Azure region (e.g., EU West for GDPR) |
| **Compliance** | Limited | GDPR, ISO 27001, SOC 2 |
| **SLA** | Best-effort | 99.9% with Microsoft support |

The cost is access (it is gated behind a Microsoft application process and quota allocation) and slightly higher pricing than the public API. For any regulated or enterprise context, the cost is worth paying; for prototypes that do not touch sensitive data, the public OpenAI API is faster to get started with.

---

## Azure Machine Learning: four faces of the same platform

Azure ML is the Level-3 platform, and it deliberately exposes four different workflows on top of the same underlying compute and storage.

### Designer (no-code ML)

Drag-and-drop pipeline builder. Connect data sources, transformations, training modules, output targets through a visual editor.

- **For**: business analysts, MVPs, teams coming from Excel-style tooling.
- **Limit**: hits a ceiling when the workflow needs custom logic or non-standard models.

### AutoML

Automated search over **100+ algorithm/hyperparameter combinations**. You give it a dataset and a target, it gives you the best model it could find.

- **For**: tabular problems where the value is in the data, not the algorithm; teams without senior ML talent.
- **Limit**: black-box-ish, harder to debug specific failure modes; not a substitute for problem framing.

### Notebooks (code-first)

Managed Jupyter and VS Code, with direct access to **GPUs and Spark clusters**, libraries pre-installed (TensorFlow, PyTorch, Scikit-learn).

- **For**: data scientists writing code, full control over the model and the workflow.
- **Limit**: requires the team you would expect.

### MLOps (production)

The components that move a model from a notebook to a running endpoint:
- **Deployment as REST API** with managed endpoints.
- **Monitoring** with drift detection.
- **Model Registry** with versioning and lineage.
- **CI/CD** with GitHub Actions or Azure DevOps.

This is the production layer; the previous three are how the model gets built.

### The pattern

A team often crosses all four faces over a project's lifetime: prototype with AutoML to see if there is signal, move to Notebooks once the approach is chosen, and wire the result through MLOps to deploy. Designer is the outlier, mostly used by non-developer audiences.

---

## Power Platform: AI for citizen developers

The Power Platform is **above** the AI pyramid. It does not give you models; it gives **business users and citizen developers** a way to consume AI without coding.

| Product | What it does | AI angle |
|---|---|---|
| **Power BI** | Business Intelligence and dashboards | Natural-language Q&A ("sales by region last 3 months"), automatic insights, Key Influencers analysis, integration with Azure ML custom models |
| **Power Apps** | Low-code app builder | AI Builder with OCR, object detection, form processing, sentiment built-in |
| **Power Automate** | Workflow automation | Cognitive Services in workflows: incoming invoice → Document Intelligence extracts fields → auto-approve if amount < threshold |

The strategic role: Power Platform is what turns a Cognitive Services API into a feature **inside an existing business process** that someone without engineering bandwidth can build and operate. It is also the easiest demonstration of why Azure adoption is sticky in enterprises (no other cloud has the same low-code surface tied to its AI portfolio).

---

## Data foundation: storage and databases

Four primary services, picked by data shape and access pattern.

| Service | Stores | Use in ML | Pricing |
|---|---|---|---|
| **Blob Storage** | Unstructured (images, video, CSV, logs) | Training datasets for vision/speech, data lake for big data | ~$0.02/GB/month, Archive tier cheaper |
| **Azure SQL Database** | Structured tabular with schema | Feature store, transactional data for training, prediction outputs | Per vCore + storage |
| **Cosmos DB** | JSON documents, key-value, graph, columnar | Real-time predictions, model cache, chat history, user sessions | Provisioned or serverless throughput |
| **Data Lake** | Petabyte structured and unstructured | Training on huge datasets (>1 TB), data warehouse, ETL | Per GB + transactions |

### When to pick which

| Need | Pick |
|---|---|
| Bulk files, images, audio, logs | **Blob Storage** |
| Relational queries, joins, transactions | **Azure SQL** |
| Single-key real-time access, global distribution | **Cosmos DB** |
| Analytics on terabyte-to-petabyte data | **Data Lake** + Spark/Databricks |

Cosmos DB's selling point is the **<10 ms latency globally**: data is replicated automatically to chosen regions, and reads are served from the closest one. For a chat application with a worldwide user base, this is the right fit.

---

## Pricing: the standard playbook

Cloud AI costs are predictable in their unpredictability: a successful feature explodes the bill. The cost-optimisation patterns are well-known and stack.

| Technique | What it does | Typical reduction |
|---|---|---|
| **Batch processing** | Group requests instead of one-by-one calls | ~-50% |
| **Result caching** | Memoise frequent responses | ~-70% |
| **Reserved instances** | Pre-commit to annual capacity | ~-40% |
| **Auto-scaling** | Match capacity to demand | ~-50% |

These multiply, not add. A workload that batches, caches popular responses, runs on reserved instances, and auto-scales the rest pays a small fraction of the naive bill.

The discipline is to apply them **before** the bill becomes a problem, not after a CFO escalation. For an MVP, you can skip them; for anything that is shipping to production, they are a checklist item.

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Building Level-3 custom ML for a problem Level-1 solves | A team spends a quarter on what an API call covers | Always try the API first; build custom only when API outputs miss the spec |
| Public OpenAI used for sensitive data | Compliance breach | Use Azure OpenAI Service; verify region and contract |
| Cognitive Services for tasks outside their training distribution | Bad accuracy, surprises in production | Validate against your own test set before launch; consider Custom Vision / Azure ML if generic accuracy fails |
| Cosmos DB used as a transactional RDBMS | High cost, poor query patterns | Use Cosmos for global low-latency access, Azure SQL for transactions |
| Azure ML deployed without MLOps | Cannot reproduce, no drift monitoring | Always wire Model Registry + monitoring + CI/CD from the first deploy |
| Cost optimisations applied after the fact | The team gets a $30 K monthly bill before the optimisations are done | Build batch/cache/auto-scale into the architecture, not as a remediation |
| Power Platform used without governance | Citizen developers create unmanaged workflows that leak data | Establish a Power Platform CoE: environments, policies, audited connectors |
| Cognitive Services region mismatched with data residency policy | Audit finding | Choose region explicitly; default may be US |

---

## When to use what

| Need | Pick |
|---|---|
| Fastest possible OCR / sentiment / object detection feature | **Cognitive Services** (Lv 1) |
| Model the generic API does not handle, no data science team | **Custom Vision / LUIS** (Lv 2) |
| Full custom model, ML team available | **Azure ML** (Lv 3) |
| LLM capability with enterprise guarantees | **Azure OpenAI Service** |
| AI inside a workflow built by a business user | **Power Platform** + Cognitive Services |
| Store training datasets, model artefacts, logs | **Blob Storage** |
| Transactional features and prediction outputs | **Azure SQL Database** |
| Real-time prediction context with global low latency | **Cosmos DB** |
| Petabyte-scale analytics workloads | **Data Lake** + Spark |
| Reduce bill on a popular AI feature | Batch + Cache + Reserved + Auto-scale |
| Tabular ML problem without senior ML team | **AutoML** in Azure ML |
| Imbalanced classification (e.g., HR attrition) | AutoML with explicit class-weight handling and a held-out test set |
| Custom `predict_proba` exposure on AutoML endpoint | Customise the scoring script that AutoML auto-generates (it is exposed for editing) |

---

## See also

### Other notes
- [01_aiaas_and_cloud_architecture_fundamentals.md](01_aiaas_and_cloud_architecture_fundamentals.md) — pyramid maps to the AIaaS-vs-custom-platform tradeoff
- [02_aws_ai_ml_stack.md](02_aws_ai_ml_stack.md) — AWS counterpart (Cognitive Services ↔ Bedrock + Comprehend etc.; Azure ML ↔ SageMaker)
- [04_google_cloud_vertex_ai_data_first.md](04_google_cloud_vertex_ai_data_first.md) — GCP counterpart, with a different philosophy (data-first vs services-first)
- [06_paas_vs_iaas_vs_oss_decision_framework.md](06_paas_vs_iaas_vs_oss_decision_framework.md) — when to leave the Azure pyramid for IaaS or OSS

### Cross-module
- Module 02 [05_prompt_engineering.md](../../02_large_language_models/notes/05_prompt_engineering.md) — what you build on top of Azure OpenAI Service
- Module 04 [02_kpis_lifecycle_drift.md](../../04_business_case_AIPM/notes/02_kpis_lifecycle_drift.md) — the metrics that Azure ML's monitoring tracks
