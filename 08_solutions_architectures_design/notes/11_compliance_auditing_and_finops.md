# Compliance, auditing, and FinOps

## TL;DR

**Compliance** is the process through which an organisation demonstrates that its AI systems operate responsibly, traceably, and transparently, in line with regulations, standards, and ethical guidelines. AI needs auditing more than traditional software because its behaviour drifts, its decisions are opaque, and non-compliance carries legal, reputational, and economic cost. The regulatory map has four layers: the **EU AI Act** with its obligations for high-risk systems, **GDPR** for personal data, **ISO 42001** (AI management) and **ISO 38507** (IT-AI governance), plus national frameworks and internal policy. An AI audit runs through five phases (planning, evidence collection, evaluation, reporting, follow-up) and leans on four documentation artifacts: policy repository, **ADRs**, **audit trail**, and the **AI Impact Assessment**. Technical controls (IAM, data protection, runtime monitoring, **explainability**, bias validation) make compliance enforceable rather than declarative, and the **PDCA** cycle keeps it alive as the system evolves. **FinOps** is the economic twin of the same discipline: not a finance exercise but an architectural one, because AI cloud cost is dynamic and non-linear, and the goal is to **spend better, not less**, through cost visibility, compute and data optimisation, and a sane model lifecycle. The module closes with the **AI architecture review** exercise: a TELCO churn system in production is reviewed across test and validation, governance, security and compliance, and responsible AI, pulling together everything from notes 09, 10, and this one.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **Compliance** | Demonstrable conformity to regulations, standards, ethics | Traceable, responsible, transparent operation |
| **EU AI Act** | EU regulation with obligations for high-risk AI | Risk classification drives your obligations |
| **GDPR** | Personal data protection applied to AI | Anonymisation, lawful basis, data subject rights |
| **ISO 42001** | AI management system standard | Certifiable, the "ISO 27001 of AI" |
| **ISO 38507** | Governance of IT amplified by AI | Board-level oversight of AI use |
| **Audit (5 phases)** | Plan, collect evidence, evaluate, report, follow up | Cyclic, not one-shot |
| **ADR** | Architecture Decision Record | Why a decision was made, dated and versioned |
| **Audit trail** | Logs, model versions, changes over time | Can you reconstruct a decision? |
| **AI Impact Assessment** | Structured evaluation of an AI system's impact | The AI-IA report, pre-deployment |
| **XAI** | Techniques that explain model decisions | Black box to white box |
| **PDCA** | Plan-Do-Check-Act continuous compliance loop | Compliance as a living process |
| **FinOps** | Architectural discipline for cloud cost sustainability | Spend better, not less |
| **Cost attribution** | Costs mapped to pipelines, models, teams | "What does one training run cost?" has an answer |
| **Right-sizing** | Match compute to actual load | No idle GPUs billing around the clock |
| **Architecture review** | Structured critical evaluation of an existing system | Four areas, guiding questions, checklist |

## Why compliance is a design concern

> Compliance is the process through which an organisation demonstrates that its systems operate responsibly, traceably, and transparently, in conformity with regulations, standards, and ethical guidelines.

Conformity means respecting norms, technical standards, and sector guidelines. For AI this takes a particular shape: intelligent systems have properties (learned behaviour, opacity, drift) that make them harder to govern than traditional software, so the demonstration part matters as much as the conformity part. The slides anchor the need for audit on three words: **traceability**, **responsibility**, **transparency**. Behind them sits a concrete risk calculus: non-compliance has legal consequences (fines, liability), reputational ones (a biased model in the news), and economic ones (remediation under pressure costs more than design-time compliance).

The architectural reading: compliance is a set of system requirements, not a document produced after the fact. A mature AI architecture is designed against the full regulatory stack from day one, because retrofitting traceability into a system that never logged its decisions is somewhere between expensive and impossible.

## The regulatory map

Four layers to keep in view when building AI systems:

- **EU AI Act**: obligations for systems classified as high-risk (risk management, data governance, technical documentation, logging, human oversight, accuracy and robustness).
- **GDPR**: personal data protection applied to AI pipelines, from lawful basis for training data to data subject rights over automated decisions.
- **ISO standards**: **ISO 42001** for the AI management system (the certifiable one), **ISO 38507** for the governance implications of AI at board level.
- **National frameworks**: public administration guidelines, sector rules, and internal organisational policy.

Knowing these frameworks is what lets you structure compliance correctly and plan audits that are coherent and effective. The layers are not alternatives: a real system typically answers to all four at once, and the architecture has to satisfy the strictest applicable constraint per concern.

## The audit process: five phases

> An audit is a structured, cyclic process. Understanding its phases is fundamental to guaranteeing not just initial conformity but its maintenance over time.

```
  +-> 1. Planning ........ objectives, scope, audit metrics
  |   2. Evidence ........ logs, metadata, model versions, decisions
  |   3. Evaluation ...... analysis against policy, regulation, risk
  |   4. Reporting ....... gaps, recommendations, remediation plan
  |   5. Follow-up ....... verify corrective actions landed
  +--------- cycle repeats as the system evolves ----------+
```

The phase most underestimated in practice is evidence collection: it is only cheap if the system was built to produce evidence. Logs, model version metadata, and decision records are architectural features; an auditor cannot conjure them retroactively. The loop closure (follow-up feeding the next planning round) is what makes the difference between an audit and an audit ritual: findings that nobody verifies got implemented are just expensive PDFs.

## Documentation artifacts

Documentation is the foundation of permanent compliance. Four artifacts carry the weight:

- **Policy and standards repository**: governance documents, ethical code, procedures. The single place where "what we committed to" lives.
- **Architecture Decision Records (ADR)**: the relevant architectural decisions, each with its context and rationale, dated. ADRs turn "why is it built this way?" from archaeology into a lookup.
- **Audit trail**: logs, model versions, changes over time. The raw material of phase 2 above.
- **AI Impact Assessment (AI-IA)**: the structured evaluation of what the system can affect and how badly.

Keeping these current is what lets an organisation demonstrate compliance under inspection and improve continuously. The practitioner's note: ADRs are the cheapest of the four and the most neglected. A ten-line record written at decision time saves a week of reverse engineering two years later, and it is exactly what an auditor (or the architecture review at the end of this note) asks for first.

## Technical controls

Compliance without technical enforcement is a promise, not a property. The slides list five control families:

- **Access control**: IAM, least privilege, AI-specific roles (who can retrain, who can deploy, who can read predictions).
- **Data protection**: encryption, masking, anonymisation.
- **Runtime monitoring**: metrics, alerts, decision logging.
- **Explainability**: mechanisms to explain model decisions.
- **Bias validation**: periodic tests for fairness and partiality.

These are the same controls that appeared in note 10 under security and responsible AI, now wearing their compliance hat: the point of this lecture is that one well-designed control serves both masters. Decision logging is simultaneously an operations tool, a security trail, and audit evidence.

## XAI: from black box to white box

**eXplainable AI (XAI)** is the set of techniques that make AI models transparent and understandable to humans, aiming to explain the "why" behind an algorithm's decisions. With XAI, algorithms move from black box to white box: more trust in the results, bias that can be found and corrected, and regulatory requirements that can actually be met. The slides distil it into three key principles: **transparency**, **comprehensibility**, **trust**.

The deck files XAI under "trends", which undersells it slightly: for high-risk systems under the AI Act, explainability stops being a trend and becomes an obligation. The honest caveat is that XAI techniques explain approximations of model behaviour, not the model's ground truth; treating a post-hoc explanation as gospel is its own failure mode. Still, an approximate explanation beats an unexplainable refusal when a stakeholder or a regulator asks why a customer was flagged.

## Internal vs independent audits, and certifications

Beyond internal audit, organisations reinforce credibility through external validation:

- **Internal vs external audits**: internal ones are cheaper and continuous; external ones are credible precisely because the auditor has no stake in the outcome.
- **Relevant certifications**: ISO 42001, GDPR conformity, security standards.
- **Independent review**: external validation of the AI governance itself.
- **Assurance mechanisms**: conformity reports, regular verification, integrity tests.

The dynamic worth internalising: internal audit finds problems early, independent audit makes the findings believable to customers and regulators. They are complements, not substitutes, and a certification is a snapshot; the assurance mechanisms are what keep the snapshot honest between renewals.

## PDCA: compliance as a living process

Compliance is not a one-off activity; it has to evolve with the AI system. The model the slides adopt is the classic **PDCA** cycle:

```
    +----> Plan ..... define policies, controls, roles, processes
    |      Do ....... implement them in architecture and process
    |      Check .... run audits, collect metrics, analyse incidents
    |      Act ...... update policies, fix non-conformities
    +--------------------- and around again -------------------+
```

The same loop already governs quality management and information security; reusing it for AI compliance is the right call because organisations already know how to run it. What changes for AI is the tempo: models drift and regulation is still settling, so the Check phase runs on months, not years.

## Challenges

The slides name four: **regulatory change** (the deck says the AI Act is "not yet fully defined"), **technical complexity**, **audit cost**, and **skills shortage**. Mitigation strategies exist: training, policy automation, compliance-integrated infrastructure, dedicated teams.

One factual aside on the first challenge: the AI Act entered into force in 2024 with obligations phasing in through 2026-2027, so the deck's caveat is about implementation detail (harmonised standards, guidance), not about whether it applies. Designing as if it might not arrive is no longer a defensible bet.

The deck's own compliance checklist, kept verbatim in spirit: documented governance policies aligned with regulation; clear roles for audit and compliance (committee, AI owner, compliance officer); logging, traceability, and audit trail implemented; a defined and cyclic audit process; explainability or transparency mechanisms; bias validation and periodic tests; continuous risk evaluation with active corrective measures.

## FinOps for AI: an architectural discipline

> FinOps for AI is first of all an architectural discipline: designing AI systems that are economically sustainable over time without sacrificing quality, reliability, or business value.

Many read FinOps as a purely financial topic; the slides push back, and rightly. In cloud AI systems, cost is neither static nor predictable the way it is in traditional systems. It is dynamic, driven by data volume, training frequency, model complexity, GPU usage, and inference patterns. Worse, it is **non-linear**: a small increase in data or model complexity can produce a disproportionate jump in storage, compute, or training cost. Which is why the goal is framed as **spend better, not less**: maximise the value generated per cloud euro. Architectural choices have a very strong economic impact, and an architect who cannot reason about the cost of a design is only doing half the job. Cost estimation basics were covered in module 04; this lecture is about making cost a first-class design variable.

## Cost visibility and attribution

The first FinOps principle: you cannot optimise what you do not measure. In AI systems this is genuinely hard, because cost is spread across storage, compute, networking, managed services, licences, and monitoring tools. Visibility means being able to answer questions like:

- What does a single training pipeline cost?
- What does one day of batch inference cost?
- Which models consume the most resources?
- Which team or project generates which costs?

The mechanism is **cost attribution**: associating costs to components, pipelines, models, and teams (in practice, tagging and per-workload accounting). Without attribution, cost optimisation degenerates into across-the-board budget cuts, which is precisely the "spend less" trap the discipline exists to avoid.

## Optimising compute, data, and the model lifecycle

**Compute** is usually the dominant cost line, especially with GPUs and other accelerators. The levers: **batch vs real-time** (batch tolerates cheaper, interruptible capacity; real-time pays for latency), **autoscaling** (capacity follows load instead of provisioning for peak), and **right-sizing** (instances matched to actual utilisation). The design target is elastic, load-aware, interruption-tolerant systems, turning cost into a controllable variable. This connects directly to the batch/streaming decision from note 02 and the scalability machinery from note 09: the same architecture choices that buy resilience also set the cost profile.

**Data** grows cost silently: storage, transfers, and uncontrolled duplication. Not everything deserves to live in storage forever, and feature engineering pipelines that spray intermediate datasets everywhere get expensive fast. The remedies are unglamorous: retention and cleanup policies for older data, compression, and relational storage where it kills redundancy. Data governance ground covered in depth in module 07 notes; here the angle is purely economic.

**Model lifecycle** is the cost centre nobody watches. Obsolete models left deployed, unused versions archived without control, and above all **unjustified retraining**: retrains that are too frequent, with no real benefit, burn compute and storage without moving performance. The slide's framing is the one to keep: design systems with a clear economy of data and models, where every stored artifact has a justifiable value. Retraining triggers belong to drift signals (note 05, note 09), not to a calendar.

## FinOps as a continuous loop

FinOps is not a one-off exercise but a continuous process: **feedback loops between cost, performance, and business value**, with architectural decisions revisited periodically against real production costs. The organisational half is accountability: data scientists, ML engineers, and architects must all be aware of the economic impact of their choices. The symmetry with the compliance half of this note is not accidental: PDCA for conformity, the cost feedback loop for economics, both running continuously over the same architecture. A system that is audited but unaffordable fails; so does one that is cheap but unauditable.

## The closing exercise: AI architecture review

The module ends with a slide-only esercitazione that is effectively the synthesis of notes 09, 10, and 11: simulate a structured evaluation of an existing AI system, the way an AI architect would in an internal audit, a pre-production review, or a compliance check. Not designing from scratch, but analysing critically what is already there.

**The system under review**: a churn prediction system at a telecom company, in production for several months. Daily batch pipeline; data from CRM, billing, and customer care; automatic feature processing; periodic model training; batch inference producing a CSV of at-risk customers, emailed as a report to marketing. The reported symptoms: model performance decay, decisions that are hard to explain, doubts about personal data handling, and no structured tests on the architecture. A believable system, which is what makes the exercise useful: nothing about it is cartoonishly broken, it is just a system that shipped and then aged without governance.

The review works through four intervention areas, each with guiding questions:

- **Test and validation** (note 09): are there load tests on the batch pipelines? Resilience tests (job failure, data errors, retries)? Is the system monitored for data drift and model degradation? Are the observed metrics technical only, or business too?
- **Governance and responsibility** (note 10): is it clear who owns the model? Are architectural decisions documented (ADRs)? Is there a deploy approval process? Does marketing know how to interpret the output correctly?
- **Security and compliance** (this note): is personal data anonymised and protected? Are model and results restricted to authorised roles? Are there controls against misuse or data leaks? Can you reconstruct how a decision was made?
- **Responsible AI** (note 10): have bias and fairness been analysed? Is human oversight in place for critical decisions? Can the system produce unintended negative effects? Can the result be explained to a non-technical stakeholder?

The operational checklist mirrors the four areas: documented load tests, resilience and fault-injection tests, model performance monitoring, drift and anomaly alerts; defined roles, tracked ADRs, approval and rollback process, business usage guidelines; access control on data and models, protection of sensitive outputs, logging and audit trail, incident response plan; bias and fairness analysis, decision explainability, defined human-in-the-loop, ethical impact assessment.

Two things make this exercise land. First, the scenario is the same TELCO churn system designed in the section 1 esercitazione (note 03), so the module closes by reviewing the architecture it opened by designing, which is exactly the arc of a real system's life. Second, every question in the four areas maps to a control, an artifact, or a test introduced somewhere in notes 09 through 11: the review is where the checklist stops being a list and becomes a method.

## See also

- [03_from_use_case_to_architecture_diagram.md](03_from_use_case_to_architecture_diagram.md) - the TELCO churn architecture designed in section 1, the system this module's closing review puts under scrutiny
- [05_ai_model_lifecycle_pipeline.md](05_ai_model_lifecycle_pipeline.md) - the lifecycle whose retraining and monitoring stages carry both the compliance evidence and the FinOps cost
- [09_scalability_resilience_testing_validation.md](09_scalability_resilience_testing_validation.md) - the test and validation area of the review; autoscaling and elasticity as shared ground between resilience and cost
- [10_enterprise_ready_architectures_and_governance.md](10_enterprise_ready_architectures_and_governance.md) - governance, responsible AI, and security controls that this note's audits verify
- Module 07 notes for data governance in depth; module 04 for cost estimation basics that FinOps operationalises
