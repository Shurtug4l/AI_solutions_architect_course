# International compliance

## TL;DR

**There is no global AI law; there is a spectrum of national bets, a handful of convergence machines, and a set of arbitrage opportunities that close slowly.** The EU bet on a comprehensive, binding, horizontal regulation; the US on sectoral enforcement, voluntary frameworks (NIST), executive orders that flip with administrations, and a growing state patchwork; the UK on regulator-led principles without a statute; China on early, binding, vertical rules (recommendation algorithms, deep synthesis, generative AI) built around content control and labeling; Korea passed the second comprehensive law, Brazil is advancing an EU-inspired bill, Canada's attempt died with its parliament. Across this map the **Brussels effect** operates in two modes: de facto (global firms standardize on the strictest big-market rule because one compliance stack is cheaper than five) and de jure (legislators copy the text), with the GDPR as the proven precedent and the AI Act's replay still partial: strong export of **definitions and vocabulary**, weaker pull at the frontier-model layer, where geo-fencing the EU is a live alternative. The convergence machinery is institutional: the **OECD** supplies the shared definition of an AI system (the AI Act's Art 3(1) tracks it nearly verbatim), the **Council of Europe** produced the first binding treaty (flexible to a fault), UNESCO and the UN supply near-universal soft law, the G7 a code of conduct, and **ISO/IEC SC 42** does the quiet real work of harmonization through standards. **Regulatory loopholes** (jurisdictional arbitrage, open-source carve-outs, definitional edges, threshold gaming) are best read as a map of where guidance and enforcement will concentrate next. The HQ-country exercise resolves to one question: if you serve the EU market, extraterritoriality prices the AI Act into your stack wherever the brass plate sits.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **EU approach** | Binding, horizontal, ex ante, rights-based | One rulebook, staggered calendar, CE-mark machinery |
| **US approach** | Sectoral + voluntary + state patchwork | NIST RMF is voluntary; Colorado and NYC bind; EOs oscillate |
| **UK approach** | Principles to existing regulators, no statute | Flexibility purchased with regulatory uncertainty |
| **China approach** | Vertical binding rules, content-centric | Algorithm registry, deep synthesis and labeling duties |
| **Brussels effect, de facto** | Firms standardize on the strictest big market | One global privacy policy; possibly one AI compliance stack |
| **Brussels effect, de jure** | Legislators copy the EU text | GDPR clones worldwide; AI Act echoes in Brazil, Korea |
| **OECD definition** | The shared scope anchor across regimes | AI Act Art 3(1) tracks it deliberately, near verbatim |
| **Council of Europe convention** | First binding AI treaty (2024) | Broad signatories, obligations flexible by design |
| **Standards channel** | ISO/IEC SC 42, CEN-CENELEC as transmission belt | Harmonization happens in committees, not summits |
| **Regulatory loophole** | Gap between the rule's text and its reach | Each one is a forecast of the next guidance document |
| **Military / nat-sec exclusion** | Whole-Act carve-out for defense and national security (Art 2(3)) | The largest gap; its dual-use boundary is the contested edge |
| **Geo-fencing** | Withhold or degrade the product for the EU | The anti-Brussels-effect: divisibility beats convergence |
| **HQ choice** | Market served decides compliance, not incorporation | Extraterritoriality makes the brass plate mostly tax law |

## The global regulatory map

Comparing regimes needs axes, not anecdotes. Four do most of the work: binding or voluntary; horizontal or sectoral; ex ante (pre-market duties) or ex post (liability after harm); rights-anchored or innovation-anchored.

| Jurisdiction | Instrument | Character |
|---|---|---|
| EU | AI Act (2024) + GDPR | Binding, horizontal, ex ante, rights-based |
| US federal | NIST AI RMF, sectoral enforcement (FTC, EEOC), executive orders | Voluntary core, ex post enforcement, direction swings with administrations |
| US states | Colorado AI Act (2024, effective 2026), NYC Local Law 144, others | Binding, narrow scopes (consequential decisions, hiring audits), a compliance patchwork |
| UK | 2023 white paper approach: principles via existing regulators | Non-statutory, sectoral, deliberately light |
| China | Algorithm recommendation rules (2022), deep synthesis (2023), generative AI measures (2023), content labeling (2025) | Binding, vertical, content- and stability-centric, registry-based |
| South Korea | AI Basic Act (in force from early 2026) | Second comprehensive national law, EU-familiar structure, lighter touch |
| Brazil | PL 2338, Senate-approved 2024 | EU-inspired risk-based bill in progress |
| Canada | AIDA (Bill C-27) | Died with the 2025 prorogation; restart uncertain |
| Japan | Soft-law posture, 2025 promotion-oriented law | Innovation-first, governance by guidance |

Two readings of the table. First, the popular "EU regulates, US innovates, China surveils" line is a slogan, not an analysis: the US binds hard in narrow slices (try shipping an unaudited hiring tool into NYC), China's rules are operationally demanding and arrived earliest, and the EU's regime has more flexibility valves (sandboxes, SME accommodations, the Art 6(3) filter) than its reputation admits. Second, the real divergence is less about strictness than about **what each regime is protecting**: fundamental rights (EU), market fairness and consumer protection (US enforcement practice), information control and social stability (China), competitiveness (UK, Japan). Compliance programs that only translate rules, without registering what the regulator cares about, misallocate effort across regions.

## The Brussels effect

The term (Anu Bradford's) names the EU's ability to set global rules without global jurisdiction, and it has two distinct mechanisms. **De facto**: multinationals adopt the strictest major-market standard globally because maintaining divergent product versions costs more than over-complying elsewhere; one privacy policy, GDPR-shaped, for every user on earth. **De jure**: other legislators copy the EU text because it exists, is detailed, and arrives with an enforcement track record; the worldwide family of GDPR-style laws (Brazil's LGPD the clearest case) is the proof of concept.

Whether the AI Act repeats the GDPR's run is a live question, and the honest answer splits by layer:

- **Definitions and vocabulary: already exported.** Risk tiers, "high-risk system", provider/deployer split, and the OECD-aligned definition appear in Brazilian, Korean, Canadian, and Council of Europe texts. Whoever writes the vocabulary frames every subsequent national debate, and the EU wrote it.
- **Standards: the strong channel.** Harmonized standards drafted for the AI Act feed the same ISO/IEC pipeline every other jurisdiction draws on, so AI Act requirements travel inside "neutral" technical documents. This is the same quiet mechanism that globalized EU product safety, and it is the one to bet on.
- **Frontier models: the weak layer.** The Brussels effect requires **non-divisibility**, one product too costly to fork per region. AI services are more divisible than data protection practices: behavior can be geo-conditioned, features withheld, models released everywhere except the EU, and several high-profile launches have indeed arrived in Europe late or trimmed. Add that the two frontier-model jurisdictions (US, China) have geopolitical reasons not to import EU rules, and the effect at this layer looks partial at best.

The synthesis for a practitioner: expect AI Act concepts in every jurisdiction's next draft, expect global enterprise compliance stacks to be AI Act-shaped (de facto effect via B2B procurement, where EU-grade compliance becomes a selling feature), and do not expect the frontier labs' release strategies to be written in Brussels.

## International organizations: who does what

The alphabet soup sorts cleanly by function:

- **OECD**: the interoperability hub. The AI Principles (2019, revised 2024, 47+ adherents) set the shared values; the 2023 revised **definition of an AI system** became the de facto global scope anchor; the AI Policy Observatory tracks national policies. No enforcement, maximal influence per page.
- **Council of Europe**: the **Framework Convention on AI, human rights, democracy and the rule of law** (opened for signature 2024), the first binding international AI treaty, signed by the EU, the US, and the UK among others. Binding in form, flexible in substance: parties choose how to give effect to obligations, which is the price of getting those three signatures on one document.
- **UNESCO**: the Recommendation on the Ethics of AI (2021), adopted by 193 states; the widest consensus and the softest instrument.
- **UN**: General Assembly resolutions, the Global Digital Compact, and advisory bodies: agenda-setting for the jurisdictions no other forum reaches.
- **G7 Hiroshima Process**: the code of conduct for advanced AI systems (2023), the plurilateral vehicle for frontier-model voluntary commitments while binding law catches up.
- **ISO/IEC JTC 1/SC 42** (with IEEE alongside): where harmonization actually happens. Management systems (42001), terminology (22989), risk guidance; the standards get referenced by regulators on every continent, which makes committee seats quietly geopolitical.

The pattern: political bodies converge vocabulary and principles, the treaty layer is broad but shallow, and the technical standards layer is narrow but deep. Real interoperability, the kind that lets one audit serve two jurisdictions, comes from the third.

## One definition to rule them: AI Act vs OECD

The AI Act's Art 3(1) defines an AI system as a machine-based system designed to operate with varying levels of autonomy, possibly adaptive after deployment, that infers from received input how to generate outputs (predictions, content, recommendations, decisions) capable of influencing physical or virtual environments. Set beside the OECD's 2023 revised definition, the texts are nearly interchangeable, and deliberately so: the EU legislator swapped its earlier, list-based definition for the OECD's precisely to anchor the Act's scope in an internationally shared concept.

Why the alignment is worth caring about:

- **Scope interoperability.** A system classified as "AI" under one OECD-aligned regime is almost certainly "AI" under the next, so scoping analyses travel. The Council of Europe convention and several national drafts use the same skeleton.
- **The load-bearing word is "infers".** It draws the line between systems that derive their behavior from data or objectives and classic software executing rules a human wrote in full. Deterministic rule engines, standard statistical calculations, and spreadsheets sit outside; learned models sit inside. The Commission's 2025 guidelines on the definition walk the boundary cases, and the honest summary is that anything trained sits in scope while simple hand-coded heuristics generally do not.
- **The definition is not the risk class.** In-scope means the Act applies at all; nearly everything in scope still lands in the minimal tier. Scope panic ("our regression is AI now!") confuses the gate with the obligations behind it, which is exactly the two-step the note 06 procedure separates.

## Regulatory loopholes and how they close

Every regime ships with gaps; listing the AI-relevant ones is less about using them than about forecasting where enforcement attention lands next.

- **Jurisdictional arbitrage.** Develop and host where rules are lax, serve the regulated market remotely. The AI Act's answer is the output-used-in-EU clause; the honest caveat is that enforcing against an entity with no EU establishment is slow, which is why the Act requires non-EU providers to appoint an EU **authorized representative**, an enforcement hook with an address.
- **The open-source carve-outs.** Free and open-source models escape parts of the GPAI regime unless they cross the systemic-risk line (and open-sourcing never exempts prohibited practices or high-risk deployments). Releasing weights as a compliance strategy is note 08's subject, and the exemption's edges are among the most-watched in the whole Act.
- **The research exemption.** Scientific R&D is out of scope until placing on market or putting into service; the gray zone is the perpetual "research preview" serving production traffic. Regulators have seen this movie in other industries; the label does not survive contact with revenue.
- **The military and national-security exclusion.** The Act does not apply to AI systems placed on the market or used exclusively for military, defense, or national-security purposes, whoever develops them, because those domains sit outside the Union's internal-market competence (Art 2(3)). This is the largest carve-out in the whole regime, and its live edge is dual-use: a system built for a security purpose is exempt, the same system repurposed into a civilian Annex III use is not, and "national security" is exactly the kind of scope claim that invites documentation and challenge when the deployment looks civilian. Market surveillance holds no writ inside the exclusion, which is why its boundary, not its interior, is where the compliance question actually lives.
- **Definitional edges.** Arguing the system does not "infer", or stretching Art 6(3)'s narrow-task exceptions past their qualifiers. Both are documented, challengeable positions, and the profiling override plus the registration duty were designed to make silent stretching visible.
- **Boundary gaming in the value chain.** Structuring contracts so no party looks like the provider; Art 25's role-switch rules close most of it by attaching the label to conduct (branding, modifying, repurposing) rather than to contracts.
- **Threshold engineering.** Staying under the GPAI systemic-risk compute presumption, or portioning training runs to avoid designation. Numeric thresholds invite this by construction, which is why the Act pairs the number with a discretionary designation power (note 08).

The meta-lesson from GDPR practice: loopholes in EU law have a half-life. Guidance, coordinated enforcement, and court decisions arrive in that order, and positions that relied on a gap without documentation age the worst. Using a gray zone is a legitimate risk decision when it is written down as one, with an owner and a revisit date; as an unstated assumption it is deferred liability.

## Where to incorporate: the HQ exercise

The course exercise, choosing the most appropriate country for an AI company's seat, is best solved by refusing its framing first: **the AI Act follows the market served, not the place of incorporation.** If the EU's 450 million consumers are in the plan, extraterritoriality plus the authorized-representative requirement mean the compliance stack is EU-grade wherever the HQ sits. The real decision matrix, then:

| Factor | EU seat | Non-EU seat, serving EU | Non-EU seat, avoiding EU |
|---|---|---|---|
| AI Act exposure | Full, direct | Full, plus authorized representative | None, until output leaks in |
| Regulatory relationship | Lead authority, sandbox access | Arm's length, via representative | None |
| Compliance cost | High, predictable | High, plus intermediation | Low, until expansion |
| Enterprise sales in EU | Compliance as a feature | Same, harder to evidence | Excluded from the market |
| Optionality | Committed | Balanced | Locked out of a third of global spend |

Reading it out: for a company that will sell into the EU, an EU establishment mostly **adds** benefits rather than costs, direct regulator relationships, mandatory-by-2026 national sandboxes (member states must stand up at least one; Spain moved early with a dedicated agency), and the trust premium that EU-grade compliance carries in B2B procurement globally, the de facto Brussels effect working in your sales deck's favor. Choosing a light-touch jurisdiction (UK flexibility, US scale, Singapore-style incentives) is coherent only when the EU market is genuinely out of the plan or deferred, and that is a commercial decision wearing a regulatory costume. The exercise's deepest lesson is that "which country" is rarely a compliance question at all: it is a market-strategy question whose compliance consequences are largely predetermined.

## Gotchas

- **Comparing regimes by strictness instead of by protected interest.** The EU protects rights, US enforcers protect markets and consumers, China protects information control. The same system can be fine in one regime and radioactive in another for reasons no strictness ranking captures.
- **Betting on a full GDPR-style Brussels effect for frontier models.** The de facto effect needs non-divisibility, and AI services fork by region cheaply. Vocabulary and enterprise stacks will converge on the EU shape; frontier release strategies will not, and EU users may simply get products later.
- **Reading the Council of Europe convention as hard law.** Binding in form, elastic in implementation. It moves the diplomatic baseline, not your compliance backlog.
- **Ignoring the US state layer because the federal layer is voluntary.** Colorado's duties and NYC's audit mandates bind today; a "the US is unregulated" slide is wrong in the two places most likely to sue you.
- **Scope panic over the AI definition.** "Infers" pulls trained models in and leaves hand-coded rules out, and in-scope almost always means minimal tier. The definition gates applicability, not obligations.
- **Treating a loophole as a strategy instead of a documented risk position.** Gray zones close via guidance and enforcement on a known clock. The difference between arbitrage and negligence is a written analysis with an owner and a review date.

## See also

- [06_ai_act.md](06_ai_act.md) - the regulation whose export potential this note assesses: scope, tiers, extraterritorial hooks
- [01_ai_governance_foundations.md](01_ai_governance_foundations.md) - the OECD principles and NIST RMF as the frameworks under the international vocabulary
- [08_generative_ai_gpai_and_copyright.md](08_generative_ai_gpai_and_copyright.md) - the open-source carve-outs and compute thresholds that anchor two of the loopholes here
- [09_conformity_audit_and_certification.md](09_conformity_audit_and_certification.md) - the standards machinery that is the Brussels effect's strongest transmission channel
