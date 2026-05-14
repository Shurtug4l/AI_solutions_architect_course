# Google Cloud AI and Vertex AI: the Data-First Philosophy

## TL;DR

Google Cloud's positioning is **data-first**: build the AI around the data warehouse, not the warehouse around the AI. The strategy is consistent with Google's own product history (Search, YouTube, Gmail are data products), and it translates into a stack where **BigQuery** is the gravitational centre and **Vertex AI** is the unified ML platform that orbits it. **BigQuery** is a serverless, columnar warehouse that scales from gigabytes to petabytes, with a billing model based on query bytes scanned (not stored), and a feature that justifies the philosophy on its own: **BigQuery ML**, the ability to train and serve ML models with plain SQL, with no data movement. **Vertex AI** unifies what other clouds split across multiple products: managed **Workbench** (notebooks with GPU/TPU), **AutoML** (no-code on tabular, vision, NLP, video), **Custom Training** (distributed on GPU/TPU with hyperparameter tuning), **Model Registry**, **Endpoints** (REST with autoscaling), **A/B testing**, **Feature Store** (centralised features shared between training and serving, guaranteed consistent). **Dataflow** is the managed Apache Beam runner for streaming and batch ETL, the data engineering layer that prepares data for ML, with **TensorFlow Transform** as the bridge that ensures the same code runs at training and serving time, eliminating training-serving skew. The four AI APIs (Vision, Language, Speech, Dialogflow) are the equivalent of Azure's Cognitive Services, all designed to plug into Vertex AI for customisation. The strategic question: **pick GCP when the data side is the differentiator** (large volumes, real-time analytics, BigQuery-first architectures, Google-ecosystem alignment); pick Azure when the enterprise integration is the differentiator; pick AWS when the breadth of the catalogue and the maturity of the operations are.

## Cheatsheet

| Service / Concept | One-line | Where it sits |
|---|---|---|
| **Data-first philosophy** | Build AI around the data warehouse, not the other way round | Strategy |
| **BigQuery** | Serverless columnar warehouse, petabyte-scale, SQL | Data foundation |
| **BigQuery ML** | Train and serve ML models with SQL, no data movement | Data foundation + ML |
| **Vertex AI** | Unified ML platform (single console for all ML steps) | ML platform |
| **Workbench** | Managed Jupyter with GPU/TPU access | Vertex AI |
| **AutoML** | No-code training for vision, NLP, tabular, video | Vertex AI |
| **Custom Training** | Distributed training on GPU/TPU clusters, HPO | Vertex AI |
| **Model Registry** | Versioned model catalogue with lineage | Vertex AI |
| **Endpoints** | REST inference with autoscaling | Vertex AI |
| **Feature Store** | Centralised features, training-serving consistency | Vertex AI |
| **Model Monitoring** | Drift detection, performance tracking, alerts | Vertex AI |
| **Vertex Pipelines** | Orchestrate end-to-end ML pipelines | Vertex AI |
| **Dataflow** | Managed Apache Beam, streaming + batch ETL | Data engineering |
| **Pub/Sub** | Real-time event streaming | Data engineering |
| **Cloud Storage** | Object storage, GCP's S3 equivalent | Data foundation |
| **AI APIs** | Vision, Language, Speech, Dialogflow as REST | Ready-to-use AI |
| **TensorFlow Transform** | Preprocessing code shared between training and serving | Anti-skew tool |

---

## The data-first philosophy: why it matters

> **Premise**: Google built its products on data. BigQuery, TensorFlow, Transformers, BERT all originated at Google. The cloud reflects that history.

In practical terms, the philosophy translates into design choices that are **different** from AWS or Azure:

- **No data movement** is the default. Models train where the data lives (BigQuery ML), preprocessing runs against the warehouse (Dataflow → BigQuery), inference reads directly from BigQuery for batch use cases.
- **The data warehouse is a first-class citizen**, not an analytics afterthought. BigQuery is positioned at the centre of the architecture, with ML, BI, and operational systems all reading from it.
- **Battle-tested internal tools**, externalised. BigQuery is the same engine behind YouTube and Google Search analytics; Vertex AI is built on the same infrastructure Google uses for its own ML.
- **Open source affinity**: TensorFlow, Kubeflow (which Vertex Pipelines is based on), Apache Beam (which Dataflow runs). The portability story is stronger than on the other two clouds.

The implication: GCP excels when **the data scale or the analytics workload is the binding constraint**. For a startup that will accumulate billions of events and needs to query them quickly, BigQuery is hard to beat. For a workload that is primarily transactional with a small ML component, the philosophical edge is less relevant.

---

## BigQuery: the centre of the data-first stack

> Not a data warehouse; **the foundation of the architecture**.

| Property | Detail |
|---|---|
| **Architecture** | Serverless, columnar storage, separated storage and compute |
| **Scale** | Gigabytes to petabytes, transparent autoscaling |
| **Pricing** | Pay per TB scanned by the query, not per TB stored (storage is cheap and separate) |
| **Performance** | Petabyte queries in seconds for analytics-shaped workloads |
| **Caching** | Intelligent query cache: repeated identical queries are free |

### BigQuery ML: SQL-native ML

The feature that defines the philosophy. **Train models with SQL**, no data export, no separate infrastructure.

```sql
CREATE MODEL my_churn_model
OPTIONS(model_type='logistic_reg') AS
SELECT customer_id, features, churned
FROM customer_dataset
```

That single statement creates a model, trains it on the source table, and registers it inside BigQuery. Serving is just another SQL function call.

| Capability | What it covers |
|---|---|
| **Algorithms** | Logistic/linear regression, k-means, matrix factorisation, time-series forecasting (ARIMA Plus), boosted trees, DNN, AutoML Tables |
| **Use cases** | Churn prediction, demand forecasting, segmentation, classification on tabular data |
| **Concrete benefit** | A team with 5 TB of transactional history trains a churn predictor in BigQuery in minutes, without moving any data |

**Where it stops**: BigQuery ML is excellent for **tabular ML on warehouse data**. It is not the right tool for image models, custom architectures, or low-latency online inference; those are Vertex AI's territory.

---

## Vertex AI: the unified ML platform

> Vertex AI eliminates the complexity of ML by unifying **all** Google Cloud ML services in one console.

The philosophical move: on AWS or Azure, ML touches half a dozen products. On GCP, the entry point is Vertex AI, and the rest is sub-components.

### Vertex AI Workbench

Managed Jupyter notebooks pre-configured with TensorFlow, PyTorch, Scikit-learn, with on-demand GPU/TPU access. Reads directly from BigQuery, no driver setup, no auth dance.

### Vertex AI AutoML

Automated training of custom models without writing code. Supports **vision, NLP, tabular, video**. The differentiator over competing AutoML offerings is the depth of integration with BigQuery: a Vertex AI AutoML job can be pointed at a BigQuery table directly.

### Vertex AI Custom Training

Distributed training on GPU/TPU clusters with custom containers or pre-built ones. Hyperparameter tuning is built-in. This is the equivalent of SageMaker Training or Azure ML jobs.

### Vertex AI Model Registry

Centralised versioning, lineage tracking, model approval workflows. Same purpose as SageMaker Model Registry; the GCP integration is tighter with BigQuery (lineage extends into the warehouse).

### Vertex AI Endpoints

REST API deployment with autoscaling. A/B testing between model versions is native: route a fraction of traffic to a candidate version, measure, promote or roll back.

### Vertex AI Feature Store

> A central feature repository that guarantees **the same features are used in training and serving**.

This is the single biggest cause of silent production failures: a feature computed one way in the training pipeline (offline, with full history) and a different way in serving (online, with partial context). The Feature Store removes that source of bugs by being the source of truth for both.

The collateral benefit: **reuse**. A feature defined once is shared across teams, which compresses development time for the second and third model.

### Vertex AI Model Monitoring

Native drift detection on inputs and outputs, performance tracking, alerting on anomalies. The equivalent of SageMaker Model Monitor.

### Vertex AI Pipelines

Orchestration of full ML pipelines (data ingestion → training → evaluation → deployment), based on Kubeflow Pipelines, fully managed. The native way to encode CI/CD/CT on GCP.

---

## Dataflow: data engineering for ML

> Managed **Apache Beam** runner for streaming and batch processing.

| Property | Detail |
|---|---|
| **Programming model** | Apache Beam, unified across batch and stream |
| **Scale** | Terabytes to petabytes, automatic worker scaling |
| **Use cases** | ML preprocessing, real-time stream ingestion, batch transformations on huge datasets |

### Why it matters for ML

| Function | Concretely |
|---|---|
| **Preprocessing for ML** | Cleaning, normalisation, complex feature engineering on massive datasets |
| **Real-time streaming** | Ingest events from Pub/Sub, process immediately for fraud detection or recommendations |
| **Batch processing** | Transform terabytes to build training sets or migrate systems |

### TensorFlow Transform: the anti-skew bridge

The same Apache Beam transformation code can be packaged with TensorFlow Transform and used **both** at training (in batch) **and** at serving (in real-time). The training-serving skew problem disappears because the code is literally the same.

### A canonical example

E-commerce store, **1 million events per hour** (clicks, purchases, views) streamed via Pub/Sub. Dataflow:
1. Ingests the stream.
2. Computes features in real time (rolling counts, last-N items, segment markers).
3. Writes the features to BigQuery for analytics and to the Vertex AI Feature Store for serving.

Every night, the recommendations model is retrained on the BigQuery snapshot of those features.

---

## AI APIs: the ready-to-use layer

GCP's equivalent of Azure Cognitive Services. Pre-trained REST APIs for common AI tasks, designed to be **upgraded** into Vertex AI custom models when the generic version is not enough.

| API | Capability |
|---|---|
| **Vision API** | Label detection, OCR, face detection, landmark recognition, content moderation |
| **Language API** | Sentiment, entity extraction, syntax analysis, content classification |
| **Speech API** | Speech-to-Text, Text-to-Speech, in 125+ languages |
| **Dialogflow** | Conversational AI for chatbots and voice agents |

The design discipline is the same as Azure's: try the API first; if it does not meet the bar, escalate to Vertex AI AutoML; if that does not, escalate to custom training.

---

## The data-first end-to-end workflow

A canonical GCP ML workflow runs from the warehouse to the endpoint without leaving the platform:

```
Pub/Sub (events) ─┐
                  ├─► Dataflow ─► BigQuery ─► Vertex AI Workbench (EDA / feature work)
Cloud Storage ────┘                  │
                                     ▼
                              Vertex AI Training (AutoML or Custom)
                                     │
                                     ▼
                              Vertex AI Model Registry
                                     │
                       ┌─────────────┴────────────┐
                       ▼                          ▼
              Vertex AI Endpoint           BigQuery batch predict
              (real-time, REST)            (offline scoring at scale)
                       │
                       ▼
                Vertex AI Model Monitoring
```

The hallmarks:
- **Data never leaves the platform**: no export to a separate ML stack.
- **Real-time and batch share infrastructure**: the same model is served via endpoint for live use and via BigQuery for nightly scoring.
- **Drift loops back to retraining** through Pipelines.

### Concrete case study: e-commerce churn prediction

Following the official end-to-end example:

| Stage | What runs |
|---|---|
| **Data** | User events streamed from Pub/Sub, order history from Cloud Storage |
| **Processing** | Dataflow aggregates features and writes them to BigQuery in real time |
| **Exploration** | Vertex AI Workbench reads from BigQuery for EDA and feature engineering |
| **Training** | Vertex AI AutoML on the BigQuery data to predict churn probability |
| **Deployment** | Real-time endpoint for the CRM + batch predictions on BigQuery for marketing campaigns |
| **Monitoring** | Model Monitoring on drift and performance over time |
| **Result** | End-to-end system serving 1M+ users, prediction latency <100 ms, zero infrastructure management |

The point is not "look at this case study", it is **the pattern**: every step is glued to the next without external tooling, and the warehouse is in the centre.

---

## When to pick GCP (and when not)

### Pick GCP if

- You are working with **large data volumes** (>1 TB) and analytics is a first-order concern.
- You want **cutting-edge AI** technologies (TensorFlow, JAX, the latest research from Google DeepMind).
- You are already in the **Google ecosystem** (Android, Firebase, Workspace).
- You prefer **open-source portability** (Kubeflow, TensorFlow, Beam, Kubernetes).
- You need fast analytics on huge datasets (BigQuery's killer feature).

### Consider alternatives if

- You are deeply integrated with **Microsoft or AWS**: the friction to migrate is higher than the GCP benefit.
- You need the **broadest service catalogue**: AWS still wins on breadth.
- You need **enterprise support at scale** with regional partnerships: Azure and AWS have larger account-management surfaces.
- Your priority is **legacy compatibility** with existing on-prem Microsoft tooling: Azure is the natural fit.

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| BigQuery used as a transactional database | Queries are slow, costs blow up on small frequent reads | BigQuery is for analytics; use Cloud SQL or Spanner for transactions |
| Per-query pricing surprises | A misconfigured query scans the entire warehouse | Always partition and cluster tables; use `SELECT *` only against partitioned slices; set query cost limits |
| Vertex AI AutoML used for non-tabular non-vision custom tasks | Poor results | AutoML covers well-defined modalities; for anything bespoke, use Custom Training |
| Training-serving skew despite the Feature Store | Feature definitions diverge between offline and online paths | Always declare features in the Feature Store; never compute serving features in application code |
| Pub/Sub → Dataflow pipeline with no schema | Schema drift breaks downstream training | Use schema-registered topics, validate at ingestion |
| Vertex AI Endpoints with no autoscaling configured | Pay for idle capacity or fail under load | Set min/max replicas, scaling thresholds, health checks |
| BigQuery ML used for image or sequence models | Bad fit, custom training is the right tool | BigQuery ML is for tabular ML on warehouse data |
| Cross-region data movement for analytics | Surprise egress bill, slower queries | Co-locate BigQuery, storage, and compute in the same region |
| Migrating from another cloud "for innovation" | Cost of switching exceeds the benefit | Pick GCP for new workloads where the data-first story applies; do not migrate without a TCO case |

---

## When to use what

| Need | Pick |
|---|---|
| Petabyte analytics with SQL | **BigQuery** |
| Tabular ML directly on warehouse data | **BigQuery ML** |
| Notebook with GPU/TPU access | **Vertex AI Workbench** |
| Custom model on vision/NLP/tabular without code | **Vertex AI AutoML** |
| Custom training with full control | **Vertex AI Custom Training** |
| Versioned model catalogue with lineage | **Vertex AI Model Registry** |
| Real-time inference with autoscaling | **Vertex AI Endpoint** |
| Offline scoring at warehouse scale | **BigQuery batch predict** |
| Feature consistency across training and serving | **Vertex AI Feature Store** |
| Stream and batch ETL with the same code | **Dataflow + Apache Beam** |
| Avoid training-serving skew | **TensorFlow Transform** |
| Orchestrate the full ML pipeline | **Vertex AI Pipelines** |
| Ready-to-use vision, OCR, label detection | **Vision API** |
| Sentiment, NER, syntax | **Language API** |
| Speech-to-text and text-to-speech | **Speech API** |
| Conversational chatbot or voice agent | **Dialogflow** |

---

## See also

### Other notes
- [01_aiaas_and_cloud_architecture_fundamentals.md](01_aiaas_and_cloud_architecture_fundamentals.md) — the abstract pipeline; GCP just collapses the seams
- [02_aws_ai_ml_stack.md](02_aws_ai_ml_stack.md) — AWS comparison (S3 ↔ Cloud Storage, SageMaker ↔ Vertex AI, no native BigQuery analogue)
- [03_azure_ai_ecosystem.md](03_azure_ai_ecosystem.md) — Azure comparison (Cognitive Services ↔ AI APIs, Azure ML ↔ Vertex AI)
- [06_paas_vs_iaas_vs_oss_decision_framework.md](06_paas_vs_iaas_vs_oss_decision_framework.md) — Vertex AI is the PaaS choice; sometimes you do not want it
- [07_hybrid_and_multi_cloud_patterns.md](07_hybrid_and_multi_cloud_patterns.md) — when to mix BigQuery with non-GCP workloads

### Cross-module
- Module 01 [09_model_selection.md](../../01_machine_learning/notes/09_model_selection.md) — the model selection logic that AutoML automates
- Module 02 [08_vector_stores_chroma_pinecone_weaviate.md](../../02_large_language_models/notes/08_vector_stores_chroma_pinecone_weaviate.md) — Vertex AI Vector Search is the GCP take on this layer
