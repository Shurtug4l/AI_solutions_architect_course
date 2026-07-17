# From use case to architecture diagram

## TL;DR

This is the module's bridge from theory to practice: take the patterns of note 02 and apply them to a real case through a five-step workflow, **use-case analysis -> requirements mapping -> pattern choice -> component definition -> architectural drawing**. The worked case is an **e-commerce real-time recommender**: functional requirements (live personalised recommendations, continuous event stream, feedback loop) plus non-functional ones (**latency < 500 ms**, elastic scalability, governance, cost) drive a **hybrid pattern: streaming + batch + microservices + event-driven**, with recognised trade-offs in complexity and infrastructure cost. **Model versioning** gets its own focus: rollback, A/B testing, and coexistence of versions are architectural requirements, not MLOps afterthoughts. The second half turns the chosen architecture into a **diagram**: tool landscape (draw.io / diagrams.net, Lucidchart, Visio, Structurizr, Miro), the **C4 model** for levels of detail, best practices, a recommended **five-layer structure for AI solutions**, and six construction steps, illustrated with a context diagram that answers business questions (users, external systems, KPIs). The section closes with the **TELCO churn esercitazione**: a daily email-plus-CSV report needs no real time, so the pattern is plain **batch**, proof that the workflow can also conclude "the simple pattern wins".

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **Mapping workflow** | Use case -> requirements -> pattern -> components -> diagram | Abstract concepts become architecture decisions |
| **Functional requirement** | What the system must do | Live recommendations, event stream, feedback loop |
| **Non-functional requirement** | How well it must do it | Latency < 500 ms, elastic scale, governance, cost |
| **Model versioning** | Track model versions like source code | Rollback, A/B testing, coexisting versions |
| **Hybrid pattern** | Streaming + batch + microservices + event-driven | Low latency AND daily retraining AND evolvability |
| **Recognised trade-off** | Every pattern choice has a cost | More complexity, higher infrastructure spend |
| **Validation checklist** | Sanity questions before implementation | Decoupling, lifecycle, monitoring, fallback, docs |
| **C4 model** | Context, Containers, Components, Code | One architecture, four zoom levels by audience |
| **draw.io / diagrams.net** | Same free editor, two names | diagrams.net is the official project domain |
| **Context diagram** | System boundary plus external actors | Answers business questions, not protocol questions |
| **Batch pattern (TELCO)** | Daily job, no real-time requirement | Churn report by email + CSV every morning |

## The workflow: from abstract patterns to concrete decisions

Notes 01 and 02 supplied the vocabulary: batch vs streaming, event-driven, microservices, and the criteria for choosing among them. This session applies them to a real case through a fixed sequence:

```
  use-case      requirements     pattern      component      architecture
  analysis  ->  mapping      ->  choice   ->  definition  ->  diagram
```

The order matters. Choosing a pattern before mapping requirements is the classic failure mode (resume-driven architecture: pick Kafka, then invent the requirement). The workflow forces requirements to come first, so the pattern is a consequence, not a preference.

## Use case: e-commerce with real-time recommendations

An e-commerce platform that recommends products to users in real time. The relevant actors and flows:

- the user generates clicks, navigation, purchases
- the frontend requests recommendations in real time
- the AI recommendation system computes the suggestions
- data ingestion captures every user-driven event
- a batch pipeline periodically updates the model
- a feedback loop monitors performance and drift

The defining constraint: **instant personalisation**. The system must respond to what the user is doing right now, not to who the user was yesterday. That single sentence already smells like streaming, but the workflow demands the requirements pass first.

### Requirements: functional vs non-functional

The nature of the requirements drives the architecture, so the two families are kept separate:

**Functional** (what the system does):
- live recommendation and personalisation
- handling of a continuous event stream
- user feedback loop

**Non-functional** (how well it does it):
- **latency < 500 ms** on the recommendation path
- elastic scalability, absorbing traffic peaks
- governance: security, model versioning
- operating costs: budget and optimisation

The non-functional list is where architectures are actually decided. Any pattern can produce a recommendation eventually; only some can produce it in under 500 ms during a Black Friday peak without bankrupting the infrastructure budget.

### Data, volumes, and constraints

Beyond requirements, the slides list the context that shapes the choice: data volumes (sessions per minute, purchase history, clickstream) and cross-cutting constraints (data governance, privacy, logging, model versioning). Clickstream volume is what rules out "just query the database on each page load", and the privacy constraint follows the user data through every component that touches it.

### Focus: model versioning

> Model versioning is the practice of managing and tracking the different developments of a machine learning model, the way source code is managed. The goal is reproducibility, traceability, and safe deployment to production.

Three capabilities to design in from the start:

- **Rollback**: return immediately to a previous stable version when a deployment goes wrong.
- **A/B testing**: compare two or more model versions in real production traffic.
- **Coexistence**: keep several versions of the same model live and route to the appropriate one.

This lands in the requirements phase, not the deployment phase, and that placement is the point: rollback and A/B routing impose structure on the serving layer (an inference service that can address versions, a registry that stores them). Bolting them on after the architecture is frozen is expensive. The registry side of this story is note 06; the lifecycle it belongs to is note 05.

### Scenario analysis: streaming vs batch elements

Trace the user's journey and how data travels:

```
  data collection -> feature engineering -> inference -> recommendation -> feedback
```

Then split the elements by tempo: clicks and sessions are **streaming** (they lose value in seconds), model retraining is **batch** (daily is enough). This split is what selects the pattern. One flow, two clocks.

### Pattern choice and its trade-offs

The mapping from requirement to pattern, straight from the slides:

- low latency -> **streaming**
- daily model update -> **batch**
- system evolution -> **microservices**

Proposed pattern: **hybrid "streaming + batch" + microservices + event-driven**. The rationale is balance: speed on the inference path, scale and simplicity on the training path, maintainability through service decomposition. This is the Lambda-shaped hybrid of note 02 applied for real.

The recognised trade-offs, stated up front rather than discovered in production: **greater operational complexity** (three paradigms to run at once) and **higher infrastructure costs** (broker, real-time pipeline, scaled microservices). The later slide on critical points adds model management (versioning, rollback, A/B), **fallback and resilience** (what happens if the model does not respond?), and maintenance (model evolution, feature drift, new data). The fallback question deserves the emphasis: a recommender that returns nothing when inference fails is a broken page; one that falls back to "most popular products" is a degraded but working shop. Resilience patterns are note 09's territory.

### Component definition

The chosen pattern expands into nine components:

1. Streaming event ingestion (clicks, sessions)
2. Event-stream broker (e.g. Kafka)
3. Real-time transformation pipeline (feature extraction)
4. Feature store / historical database
5. Model inference service (microservice)
6. Batch pipeline (training, updated model)
7. Feedback loop and model monitoring
8. Frontend API / recommendation service
9. Monitoring, logging, DevOps

### Flows between components

Three flows, matching the three clocks of the system:

```
  Streaming / inference (< 500 ms):
    user click -> broker -> feature extraction -> inference -> frontend

  Batch / training (nightly):
    historical data -> nightly job -> updated model -> deploy

  Feedback loop (continuous):
    user outcome -> monitoring -> retraining
```

The feedback loop is what makes this an AI architecture rather than a fast website: user outcomes feed monitoring, monitoring detects drift, drift triggers retraining, retraining redeploys through the versioned registry. Close the loop or the model quietly rots.

### Validation checklist

Before implementation, the slides propose a validation pass:

- Are the services decoupled and scalable?
- Does the chosen pattern match the requirements (latency, volume)?
- Is the model lifecycle defined (versioning, rollback, monitoring)?
- Is data and model monitoring in place (drift, accuracy, latency)?
- Is there a fallback if inference fails?
- Have operating costs and maintenance been considered?
- Is documentation ready (diagram, metadata)?

Seven questions, cheap to ask, and each "no" is far cheaper to fix on the whiteboard than in production. Note the last item: the diagram is part of the architecture's definition of done, which is exactly where the second half of this note picks up.

## From architecture to diagram

### Why diagrams matter

A diagram makes the architecture communicable to teams, documentable, and evolvable. Concretely, the slides give it four jobs: it enables communication between technical and non-technical teams, it exposes bottlenecks, risks, and dependencies, it supports maintenance and evolution by making visible what would otherwise stay hidden, and it acts as the **blueprint** of how the system is built. The slides' verdict, worth endorsing: time invested in diagram quality is a good investment for the project. An architecture that lives only in one architect's head is a bus-factor of one.

### Tool landscape

- **draw.io (diagrams.net)**: free diagram editor, works in the browser (online or offline), wide shape library, drag shapes onto a grid, connect with arrows, save to Google Drive, OneDrive, or locally. Naming clarified: draw.io and diagrams.net are the **same software**; diagrams.net is the official open-source project name and main domain, draw.io the original and more popular name.
- **Lucidchart**: professional cloud-based tool; adds real-time collaboration, comments, and integrations with Slack, Google Workspace, and Atlassian. Free tier with limits, paid plans beyond.
- **Others**: Visio, **Structurizr** (built around the C4 model), Miro.

Selection criteria: ease of use, component libraries, collaboration, integration with the repo and documentation. For coursework and most real work draw.io is the default: free, no account, and the XML file versions cleanly in git, which quietly satisfies the "integration with repo" criterion better than the paid tools do.

### Diagram levels and the C4 model

The right diagram depends on the audience, so levels of detail are distinguished: **layered diagrams** following the C4 progression, **high-level diagrams** giving stakeholders the general picture, and **detail diagrams** showing flows, protocols, and dependencies.

> The C4 model (Context, Containers, Components, Code) is a system-architecture diagramming method designed for software architects. It shows the architecture of a software system through a series of diagrams at four zoom levels.

Context (the system and its users), Containers, Components, Code. The strength is the explicit zoom contract: a stakeholder gets the context diagram, a developer gets components, and nobody gets a single diagram trying to serve both audiences and failing at each.

### Best practices for drawing

- Keep it simple and clear: do not overload the canvas with components.
- Use consistent symbols and notation: uniform shapes, colours, styles.
- Label components and data flows clearly.
- Group related components into layers or containers.
- Use standard libraries and stencils (AWS icons, microservice and message-broker shapes).
- Use clear connectors with arrows and directions; avoid crossing lines.
- Use whitespace; avoid overcrowding.
- Add legends, annotations, and versioning.

The last item is the one most often skipped: an undated, unversioned diagram is a rumor, not documentation.

### Recommended layer structure for AI solutions

```
  1. Data ingestion and acquisition
  2. Transformation and feature engineering
  3. Model / inference
  4. Monitoring and feedback loop
  5. Application services / users
```

Show the flows between layers in logical order, and make the architectural pattern visible on the diagram itself: batch vs streaming paths, microservices, event-driven links. For the e-commerce case the recommended symbols are microservice, event broker, feature store, and model, with the streaming, batch, and feedback flows each visually distinct.

### Building the diagram in six steps

1. Define the scope of the diagram (which level of detail).
2. Identify the main components and layers.
3. Place components on the canvas, grouped by layer.
4. Add connections and flows, with directions and annotations.
5. Apply a uniform style and a legend; verify readability.
6. Review with stakeholders and iterate.

Step 6 is the one that separates a diagram from a drawing: it is a communication artifact, so it is only done when the audience confirms it communicates.

### Context diagram example: the e-commerce recommender

Applying C4 level 1 to the running case, the context diagram shows the whole system and its external relations. The user interacts via the Frontend; the Frontend requests recommendations from the Recommendation Service; the service interfaces with an external payment system, an internal database producing purchase events, Analytics/Marketing reading events for A/B tests, campaigns, and reports, and third-party data providers (product catalogs, price feeds, enrichments).

```
                        +--------------------------------------+
   [User] ---uses--->   |  Frontend --> Recommendation Service |   ---> [Payment Gateway]
                        |     Analytics/Marketing     DB       |   ---> [3rd-party data providers]
                        +---------------- system ------------- +
```

This level answers **business questions**: who are the users? which external systems must be integrated? which business KPIs must be measured? What to highlight: the external actors (User, Payment Gateway, third parties), the system boundary (the box enclosing Frontend, Recommendation Service, Analytics, DB), visible KPIs, a privacy/GDPR note, and suggested annotations or ADRs. No protocols, no pods, no ports: those belong two zoom levels down.

## Esercitazione: TELCO churn architecture

The section's hands-on applies the whole workflow to a fresh case. A TELCO company wants a churn-analysis system: every day the marketing team receives an **email with a CSV file** listing the customers most at risk of churn, plus statistics. The at-risk customers are identified by an AI model making predictions.

Requirements pass: the deliverable is a daily report. Nobody needs a churn score in 500 ms. So the pattern is **batch**, and the honest reading is that this is the exercise's real lesson: after a session spent building a hybrid streaming architecture, the workflow applied correctly to this case concludes that the simplest pattern is the right one. Real-time behaviour is not required, therefore not paid for.

The main pipeline steps:

```
  Data Sources -> Ingestion Pipeline -> Feature Processing Pipeline
      -> Model Training Pipeline -> Trained Model Registry
      -> Batch Inference Job (daily) -> Churn Scores + analytics
      -> Email Service -> Marketing Team
```

The model registry sitting between training and inference is the versioning focus of the first deck made concrete (and note 06's subject). The deliverable is the draw.io diagram of this architecture, following the layer structure and the six construction steps above. Module 08's exercise 04_industry_ai_architecture continues the draw.io practice on industry-scale cases.

## See also

- Note 01 for the conceptual layers and trade-off vocabulary this workflow assumes
- Note 02 for the patterns being mapped here: batch, streaming, Lambda/Kappa, event-driven, microservices, and the selection criteria
- Note 05 for the model lifecycle pipeline behind the training and feedback flows
- Note 06 for the model registry and the build-vs-reuse decision the TELCO pipeline touches
- Note 09 for the resilience and fallback questions the validation checklist raises
- exercises/04_industry_ai_architecture for the draw.io workshop that extends this section's practice
