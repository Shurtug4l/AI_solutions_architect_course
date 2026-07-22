# Organizational policies and case studies

## TL;DR

**This is where the module lands: the regulation stops being a text and becomes procedures, policies, and a framework someone in the organization actually runs.** The integration point is the **QMS** (Art 17): a documented system covering compliance strategy, design control, data management, risk management, post-market monitoring, incident handling, and accountability, built by **extending the management systems the organization already has** (ISO 9001, 27001, and 42001 as the AI-specific layer) rather than erecting a parallel silo; the article itself scales with organization size, and financial institutions fold it into their sectoral governance. **Regulatory learning** runs both ways: sandboxes (Art 57, at least one per member state by 2026-08-02) and real-world testing (Art 60) let providers de-risk under supervision while regulators learn where the rules bind badly, with the Act's own review clauses as the feedback loop. The **sanctions system** (Art 99) prices non-compliance in three tiers: 35M EUR or 7 percent of worldwide turnover for prohibited practices, 15M or 3 percent for most obligations, 7.5M or 1 percent for misleading authorities, with the SME proportionality flip (lower of the two) and Commission-levied GPAI fines. Organizational case studies converge on a short list of lessons: inventory before committee, pilot before framework, procurement as a governance gate, and policy without enforcement as the universal failure mode. The **serious-incident policy** operationalizes Art 73's clocks (15 days standard, 10 for death, 2 for critical-infrastructure disruption, all starting at awareness), which makes internal detection and escalation speed the real compliance parameter. The closing exercise assembles the whole module into one **internal governance framework**: policy, intake and triage, lifecycle gates, inventory, three lines of defense, AI literacy (Art 4, live since February 2025 and routinely forgotten), KPIs, and an annual review that keeps the thing alive.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **Art 17 QMS** | Documented policies, procedures, records for the AI lifecycle | Proportionate to size; extend the QMS you have, not a new silo |
| **ISO 42001 fit** | The certifiable AI management layer over 9001/27001 | One integrated audit trail instead of three |
| **Regulatory sandbox (Art 57)** | Supervised environment, one per member state by 2026 | Guidance in writing, participation evidence counts |
| **Real-world testing (Art 60)** | Pre-market testing outside sandboxes, conditioned | Plan, registration, informed consent, withdrawal right |
| **Regulatory learning** | Rules adjust on evidence: reviews, guidance, delegated acts | The Act is a process, not a snapshot |
| **Sanction tiers (Art 99)** | 35M/7%, 15M/3%, 7.5M/1% | Prohibitions, obligations, lying to authorities |
| **SME flip** | For SMEs the lower of amount and percentage applies | Proportionality made arithmetic |
| **Serious incident (Art 3(49))** | Death, serious harm, infrastructure disruption, rights infringement | The definition decides what starts the clock |
| **Art 73 clocks** | 15 days standard, 10 death, 2 critical infrastructure | All from awareness, initial report may be incomplete |
| **Inventory-first** | You govern what you can list | Shadow AI discovery precedes every real program |
| **Policy without enforcement** | The universal governance failure mode | A rule nobody checks is a suggestion with a logo |
| **Art 4 AI literacy** | Staff competence duty, live since 2025-02-02 | The obligation most programs forget they carry |

## Folding compliance into the QMS

Art 17 requires high-risk providers to run a quality management system: written policies, procedures, and instructions covering, among the listed items, the regulatory compliance strategy, design and development control, data management, the Art 9 risk process, post-market monitoring, incident reporting, communication with authorities, record keeping, resource management, and an accountability framework assigning responsibilities. Read as a list it looks like a bureaucratic mountain; read structurally it is one sentence: **the organization must be able to show, with records, that its AI lifecycle runs on defined, owned procedures.**

The architectural decision that determines whether this costs a little or a lot: **integrate, do not duplicate**. Most organizations subject to Art 17 already run management systems, ISO 9001 for quality, ISO/IEC 27001 for information security, sectoral regimes in finance and medical. Each Art 17 item lands on an existing hook: design control extends the 9001 development procedures, data management extends the module 07 governance program, incident reporting extends the security incident process with new clocks and a new recipient. **ISO/IEC 42001** exists precisely as the AI-specific management layer that composes with the others, and an integrated audit trail beats three parallel ones on cost, consistency, and credibility. Building a standalone "AI compliance QMS" next to the corporate QMS produces the document-drift problem note 09 described, twin procedures that contradict each other by the second revision.

Two proportionality valves are written into the article: the QMS scales with the provider's size (a startup's Art 17 is a binder, not a department), and financial institutions may discharge it through their existing sectoral governance, an explicit anti-duplication clause. The operating principle underneath is the one the audit note ended on: a QMS is not the documents, it is the habit of producing evidence as a byproduct of working. The documents are what the habit leaves behind.

## Regulatory learning: sandboxes and real-world testing

The Act treats its own imperfection as a design input, and builds mechanisms for rules and reality to inform each other.

**Regulatory sandboxes** (Art 57): controlled frameworks where providers develop and test systems under the supervision and guidance of the competent authority, with every member state required to have at least one operational by 2026-08-02 (Spain moved earliest, with a dedicated agency). The exchange is explicit: the provider gets authoritative guidance in writing, reduced enforcement uncertainty (authorities cannot fine what they supervised in good faith inside the sandbox), and an exit report whose documentation counts toward demonstrating conformity; the regulator gets ground truth about how the rules behave against real systems. **Real-world testing** (Art 60) extends the idea outside sandbox walls: high-risk systems may be tested in real conditions before conformity assessment, gated by a plan, registration, informed consent of participants, the right to withdraw, and monitoring. SMEs get priority access and reduced costs (Art 62), the innovation-side counterweight to the compliance burden.

The other direction of learning is the Act's own metabolism: annual Commission review of the Annex III list and the prohibitions, delegated acts to adjust technical thresholds (the 10^25 FLOPs dial from note 08), guidance and codes filling gaps between revisions. The practical consequence for a compliance function: the AI Act is a **process to track, not a text to file**. A program calibrated to the 2024 text and never revisited will be quietly wrong within two revision cycles.

The strategic reading of sandboxes deserves one more sentence, because it is the consulting insight of the section: for a company facing a genuinely novel use case, the sandbox converts regulatory uncertainty (unbounded, unpriceable) into a supervised process with written answers. That trade is almost always worth the transparency it costs, and early participants additionally shape the guidance everyone else will live under.

## The sanctions system

Art 99 prices non-compliance in three tiers, each "up to" the higher of a fixed amount and a share of total worldwide annual turnover:

| Violation | Ceiling |
|---|---|
| Prohibited practices (Art 5) | 35M EUR or 7% of worldwide turnover |
| Most other obligations (provider, deployer, importer, distributor, notified body duties) | 15M EUR or 3% |
| Supplying incorrect, incomplete, or misleading information to authorities | 7.5M EUR or 1% |

Three design features carry the meaning. The top tier **exceeds the GDPR's** (20M/4%), a deliberate signal about where the EU now prices the worst AI conduct. For **SMEs and startups**, each tier applies as the **lower** of the amount and the percentage, proportionality made arithmetic rather than rhetorical. And the third tier criminalizes the cover-up separately from the crime: lying to the authority is its own violation, which converts every information request into a moment where the cheap option is honesty. Enforcement is national (market surveillance authorities, with member states setting procedural rules) except for GPAI providers, whom the Commission fines directly, up to 15M or 3 percent (Art 101).

The fine is also not the cost model. Market surveillance powers include forced withdrawal, recall, and prohibition of systems, which for a deployed product is usually worth more than the fine; procurement exclusion and contractual liability cascade from findings; and the reputational repricing of a public enforcement action against an "AI company" has no ceiling written anywhere. The board-level summary: the sanction system exists to make non-compliance a quantifiable business risk, and it succeeds, the numbers are designed to survive translation into any risk register (the same design logic module 09 noted for NIS 2).

## What organizational case studies teach

Across corporate AI governance builds, the same patterns recur often enough to state as findings.

**What works:**

- **Inventory first.** Every effective program starts by discovering what AI is actually running, and the discovery reliably surprises: shadow AI (unapproved tools, embedded vendor models, spreadsheet-adjacent scripts nobody classified) outnumbers the official portfolio. Governance without an inventory is jurisdiction without territory.
- **Pilot depth before framework breadth.** One high-stakes use case taken end-to-end (classification, risk file, gates, monitoring, the whole apparatus) teaches more than a company-wide policy rollout, and produces the internal case study that sells the rest.
- **Procurement as a gate.** Most organizations' AI arrives through vendors, so contract clauses (documentation duties, Art 25 role clarity, incident cooperation, audit rights) govern more systems than any internal review board. The buying process is the control point with existing teeth.
- **An executive sponsor with budget.** Note 01's accountability-without-authority failure, resolved in advance.

**What fails, predictably:**

- **Committee before content.** A governance board convened before inventory and policy exist generates opinions without objects, and burns executive attention on abstractions.
- **Policy without enforcement mechanism.** A published AI policy with no gate, no checker, and no consequence is a suggestion with a logo; the case studies' single most universal finding.
- **Tooling before process.** Governance platforms bought to "solve compliance" before the process they should instrument exists, automating a vacuum.
- **The one-time mapping.** Regulation mapped to controls once, at program launch, then shelved while the regulation metabolized (previous section) and the model portfolio turned over.

The synthesis: successful programs are **incremental, evidence-producing, and anchored to existing machinery** (SDLC gates, procurement, the QMS above); failed ones are declarative, parallel, and event-shaped.

## An internal policy for serious incidents

Art 73 obliges providers of high-risk systems to report **serious incidents**, defined (Art 3(49)) as incidents or malfunctions directly or indirectly leading to death or serious harm to health, serious and irreversible disruption of critical infrastructure management, infringement of fundamental-rights obligations under Union law, or serious harm to property or the environment. The clocks all start at **awareness**: immediately and no later than 15 days for the general case, no later than 10 days for death, no later than 2 days for widespread infringement or critical-infrastructure disruption, with an initial incomplete report explicitly permitted and followed up. Deployers who detect a serious incident inform the provider; the provider owns the authority-facing report, plus investigation and corrective action, without prejudice to market surveillance.

An internal policy that makes those clocks survivable has a known anatomy:

- **Definitions and classification matrix.** Art 3(49) translated into the organization's own severity ladder, with worked examples per product line, because the person triaging at 2 a.m. needs examples, not article numbers.
- **Detection channels, enumerated.** Monitoring alerts, user reports, deployer notifications, support tickets, red-team findings: each mapped to where it enters the process. The clock argument makes this the load-bearing section: reporting deadlines run from awareness, so the compliance parameter is actually **time-to-awareness plus time-to-escalation**, both internal properties the policy controls.
- **Triage and escalation.** Severity levels with response times, a named on-call chain, and the explicit rule for when the clock is deemed started.
- **The reporting decision.** Who determines notifiability, with legal sign-off, against a bias-to-report default: the third sanction tier prices under-reporting discovered later far above over-reporting now.
- **Corrective action and root cause.** The Art 20 duties (correct, withdraw, recall, inform deployers and authorities) wired to the incident, and findings fed back into the Art 9 risk file, closing note 04's loop.
- **The register and the drill.** Every incident and near-miss recorded (an empty register maintained is evidence; an absent one is a finding), and the policy exercised via tabletop before reality exercises it first.

One structural warning: a single event can be simultaneously an AI Act serious incident (15 days, market surveillance), a GDPR personal data breach (72 hours, the DPA), and a NIS 2 incident (CSIRT, without delay). Three regimes, three clocks, three recipients, one underlying failure: the policy must route one incident to all applicable tracks from a single intake, or the fastest clock will be discovered expired.

## Designing the internal governance framework

The closing exercise assembles every note in the module into one artifact. A blueprint that holds together:

- **AI policy** at the top: scope, principles (note 02), risk appetite, and the non-negotiables, one page the board signed.
- **Intake and triage**: every proposed use case enters through one funnel and receives a risk classification aligned to the AI Act procedure (note 06), plus the org's own dimensions (data sensitivity, autonomy, audience). The Art 6(3) documentation duty lives here.
- **Lifecycle gates**: design review, pre-deployment review, periodic re-review, run by the AI board with recorded decisions and real veto (note 01), consuming the artifacts the QMS produces (this note) and producing the evidence conformity needs (note 09).
- **The inventory as backbone**: every system, its risk class, owner, review dates, and monitoring status, the single source the KPIs (note 02), the audits, and the incident process all key on.
- **Three lines of defense** staffing the whole thing: model owners and stewards first, risk and compliance second, internal audit third (note 01).
- **AI literacy** (Art 4): providers and deployers must ensure sufficient AI literacy of staff dealing with AI systems, an obligation live since 2025-02-02 and absent from most programs' checklists; role-tiered training with records, because records are what the verb "ensure" audits as.
- **Metrics and review**: the KPI set with owners and thresholds, board reporting on a cadence, and an annual framework review wired to the regulatory-learning tracker, because both the portfolio and the law will have moved.

Right-sizing is the last discipline: the startup version is the same skeleton at binder scale (one policy, one intake form, one gate, one spreadsheet inventory, quarterly review), and inflating it to enterprise ceremony kills adoption faster than any gap. The framework's quality test mirrors the module's opening question about governance itself: not whether the diagram is complete, but whether a real deployment has ever been changed, delayed, or stopped by it. A framework that has never said no is decoration; the whole module has been the argument for why it must be able to.

## Gotchas

- **Building the AI QMS as a parallel silo.** Twin procedures drift into contradiction and double the audit surface. Art 17 items map onto 9001/27001/42001 hooks the organization already runs; integration is the cheap and the credible path, and the article's own proportionality language endorses it.
- **Treating the sandbox as a startup perk.** It is a risk instrument: written regulatory guidance against a novel use case is uncertainty conversion no legal memo matches, and exit documentation counts toward conformity. The cost is transparency with the authority, which the enforcement-shy systematically overprice.
- **Reading the fine ceilings as the cost of non-compliance.** Withdrawal, recall, procurement exclusion, and reputational repricing routinely exceed the fine, and the misleading-information tier makes the cover-up separately billable. Price the scenario, not the statute.
- **Convening the committee before the inventory.** Governance without a registry of what it governs produces opinions, not decisions, and spends the executive sponsorship the real program will need later.
- **Writing the incident policy around the authority's clock.** The 15-2-10 deadlines run from awareness; the controllable variables are detection and escalation speed. A policy that perfects the report template while support tickets take nine days to reach the right desk has optimized the wrong latency.
- **Forgetting Art 4.** AI literacy has been a live obligation since February 2025, it covers deployers as well as providers, and it is verified through training records. It is the cheapest finding an authority will ever write against an otherwise mature program.

## See also

- [01_ai_governance_foundations.md](01_ai_governance_foundations.md) - the roles, board, and three-lines structure this framework staffs and formalizes
- [02_ethics_and_responsible_ai.md](02_ethics_and_responsible_ai.md) - the principles, checklists, and KPI machinery the gates and metrics operationalize
- [04_ai_risk_management.md](04_ai_risk_management.md) - the Art 9 loop the incident register and post-market data feed back into
- [06_ai_act.md](06_ai_act.md) - the classification procedure the intake funnel implements, and the obligation map the gates enforce
- [09_conformity_audit_and_certification.md](09_conformity_audit_and_certification.md) - the audit that consumes this note's evidence, and the institutions behind the sanction letters
