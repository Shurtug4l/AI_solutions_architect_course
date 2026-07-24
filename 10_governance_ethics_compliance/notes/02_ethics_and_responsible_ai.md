# Ethics and responsible AI

## TL;DR

**Responsible AI is what remains of AI ethics after it survives contact with a release calendar: principles converted into controls, metrics, and named owners.** The working vocabulary is **FATE**: fairness (comparable treatment of people and groups), accountability (a named human answers for the system's decisions), transparency (system-level disclosure of what the AI is and does), and explainability (decision-level answers to "why this output"). Around these, the global guideline corpus shows a real **ethical consensus**: dozens of published frameworks converge on human rights as the baseline, human agency and oversight, non-discrimination, and robustness. The convergence is genuine at the level of words and dissolves at the level of implementation, which is exactly where **ethics washing** lives: principles published for reputational cover while nothing in the development process changes. The known specimens are ethics boards without veto power and principle lists without a single associated metric. The antidote is operational: moral dilemmas analyzed concretely per domain (healthcare triage, credit scoring, hiring, all three sitting in the AI Act's high-risk annex for a reason), **ethical checklists** applied as gates in the lifecycle rather than as retrospective paperwork, and **ethical KPIs** that turn a one-shot assessment into continuous evaluation: fairness gaps per release, override rates, redress turnaround, drift alerts with owners and escalation thresholds.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **FATE** | Fairness, accountability, transparency, explainability | Two outcome principles (F, A) plus two visibility principles (T, E) |
| **Fairness** | Comparable treatment across groups and individuals | The metric is chosen before training, not after the complaint |
| **Accountability** | A named human answers for the system | "The model decided" is not an accepted answer, anywhere |
| **Transparency** | System-level disclosure: what it is, that it is AI, on what data | The user knows they are facing a machine and what it does |
| **Explainability** | Decision-level: why this specific output | Explanation calibrated to the audience, not to the developer |
| **Ethical consensus** | Published guidelines converge on a handful of themes | Human rights, agency, non-discrimination, robustness recur everywhere |
| **Ethics washing** | Principles as PR, enforcement absent | Board without veto, principles without metrics, ethics as marketing |
| **Domain dilemmas** | Health, finance, HR concentrate the hard tradeoffs | All three map onto Annex III high-risk categories |
| **Ethical checklist** | Forcing function applied at lifecycle gates | Useful as structured interrogation, useless as checkbox ritual |
| **Ethical KPIs** | Principles converted into monitored metrics | Thresholds, owners, escalation; evaluated continuously, not annually |

## FATE: four principles, two families

The acronym packs two different kinds of demand, and keeping them separate sharpens every later discussion.

**Fairness** and **accountability** are outcome principles. Fairness asks whether the system distributes benefits and errors acceptably across people and groups; it is a property of what the system does. The immediate complication is that fairness is not one metric but a family of mutually incompatible ones (demographic parity, equalized odds, calibration), and the choice among them is a value judgment wearing a mathematical costume. That judgment belongs to the governance layer, made explicitly and documented, before training starts. Note 03 goes deep on this. Accountability asks who answers when the outcome is wrong: a named role with authority to remediate, an audit trail that reconstructs the decision, and a redress path the affected person can actually use. Accountability is the principle that makes the other three enforceable; without it, fairness violations are discovered but nobody owns the fix.

**Transparency** and **explainability** are visibility principles, and the distinction between them is one of the exam-grade items of this module. Transparency operates at the **system level**: disclosing that an AI system is in use, what it is for, what data feeds it, what its known limitations are. It is satisfied by documentation and disclosure, and the AI Act's transparency obligations (chatbot disclosure, deepfake marking) live here. Explainability operates at the **decision level**: why did this applicant get rejected, why this diagnosis suggestion. It has degrees, global versus local, intrinsic versus post-hoc, and its quality is judged by the recipient: a data scientist reads SHAP values, a loan applicant needs the principal reasons in one paragraph, a regulator needs both plus the methodology. A system can be perfectly transparent and completely unexplainable (disclosed black box), or locally explainable while opaque as a system. Conflating the two produces governance documents that promise the wrong artifact to the wrong audience.

## The consensus and its limits

A striking empirical fact about AI ethics: reviews of the guideline corpus (the most cited, Jobin et al. 2019, analyzed 84 published frameworks from governments, companies, and NGOs) find genuine convergence on a short list of themes: transparency, justice and fairness, non-maleficence, responsibility, privacy. The course's framing of the consensus, human rights as the floor, human agency, non-discrimination, robustness, is the same list from a European angle, and it matches the HLEG requirements from note 01 nearly term for term. The two reference frameworks the field keeps returning to, the OECD AI Principles and the NIST AI RMF, rest on this same settled values layer and are dissected in note 01; here they matter only as evidence that agreement at the level of principle is a solved problem, and the real disagreement lives one floor down.

The consensus is real and it is also thin. Everyone agrees AI should be fair; the agreement evaporates when you ask which fairness metric, at what threshold, at whose cost. Everyone endorses human oversight; few specify when an override is mandatory versus theatrical. The guideline corpus converges because principles at that altitude are cheap to endorse. The practical reading: cross-organizational agreement on principles is a solved problem and carries almost no information. What differentiates organizations is the layer below, and that layer is where this module spends the rest of its time.

## Ethics washing

The term names the practice of deploying ethics language as a substitute for binding constraints: publish principles, appoint an advisory board, sponsor a conference, and change nothing about how systems ship. The phrase entered the debate around 2018 (Ben Wagner's formulation, "ethics as an escape from regulation", remains the sharpest) precisely because the corporate principle inflation of those years made the pattern visible.

The mechanism has recognizable parts:

- **Boards without power.** The canonical case is Google's external AI ethics council (ATEAC, 2019), dissolved about a week after launch; whatever the proximate cause, an advisory body with no gate in the release process was structurally incapable of mattering. The diagnostic question from note 01 applies unchanged: has a launch ever waited for this body?
- **Principles without metrics.** A published value that no dashboard tracks and no threshold enforces is a communications asset, not a control.
- **Self-assessment without evidence.** "We take fairness seriously" versus a fairness report with the metric, the number, and the trend.
- **Ethics as regulation deferral.** The historical function of some corporate ethics programs was to argue that binding rules were unnecessary. The AI Act's arrival settles that argument in the EU, and repositions ethics work as the layer above legal compliance rather than a substitute for it.

The countermeasure is not more sincerity, it is structure: every principle maps to at least one policy, every policy to at least one control, every control to a metric and an owner. That chain is checkable by an outsider, which is the point. Ethics that cannot be audited is indistinguishable from marketing.

## Moral dilemmas in the field

Three domains concentrate the hard cases, and not coincidentally all three appear in the AI Act's Annex III high-risk list.

**Healthcare.** A diagnostic support model trades sensitivity against specificity, and the two error types carry asymmetric moral weight: a missed tumor is not the mirror image of a false alarm. Resource allocation models (triage, transplant lists) push distributive justice questions directly into code. The quieter dilemma is automation bias: clinicians defer to the model's suggestion even when their own judgment disagrees, which silently converts decision support into decision replacement without anyone signing off on the change.

**Finance.** Credit scoring is the textbook case of proxy discrimination: remove the protected attribute and the model reconstructs it from postal code, employment history, or shopping patterns. The dilemma is real because the alternative is not obviously better: a stricter model that excludes marginal applicants "for their own protection" produces financial exclusion, and a looser one produces over-indebtedness. Both failure modes hurt the same populations.

**Human resources.** Hiring models train on historical decisions and inherit their prejudices; the documented case is Amazon's experimental CV screener (reported 2018), which learned to penalize resumes signaling female candidates because the training data reflected a male-dominated hiring history. HR adds a feedback loop the other domains lack: today's biased screening becomes tomorrow's training data, so the bias compounds across hiring cycles unless actively interrupted.

The shared lesson: the dilemmas are domain-specific but the failure pattern is constant, historical data encoding past choices, error costs distributed unevenly, and human oversight degrading under throughput pressure. This is why the checklist and KPI machinery below is generic while its calibration is always local.

## From principles to checklist

An ethical evaluation checklist is the cheapest operationalization tool available, and its value depends entirely on where it sits. Applied as a gate, before development starts and again before deployment, with a named reviewer and recorded answers, it is a forcing function: it guarantees the uncomfortable questions get asked while there is still time to act on the answers. Applied retrospectively to a finished system, it is documentation of decisions already taken, at best.

A checklist worth using for a decisional model interrogates, at minimum: purpose and necessity (is an automated decision justified here at all); data provenance and legal basis; the fairness metric chosen, the threshold, and who chose it; the explainability method and whether it matches each audience that will receive explanations; the human oversight design, including when override is mandatory; the redress path from the affected person's point of view; and the monitoring plan after deployment. The last item is the one most often missing, and it is the bridge to KPIs: a checklist certifies a snapshot, and models do not stay snapshotted.

Checklists fail in a known way: checkbox compliance, where the ritual of ticking replaces the judgment the item was meant to trigger. Two design counters help: require free-text justifications rather than yes/no answers on the judgment-heavy items, and record dissent, who disagreed and why, instead of forcing consensus. A checklist with an unanimous yes on every item across every project is not evidence of virtue, it is evidence the instrument has stopped measuring.

## Ethical KPIs: making evaluation continuous

The structural weakness of assessments and checklists is that they are events, while model behavior is a process. Ethical KPIs close that gap: a small set of quantitative indicators, computed on production behavior, reviewed on a cadence, with thresholds that trigger action. Turning "we value fairness" into "demographic parity difference on approvals, computed monthly per segment, owner: model owner, escalation to the AI board above 0.05" is the entire distance between ethics and responsible AI.

A base KPI set for a decisional system, organized by the principle it operationalizes:

| Principle | KPI examples | Reading |
|---|---|---|
| Fairness | Parity or odds gap per release and per segment; drift of the gap over time | The trend matters more than the level; a widening gap is an incident, not a footnote |
| Accountability | Redress requests received, upheld, turnaround time; incidents with a named owner within SLA | Slow redress is denied redress |
| Transparency | Share of affected users reached by disclosure; documentation coverage of production models | An inventory gap is a transparency KPI at zero |
| Explainability | Explanation delivery rate; complaint rate about unintelligible explanations | Measured at the recipient, not at the method |
| Oversight | Human override rate and its trend | Near-zero override signals rubber-stamping as loudly as constant override signals distrust |

Design rules that keep the set honest: few indicators rather than many (a KPI nobody reviews is a log line), every KPI has an owner and a threshold with a defined consequence, and the set mixes leading indicators (documentation coverage, review completion) with lagging ones (incidents, complaints). The override rate deserves its double reading: it is the single cheapest signal of whether human oversight is real, and both of its extremes are findings.

## Gotchas

- **Treating transparency and explainability as synonyms.** One is system-level disclosure, the other is decision-level justification. Promising "full transparency" when the recipient needs a local explanation (or vice versa) produces compliant-looking documents that satisfy nobody, including the regulator reading them.
- **Reading consensus on principles as agreement on practice.** The 84-guideline convergence is about vocabulary. Two organizations endorsing "fairness" can be running incompatible metrics with opposite winners. Always ask for the metric and the threshold; the principle carries no information.
- **Auditing the existence of ethics artifacts instead of their power.** Principles published, board appointed, checklist filed: all can be true of a pure ethics-washing operation. The audit question is whether any of it can stop a launch, and whether it ever has.
- **Removing the protected attribute and declaring the model fair.** Proxy reconstruction is the default behavior of any capable model trained on correlated data. Fairness through blindness fails predictably; measuring outcomes per group requires keeping (governed) access to the attribute you are protecting.
- **One-shot ethical assessment on a system that drifts.** The assessment certifies the model at time zero; the training distribution, the population, and the use pattern all move. Without KPIs on production behavior, the assessment's shelf life is weeks, and its main function becomes liability theater.
- **KPI sets designed for reporting instead of action.** Twenty indicators reviewed annually in a slide deck govern nothing. Five indicators with owners, thresholds, and a defined escalation govern. The test of an ethical KPI is naming what happens when it crosses the line.

## See also

- [01_ai_governance_foundations.md](01_ai_governance_foundations.md) - the governance machinery (boards, roles, gates) that keeps these principles enforceable
- [03_bias_and_non_discrimination.md](03_bias_and_non_discrimination.md) - the fairness principle in full depth: bias sources, metrics, mitigation, and the FRIA
- [04_ai_risk_management.md](04_ai_risk_management.md) - robustness and oversight requirements as the AI Act codifies them for high-risk systems
- [10_organizational_policies_and_case_studies.md](10_organizational_policies_and_case_studies.md) - where checklists and KPIs get institutionalized: QMS integration and internal policy design
