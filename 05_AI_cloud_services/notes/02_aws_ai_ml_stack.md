# AWS AI and ML Stack

## TL;DR

AWS sells the broadest catalog of cloud services (200+), and its AI/ML stack is built on three primitives plus a managed platform. The primitives are **storage** (object, relational, NoSQL), the platform is **SageMaker**, and they are bound together by AWS's **Region / Availability Zone** geography. **S3** is the default landing zone for everything (raw data, processed features, model artefacts, logs) and behaves like a flat data lake. **Aurora** is the managed relational engine (MySQL/PostgreSQL-compatible) with autoscaling storage, suited to feature stores and transactional workloads. **DynamoDB** is the serverless NoSQL with single-digit-millisecond latency at any scale, suited to real-time prediction lookups and session state. **SageMaker** is the end-to-end ML platform: it reads from S3, runs managed training and tuning, registers models, deploys them as endpoints, and monitors them for drift through **CloudWatch** and **EventBridge**. The canonical AWS pipeline is **S3 (raw) → SageMaker Processing/Feature engineering → SageMaker Training/HPO → Model Registry → SageMaker Endpoint → SageMaker Model Monitor**. At re:Invent 2024 AWS introduced the **next-generation SageMaker / SageMaker Unified Studio**, a single workspace combining the classical ML platform (renamed **SageMaker AI**) with Glue, Athena, EMR, Redshift and QuickSight; existing SageMaker notebooks and the v2 Python SDK still work unchanged. On top of the ML stack, **Amazon Bedrock** is the managed gateway for foundation models (Anthropic Claude, Meta Llama, Mistral, Cohere, AI21, Amazon Titan/Nova, Stable Diffusion), with private fine-tuning, agents, guardrails and knowledge bases. Bedrock is the natural AWS counterpart to Azure OpenAI Service / Azure AI Foundry. Resilience is built on **Regions** (geographic macro-areas, the operational and legal boundary) containing multiple **Availability Zones** (isolated failure domains within a region). A model that needs intra-region HA is deployed across AZs; a model with global users needs deployment across regions and is a separate architectural question (latency, cross-region cost, data residency).

## Cheatsheet

| Service / Concept | One-line | Used for |
|---|---|---|
| **Region** | Geographic macro-area, legal and operational boundary | Choosing where data lives, GDPR compliance |
| **Availability Zone (AZ)** | Isolated failure domain inside a Region | Intra-region HA |
| **S3** | Object storage, virtually unlimited, the AWS data lake | Datasets, models, logs, artefacts |
| **DynamoDB** | Serverless NoSQL key-value, single-digit ms latency | Real-time prediction context, session state |
| **Aurora** | Managed RDBMS, MySQL/PostgreSQL-compatible, autoscaling storage | Feature store, transactional data |
| **SageMaker AI** (formerly just **SageMaker** / **SageMaker Studio**, renamed in 2024) | End-to-end managed ML platform | Build, train, deploy, monitor |
| **SageMaker Unified Studio** | Next-gen workspace bundling SageMaker AI + Glue + Athena + EMR + Redshift + QuickSight (announced re:Invent 2024) | Single pane for data + ML |
| **SageMaker Processing** | Managed jobs for preprocessing and feature engineering | ETL inside the ML pipeline |
| **SageMaker Training / HPO** | Distributed training and hyperparameter tuning | The training step |
| **SageMaker Model Registry** | Versioned model catalogue | Promotion, lineage, governance |
| **SageMaker Endpoint** | Managed inference endpoint, real-time or batch | Serving |
| **SageMaker Model Monitor** | Drift detection on data and model quality | ML observability |
| **Amazon Bedrock** | Managed foundation-model gateway (Claude, Llama, Mistral, Titan/Nova, Stable Diffusion) with agents, guardrails, knowledge bases | GenAI / LLM workloads |
| **CloudWatch** | Metrics, logs, alarms | Observability sink |
| **EventBridge** | Event bus for triggering reactions | Auto-retrain on alarm, glue between services |

---

## The AWS geography: Region and AZ

> AWS is physically distributed in **Regions**, which are themselves split into **Availability Zones**.

**Region** = a macro-geographic area (e.g., `eu-west-1` in Ireland). It is the **operational and legal boundary**: data in a region stays in that region unless you explicitly replicate it elsewhere. The choice of region carries the GDPR consequence: a workload serving EU customers should sit in an EU region, not because of performance but because of jurisdiction.

**Availability Zone** = a physically isolated data centre (or cluster of data centres) inside the Region, with its own power, cooling, and network. AZs are linked by low-latency private fibre, so a service deployed across multiple AZs in the same Region survives a data-centre outage with no cross-region complication.

The practical pattern:
- **Production workloads**: at least 2 AZs in the chosen Region (HA without cross-region cost).
- **Multi-region**: only when latency to a remote user base or disaster-recovery requirements justify the cost and the complexity (cross-region replication is paid, both in network fees and in engineering).

---

## Storage primitives

The AWS approach is to keep **raw data on S3** and overlay typed databases where the access pattern needs them. The three primitives have very different shapes.

### Amazon S3: the universal landing zone

> **Object storage**, organised in **buckets** containing **objects**, addressed by key.

S3 is best thought of as either a file system or a data lake, depending on how you query it.

| Property | Detail |
|---|---|
| **Scale** | Virtually unlimited storage per bucket |
| **Durability** | 11 nines (99.999999999%) by spec, replicated within Region |
| **Pricing** | Pay per GB stored + per request + per egress; storage classes (Standard, Intelligent Tiering, Glacier) for cost optimisation |
| **Access pattern** | HTTPS API, IAM-controlled, no native indexing |

What you put on S3:
- **Training datasets**: CSV, Parquet, image files, NDJSON.
- **Model artefacts**: serialised models, ONNX exports, tokenisers.
- **Logs and traces**: from CloudWatch exports, application logs.
- **Anything that does not need a structured query engine** to be useful.

S3 is what every other AWS ML service reads from and writes to. If a piece of data does not have a clear home in a typed database, it goes on S3.

### Amazon Aurora: the managed RDBMS

> Compatible with **MySQL and PostgreSQL**, with distributed storage and replicas for performance.

The point of Aurora over a raw RDS instance is:
- **Storage autoscales** in 10-GB increments up to 128 TB without manual intervention.
- **Compute autoscales** instantly and granularly via Aurora Serverless v2.
- **Replicas** can be added without disrupting the writer.
- Native integration with the rest of AWS (IAM, Secrets Manager, CloudWatch).

Where it fits in ML:
- **Feature store** for tabular features that need transactional consistency.
- **Output of predictions** that must be queried by business systems with SQL.
- **Training data sourced from operational systems** when the source is already relational.

### Amazon DynamoDB: serverless NoSQL

> **Fully managed, serverless** key-value / document store with **single-digit ms latency at any scale**.

DynamoDB is the opposite philosophy from Aurora: no schema, no joins, no manual scaling, predictable latency under load. The price is denormalisation: you design the table around the access patterns, not the data model.

Where it fits in ML:
- **Real-time prediction context**: user profile, last N events, recent items viewed, fetched in a single ms-latency lookup at request time.
- **Session state** for stateful agents or chat assistants.
- **Caching** of expensive prediction results keyed by input fingerprint.

### Picking between them

| Need | Pick |
|---|---|
| Bulk training data, model files, logs | **S3** |
| SQL queries, joins, transactions | **Aurora** |
| Single-key, low-latency, high-throughput lookups | **DynamoDB** |
| Time series at scale | DynamoDB or Timestream (out of scope here) |
| Analytical queries on historical data | S3 + Athena/Redshift (out of scope here) |

---

## Amazon SageMaker: the managed ML platform

> The end-to-end platform for **building, training, deploying, and monitoring** ML models at scale.

SageMaker is not one service but a suite, with each step of the ML pipeline mapped to a managed component.

### The pipeline mapped to SageMaker

```
Raw data on S3
       │
       ▼
 SageMaker Processing            ── preprocessing, feature engineering
       │
       ▼
 SageMaker Training / HPO        ── managed training jobs, hyperparameter tuning
       │
       ▼
 SageMaker Model Registry        ── versioning, promotion, lineage
       │
       ▼
 SageMaker Endpoint              ── real-time or batch inference
       │
       ▼
 SageMaker Model Monitor         ── data + model drift, quality alarms
       │
       ▼
 CloudWatch / EventBridge        ── alarms, automation triggers
```

### What each step buys you

| Component | What it does | Why use the managed version |
|---|---|---|
| **Processing** | Run a containerised preprocessing job on managed compute | No cluster to manage, scales to the job size |
| **Training / HPO** | Distributed training, automatic hyperparameter tuning | Spot instances supported, no infra setup |
| **Model Registry** | Stores versioned model artefacts with metadata, approval workflows | Governance and reproducibility |
| **Endpoint** | Real-time HTTPS endpoint or batch transform job, autoscaling | One API call instead of building a serving stack |
| **Model Monitor** | Statistics on input distribution, drift, model quality | Out-of-the-box ML observability |

### Where Amazon Bedrock fits

SageMaker is for **training and serving your models** (classical ML, fine-tuned LLMs, custom architectures). **Amazon Bedrock** is for **consuming foundation models** through a managed API without owning the weights or the GPUs:

- Single API across providers (Claude, Llama, Mistral, Cohere, Titan/Nova, Stable Diffusion).
- **Knowledge Bases** for fully managed RAG against S3 sources.
- **Agents** for tool-calling orchestration without writing an agent loop.
- **Guardrails** for content filtering, PII redaction, denied topics.
- **Custom Model Import** to bring your own fine-tuned weights into the Bedrock runtime.

The AWS counterpart of Azure OpenAI Service / Azure AI Foundry. If the use case is "we need an LLM that does X", Bedrock is the first stop; SageMaker is for when you actually need to train.

### Why "use SageMaker" is the right default on AWS

The alternative is to wire S3 + EC2 + ECR + a custom serving stack + a custom drift pipeline. That works but reproduces what SageMaker already gives, and the maintenance falls on the team. SageMaker pays back its higher per-hour cost in **engineering hours saved** unless the workload is unusual enough to need the bespoke setup.

The case for going outside SageMaker:
- **Custom training frameworks** that the SageMaker containers do not support cleanly.
- **Cost optimisation at scale** where the managed premium matters and the team has the headcount to operate the alternative.
- **Hybrid deployments** where part of the pipeline lives on-prem.

### Monitoring and automation glue

SageMaker emits metrics into **CloudWatch**: latency, errors, drift indicators from Model Monitor. **EventBridge** can subscribe to those events and trigger reactions: kick off a retraining pipeline when drift breaches a threshold, page on-call when error rate spikes, archive a stale model.

The pattern that ties this together is **drift → EventBridge → pipeline run → Model Registry promotion → endpoint update**, with the model never touched by hand in production.

---

## A canonical AWS ML pipeline

Reading order matches the architecture used in the section 2 exercise (KMeans clustering trained on SageMaker and persisted to S3):

1. **Ingest** raw data into S3.
2. **Process** features with a SageMaker Processing job, writing the prepared dataset back to S3.
3. **Train** with a SageMaker Training job, reading the prepared dataset, writing the model and metrics to S3.
4. **Register** the model in the Model Registry with version metadata.
5. **Deploy** the registered model behind a SageMaker Endpoint (real-time or batch).
6. **Monitor** with Model Monitor, with alarms on CloudWatch.
7. **Persist outputs**: for the exercise, the cluster assignments and centroids back to a designated S3 bucket.

The point of running this on AWS (rather than locally) is the **reproducibility envelope**: every step is logged, every artefact lands on S3 with provenance, and the same pipeline can be re-run on a larger dataset by changing the input path and the instance type.

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Region picked on cost alone | GDPR audit finding, latency from EU to US East | Treat region as a legal-first decision, not a price one |
| Single-AZ deployment in production | One AZ outage takes the model offline | At least 2 AZs for prod endpoints, multi-AZ Aurora |
| Aurora used as a data lake | High cost, slow scans on big tables | Keep bulk on S3, query with Athena; reserve Aurora for transactional access |
| DynamoDB queried like a relational DB | Bad partition design, hot keys, throttling | Design tables around access patterns, not the data model |
| S3 bucket exposed publicly by accident | Data leak | Default-deny bucket policies, S3 Block Public Access enabled at account level |
| Built a custom serving stack on EC2 | Maintenance cost grows, drift detection missing | Use SageMaker Endpoint unless the use case truly requires bespoke serving |
| Training jobs run on on-demand GPU instances | High bill | Use Spot instances for fault-tolerant training, reserve only for time-critical workloads |
| Model deployed without Model Registry | Cannot trace which version is in prod | Always register before deploying, even for one-off models |
| Cross-region replication enabled by reflex | Surprise egress bill | Replicate only if a documented requirement justifies it |
| Drift detection set up but no alert wired | Model degrades silently | EventBridge rule → SNS notification or pipeline trigger |

---

## When to use what

| Need | Service | Why |
|---|---|---|
| Land raw or processed data, model artefacts | **S3** | Universal, cheap, the lake everything else reads |
| Tabular features with transactional consistency | **Aurora** | Managed RDBMS, autoscales |
| Real-time lookup at <10 ms | **DynamoDB** | Serverless, predictable latency |
| Preprocess data on managed compute | **SageMaker Processing** | No cluster management |
| Train a model with HPO | **SageMaker Training + HPO** | Managed, supports Spot |
| Promote and govern model versions | **SageMaker Model Registry** | Lineage, approvals |
| Serve a model with auto-scaling | **SageMaker Endpoint** | Real-time or batch |
| Detect data and model drift | **SageMaker Model Monitor** | Native ML observability |
| Call a foundation LLM / agent / RAG without owning the model | **Amazon Bedrock** | Managed gateway, multi-provider |
| Centralise metrics and logs | **CloudWatch** | The AWS sink |
| Trigger automation on events | **EventBridge** | Glue between services |
| Survive a data-centre failure | Multi-AZ deployment | Same Region, no cross-region cost |
| Survive a Region failure / serve globally | Multi-Region deployment | Costlier, only when justified |

---

## See also

### Other notes
- [01_aiaas_and_cloud_architecture_fundamentals.md](01_aiaas_and_cloud_architecture_fundamentals.md) — the abstract pipeline that SageMaker concretises
- [03_azure_ai_ecosystem.md](03_azure_ai_ecosystem.md) — Azure's equivalent stack and its pyramid of services
- [04_google_cloud_vertex_ai_data_first.md](04_google_cloud_vertex_ai_data_first.md) — GCP's data-first answer to SageMaker
- [06_paas_vs_iaas_vs_oss_decision_framework.md](06_paas_vs_iaas_vs_oss_decision_framework.md) — when SageMaker (PaaS) is the right pick and when it is not

### Cross-module
- Module 01 [09_model_selection.md](../../01_machine_learning/notes/09_model_selection.md) — the classical model selection workflow that SageMaker HPO automates
- Module 02 [14_rag_production.md](../../02_large_language_models/notes/14_rag_production.md) — production patterns that apply to RAG endpoints hosted on SageMaker
