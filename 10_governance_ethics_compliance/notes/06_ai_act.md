# The AI Act

## TL;DR

**The AI Act (Regulation (EU) 2024/1689) is a hybrid: the enforcement machinery of European product safety law, loaded with a fundamental rights payload.** From product law it takes CE marking, conformity assessment, harmonized standards, market surveillance, and the vocabulary of placing on the market; from rights law it takes what the machinery protects, not just health and safety but non-discrimination, privacy, and human dignity. It is a **regulation** (directly applicable, no transposition) and **horizontal** (all sectors), with extraterritorial reach: it catches non-EU providers whose systems, or whose systems' **outputs**, are used in the EU. The four-tier pyramid from note 04 gets its legal teeth here: **Art 5 prohibitions** (manipulation, exploitation of vulnerability, social scoring, predictive policing on profiling alone, untargeted face scraping, emotion recognition at work and school, sensitive biometric categorization, real-time remote biometric ID with narrow law-enforcement exceptions) applying since 2025-02-02 at the top penalty tier; **high-risk** via two routes (Annex I safety components, Annex III listed areas) with the **Art 6(3) exceptions** for narrow procedural or preparatory tasks, killed automatically by profiling and requiring documented, registered justification; **deepfakes** handled as a transparency problem (Art 50: machine-readable marking by providers, disclosure by deployers, with an art-and-satire accommodation), not a ban. The provider obligation map (Art 16 and neighbors) sequences the lifecycle: QMS, technical documentation, conformity assessment, CE mark, registration, then post-market monitoring, incident reporting, and corrective action. Classification is therefore a documented procedure, not an intuition, and misclassification is itself an enforceable error.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **Hybrid regulation** | Product safety machinery + fundamental rights payload | CE marking logic applied to discrimination risk |
| **Regulation, horizontal** | Directly applicable, all sectors | One text, no national transposition to reconcile |
| **Extraterritorial reach** | Catches non-EU providers if output is used in EU | Serving the EU from abroad does not exit the scope |
| **Staggered application** | 2025-02-02 prohibitions; 2025-08-02 GPAI; 2026-08-02 general | Compliance calendar, not a single deadline |
| **Art 5 prohibitions** | Practices banned outright, top penalty tier | 35M EUR or 7% of turnover, whichever is higher |
| **Annex I route** | Safety component of regulated products | Medical devices, machinery, vehicles: high-risk by attachment |
| **Annex III route** | Eight listed areas of use | Employment, credit, education, law enforcement, migration, ... |
| **Art 6(3) exceptions** | Annex III but no significant risk: narrow tasks | Profiling of natural persons kills the exemption, always |
| **Documented derogation** | Exemption claims are assessed, written, registered | An undocumented exemption is a misclassification finding |
| **Deepfake rule (Art 50)** | Transparency, not prohibition | Provider marks machine-readably, deployer discloses |
| **Art 16 map** | The provider's master obligation list | QMS, docs, assessment, CE, registration, post-market |
| **Role switch (Art 25)** | Rebrand, modify, or repurpose and become the provider | White-labeling a model imports its full obligation set |

## A hybrid regulation: product safety machinery, fundamental rights payload

The Act's designers had a choice of chassis and picked the **New Legislative Framework**, the EU's product safety architecture: economic operators (provider, importer, distributor, deployer), conformity assessment before market access, harmonized standards giving presumption of conformity, CE marking as the visible attestation, market surveillance authorities policing after the fact. Everything about how the Act operates is recognizable to anyone who has shipped a medical device or a machine.

What makes it a hybrid is what the machinery protects. Classic product law guards health and safety; the AI Act adds **fundamental rights** as a protected interest of the same rank, which is why a CV screener with flawless uptime can be non-conforming for discriminatory outcomes, and why an impact assessment on rights (the FRIA of note 03) sits inside a product safety law at all. The marriage is pragmatic: rights litigation is slow and individual, product law is ex ante and systemic, so the Act uses the second to prevent the harms the first would only compensate.

Three structural facts complete the frame. It is a **regulation**, not a directive: directly applicable in every member state, no transposition drift (the NIS 2 contrast from module 09 is instructive). It is **horizontal**: one rulebook across sectors, with sectoral law layered on top where it exists. And its **reach is extraterritorial** by design: it binds providers placing systems on the EU market wherever established, and even providers and deployers in third countries when the system's output is used in the EU, a clause written specifically to prevent offshoring the inference while keeping the European customer.

The obligations arrive on a **staggered calendar**: entry into force 2024-08-01; prohibitions and AI literacy duties from 2025-02-02; GPAI rules, governance bodies, and penalties from 2025-08-02; the bulk of high-risk obligations from 2026-08-02; Annex I embedded systems from 2027-08-02. As of mid-2026, the prohibitions and GPAI tiers are live and the general regime is weeks away, which reframes every "we will look at it later" in a project plan.

## Prohibited practices: the unacceptable tier

Art 5 bans practices, not technologies, and the list rewards precise reading because each item carries qualifiers that decide real cases:

- **Manipulation**: subliminal or purposefully manipulative techniques that materially distort behavior and cause (or are reasonably likely to cause) significant harm.
- **Exploitation of vulnerability**: same distortion-and-harm structure, targeting age, disability, or social and economic situation.
- **Social scoring**: evaluating people over time on social behavior or personal characteristics, where the score leads to detrimental treatment in unrelated contexts or disproportionate to the behavior. Written against the general-purpose citizen score; sectoral creditworthiness assessment lands in high-risk instead.
- **Predictive policing on profiling alone**: assessing the risk that an individual commits a crime based solely on profiling or personality traits. Supporting a human assessment grounded in objective facts is outside the ban.
- **Untargeted face scraping**: building or expanding facial recognition databases by indiscriminate harvesting from the internet or CCTV.
- **Emotion recognition** in workplaces and educational institutions, save medical and safety purposes.
- **Biometric categorization** to infer race, political opinions, trade union membership, religious beliefs, sex life, or sexual orientation from biometric data.
- **Real-time remote biometric identification** in publicly accessible spaces for law enforcement: prohibited as a rule, with narrow, exhaustively listed exceptions (targeted search for victims, imminent threat to life, perpetrators of listed serious crimes), each gated by prior authorization and safeguards.

Two readings matter in practice. First, the qualifiers are the law: "untargeted", "solely", "significant harm", "unrelated context" are where every borderline case is argued, and the Commission's 2025 guidelines on prohibited practices exist because those words needed forty pages of unpacking. Second, the tier is enforced at the maximum penalty level (35M EUR or 7% of worldwide turnover), and it has applied since February 2025: this is the one part of the Act where "still preparing" was never an available posture.

## High-risk classification and the Art 6(3) exceptions

High-risk status arrives by two routes. **Annex I**: the system is a product, or the safety component of a product, covered by listed EU harmonization law (machinery, medical devices, vehicles, toys, lifts, and so on) and subject to third-party conformity assessment there; the AI Act attaches to the existing product regime. **Annex III**: the system is used in one of eight listed areas: biometrics (where not prohibited); critical infrastructure; education and vocational training; employment and worker management; access to essential private and public services (including creditworthiness assessment, life and health insurance risk pricing, benefit eligibility, emergency dispatch); law enforcement; migration, asylum and border control; administration of justice and democratic processes.

The list is deliberately use-based, which creates the over-inclusion problem Art 6(3) exists to fix: not everything touching an Annex III area threatens anyone. An Annex III system is **not** high-risk where it poses no significant risk to health, safety, or fundamental rights because it is limited to:

- performing a **narrow procedural task**;
- **improving the result** of a previously completed human activity;
- **detecting decision-making patterns or deviations**, without replacing or influencing the human assessment absent proper review; or
- performing a **preparatory task** to an assessment relevant to the listed use.

One override sits above all four: a system that performs **profiling of natural persons** is high-risk regardless. And the exemption is procedural, not self-serve: the provider documents the assessment **before** placing the system on the market, keeps it available for authorities, and registers the system in the EU database. Claiming the exception in an architecture meeting and writing nothing down is not a classification, it is a finding scheduled for later; market surveillance can disagree, and misclassification carries its own penalties.

The pattern to internalize: a document-summarization service inside an HR suite plausibly rides the narrow-procedural exemption; a tool that ranks the same CVs is profiling and there is no exit. The distance between the two is one product feature and the whole compliance regime.

## Deepfakes: transparency, not prohibition

The Act's answer to synthetic media is disclosure, split across the value chain in Art 50. **Providers** of systems generating synthetic audio, image, video, or text must ensure outputs are **marked in machine-readable format** and detectable as artificially generated, with the marking effective, interoperable, and robust as far as technically feasible: in practice watermarking, embedded metadata, and provenance standards of the C2PA family, none of which survives adversarial laundering perfectly, which is exactly why the law says "technically feasible" rather than promising detection. **Deployers** of deepfakes (content resembling real persons, places, or events that would falsely appear authentic) must **disclose** the artificial generation or manipulation; for evidently artistic, creative, or satirical work the disclosure need only avoid hampering the display of the work, an accommodation that keeps parody legal without exempting it. AI-generated text published to inform the public on matters of public interest carries its own disclosure duty unless a human exercised editorial control and someone bears responsibility for the publication.

Two framing points. The tier is transparency: a labeled deepfake is lawful under the AI Act, and whatever else it violates (defamation, image rights, electoral law) belongs to other statutes. And the architecture bets on **provenance over detection**: post-hoc detectors are losing the arms race, so the obligation attaches at generation time, where marking is cheap and coverage is structural. The bet only pays if marking becomes ubiquitous, which is the actual policy gamble behind Art 50, worth watching rather than assuming.

## The provider obligation map

Art 16 is the master list for high-risk providers; laid on the product lifecycle it reads as a sequence, each step producing evidence the next consumes:

| Phase | Obligation | Anchor | Artifact |
|---|---|---|---|
| Design and build | Meet the substantive requirements | Arts 8-15 | Risk file, data governance records, logs (note 04) |
| Organize | Quality management system | Art 17 | QMS documentation (note 10 for integration) |
| Document | Technical documentation | Art 11, Annex IV | The tech file an authority reads first |
| Verify | Conformity assessment | Art 43 | Internal control or notified body route (note 09) |
| Declare | EU declaration of conformity, CE marking | Arts 47-48 | Signed declaration, visible marking |
| Register | EU database entry | Art 49 | Public registration, including Art 6(3) claims |
| Identify | Name and contact on the system; EU authorized representative for non-EU providers | Art 22 | Accountability has an address |
| Operate | Post-market monitoring plan | Art 72 | Living monitoring file feeding the Art 9 loop |
| React | Serious incident reporting; corrective actions; cooperation | Arts 73, 20-21 | Incident reports on the clock (note 10), recalls, notifications |
| Retain | Logs under provider control | Art 19 | Retention appropriate to purpose, minimum six months |

Around the provider, the value chain carries its own duties: importers and distributors verify conformity markings and documentation before selling, and **Art 25** springs the trap non-lawyers miss most often: a deployer, importer, or distributor that puts its name on a high-risk system, substantially modifies one, or repurposes a non-high-risk system into high-risk use **becomes the provider**, inheriting the entire table above. White-labeling a vendor's model is not a branding decision, it is an assumption of regulatory identity.

## Determining the risk category: a working procedure

The classification exercise runs the same decision path every time; the discipline is executing it in order and writing down each answer:

```
  0. AI system at all? (Art 3(1): machine-based, infers from
     input how to generate output, varying autonomy)
        no -> out of scope (still check GDPR etc.)
  1. Prohibited practice? (Art 5 list, read the qualifiers)
        yes -> stop: cannot be placed on the market
  2. Safety component under Annex I law?
        yes -> high-risk, attached to the product regime
  3. Annex III area?
        no -> tier 3/4: check Art 50 transparency, then minimal
        yes -> 4. Art 6(3) exception arguable?
                 profiling involved? -> high-risk, no exit
                 narrow/preparatory task -> document, register,
                                            treat as exempt
  5. GPAI model in the stack? -> separate track (note 08)
```

Worked contrast, the kind the course simulation trades in. A **CV-ranking system** for hiring: AI system, not prohibited, no Annex I hook, squarely Annex III employment, and it profiles natural persons, so Art 6(3) is unavailable: high-risk, full provider map applies. A **customer-support chatbot** answering product FAQs: no Annex III area, minimal risk, but Art 50 requires disclosing that the user is talking to a machine. Between the poles live the honest hard cases (an emergency-call triage assistant, an exam-proctoring add-on), and for those the procedure's value is not producing certainty but producing a **defensible, documented reasoning trail** at classification time, because the borderline call will be reviewed by someone with hindsight and enforcement powers.

## Gotchas

- **Classifying the technology instead of the use.** The same model is minimal risk in one deployment and high-risk in the next. Any internal registry that assigns risk classes to models rather than to systems-in-context is answering the wrong question, note 04's point, now with legal consequences attached.
- **Treating Art 6(3) as self-service.** The exemption exists, and it is a documented, registered, challengeable legal position, not a checkbox. Profiling kills it outright, and an authority that finds the assessment missing has found two violations, the misclassification and the missing paperwork.
- **Forgetting the calendar is staggered.** Prohibitions have applied since 2025-02-02 and GPAI duties since 2025-08-02; a compliance program aimed entirely at the 2026-08-02 general date is already late for two tiers.
- **Reading the deepfake rule as a ban.** Art 50 is a transparency obligation; lawfulness questions about the content itself live in other law. Conversely, marking does not launder a defamatory fake: both regimes apply, on different questions.
- **White-labeling without reading Art 25.** Put your brand on it, modify it substantially, or repurpose it into Annex III territory, and you are the provider, with the QMS, the tech file, and the incident duties. The contract with the original vendor does not transfer the obligations back.
- **Assuming extraterritoriality has gaps.** Output used in the EU pulls in providers and deployers established anywhere. Serving European users from a non-EU entity changes the enforcement mechanics, not the applicability.

## See also

- [04_ai_risk_management.md](04_ai_risk_management.md) - the substantive high-risk requirements (Arts 8-15) this note's obligation map wraps in process
- [03_bias_and_non_discrimination.md](03_bias_and_non_discrimination.md) - the FRIA and the discrimination exposure that explains most of Annex III
- [08_generative_ai_gpai_and_copyright.md](08_generative_ai_gpai_and_copyright.md) - the GPAI track that runs parallel to the risk pyramid, including systemic-risk models
- [09_conformity_audit_and_certification.md](09_conformity_audit_and_certification.md) - conformity assessment routes, harmonized standards, and the institutions behind CE marking
- [07_international_compliance.md](07_international_compliance.md) - how this regulation travels: the Brussels effect and the OECD-aligned definition
