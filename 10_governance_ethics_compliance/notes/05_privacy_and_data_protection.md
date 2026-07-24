# Privacy and data protection

## TL;DR

**The GDPR is the regulation that already bites: while AI Act enforcement ramps up on its staggered calendar, every AI system touching personal data has been fully regulated since 2018, and data protection authorities have not waited for anyone.** The two regimes have different objects: the GDPR governs **processing of personal data** with any technology, the AI Act governs **AI systems** with any data; the overlap, AI processing personal data, is where most interesting systems live. Roles do not map one-to-one: provider and deployer (AI Act) versus controller and processor (GDPR) must be assessed separately, per processing activity. For AI training, the realistic **legal bases** reduce to consent (impractical at scale, withdrawal poisons the pipeline) and **legitimate interest**, which stands or falls on a documented three-step **balancing test**: purpose, necessity, balancing with safeguards. The EDPB's Opinion 28/2024 confirmed the path exists and is conditional. **Privacy by design** (Art 25) translates into ML practice as minimization at collection, pseudonymization before training, retention schedules on snapshots, and formal techniques (differential privacy, federated learning) each with real costs. The hardest collision is the **right to erasure versus trained weights**: models memorize, deleting from the corpus does not delete from the model, retraining is the only complete remedy and rarely a proportionate one. The operational answer layers source deletion, unlearning where it matures, output suppression, and honest documentation of what each layer does and does not achieve; for RAG systems, deleting from the retrieval index is real, cheap erasure of the operational path.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **GDPR x AI Act** | Different objects, full parallel application | AI Act compliance never absorbs or replaces GDPR duties |
| **Roles mapping** | Provider/deployer vs controller/processor, assessed separately | The deployer is usually a controller; the provider varies per activity |
| **Art 22 GDPR** | No solely automated decision with significant effects | Human intervention right, predating and complementing Art 14 AI Act |
| **DPIA vs FRIA** | Data processing risk vs fundamental rights impact | Overlapping content, complementary instruments (Art 27(4)) |
| **Legal bases (Art 6)** | Six options; training realistically runs on two | Consent or legitimate interest; contract is narrower than assumed |
| **Special categories (Art 9)** | Stricter regime, explicit consent or narrow exceptions | Inferring sensitive attributes is itself sensitive processing |
| **Legitimate interest** | The workhorse basis, conditional on a documented LIA | Purpose, necessity, balancing; safeguards tip the scale |
| **EDPB Opinion 28/2024** | Model anonymity case-by-case; LI viable with conditions | Unlawful training can taint downstream deployment |
| **Privacy by design (Art 25)** | Protection built into the pipeline, default-on | Minimization decided at collection, not at audit time |
| **Anonymization vs pseudonymization** | Only the first exits the GDPR, and it is hard | Re-identification risk makes most "anonymous" datasets pseudonymous |
| **Erasure vs weights** | Deleting from the corpus does not delete from the model | Memorization is demonstrated; retraining is the only full remedy |
| **RAG erasure** | Deleting from the index removes the operational path | The cheapest honest erasure a deployer can actually execute |

## Two regulations, one system: GDPR meets the AI Act

The cleanest way to hold the two regimes in one head: the GDPR regulates an **activity** (processing personal data), the AI Act regulates an **artifact** (an AI system placed on the market or put into service). Neither displaces the other, and the AI Act says so explicitly: it applies without prejudice to data protection law. A high-risk system that clears conformity assessment with full marks still needs a legal basis, purpose limitation, and data subject rights handling for every drop of personal data it touches.

The role systems do not align, and pretending they do is a recurring consulting error. A **deployer** using an AI system on its customers is almost always a **controller** for that processing. A **provider** may be a controller for its own training processing, a processor when serving the model on a customer's data via API, and a controller again for logs it keeps for its own purposes, three different hats over one product, each with its own obligations. The mapping has to be done per processing activity, not per company.

Where the regimes both speak, they are complementary rather than redundant:

- **Automated decisions**: GDPR Art 22 gives the data subject a right not to be subject to a solely automated decision with legal or similarly significant effects (with exceptions requiring safeguards including human intervention); AI Act Art 14 requires oversight to be designed into high-risk systems. One is a subject's right, the other a product requirement; a real human-in-the-loop satisfies both, a rubber stamp satisfies neither.
- **Impact assessments**: the DPIA (GDPR Art 35) analyzes risks of the processing; the FRIA (AI Act Art 27) analyzes impacts on fundamental rights of the deployment. Art 27(4) wires them together, where the DPIA already covers ground, the FRIA complements it. In practice one merged document with two lenses is the efficient shape (note 03 details the FRIA).
- **Documentation and traceability**: records of processing (Art 30 GDPR) and technical documentation plus logs (Arts 11-12 AI Act) are cousins; a decent data map feeds both.

On enforcement, the asymmetry is the practical point. DPAs have years of AI case practice already, the Italian Garante's 2023 intervention on ChatGPT (temporary limitation, then reinstatement under conditions, later a fine) is the canonical demonstration that data protection law reaches AI systems today, no AI Act needed. Until the Act's enforcement machinery matures, the DPA is the regulator most likely to knock first.

## Legal bases for AI data processing

Art 6 GDPR offers six bases; for AI, the field narrows fast. Legal obligation, vital interests, and public task cover specific niches. **Contract** covers only processing objectively necessary to deliver the service the person asked for, which stretches to personalizing their experience and snaps well before "and we also train our foundation model on it". That leaves two workhorses:

- **Consent**: valid if freely given, specific, informed, unambiguous, and as withdrawable as it was givable. At web-corpus scale it is unobtainable; even at product scale, withdrawal creates the downstream problem this note's last section is about, consent that cannot be meaningfully honored after training was arguably not a sound basis before it.
- **Legitimate interest**: the flexible basis, and the only realistic one for large-scale training, purchased at the price of a documented balancing test (next section) and the standing risk that a DPA weighs the balance differently.

**Special categories** (Art 9: health, ethnicity, political opinions, religion, sexual orientation, biometrics for identification, and so on) sit under a separate, stricter regime: processing is prohibited unless an exception applies, explicit consent being the main private-sector route. Two AI-specific wrinkles. First, capable models **infer** special-category data from ordinary data (health status from purchase patterns, orientation from behavioral signals), and both supervisory authorities and EU case law read the concept broadly enough that inference can itself constitute special-category processing; a system designed to never ingest sensitive data may still produce it. Second, the AI Act's Art 10(5) opens a narrow, safeguarded gate to process special categories precisely for bias detection and correction in high-risk systems, the carve-out note 03 leans on, and a genuine novelty relative to GDPR alone.

The reference point for the whole area is the **EDPB Opinion 28/2024** on AI models: model anonymity is possible but assessed case-by-case (a model is not anonymous just because weights look like noise); legitimate interest can ground training if the three-step test genuinely passes; and a model trained unlawfully can contaminate the lawfulness of its later deployment. None of it is comfortable, all of it is workable, which is roughly the Opinion's intent.

## Privacy by design in the ML lifecycle

Art 25 requires data protection **by design and by default**: built into the processing, not appended to it. Mapped onto an ML pipeline, the checkpoints are concrete:

- **Collection**: minimization decided here or never. Which fields does the model demonstrably need? Raw identifiers rarely survive an honest answer.
- **Preparation**: pseudonymize before the data spreads into training snapshots, feature stores, and notebooks. Keep the re-identification key in a separate, governed system.
- **Training**: retention schedules on dataset snapshots (training data is data, snapshots multiply silently); access control on corpora and feature stores; where the threat model warrants, **differential privacy** offers a formal bound on individual leakage at a measurable utility cost.
- **Architecture**: **federated learning** keeps raw data local, though gradients and updates can still leak and the aggregation layer becomes the trust boundary; **synthetic data** helps until the generator memorizes its training set, at which point the problem has been relocated, not solved. Encryption at rest and in transit is table stakes; trusted execution environments cover the higher-assurance niches.

The pseudonymization versus anonymization line deserves its own sentence, because the vocabulary is routinely abused: pseudonymized data is still personal data, and true anonymization, judged against all means reasonably likely to be used for re-identification, including singling out, is genuinely hard to reach and harder to keep as auxiliary data accumulates. Most datasets marketed as anonymous are pseudonymous with good intentions. The honest engineering posture is to treat anonymization claims as claims requiring evidence, and to design controls assuming the data remains personal.

## The balancing test for AI training

The legitimate interest assessment (LIA) is a three-step argument, and for AI training each step has a known shape:

1. **Purpose test.** The interest must be lawful, real, and articulated: "developing and improving an AI model for service X" qualifies (commercial interests can qualify, the EDPB accepts as much); "AI" as a mission statement does not. Specificity here pays rent at step three.
2. **Necessity test.** Could the purpose be achieved with less data or less intrusion? This is where web-scale indiscriminate scraping meets its hardest question, and where curation, filtering of identifiers, deduplication, and dataset scoping become legal arguments rather than engineering hygiene.
3. **Balancing test.** The interest against the data subjects' rights, freedoms, and **reasonable expectations**. Publicly accessible does not mean free-for-all: a forum post written for a community carries different expectations than a press release. Context of publication, nature of the data (approaching special categories raises the bar), scale, and the subject's relationship to the controller all weigh in.

The design feature to internalize: **safeguards move the balance**. Respecting machine-readable opt-outs (the TDM reservation mechanism returns in note 08), filtering sensitive and identifying content, pseudonymization, output-side controls against regurgitation, transparency about sources, and a working objection channel are not decorations around the test, they are how a borderline balance tips to defensible. The LIA is a living document with an owner and a review date, the first artifact a DPA requests, and the difference between "we considered this" and "we can show you what we considered".

## Erasure and LLMs: what "delete" means for a trained model

Art 17's right to erasure was drafted for records; an LLM's weights are not records, and the collision is the most instructive open problem in AI data protection.

The technical facts first. Models **memorize**: extraction attacks recovering verbatim training data, including personal data, are demonstrated across model families, and the risk grows with duplication in the corpus and with model scale. Deleting a person's data from the training corpus does nothing to the already-trained model. The only complete remedy is **retraining without the data**, which for a foundation model is a cost measured in months and millions, and fails any proportionality argument for a single erasure request; for a narrow fine-tune it can be entirely feasible, which is why the answer differs by layer.

The realistic options form a ladder, and each rung should be described honestly for what it does:

| Option | What it achieves | Status |
|---|---|---|
| Delete at source + retrain | Complete erasure from the model | Proportionate for fine-tunes; rarely for foundation models |
| Machine unlearning | Targeted removal from weights | Research-grade; verification of successful forgetting is the unsolved part |
| Output suppression / filters | Blocks regurgitation of the data | Deployable today; suppression, not deletion, and bypasses exist |
| Behavioral fine-tuning | Trains the model to refuse or avoid | Brittle under adversarial prompting |

The anonymity question sits underneath: if a specific model, assessed case-by-case per the EDPB's framing, genuinely does not allow extraction of personal data by reasonable means, GDPR rights may not attach to the weights themselves. That assessment never extends to the surrounding pipeline: corpora, caches, logs, embeddings, and fine-tune datasets remain personal data on any reading, and erasure applies to them in the ordinary way.

Which yields the operational playbook for a deployer answering a real request: **locate** the person's data across corpus copies, RAG indexes, caches, logs, and fine-tune sets; **delete** where deletion is real (for RAG, removing the documents and re-embedding erases the operational retrieval path, which is both technically honest and often what actually matters to the requester); **suppress** at the output layer where deletion is not currently feasible; **flow down** contractually to the model provider what only they can do; and **record** the whole disposition, including its limits, in the response, which GDPR Art 12(3) expects without undue delay and in any case within one month of the request. A response that states plainly what was deleted, what was suppressed, and why retraining is disproportionate is defensible; one that says "done" when the model still regurgitates the data on a crafted prompt is a finding waiting for its incident number.

## Gotchas

- **Assuming AI Act conformity implies GDPR compliance.** Different objects, parallel application. The CE mark on a high-risk system says nothing about the legal basis of its training data, and the DPA is the authority most likely to ask first.
- **Reading provider/deployer as controller/processor.** The pairs come from different laws and split along different lines; a provider can be controller, processor, and controller again across three activities of the same product. Map roles per processing, in writing.
- **Stretching "contract" to cover training.** Necessary-for-the-service covers the service, not the roadmap. Training on customer data needs its own basis, and burying it in terms of service converts a legal gap into a transparency violation on top.
- **Marketing pseudonymous data as anonymous.** The recital 26 test (all means reasonably likely, including singling out) fails most real datasets as auxiliary data grows. Claims of anonymity are technical claims; without evidence they are liabilities with a timestamp.
- **Consent architectures that cannot honor withdrawal.** If withdrawal cannot propagate into the trained artifact, the consent story was broken at design time. Legitimate interest with real safeguards is often the more honest architecture than consent theater.
- **Answering erasure requests with silent suppression.** Output filtering is a legitimate layer and a false statement if reported as deletion. State the layers, their limits, and the proportionality reasoning; regurgitation under a crafted prompt after a "completed" erasure is the worst possible way to reopen the file.

## See also

- [03_bias_and_non_discrimination.md](03_bias_and_non_discrimination.md) - the Art 10(5) gate for sensitive data in bias work, and the FRIA the DPIA interlocks with
- [04_ai_risk_management.md](04_ai_risk_management.md) - logging and data governance duties on the AI Act side of the same pipeline
- [06_ai_act.md](06_ai_act.md) - where the AI Act's own transparency and classification machinery sits relative to GDPR
- [08_generative_ai_gpai_and_copyright.md](08_generative_ai_gpai_and_copyright.md) - the TDM opt-out and training-data transparency duties that meet the balancing test's safeguards from the copyright side
