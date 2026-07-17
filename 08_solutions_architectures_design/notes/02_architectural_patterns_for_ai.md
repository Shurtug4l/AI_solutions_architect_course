# Architectural patterns for AI

## TL;DR

An **architectural pattern** is a proven, reusable solution to a recurring design problem; in AI it answers four questions: how the system is organised over time, how data is treated, how it reacts in real time, and how it decomposes into services. The first fork is **batch vs streaming**: batch processes data in blocks on a tolerant schedule (training on historical data, nightly reports), streaming processes events continuously with low latency (fraud detection, real-time recommendations). They differ on **latency, complexity, consistency, and cost**, and the choice is rarely binary: **Lambda architecture** runs batch and real-time paths side by side for accuracy plus speed, **Kappa architecture** collapses everything into a single streaming pipeline for simplicity. **Event-driven architecture (EDA)** replaces synchronous calls with asynchronous events flowing through producers, a **broker** (Kafka being the canonical one), and consumers, which buys decoupling, scalability, and real-time reaction, exactly what event ingestion, online inference, and feedback loops need. **Microservices** decompose the AI system into independently deployable services, with three AI-specific shapes: **model serving** (one model, one REST/gRPC service), **pipeline** (preprocessing, feature extraction, inference as a chain of services), and **sidecar** (an AI component bolted next to an existing application). Pattern selection is requirements-driven: latency, data volume and velocity, team shape, budget. The emerging drift is toward Kappa, event-fed AI agents, feature stores, and edge inference.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **Architectural pattern** | Reusable solution to a recurring design problem | Avoids known mistakes, cuts complexity, aids maintenance |
| **Batch processing** | Data collected, then processed in blocks | Nightly pipelines, warehouse/lake, latency tolerated |
| **Streaming** | Continuous, near-real-time processing as data arrives | Broker + stream processor (Flink, Spark Streaming), online inference |
| **Lambda architecture** | Batch + real-time paths combined | Accuracy from batch, speed from the streaming leg |
| **Kappa architecture** | Streaming only, one unified pipeline | One codebase, no batch/speed duplication |
| **Event-driven (EDA)** | Components react to events, not synchronous calls | Producer, broker (Kafka), consumer; async and decoupled |
| **Microservices** | Small autonomous services talking over API/messaging | Independent scaling and deploy, per-service teams |
| **Model serving pattern** | Each model exposed as its own REST/gRPC service | One endpoint per model, versioned independently |
| **Pipeline pattern** | Preprocessing, features, inference as chained services | Each stage scales and fails on its own |
| **Sidecar pattern** | AI component adjacent to an existing app | Add AI without rewriting the host application |

## What an architectural pattern means in AI

> An architectural pattern is a solid, proven solution to recurring problems in software and AI architecture.

In an AI context the pattern governs three things at once: how data flows are treated, how training and inference are oriented, and how services are organised. The payoff for using established patterns instead of improvising is the classic one: avoid common mistakes, reduce complexity, increase maintainability. Note 01 set up the components and trade-offs of an AI system; this note is about the recurring shapes those components arrange themselves into.

## Batch vs streaming

> Batch processing: data processed in blocks, collected first and processed at non-immediate times. Streaming (real-time): continuous, near-real-time processing of data as it arrives.

The two differ along four axes:

- **Latency**: batch tolerates hours, streaming targets seconds or less.
- **Complexity**: batch pipelines are simpler to build, test, and rerun; streaming introduces ordering, windowing, and state management.
- **Consistency**: a batch job sees a complete, closed dataset and produces one consistent answer; a stream sees a moving window and produces continuously updated, provisional answers.
- **Cost**: batch amortises compute in scheduled bursts on infrastructure you can switch off; streaming means an always-on ingestion and processing layer.

### When batch fits

Typical use cases: model training on historical data, end-of-day analysis, reporting. The characteristics that signal batch: latency is tolerated, volumes are large and historical, and the data does not evolve minute by minute. Architecturally that translates into nightly pipelines, a data warehouse or data lake as the substrate (covered in depth in note 04 and in the module 07 notes), strong compute capacity, and few latency requirements. Exercise 01 (data pipeline with Python, the orders dataset) is exactly this shape: an ETL run over a closed dataset.

### When streaming fits

Typical use cases: fraud detection, real-time recommendations, predictive maintenance. The signals: very low latency requirements, a continuous flow of events, and the need to react immediately. Architecturally: a message broker, a stream processor (Apache Flink, Spark Streaming), stateful pipelines, and online inference. The catch, and it is a real one: "stateful" is where the complexity lives. A fraud model that needs the last N transactions per card is carrying per-key state that must survive restarts, scale with the keyspace, and stay correct under out-of-order events. That is a different engineering discipline from rerunning a nightly job.

## Hybrid patterns: Lambda and Kappa

It is rarely a clean binary. Two hybrid patterns combine the modes:

- **Lambda architecture**: batch and real-time legs run in parallel, combining the accuracy of a full historical recompute with the speed of a streaming view.
- **Kappa architecture**: streaming only, one unified pipeline, chosen to simplify.

```
  Lambda:
             +--> batch leg (full history, accurate) -----+
    data --->|                                            +--> combined view
             +--> real-time leg (fresh, fast) ------------+

  Kappa:
    data ---> single streaming pipeline ---> view
              (history handled by replaying the stream)
```

Which to choose in an AI project is the question the slides leave open, and the honest answer is: Lambda when the batch and real-time answers genuinely differ in quality and both matter; Kappa when one streaming codebase can serve both needs. My reading: Lambda's hidden cost is maintaining two implementations of the same logic that must agree, and that tax is why the industry trend (picked up again in the emerging-trends section) runs toward Kappa wherever replayable streams make it viable.

## Event-driven architecture

> Event-Driven Architecture (EDA): components react to events rather than to synchronous invocations.

Characteristics: asynchronous communication, decoupling of components, scalability, real-time response. In AI it earns its place in three moments: event ingestion, real-time inference, and feedback loops, the last one being underrated (predictions generate outcomes, outcomes are events, and events are how those outcomes get back to retraining without a bespoke integration).

### How to implement it for AI

Three key components:

- **Producer** (event source): the system emitting events.
- **Message bus / broker**: Apache Kafka is the canonical example; it buffers, orders, and distributes.
- **Consumer**: the AI-side services, inference and feature extraction.

The typical workflow:

```
  event --> broker --> inference service --> result --> feedback
    ^       (Kafka)     (consumer)                        |
    |                                                     |
    +--------------- feedback re-enters as events --------+
```

The decoupling is the architectural point: the producer does not know the model exists, the model does not know who produces events, and either side can be scaled, replaced, or multiplied without touching the other. That is also what makes EDA the natural transport under streaming AI: the broker is the boundary between "the world emitting data" and "the system reacting to it".

## Microservices for AI

> A microservices architecture is a system decomposed into small autonomous services that communicate via APIs or messaging.

Benefits: independent scaling, independent deployment, ease of evolution. Challenges: orchestration, inter-service latency, governance, monitoring. For AI specifically, three patterns recur:

- **Model serving pattern**: each model exposes its own independent service (REST or gRPC). One model, one endpoint, one deployment lifecycle. Exercise 02 (FastAPI image classifier in Docker) is this pattern in miniature.
- **Pipeline pattern**: a sequence of microservices for preprocessing, feature extraction, and inference. Each stage scales independently; a heavy feature-extraction step no longer forces you to overprovision the inference tier.
- **Sidecar pattern**: an AI component placed adjacent to an existing application and integrated as a microservice. This is the low-friction path for adding AI to a legacy system: the host application stays untouched.

Communication options: REST, gRPC, message queues, event bus. The choice is not cosmetic. REST is the universal default, gRPC wins on latency and typed contracts between internal services, and queues or an event bus shift the interaction from request/response to the event-driven model above. In practice a real AI platform mixes them: gRPC inside the pipeline, REST at the edge, events for the feedback loop.

## The comparison that matters

| | Batch | Streaming | Event-driven | Microservices |
|---|---|---|---|---|
| **Latency** | High | Low | Very low | Low |
| **Complexity** | Low | High | Medium-high | High |
| **Scalability** | Medium | High | High | Very high |

Reading the table as a decision rule:

- **Batch**: historical analysis, model training, reporting.
- **Streaming / event-driven**: real-time inference, reaction to events, feedback loops.
- **Microservices**: complex AI architectures with many models, diverse functionality, multiple teams.

One caveat on the table: the columns are not mutually exclusive alternatives. Batch vs streaming is a data-processing choice, event-driven is a communication style, microservices is a decomposition strategy. The worked examples below combine three of the four in a single system, which is the normal case, not the exception.

## Choosing a pattern

The pattern follows the requirements, not the other way around:

- **Functional requirements**: latency, data frequency, type of output.
- **Non-functional requirements**: scalability, resilience, maintainability, cost.
- **Data volume and velocity**: the batch vs streaming axis directly.
- **Team organisation and operations**: are microservices sustainable for this team? Who owns governance?
- **Budget and infrastructure**: complexity has a price; pay it only where the requirement justifies it.

The last two criteria are the ones junior designs skip. A microservices AI platform run by a two-person team is an outage schedule, not an architecture, and a streaming stack chosen for a daily-refresh use case is budget converted into complexity with no requirement behind it.

## Worked example 1: real-time fraud detection

- **Use case**: financial transactions, latency under 100 ms, high volumes.
- **Architectural choices**: streaming + event-driven + a dedicated inference microservice.
- **Components**: message broker, stream processor, inference model, feedback loop.
- **Trade-offs**: high complexity, real operating costs, stateful processing is unavoidable.

Every axis of the requirements pushes the same way: sub-100 ms latency rules out batch outright, high volume demands broker-based ingestion, and the fraud domain needs per-entity state (recent transaction history) that only a stateful stream processor provides. The system accepts the full complexity bill because the requirement leaves no alternative.

## Worked example 2: daily e-commerce recommendations

- **Use case**: e-commerce producing personalised daily recommendations, latency tolerated (up to 1 hour).
- **Architectural choices**: batch processing for the model plus an inference microservice, optionally event-driven for updates.
- **Components**: data warehouse, nightly batch pipeline, REST inference service, daily model refresh.
- **Trade-offs**: tolerated latency, contained cost, moderate complexity.

The mirror image of example 1: because the requirement tolerates an hour, batch is not a compromise, it is the correct answer, and every euro not spent on streaming infrastructure is a euro the requirement never asked for. The interesting nuance is the hybrid seam: the model retrains in batch, but serving is a live microservice, and events can trigger incremental updates without converting the whole pipeline to streaming. Note 03 takes this exact use case and turns it into a full architecture diagram.

## Emerging trends

- Growing adoption of the **Kappa pattern**: one streaming pipeline instead of Lambda's dual maintenance.
- **AI agents** built on streams of continuous events, the agent as a long-lived consumer reacting to the world rather than a request/response endpoint (agentic patterns were module 03's ground; LLM-side architectures are note 07).
- Deeper integration between **microservices and event-driven** styles: hybrid architectures as the default rather than a special case.
- Rising importance of the **feature store** (shared, consistent features across training and inference) and of **distributed inference at the edge**, which note 08 covers in depth.

## Design checklist

Before committing to a pattern, walk the list:

- Define the required latency.
- Estimate data volume and velocity.
- Determine how often, and how, the model gets updated.
- Evaluate service isolation and modularity needs.
- Decide the communication mode: REST, gRPC, events.
- Plan monitoring, governance, and fallback paths.
- Assess infrastructure capacity and operating costs.

The checklist doubles as a review instrument: an existing architecture that cannot answer one of these lines has an undocumented decision in it, and undocumented decisions are where systems rot. Scalability and resilience testing, the proof that the chosen pattern actually holds, is note 09's subject.

## Gotchas

- **Choosing streaming for prestige.** If the business requirement tolerates an hour, batch wins on every remaining axis: cost, simplicity, testability. Real-time is a requirement, not a virtue.
- **Lambda's silent divergence.** Two legs implementing the same logic will drift unless actively reconciled. If you cannot fund that reconciliation, Kappa or plain batch is the honest choice.
- **Event-driven without idempotent consumers.** Brokers redeliver. An inference consumer that produces side effects must tolerate seeing the same event twice, or the feedback loop amplifies duplicates.
- **Microservices before the team exists.** Independent deploy and scaling only pay off when there are independent teams and models to exploit them. A monolithic model server is a legitimate pattern for a small system.
- **Reading the comparison table as a menu of exclusives.** The columns compose. Fraud detection above is streaming and event-driven and microservices at once; the table compares properties, not products.

## See also

- Note 01 (software and AI architecture fundamentals) for the components and trade-off vocabulary these patterns arrange.
- Note 03 (from use case to architecture diagram) for the e-commerce recommendation case turned into a full diagram, plus C4 and diagramming tools.
- Note 04 (big data and data foundations) for the warehouse/lake substrate under the batch leg; deeper coverage in the module 07 notes.
- Note 05 (AI model lifecycle pipeline) for where training, deployment, and monitoring sit inside whichever pattern is chosen.
- Note 07 (architectures for LLM and generative AI) for the LLM-specific reference shapes, including agent architectures.
- Note 08 (edge AI vs cloud AI) for distributed edge inference.
- Note 09 (scalability, resilience, testing) for validating that the selected pattern holds under load and failure.
- Exercises: 01_data_pipeline_with_python (batch ETL in practice), 02_api_and_enterprise_integration (the model serving pattern as a FastAPI service in Docker).
