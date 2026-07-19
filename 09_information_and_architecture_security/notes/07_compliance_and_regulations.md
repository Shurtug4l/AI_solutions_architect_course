# Compliance and regulations

## TL;DR

**Regulation is part of the threat model: non-compliance costs contracts, reputation, and fines, so an architect reads the rules with the same attention given to attackers.** The EU frame rests on five instruments: **GDPR** (personal data), the **AI Act** (AI systems by risk class), the **Cybersecurity Act** (a permanent ENISA plus a European certification scheme for ICT products at three assurance levels), **DORA** (financial-sector operational resilience), and **NIS 2**, the horizontal cybersecurity directive. This section commits to NIS 2 and sketches the Cybersecurity Act; the rest is deferred to the next module. NIS 2 (Directive EU 2022/2555, in Italian law via D.lgs. 138/2024) applies to strategic sectors above a size threshold (50 employees, or EUR 10 million turnover or balance sheet), but reaches smaller companies anyway through **supplier verification**: sell software to an in-scope entity and its obligations land on you via audit. Core duties: incident notification to the CSIRT without delay, trained governance, a **multirisk management system** that puts sabotage, fires, floods, blackouts, and human error in the same register as malware, vulnerability management, service continuity, documented security policies. Fines reach 1.4-2% of turnover depending on entity classification. The section closes with AI ethics anchored to the **Belmont Report** (respect for persons, beneficence, justice) and the reminder that the first security control is people.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **EU regulatory frame** | GDPR, AI Act, NIS 2, Cybersecurity Act, DORA | This section: NIS 2 in depth, Cybersecurity Act in sketch |
| **Cybersecurity Act** | Reg. EU 2019/881: permanent ENISA + ICT certification framework | Three assurance levels: basic, substantial, high |
| **NIS 2** | Directive EU 2022/2555, horizontal cybersecurity duties | Italian transposition: D.lgs. 138 of 2024-09-04 |
| **NIS 2 scope** | Strategic sectors, plus 50 employees or EUR 10M threshold | Below threshold is not a safe harbor |
| **Supplier pull-in** | In-scope entities must verify their suppliers | Compliance arrives via customer audit, not via the law directly |
| **Incident notification** | Significant incidents go to the CSIRT without delay | The reporting process must exist before the incident does |
| **Multirisk system** | One register for cyber, physical, environmental, human risks | Sabotage, fire, flood, blackout, human error, all in one document |
| **Sanctions** | Up to 1.4-2% of turnover by entity classification | Enough to make compliance a board topic, which is the point |
| **Belmont principles** | Respect for persons, beneficence, justice | Informed consent, bias control, fair distribution of risk and benefit |
| **Cyber hygiene** | People are the first security layer | Credentials pasted in cleartext into a ticket is a training failure |

## Why regulation is an architecture input

> Whoever works in programming and AI must also account for regulations. If they are not respected, the consequences are reputational damage, lost contracts, and fines.

That is the deck's opening argument, and it lands where module 08 already pointed: governance and compliance are non-functional requirements that dictate components, not policy documents that live next to the system. A notification duty implies logging and detection you can trust. A multirisk register implies an asset inventory. A supplier audit implies evidence you can produce on request. None of that appears in the architecture by accident.

The commercial angle deserves the emphasis the deck gives it. Fines are the visible penalty, but for a software vendor the faster failure mode is losing a contract because a customer's audit found nothing to audit. Compliance readiness is a sales prerequisite in regulated sectors, before it is a legal one.

## The EU regulatory map

Five instruments, one line each:

- **GDPR**: the EU privacy law, protection of personal data.
- **NIS and NIS 2**: EU-wide cybersecurity, the successor directive being the current reference.
- **Cybersecurity Act**: ENISA's mandate plus European security certification for ICT.
- **AI Act**: AI systems regulated by risk class.
- **DORA**: digital operational resilience for the financial sector.

The deck is candid about its own scope: almost all of these are deferred to the next module, which takes on the AI Act and GDPR properly (module 10, governance and ethics). This section describes NIS 2 and sketches the Cybersecurity Act. Worth keeping that honesty: what follows is one directive in reasonable depth plus pointers, not a survey of EU digital law. Module 07 already covered the data governance side of the same coin; the regulatory layer here is what makes several of those practices mandatory rather than merely sensible.

## The Cybersecurity Act in one slide

Regulation EU 2019/881, with two goals: give **ENISA** (the European cybersecurity agency) a permanent mandate and a central role supporting member states, and create a **European certification framework** for the security of ICT products, services, and processes.

Certification grades systems into three assurance levels: **basic, substantial, high**. It guarantees that technologies meet defined security standards, which is a trust mechanism for consumers and businesses as much as a technical one. Certification is generally voluntary, but member states can require it in critical sectors, so "voluntary" degrades gracefully into "mandatory where it matters".

## NIS 2: scope and the supplier pull-in

NIS 2 is the reference norm for cybersecurity in the EU. Formally it is **Directive (EU) 2022/2555**, adopted in 2022 and operative in Italy through **D.lgs. 138 of 2024-09-04**; the deck's "it came out in 2024" refers to that national entry into force. A directive, not a regulation, which matters in practice: the text an Italian entity actually answers to is the transposition decree, read against the directive. The full official text (Italian, 73 pages) is in the course readings at [../exercises/04_compliance_reference_texts/](../exercises/04_compliance_reference_texts/), and skimming its annexes is the fastest way to answer the first scoping question below.

Direct applicability is a two-gate test:

```
  Gate 1: is the entity in a strategic sector
          (energy, transport, health, water, digital
           infrastructure, waste, public admin, ...)?
             |                          |
            yes                         no
             |                          |
  Gate 2: >= 50 employees, OR      Do you supply an
          annual turnover or        in-scope entity?
          balance sheet total          |         |
          > EUR 10 million?           yes        no
             |                         |         |
            yes                  compliance    out of
             |                   via customer  scope
      directly in scope          audits
   (essential or important
    entity by classification)
```

The second column is the part small companies get wrong. In-scope entities have an explicit obligation to **verify their suppliers**, so the directive propagates down the supply chain through audits. The deck's example: waste management is a listed sector (collection, transport, recovery, disposal, supervision of those operations, post-closure interventions, brokerage). Supply software to such a company and you will be asked to demonstrate compliance, whatever your headcount says. The size threshold decides who the regulator can fine directly; the audit clause decides who has to do the work.

Sanctions scale with the entity's classification, reaching **1.4% to 2% of turnover** depending on whether the entity is classed as important or essential. Percentages of turnover, not fixed caps: the number is designed to survive translation into any boardroom.

## NIS 2: the duty list

What an in-scope entity (or an audited supplier) actually has to do:

- **Notify the CSIRT without delay** of any incident with significant impact on service provision. Notification presumes detection, triage, and a decision process that already exist.
- **Train governance**: the management body receives specific security training and guarantees the same for employees and collaborators. Accountability sits at the top by design.
- **Build a multirisk management system** covering, among other factors: sabotage, theft, fire, flood, telecommunications failures, power outages, unauthorized physical access, equipment failures, human error, malicious action.
- **Define security requirements** for systems and services.
- **Manage vulnerabilities** to prevent and counter anomalous events.
- **Guarantee service continuity**.
- **Define security policies** for information systems and networks.
- **Systematically monitor communications from the authorities** for clarifications and notifications. Compliance is a subscription, not a one-time filing.

The multirisk list is the item that reshapes how technical people think about the exercise. It deliberately mixes cyber threats with physical and environmental ones: a flooded server room and a ransomware operator are entries in the same register, assessed with the same discipline. Security architecture that stops at the network boundary fails the directive's framing before it fails any specific control.

## The multirisk walkthrough: a care home

Lesson 7.3 runs the method on a concrete case: a residential healthcare facility with a WiFi network, administrative staff, doctors, and care workers. It is accredited with the public health system, and the patient database is managed in cloud.

**Does NIS 2 apply?** Headcount alone says no, the facility is well under threshold. But it is accredited, so it processes data on behalf of a public structure: that makes it identifiable as a supplier, and the obligations arrive anyway. The scoping question is never just "how big are we" but "who do we serve".

**What is at stake?** Personal and health data, which must not be exfiltrated under any circumstance. The walkthrough scopes itself to cybersecurity; the GDPR exposure on the same data is deferred to the next module, though the overlap is obvious and module 07's data governance material already maps where that data lives and who touches it.

The assessment then maps the estate, layer by layer:

- **On-premise**: user PCs, WiFi, network, local and domain servers if present. For each: OS and patch state (the deck's example is a PC still on Windows 7), network characteristics and WiFi configuration, presence of backups on the servers, presence of UPS units for power loss.
- **Cloud**: the provider's published security posture is the evidence you get. The deck walks through Heroku's public security policy as the exercise: shared responsibility, certifications, what the vendor attests versus what remains yours. You inherit controls you cannot inspect, so vendor documentation review is a first-class assessment step, not paperwork.
- **People**: does competent staff exist? Has a system administrator been formally appointed? Has the personnel received cybersecurity training?

Everything found feeds the **multirisk assessment document** the directive requires, and the document drives remediation: the Windows 7 machine gets upgraded or retired, it does not get a footnote. An assessment that changes nothing is an inventory, not a risk process.

## Good practice, bad practice

The section's exercise grades five findings from a hypothetical multirisk assessment. Worth internalizing as calibration for what "compliant" means in NIS 2 terms:

| Case | Verdict | Why |
|---|---|---|
| BC/DR plan written 5 years ago, never formally updated despite changed processes and IT owners | Bad | NIS 2 expects continuous review, risk-based management, and documented role accountability. An obsolete document invalidates the plan's effectiveness. |
| Digital risk register maps critical suppliers (software, cloud, network services), refreshed every 6 months and after audits or incidents | Good | Supply chain census and monitoring is a key NIS 2 requirement: identify essential suppliers, assess correlated risk, update on a documented cadence. |
| Network logs retained 5 days "to avoid saturating storage" | Bad | Retention must support detection, forensic analysis, and legal evidence; think 6+ months, not days. Five days erases the incident before anyone asks about it. |
| Cyber insurance purchased, incident response never exercised ("we are covered") | Bad | Insurance transfers financial residue, not obligations. Prevention, exercises, incident handling, and continuity duties remain, and an untested response capability is a hypothesis. |
| Automated vulnerability scanning weekly on internal servers, monthly on internet-exposed ones, alerts to the SOC | Good | Periodic automated scanning with active alerting matches the vulnerability management and continuous monitoring requirements. |

One measured aside on the last case: the cadence is inverted relative to common practice. The internet-facing perimeter usually deserves scanning at least as frequent as the internal estate, since it is the surface an attacker probes daily. The verdict stands on the pattern (automated, periodic, SOC-wired), but in a real assessment the frequencies would be the first thing to renegotiate.

## The ethics detour: impact and trust

Lesson 7.2 steps back from law to ethics, starting with environmental cost. The deck's figures: generating one image consumes about half the energy needed to charge a smartphone, and every 10-50 responses consume the equivalent of a half-liter bottle of water. Published estimates vary widely with model size, datacenter efficiency, and accounting method, but the direction is not in dispute: inference at scale has a physical bill. The deck's conclusion is proportionality, not prohibition: use the tool with the weight it deserves, and keep asking whether a given use is worth its cost.

The second thread is trust. Security flaws of the kind this course has cataloged do not only cause damage, they erode confidence, and what is new is rarely presumed safe. Some owners will consider replacing workers with AI or deploying it out of proportion; in small companies, executives unfamiliar with the technology may block adoption outright, and traditional media rarely make the mechanisms clearer.

> The task of the programmer and of IT staff is to instill trust.

That means demonstrating, documentation in hand, that the AI tooling is secure and can actually reduce errors and improve safety. Trust is built with evidence, which conveniently is the same artifact compliance asks for: the multirisk document, the vendor review, the training record do double duty.

## The Belmont principles

For ethical guidance the AI community leans on the **Belmont Report** (1979), the foundational statement of research-ethics principles, included in the course readings as [../exercises/04_compliance_reference_texts/belmont_report_1979.pdf](../exercises/04_compliance_reference_texts/belmont_report_1979.pdf). Three principles, each with a direct AI translation:

- **Respect for persons**: recognize individual autonomy and protect those with reduced autonomy (age, illness, disability). Grounded in **informed consent**: every person must know the risks and benefits and be free to participate or withdraw at any time. In AI terms: consent flows, transparency about what a system does with a person's data and decisions.
- **Beneficence**: descended from the medical "do no harm", maximize benefit and minimize harm. For AI this becomes the responsibility to keep algorithms from amplifying bias tied to race, gender, or ideology.
- **Justice**: fairness and equality in distributing the risks and benefits of research and of machine learning. The report proposes five criteria for fair distribution: equal share, individual need, individual effort, societal contribution, merit.

A 1979 document about human-subjects research is an odd-looking anchor for AI ethics until you notice what it provides: principles that predate the technology and therefore cannot be gamed by it. The AI Act's obligations, which module 10 takes on in depth, are recognizably these three principles turned into enforceable requirements.

## The human layer

The deck closes on **cyber hygiene**: the first step of information security is people, and correctly trained staff prevents whole classes of incidents. The example given is a user writing to support "I cannot log into miosito.it, the username is pippo and the password is Topolino1927". The failing control is not technical.

Training also brings practices like **vibe coding** under control. Unmanaged, delegating code to an AI without review is a real risk vector; managed with competence and process, the same tool is a resource. The variable is never the tool, it is the operator's preparation, which is exactly why NIS 2 puts training obligations on governance and staff alike rather than mandating any particular technology.

## Gotchas

- **Reading the size threshold as a safe harbor.** Below 50 employees and EUR 10 million you escape direct scope, not the directive. The supplier verification clause delivers the same obligations through your customer's audit, with a contract instead of a fine as the enforcement mechanism.
- **Treating NIS 2 as an IT-only exercise.** The multirisk system deliberately spans sabotage, fire, flood, power loss, physical access, human error, and malice. An assessment that only inventories firewalls answers a question the directive did not ask.
- **Insurance as a substitute for capability.** A cyber policy transfers part of the financial residue and none of the duties. Prevention, exercises, and incident handling remain yours, and "we are covered" is how untested response plans stay untested.
- **Log retention sized by storage cost.** Five days of logs means the evidence is gone before detection, forensics, or a legal request needs it. Retention is a compliance and forensics parameter, not an infrastructure convenience; note 08 develops what those logs must support.
- **One-shot compliance documents.** A five-year-old BC/DR plan is formally present and materially void. NIS 2 expects living documents with review cadence and named owners; the same applies to the supplier register and the risk assessment itself.
- **Citing the wrong instrument.** NIS 2 is a directive (EU 2022/2555), not a regulation, so the operative text for an Italian entity is the transposition decree, D.lgs. 138/2024. Getting the legal mechanics right is cheap credibility in front of an auditor, and losing it is expensive.

## See also

- [01_ai_security_fundamentals.md](01_ai_security_fundamentals.md) - the security fundamentals that NIS 2 converts from good practice into legal duty
- [02_data_security.md](02_data_security.md) - protecting the personal and health data the care-home walkthrough revolves around
- [05_critical_asset_protection.md](05_critical_asset_protection.md) - asset mapping and prioritization, the operational core of the multirisk document
- [06_ai_architecture_security.md](06_ai_architecture_security.md) - the architecture-level controls the mandated security policies have to describe
- [08_ai_forensics.md](08_ai_forensics.md) - log retention and evidence quality, the exact point the 5-day retention case fails on
