# Conformity, audit and certification

## TL;DR

**Conformity assessment is where the AI Act's promises get cashed: the procedure that converts "we meet Arts 8-15" from a claim into a defensible, marked, registered position.** Two routes exist (Art 43): **internal control** (Annex VI), self-assessment against the requirements, available for most Annex III systems especially when harmonized standards were applied; and the **notified body** route (Annex VII), third-party assessment, mandatory mainly for biometric systems when standards were not fully applied or do not exist. Annex I systems fold into their existing product regimes. The output chain is fixed: assessment, **EU declaration of conformity**, **CE marking**, **registration** in the EU database, and a substantial modification reopens the file. The quiet structural fact: the regime is mostly **self-assessed**, with market surveillance as the backstop, which makes documentation quality the real compliance currency. **Harmonized standards** (CEN-CENELEC JTC 21, leaning on ISO/IEC SC 42) carry a **presumption of conformity** (Art 40): comply with the cited standard and the burden shifts to whoever doubts you; without standards you argue every requirement from first principles, and the standards' lag behind the application dates is the regime's best-known operational risk, with **common specifications** (Art 41) as the Commission's fallback. Institutionally, the **AI Office** supervises GPAI exclusively and produces the templates, codes, and guidance; the **European Artificial Intelligence Board** (member states) keeps 27 national enforcement practices coherent, flanked by an advisory forum and a scientific panel; national **market surveillance authorities** do the domestic policing. In an audit, everything reduces to one behavior: answering "show me" instead of "let me explain", from a living, cross-referenced evidence trail.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **Conformity assessment (Art 43)** | The procedure proving Arts 8-15 are met | Precedes market placement; not a one-time event |
| **Internal control (Annex VI)** | Self-assessment route | The default for most Annex III systems |
| **Notified body (Annex VII)** | Accredited third-party assessment | Biometrics without fully applied standards |
| **Annex I systems** | Assessed inside the existing product regime | The sectoral notified body absorbs the AI file |
| **Declaration + CE + registration** | The fixed output chain of a passed assessment | Missing registration undoes the rest |
| **Substantial modification** | Reopens the conformity file | Retraining that changes intended behavior counts |
| **Presumption of conformity (Art 40)** | Cited harmonized standard = burden shifts | The cheap path, when the standards exist |
| **CEN-CENELEC JTC 21** | Drafts the European AI standards | Leverages ISO/IEC SC 42 where possible |
| **Common specifications (Art 41)** | Commission fallback for late standards | The known risk of the calendar |
| **AI Office** | Commission body; exclusive GPAI supervisor | Also the source of templates, codes, guidelines |
| **European AI Board** | Member state representatives, coherence organ | The anti-fragmentation device, GDPR lesson applied |
| **Market surveillance authority** | National enforcement arm | The regulator a high-risk provider actually meets |
| **Evidence trail** | Living, dated, cross-referenced documents | "Show me" beats "let me explain" in every audit |

## Conformity assessment: the two routes

The assessment answers one question, is this high-risk system compliant with the requirements of Arts 8-15, and the Act provides two procedures for answering it.

**Internal control** (Annex VI) is self-assessment: the provider verifies its own QMS, examines its own technical documentation, and confirms the system's compliance, then signs the declaration. No external party is involved. This is the route for the large majority of Annex III systems, and its availability is broadest when harmonized standards were applied, the standards do the specification work, and the provider demonstrates adherence.

**Notified body assessment** (Annex VII) brings in an accredited third party that examines the QMS and the technical documentation and issues a certificate. Under the Act as adopted, the mandatory perimeter is narrow: essentially **biometric systems** (Annex III point 1) when the provider has not applied harmonized standards in full, or they do not yet exist. The design logic: where the technology is most rights-sensitive and the specification least settled, self-assessment is not enough.

**Annex I systems**, AI as safety components of already-regulated products, do not get a separate AI procedure: the AI requirements ride inside the existing sectoral conformity assessment (a medical device's notified body reviews the AI file with the rest), avoiding double certification of one product.

Whichever route, the output chain is invariant: a passed assessment produces the **EU declaration of conformity** (Art 47, the provider's signed legal statement), the **CE marking** (Art 48, the visible claim), and **registration** in the EU database (Art 49, the public record, including Art 6(3) exemption claims from note 06). A **substantial modification**, a change affecting compliance or intended purpose, reopens the assessment; for learning systems, changes within a pre-declared envelope of continuous learning are carved out of "substantial", which makes that envelope one of the most consequential paragraphs a provider writes in the whole tech file.

The structural honesty the course flags deserves italics in the mind: **this regime is predominantly self-assessed**. No authority pre-approves most high-risk AI; the state's role is surveillance after placement. Which reframes the whole exercise: the assessment's real product is not the CE mark but the **defensibility of the file behind it** on the day market surveillance asks. Self-assessment is not the easy route; it is the route where the provider carries the full evidentiary burden alone.

## Standards and the presumption of conformity

Arts 8-15 are written at the altitude of law ("appropriate level of accuracy", "effective human oversight"), and something has to translate them into testable engineering statements. That something is the harmonized standard.

The mechanics (Art 40): the Commission requests standards from the European standardization organizations; **CEN-CENELEC JTC 21** drafts them, reusing international work from **ISO/IEC JTC 1/SC 42** where it fits (the management-system standard 42001, risk guidance 23894, the data-quality and robustness families); the Commission cites the finished standards in the Official Journal; and from that moment, compliance with the cited standard grants a **presumption of conformity** with the requirements it covers.

The presumption is the whole economy of the regime. With it, the provider's argument is one line: we applied EN standard X, here is the evidence. Without it, every requirement is argued from first principles, bespoke justification, bespoke testing methodology, and a market surveillance officer free to disagree with the methodology itself. The presumption is rebuttable, but it flips the burden: the doubter must show the standard was misapplied or insufficient, rather than the provider showing its homemade approach was adequate. Cheap path versus expensive path, and every serious compliance program is a bet on the cheap one existing in time.

Which is exactly the known problem: **the standards are late relative to the application dates**, a lag structural to standardization (consensus processes measured in years, against a fixed legal calendar). The Act anticipates its own risk with **common specifications** (Art 41): where standards are absent or inadequate, the Commission can adopt technical specifications by implementing act, granting the same presumption. Politically these are the instrument nobody wants used, standards bodies because it displaces them, industry because Commission-drafted specs skip the consensus machinery, but their existence disciplines the timeline.

Note 07's transmission-belt point completes the picture: because JTC 21 builds on SC 42, the specifications that operationalize the AI Act flow into the same international catalog other jurisdictions reference. A provider certified against the European standards holds artifacts that travel, which is the Brussels effect in its most durable form.

## The institutional layer: AI Office, Board, and the national authorities

The Act's institutions answer a question the GDPR answered badly: how does one law stay one law across 27 enforcement systems?

The **AI Office**, established inside the Commission in 2024, holds three jobs. It is the **exclusive supervisor of GPAI models** (the note 08 tier: documentation, codes adherence, systemic-risk duties, with its own fining power), the machinery producer (the training-content summary template, the Code of Practice process, guidelines on definitions and prohibited practices), and the coordination hub for everything cross-border. Centralizing the GPAI layer was the direct lesson of GDPR's one-stop-shop frictions: a dozen frontier providers supervised by one body, not arbitraged across member states.

The **European Artificial Intelligence Board** (the course's "EAIB"; the regulation names it the European Artificial Intelligence Board, Art 65) is the member-state organ: one representative each, advising the Commission and coordinating national practice, issuing opinions and recommendations so that "high-risk" means the same thing in Lisbon and in Helsinki. Around it, an **advisory forum** (Art 67) brings stakeholder input, industry, SMEs, civil society, academia, and a **scientific panel** of independent experts (Art 68) supports the AI Office on GPAI, including a formal power to raise qualified alerts on systemic risks, the institutional home for "the evaluators saw something".

The national layer does the ground enforcement: each member state designates **market surveillance authorities** (policing systems on the market, with the investigation and corrective powers of EU market surveillance law) and a **notifying authority** (accrediting and monitoring the notified bodies). Italy has pointed at AgID and ACN for the respective roles. For a provider of an ordinary high-risk system, the market surveillance authority is the regulator that actually calls; the Brussels bodies set the weather.

The coherence problem is not decorative. GDPR's decade demonstrated how divergent national enforcement fragments a single market regulation into 27 de facto regimes, forum shopping included. The Board-plus-Office architecture, with the GPAI layer fully centralized, is the structural correction, and whether it works is one of the two live bets of the whole regime (the other being the standards calendar).

## Inside an audit: what gets asked

The course's role-play, an audit of a high-risk system's documentation, is worth converting into the checklist the auditor is holding. The request list maps one-to-one onto the obligations, and the mapping is the preparation:

| Requested | Anchor | What "good" looks like |
|---|---|---|
| Technical documentation | Art 11, Annex IV | Complete, current, structured per the annex, not a marketing deck |
| Risk management file | Art 9 | Iterations visible: dated entries, post-market findings feeding back |
| Data governance evidence | Art 10 | Provenance, representativeness analysis, bias examination with results |
| Logs and retention | Arts 12, 19 | Automatic, tamper-evident, retention actually configured |
| Instructions for use | Art 13 | Capabilities, limitations, oversight measures, metrics with conditions |
| Human oversight design | Art 14 | Interface evidence: what the overseer sees, can interrupt, can reverse |
| Accuracy, robustness, security results | Art 15 | Declared metrics, test protocols, per-segment breakdowns, dates |
| QMS documentation | Art 17 | Procedures with owners, records proving the procedures run |
| Declaration, CE, registration | Arts 47-49 | Consistent identifiers across all three |
| Post-market monitoring plan | Art 72 | A plan with data actually flowing, not a template |
| Incident register and reports | Art 73 | Register maintained even if empty; clock discipline visible |

The audit dynamics matter more than the list. Three behaviors separate a clean audit from a long one:

- **Evidence over assertion.** Every "we do X" invites "show me the record of X happening". Procedures without records read as fiction; the record is the compliance.
- **Living documents over snapshots.** Timestamps tell the story note 04 warned about: a risk file untouched since release, for a system in production for a year, is self-incriminating regardless of content quality. Auditors read metadata before they read prose.
- **Cross-referenced consistency.** The risk file cites the test report, the test report cites the dataset sheet, the instructions for use quote the same metrics the Art 15 results contain. Documentation written in one heroic pre-audit sprint fails exactly here, internal contradictions between documents that were never meant to be read side by side.

The role-play's real lesson generalizes past the Act: an audit is a conversation with your own past discipline. Organizations that produce evidence as a byproduct of working (the QMS point of note 10) walk through; organizations that produce evidence as a genre of creative writing get found, because inconsistency is cheap to detect and impossible to retrofit away.

## Gotchas

- **Reading self-assessment as the easy route.** Internal control means no third party checks your work before market, and market surveillance checks it after, with hindsight and penalties. The evidentiary burden is higher, not lower; the notified body you skipped was also a rehearsal.
- **Treating conformity as an event.** Substantial modifications reopen the file, and for learning systems the pre-declared change envelope decides what counts. An MLOps pipeline that retrains weekly needs the conformity architecture designed around that fact, not discovered by it.
- **Building bespoke compliance while the standard exists.** Once a harmonized standard is cited, a homemade methodology forfeits the presumption and invites methodological debate with the authority. Track JTC 21's pipeline as an engineering dependency, because it is one.
- **Betting the calendar on the standards arriving.** The lag is real and known; common specifications are the fallback, not a rescue. Programs that need the cheap path by a fixed date carry the expensive path as contingency or carry schedule risk silently.
- **Ignoring the institutional split.** GPAI questions go to the AI Office; system questions go to the national market surveillance authority; consistency questions percolate through the Board. Sending the right argument to the wrong body wastes the one first impression.
- **Preparing the audit instead of the evidence.** A documentation sprint before the inspection produces internally inconsistent artifacts with identical creation dates, the single most legible signature of retrofitted compliance. The only preparation that works is the boring one, running the QMS all along.

## See also

- [04_ai_risk_management.md](04_ai_risk_management.md) - the Arts 8-15 substance this procedure verifies, and the living risk file the auditor reads first
- [06_ai_act.md](06_ai_act.md) - the provider obligation map the assessment sits inside: declaration, CE, registration, role switches
- [08_generative_ai_gpai_and_copyright.md](08_generative_ai_gpai_and_copyright.md) - the parallel GPAI supervision track: AI Office, Code of Practice, systemic-risk duties
- [07_international_compliance.md](07_international_compliance.md) - why the standards channel is the Brussels effect's strongest export route
- [10_organizational_policies_and_case_studies.md](10_organizational_policies_and_case_studies.md) - the QMS and incident machinery that generate the evidence this note's audit consumes
