# Roles and Stakeholders in AI Projects

## TL;DR

AI projects need a wider set of roles than traditional software, and the way those roles interact decides whether the project ships value. Two roles sit at the centre. The **AI Product Manager** owns the *what* and the *why*: the business problem, the vision, the prioritisation, the stakeholder hub between business and engineering. The **AI Solution Architect** owns the *how*: the technical design, feasibility, choice of frameworks and models, scalability, robustness, integration. Their partnership is the spine of every successful AI project, and the mountain-climbing analogy is useful: the **PM makes sure you are climbing the right mountain**, the **SA makes sure you have the right gear**. Both must speak both languages well enough to collaborate - the PM needs to understand drift, latency, accuracy limits; the SA needs to understand business KPIs and why a feature matters strategically. Around them sits the broader **orchestra**: **Data Scientists** as explorers (can we solve this with the data we have?), **ML Engineers** as builders (industrialise the prototype into robust production software), **DevOps/MLOps** as guardians (keep the system alive, deploy, monitor, retrain continuously), and **Business Stakeholders** as commissioners (define the goal, judge the result, provide domain expertise). The recurring obstacle is the **"two languages curse"**: technical teams speak in accuracy/precision/recall, business speaks in revenue/conversion/retention. The Solution Architect is the **universal translator** - decomposing high-level goals into measurable technical targets via the same translation chain seen in [02_kpis_lifecycle_drift.md](02_kpis_lifecycle_drift.md). Without that translator, even the most talented team ends up optimising the wrong metric on a model nobody adopts.

## Cheatsheet

| Role | Owns | One-line |
|---|---|---|
| **AI Product Manager (PM)** | *What* and *why* | Stakeholder hub; business problem, vision, prioritisation; "the right mountain" |
| **AI Solution Architect (SA)** | *How* technically | Feasible, scalable, robust design; "the right gear"; **universal translator** |
| **Data Scientist** | Exploration | "Can we solve this with the data we have?"; prototype and proof-of-value |
| **ML Engineer** | Industrialisation | Prototype → production-grade software; scalable serving, API integration |
| **DevOps / MLOps** | Continuous operation | Deployment + monitoring + retraining; drift detection; "guardian of the system" |
| **Business Stakeholder** | Goal and judgement | Defines the *why* and the success criteria; provides domain expertise |
| **The two languages curse** | The recurring failure mode | Tech speaks accuracy; business speaks revenue; without a translator, both lose |
| **PM ↔ SA collaboration** | The project's spine | Vision (PM) anchored to feasibility (SA), every initiative |
| **Cross-functional ownership** | The antidote to silos | All roles aligned around the same business KPI |

---

## The two central roles

### AI Product Manager (PM)

The PM in an AI context plays the same fundamental role as in any product organisation - own the *what* and the *why* - but with additional AI-specific responsibilities that traditional PMs rarely face.

#### Core responsibilities

- **Stakeholder hub.** The PM is the central communication node between business stakeholders and the technical team. They translate business requirements into something the technical team can act on, and they translate technical limitations (data quality, model accuracy ceilings, latency constraints) back to non-technical stakeholders.
- **Expectation management.** Stakeholders often arrive with unrealistic expectations - "AI will solve X" without understanding the probabilistic nature, the data dependencies, or the time required. The PM's job is to set those expectations honestly.
- **Mediation.** Without the PM, the technical team risks working on the wrong problem (because the requirements were filtered through a game of telephone), and the business risks being disappointed by an output that misses the actual need.

#### AI-specific responsibilities

The traditional PM curriculum doesn't fully cover what an AI PM must own.

**1. Active management of the data lifecycle.** In traditional software, the product logic is *explicit*: the engineering team writes the rules. In AI, the product logic *emerges from data*. This makes data not just an input but the **primary asset**. The AI PM owns the right questions:

- Is the data **available**? Where does it live, who owns it?
- Is the data **of sufficient quality**? Clean, representative, unbiased?
- How is the data **acquired** and **labelled**?
- What is the **strategy** for improving data over time?

Because **GIGO** ("garbage in, garbage out") is the leading cause of AI project failure, the PM must be obsessed with data quality - more so than with any single model architecture choice.

**2. Collaboration with an experimental team.** The PM works with Data Scientists (who do research-style exploration) and ML Engineers (who industrialise the result). Two consequences:

- **Managing uncertainty.** Pure experimentation can drift forever without producing business value. The PM has to balance the team's need to explore with the business's need to ship.
- **Production focus.** A working prototype in a Jupyter notebook is not a product. The PM must understand the transition from prototype to production-grade serving, monitoring, and retraining - and plan for it.

#### What the PM is NOT

The PM is **not the technical decision-maker**. They don't pick the model architecture, the database, the framework. That's the Solution Architect.

### AI Solution Architect (SA)

The SA owns the *how*. Where the PM ensures the project is solving the right problem, the SA ensures the solution can actually be built, scaled, and operated.

#### Core responsibilities

- **Technical architecture.** The end-to-end design of the system: data pipelines, model serving infrastructure, integration with existing systems, security, observability.
- **Technology choices.** Selection of frameworks, libraries, platforms (databases, microservices vs monolith, on-prem vs cloud, which cloud, which ML platform).
- **Model integration.** How the ML model fits into the broader application: serving layer, API contracts, fallback behaviour.
- **Longevity.** The system must work now *and* be able to grow and adapt over time. Architecture decisions made on day one constrain what's possible on day 1000.

#### The SA's role in feasibility

The SA is the reality check on the PM's vision. When the PM proposes a new initiative, the SA evaluates:

- Is the necessary data available and accessible?
- Is the model architecture realistic given the constraints (latency, compute budget, data volume)?
- Are the required skills and infrastructure in place?
- What are the integration points with existing systems?

The collaboration between PM and SA in the early feasibility phase is what prevents the team from investing months in an idea that can't actually be built.

#### The SA as universal translator

This is the SA's most underrated function and the one that solves the "two languages" problem (more below). The SA decomposes high-level business goals into specific, measurable technical metrics.

Example chain:

```
Business goal:    "Reduce customer churn"
                            │
                            ▼
AI metric:        "Identify ≥85% of customers likely to churn
                   in the next 30 days, with intervention budget X"
                            │
                            ▼
Technical metric: "Recall > 85% on the 'likely churn' class,
                   precision > 60% to keep intervention costs reasonable"
```

The SA owns this translation. Without it, the engineering team optimises a metric in isolation that may have no business impact.

### The PM-SA partnership

The relationship between PM and SA is the **spine** of every successful AI project. Each balances the other:

- **PM brings ambition.** Vision, market understanding, strategic intent.
- **SA brings reality.** Technical feasibility, architectural constraints, operational implications.

A useful analogy: **PM ensures you're climbing the right mountain; SA ensures you have the right gear for the climb.** Both are required. A talented PM with no technical partner picks unfeasible projects; a talented SA with no product partner builds technically beautiful things nobody needs.

#### The shared language requirement

For the partnership to work, both must understand each other's domain at a working level.

**What the AI PM must understand technically:**

- **Model drift** and the implication for ongoing operations.
- **Inference latency** and how it constrains UX.
- **Accuracy ceilings** - that AI is probabilistic and 100% is never achievable.
- The data lifecycle in enough depth to have intelligent conversations about quality.

**What the AI SA must understand on the business side:**

- The actual business KPIs and what moves them.
- Why a given feature is strategically critical (e.g., why conversion rate, not just engagement).
- The cost of being wrong, both per-incident and at scale.
- Stakeholder dynamics and the political reality of the organisation.

When either side opts out of learning the other's domain, the partnership breaks down and the project's failure rate spikes.

---

## The broader orchestra

The PM and SA are central but not sufficient. Successful AI projects require a wider team, each role specialised, all aligned.

### Data Scientists - the explorers

The Data Scientist's mandate is exploration. They dive into the data, find hidden patterns, test hypotheses, build prototypes.

- **Guiding question:** "Can we solve this problem with the data we have?"
- **Output:** Prototype models, proofs of value, exploratory analyses that turn uncertainty into feasibility.
- **Mindset:** Research-oriented, scientific. Iteration, failure, and learning are part of the job.

The Data Scientist is the one who answers "is this even possible with current data?" before millions are spent trying to build it.

### ML Engineers - the builders

The Data Scientist's notebook is not a product. The ML Engineer's job is to **industrialise** it: transform the prototype into robust, scalable, maintainable production software.

- **Core focus:** Deployment and integration. Handling thousands of requests per second, integrating with enterprise APIs, ensuring reliability under load.
- **Output:** Production-grade serving infrastructure, the "highway" that delivers the model's intelligence to end users.

The ML Engineer is the bridge from "we proved it works in the lab" to "it serves real traffic at SLA".

### DevOps and MLOps - the guardians

The system doesn't stop existing the moment it ships. **MLOps** is the discipline of operating ML systems continuously, and the team that owns it is the guardian of the deployed model.

- **Continuous Deployment (CD):** Push new model versions safely.
- **Continuous Monitoring:** Track performance, data drift, business KPIs in real time.
- **Continuous Training:** Detect drift, trigger retraining, version models, enable rollback.

Without MLOps, the team that deployed the model is also the team that has to handle every alert at 3am with no tooling. With MLOps, the system survives.

See [02_kpis_lifecycle_drift.md](02_kpis_lifecycle_drift.md) and [07_deployment.md](../../03_agentic_ai/notes/07_deployment.md) for the operational details.

### Business Stakeholders - the commissioners

The business stakeholders are the **commissioners** of the AI initiative and the **final judges** of its success.

- **What they provide:**
  - The business goals - the *why*.
  - Domain expertise - knowledge of customers, market, regulatory context.
  - The success criteria the project will be measured against.

- **What is NOT expected of them:**
  - Understanding the algorithm itself. They don't need to know whether the model is XGBoost or a transformer. They need to know whether it moves the KPI.
  - Defining technical metrics. That's the SA's domain via the translation chain.

Strong business stakeholder engagement is correlated with project success more than almost any technical factor. Detached stakeholders produce projects that ship but go unused.

---

## The "two languages" curse and how to break it

> Without a translator, the orchestra produces noise. Two professional musicians playing in different keys is worse than one amateur in tune.

This is the most consistent failure mode in AI project organisations: the technical team and the business team are both competent in their domains but **cannot communicate effectively across the boundary**.

### The disconnect, restated

- Technical team measures **accuracy, precision, recall, F1, latency, throughput**.
- Business team measures **revenue, conversion, retention, cost reduction**.

When the technical team picks an optimisation target without business input, the result is often the fraud-detector trap from [02_kpis_lifecycle_drift.md](02_kpis_lifecycle_drift.md): 99.9% accuracy that catches zero fraud because the model always predicts "not fraud" on imbalanced data. Technical success, business failure.

### The fraud-detector example, again

This case keeps coming back because it's the cleanest illustration:

| Metric optimised | Result |
|---|---|
| **Accuracy** | 99.9%, but model predicts "not fraud" almost always; fraud losses unchanged |
| **Recall** | 80%, lower accuracy; catches actual fraud; **prevents real financial losses** |

The choice between optimising accuracy or recall is a **business decision** about how to trade false positives against false negatives. It must be made collaboratively, upfront, before any modelling.

### The solution: SA as translator, plus shared metrics framework

Two structural fixes break the two-languages curse.

**1. The Solution Architect acts as the translation layer.** The SA's explicit job is to take high-level business intent and decompose it into measurable technical targets. They speak both languages well enough to bridge them.

**2. A shared metrics framework anchored on the translation chain.** Every AI project documents the full chain explicitly:

```
Business goal → Strategy → Business KPI → AI metric → Technical metric
```

This becomes the **shared sheet music** the whole orchestra plays from. Everyone - PM, SA, Data Scientist, ML Engineer, MLOps, Business Stakeholder - is aligned on the same chain. Disagreements happen in the open and get resolved at the right level, not in production.

### From friction to alignment

The signs of a healthy organisation around AI projects:

- Business KPIs are visible to and understood by the technical team.
- Technical constraints (drift, latency, accuracy limits) are visible to and understood by the business.
- Disagreements happen at project kickoff, in conference rooms, not after deployment.
- The chosen technical metrics are obviously, traceably tied to a business outcome.

When all four are true, the orchestra plays together and AI ambition translates into business impact.

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| PM that doesn't understand technical limits | Promises "the model will be 100% accurate"; team scrambles to deliver impossible | PM training in AI fundamentals: drift, probabilistic outputs, accuracy ceilings |
| SA that doesn't understand business priorities | Architecturally elegant system that doesn't move any KPI | SA training in business strategy and the specific organisation's KPIs |
| No translation chain documented | Technical team optimises accuracy on imbalanced data; business confused | Mandatory business goal → KPI → AI metric → tech metric chain at project start |
| Data Scientist tasked with industrialisation | Prototype hard to deploy; performance degrades at scale | Separate exploration (DS) from industrialisation (MLE); explicit handoff |
| ML Engineer asked to do exploration | Engineer applies "ship it" mindset to a research-shaped problem | Different mindset; either hire a DS or set explicit experimentation timeboxes |
| No dedicated MLOps capability | Model rots in production; nobody owns the operational loop | MLOps team formed before launch, not after the first incident |
| Business stakeholders disengaged | Project ships, success criteria shift, KPI not moved, project judged a failure | Force stakeholder engagement via the metrics chain; their sign-off on KPI is mandatory |
| Cross-functional silos | Each role optimises locally; integration only at the end | Daily / weekly cross-functional standups from project start, not just at milestones |
| SA picks tech without PM input | Stack chosen for engineering preference, not business need | SA proposes, PM challenges based on business priorities; decision documented |
| "We can't take it down" | No rollback plan when the model misbehaves | Rollback procedure owned by MLOps; tested before launch |

---

## When to use what

| Need | Role | Why |
|---|---|---|
| Define the business problem | PM with stakeholders | Owns the *why* and the prioritisation |
| Validate technical feasibility | SA with DS | Avoids investment in unfeasible ideas |
| Choose the technical metric | SA via translation chain | Anchors engineering work to business outcome |
| Explore the data | DS | Research-mode, can answer "is this possible?" |
| Build production serving | MLE | Industrialises the prototype |
| Monitor + retrain in production | MLOps | Continuous operation, drift response |
| Sign off on success criteria | Business stakeholder | Provides domain expertise and final judgement |
| Mediate technical-business conflicts | PM + SA together | One owns *why*, the other *how*; both needed |
| Architect for longevity | SA | Day-one choices shape what's possible in year three |
| Plan stakeholder communication | PM | Hub role; manages expectations on both sides |

---

## See also

### Other notes
- [01_identifying_ai_problems_and_feasibility.md](01_identifying_ai_problems_and_feasibility.md) — the early-phase work where PM and SA collaborate most intensely
- [02_kpis_lifecycle_drift.md](02_kpis_lifecycle_drift.md) — the translation chain that the SA owns, plus the lifecycle the MLOps team operates
- [03_case_studies.md](03_case_studies.md) — Family 5 failures (silos, weak governance) are role-and-stakeholder failures
- [05_roadmap_and_prioritization.md](05_roadmap_and_prioritization.md) — the prioritisation tools the PM uses to choose what to build next
- [06_product_lifecycle_poc_to_scale.md](06_product_lifecycle_poc_to_scale.md) — where the DS → MLE handoff happens
- [07_project_management_methodologies.md](07_project_management_methodologies.md) — how Scrum/Kanban map onto these roles
- Module 03 [07_deployment.md](../../03_agentic_ai/notes/07_deployment.md) — the MLOps operational layer for agentic systems
- Module 02 [08_ethics_and_governance.md](../../02_large_language_models/notes/08_ethics_and_governance.md) — governance roles that complement PM/SA in regulated contexts
