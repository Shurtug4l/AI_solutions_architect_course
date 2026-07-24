# Generative AI, GPAI and copyright

## TL;DR

**General-purpose AI broke the AI Act's central assumption, that risk attaches to an intended purpose, so it got its own chapter: rules for models rather than systems, layered in two tiers.** A **GPAI model** (significant generality, wide task range, trained at scale with self-supervision) is a component, not a product; the Act regulates it because everything downstream inherits its properties. The base tier (**Art 53**) binds every GPAI provider: technical documentation for authorities, documentation for downstream providers who must build their own compliance on it, a **copyright policy** that identifies and respects text-and-data-mining opt-outs under the DSM Directive, and a **sufficiently detailed public summary of training content** on the AI Office template. Free and open-source models are exempt from the two documentation duties, never from copyright and the training summary. The **systemic-risk tier** (Arts 51, 55) catches models with high-impact capabilities, presumed at cumulative training compute above **10^25 FLOPs**: added duties of state-of-the-art evaluation with adversarial testing, Union-level risk mitigation, serious-incident reporting to the AI Office, and cybersecurity worthy of the weights. The **Code of Practice** offers a compliance presumption until harmonized standards land. The open-source carve-out is the Act's most contested bet: open weights are irrevocable, safety tuning is strippable, and the malicious-use surface of capable non-systemic models (disinformation, non-consensual imagery, fraud at scale) is real, while openness remains the strongest transparency and research mechanism available. The LLM risk inventory, hallucination, sycophancy, authority mimicry, provenance erosion, is the practical face of the same problem: fluency divorced from reliability.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **GPAI model** | Significant generality, wide task range, self-supervised at scale | Regulated as a component; the system built on it is a separate question |
| **Model vs system** | Chapter V binds model providers; risk tiers bind systems | A GPAI model inside a CV screener: two regimes, both apply |
| **Art 53 base tier** | Docs for authorities, docs downstream, copyright policy, training summary | Applies to every GPAI provider placing on the EU market |
| **Downstream documentation** | Enough for integrators to meet their own duties | The value-chain fix: high-risk builders inherit evidence, not mysteries |
| **Copyright policy** | Identify and respect TDM opt-outs (DSM Art 4(3)) | Applies for the EU market regardless of where training ran |
| **Training content summary** | Public, per AI Office template | The transparency lever rights holders enforce with |
| **Open-source exemption** | Skips the two documentation duties only | Copyright and summary always due; vanishes at systemic tier |
| **Systemic risk (Art 51)** | High-impact capabilities; presumed above 10^25 FLOPs | Notify within two weeks of meeting the threshold |
| **Art 55 add-ons** | Evaluations, red-teaming, mitigation, incidents, weight security | The frontier-lab duty set, enforced by the AI Office |
| **Code of Practice** | Adherence signals compliance until standards exist | The pragmatic path most large providers took in 2025 |
| **Strippable safety** | Fine-tuning removes refusal behavior from open weights | Published guardrails are a default, not a guarantee |
| **LLM reliability risks** | Hallucination, sycophancy, authority mimicry | Fluent register with no internal truth signal |

## Why general-purpose models broke the Act's logic

The Act's classification machinery runs on **intended purpose**: declare what the system is for, look up the risk tier, apply the obligations. A foundation model has no intended purpose; it has capabilities, and its purposes are whatever ten thousand downstream integrators invent. Classifying it under the pyramid is a category error in both directions: minimal risk (as a bare model it decides nothing) and high risk (someone will certainly wire it into an Annex III use) are simultaneously defensible and useless.

The legislator's answer, added late in the negotiation after generative models made the gap impossible to ignore, was Chapter V: regulate the **model layer** directly, with obligations that follow the artifact up the value chain. The definition (Art 3(63)) targets significant generality, competence across a wide range of distinct tasks, and training on large amounts of data with self-supervision at scale; models built and used purely for research and prototyping stay out until placed on the market. A **GPAI system** is the model plus whatever wraps it, and the wrapping is where the ordinary risk pyramid resumes: the same model is a component in a minimal-risk brainstorming tool and in a high-risk credit engine, and the system-level obligations differ accordingly while the model-level obligations stay constant.

The value-chain reading explains most of the design: a downstream provider building a high-risk system on a third-party model cannot satisfy Arts 8-15 with a black box under NDA. Art 53's documentation duties exist so that compliance evidence flows down the chain with the model, which is why the exemptions are calibrated to transparency: where openness already delivers the evidence, the paperwork duty relaxes.

The tier applies from 2025-08-02, with models already on the market before that date given a grace period to 2 August 2027 under Art 111(3); as of this module, the regime is live and the first compliance cycle is running.

## The base tier: Art 53 obligations

Four duties, two of them paired documentation flows:

- **Technical documentation for authorities** (Annex XI): architecture and training approach, evaluation methods and results, energy and compute information, available on request to the AI Office and national authorities.
- **Documentation for downstream providers** (Annex XII): capabilities, limitations, integration guidance, enough for an integrator to discharge its own AI Act duties. This is the value-chain fix in operation: the deployer of note 06's obligation map can only comply if this document exists and is honest.
- **A copyright policy**: state-of-the-art measures to comply with EU copyright law, specifically to identify and respect rights reservations under the TDM regime (next section).
- **A sufficiently detailed summary of training content**, published on the AI Office's template (issued 2025). Not the dataset itself: a structured account of sources and collections precise enough that rights holders and regulators can act on it.

**Open-source relief**: models released under a free and open-source license, with weights, architecture, and usage information publicly available, skip the two documentation duties, the logic being that openness substitutes for them. The relief never touches the copyright policy or the training summary, and it evaporates entirely at the systemic-risk tier. Non-EU providers appoint an authorized representative (Art 54), the same enforcement hook note 07 flagged. Underneath all four duties runs a standing obligation of cooperation with the AI Office and national authorities: the technical file is framed as available on request rather than filed once, because the documentation is the instrument of a supervisory relationship, not an archive deposited and forgotten.

Compliance mechanics run through the **Code of Practice** (Art 56): drafted through an AI Office process with providers and stakeholders, published in 2025, covering transparency, copyright, and (for the systemic tier) safety and security. Adhering to it earns a presumption-flavored simplification of demonstrating compliance until harmonized standards arrive; declining it means proving equivalence line by line. Most major providers signed, which was the point: the Code is soft law doing hard law's job during the standards gap.

## Copyright: the TDM bridge

The Act did not write new copyright law; it built a bridge to the existing one and closed its enforcement gap.

The **DSM Directive (2019/790)** created two text-and-data-mining exceptions: Art 3, mandatory and unwaivable, for scientific research by research organizations; Art 4, for everyone else, allowing reproduction for TDM **unless the rights holder has reserved the right**, for online content in machine-readable form. That reservation mechanism (robots-style signals, metadata, terms expressed machine-readably) existed before generative AI and was mostly theoretical, because no one could tell whether a given model had respected it.

The AI Act operationalizes it twice over. The Art 53 copyright policy obliges GPAI providers to **identify and comply with** Art 4(3) reservations as a regulatory duty, converting a rights holder's civil claim into a compliance obligation supervised by the AI Office. And the training content summary provides the visibility that enforcement was missing: a rights holder who finds their reserved corpus in the summary has a case that no longer depends on model forensics. The recitals add the **level playing field** clause: a provider placing a model on the EU market must meet the EU copyright standard regardless of where the training ran, neutralizing the obvious arbitrage of training in a jurisdiction with looser rules and importing the weights (the same extraterritorial instinct note 07 traced elsewhere in the Act).

Two boundaries keep the analysis honest. The TDM regime governs the **input side** (reproduction for training); output-side questions, memorized reproductions, style imitation, substantial similarity, remain classic copyright analysis, currently being litigated across jurisdictions with no settled answer. And the opt-out is prospective and practical: content scraped before reservations were expressed, and reservations expressed in non-machine-readable prose, are exactly the gray zones where the litigation lives.

## The systemic-risk tier

Some models concentrate enough capability that their failure modes stop being product defects and become **Union-level risks**: large-scale disinformation, serious accidents, offensive cyber capability, chemical-biological uplift, loss-of-control scenarios, the Act's definition speaks of significant impact on the internal market, public health, security, fundamental rights, or society as a whole, propagating at scale across the value chain.

Classification (Art 51) has two doors: a capability assessment against criteria in Annex XIII (parameters, dataset scale, compute, modalities, benchmark performance, market reach), or the bright-line **presumption at cumulative training compute above 10^25 FLOPs**, with the Commission holding a designation power for models the number misses. Providers must notify the Commission within two weeks of meeting the threshold, and may argue the presumption down with evidence. The threshold is the Act's most obviously perishable number, chosen to catch the frontier of 2024, adjustable by delegated act as the frontier moves, and a standing invitation to the threshold engineering note 07 listed.

The added obligations (Art 55) read as a codification of frontier-lab safety practice:

- **model evaluations** with state-of-the-art protocols, including **adversarial testing and red-teaming**;
- **assessment and mitigation** of the systemic risks identified, at Union level;
- **serious-incident tracking and reporting** to the AI Office and national authorities without undue delay;
- **cybersecurity** for the model and its infrastructure, which in practice means treating the weights as crown-jewel assets against theft and tampering (module 09's model-security material, now with a statutory hook).

Supervision is exclusively the **AI Office's** (note 09), with fines up to 3 percent of worldwide turnover or 15M EUR. The architecture is worth a beat of appreciation: the EU built a bespoke federal-style regulator for perhaps a dozen companies worldwide, on the theory that this is where single-system regulation stops scaling, the geopolitical risk layer of note 04 turned into an org chart.

## The open-source question

The open-source carve-out is where the Act's cleanest tension lives, and the course is right to frame it as a problem rather than a rule.

The case for the exemption is solid: openness **is** transparency (weights, architecture, and behavior are inspectable in ways no documentation duty matches), open models are the substrate of European research and SME innovation, and burdening hobbyist releases with Annex XI paperwork would regulate exactly the actors with no capacity to comply and no market power to matter.

The case against is equally solid, and it is empirical, not rhetorical. Open weights are **irrevocable**: there is no recall, no patch channel, no deprecation. Safety alignment is **strippable**: published work shows refusal behavior removed with modest fine-tuning budgets, so the guardrails a provider ships are a default configuration, not a property of the artifact. And capable models below the systemic threshold are already sufficient for the industrialization of harm that needs no frontier capability: persuasive disinformation at negligible marginal cost, non-consensual intimate imagery, voice-clone fraud, phishing at native-speaker quality in every language. None of that requires 10^25 FLOPs, which is precisely the gap the exemption leaves open by design.

The Act's implicit bet: the marginal risk of open non-systemic models is acceptable against the innovation and transparency value, and the truly dangerous capability lives above a compute line where the exemption dies anyway (an open-weights systemic model carries full Art 55 duties, the question the largest open releases now test). Both positions in this debate have serious defenders, and the intellectually honest posture is to hold it as an open empirical question with a known review mechanism, the Commission can and will revisit, rather than a settled principle. For a practitioner the operational takeaway is narrower: deploying an open model does not import its provider's exemptions, your system-level obligations (risk class, Art 50 transparency, GDPR) are untouched by the license on the weights.

## LLM disinformation and reliability risks

The exercise closing the section, building the risk inventory for an LLM deployment, is the systemic discussion scaled down to one system. The inventory sorts by mechanism:

- **Hallucination**: fluent generation without a truth signal; the model optimizes plausibility, and fabricated citations, invented case law, and confident wrong numbers are the canonical production incidents.
- **Sycophancy**: agreement preferred over accuracy under conversational pressure; the failure compounds in exactly the workflows (review, advice) where users bring a hypothesis to confirm.
- **Authority mimicry**: the register of expertise regardless of underlying reliability, which defeats the user's calibration; the interface reads as an oracle while behaving as an autocomplete.
- **Staleness and asymmetry**: knowledge cutoffs, and quality that degrades off-distribution and off-English, an equity issue as much as an accuracy one (note 03's exclusion class, reappearing).
- **Adversarial channels**: prompt injection and poisoned retrieval content steering outputs, the security face of reliability, covered mechanically in module 09.
- **Ecosystem effects**: synthetic content feeding back into training corpora, and deliberate seeding of content designed to be retrieved and repeated by models, disinformation aimed at the machines rather than the humans.

Disinformation-specific risk adds the scale economics from note 04: near-zero marginal cost of persuasive text, personalization, and the liar's dividend eroding trust in authentic evidence, with Art 50's marking regime (note 06) as the regulatory counter on the media side.

Mitigations map one-to-one: retrieval over curated sources with verified citations against hallucination; abstention and uncertainty surfacing against authority mimicry; domain guardrails and human gates for public-facing claims; provenance marking on generated media; monitoring with an incident path (note 10) because every mitigation above degrades silently. The exercise's structure, risk, mechanism, mitigation, residual, is the Art 9 loop of note 04 applied to a generative system, which is the point of putting it here: GPAI changed which layer the rules attach to, not how risk work is done.

## Gotchas

- **Confusing the model regime with the system regime.** Art 53 binds the model provider; the risk pyramid binds the system. Building on a fully compliant GPAI model discharges none of your system-level duties, and the model's documentation is an input to your conformity work, not a substitute for it.
- **Reading the open-source exemption as a general pass.** It waives two documentation duties at the model layer, conditional on genuine openness, and nothing else: copyright policy and training summary remain, systemic risk cancels it, and deployers inherit no part of it.
- **Treating 10^25 FLOPs as the definition of dangerous.** It is a presumption with a designation power behind it and a delegated-act dial on it. Engineering a training run to 9.9 x 10^24 buys an argument, not an exemption, and the AI Office has seen the spreadsheet.
- **Assuming training abroad settles the copyright question.** The level-playing-field clause attaches the EU TDM standard to EU market placement. Where the GPUs sat is irrelevant to whether the weights can be sold in Brussels.
- **Trusting shipped guardrails on open weights.** Refusal behavior is a fine-tune away from gone. Any deployment threat model that says "the model refuses such requests" is describing the default configuration of an artifact the attacker also possesses.
- **Building LLM products on the oracle assumption.** Fluency is not a truth signal, and users cannot calibrate against a confident register. Reliability engineering (retrieval, abstention, verification, review gates) is product architecture, not a polish phase.

## See also

- [06_ai_act.md](06_ai_act.md) - the system-level regime this chapter runs parallel to, including Art 50's marking duties for synthetic media
- [04_ai_risk_management.md](04_ai_risk_management.md) - the risk-management loop that Art 55 scales up to frontier models, and the geopolitical risk layer behind "systemic"
- [05_privacy_and_data_protection.md](05_privacy_and_data_protection.md) - the data-protection face of training-data governance: legal bases, balancing test, erasure against weights
- [07_international_compliance.md](07_international_compliance.md) - threshold gaming and the open-source carve-out as regulatory loopholes, and the extraterritorial pattern the copyright clause repeats
- [09_conformity_audit_and_certification.md](09_conformity_audit_and_certification.md) - the AI Office as GPAI supervisor, and the Code of Practice's place in the standards machinery
