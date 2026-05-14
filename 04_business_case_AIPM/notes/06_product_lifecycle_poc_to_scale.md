# Product Lifecycle: PoC → MVP → Scale

## TL;DR

An AI product is not launched, it is **evolved through three distinct phases**, each answering a different question with different metrics. **Phase 1 — Proof of Concept (PoC)** asks *"Can it be done?"*: validate a fundamental technical hypothesis with minimum effort. The output is a scientific experiment (usually a notebook) returning a clean yes/no on technical feasibility. **Phase 2 — Minimum Viable Product (MVP)** asks *"Should we do it?"*: validate the *value* hypothesis. The MVP is a **Minimum Viable Test**, not a "small product"; it is the cheapest possible experiment that puts the model in front of real users in a real workflow and measures whether they act on it. The trade-off triangle is **Desirability / Feasibility / Viability** - users want it, we can build it robustly, the economics work. **Phase 3 — Scaling** asks *"Can we do it 1000 times?"*: validate the operational and economic sustainability. The trap is that what works for 100 beta users collapses under 100,000 - latency explodes, GPU costs balloon, the architecture isn't designed for it. **Scaling is an architectural problem from day one, not a post-launch concern.** Beyond MVP, the work shifts to **Customer Development**: Acquisition, Retention, Growth, all driven by the **Build-Measure-Learn loop** as the continuous improvement engine. **Product-Market Fit (PMF)** is the goal of the MVP → Scale transition: the elusive state where the market starts *pulling* the product instead of being pushed to it. PMF is a state, not a KPI, and its indicators (sustained adoption beyond the novelty curve, retention, prediction satisfaction) are subtler than launch metrics. The **Go-To-Market (GTM)** strategy for AI is mostly about **education and trust**: don't sell the technology ("Transformer model"), sell the user benefit ("write emails in half the time"); proactively communicate the probabilistic nature instead of overpromising; be transparent about limits. The Netflix recommender is the canonical worked example - from a 2006 collaborative-filter PoC to today's multi-billion-dollar retention engine, each phase clearly delineated, each pivot grounded in measurement.

## Cheatsheet

| Phase | Key question | Output | Metrics |
|---|---|---|---|
| **PoC** | "Can it be done?" | Technical experiment, yes/no | Beats baseline? Is there a signal? |
| **MVP** | "Should we do it?" | Smallest test of value with real users | Does the user act on the output? Does the business KPI move? |
| **Scaling** | "Can we do it 1000 times?" | Production-grade service | Latency, throughput, cost-per-prediction, reliability |
| **PMF** | "Does the market pull the product?" | Sustained adoption + retention + satisfaction | Indicators, not a single KPI |
| **Trade-off triangle** | Desirability + Feasibility + Viability | Used in MVP design | Want it + can build it + economics work |
| **Build-Measure-Learn** | Continuous improvement engine | Each iteration | Learning, not just shipping |
| **Customer Development** | Post-MVP focus | Acquisition + Retention + Growth | Different metrics per stage |
| **GTM for AI** | Engineer adoption, build trust | Education + expectation management + transparency | Adoption rate, trust signals |
| **Black-box risk** | Users don't understand → don't adopt | Mitigated by explainability + onboarding | First "wow moment" speed |

---

## Part 1: The three phases

### Phase 1 — Proof of Concept (PoC): "Can it be done?"

The PoC validates a **fundamental technical hypothesis** with the absolute minimum of effort. It is a scientific experiment, not a product.

#### What it is

- **Format:** Often just a notebook. No polished UI, plenty of technical shortcuts.
- **Audience:** A tiny internal group - the team, "friends", maybe one or two domain experts.
- **Metric:** Reactions and signal detection, not adoption rates.
- **Question answered:** "Is there a learnable signal in our data?" or "Does our chosen approach beat a trivial baseline?"

#### Example

> "Can we predict customer churn with accuracy meaningfully better than chance, using the data we currently have?"

The PoC succeeds if it returns a confident "yes" or "no" cheaply and quickly. A successful PoC unlocks the MVP; a failed PoC kills the initiative before serious investment.

#### The PoC trap

Many AI initiatives die *because they were declared successful as a PoC and then immediately treated as a product*. The PoC's job is to answer one technical question - that's it. The notebook is not the product. The data scientist's laptop is not the production environment. Skipping the MVP and jumping to scaling produces the "pilot purgatory" pattern from [03_case_studies.md](03_case_studies.md) Family 3.

### Phase 2 — MVP: "Should we do it?"

The MVP validates the **value hypothesis**. The PoC said the model *can* predict; the MVP asks whether the prediction *matters*.

#### The key reframe

The MVP is **not a small product**. It is a **Minimum Viable Test** - the fastest, cheapest experiment that puts the model in front of real users in a real workflow and measures whether the value chain actually closes.

Example: the PoC proved we can predict churn. The MVP asks: *"If we surface churn predictions to customer-service agents, will they act on them and successfully retain customers?"* This is a fundamentally different question - it's about humans and processes, not just models.

#### The trade-off triangle

MVP design balances three forces:

```
                    Desirability
                  (do users want it?)
                          ▲
                         ╱ ╲
                        ╱   ╲
                       ╱ MVP ╲
                      ╱       ╲
                     ╱         ╲
       Feasibility  ──────────  Viability
       (can we build       (is it economically
       it robustly?)        sustainable?)
```

| Vertex | Question |
|---|---|
| **Desirability** | Do users actually want this? Will they use it? |
| **Feasibility** | Can we build it well enough to be tested honestly? |
| **Viability** | Does the unit economics work? Is the value > cost? |

All three must hold for an MVP to be a meaningful test. A feasible but undesirable MVP teaches nothing about value. A desirable but unviable MVP teaches us we're building something we can't afford.

#### Primary goal: feed the feedback loop

The MVP's primary purpose is **not launch** - it's **learning**. The Build → Measure → Learn → Iterate loop is what justifies the existence of an MVP. Every MVP cycle ends with a decision: continue (validated), pivot (partially validated), or stop (invalidated).

### Phase 3 — Scaling: "Can we do it 1000 times?"

Scaling is the transition from a working test to a continuously operating service at production volume.

#### The scaling trap

A system that works for 100 beta users may collapse at 1,000, let alone 100,000:

- Inference latency explodes when a single GPU can't keep up.
- API costs grow non-linearly with traffic.
- Memory pressure causes random crashes.
- The MVP-grade architecture (a notebook served behind a Flask app on one VM) is not a production system.

#### The architectural principle

> **Scaling is not a post-launch problem. It is an architectural decision from day one.**

This does not mean over-engineering the MVP. It means the architect (see [04_roles_and_stakeholders.md](04_roles_and_stakeholders.md)) has a clear scaling plan from the start, and the MVP is built in a way that doesn't paint the team into a corner.

#### The hidden costs of AI at scale

Costs grow **exponentially**, not linearly.

| Cost category | At MVP | At scale |
|---|---|---|
| Compute | CPU sufficient | GPUs required for high-volume inference |
| API spend | Negligible per call | Token-per-call cost dominates the bill |
| Storage | Single bucket | Multi-region, tiered, with lifecycle policies |
| Infrastructure | One VM | Load-balanced clusters, autoscaling, observability |
| Operational complexity | One person handles it | Dedicated MLOps team |

The 30-40% / 60-70% split between build cost and 3-year operational cost from [01_identifying_ai_problems_and_feasibility.md](01_identifying_ai_problems_and_feasibility.md) lives almost entirely on the scaling side.

#### The economic decision point

Every scaling effort hits a decision: **is the cost increment justified by the ROI?** The Netflix case (more below) shows this explicitly - they answered yes because the system saved >$1B/year in retained subscriptions. A different system facing the same scaling cost with no equivalent ROI is making a strategic mistake.

### Post-MVP: Customer Development

Launching the MVP is the **starting line**, not the finish line. Post-MVP work is **Customer Development** - validating that the product grows and sustains value.

Three growth stages, each with its own metrics:

| Stage | Question | Metric examples |
|---|---|---|
| **Acquisition** | How do we get new users to try the AI feature? | Trial rate, first-use completion |
| **Retention** | Do users come back (i.e., is it more than a novelty)? | Day-7, Day-30, Day-90 return rates |
| **Growth** | Does usage drive incremental business value? | Revenue per active user, repeat purchase, NPS |

Different stages need different optimisations. A team that knows how to drive Acquisition but not Retention has a leaky bucket.

### The Build-Measure-Learn engine

The same engine introduced in [05_roadmap_and_prioritization.md](05_roadmap_and_prioritization.md) powers post-MVP growth:

```
       ┌───────────┐
       │  BUILD    │  Small improvement based on signal
       │           │  (e.g., add an explanation to a prediction)
       └─────┬─────┘
             ▼
       ┌───────────┐
       │  MEASURE  │  Did adoption increase?
       │           │  Did the business KPI move?
       └─────┬─────┘
             ▼
       ┌───────────┐
       │   LEARN   │  What does the data say?
       │           │  What's the next experiment?
       └─────┬─────┘
             │
             └────────► next iteration
```

The cadence matters: monthly iterations are agile, weekly is aggressive, daily is rare and expensive. Pick the cadence the team and infrastructure can sustain.

---

## Part 2: Product-Market Fit for AI

### What PMF means

> **Product-Market Fit is a state, not a KPI.** The market stops being pushed by sales effort and starts pulling the product.

Achievement criteria:

- Users adopt the product actively.
- They integrate it into their workflow.
- They would complain - loudly - if it stopped working.

The negative case: a technically valid AI project that nobody adopts. This is the *single most common* failure mode of post-MVP AI initiatives - the model is good, the integration works, but the market doesn't pull. PMF is missing.

### Three indicators

#### Indicator 1: Adoption rate (sustained, not peak)

The **novelty trap**: a new AI feature can show a beautiful adoption spike that has nothing to do with PMF. People try anything labelled "AI" once.

The signal that matters: **sustained adoption over time**, especially within the target audience. Is the user understanding the value fast enough to complete the first use? Are they coming back next week?

#### Indicator 2: Retention (the real question)

Adoption measures the first date. Retention measures the relationship.

A user who returns is implicitly saying: *"This tool gives me more value than it costs me, in time or in trust."* That is the PMF signal in its purest form. The Netflix case is the canonical example: long-term retention, not single-session engagement, is the goal.

#### Indicator 3: Prediction satisfaction

Critical distinction: **user satisfaction with predictions is different from technical accuracy**.

A 90% accurate model can produce frustrating user experiences if the 10% errors are concentrated, weird, or come at high-stakes moments. A 75% accurate model with gracefully degraded errors can feel like magic.

Measuring perception, not just accuracy, is essential. Tools: in-product feedback widgets, satisfaction surveys, qualitative interviews.

---

## Part 3: Go-To-Market for AI

### GTM as engineering of adoption

GTM for AI is not just marketing and sales. It is the **engineering of adoption** itself, with **trust as the central asset** to build.

The black-box problem: if users don't understand what the AI does, how it does it, and why it should matter to them, **adoption fails regardless of model quality**. GTM is the process of bridging that understanding gap.

### Tactic 1: User education

> Don't sell the technology, sell the benefit.

| Don't say | Do say |
|---|---|
| "Powered by Transformer models" | "Write emails in half the time" |
| "RAG over your enterprise knowledge base" | "Get accurate answers about your company instantly" |
| "85% Recall on the churn class" | "We identify customers at risk before they leave" |

**Onboarding is critical.** Show, don't tell. Guide the user to the first **"wow moment"** as fast as possible. Time-to-first-value is a launch KPI.

### Tactic 2: Manage accuracy expectations

> Don't promise magic. Don't promise infallibility.

The worst possible promise: "the AI will always be right". The first error destroys trust permanently.

**Honest communication wins.** Proactively explain that the system is probabilistic.

| Bad | Good |
|---|---|
| "This tool finds all opportunities" | "This tool helps you identify the majority of opportunities" |
| "The model is always accurate" | "The model is right most of the time; we'll show you the cases where it's most confident" |
| "AI knows the answer" | "AI surfaces likely answers; verify the important ones" |

This **prevents the disappointment cycle** that destroys reputation and trust.

### Tactic 3: Transparency about limits

State what the system **cannot do**, clearly and visibly:

- Domains it wasn't trained on.
- Edge cases where it underperforms.
- Confidence indicators on outputs.
- Disclaimers in high-stakes contexts.

The Air Canada chatbot case in [03_case_studies.md](03_case_studies.md) is what happens when this tactic is skipped: the system confidently produces a hallucination, the user trusts it, the organisation pays. Honest limits are not a sales weakness; they are a trust asset and a legal defence.

---

## Part 4: Worked example — the Netflix recommender

The Netflix recommendation engine is the textbook journey through all three phases. Each phase clearly delineated, each pivot grounded in measurement, the whole journey worth >$1B/year in retained subscriptions.

### The business problem

Streaming is a saturated market with low switching costs. Acquiring new customers is expensive; retaining existing ones is the strategic priority. AI is not an accessory - it is *the engineering solution* to the central business problem of retention.

### Phase 1 — The PoC (mid-2000s)

**Question:** Can we predict a user's tastes using the rating data ("stars") we have?

**Hypothesis:** A collaborative-filtering algorithm can beat a simple popularity ranking.

**Trade-off:** Sacrifice everything else (cost, speed, UI polish) to validate one thing: **is there a predictive signal in the rating data?**

The famous "Netflix Prize" (2006) was effectively a public PoC: $1M for a 10% improvement on their baseline. The PoC confirmed a strong signal existed.

### Phase 2 — The MVP

**Pivot in question:** From "Can we do it?" to "If we do it, will anybody care?"

**The business hypothesis being tested:** the "Picked for you" row will generate higher CTR than the generic "Popular" row.

**The decision point:** YES. Users clicked the personalised row more. The value hypothesis was validated. The team could proceed.

This is the textbook MVP - not a small product, but a sharp test of one value hypothesis with a clean measurable outcome.

### Phase 3 (early) — Feature expansion

From MVP to expansion: the basic personalisation worked, so the roadmap asked **what else can be personalised?**

- New algorithms alongside collaborative filtering: content-based filtering, hybrids.
- Beyond single titles: entire personalised categories ("Comedies for you").
- Immersive personalisation across the homepage.

### Critical decision point — beyond the click

The most consequential pivot: Netflix realised that **optimising for CTR was producing clickbait recommendations**. Users clicked but didn't enjoy what they watched. The metric was wrong.

The pivot: **optimise for long-term retention, not short-term clicks**. Switch the primary metric from CTR to viewing time, completion rates, and ultimately retention. This is the metric-alignment story from [02_kpis_lifecycle_drift.md](02_kpis_lifecycle_drift.md) playing out in production.

### Phase 3 (advanced) — Algorithm ecosystem

- From single model to ensemble: deep learning, RNNs, contextual bandits, multiple specialised models stacked.
- Personalised artwork: the AI selects the preview image based on user taste. Same film, different cover - dark-toned for thriller fans, comedic still for comedy fans.

### Phase 3 — Scaling and MLOps

The architectural challenge: serve recommendations to hundreds of millions of users in real time. The MVP-era architecture cannot support this.

The solution wasn't only better algorithms - it was **robust MLOps infrastructure** to test and deploy them at scale. Rigorous A/B testing of every new feature on small user slices before global rollout. Continuous monitoring and retraining.

### The economic decision

Real-time serving of deep-learning models at hundreds-of-millions scale has enormous compute costs.

**Decision point:** Is the additional cost justified by ROI?

**Answer (Netflix):** Yes. The system generates >$1B/year in retained subscription value. Massive investment, massively justified by the business metric.

### Lessons distilled

1. **Start with the business problem.** Not with the technology. Netflix started with retention.
2. **Validate in distinct phases.** PoC for technical feasibility; MVP for business value. Don't merge them.
3. **Evolve the metrics.** When the team realised CTR was wrong, they switched to viewing time and retention. The team that holds onto a wrong metric for reasons of inertia is doomed.
4. **Invest in scaling and MLOps.** Excellent models stay experiments without the infrastructure to run them at scale.

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Skipping PoC, going straight to MVP | Build expensive MVP that fails because the signal wasn't there | Cheap PoC first; spend MVP budget only after technical validation |
| Skipping MVP, going from PoC to production | The model works technically; nobody uses it; pilot purgatory | Mandatory MVP-as-test phase before scaling investment |
| MVP confused with "small product" | MVP becomes a polished mini-launch; learning loop missing | MVP = Minimum Viable Test; learning is the primary goal |
| Architecture designed only for MVP | System collapses at scale; emergency rebuild required | Scaling plan from day one, even if MVP itself is simple |
| Treating scaling cost as linear | Year-2 cost surprise; ROI collapses | Model AI cost growth as non-linear in TCO from the start |
| Adoption peak mistaken for PMF | Initial novelty curve celebrated; team relaxes; product dies in month 4 | Track sustained adoption, retention, satisfaction - not just peaks |
| Selling the technology in GTM | Users don't understand the benefit; adoption fails | Sell the user benefit; the technology stays invisible |
| Promising infallibility | First error destroys trust permanently | Honest communication of probabilistic nature from day one |
| Hiding system limits | Users hit edge cases unprepared; reputational damage | Transparent disclosure of what the system can't do, visible in-product |
| Optimising the wrong metric in production | CTR clickbait scenario; long-term value erodes | Periodically question whether the metric still aligns with the business goal (Netflix pivot) |
| No A/B testing infrastructure at scale | Every change is a coin flip; learning slows | Build A/B testing as part of scaling infrastructure, not after |
| Customer Development skipped post-MVP | Product ships, growth flatlines | Explicit ownership of Acquisition / Retention / Growth phases with distinct metrics |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Validate technical feasibility | PoC | Cheap yes/no on whether the signal exists |
| Validate value with real users | MVP | Smallest test that closes the value chain |
| Balance trade-offs in MVP design | Desirability / Feasibility / Viability triangle | All three must hold for meaningful test |
| Drive post-MVP improvement | Build-Measure-Learn loop | Continuous learning, not just shipping |
| Plan production-grade operation | Scaling phase with explicit architectural plan | Scaling is a day-one concern, not post-launch |
| Drive growth post-launch | Acquisition / Retention / Growth stages | Different problem at each stage, different metrics |
| Diagnose PMF | The three indicators (sustained adoption, retention, satisfaction) | PMF is a state, not a KPI |
| Build trust in launch | GTM tactics: education, expectation management, transparency | Adoption depends on understanding and trust |
| Convey value to users | Sell the benefit, not the technology | Users don't care about Transformers; they care about saving time |
| Calibrate user expectations | Probabilistic language ("most", "likely") | Prevents disappointment cascade and protects reputation |

---

## See also

### Other notes
- [01_identifying_ai_problems_and_feasibility.md](01_identifying_ai_problems_and_feasibility.md) — TCO model that anticipates the cost trajectory of scaling
- [02_kpis_lifecycle_drift.md](02_kpis_lifecycle_drift.md) — the metric-evolution discipline that powered the Netflix CTR→retention pivot
- [03_case_studies.md](03_case_studies.md) — the success and failure patterns whose mechanics are dissected here
- [04_roles_and_stakeholders.md](04_roles_and_stakeholders.md) — the PM and SA roles that own the phase transitions and the GTM strategy
- [05_roadmap_and_prioritization.md](05_roadmap_and_prioritization.md) — the hypothesis-and-experiment apparatus driving each phase
- [07_project_management_methodologies.md](07_project_management_methodologies.md) — Scrum-like cadence supports Build-Measure-Learn at MVP; Kanban supports Customer Development flow post-launch
- Module 02 [07_rag_production.md](../../02_large_language_models/notes/07_rag_production.md) — scaling and operating a generative system in production
- Module 03 [07_deployment.md](../../03_agentic_ai/notes/07_deployment.md) — the deployment + scaling layer for agentic systems
