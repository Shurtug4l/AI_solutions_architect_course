# Project Management Methodologies for AI

## TL;DR

The execution layer underneath the AI roadmap. A project is **a coordinated set of activities aimed at a unique goal within a defined time**, governed by the **constraint triangle** of Time, Cost, Quality - move one vertex, the others shift. The standard team roles - Project Manager, Project Team, Stakeholders, Sponsor - sit alongside the AI-specific roles from [04_roles_and_stakeholders.md](04_roles_and_stakeholders.md). PM methodologies split into three families. **Predictive (Waterfall)**: dense upfront planning, linear execution, ideal for stable requirements and regulated contexts; the cost of late changes is brutal because errors upstream become expensive downstream. **Adaptive (Agile)**: short iterations, continuous feedback, two dominant variants - **Scrum** (sprints of 1-4 weeks, defined roles Product Owner / Scrum Master / Development Team, four ceremonies Sprint / Daily / Review / Retrospective, three artefacts Product Backlog / Sprint Backlog / Increment) and **Kanban** (continuous flow, WIP limits, visual board, no fixed cadence). The slogan: **"Scrum plans, Kanban flows"**. **Hybrid** combines both - usually predictive for the regulatory or fixed-scope part, adaptive for the experimental modelling part. For AI, the practical answer is almost always **hybrid**: the data pipeline and compliance work fits Waterfall-style phase gates; the model development and iteration fits Scrum; the post-deployment monitoring and incident response fits Kanban. The single most important mental shift: **AI is intrinsically experimental and probabilistic** (see [02_kpis_lifecycle_drift.md](02_kpis_lifecycle_drift.md)), so pure Waterfall on the modelling stage will fail. Choose by context, team, and goals; no methodology is universally "better".

## Cheatsheet

| Concept | One-line | Where it matters |
|---|---|---|
| **Project** | Coordinated activities, unique goal, defined time | Any structured work |
| **Constraint triangle** | Time / Cost / Quality - move one, the others shift | All planning |
| **PM core roles** | PM, Team, Stakeholders, Sponsor | Every project |
| **Predictive (Waterfall)** | Plan first, execute linearly, change is expensive | Stable requirements, regulated domains |
| **Adaptive (Agile)** | Short iterations, continuous feedback | Variable requirements, high uncertainty |
| **Hybrid** | Predictive for stable parts + adaptive for evolving parts | Most AI projects in practice |
| **Scrum** | Sprints + roles + ceremonies + artefacts | Time-boxed iteration on the same goal |
| **Kanban** | Visual flow + WIP limits + continuous improvement | Continuous stream of work, no fixed cadence |
| **Scrum vs Kanban** | "Scrum plans, Kanban flows" | Choose by work shape |
| **Waterfall cost curve** | Errors upstream cost 10-100x to fix downstream | Why phase gates exist in Waterfall |
| **AI mismatch** | Pure Waterfall on probabilistic modelling = failure | Reason why hybrid wins for AI |

---

## Part 1: Project management fundamentals

### What is a project, and what does managing it mean?

A **project** is a coordinated set of activities aimed at a unique goal within a defined timeframe. The "unique goal" distinguishes a project from ongoing operations (which are recurring) and the "defined timeframe" distinguishes it from open-ended initiatives.

**Managing a project** means planning, coordinating, and controlling resources and activities. The three pillars of project success:

- **Clear objectives.** Vague goals produce vague outcomes.
- **Communication.** Most project failures are communication failures in disguise.
- **Constant monitoring.** Issues caught early cost a fraction of issues caught at delivery.

### The constraint triangle: Time, Cost, Quality

```
                    Quality
                       △
                      ╱ ╲
                     ╱   ╲
                    ╱     ╲
                   ╱   ◆   ╲
                  ╱  scope  ╲
                 ╱           ╲
       Time   ──────────────── Cost
```

The three constraints are **interdependent**. Move one, and at least one of the others moves with it:

- Compress **Time** → either pay more (Cost up) or deliver less / worse (Quality down).
- Cap **Cost** → either accept slower delivery (Time up) or accept lower quality.
- Raise **Quality** → either more time or more money, often both.

Some traditions add a fourth element (scope) in the centre, treated as the explicit variable that gets adjusted when the triangle is in tension. Either form, the principle is the same: **you cannot freely improve all three at once**. Project management is the discipline of making these trade-offs explicit and conscious instead of accidental.

### Roles and responsibilities

The general PM roles, distinct from but overlapping with the AI-specific roles from [04_roles_and_stakeholders.md](04_roles_and_stakeholders.md).

| Role | Responsibility |
|---|---|
| **Project Manager** | Coordinates, monitors, and adjusts the project; the central operational owner |
| **Project Team** | Executes the operational activities |
| **Stakeholders** | Influence or are influenced by the project (internal or external) |
| **Sponsor** | Provides funding, authority, and strategic support |

In AI projects, the Project Manager works in tandem with the AI PM and the Solution Architect. The Project Manager owns the *execution discipline* (timeline, budget, dependencies); the AI PM owns *what* to build and *why*; the SA owns *how* to build it.

### The lifecycle of a project (generic)

Every project, regardless of methodology, goes through these phases (the names vary):

1. **Initiation** — define the project, justify it, secure approval.
2. **Planning** — define scope, schedule, budget, resources, risks.
3. **Execution** — do the work.
4. **Monitoring and control** — track progress, manage changes, surface issues.
5. **Closure** — deliver, document, retrospective.

The differences between methodologies are mostly about *how long* each phase takes, *how strictly* phases are sequenced, and *how often* the cycle repeats.

---

## Part 2: Three families of methodology

### Historical evolution

| Era | Approach |
|---|---|
| 1950s-1980s | **Predictive** (Waterfall) dominates; born from military and engineering large-scale projects |
| 1990s-2000s | **Adaptive** (Agile, Scrum, Kanban) rises in response to software-development pain |
| Today | **Hybrid** approaches combine planning and adaptability based on context |

### Predictive vs. Adaptive vs. Hybrid

| Approach | Definition | Best for |
|---|---|---|
| **Predictive** | Detailed upfront planning, linear execution; minimise change | Clear requirements, stable environment |
| **Adaptive** | Short iterations, continuous feedback, embrace change | Variable requirements, high uncertainty |
| **Hybrid** | Mix predictive for some parts, adaptive for others | Most real-world projects, including most AI |

### When to choose what

- **Predictive:** requirements are well understood, the environment is stable, change is costly (regulated industries, infrastructure, manufacturing).
- **Adaptive:** requirements will evolve, the team needs to learn through doing, the cost of change must be low.
- **Hybrid:** part of the project is stable (compliance, infrastructure), part is evolutionary (modelling, UX). This is the realistic answer for almost every AI project.

### The three best-known methodologies

| Methodology | Family | Defining feature |
| --- | --- | --- |
| **Waterfall** | Predictive | Sequential phases, full plan upfront |
| **Scrum** | Adaptive | Time-boxed sprints with defined ceremonies |
| **Kanban** | Adaptive | Continuous flow with WIP limits |

---

## Part 3: Waterfall in depth

### What it is

The **Waterfall model** follows a strictly linear sequence:

```
   ┌────────────┐
   │ Requirements
   └─────┬──────┘
         ▼
   ┌────────────┐
   │   Design   │
   └─────┬──────┘
         ▼
   ┌────────────┐
   │ Development│
   └─────┬──────┘
         ▼
   ┌────────────┐
   │    Test    │
   └─────┬──────┘
         ▼
   ┌────────────┐
   │  Release   │
   └────────────┘
```

**Each phase must complete before the next begins.** Once development starts, requirements are frozen; once test starts, code is frozen.

### Phases in detail

| Phase | What happens |
|---|---|
| **Requirements analysis** | Collect, document, and sign off on what is to be built |
| **Design** | Architecture, interfaces, components, data model |
| **Development** | Build the system to spec |
| **Test** | Verify functional correctness, fix defects |
| **Release** | Final delivery |

### Roles, deliverables, milestones

- **Roles:** Project Manager, Analysts, Developers, Testers.
- **Deliverables:** documents, prototypes, code, test reports.
- **Milestones:** phase-gate checkpoints where one phase formally closes and the next opens.

Planning and control are the central skills - the upfront work in requirements and design is what makes the downstream execution predictable.

### The key insight: "errors upstream cost dearly downstream"

In Waterfall, the cost of fixing a defect grows by roughly an order of magnitude per phase. A bad requirement is cheap to fix in the requirements phase, painful in design, expensive in development, catastrophic in test, and may sink the release entirely. This is **why phase gates exist** - they are quality controls aimed at catching errors before they propagate.

### Strengths

- **Predictability.** When requirements are truly stable, the plan delivers what it promised.
- **Documentation.** Every phase produces formal artefacts - useful for audits, regulatory compliance, handoffs.
- **Clear accountability.** Each phase has clear ownership.
- **Suited to fixed contracts.** Easier to write contracts around than Agile.

### Weaknesses

- **Brittle under change.** A late requirement change can collapse weeks of work.
- **Late feedback.** The customer sees the system only at the end - any misunderstanding compounds.
- **Bad fit for experimental work.** Requires knowing what to build before building it; AI development can't honestly commit to that.

### Worked context: AI for credit-risk scoring (regulated)

> A financial company wants to develop an AI system to support credit-risk evaluation for retail customers. The system analyses historical customer data, returns a risk score, does not make automatic decisions but supports the human analyst, and must respect regulatory and auditability constraints. The project will be managed in Waterfall.

Why Waterfall fits *here*: the requirements come from regulation (GDPR, banking supervision, audit trails); they are known up front; they will not change mid-project. The need for documentation and traceability matches Waterfall's strengths. Phase gates align with regulatory milestones.

But note: this fit is for the *project management* layer, not the *modelling activity itself*. Even in a Waterfall-managed regulated project, the actual model development inside the Development phase will involve experimentation, hyperparameter tuning, and iteration - that's an Agile mini-loop inside a Waterfall macro-frame. This is the hybrid pattern in microcosm.

---

## Part 4: Scrum in depth

### What it is

**Scrum** is an Agile framework for managing complex projects through iterative and incremental cycles. Key principles:

- **Value delivered in small steps** — not a single big-bang release.
- **Constant customer collaboration** — feedback every cycle, not just at the end.
- **Continuous improvement** — the team itself gets better over time.

### The three roles

| Role | Responsibility |
|---|---|
| **Product Owner (PO)** | Defines priorities, maximises product value, owns the Product Backlog |
| **Scrum Master (SM)** | Facilitates the process, removes obstacles, protects the team from external pressure |
| **Development Team** | Builds the product increments; cross-functional, self-organising |

The PO is the voice of the business and customer. The SM is the voice of the process. The Development Team is the voice of execution.

### The four events (ceremonies)

| Event | Cadence | Duration | Purpose |
|---|---|---|---|
| **Sprint** | The container itself | 1-4 weeks | Time-boxed period to produce one increment |
| **Daily Scrum (standup)** | Daily | 15 min | Sync on progress, blockers, plan for the day |
| **Sprint Review** | End of sprint | 1-2 hours | Demo the increment to stakeholders, gather feedback |
| **Sprint Retrospective** | End of sprint | 45-90 min | Internal reflection: what worked, what didn't, what to change |

Each sprint produces a potentially shippable increment. The retrospective is the engine of continuous improvement - the team itself evolves between sprints.

### The three artefacts

| Artefact | What it is |
|---|---|
| **Product Backlog** | Dynamic list of all features, user stories, hypotheses. Prioritised by the PO. |
| **Sprint Backlog** | The slice of the Product Backlog the team commits to in the current sprint. |
| **Increment** | The output of the sprint - working, demonstrable, potentially shippable. |

The artefacts make progress visible. Everyone can see what's planned, what's in flight, what's done.

### Scrum for AI: the adaptation

Vanilla Scrum has a problem with AI: a sprint commits to producing an increment, but a modelling experiment may produce **no working increment** - just learnings. Two adaptations are common:

- **Treat experiments as first-class sprint goals.** "We will run experiment X and report findings" is a valid sprint commitment, even if no shippable code results.
- **Use Hypothesis Statements from [05_roadmap_and_prioritization.md](05_roadmap_and_prioritization.md)** as the unit of sprint work, with dual acceptance criteria.

Scrum then becomes the cadence layer for the Build-Measure-Learn loop, with each sprint being one cycle of the loop.

### Strengths and weaknesses

| Strengths | Weaknesses |
|---|---|
| Fast feedback, early course-correction | Requires disciplined team and committed PO |
| Built-in continuous improvement | Ceremonies can become rituals if not respected |
| High stakeholder engagement | Hard with distributed teams across time zones |
| Adapts to changing requirements | Hard to commit to fixed scope and date contracts |

---

## Part 5: Kanban in depth

### Origin and principle

Kanban (from Japanese 看板 = visual card) was born in Toyota's manufacturing system in the 1940s. It was adapted to software and project management to handle continuous flows of work where Scrum's fixed-cadence sprints don't fit.

> **Efficiency arises from visualisation.**

### What Kanban is

A visual method for managing workflow that reduces waste and bottlenecks. Three fundamental principles:

1. **Visualise the work.**
2. **Limit Work in Progress (WIP).**
3. **Measure and improve continuously.**

### The board

A typical Kanban board with columns representing workflow states:

```
┌──────────┬──────────┬──────────┬──────────┐
│  To Do   │  Doing   │  Review  │   Done   │
│          │ WIP ≤ 3  │ WIP ≤ 2  │          │
├──────────┼──────────┼──────────┼──────────┤
│  task A  │  task D  │  task F  │  task H  │
│  task B  │  task E  │          │  task I  │
│  task C  │          │          │  task J  │
└──────────┴──────────┴──────────┴──────────┘
```

Each card represents one unit of work. As work progresses, cards move left to right. WIP limits cap how many items can sit in each column simultaneously.

### WIP limits — the key mechanism

This is what makes Kanban work. If the "Doing" column is limited to 3 items, a 4th item cannot enter until something exits to "Review". This:

- **Surfaces bottlenecks.** If items pile up in front of a constrained column, the constraint becomes visible.
- **Forces focus.** The team can't take on more work just because it exists.
- **Reduces context switching.** Fewer items in flight, more attention per item.
- **Optimises flow.** The system gets faster end-to-end, even if individual workers feel "less busy".

### Kanban for AI: the natural fit

Kanban shines in **AI operations and maintenance** - where work arrives unpredictably and continuously (drift alerts, bug reports, retraining triggers, feature requests, security incidents). The post-deployment phase of an AI system is a Kanban problem, not a Scrum problem.

Typical AI-ops Kanban board:

| Column | Examples of cards |
|---|---|
| To Do | "Investigate drift alert on churn model"; "Add new data source to pipeline"; "Bug: API returns 500 on empty input"; "Quarterly retraining run"; "Update documentation for v2.3" |
| Doing (WIP ≤ 3) | "Retraining churn model with Q4 data"; "Investigating latency spike" |
| Review | "PR #144: improved feature engineering" awaiting MLE review |
| Done | (completed tasks for the week) |

### Strengths and weaknesses

| Strengths | Weaknesses |
|---|---|
| Adapts to continuous flow with no fixed cadence | Less effective for goal-driven sprints with a single shared objective |
| Reveals bottlenecks naturally | Requires discipline to respect WIP limits |
| Easy to start with - just a board | Less ceremony, less built-in alignment than Scrum |
| Strong fit for support and operations work | Risk of becoming "just a to-do list" without active flow management |

### "Scrum plans, Kanban flows"

The slogan captures the essential difference:

- **Scrum:** time-boxed iterations with a planned scope per sprint. Best when you have a stack of work to deliver toward a shared goal within a cadence.
- **Kanban:** continuous flow with WIP limits. Best when work arrives unpredictably and the goal is throughput and responsiveness.

Both are valid. Pick by the shape of the work.

---

## Part 6: Choosing and combining for AI

### Why pure approaches usually fail for AI

- **Pure Waterfall** fails on modelling because experimentation can't be planned linearly.
- **Pure Scrum** struggles with the unpredictable workload of production AI operations (incidents, drift events).
- **Pure Kanban** lacks the cadence that drives modelling iteration toward a goal.

### The hybrid pattern

Most real AI projects end up with a layered methodology stack:

| Layer | Methodology | Why |
|---|---|---|
| **Compliance and infrastructure setup** | Waterfall-like phase gates | Stable requirements; regulatory milestones |
| **Data pipeline build** | Waterfall or Scrum, depending on scope | Predictable engineering work |
| **Model development and iteration** | Scrum with adapted ceremonies | Iterative, hypothesis-driven, time-boxed |
| **Post-deployment operations** | Kanban | Continuous, unpredictable, flow-oriented |
| **Incident response** | Kanban with priority swimlane | Reactive, requires fast routing |

### The LEGO analogy

A useful demo: build a small LEGO house in three layers - base, walls + door + window, roof - using Waterfall vs. Agile.

- **Waterfall version:** design the whole house up front, then build it. More control, less flexibility. If the design is wrong, the whole structure is wrong at the end.
- **Agile version:** build the base, look at it, decide what to build next. More adaptability, more engagement. If something is wrong, you discover it after one layer, not three.

Neither is "better" in the abstract. Waterfall is better when the design is well understood and locked. Agile is better when learning is part of the process. **For AI, learning is always part of the process** - so Agile (or hybrid leaning Agile) is the default.

### Decision factors

When deciding the methodology for a specific AI project, weigh:

| Factor | Predictive favoured | Adaptive favoured |
|---|---|---|
| Requirements stability | High | Low |
| Regulatory / audit requirements | Strict | Light |
| Team familiarity with the domain | High | Low / experimental |
| Stakeholder availability for iteration | Low | High |
| Cost of late changes | Catastrophic (e.g., regulated release) | Manageable |
| Modelling vs. engineering balance | Engineering-heavy | Modelling-heavy |

In practice, most AI projects sit somewhere in between, and the answer is **hybrid by design** - not by accident.

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Treating PM methodology as religion | Religious wars about "we don't do that here" instead of practical choices | Choose by context, team, and goals; methodology serves the project, not the reverse |
| Pure Waterfall on AI modelling | Spec fixed at month 1, modelling reveals it's unbuildable at month 4, project crisis | Hybrid: Waterfall on the regulated frame, Agile inside the modelling phase |
| Scrum without a real PO | Backlog drifts, priorities unclear, team builds wrong things | Real PO with authority and time to engage, or don't call it Scrum |
| Scrum without retrospectives | Team never improves, same problems recur | Retrospectives are non-negotiable; they are the improvement engine |
| Kanban without WIP limits | Just a digital to-do list; bottlenecks invisible; nothing improves | Set WIP limits and respect them; the limits are the method |
| Daily standup as status report to manager | Team disengages, becomes ritual | Standup is for the team's coordination, not management reporting |
| Sprint reviews skipped | No external feedback, team builds in a vacuum | Demo every sprint, even rough; feedback is the point |
| Hybrid with no clear boundary | Confusion about which rules apply where | Document explicitly: this part is Waterfall, this part is Scrum, this part is Kanban |
| Constraint triangle ignored | Stakeholder asks for more scope same time same budget; team agrees; project fails | Surface the trade-off explicitly; force the conversation |
| Methodology change mid-project | Team disoriented, no methodology fully implemented | Methodology choice at planning; changes only with explicit retro decision |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Compliance / regulated AI project | Waterfall on the regulatory frame | Documentation, audit trail, predictability |
| Building data pipelines | Waterfall or Scrum | Mostly engineering, mostly predictable |
| Model development and experimentation | Scrum with Hypothesis Statements | Iterative, hypothesis-driven |
| Continuous AI operations post-deployment | Kanban with WIP limits | Unpredictable flow, throughput focus |
| Incident response on production model | Kanban with priority swimlane | Fast routing, visible flow |
| Cross-team AI initiative | Hybrid with clear boundaries | Different parts have different shapes |
| Surfacing scope/time/cost trade-offs | Constraint triangle explicitly | Forces conversation, prevents accidental trade-offs |
| Continuous improvement of the team itself | Scrum retrospectives or Kanban kaizen | Built-in feedback loop on the process |
| Aligning a non-technical sponsor | Predictive plan view as overlay | Sponsors understand timelines and milestones |

---

## See also

### Other notes
- [01_identifying_ai_problems_and_feasibility.md](01_identifying_ai_problems_and_feasibility.md) — feasibility / business case work that typically uses predictive structure
- [02_kpis_lifecycle_drift.md](02_kpis_lifecycle_drift.md) — the AI lifecycle phases this methodology layer executes; the experimental nature explains why pure Waterfall fails on modelling
- [03_case_studies.md](03_case_studies.md) — Family 4 failures (no MLOps) map onto missing Kanban-style operations discipline
- [04_roles_and_stakeholders.md](04_roles_and_stakeholders.md) — the AI PM and SA work alongside the Project Manager defined here
- [05_roadmap_and_prioritization.md](05_roadmap_and_prioritization.md) — the Hypothesis Statements that become sprint goals
- [06_product_lifecycle_poc_to_scale.md](06_product_lifecycle_poc_to_scale.md) — PoC fits experimental Kanban, MVP fits Scrum, Scaling fits hybrid with strong ops Kanban
- Module 03 [07_deployment.md](../../03_agentic_ai/notes/07_deployment.md) — the operational layer where Kanban-style flow management lives
- Module 02 [08_ethics_and_governance.md](../../02_large_language_models/notes/08_ethics_and_governance.md) — compliance constraints that push the project frame toward Waterfall
