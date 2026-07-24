# AI governance foundations

## TL;DR

**AI governance is the system of decision rights, accountability, and controls that keeps AI systems aligned with strategy, law, and acceptable risk across their whole lifecycle. It is not IT governance with new vocabulary.** IT governance (COBIT, ITIL, ISO/IEC 38500) manages systems whose behavior is specified up front; data governance (DAMA-style stewardship, quality, lineage) manages the asset those systems consume; AI governance has to manage software whose behavior is **learned**, shifts with the data, resists inspection, and carries fundamental-rights exposure that a CRM rollout never had. The operating target is **trustworthy AI**: the EU High-Level Expert Group frames it as lawful, ethical, and robust, decomposed into seven requirements from human agency to accountability. Trust is the adoption currency, so this is an economic argument before it is a moral one. The actor map spans regulators (AI Office, national authorities), standards bodies (ISO/IEC SC 42, CEN-CENELEC JTC 21), providers and deployers, and civil society; inside the organization the machinery is an **AI board** with real veto power, a **CDO or CAIO** with mandate and budget, **data stewards** on the domains, and model owners on the first of three lines of defense. Two reference frames anchor the module: the **OECD AI Principles** (2019, updated 2024) supply the values baseline that the AI Act's own definition of an AI system tracks, and the **NIST AI RMF** supplies the operational loop (Govern, Map, Measure, Manage). ISO/IEC 42001 packages both instincts into a certifiable management system.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **AI governance** | Decision rights and accountability over the AI lifecycle | If nobody can block a deployment, there is no governance |
| **IT governance** | COBIT / ITIL / ISO 38500, systems with specified behavior | Change management assumes behavior changes via a ticket |
| **Data governance** | Ownership, quality, lineage of the data asset | Necessary substrate for AI governance, not a substitute |
| **Trustworthy AI** | Lawful, ethical, robust (HLEG), seven requirements | Trust decides adoption; distrust is a market failure mode |
| **AI board / committee** | Cross-functional body gating AI use cases | Recorded approvals and vetoes, not advisory opinions |
| **CDO / CAIO** | Executive owner of data and AI strategy | Accountability without budget and mandate is decoration |
| **Data steward** | Operational custodian of a data domain | First to see quality drift, closest to the source |
| **Three lines of defense** | Run, oversee, assure | Model owners are first line; risk does not own the model |
| **OECD AI Principles** | Values baseline, 2019 updated 2024, 47+ adherents | The AI Act definition of AI system tracks the OECD one |
| **NIST AI RMF** | Govern, Map, Measure, Manage; voluntary | Govern is cross-cutting culture, not a project phase |
| **ISO/IEC 42001** | Certifiable AI management system (AIMS) | The audit-ready wrapper when a client asks for proof |

## What AI governance is, and what it is not

A working definition: AI governance is the set of structures, processes, and controls through which an organization decides **which AI systems to build or buy, under what constraints, with whose accountability, and with what evidence**. The objectives are the classic governance triad adapted to a new object: strategic alignment (AI spend serves business goals), risk control (legal, ethical, operational, reputational exposure stays within appetite), and value assurance (someone can demonstrate the system does what was promised).

The boundary questions with the two neighboring disciplines are where the definition earns its keep:

| Dimension | IT governance | Data governance | AI governance |
|---|---|---|---|
| Object | Systems and services | Data as an asset | Models and the decisions they drive |
| Behavior | Specified, changes via release | Static rules, schemas, policies | Learned, shifts with data and drift |
| Failure mode | Outage, defect, project overrun | Bad quality, silos, breaches | Bias, opacity, harmful decisions at scale |
| Key artifact | Service catalog, change record | Data catalog, lineage, quality SLA | Model inventory, risk class, monitoring evidence |
| Maturity anchor | COBIT, ITIL, ISO 38500 | DAMA-DMBOK, stewardship programs | OECD, NIST AI RMF, ISO 42001, AI Act |

The inheritance is real: AI governance reuses IT change discipline and stands on data governance, because a model is only as governable as the data that trains it. What it adds is the part neither parent handles: behavior that degrades silently without any change request, decisions that touch fundamental rights, and an accountability chain that has to survive the question "why did the model do that" in front of a regulator. Module 07 covered the data side of this house; this module builds the floor above it.

## Trustworthy AI as the operating principle

The EU's framing, from the High-Level Expert Group's Ethics Guidelines (2019), defines trustworthy AI through three properties that must hold simultaneously: **lawful** (complies with applicable rules), **ethical** (respects principles beyond legal minimums), and **robust** (technically and socially sound, because good intentions with fragile engineering still produce harm). The guidelines unpack this into seven requirements: human agency and oversight; technical robustness and safety; privacy and data governance; transparency; diversity, non-discrimination and fairness; societal and environmental well-being; accountability. The list is worth memorizing once, because the AI Act's high-risk requirements are recognizably these seven items converted into legal obligations, and the mapping exercise reappears in every gap analysis.

The reason trust carries this much architectural weight is economic. AI systems are adopted at scale only when users, customers, and regulators extend trust they cannot verify personally; a single visible failure (a discriminatory credit model, a chatbot inventing legal citations) withdraws that trust for the whole category. An ethical and fiduciary posture is therefore not compliance overhead on top of the product: for AI systems it is a load-bearing product feature. Organizations that treat it as paperwork discover the cost difference between building trust and rebuilding it.

## The actor map

Governance is a multi-player game, and the players hold different instruments:

- **Legislators and regulators**: the EU with the AI Act and the enforcement stack around it (Commission's AI Office for GPAI and coordination, national market surveillance authorities, data protection authorities and the European Data Protection Board where GDPR overlaps, the EDPB's Opinion 28/2024 on AI models being the clearest sign the two regimes now read each other). They set binding constraints and hold the sanction lever.
- **Standards bodies**: ISO/IEC JTC 1/SC 42 internationally, CEN-CENELEC JTC 21 for the European harmonized standards that will carry presumption of conformity under the AI Act. They translate legal requirements into testable technical specifications, which makes them quietly powerful: the standard's checklist becomes the de facto law.
- **Providers and deployers**: the regulated parties. The AI Act splits obligations along this axis, so knowing which hat the organization wears per system is the first scoping question of any engagement.
- **Auditors and notified bodies**: the verification layer, internal and external.
- **Civil society and academia**: watchdogs, incident databases, and the research that turns anecdotes into measurable harm categories. They shape enforcement priorities more than their lack of formal power suggests.

The internal actors mirror this structure at company scale, which is the subject of the next section.

## Internal roles: who owns what

The recurring failure in AI governance rollouts is diffuse accountability: everyone is involved, nobody is answerable. The remedy is boring and effective, named roles with explicit decision rights:

- **AI board (or AI governance committee)**: cross-functional (business, legal, risk, security, data science), meets on a cadence, and gates use cases at defined checkpoints: intake, pre-development, pre-deployment, and periodic review. The design test is simple: can this body stop a launch, and has it ever done so? A committee that only advises is furniture.
- **Chief Data Officer / Chief AI Officer**: executive ownership of the data and AI strategy, the model inventory, and the governance budget. The role fails predictably when it carries accountability without authority: responsible for AI risk, but with no headcount and no veto.
- **Data stewards**: domain-level custodians inherited from data governance, responsible for quality, definitions, and access in their slice. In AI programs they gain a second job: attesting that training data for a given use case is fit for purpose, documented, and legally usable.
- **Model owners**: the first-line role that IT governance never needed. A named person per production model, accountable for its performance, monitoring, retraining, and incident response.
- **Data protection officer**: where personal data is in play, the DPO inherited from GDPR owns the data protection impact assessment (DPIA) and the lawful-basis argument, and interlocks with the deployer-side FRIA of note 03 rather than duplicating it. In AI programs the DPO is a governance actor, not a compliance mailbox: the privacy risk and the fundamental-rights risk are one risk seen through two statutes.

Layered over the roles, the **three lines of defense** model ports cleanly from financial services: the first line builds and operates (model owners, data stewards), the second line sets policy and challenges (risk, compliance, the AI board's staff function), the third line independently assures (internal audit). The port matters because it settles turf questions in advance: risk does not own models, and audit does not write policy. A lightweight RACI over the AI lifecycle stages, from intake to retirement, is usually the single most clarifying artifact a governance program produces in its first quarter.

## OECD and NIST AI RMF, a first pass

Two frameworks anchor the international vocabulary, and both return in later notes.

The **OECD AI Principles** (Recommendation adopted 2019, revised 2024, adhered to by 47+ jurisdictions including non-members) supply the values layer: inclusive growth and well-being; human rights and democratic values, including fairness and privacy; transparency and explainability; robustness, security and safety; accountability. Their practical weight comes from adoption, not enforcement: they are the closest thing to a global common denominator, the G20 endorsed them, and the AI Act's definition of an AI system was deliberately aligned with the OECD's revised definition to keep the EU interoperable with the international conversation. When two regulators on different continents agree on anything, it is usually phrased in OECD terms.

The **NIST AI Risk Management Framework** (AI RMF 1.0, January 2023) supplies the operational layer: a voluntary, sector-agnostic method organized in four functions. **Govern** builds the cross-cutting culture, policies, and accountability structures; **Map** establishes context and identifies risks per use case; **Measure** analyzes and tracks them with metrics and testing; **Manage** prioritizes and treats them. Govern is deliberately not a phase but a foundation the other three rotate on, which is the framework's sharpest design choice: risk management fails as a bolt-on activity and works as an operating rhythm. The RMF's companion playbook and the generative AI profile (2024) give it a practical depth the OECD principles do not attempt.

The two are complements, not competitors: OECD tells you what to care about, NIST tells you how to run the loop, and ISO/IEC 42001 wraps the loop in a certifiable management system when the market asks for third-party proof. A governance program needs all three layers; collecting the logos without mapping them to actual controls is how ethics washing starts, which is exactly where the next note picks up.

## Gotchas

- **Running AI governance as IT governance with a thesaurus.** Change management assumes behavior changes through a release. Models drift, degrade, and discriminate without any ticket being filed. Governance that only watches the deployment pipeline misses the failure class that makes AI governance a separate discipline.
- **Mistaking data governance maturity for AI readiness.** Clean, cataloged, well-stewarded data is the substrate, and it says nothing about model opacity, drift, fairness, or accountability for automated decisions. The DAMA program is the ground floor, not the building.
- **Advisory-only AI boards.** A committee without a documented veto, gate checkpoints, and recorded decisions is governance theater. The test is not whether the board exists but whether a launch has ever waited for it.
- **Accountability without authority.** Appointing a CDO or CAIO to own AI risk while giving them no budget, no headcount, and no gate is a way to name a future scapegoat, not to govern. Mandate follows accountability or the role is decorative.
- **Framework collecting.** OECD principles on the website, NIST RMF in a slide deck, ISO 42001 on the roadmap, and no mapping from any of them to concrete controls, owners, and evidence. Frameworks are inputs to a control set, not wall decoration.
- **Waiting for enforcement to justify the machinery.** The AI Act's obligations arrive on a fixed calendar regardless of organizational readiness, and retrofitting governance onto a live model portfolio costs multiples of building it in. The cheapest governance program is the one that starts before the first audit letter.

## See also

- [02_ethics_and_responsible_ai.md](02_ethics_and_responsible_ai.md) - the principles this machinery is supposed to enforce, and what happens when the machinery is missing (ethics washing)
- [04_ai_risk_management.md](04_ai_risk_management.md) - the risk-based logic the governance loop runs on, from the AI Act pyramid to high-risk requirements
- [09_conformity_audit_and_certification.md](09_conformity_audit_and_certification.md) - the external verification layer: conformity assessment, standards, AI Office and Board
- [10_organizational_policies_and_case_studies.md](10_organizational_policies_and_case_studies.md) - the same roles and gates turned into an internal governance framework and QMS integration
