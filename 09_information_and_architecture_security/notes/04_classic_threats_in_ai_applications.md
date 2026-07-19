# Classic threats in AI applications

## TL;DR

**AI systems are still software, so every classic threat still applies**: malware (trojans, ransomware, backdoors), phishing, DDoS, man in the middle, SQL injection, brute force. The previous sections covered the AI-native attacks; this one closes the loop on the traditional ones, and on the uncomfortable twist that **AI now amplifies them**. A **trojan** hides malicious code inside a program the user willingly installs; a **backdoor** is a hidden rear entrance giving an attacker remote access. Ransomware like **WannaCry** encrypts the disk and demands payment, and the **PromptLock** prototype shows the next step: a local LLM that scans the filesystem and generates unique encryption code per infection, defeating signature-based detection outright. Banking trojans **Maverick** (WhatsApp-delivered, AI-assisted code development) and **Herodotus** (mail/SMS link, Android accessibility-service abuse, overlay screens) show the same amplification in the wild. Defenses stack the usual layers, IAM, least privilege, behavioral monitoring, antivirus, patching, but each layer leaks, so **user attention plus good practice remains the best protection**. The section closes with a discrimination skill every AI architect needs: telling an ML **backdoor** (fixed trigger, deterministic flip) apart from **data drift** (population-wide degradation) and **adversarial evasion** (per-example optimized perturbation), because the three look similar from the outside and demand entirely different responses.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **Classic threat list** | Malware, phishing, DDoS, MitM, SQL injection, brute force | AI systems inherit all of them, none retire |
| **Trojan** | Malicious code hidden inside a "good" program the user installs | The Pokemon Go Guide app pushing adware |
| **Ransomware** | Encrypts the disk, demands payment to decrypt | WannaCry is the canonical case |
| **PromptLock** | Prototype ransomware using a local LLM to generate code at runtime | Each infection is unique, signatures never match |
| **Backdoor (system)** | Hidden rear entrance giving remote access to the victim's machine | Countered with IAM, behavioral checks, least privilege |
| **Maverick** | AI-assisted banking trojan spread via WhatsApp links (October 2025) | Keylogging, screen lock on bank sites, phishing overlays |
| **Herodotus** | Banking malware abusing Android accessibility services | A bank app asking for accessibility is the tell |
| **Overlay attack** | Fake screen drawn on top of the real app to harvest credentials | Enabled by the permissions the user granted |
| **Least privilege** | Grant only the access a component (or app) actually needs | "Why would this app need that permission?" |
| **ML backdoor / trojaned model** | Trigger planted in training forces a chosen output | Fixed, repeatable trigger; normal behavior without it |
| **Data / concept drift** | The world changes, model quality degrades everywhere | Population-level errors tracking a real event |
| **Adversarial evasion** | Test-time input optimized to fool the model | Imperceptible per-example noise, no fixed trigger |
| **Signature-based detection limit** | AV matching known patterns misses freshly generated code | AI-written malware never looks the same twice |

## The classic list still applies

The earlier sections of this module covered threats born with AI: poisoning, model theft, prompt injection. This section is the reminder that the traditional catalogue never went away:

- **Malware**: trojans, ransomware, backdoors, the focus of this deck.
- **Phishing**: credential theft through impersonation, now the delivery channel of choice for the malware below.
- **DDoS**: flooding a service, and an inference endpoint is an expensive service to flood.
- **Man in the middle**: interception of traffic between client and server.
- **SQL injection**: malicious input reaching a query, the ancestor of prompt injection in spirit.
- **Brute force**: exhaustive credential guessing.

An AI application is a web service, a data store, an authentication layer, and a model. The first three are attacked exactly as they were in 2015. Budgeting all the security effort on the model while the login page accepts weak passwords is a category error the classic list exists to prevent.

## Trojans and ransomware

> A malware is inserted into a "good" program that the user unknowingly downloads.

The trojan takes its name from the Trojan Horse: the payload rides inside something the victim wants. The slides' example is instructive precisely because it is banal: the "Guide for Pokemon Go" app, downloaded from official stores, which once installed pushed unwanted apps and advertising onto the device. No exploit, no zero-day, just a payload hidden behind a desirable wrapper.

The same logic threatens AI products directly. A user downloading an AI-powered application can download a trojan with it, and the AI hype cycle produces exactly the flood of "wanted" apps that trojan authors need for cover.

Ransomware is the trojan's most profitable payload:

> This malware encrypts all the data on the disk and demands a ransom to recover it.

WannaCry is the deck's example, and a fair one: the 2017 outbreak locked hundreds of thousands of machines, hospitals included, and remains the reference picture for what disk encryption at scale does to an organization.

## AI as an attack amplifier: PromptLock

The deck's most forward-looking case. PromptLock is a ransomware prototype that embeds a local language model in the attack loop:

```
  User runs a local AI language model
        |
        v
  Malware silently walks the filesystem
        |
        v
  LLM generates code in real time and
  analyzes file contents
        |
        v
  Encrypts the files that matter most
```

Two properties make it a different animal from WannaCry:

- **Targeting**: the model reads file contents and picks the valuable ones, instead of encrypting blindly.
- **Adaptation**: scripts are generated dynamically, so every infection can look unique. Signature-based antivirus and recurring-behavior heuristics have nothing stable to match.

> The ransomware no longer follows a fixed script: it can reinvent itself with every infection.

The slides are explicit that PromptLock is only a prototype, and equally explicit that it is an alarm bell: current tooling will not be sufficient, and defense has to turn proactive rather than reactive. From a practitioner angle this is the malware-side mirror of everything this module teaches on the defense side, the attacker gets the same generative leverage we do.

## AI-powered banking trojans: Maverick and Coyote

The amplification is not hypothetical. Maverick, identified in October 2025 and related to the Coyote family, is a banking trojan spread through malicious WhatsApp links; one click and the attacker's system takes control of the machine. Its capabilities read like a checklist of financial-fraud tradecraft:

- Captures screenshots and logs keystrokes.
- Controls the mouse or locks the screen when the victim visits their bank's site.
- Overlays phishing pages on top of the real ones to steal usernames and passwords.
- Monitors activity on 26 Brazilian bank sites, six cryptocurrency platforms, and a digital payment site, which is why its spread is so far concentrated in Brazil.

The novelty flagged by the deck: Maverick uses AI for certificate decoding and for general code development. The consequence generalizes beyond this one sample: if malware development is AI-assisted, new and more dangerous variants can appear continuously, at a cadence human-written malware never reached.

The countermeasures the slides list are deliberately unglamorous: verify that the message sender is who they claim to be, audit and update installed software periodically, run antivirus and monitoring tooling. Nothing AI-specific, because the entry point is not AI-specific either, it is a link in a chat message.

## Backdoors

> Backdoors are "rear" communication doors that give an attacker remote access to the victim's computer system.

Where a trojan is a delivery mechanism, a backdoor is a persistence mechanism: a hidden channel that bypasses normal authentication. Backdoors can always turn up, planted by malware, left by a compromised dependency, or shipped in a poisoned model, so the defense posture assumes their existence rather than hoping to prevent it:

- **Access control (IAM)**: identity and permission management as the front line.
- **Continuous behavioral verification**: watch what programs actually do, not what they claim to do. Against AI-generated payloads with no stable signature, behavior is the only observable left.
- **Least privilege**: every component gets the minimum access it needs, so a backdoor inherits a small blast radius instead of the keys to everything.

## Anatomy of an infection: Herodotus

The deck walks through Herodotus, a banking malware that reached Italy, as a detection case study. The kill chain has two points where an attentive user stops it cold:

```
  Mail / SMS with a link
        |
        |  ALERT 1: check the link, verify the sender.
        |  Banks do not ask you to follow external links.
        v
  App downloaded and installed
        |
        |  ALERT 2: the app requests Android
        |  accessibility services. Why would a
        |  banking app ever need those? Deny and stop.
        v
  Accessibility granted -> THE DAMAGE IS DONE
        |
        v
  Overlay screens on top of the real apps,
  full remote control of the device
```

The accessibility-services angle is the interesting part. Those APIs exist so assistive tools can read the screen and act on the user's behalf; granted to malware, they hand over exactly that power. It is least privilege applied to end users: an unexplained permission request is a red flag regardless of how legitimate the app looks.

The slides then stress-test the standard defenses and find each one leaking:

- **Antivirus**: can scan and block the malicious link, but AI-generated fresh code can slip past it, so it cannot be the only layer.
- **Updates and patches**: certified app developers and OS vendors close holes with security updates, but a patch for the current campaign may simply not exist yet.

> User attention, combined with the good practices described, is the best protection.

That closing line is not resignation, it is an architecture statement: when every technical layer has a known bypass, the human check is a load-bearing control, and training it is part of the system design.

## Backdoor or not: a discrimination drill

The section's exercise presents five ML incidents and asks which are trojans or backdoors. The value is in the differential diagnosis, because three distinct failure modes produce superficially similar symptoms:

| Scenario | Verdict | Why |
|---|---|---|
| Road-sign classifier reads any sign with a small yellow sticker as "Limit 50" | Backdoor | Fixed trigger planted via a few training examples; deterministic label flip; normal behavior without the trigger |
| Voice assistant executes commands on an inaudible ultrasonic sequence | Backdoor | A specific, repeatable external trigger activates privileged behavior; the pattern matches no human phrase; plausibly planted in the model or firmware |
| Fraud model's false positives and negatives rise after customers change spending habits post-holidays | Not a backdoor: data / concept drift | No single trigger; generalized degradation across the population, feature statistics shifting in step with a real external event |
| Sentiment model rates any comment containing "#sunrise42" as strongly positive | Backdoor | Classic token-based text backdoor: a discrete trigger forces a target class regardless of content; few training occurrences, consistent inference effect |
| Quality-control vision model rejects perfect parts under imperceptible, numerically optimized pixel noise | Not a backdoor: adversarial evasion | Perturbations are optimized per example at test time; no fixed trigger; the weakness is the decision surface itself, not an implanted rule |

The distilled rule set:

- **Fixed, repeatable trigger + deterministic output flip + clean behavior otherwise** = backdoor implanted at training time. Response: audit training data provenance, retrain from trusted data.
- **Broad degradation correlated with a real-world change** = drift. Response: monitoring caught it working as intended, retrain on recent data. No attacker involved.
- **Per-example crafted perturbations at inference time** = evasion. Response: adversarial robustness work, input sanitization. The training set was never touched.

Misdiagnosing across these categories wastes the response: retraining fixes drift but not a poisoned pipeline, and hunting for a training-set trigger is futile when the attack is test-time optimization.

## Gotchas

- **Securing only the AI-specific surface.** The model gets threat-modeled while the app ships with phishable credentials and injectable queries. Attackers take the cheapest door, and the cheapest door is usually a classic one.
- **Trusting signature-based antivirus against AI-generated malware.** PromptLock and Maverick generate code per infection; there is no stable signature to match. Behavioral monitoring is the fallback observable, and even that needs tuning.
- **Reading "prototype" as "not my problem".** PromptLock does not exist in the wild at scale; the deck's point is that the technique is proven and the defensive tooling gap is already visible. Proactive posture beats waiting for the first campaign.
- **Confusing a backdoor with drift.** Both degrade outcomes, but a backdoor is a deterministic trigger rule and drift is a statistical shift. The first is an incident with an adversary; the second is maintenance. Different playbooks, different urgency.
- **Confusing a backdoor with adversarial evasion.** A backdoor is planted during training and fires on a fixed trigger; evasion is computed at test time against a clean model. Cleaning the training set only helps with the first.
- **Granting permissions because the app asked.** Herodotus is powerless until the user enables accessibility services. Any permission request without an obvious need is the second alert of the kill chain, and the cheapest place to stop it.
- **Treating patching as sufficient.** Updates close known holes; an active campaign may exploit one with no patch available yet. Layers, not silver bullets.

## See also

- [01_ai_security_fundamentals.md](01_ai_security_fundamentals.md) - the AI-native threat landscape these classic threats sit alongside
- [03_ai_model_security.md](03_ai_model_security.md) - poisoning, model backdoors, and adversarial attacks in depth, the ML side of this deck's exercise
- [05_critical_asset_protection.md](05_critical_asset_protection.md) - IAM and least privilege as systematic controls, here invoked against backdoors
- [06_ai_architecture_security.md](06_ai_architecture_security.md) - layered defenses at architecture level, the answer to every single-layer bypass in this deck
- [08_ai_forensics.md](08_ai_forensics.md) - post-incident analysis when a trojan or backdoor has already fired
