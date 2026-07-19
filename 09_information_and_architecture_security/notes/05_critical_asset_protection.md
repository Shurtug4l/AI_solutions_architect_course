# Critical asset protection

## TL;DR

**A supply chain is every activity, organization, person, and resource between raw materials and the delivered product; software has one too, made of third-party code libraries, external programs, and third-party datasets, and compromising it compromises everything downstream. SolarWinds is the canonical case: one vendor's Orion update carried malware onto the machines of customers worldwide. AI raises the stakes because the critical inputs (datasets, compute) come from suppliers by default, so evaluating the internal work is not enough; the suppliers' work has to be evaluated too. Protection is layered. At the model boundary sit guardrails: post-hoc, black-box mechanisms that monitor, filter, and regulate LLM inputs and outputs (pre-processing, inference control, post-processing) against misinformation, bias, privacy violations, and illegal content, with Llama Guard as the worked example of an LLM-based input-output safety classifier. At the organization boundary sit five practices: a proactive posture that assumes any system can be compromised, monitoring early indicators of compromise in access logs (yours and your suppliers'), quality controls and least privilege on suppliers, certification checks (a payment provider should hold PCI DSS), and honest maintenance of your own security operations. The classification test that ties the section together: an incident is a supply-chain attack when a trusted external component was compromised on its way into your system, not when an internal pipeline failed or your own code exposed a direct vulnerability.**

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **Supply chain** | All activities, organizations, people, information, and resources from raw material to delivered product | In IT: suppliers with access to your systems that you do not fully control |
| **Supply-chain attack** | Compromise a trusted third-party component to reach everyone downstream | SolarWinds Orion: one vendor breached, malware installed at customer sites worldwide |
| **Critical assets** | Third-party code libraries, external programs and software, third-party datasets | For AI, add rented compute: resources you consume but do not govern |
| **Supplier ransomware scenario** | The supplier gets hit, your services go down with it | Encrypted supplier data is your outage, whoever owns the servers |
| **Guardrails** | Post-hoc, black-box mechanisms that monitor, filter, and regulate LLM behavior | Input and output regulation without touching model internals |
| **Input validation** | Screen prompts for malicious intent, inappropriate queries, privacy violations | The filter before the model sees anything |
| **Output moderation** | Scan responses for hallucinations, bias, toxicity, misinformation | The filter before the user sees anything |
| **Llama Guard** | Meta's LLM-based input-output safety classifier | Safe / unsafe verdict per exchange; this section's assigned paper |
| **Proactive posture** | Assume any system can be compromised, look for threats before damage | Timely analysis would have let SolarWinds customers spot the anomalies |
| **IoC monitoring** | Analyze access logs, your own and your suppliers' | An admin login at 3:15 AM on a Sunday deserves an investigation |
| **Least privilege for suppliers** | Each supplier gets only the access its job requires | The cleaning company does not need the vital company data |
| **Certification checks** | Ask suppliers to demonstrate compliance with relevant standards | A payment provider without PCI DSS is a red flag |
| **Own security operations** | Supplier vetting never replaces internal hygiene | 2FA implemented by the provider and actually enabled by staff |

## From logistics to software supply chains

> The supply chain is the system of all activities, organizations, people, information, and resources involved in the entire process, from raw materials to the delivery of the final product to consumers.

The logistics version has recognizable stages (sourcing, production, storage, transport, distribution, retail) and multiple participants at each one. The IT version keeps the shape and swaps the goods: modern systems are complex enough that external personnel need access to internal systems, and those suppliers are parties over which the organization rarely has complete control. That gap between "trusted" and "controlled" is the whole attack surface.

The slides' nefarious hypothesis makes the dependency concrete. A supplier is hit by ransomware; the malware encrypts the supplier's data, possibly the company's too, and either way the company's services end up seriously degraded. Nobody attacked you directly. It does not matter.

SolarWinds is the reference incident. The company produces Orion, a network management product used by millions of customers. Attackers compromised it, and the malware rode the vendor's own distribution channel onto customer machines:

```
  attacker -> vendor build/update system -> legitimate signed update -> customer installs
                                                                        (millions of them)
```

The economics explain the pattern: breaching one well-connected vendor is cheaper than breaching each of its customers, and the update channel arrives pre-trusted. Defenses that key on "untrusted origin" are blind to it by construction.

## Critical assets, and why AI concentrates them

The slides name three categories of critical asset flowing in from outside:

- **Third-party code libraries**: dependencies imported into your builds.
- **External programs and software**: vendor products running inside your perimeter.
- **Third-party datasets**: data you did not produce and cannot fully audit.

The mandatory countermeasures are unglamorous: verify supplier trustworthiness, demand specific guarantees, and keep systems periodically updated. For AI applications the exposure is structurally worse, because the assets an AI system depends on most (datasets, compute) are precisely the ones sourced from suppliers by default. A team that builds on a rented GPU cluster, a hub-downloaded model, and a licensed dataset has outsourced most of its critical path before writing a line of code. The slides' conclusion is blunt: evaluating the internal work is not enough, the suppliers' work must be evaluated with the same seriousness.

## Guardrails: protecting the model boundary

The deck's chosen protection methodology for the model asset is the guardrail layer. It carries a double role: a good practice for anyone developing AI applications, and something you can demand from service providers, which makes it a concrete instance of supply-chain verification.

> Guardrails are mechanisms designed to monitor, filter, and regulate the behavior of LLMs to prevent harmful outcomes such as misinformation, bias, privacy violations, or illegal content.

Two properties define them. They are **post-hoc** safety measures, distinct from anything done during pre-training, and they operate mostly **black-box**: they regulate inputs and outputs without modifying the model's internal workings. That makes them deployable on models you do not own, which is the normal case.

The deck spends a slide pair on the before / after contrast, and the asymmetry is the point:

```
  without guardrails:  prompt ------------------------> model ------------------------> raw output
                       (any request in, any completion out)

  with guardrails:     prompt -> [ filter ] -> model -> [ moderate ] -> vetted output
                       (blocked, rewritten, or redirected on either side of the model)
```

The model in the two rows is identical. Everything that changes sits in the surrounding layer, which is exactly why guardrails can be demanded from a supplier without asking them to retrain anything.

Operationally the layer acts at three points:

```
  user input --> [ pre-processing ] --> LLM --> [ inference control ] --> [ post-processing ] --> user
                  filter inputs            monitor and modify         extra checks,
                  before the model         outputs before             redirects, edits
                  sees them                presentation
```

The key components split along the same boundary:

- **Input validation**: check incoming prompts for malicious intent, inappropriate queries, or privacy violations.
- **Output moderation**: analyze responses for hallucinations, bias, toxicity, or misinformation.
- **Feedback loops**: reinforcement learning techniques that fold moderation outcomes back into better future responses.
- **Customization frameworks**: developers specify the criteria and constraints their specific application needs, because "harmful" is application-dependent.

The lecture's live demo probes ChatGPT's guardrails with questions about a public figure, with an explicit correction attached: guardrails are required to prevent violations against every citizen, not just famous ones. Public figures are simply the easy test case.

### Llama Guard, and vetting a supplier by reading its paper

The worked example is **Llama Guard**, Meta's LLM-based input-output safeguard for human-AI conversations: a classifier model that inspects both the user turn and the model turn and returns a safe / unsafe verdict against a configurable risk taxonomy. The lecture walks both outcomes: a benign exchange classified safe, and a harmful one flagged unsafe together with the violated category, which is what makes the verdict actionable rather than a bare boolean. It is this section's assigned reading, in [../exercises/02_llama_guard_paper/](../exercises/02_llama_guard_paper/); the paper (Inan et al. 2023) is worth the time for how it frames moderation as instruction-following, which is what makes the taxonomy adaptable without retraining.

The deck draws a second lesson from the exercise of reviewing it. Checking that document was itself a partial analysis of a potential supplier: choosing a Llama model with the paper in hand means knowing, with evidence, that mechanisms exist to block unwanted access. Reading a vendor's safety documentation is not paperwork, it is supply-chain due diligence in its cheapest form.

## Five defenses against supply-chain attacks

No single instruction covers the problem; the slides offer five practices, and some deliberately overlap with material from other sections.

1. **Adopt a proactive approach.** Work from the assumption that any system can be compromised, and try to detect threats before they do damage. In the SolarWinds case, timely analysis could have let even the customers discover the anomalies rather than waiting for the vendor's disclosure.

2. **Monitor early indicators of compromise.** Access log analysis is the slides' concrete tool. Their example entry:

   ```
   User: General Director    Login 3:15 AM    Sun 2025-10-23
   ```

   An administrative account authenticating at 3:15 AM on a Sunday is anomalous: possibly a compromised account, certainly worth investigating. If the same session then performs a large data modification or download, the case for a breach strengthens considerably. The often-skipped half of the practice: analyze the suppliers' logs too, because their anomaly is your early warning.

3. **Run quality controls on suppliers.** Map which suppliers are most exposed to security risk, and calibrate the privileges assigned to each. The slides' example is deliberately mundane: the cleaning company probably does not need access to the vital data of the corporate system. Least privilege applies to organizations exactly as it applies to accounts.

4. **Assess the security posture of suppliers and partners.** Check whether they hold the standards and certifications relevant to their role. A payment provider should comply with **PCI DSS**, the Payment Card Industry Data Security Standard: a security standard for companies that process, transmit, or store payment card data, built around 12 requirements organized into six control objectives, aimed at protecting cardholder data and preventing fraud. The generalizable point is the method, not the acronym: certification is a transferable, auditable signal that replaces trust-by-reputation with trust-by-evidence.

5. **Examine the integrity of your own IT security operations.** Knowing the suppliers' security state is essential, but many organizations neglect their own, either because they do not know where to start or because they assume they are too unimportant to be a target. The slides put it starkly: good cybersecurity practice can be the deciding factor between a minor inconvenience and a catastrophic data breach.

The closing example threads the last two together: ask your supplier to implement two-factor authentication (some domain and email providers still do not offer it, which is itself a risk signal), and then make sure internal staff actually enable it. A control that exists but sits unactivated protects nobody.

## Supply-chain attack or not

The section's exercise is a classification drill: five incidents, decide which are supply-chain attacks. The verdicts and their reasoning are where the definition earns its keep.

| Scenario | Verdict | Why |
|---|---|---|
| Popular open-source package republished with code that exfiltrates API keys on import | Supply chain | A compromised third-party library, positioned to be pulled into many downstream applications; the hit point is the package repository |
| IoT firmware patch from an external vendor silently adds telemetry shipping sensitive user metadata to vendor endpoints | Supply chain | The vector is a trusted, authorized software supplier delivering undocumented malicious behavior; the hit point is the third-party update channel |
| Team runs a third-party pre-built Docker image in production; it contains admin tools removed from the official build, acting as an unauthenticated backdoor | Supply chain | An external component (the container image) entered the production pipeline carrying a preconfigured backdoor |
| Analytics engine degrades after retraining; the cause is labeling errors from a bug in the internal ETL pipeline | Not supply chain | The failure is generated internally; it is a data quality problem, with no compromised external component anywhere in the chain |
| Web application suffers XSS because a form does not sanitize user input; attacker steals session cookies | Not supply chain | A direct application vulnerability exposed at runtime, unrelated to compromised dependencies, builds, firmware, or containers |

The discriminating test is narrow on purpose: was a **trusted external component compromised on its way into your system**? Internal pipeline failures and directly exploitable application bugs can be just as damaging, but they call for different responses (data quality process and secure coding respectively, not supplier incident response), so the taxonomy is operational, not academic. Notice also that the second scenario counts even if the vendor added the telemetry deliberately rather than being breached: from the customer's side, unwanted behavior arriving through a trusted channel is the same failure mode either way.

## Gotchas

- **Equating trusted with safe.** SolarWinds malware arrived as a legitimate signed update from a known vendor. The trust you place in a channel is precisely the asset the attacker monetizes, which is why "verify the supplier" cannot stop at the logo.
- **Vetting suppliers once, at onboarding.** A supplier's security posture is a time series, not a checkbox. The proactive stance in the slides implies periodic re-checks, updated systems, and renewed certification evidence.
- **Treating guardrails as a model property.** They are post-hoc and black-box by definition: an external layer around the model, not a feature baked into it. Buying a "safe model" does not remove the need for input validation and output moderation components in your own architecture.
- **Watching only your own logs.** The slides insist on analyzing supplier logs as well. A supplier-side anomaly is the earliest indicator of compromise you will get for an attack that has not reached you yet.
- **Uniform supplier privileges.** Granting every vendor broad access because contracts are easier that way inverts point 3. Exposure should be proportional to function; the cleaning company example is silly precisely so the principle sticks.
- **Calling every failure a supply-chain attack.** Mislabeled training data from an internal ETL bug is a quality incident and an XSS hole is an application vulnerability. Misclassifying them routes the response to the wrong team and leaves the real weakness open.
- **Controls implemented but not enabled.** The 2FA example cuts both ways: demand the capability from the supplier, then verify internal adoption. Between "available" and "active" sits most of the residual risk.

## See also

- [02_data_security.md](02_data_security.md) - third-party datasets are one of the three critical asset classes; their protection and quality controls live here
- [03_ai_model_security.md](03_ai_model_security.md) - the model-side attacks (poisoning, evasion, extraction) that guardrails and supplier vetting are defending against
- [04_classic_threats_in_ai_applications.md](04_classic_threats_in_ai_applications.md) - the XSS scenario from the exercise belongs to this family: direct application vulnerabilities, not supply chain
- [06_ai_architecture_security.md](06_ai_architecture_security.md) - where the guardrail layer and the trust boundaries around third-party components sit in the overall architecture
- [08_ai_forensics.md](08_ai_forensics.md) - the log analysis sketched in the IoC practice, done properly: evidence collection and investigation after the anomaly fires
