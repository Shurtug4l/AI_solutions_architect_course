# Identifying AI Problems and Assessing Feasibility

## TL;DR

The first decision in any AI initiative is not "which model?" but "is this even an AI problem worth solving?". The course's "Golden Rule" is sharp: **business strategy precedes technology choice**, never the reverse. The opposite anti-pattern is **solutionism** - falling in love with the AI hammer and looking for nails everywhere. To stop the soulutionism trap there is a three-criterion **fitness test** every candidate problem must pass before resources are committed: **data** (do you have the right, clean, representative data?), **repeatability and scale** (does the task happen often enough that automation pays?), **error tolerance** (is the probabilistic nature of an AI output acceptable?). Problems that pass split into five families - **forecasting, classification, anomaly detection, optimisation, generation** - each pointing at a different AI approach. Once a problem qualifies, the second filter is the **Value / Feasibility matrix**: a 2x2 that places candidate initiatives by business value and technical complexity, producing four quadrants (Quick Wins, Strategic Initiatives, Fill-ins, Time Sinks) and clear priorities. Building the business case requires explicit **KPIs, scope (PoC vs PoV)**, and an honest **total-cost-of-ownership** that includes the hidden costs nobody budgets for at the start: data acquisition and cleaning, infrastructure and API spend, MLOps tooling, and the perpetual operational budget for monitoring and retraining a model that **drifts**.

## Cheatsheet

| Concept | One-line | Where it shows up |
|---|---|---|
| **Golden Rule** | Business strategy precedes technology choice | Every project kickoff |
| **Solutionism** | Falling in love with the tech before defining the problem | The #1 anti-pattern |
| **Fitness test** | Data + Repeatability + Error tolerance | Before any resource allocation |
| **Problem types** | Forecasting, Classification, Anomaly, Optimisation, Generation | Drives the AI approach |
| **Value / Feasibility matrix** | 2x2 prioritisation tool | Portfolio selection |
| **Quick Win** | High value + High feasibility | Maximum priority |
| **Strategic Initiative** | High value + Low feasibility | Long-term roadmap |
| **Fill-in** | Low value + High feasibility | Only if spare capacity |
| **Time Sink** | Low value + Low feasibility | Avoid |
| **PoC vs PoV** | Proof of Concept vs Proof of Value | Always aim for the second |
| **Total Cost of Ownership (TCO)** | Build + Run + Monitor + Retrain | The hidden 70% of the budget |
| **Model drift** | Accuracy degrades over time as the world changes | Permanent operational cost |

---

## The principle: business first, technology second

> **The Golden Rule:** business strategy always precedes the choice of technology.

The most common AI-project failure mode is the inverse: a team enthusiastic about AI starts with the solution ("we want to use LLMs / computer vision / RAG") and then hunts for a problem to apply it to. The Italian shorthand for this is **soluzionismo** - solutionism. It produces projects with no clear business value, low user adoption, and that get stuck forever in the "pilot purgatory" without ever reaching production.

The corrective: every AI project starts by stating the business problem, the user it affects, the magnitude of the impact, and *only then* considers whether AI is the right tool to address it.

---

## The fitness test: three filters

> **Premise**: not every business problem is an AI problem.

Before any resources are allocated, the candidate problem must pass three filters. Each filter is a strategic check, not a technical one. Failing any one of them usually means the project is doomed regardless of how good the model is.

### Filter 1: Data (the non-negotiable prerequisite)

AI systems are fundamentally **data-driven**. The feasibility hinges on a small set of brutal questions:

- Is the required data actually **available** and **accessible** (not locked in a silo or behind a procurement contract)?
- Is it **relevant** to the problem - the right features for the right outcome?
- Is it **clean** enough? Has it been **labelled** where supervised learning needs it?
- Is it **representative** of the operational distribution the model will face?

The principle is **garbage-in-garbage-out**. If the data is sparse, biased, or low-quality, the model's failure is almost guaranteed. Investments in model architecture cannot rescue bad data.

### Filter 2: Repeatability and scale

AI unlocks its value through the **scaled automation of repetitive tasks**. The right target is a process that happens **hundreds or thousands of times per day** with recognisable patterns: operations, customer service routing, anomaly screening.

The wrong target is a task executed **rarely** (once a year, monthly board reports, one-off strategic decisions). The investment in building, deploying, and maintaining an AI system cannot pay back when the volume is low. A human doing it manually each time is cheaper.

A useful proxy: count the number of times the task will run in a year multiplied by the time it currently takes. If the product is meaningful (hundreds of hours), AI scale is plausible. If it is not, it is not.

### Filter 3: Error tolerance (the probabilistic nature)

AI models are **probabilistic**, not deterministic. They will be wrong some fraction of the time. The business context must accept that.

| Tolerance | Examples |
|---|---|
| **High** | Recommendations, content suggestions, marketing copy generation - a wrong call has small per-instance cost |
| **Medium** | Customer-service triage, document classification, demand forecasting - wrong calls are recoverable |
| **Low** | Medical diagnosis, legal decisions, irreversible financial actions - the cost of one wrong call is catastrophic |

Low-tolerance use cases are not impossible, but they require an entirely different design: human-in-the-loop validation, conservative thresholds, audit trails. The system is no longer the AI alone but the AI plus the human plus the institutional safeguards.

---

## Five families of AI problems

When a candidate problem clears the fitness test, classifying it points at the right AI approach. The course identifies five families.

| Type | Question | Examples |
|---|---|---|
| **Forecasting** | "What is likely to happen next?" | Customer churn, demand prediction, equipment failure |
| **Classification** | "What kind of thing is this?" | Email spam, ticket routing, sentiment analysis |
| **Anomaly detection** | "Is this event unusual?" | Credit card fraud, network security monitoring |
| **Optimisation** | "What is the best way to do this?" | Logistics routing, ad budget allocation |
| **Generation** | "Can you create something new for me?" | Marketing copy, image generation, synthetic data |

### A note on generative AI

Generation is the most fashionable family today, and **the one most prone to solutionism**. "Let's add a GenAI feature" is the rallying cry. The fitness criteria still apply with full force:

- Data: even generative tasks need representative training data and grounding sources.
- Repeatability: a chatbot that fields the same thousand questions is a strong fit; a one-off marketing campaign is not.
- Error tolerance: GenAI hallucinates. Use it only where occasional wrong outputs are acceptable, or pair it with grounding mechanisms (RAG, see module 02 notes 04-07).

---

## Prioritising: the Value / Feasibility matrix

Once a set of candidate problems passes the fitness test, ranking them needs an explicit framework. The course's tool is a **2x2 matrix**.

```
         High value
              ▲
              │
   Strategic  │  Quick Wins
   Initiative │   (highest
              │    priority)
              │
              ┼─────────────────► High feasibility
              │
   Time Sinks │   Fill-ins
   (AVOID)    │  (low priority)
              │
              ▼
         Low value
```

### The value axis: quantifying business impact

Forces an explicit answer to a hard question: **how does this project affect the main business KPIs?**

- Revenue increase?
- Cost reduction?
- Risk mitigation?

The magnitude matters. A €10,000 problem is fundamentally different from a €1,000,000 one, and the investment level should reflect this. An approximate order-of-magnitude estimate is enough - precision is impossible at this stage, but a rough figure is essential to justify investment.

### The feasibility axis: technical complexity

An honest technical assessment along three vectors:

- **Data**: is the necessary data available, clean, and of acceptable quality? (Back to filter 1.)
- **Algorithmic complexity**: is the model architecture simple (logistic regression, gradient boosted trees) or complex (deep learning, large generative models)?
- **Resources and infrastructure**: do we have the skills, the hardware (GPUs), and the MLOps infrastructure?

### The four quadrants

| Quadrant | Definition | Action |
|---|---|---|
| **Quick Wins** | High value + High feasibility | Max priority. Rapid ROI. Build momentum. |
| **Strategic Initiatives** | High value + Low feasibility | Long-term roadmap. Real investment justified. |
| **Fill-ins** | Low value + High feasibility | Low priority. Pick up only with spare capacity. |
| **Time Sinks** | Low value + Low feasibility | **Avoid.** Drains resources, returns nothing. |

### The matrix as an alignment tool

The matrix is not just a chart - it is a **conversation forcing function** between business and technology:

- Business owners are forced to **quantify value** (the "why").
- Tech owners are forced to **articulate complexity** (the "how", including showstoppers like "we don't have the data", "the legacy system has no API").

Disagreements surface early instead of in production. The exercise reveals dependencies, blockers, and misalignments that would otherwise show up six months in.

---

## Building the business case

A convincing AI business case has four explicit elements.

### 1. Problem definition and strategic alignment

Stated in business terms, not technical. The problem should map clearly onto a strategic priority of the organisation. "We want to use LLMs" is not a problem statement; "Our customer-service agents spend 40% of their time on repetitive routing decisions that could be automated" is.

### 2. Target audience and use cases

Who is the end user? What specific scenario does the project address? Generic personas ("our customers") are useless; specific scenarios ("a tier-2 support agent triaging incoming tickets") drive design decisions.

### 3. Measurable KPIs (not vague ones)

Bad: "improve customer satisfaction." Good: "reduce average ticket resolution time from 24h to 8h." See [02_kpis_lifecycle_drift.md](02_kpis_lifecycle_drift.md) for the full treatment.

### 4. Scope: PoC vs PoV

A **Proof of Concept** demonstrates that the technology *can* be built. A **Proof of Value** demonstrates that the technology *creates measurable business value*. Always aim for PoV: a PoC that nobody adopts is a sunk cost; a PoV with quantified impact is the foundation for scaling.

---

## ROI and the hidden costs

The temptation in the business case is to **overstate the benefit** and **understate the investment**. The latter is the more frequent error, because the visible costs (model development, initial deployment) are only a fraction of the total.

### The full formula

```
ROI = (Net Benefit) / (Total Investment)
```

The trap is in the denominator. "Total Investment" is not the cost of the PoC.

### Hidden costs - data

Most projects budget for the initial data ingestion. They forget the **recurring costs**:

- Acquisition (paid feeds, scraping infrastructure).
- Cleaning (data engineers, validation pipelines).
- Labelling (annotators, quality control - massive on a continuous basis).
- Storage (object storage, data warehouses scale linearly with volume).

### Hidden costs - infrastructure

- **Compute**: GPUs or token-based APIs. The cost is small per call and explodes unpredictably as usage grows. A successful feature can produce a runaway bill.
- **Latency and reliability**: serving production traffic at low latency needs more capacity than serving a demo.
- **Network**: data egress, cross-region traffic.

### Hidden costs - tooling

- **MLOps platforms**: pipelines, registry, deployment.
- **Monitoring and observability**: model performance, data drift, prediction logs.
- **Security**: PII handling, access control, audit trails (see module 02 note 08 ethics).

### The most critical hidden cost: continuous maintenance

A pre-trained AI model is not "build and forget". Models **degrade over time** (model drift) as the data distribution shifts. The world changes; the model does not, until it is retrained.

This means a **perpetual operational budget**:

- Continuous monitoring of model performance and data drift.
- Periodic retraining (every quarter, every month, sometimes continuously).
- A team of in-house experts to run the operation. Outsourcing this is fragile.

Module 04 note 02 covers drift and the lifecycle that supports it in depth.

### What to do about it

Build the business case with TCO over a **3-year horizon**, not just the build cost. Break down:

- Year 1: build + initial deployment (the visible costs).
- Year 2-3: operation + retraining + maintenance (the hidden ones).

The total is often 3-5x the visible Year 1 number. If the project still has a positive ROI under that assumption, it is a real candidate. If not, the team has been hiding from the truth.

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Starting with the technology | "We want to use AI" without a problem | Define the business problem first, ignore the tech for a week |
| Treating fitness criteria as suggestions | Build proceeds despite missing data / low scale / low tolerance | Each criterion is a hard gate, not a checkbox |
| Generative AI applied indiscriminately | High cost, unclear ROI, hallucinations in serious contexts | Apply the same fitness test as any other AI family |
| 2x2 matrix filled in by tech alone | Business owners disengage; the matrix loses its alignment function | Both sides own the matrix; disagreement is the signal |
| Quick Wins delayed to chase Strategic Initiatives | Momentum lost, executive sponsorship erodes | Ship Quick Wins first, fund Strategic Initiatives with their visible success |
| Time Sinks pursued anyway | "But it's so cool technically" | Veto from product / business |
| PoC declared successful, never scaled | Pilot purgatory | Aim for PoV from the start, with a quantified business metric |
| TCO uses only Year 1 visible costs | Project becomes loss-making in Year 2 | 3-year TCO with explicit maintenance, retraining, monitoring budget |
| Model treated as static after deployment | Performance silently degrades for months | Drift monitoring + retraining cadence written into the SLA |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Filter candidate AI ideas | Fitness test (data + repeatability + tolerance) | Cheap, fast, kills bad ideas early |
| Rank validated ideas | Value / Feasibility matrix | Forces the right conversation |
| Pick the first project | A Quick Win | Build credibility and capability |
| Long-term competitive bets | Strategic Initiatives | Higher risk, transformative when they work |
| Prove technical feasibility | PoC | Internal milestone, not a launch |
| Justify continued investment | PoV with measurable KPI | Real business signal |
| Cost the project | 3-year TCO | Year 1 alone hides 70% of the spend |
| Forecast continuous demand | "Will be X next month / quarter" | Forecasting family |
| Tag / categorise items | "What kind is this?" | Classification family |
| Detect outliers | "Is this normal?" | Anomaly detection family |
| Find the best plan / route / allocation | "What is the optimum?" | Optimisation family |
| Create new artefacts | "Generate this for me" | Generation family |

---

## See also

### Other notes
- [02_kpis_lifecycle_drift.md](02_kpis_lifecycle_drift.md) — KPIs as the translation layer, lifecycle phases, model drift in depth
- [03_case_studies.md](03_case_studies.md) — what wins and what fails when these principles are ignored
- [04_roles_and_stakeholders.md](04_roles_and_stakeholders.md) — who builds, who decides, who validates
- [05_roadmap_and_prioritization.md](05_roadmap_and_prioritization.md) — once the matrix has selected the candidates, prioritisation frameworks (MoSCoW, RICE, Kano)
- [06_product_lifecycle_poc_to_scale.md](06_product_lifecycle_poc_to_scale.md) — the journey from PoC to MVP to production scaling
- [07_project_management_methodologies.md](07_project_management_methodologies.md) — how to run the project after the business case is approved
- Module 02 [08_ethics_and_governance.md](../../02_large_language_models/notes/08_ethics_and_governance.md) — error-tolerance constraints become regulatory constraints in regulated domains
