# Software and AI architecture fundamentals

## TL;DR

**Software architecture** is the set of structures needed to understand, build, and modify a system: **components** (modules, services, storage), **relations** (APIs, messaging, protocols), and **properties** (latency, throughput, availability). It is the system's **blueprint** and the shared language between business, development, and DevOps. Architecture answers "the what and the why", design answers "the how (internal)", implementation answers "the how (code)". The classic principles still hold: **modularity**, **high cohesion / low coupling**, **technology agnosticism**, **evolvability**, **domain orientation**. AI does not repeal any of this, it adds on top: new components (data pipelines, feature stores, models, inference services), new architectural dimensions (real-time latency, model state, model lifecycle), and a hybrid system where traditional software must coexist with a probabilistic "intelligent" component. The typical AI architecture chains **ingestion, feature engineering, training, serving, monitoring, retraining**, backed by model, feature, and metadata stores, and splits into a compute-heavy offline **training pipeline** and a latency-sensitive **inference pipeline** whose feature engineering must be identical. With generative AI the training pipeline mostly leaves the building (foundation models, APIs, fine-tuning at most) and inference becomes the pipeline that counts. The governing rule for all of it: **everything is a trade-off**, so motivate and document every decision against the business context.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **Software architecture** | Structures to understand, build, modify a system | Components + relations + properties, the blueprint |
| **Architecture vs design vs implementation** | The what/why vs the internal how vs the code | Fundamental decisions vs module patterns vs libraries and tests |
| **High cohesion / low coupling** | Each part does one thing, parts barely depend on each other | A change stays local instead of rippling |
| **Evolvability** | The system can grow without a full rewrite | New features land as additions, not surgery |
| **AI architecture components** | Ingestion, features, training, serving, monitoring, retraining | Plus model / feature / metadata stores |
| **Training pipeline** | Offline, batch, compute-heavy; output is a trained model | GPU/TPU clusters, scheduled runs |
| **Inference pipeline** | Applies the trained model to new data | Latency-sensitive, often streaming |
| **Feature engineering parity** | Inference features must match training exactly | Same encoding, same normalization, or silent garbage |
| **Foundation / pre-trained models** | Someone else paid for the training pipeline | GPT, Gemini, Claude; HuggingFace hubs; provider APIs |
| **Fine-tuning** | Further training of a pre-trained model on specific data | BERT for NLP, YOLO for vision, small focused dataset |
| **Model drift** | Performance decays as data changes over time | Monitoring alarms, retraining trigger |
| **Hallucination** | Confident, fluent, false generative output | Invented dates, names, citations, statistics |
| **"Everything is a trade-off"** | No decision is free of cost | Documented rationale, business context as tiebreaker |

## What software architecture is

> Software architecture is the set of structures needed to understand, build, and modify a software system.

The architecture is the **blueprint**. The structures it comprises are three: **components** (modules, services), **relations** (interactions, protocols), and **properties** (latency, throughput, availability). It defines the organization of the system, the technologies in play, and who is responsible for what, and through those choices it drives quality, maintainability, scalability, and operating cost. Just as important, it works as a common language across stakeholders: business, development, DevOps all point at the same diagram. Architectural decisions are strategic decisions, which is why they are made deliberately and not discovered in the codebase after the fact.

The slides break the key structures into four, and the fourth is the one people forget:

- **System components**: modules, microservices, data storage.
- **Relations and connections**: how components interact (APIs, messaging).
- **Architectural properties and constraints**: latency, throughput, security, scalability.
- **Stakeholders and teams**: team structure and how it correlates with the architecture.

That last item is Conway's law territory in all but name: the shape of the teams and the shape of the system constrain each other, so an architect who ignores the org chart is designing fiction.

## Architecture vs design vs implementation

Three terms, routinely conflated:

- **Architecture**: the fundamental decisions, the high-level structure.
- **Design**: internal decomposition of modules, choice of patterns and algorithms.
- **Implementation**: code, libraries, tests, deployment.

> Architecture is "the what and the why", design is "the how (internal)", implementation is "the how (code)".

The boundary is fuzzy in practice, but the test is cost of change: if reversing a decision means rebuilding half the system, it was architectural, whatever the ticket called it.

## Key principles

- **Modularity and separation of responsibilities**: each part owns one concern.
- **High cohesion / low coupling**: strong internal focus, weak external dependency. This is the principle the others mostly reduce to.
- **Technology agnosticism**: the architecture is independent of specific implementations. In practice technology leaks into structure constantly; the realistic reading is to keep boundaries clean enough that swapping a technology does not mean redrawing the diagram.
- **Evolvability**: the system must be able to evolve without total rewrites.
- **Domain orientation**: the architecture reflects the business model, not the framework of the month.

For AI systems evolvability quietly becomes the load-bearing principle: models get replaced far more often than services, so an architecture that cannot swap a model cheaply is already legacy.

## The software architect role

The architect defines the structure, selects patterns and technologies, weighs constraints, and manages the evolution of the software. The role is collaborative by construction: development teams, DevOps, data science, business stakeholders. It demands both technical vision and the ability to communicate complex concepts, because the slides' summary is exact:

> The software architect is a bridge between strategic vision and technical implementation.

The AI variant of the role adds data science to the list of teams to bridge, which matters more than it sounds: data scientists and platform engineers optimize for different things (experiment velocity vs operational stability), and the architect is where that tension gets resolved.

## What AI adds to the picture

An AI architecture is a traditional architecture plus four kinds of change:

- **New components**: data pipelines, feature stores, models, inference services.
- **New architectural dimensions**: real-time latency, throughput, state, and the model lifecycle as a first-class concern.
- **A hybrid system**: traditional software interacting with an "intelligent" component whose behavior is learned, not coded.
- **New non-functional requirements**: model maintainability, governance, traceability.

The hybrid point is the deep one. Classic architecture assumes deterministic components with specifiable contracts. A model is a component whose behavior depends on data it was trained on and data it will see, so its "contract" degrades silently. Much of AI architecture is scaffolding built to notice and correct that degradation (notes 05 and 09 develop this).

## Typical components of an AI architecture

The recurring cast, whatever the use case:

- **Data ingestion**: collection from databases, logs, APIs, data lakes.
- **Data transformation / feature engineering**: cleaning, normalization, feature creation.
- **Model training**: training on the prepared data.
- **Model serving**: exposing the model to users and services.
- **Monitoring**: continuous performance control.
- **Retraining**: periodic refresh on the most recent data.
- **Stores**: model, feature, and metadata stores backing all of the above.

A system built from these parts is not "a model": it is a continuous pipeline that turns raw data into value. The module's exercise 01 (data pipeline with Python) builds the ingestion and transformation stages by hand, which is the fastest way to internalize why they are separate components.

## Training pipeline vs inference pipeline

The two fundamental moments are **training** (builds the model) and **inference** (applies it). Each has its own goals, resources, and constraints, and confusing them is the root of several classic production failures.

```
  TRAINING PIPELINE (offline, batch, compute-heavy)

  Data Ingestion -> Feature Engineering -> Model Training
                                                |
                                        trained, validated model
                                                v
  POST-TRAINING (user-facing, continuous)

  Model Serving -> Monitoring -> Retraining
       ^                            |
       +----------------------------+
```

```
  INFERENCE PIPELINE (online, latency-bound)

  Data Ingestion -> Feature Engineering -> Model Inference
                    (identical to the
                     training-time version)
```

Three operational facts about the training side:

1. **Compute demand**: training chews through large data volumes and needs serious hardware (GPU, TPU, distributed clusters).
2. **Batch, offline**: the pipeline can run scheduled and asynchronous with respect to end users.
3. **Retraining frequency is use-case driven**: a fraud detection model may need weekly updates, a document classifier far fewer.

The differences that matter:

- Training outputs a model; inference uses one. Different artifacts, different SLOs.
- **Feature engineering must be identical across the two pipelines**: same encoding, same normalization, or the model receives data in a format it never saw. This is training-serving skew, the most boring and most common way ML systems fail in production, and it is the practical argument for putting a feature store in the architecture rather than duplicating transformation code.
- Different architectural patterns fit each side: batch for training, streaming for inference is the slides' shorthand. Directionally right, though inference can be batch too (nightly scoring is a thing); note 02 treats the batch vs streaming choice properly.

## The pre-trained and generative shift

Classical AI assumed the training pipeline lived inside the organization. Generative AI and ever-larger models broke that assumption, for a blunt reason: training an LLM from scratch costs more than almost any organization can justify. Today the default is:

- **Foundation models** (GPT, Gemini, Claude).
- **Pre-trained models** from public hubs (HuggingFace, GitHub).
- **Paid provider APIs** (OpenAI, Google, Anthropic).
- **Fine-tuning** of pre-trained models.

So with generative AI **the pipeline that counts is inference**: the model is consumed via API or pulled from an open repository (Ollama, Meta releases), and the architecture's center of gravity moves to serving, orchestration, and control.

The exception is **fine-tuning**: start from an existing model (BERT for NLP, YOLO for computer vision) and run further training on a smaller, specific dataset, reusing the architecture and what the model already learned. It is a training pipeline, but a drastically cheaper one. The build vs reuse decision, and the model registry that keeps the resulting zoo under control, is note 06.

## Validation and hallucinations in generative models

Validating an LLM is not validating a classifier. Traditional models have clean metrics: accuracy, F1, RMSE. Generative output is free text, hard to score automatically, and performance can degrade over time (**model drift**) or shift with the usage context, so validation has to be continuous rather than a one-shot gate before release.

> A hallucination is an LLM generating false, invented, or ungrounded content, presented in a confident and convincing tone.

Invented dates, names, citations, statistics. The mechanism is not a bug: an LLM does not "know" the truth, it generates the most probable token given the context, and where the correct fact is poorly represented in training data the model completes with something plausible and wrong. Because the failure is intrinsic to the generation mechanism, elimination is effectively impossible; the honest goal is mitigation:

- **RAG**: ground answers in retrieved documents (note 07).
- **Prompt engineering**: constrain the task and the allowed sources.
- **Temperature and generation parameters**: trade creativity for determinism.
- **Human in the loop**: a person validates before the output has consequences (note 08).

Worth saying plainly: these mitigations are architectural components, not model settings. RAG is a retrieval subsystem, HITL is a workflow stage. The moment hallucination control enters the requirements, the architecture diagram changes.

## The three-layer conceptual model

Where do the components sit? Three layers:

```
  +---------------------------------------------------+
  |  1. Application services / business logic         |
  |     (what the user and the business touch)        |
  +---------------------------------------------------+
                 ^                    |
        predictions, results     data, requests
                 |                    v
  +---------------------------------------------------+
  |  2. Data pipelines / feature engineering          |
  |     (ingestion, transformation, feature serving)  |
  +---------------------------------------------------+
                 ^                    |
           features                training +
                 |               inference data
                 |                    v
  +---------------------------------------------------+
  |  3. ML/AI model (training + inference)            |
  |     (with monitoring watching the boundary)       |
  +---------------------------------------------------+
```

The model is deliberately at the bottom: business logic should not know or care which model answers, only that layer 2 delivers well-formed features and layer 3 delivers predictions within the agreed properties. Ingestion sits at the top of layer 2, inference at the top of layer 3, monitoring watches the flows between layers. This layering is what makes the evolvability principle concrete for AI: swap the model, keep the contract.

## Key questions for an AI architecture

The slides' checklist for judging whether a structure is the right one:

- Where and how is data managed? (storage, data lake, data warehouse, feature store; the lake vs warehouse vs lakehouse decision is note 04, covered in depth in module 07 notes)
- What is the maximum inference latency? (real-time vs batch)
- What data volume and velocity? (batch vs streaming, note 02)
- How is the model lifecycle managed? (versioning, rollback, A/B testing, monitoring, note 05)
- How are scalability, resilience, and fallback guaranteed? (note 09)
- What are the non-functional requirements? (security, compliance, explainability, notes 10 and 11)

The checklist looks generic until you notice each question pins down one architectural dimension that AI added. Answer all six honestly and most of the architecture has drawn itself.

## Everything is a trade-off

> "Everything is a trade-off": every decision has pros and cons.

The slides' examples: microservices vs monolith, latency vs cost, generality vs specialization. Two consequences follow. First, architectural decisions must be **motivated and documented**, because an undocumented trade-off gets relitigated every quarter by whoever was not in the room. Second, **business context drives the trade-offs**: there is no best architecture in the abstract, only one that fits this workload, this budget, this team. The AI-flavored version of the same law shows up immediately in practice: a lower-latency model costs more to serve, a more general model is worse at your niche, a more frequent retraining schedule buys freshness with compute and operational risk.

## AI-specific challenges

The challenges that traditional software architecture never had to price in:

- **Model uncertainty**: drift, data changing over time. The component's quality is a function of the world, not just of the code.
- **State and model management**: feature stores, metadata, versioning. Models are heavyweight stateful artifacts with lineage, not stateless binaries.
- **Integration** between traditional software and ML/AI components: deterministic code calling a probabilistic dependency needs contracts, fallbacks, and error semantics that plain APIs do not force you to think about.
- **Data scalability, latency, model monitoring**: the operational load grows with data volume, not only with request volume.
- **Governance, explainability, bias, result traceability**: for AI these are architectural requirements, not policy documents; they dictate components (logging, lineage, audit trails) and appear in the diagram. Notes 10 and 11 take these on directly.

## Gotchas

- **Treating the model as the system.** An AI system is the pipeline: ingestion, features, serving, monitoring, retraining, stores. The model is one component, and with generative AI often a rented one.
- **Divergent feature engineering.** Training and inference transforming data differently is silent: no exception, just wrong predictions. Parity by construction (shared code or a feature store) beats parity by discipline.
- **Reading "technology agnosticism" as tool indifference.** The principle protects boundaries, not laziness: choose technologies deliberately, but keep the architecture valid if one is swapped.
- **Planning a from-scratch training pipeline for an LLM use case.** For generative work the training pipeline is the provider's problem; the architecture's job is inference, grounding, and control. Fine-tuning is the budget-shaped exception.
- **Validating a generative model once.** Drift and context shift make LLM validation a continuous process; a one-time eval before release is a snapshot of a moving target.
- **Undocumented trade-offs.** A decision without a recorded rationale is indistinguishable from an accident. "Everything is a trade-off" only works as a discipline if the trade-offs are written down.

## See also

- [02_architectural_patterns_for_ai.md](02_architectural_patterns_for_ai.md) - batch vs streaming, Lambda/Kappa, event-driven and microservices patterns for the pipelines sketched here
- [04_big_data_and_data_foundations.md](04_big_data_and_data_foundations.md) - the data lake / warehouse / lakehouse choices behind the "where is data managed" question
- [05_ai_model_lifecycle_pipeline.md](05_ai_model_lifecycle_pipeline.md) - the training, validation, deployment, monitoring loop in full
- [06_pretrained_vs_custom_models_and_model_registry.md](06_pretrained_vs_custom_models_and_model_registry.md) - the build vs reuse decision and model registries
- [07_architectures_for_llm_and_generative_ai.md](07_architectures_for_llm_and_generative_ai.md) - LLM reference architectures and RAG as hallucination mitigation
- Module 06 notes for deployment and MLOps mechanics; module 07 notes for data architecture depth
