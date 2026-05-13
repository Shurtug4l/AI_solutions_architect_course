# Roadmap and Prioritisation for AI Products

## TL;DR

An AI roadmap is **not a project plan**, it is a **strategic map for navigating uncertainty**. The fundamental difference from traditional software is that AI development asks "*can* we build this?" before it can ask "how long will it take?". The roadmap is anchored by a **North Star vision** (where the business will be in 3 years thanks to AI) and structured around **experimentation phases** with **decision points** based on actual results, not fixed deadlines. Three constraints shape it: tight coupling with the **data roadmap** (no data, no model), a **build-measure-learn engine** at the core, and an explicit **innovation vs. delivery balance** (treat the resource split between Quick Wins and long-term Strategic Initiatives like a balanced investment fund). Once initiatives are chosen, they get decomposed into **Epic → Feature → Hypothesis** - the AI-specific reframe of agile artefacts. The crucial shift is from **writing requirements to writing hypotheses**: stop describing components, start describing outcomes. The **Hypothesis Statement** ("For [user] who [pain point], we believe [AI solution] will produce [business metric]") becomes the unit of planning, and **dual acceptance criteria** - one technical (e.g., Recall > 80%), one business (e.g., 0.5% reduction in actual churn in A/B test) - are the bridge between data science and stakeholders. To prioritise across hypotheses, three frameworks complement each other: **MoSCoW** is qualitative, negotiation-oriented, ideal for MVP scoping and fixed deadlines; **RICE** is quantitative, data-informed, ideal for comparing very different initiatives in mature organisations; **Kano** is customer-centric, the only framework that surfaces **Delighters** (the wow-factor features that create disproportionate loyalty), ideal for strategic vision-setting and not for sprint-level prioritisation. None replaces the others - pick by question being answered, not by personal preference.

## Cheatsheet

| Concept | One-line | When |
|---|---|---|
| **AI roadmap** | Strategic map for uncertainty, not a fixed plan | Always |
| **North Star vision** | 3-year direction, anchors the team when experiments fail | Defined once, revisited annually |
| **Data roadmap coupling** | AI roadmap interleaved with data acquisition / cleaning / governance | Every AI initiative |
| **Build-Measure-Learn** | The engine that turns hypotheses into knowledge | Each iteration |
| **Innovation-vs-delivery balance** | Allocate resources like a balanced fund (e.g., 70% delivery / 20% adjacent / 10% transformative) | Quarterly resource planning |
| **Hypothesis Statement** | "For [user] who [pain], we believe [solution] → [metric]" | Replaces traditional user story |
| **Dual acceptance criteria** | Technical (model performance) + Business (KPI movement) | Every AI feature |
| **Epic → Feature → Hypothesis** | Strategic goal → capability → single experiment | Always |
| **MoSCoW** | Qualitative: Must / Should / Could / Won't | MVP scoping, fixed deadlines, non-technical stakeholders |
| **RICE** | Quantitative: (Reach × Impact × Confidence) / Effort | Mature org, large backlog, comparing very different initiatives |
| **Kano** | Customer-centric: Must-be / One-dimensional / Attractive / Indifferent / Reverse | Strategic vision, finding Delighters |

---

## Part 1: Building the roadmap

### The roadmap as a map of uncertainty

> AI development is a scientific discovery process, not the assembly of bricks. The roadmap reflects that.

In traditional software, the **"if"** is generally a given. The team asks **"how long will it take?"**. Plans are based on requirements that are - in principle - knowable up front.

AI inverts this. The **"if"** is the central uncertainty. The team has to ask **"can we even build this feature?"** before any timeline is meaningful. Concretely:

- Can the model reach acceptable accuracy on this task?
- Is there a learnable signal in the available data?
- Can we collect enough representative data within a reasonable budget?

These questions cannot be answered without experimentation. Therefore the AI roadmap is **not** a sequence of dated milestones leading to a fixed launch. It is a **strategic map**: a set of experimentation phases punctuated by **decision points** based on outcomes (the experiment succeeded, failed, or produced new questions).

### The data dependency: AI roadmap meets data roadmap

The AI team does not *own* the data. They *depend on it*. The roadmap must be interlocked with the organisation's **data roadmap**:

| Required data work | Lives on the data roadmap | Affects |
|---|---|---|
| Acquisition (sources, contracts, scraping) | Yes | Whether any AI initiative is possible |
| Cleaning and normalisation | Yes | Model performance ceiling |
| Labelling (cost, throughput, quality) | Yes | Supervised learning feasibility |
| Governance (privacy, retention, access) | Yes | Legal and ethical viability |

Practical implication: the AI roadmap must include **explicit data swimlanes**. "Build churn model" is not a roadmap item by itself; the prerequisite "consolidate customer interaction data from CRM and support logs into a labelled dataset" is also a roadmap item, with its own owner, timeline, and dependencies.

### Hypothesis-driven planning: Build-Measure-Learn

The progress engine of an AI roadmap is the **Build-Measure-Learn loop**, borrowed from Lean Startup.

```
                  ┌─────────────┐
                  │   LEARN     │  → next hypothesis
                  │  (analyse)  │
                  └──────▲──────┘
                         │
                  ┌──────┴──────┐
                  │   MEASURE   │  ← KPIs, A/B test
                  │  (data)     │
                  └──────▲──────┘
                         │
                  ┌──────┴──────┐
                  │   BUILD     │  ← model, prototype
                  │ (smallest   │
                  │  experiment)│
                  └─────────────┘
```

The roadmap items are **hypotheses to validate**, not features to ship: "*we believe* increasing personalisation depth on the homepage will raise 30-day retention by 2%".

### The North Star: vision as the strategic anchor

If the roadmap is an uncertain map, the **Vision** is the **North Star**: the long-term direction that does not change when individual experiments fail. The vision answers:

> "How will our business look 3 years from now, thanks to AI?"

Example: *"Become the most personalised shopping assistant in our segment, where every interaction adapts to the individual customer's intent and context."*

Function of the vision:

- **Strategic beacon.** When an experiment fails (and many will), the team knows what to try next - aligned with the North Star, not flailing.
- **Alignment device.** Engineering, product, marketing, leadership all rally around the same destination, even when the path changes.
- **Anti-drift guard.** Prevents the slow erosion of strategic intent under the weight of operational pressure.

### Living document: reviews driven by learnings, not output

Traditional review questions: "Did we ship the feature?"
AI review questions: **"What did we learn?"**

The output of a sprint or quarter is not measured only by what was built but by what was **learned**:

- Experiment succeeded with measurable KPI movement → move into Build-out.
- Experiment succeeded technically but no KPI movement → reconsider hypothesis.
- Experiment failed (no signal in data) → de-prioritise the initiative; that learning prevents a much larger waste later.

Each iteration carries **dual metrics**: technical (does the model hit its target?) and business (does that technical level move the KPI?). The PM-as-translator role from [04_roles_and_stakeholders.md](04_roles_and_stakeholders.md) is operationalised here.

### Balancing innovation and incremental delivery

A persistent tension in AI portfolios:

- **Incremental delivery (short term):** Quick Wins, predictable value, low complexity. Builds credibility and ROI.
- **Innovation (long term):** High complexity / high uncertainty, transformative when it works. Builds strategic competitive position.

A team that only ships Quick Wins becomes operationally efficient but strategically irrelevant: someone else discovers the next paradigm and disrupts them. A team that only chases moonshots burns capital without producing visible value, loses executive support, and eventually gets defunded.

**The fix: explicit resource allocation as a balanced investment fund.** Common splits seen in mature AI orgs:

- **70% incremental delivery** (Quick Wins, Strategic Initiative execution from the Value/Feasibility matrix).
- **20% adjacent innovation** (extending current capabilities into new use cases).
- **10% transformative bets** (long-horizon research, foundational capabilities).

The numbers are organisation-specific, but the principle is universal: **innovation must be protected from delivery pressure** by an explicit budget line. Without it, the team will rationally reallocate exploration time to shipping, and the moonshots starve.

---

## Part 2: Decomposing roadmap into work — Epic, Feature, Hypothesis

### Why traditional user stories fail in AI

Traditional user stories work for deterministic software: "User clicks button → expected behaviour happens". Two failure modes appear when this template is applied to AI:

- **Probabilistic, not deterministic.** AI systems don't have a single correct output. A story like "show 5 recommendations" is technically "done" the moment 5 items appear, regardless of whether they are actually relevant.
- **Quality of intelligence matters more than quality of interface.** The traditional story can be checked off while the underlying intelligence is broken. Business failure, story marked complete.

**Conclusion:** AI user stories must describe **the quality of the intelligence**, not just the interface that exposes it.

### From output to outcome

The reframe is from **output** ("what do we build?") to **outcome** ("why do we build it, and what user experience does it create?").

| Traditional (output) | AI-adapted (outcome) |
|---|---|
| "Show 5 recommendations on the homepage" | "I want to discover products relevant to me so I can save time" |
| "Reply to customer questions in the chatbot" | "When I have a question about my order, I want a helpful answer so I don't have to wait for a human" |

The outcome formulation gives the **data science team flexibility** to experiment with different solutions toward the same user goal, instead of being locked into a specific implementation.

### The Hypothesis Statement: the unit of AI planning

A single user story is too small for an AI feature - it doesn't capture the experimental setup. The **Hypothesis Statement** extends it:

```
For [target user]                                  (User)
who [has this problem or pain point]               (Problem)
we believe that [this AI solution]                 (Solution hypothesis)
will result in [this measurable success metric].   (Success metric)
```

Worked example:

> *For an e-commerce user who has already purchased and frequently ignores generic marketing emails,*
> *we believe that a next-product prediction model embedded in personalised email content*
> *will produce a 15% increase in email open rate.*

What this format enforces:

- The user is explicit. No vague "our customers".
- The problem is concrete. No vague "improve engagement".
- The solution is named, but as a hypothesis, not a commitment.
- The success metric is quantitative and tied to a business KPI.

The whole statement is an **experiment specification**.

### Dual acceptance criteria: the technical-business bridge

The most important addition to AI user stories: **acceptance criteria come in two flavours**, technical and business.

#### Technical criteria (for Data Scientists)

The model performance bar - "pass/fail" on validation data.

| Examples |
|---|
| "The churn classification model must reach Recall > 80% on the 'likely churn' class" |
| "The recommendation engine must achieve Precision@10 > 0.6 on the held-out test set" |

#### Business criteria (for Stakeholders)

The business impact bar - tested in production, typically via A/B test.

| Examples |
|---|
| "The model (with Recall > 80%) must produce a statistically significant reduction in actual churn rate of ≥ 0.5%" |
| "The new recommendations must drive a +5% lift in 30-day return rate vs. control in A/B test" |

#### Why both are required

Technical criteria alone reproduce the fraud-detector trap: 99.9% accuracy that catches no actual fraud. Business criteria alone fail to give the team a measurable target to optimise during development. **The pair forms a contract** that ensures the team is building models that are simultaneously accurate *and* useful.

### The hierarchy: Epic → Feature → Hypothesis

| Level | Definition | Example |
|---|---|---|
| **Epic** | Long-term strategic goal on the roadmap | "Improve customer retention" |
| **Feature** | A specific capability that contributes to the Epic | "Proactive anti-churn offer system" |
| **Hypothesis** | A single experiment or learning cycle | "Test churn model with Recall > 80%" or "Test 10% discount impact on at-risk segment" |

Each Hypothesis ladders up to a Feature, each Feature to an Epic. The team's daily work is at the Hypothesis level; the strategic conversation is at the Epic level; the Feature level connects them.

### The mindset shift: hypotheses, not requirements

The final reframe: AI planning is not about writing requirements that promise certainty. It is about writing **hypotheses that produce learning**. The acceptance criteria are the contract between Data Science and Business; every experiment either validates the hypothesis, invalidates it, or refines it. **Every iteration produces value as learning**, even when the model fails - because the team now knows something it didn't, and the next experiment is better-targeted.

---

## Part 3: Three prioritisation frameworks

Once the backlog is full of hypotheses, the team must choose what to do next. Three complementary frameworks; pick by question being asked.

### MoSCoW — qualitative, negotiation-oriented

#### What it is

A qualitative prioritisation framework with four buckets:

| Bucket | Definition | AI examples |
|---|---|---|
| **Must have** | Non-negotiable. Without it, the release is a total failure. | "Model produces a prediction (even if not optimised)"; "System is GDPR-compliant" |
| **Should have** | Important and high-value but not blocking launch. | "Model handles missing data without errors"; "API responds within 500ms (workaround exists)" |
| **Could have** | Adds value, delights users, but secondary impact. First to be cut under pressure. | "Chatbot has a fun personality and uses emoji"; "Model returns a confidence score" |
| **Won't have** | Explicitly out of scope for this release - not forever, just not now. | "Recommender doesn't support anonymous users in v1"; "Model not trained on Spanish input" |

#### Strengths

- **Simplicity.** No formulas. A linguistic framework everyone understands.
- **Communication.** Easy to explain to non-technical stakeholders.
- **MVP scoping.** The MVP *is* the Must Haves; everything else can slip.
- **Fixed deadlines.** Forces hard trade-offs when the launch date is non-negotiable.

#### Weaknesses

- **"Must Have" inflation.** Stakeholders push their preferences into Must, defeating the purpose. If everything is Must, nothing is.
- **Boundary vagueness.** The line between Should and Could is subjective, generating friction.
- **Requires strong PM leadership.** Someone must arbitrate and force justification for every Must claim.

#### When to use

- Defining the MVP for a launch with a fixed deadline.
- Aligning non-technical stakeholders with simple trade-off language.
- Early-stage projects without enough data for quantitative frameworks.

### RICE — quantitative, data-informed

#### What it is

A scoring framework: `RICE = (Reach × Impact × Confidence) / Effort`.

| Factor | Definition | Quantification |
|---|---|---|
| **Reach** | How many people / transactions / events are impacted in a given period | From analytics: "users per month", "transactions per day" |
| **Impact** | How much this moves the strategic KPI if successful | Standardised scale (e.g., Massive: 3, High: 2, Medium: 1, Low: 0.5) |
| **Confidence** | How sure we are about the Reach and Impact estimates | Percentage (100% certain, 50% pure guess) |
| **Effort** | Total cost in time and resources | Person-months (1 person × 1 month = 1PM) |

```
        Reach × Impact × Confidence       (expected value)
RICE = ────────────────────────────  =  ──────────────────
                  Effort                      (cost)
```

#### Strengths

- **Quantitative rigour.** Forces evidence-based estimates rather than opinions.
- **Standardisation.** Repeatable process. Each new idea gets a RICE score.
- **Defuses arguments.** Conversation shifts from "I prefer X" to "X scored 12.5, Y scored 8.4".
- **Comparing different work.** Lets the team prioritise UI improvements alongside model retraining alongside infra work.

#### Weaknesses

- **Time-consuming.** Gathering data for Reach, Impact, Effort takes real effort across many initiatives.
- **False objectivity.** Impact and Confidence are still estimates. The formula's apparent precision can mislead.
- **Argument shifts to inputs.** Teams can spend hours debating Confidence percentages instead of customer value.

#### When to use

- Mature organisations with accessible analytics and a culture of estimation.
- Comparing many heterogeneous initiatives objectively (model vs. UX vs. infra).
- Avoid when the team is new or the data is unreliable; MoSCoW is the better starting point.

### Kano Model — customer-centric, vision-oriented

#### What it is

A framework that classifies features by their effect on **customer satisfaction**, not by internal complexity. The fundamental insight: **the relationship between functionality and satisfaction is not linear**.

#### The five categories

| Category | Customer reaction | AI example |
|---|---|---|
| **Must-be** | Present → neutral satisfaction; absent → extreme dissatisfaction | "AI never provides obviously false or harmful information" |
| **One-dimensional** | Linear: more is better | "Recommendation engine becomes more accurate"; "Chatbot understands more requests" |
| **Attractive (Delighters)** | Absence → no dissatisfaction; presence → disproportionate delight | AI proactively suggests leaving earlier due to traffic; **the wow-factor zone** |
| **Indifferent** | No effect either way - pure waste | Features users don't notice or care about |
| **Reverse** | Customer actively doesn't want it - more = worse | Overly intrusive AI assistant; annoying "smart" notifications |

#### Why AI is a Delighter factory

The Attractive / Delighter category is where AI shines. Proactive utility - help the user didn't ask for but immediately recognises as valuable - is uniquely well-suited to AI capabilities (prediction, anomaly detection, personalisation). Other prioritisation frameworks miss this category entirely; **Kano is the only one that surfaces Delighters explicitly**.

#### How it's applied: the Kano survey

Not an internal discussion - **user survey data**. For each feature, two questions:

- **Functional:** "How would you feel if you could [feature]?"
- **Dysfunctional:** "How would you feel if you couldn't [feature]?"

Cross-tabulating the answers statistically classifies each feature into one of the five categories.

#### Strengths

- **Customer-centric.** Forces the organisation to think in terms of satisfaction, not internal complexity.
- **Surfaces Delighters.** The only framework that does this explicitly.
- **Competitive advantage.** Encourages the search for wow factors that build product love.

#### Weaknesses

- **Time-consuming.** Designing, deploying, analysing Kano surveys is significant work.
- **Hard with AI.** Users struggle to evaluate abstract technical features ("a recommender with higher Precision@10" means nothing to them). Survey questions must focus on **end benefits and experiences**, not technology.
- **Not for sprint-level decisions.** Strategic tool, not tactical.

#### When to use

- Strategic vision-setting and high-level customer-driven decisions.
- Defining the vision for a new product or major release.
- Building prototypes where deep UX feedback is needed.
- **Not** for daily sprint prioritisation - use RICE or MoSCoW for that.

### Choosing between the three

The frameworks are not competitors. They answer different questions.

| If your question is... | Use |
|---|---|
| "What is the absolute minimum to ship by date X?" | MoSCoW |
| "Which of these 30 initiatives gives us the best ROI?" | RICE |
| "What would make customers fall in love with our product?" | Kano |
| Combined: define vision (Kano) → fill backlog (RICE) → scope each release (MoSCoW) | All three, sequentially |

In a mature org, all three coexist at different levels of the planning hierarchy.

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Treating the roadmap as a fixed plan | Stakeholders treat AI dates as commitments; team blamed when experiments fail | Communicate explicitly that AI roadmap is a map of uncertainty, not a project plan |
| No data roadmap alongside the AI roadmap | Model development blocked waiting for data, again and again | Interleave data swimlanes into the AI roadmap; data work is roadmap work |
| Output-driven sprint reviews | "Did we ship?" gets a yes; KPI doesn't move | Reframe reviews around learnings: what did we *learn*, not what did we ship |
| Innovation budget eroded by delivery pressure | Year-2 pipeline empty, team chasing only Quick Wins | Explicit % allocation (e.g., 10% transformative) protected at the planning level |
| Traditional user stories for AI features | Stories marked done, business KPI doesn't move | Switch to Hypothesis Statements + dual acceptance criteria |
| Only technical acceptance criteria | Models hit the technical target but produce no business value | Always add business criteria measured via A/B test or equivalent |
| "Must have" inflation in MoSCoW | Everything is a Must; the framework becomes useless | Strong PM arbitration; require explicit justification for every Must |
| RICE numbers debated instead of customer value | Hours spent on Confidence percentages; the real question forgotten | Time-box scoring; revisit assumptions, not the formula |
| Kano survey questions about technology | Users can't answer; data is noisy | Phrase Kano questions in terms of end benefits, not technical features |
| Using one framework for everything | Wrong tool for the question | Match the framework to the question being asked |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Define long-term direction | North Star vision | Anchors experimentation, survives failures |
| Plan AI work that depends on data | AI roadmap + interleaved data roadmap | Data is the dependency; ignore at your peril |
| Drive experimentation discipline | Build-Measure-Learn loop | Turns hypotheses into knowledge |
| Balance short and long term | Explicit % allocation (delivery / adjacent / transformative) | Protects innovation from delivery pressure |
| Write an AI feature | Hypothesis Statement + Dual Acceptance Criteria | Outcome-driven, measurable, bridges DS and business |
| Connect work to strategy | Epic → Feature → Hypothesis hierarchy | Daily work ladders up to strategic intent |
| Scope an MVP with a deadline | MoSCoW | Forces brutal trade-offs |
| Prioritise a large heterogeneous backlog | RICE | Quantitative comparison across very different work |
| Find the wow-factor features | Kano (focus on Attractive category) | The only framework that surfaces Delighters |
| Decide what to NOT build | MoSCoW Won't or Kano Indifferent / Reverse | Saying no is as important as saying yes |

---

## See also

### Other notes
- [01_identifying_ai_problems_and_feasibility.md](01_identifying_ai_problems_and_feasibility.md) — the Value/Feasibility matrix that feeds the initiatives the roadmap turns into hypotheses
- [02_kpis_lifecycle_drift.md](02_kpis_lifecycle_drift.md) — the dual KPI / technical metric chain that becomes dual acceptance criteria
- [03_case_studies.md](03_case_studies.md) — Netflix as a textbook example of the build-measure-learn engine at scale
- [04_roles_and_stakeholders.md](04_roles_and_stakeholders.md) — who runs the prioritisation conversation (PM with stakeholders, mediated by SA as translator)
- [06_product_lifecycle_poc_to_scale.md](06_product_lifecycle_poc_to_scale.md) — the journey from validated hypothesis to scaled production
- [07_project_management_methodologies.md](07_project_management_methodologies.md) — Scrum and Kanban as the execution layer for the prioritised backlog
- Module 01 [01_intro_ml_workflow.md](../../01_machine_learning/notes/01_intro_ml_workflow.md) — the train/validate/test discipline that underlies technical acceptance criteria
