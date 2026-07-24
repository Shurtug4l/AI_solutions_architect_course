# AI risk management

## TL;DR

**The AI Act regulates risk, not technology: the same model family can be banned, heavily regulated, or ignored depending on what it is used for.** The **risk-based approach** sorts systems into four tiers: unacceptable risk (prohibited outright), high risk (permitted under a compliance regime), transparency risk (disclosure duties), and minimal risk (no new obligations). The architecture of the module sits in the high-risk tier, where providers owe a connected set of requirements (Arts 8-15): an **iterative risk management system** running across the lifecycle (Art 9), **data governance** with bias examination (Art 10), technical documentation and automatic **logging** (Arts 11-12), transparency toward deployers (Art 13), **human oversight** designed into the system rather than bolted on (Art 14), and declared **accuracy, robustness, and cybersecurity** (Art 15). Above single-system risk sits the (geo)political and social layer: disinformation at scale, surveillance exports, labor displacement, compute concentration as a sovereignty lever; these shape regulation and procurement even when no individual system is at fault. On the technical side, Art 15 translates into engineering practice: declared metrics measured per segment, robustness under perturbation and distribution shift with fallback plans, and defenses against the AI-specific attack surface (poisoning, evasion, extraction). The operational glue is **threat modeling**: enumerate assets, trace data flows, map threats with MITRE ATLAS and OWASP as checklists, rate, mitigate, and feed a living risk register. Art 9 is that loop institutionalized, not a document produced once.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **Risk-based approach** | Four tiers: prohibited, high, transparency, minimal | Obligation intensity follows harm potential, not model size |
| **Intended purpose** | Risk class attaches to the declared use context | Same model, different use, different tier |
| **Art 9 risk management** | Continuous, iterative, lifecycle-wide process | A one-shot risk workshop does not satisfy it |
| **Foreseeable misuse** | Risks assessed beyond the intended use | "We never designed it for that" is not a defense |
| **Art 10 data governance** | Relevant, representative, error-checked data; bias examined | The evidence trail behind every training set |
| **Art 12 logging** | Automatic records over the system lifetime | Traceability is a design requirement, not an ops afterthought |
| **Art 14 human oversight** | Humans able to understand, override, and stop | Oversight designed against automation bias, not just present |
| **Art 15 triad** | Accuracy, robustness, cybersecurity, declared and maintained | Metrics in the instructions for use, not in a slide |
| **Geopolitical risk layer** | Disinformation, surveillance export, compute concentration | Lands in tenders as sovereignty and provenance clauses |
| **MITRE ATLAS** | Knowledge base of adversarial ML tactics | The AI-specific overlay on a classic threat model |
| **Risk register** | Living document: threat, rating, owner, mitigation, review date | If it has no owners and no review cadence, it is a snapshot |

## The risk-based approach, briefly

The regulatory design choice behind the AI Act is proportionality: instead of regulating "AI" as a technology (impossible to scope) or waiting for harm and litigating afterwards (too slow, too asymmetric), the Act classifies **uses** by harm potential and scales obligations accordingly.

```
  unacceptable risk   ->  prohibited (Art 5)
  high risk           ->  permitted under compliance regime (Arts 8-15, 16-27)
  transparency risk   ->  disclosure duties (Art 50: chatbots, deepfakes, ...)
  minimal risk        ->  no new obligations (the vast majority of systems)
```

Two consequences follow. First, the classification exercise, which system falls where, becomes the highest-stakes legal question in any AI project, because everything downstream hangs on it; note 06 covers the mechanics, including the Annex III list and the Art 6(3) exceptions. Second, risk is assessed **ex ante against the intended purpose** the provider declares, plus reasonably foreseeable misuse. The same foundation model inside a CV screener is high-risk machinery; inside a recipe generator it is nobody's regulatory concern. General-purpose models broke this tidy use-based logic and got their own chapter, which is note 08's subject.

## What high-risk actually requires: Arts 8-15

The high-risk requirements read as a checklist, but they are designed as a system: each one produces the evidence the next one consumes.

| Article | Requirement | What it means in practice |
|---|---|---|
| Art 9 | Risk management system | Iterative loop across the lifecycle: identify, estimate, mitigate, test, repeat |
| Art 10 | Data and data governance | Fit-for-purpose datasets, documented provenance, bias examination |
| Art 11 | Technical documentation (Annex IV) | Enough detail for an authority to assess conformity without you in the room |
| Art 12 | Record-keeping | Automatic logs enabling traceability over the system's lifetime |
| Art 13 | Transparency to deployers | Instructions for use: capabilities, limitations, oversight measures |
| Art 14 | Human oversight | Designed-in ability to understand, monitor, override, and stop |
| Art 15 | Accuracy, robustness, cybersecurity | Declared metrics, resilience to errors and to attacks |

**Art 9** is the spine. It demands a continuous, iterative process: identify foreseeable risks from intended use and reasonably foreseeable misuse, estimate and evaluate them (including risks emerging from post-market monitoring data), adopt targeted mitigation, and test that residual risk is acceptable, with specific attention to impacts on persons under 18 and other vulnerable groups. The word "iterative" carries legal weight: a risk assessment performed once at design time and filed does not meet the requirement, which is precisely where mature engineering organizations discover their existing model review process is 80 percent of the way there and their documentation is not.

**Art 14** deserves a careful read because it regulates a design property, not a staffing decision. Oversight measures must enable the natural persons assigned to them to understand the system's capacities and limitations, remain aware of **automation bias** (the Act names it explicitly), correctly interpret output, decide not to use the system in a given situation, intervene or interrupt operation, and reverse or disregard the output. The design space runs from human-in-the-loop (HITL), a person validating before the action executes, through human-on-the-loop (HOTL), the system acting while a person monitors and can intervene, to human-in-command over the process as a whole; the Act mandates none of them by name, it mandates that whichever is chosen actually functions under load. Every one of those verbs implies UI, alerting, and process design; a human "in the loop" who lacks the information, the time, or the authority to override is oversight in name only, and the override-rate KPI from note 02 is the production-side check on exactly this.

The provider carries Arts 8-15; the deployer's mirror duties (use per instructions, monitoring, log retention, the FRIA from note 03 where applicable) sit in Arts 26-27. Keeping the two roles distinct per system is the first scoping act of any compliance analysis, and the mapping exercise returns in note 06.

## The wider board: geopolitical and social risks

Single-system risk classes do not exhaust the risk landscape; a second layer operates at the scale of societies and states, and it increasingly writes itself into law and procurement.

- **Epistemic risks.** Synthetic media at near-zero marginal cost changes the economics of disinformation: influence operations scale, and the mere existence of convincing fakes lets authentic evidence be dismissed (the liar's dividend). Election integrity is the sharpest case, and it is why deepfake transparency obligations exist at all (note 06).
- **Surveillance and export.** AI-enabled monitoring stacks are exportable products; the governance question follows the supply chain, not just the deployment. Dual-use tension is structural: the same computer vision that inspects welds tracks crowds.
- **Labor and distribution.** Displacement and task restructuring at uneven speed across sectors and regions, with productivity gains and adjustment costs landing on different populations. Less a model property than a deployment-velocity property, which is why it resists system-level regulation and surfaces instead in social policy debates.
- **Concentration and sovereignty.** Frontier capability depends on a supply chain with famous choke points: advanced chips, a handful of foundries, hyperscale compute, and the capital to run training at scale. Concentration turns dependency into leverage (export controls are the visible instrument), and it is why European tenders increasingly carry data residency, model provenance, and exit-strategy clauses. For an architect this is the risk layer that arrives as contractual requirements rather than as regulation.
- **Escalation dynamics.** Military AI and autonomous weapons sit in a slow-moving international debate (UN fora, no binding treaty); the practical takeaway for civilian practice is narrower, dual-use review of what capabilities a published model or dataset actually unlocks.

The reason this panorama belongs in a risk management note: these risks motivate the regulatory tiers above single systems (the GPAI systemic-risk regime of note 08 is exactly this layer turned into law), and they explain regulatory divergence between blocs better than any reading of legal texts alone (note 07).

## Art 15 in engineering terms: accuracy, robustness, cybersecurity

The triad reads as three words in the Act and unpacks into three engineering programs.

**Accuracy** means declared, appropriate metrics: chosen for the task (a recall target for screening, calibration for scoring), measured on test data that represents the deployment population, reported per segment (the disaggregation discipline from note 03), and stated in the instructions for use together with the conditions under which they hold. The honest part is the last clause: accuracy claims are conditional on a distribution, and the claim decays under drift, which makes monitoring part of the accuracy requirement rather than a separate virtue.

**Robustness** is behavior away from the happy path: tolerance to input noise and malformed data, defined behavior on out-of-distribution inputs (detect and route to fallback beats confidently extrapolating), graceful degradation and redundancy where errors propagate, and resilience of continuous-learning setups against feedback loops that would let the system's own outputs skew its future training (the Act calls this out explicitly). The verification tools are stress testing, edge-case suites, and adversarial evaluation on a cadence, not once.

**Cybersecurity** covers the AI-specific attack surface on top of classic appsec for the serving stack: **data poisoning** (corrupting training data upstream), **model poisoning** (tampered pretrained components, a supply-chain problem), **adversarial examples / evasion** (inputs crafted to flip outputs), and **confidentiality attacks** (model extraction, membership inference). Controls follow the asset: integrity and provenance checks on the training pipeline, access control and rate limiting on model endpoints, input validation, anomaly monitoring on queries and outputs. Module 09 covered the attack mechanics in depth; this module's contribution is that Art 15 makes a documented defense posture a **legal requirement** for high-risk systems, so the security work must now produce evidence, not just protection.

## Threat modeling an AI system in production

The course exercise simulates what Art 9 institutionalizes: a structured threat mapping for a live system. The method ports from security practice with an AI overlay:

1. **Scope and assets.** Name what is worth attacking or breaking: training data, feature pipeline, model weights, the decision output itself, logs, feedback channels. For decisional systems the output is often the crown jewel, an attacker who can steer decisions does not need the weights.
2. **Draw the flow.** Data sources, training pipeline, registry, serving path, human touchpoints, feedback loops. Threats live on edges and trust boundaries, and undrawn feedback loops are where poisoning hides.
3. **Enumerate threats per element.** STRIDE still works for the infrastructure; for the model layer, walk **MITRE ATLAS** (adversarial ML tactics and real-world case studies) and the **OWASP** ML and LLM Top 10 lists as completeness checklists rather than inventing threat categories from scratch.
4. **Rate and decide.** Likelihood times impact on a scale the organization already uses; sophistication is less valuable than consistency. Each accepted risk is a documented decision with a named acceptor.
5. **Register and revisit.** Findings land in a risk register with owner, mitigation, status, and review date, and the register plugs into the Art 9 loop: post-market monitoring (Art 72, a standing obligation in its own right) feeds new entries, incidents reopen old ones, and the cadence is written down.

The failure mode worth naming: threat modeling as an event. A workshop with sticky notes produces a photograph of one afternoon's thinking; Art 9 asks for a process that is still running when the system's context has changed twice. The difference between the two is not effort, it is the register having owners and a review date.

## Gotchas

- **Classifying the model instead of the use.** Risk class attaches to intended purpose in context. Carrying a "low-risk model" label across deployments is a category error, and it is exactly the error the classification exercise in note 06 trains against.
- **Filing Art 9 as a deliverable.** The requirement is a running loop, not a document. The audit tell is timestamps: a risk file last touched at release, for a system in production for a year, answers the question against you.
- **Human oversight as staffing.** Assigning a reviewer satisfies nothing if the interface hides confidence, the queue punishes deliberation, and the override path is undocumented. Art 14 regulates the design; the human is only the last component of it.
- **Accuracy declared without conditions.** A metric without its test distribution, segment breakdown, and validity conditions is an advertisement. Under drift, an unconditional accuracy claim is false the day after it is measured.
- **Security posture without evidence.** For high-risk systems the defense has to be demonstrable: pipeline integrity checks, access logs, adversarial test results. Protection that produced no artifacts does not exist for conformity purposes; note 09 picks up what assessors actually ask for.
- **Treating the geopolitical layer as background noise.** Sovereignty, provenance, and residency clauses arrive in procurement long before any regulator calls. Architects who track only Annex III discover the binding constraint was in the tender, not in the Act.

## See also

- [06_ai_act.md](06_ai_act.md) - the classification mechanics this note takes as given: prohibitions, Annex III, exceptions, provider obligation map
- [03_bias_and_non_discrimination.md](03_bias_and_non_discrimination.md) - Art 10's bias examination in full, and the segment-level measurement discipline accuracy claims depend on
- [08_generative_ai_gpai_and_copyright.md](08_generative_ai_gpai_and_copyright.md) - the systemic-risk tier: what happens when the risk logic meets general-purpose models
- [09_conformity_audit_and_certification.md](09_conformity_audit_and_certification.md) - how Arts 8-15 get verified: conformity assessment, standards, and what an auditor asks to see
- [10_organizational_policies_and_case_studies.md](10_organizational_policies_and_case_studies.md) - the incident policy and QMS that keep the Art 9 loop and the risk register alive organizationally
