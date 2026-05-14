# Case Studies: What Worked, What Didn't

## TL;DR

A pragmatic anchor for the theoretical material in notes 01 and 02: real-world projects, where the abstract principles either held up or didn't. **Successes (Netflix, Amazon)** share four traits: AI sits on top of a core, high-value business problem (retention, supply chain), not on a side project; data is treated as a strategic asset with massive granular collection; the operating model is continuous experimentation with rigorous A/B testing; and technical metrics are explicitly chained to business KPIs (not vanity metrics like click-through rate). **Failures (Air Canada chatbot, NYC government chatbot)** share a different pattern: they are **socio-technical**, not purely technical. The hallucination or wrong answer is the surface event; the real failure is the organisational decision to deploy a generative model without grounding, without a governance plan, without a rollback procedure, and then to deny responsibility post-incident. The Air Canada case is now legal precedent: courts hold the organisation fully responsible for what its AI says, regardless of whether the AI is described as a "separate entity". The taxonomy of failure modes is broader than chatbots: **strategic failure** (solutionism, wrong problem), **data failures** (garbage in, garbage out), **operational failures** (PoC works, production doesn't scale or explodes in cost, MLOps absent), and **organisational/governance failures** (silos, no cross-functional ownership, no ethical or legal oversight). The combined lesson: **AI failure is almost always a system failure** in the surrounding human and organisational scaffolding, not a model bug.

## Cheatsheet

| Case | Type | Core lesson |
|---|---|---|
| **Netflix** | Success | AI as core engineering solution to retention; ensemble of models; rigorous A/B testing |
| **Amazon supply chain** | Success | AI pervasive in forecasting, warehouse, logistics; data + automation = resilience |
| **Air Canada chatbot** | Failure | Ungrounded generative model + denial of responsibility = legal liability |
| **NYC government chatbot** | Failure | Authoritative source + wrong answers + no rollback = trust collapse |
| **Success pattern 1** | Strategy | AI applied to the most valuable business problem, not a side experiment |
| **Success pattern 2** | Data | Massive, granular, high-quality data as the fundamental asset |
| **Success pattern 3** | Process | Continuous iteration, A/B testing, MLOps culture |
| **Success pattern 4** | Metrics | Technical metrics → business KPIs directly and measurably |
| **Failure family 1** | Strategy | Solutionism, wrong problem, unrealistic expectations |
| **Failure family 2** | Data | Garbage in, garbage out; insufficient, biased, mislabelled |
| **Failure family 3** | Ops/Scale | PoC works, production doesn't (scale or cost) |
| **Failure family 4** | Ops/MLOps | No monitoring, no retraining, drift kills the model |
| **Failure family 5** | Org/Gov | Silos, no cross-functional ownership, no governance |
| **Universal lesson** | Socio-technical | The failure is the org + process around the tech, not just the tech |

---

## Successes

### Case 1: Netflix - retention as core engineering problem

#### The business problem

Streaming is a saturated, low-switching-cost market. Acquiring a new customer costs significantly more than retaining an existing one. So Netflix's strategic priority is dual:

1. **Maximise engagement** (time spent in the product).
2. **Minimise churn** (lost subscribers).

AI is not an accessory feature here. It *is* the engineering solution to the central business problem of retention.

#### The AI solution: a multi-layer ecosystem

Personalisation goes well beyond a "Recommended for you" row. Netflix personalises:

- The homepage layout for each user.
- The order in which categories appear.
- The thumbnail images shown for the same title (different users see different stills).
- Search ranking, "because you watched", trending tweaks per profile.

It is not one magical model. It is an **ensemble**: collaborative filtering, content-based filtering, deep learning models, contextual bandits, all combined.

#### Why it worked: four success patterns

1. **Granular data ecosystem.** The fuel is not just "what you watched" but *how* you watched: pauses, rewinds, search abandonments, what trailer you watched, what you skipped without clicking. The signal density is what makes the models possible.

2. **MLOps culture and rigorous A/B testing.** New algorithms are not deployed wholesale. They are tested on a slice of the user base. Impact on key metrics (engagement, retention) is measured before broad rollout.

3. **Metric alignment beyond the click.** Netflix deliberately avoids the **CTR trap**. Optimising for click-through rate would produce clickbait recommendations - tempting titles users don't actually enjoy, which hurt retention. Instead the system optimises a longer-horizon objective: long-term satisfaction and retention. This is a textbook application of the translation chain from [02_kpis_lifecycle_drift.md](02_kpis_lifecycle_drift.md).

4. **Documented business impact.** The recommendation system drives >80% of viewed content and the public claim is >$1B/year in retained subscriptions. The KPI tied to the AI is **value retained**, not "model accuracy".

#### Reading

This is what alignment looks like when it works. The metric the engineering team optimises is not chosen by them in isolation; it descends from the business strategy and is held accountable to a business KPI.

### Case 2: Amazon - AI pervasive in the supply chain

#### The business problem

A global supply chain of unprecedented scale and complexity, where the competitive moat is speed and reliability of delivery. Every hour shaved off the average delivery time is a strategic asset.

#### The AI solution: across the whole chain

AI is infused into every layer of the supply chain.

| Layer | What AI does |
|---|---|
| Demand forecasting | Predicts SKU-level demand using historical sales **plus** weather, macro indicators, social trends |
| Warehouse | Inventory levels, automated reorder, physical movement of goods via robot fleets (RPA) |
| Last-mile logistics | Dynamic route planning, adapted in real time to traffic and weather |

#### Why it worked

- **Predictive forecasting with external signals.** Not just sales history but exogenous variables (weather, economy, trends). The model "sees" the world, not just the catalogue.
- **Automation reduces operational error.** Combining prediction with robotic execution removes large classes of human error in inventory and dispatch.
- **Dynamic re-optimisation.** Delivery routes are not computed once - they adapt continuously.
- **Cost and speed impact.** Inventory costs dropped, delivery times shrank.
- **Resilience.** The pandemic stress-tested global supply chains. Amazon's AI-driven chain handled the shock better than competitors. AI here is a resilience asset, not just an efficiency one.

#### Reading

Amazon is the case for *pervasive* AI - not one model, but AI as a horizontal capability woven through the operating model. The lesson: when AI is core, it shows up everywhere, not as a single feature.

### Success patterns: the synthesis

Across both cases, four patterns recur.

| # | Pattern | Concrete sign |
|---|---|---|
| 1 | **Obsessive focus on the business problem** | AI tackles the *primary* strategic challenge (Netflix: retention; Amazon: supply-chain speed), not a side project |
| 2 | **Investment in data as a fundamental asset** | Massive, granular, high-quality data + the infrastructure to collect and process it at scale |
| 3 | **Iteration and continuous improvement** | Systems never "done"; constant monitoring, A/B testing, retraining against drift |
| 4 | **Tight metric-to-business alignment** | Technical metrics (CTR, recommendation quality) directly and measurably linked to business KPIs (retention, delivery speed) |

These patterns are not domain-specific. They generalise to any AI initiative trying to escape pilot purgatory and produce sustained business value.

---

## Failures

### Case 1: Air Canada hallucinated bereavement-fare chatbot

#### What happened

Air Canada's customer-service chatbot told a user that the airline's bereavement fare (a discounted post-mortem ticket) could be applied **retroactively**. The bot stated this confidently. The user trusted the answer, booked a full-fare flight intending to claim the discount later, and was denied the refund. The bot had hallucinated; the actual policy did not allow retroactive application.

#### The legal outcome

The customer sued for **negligent misrepresentation** and won. The court ordered Air Canada to pay damages.

The most consequential part of the ruling: Air Canada's defence had argued that the chatbot was a **"separate legal entity"** responsible for its own statements. The court rejected this argument unambiguously: the company is fully responsible for what its AI says to customers. This is now precedent.

#### The technical cause

The chatbot was a free-running generative model with no **grounding** in a verified knowledge base of actual policies. There was no retrieval layer pulling from canonical policy documents (no RAG, see module 02 notes 04-07). The model was free to invent plausible-sounding answers, and did.

#### The governance failure

The technical failure was the hallucination. The strategic failure was bigger: the decision to deploy an ungrounded model in a high-stakes customer-facing context, **and** the post-incident strategy of trying to disclaim responsibility for it. The court framed this as an "organisational error", not a "model bug".

#### Lessons

- **Organisations are fully responsible for their AI outputs.** "The AI did it" is not a defence in court.
- **High-stakes generative use cases need grounding.** RAG, verified knowledge bases, structured retrieval - whatever it takes to keep the model anchored.
- **Failures cascade.** Technical (hallucination) → process (no grounding plan) → strategic (denial of responsibility) → legal liability.

### Case 2: NYC government "MyCity" chatbot

#### What happened

A chatbot deployed on an official New York City government website gave residents advice **contradicting local laws and regulations** - on small-business operations, housing rules, employment law.

#### Why it was worse than Air Canada

Misinformation from a generative model is bad. Misinformation from a source citizens are conditioned to trust (the city government) is much worse. The authority of the source amplifies the harm of the error: people act on it because they have no reason to doubt it.

#### The governance failure

The administration initially refused to take the chatbot down despite known errors. No rollback plan, no oversight mechanism, no clear ownership of the model's behaviour in production. The same drift / monitoring / rollback gaps that destroy commercial AI projects, applied to public infrastructure.

#### Lessons

- **Authority of the source magnifies error impact.** Trustworthy sources need stronger guardrails, not weaker.
- **A rollback procedure is a launch requirement.** "We can't take it down" should never be the answer when the system is producing wrong outputs.
- **Public-sector AI needs governance equivalent or stronger to private-sector AI.** The trust contract with citizens is unforgiving.

---

## Taxonomy of failure modes

The two chatbot stories sit inside a broader taxonomy. Most AI failures fall into one of four families.

### Family 1: Strategic failures

The project picked the wrong problem from the start. Signs:

- **Solutionism**: starting with the technology ("we want to use LLMs") instead of with a problem.
- **Wrong problem**: AI applied to a low-value or ill-suited task. The fitness test from [01_identifying_ai_problems_and_feasibility.md](01_identifying_ai_problems_and_feasibility.md) was not applied or was applied superficially.
- **Unrealistic expectations**: stakeholders sold "AI will solve X" without acknowledging probabilistic limits, error rates, or required human oversight.

Failure mode: project ships, nobody uses it, KPIs don't move.

### Family 2: Data failures - "garbage in, garbage out"

The most common cause of AI project failure. The model architecture is fine; the data is not.

- Insufficient volume.
- Low quality (errors, noise, inconsistent encoding).
- Biased sampling (training data does not represent the production population).
- Mislabelled or weakly labelled.
- Schema drift over time, silently invalidating historical labels.

**Data governance** failures sit here too: inability to integrate data across silos, no clear ownership, no quality controls. If the primary asset is weak, the whole structure collapses regardless of how good the modelling is.

### Family 3: Operational failures - scale and cost

The "silent killer" of PoCs. Many projects produce a successful prototype on a data scientist's laptop and then die in production.

- **Scalability**: the system can't handle real production traffic. Latency explodes, throughput collapses.
- **Cost explosion**: API costs, GPU costs, storage costs scale linearly (or worse) with usage. A feature that's marginally profitable in pilot becomes unprofitable in production.
- **Prototype ≠ product**: the gap between a working notebook and a production system is huge, and it is technical (infrastructure), financial (operating cost), and organisational (someone owns the SLA).

### Family 4: Operational failures - ineffective MLOps

Post-deployment failures driven by absent or weak MLOps.

- No monitoring of model performance in production.
- No drift detection on inputs or outputs.
- No retraining cadence.
- No model registry, no versioning, no rollback.

The canonical example: a predictive-maintenance model that worked perfectly in evaluation drifts silently in production. By the time the business notices, the model has been wrong for months and trust is gone. See [02_kpis_lifecycle_drift.md](02_kpis_lifecycle_drift.md) for the full mechanism.

### Family 5: Organisational and governance failures

The AI project exists as an isolated initiative without:

- Cross-functional ownership (business + engineering + data + ops + legal).
- Alignment between stakeholders.
- Ethical, legal, and reputational oversight.
- A documented response plan for when the model fails.

The chatbot cases above sit here. The technology failed; the surrounding system failed worse.

---

## The unifying lesson: socio-technical

The single most useful framing of AI failure is **socio-technical**:

> AI failures are rarely purely technical. They are almost always a breakdown of the human and organisational systems surrounding the technology.

The Air Canada hallucination was the technical event. The failure was the organisational decision to deploy an ungrounded model **and** the strategic decision to deny responsibility afterwards. Either of those decisions, taken differently, would have prevented the legal disaster.

Practically, this means **prevention has to be socio-technical too**:

- Process: ground generative models, enforce evaluation gates, document fallback behaviours.
- Governance: cross-functional review of customer-facing AI, legal sign-off, ethical review.
- Operations: monitoring, rollback procedures, incident response.
- Culture: accountability for AI behaviour clearly assigned to the deploying organisation, never disclaimed to "the model".

A team that nails the technology but neglects the surrounding system is one hallucination away from being the next case study.

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Treating AI as a side project | Effort dispersed, no executive attention, dies in pilot | Apply AI to a core, high-value problem (Pattern 1) |
| Optimising for proxy metrics (CTR) | Clickbait outputs, short-term engagement, long-term damage | Choose the deeper KPI (retention) and accept the harder modelling task |
| Single-model strategy | Brittle, can't adapt across use cases | Ensemble approach; multiple models tuned for sub-problems |
| Deploying generative model without grounding | Hallucinations in production, legal exposure | Ground via RAG or verified knowledge base; never let the model "free-roam" on factual claims |
| "The AI is a separate entity" defence | Legal liability + reputational collapse | Take full responsibility; design for accountability from day one |
| No rollback procedure | Cannot take down a misbehaving system fast | Documented, tested, fast rollback as a launch requirement |
| PoC declared success, no scaling plan | Pilot purgatory, no production deployment | Plan for scale (technical and financial) from the start; cost-per-unit at production volume must be in the business case |
| Cross-functional team formed only at launch | Silos during build, alignment problems at launch | Cross-functional ownership from problem definition onward |
| Data governance treated as separate from AI project | Data quality issues surface late, in the worst place | Data governance is part of the AI project, not a parallel track |
| No incident plan for AI errors | Each incident is a fire drill | Documented response plan for model failure, including who decides on rollback |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Justify an AI investment to executives | Netflix / Amazon-style success patterns | Concrete examples of the four success patterns at scale |
| Convince stakeholders to fund MLOps | The MLOps-failure cases | Show what happens when monitoring and retraining are skipped |
| Argue for grounding generative systems | Air Canada chatbot precedent | Legal liability is real, not hypothetical |
| Argue for cross-functional ownership | The governance / silo failure family | Most failures are organisational, not technical |
| Diagnose a stuck pilot | The Family 3 failure mode (scale / cost) | Most pilots die at the production threshold |
| Position the work for long-term success | The four success patterns checklist | Use them as a maturity benchmark |

---

## See also

### Other notes
- [01_identifying_ai_problems_and_feasibility.md](01_identifying_ai_problems_and_feasibility.md) — the solutionism trap concretely materialised in failure Family 1
- [02_kpis_lifecycle_drift.md](02_kpis_lifecycle_drift.md) — the metric alignment that Netflix nails and that fraud-detector failures miss; the drift cycle that the MLOps failures skip
- [04_roles_and_stakeholders.md](04_roles_and_stakeholders.md) — who owns the governance role that the chatbot cases lacked
- [06_product_lifecycle_poc_to_scale.md](06_product_lifecycle_poc_to_scale.md) — the PoC-to-production transition where Family 3 failures happen
- Module 02 [04_rag_fundamentals.md](../../02_large_language_models/notes/04_rag_fundamentals.md) and [07_rag_production.md](../../02_large_language_models/notes/07_rag_production.md) — the grounding mechanism the Air Canada chatbot needed
- Module 02 [08_ethics_and_governance.md](../../02_large_language_models/notes/08_ethics_and_governance.md) — accountability, regulatory exposure, the governance practices that prevent Family 5 failures
