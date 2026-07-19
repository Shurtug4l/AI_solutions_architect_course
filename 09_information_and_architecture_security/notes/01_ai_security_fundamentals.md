# AI security fundamentals

## TL;DR

**Cybersecurity** is the branch of computing that protects systems, networks, and data from attacks, damage, and unauthorized access, through techniques, tools, and practices rather than any single product. Its governing rule is the **CIA triad**: **confidentiality** (data stays private), **integrity** (data stays correct), **availability** (data stays reachable), and every control defends at least one of the three. Data is the asset that matters, the "gold mine of the twenty-first century", and AI reshaped both sides of the fight: we now hand information to AI intermediaries that process it on our behalf, attackers use the same AI tools to find flaws, and the classic threats (viruses, trojans, phishing) do not retire, they get new company. Every phase of the **model lifecycle** (development, training, test, deployment) is attack surface: datasets can be stolen or corrupted, **poisoned labels** teach a model to be confidently wrong (label every dog "cat" and it will call a dog a cat), and a small **adversarial perturbation** collapses a classifier's confidence without changing what a human sees. **Vibe coding** adds a new risk class: AI-generated programs shipped by people with no security background, plaintext passwords and known vulnerabilities included. The user-side baseline is prompt hygiene: treat a public LLM as a stranger, share nothing you would not publish (prompts can end up in training data and resurface), and verify what it returns, because the model is not infallible even when the question is harmless.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **Cybersecurity** | Protects systems, networks, and data from attack, damage, unauthorized access | Techniques + tools + practices, not one product |
| **CIA triad** | Confidentiality, integrity, availability, always | Every control maps to at least one letter |
| **Data as the asset** | The gold mine of the twenty-first century | Attacks target data, not code, most of the time |
| **AI as intermediary** | AIs process information on our behalf | Passwords and medical records pasted into chat prompts |
| **Lifecycle attack surface** | All four phases can host dangerous actions | Development, training, test, deployment each need controls |
| **Dataset theft / corruption** | The training set is a target in its own right | Huge datasets, hard to inspect end to end |
| **Label poisoning** | Corrupted labels teach wrong associations | Dog labeled "cat" in training, model says cat forever |
| **Adversarial perturbation** | A small input change collapses model confidence | Dog 41-59%, cat 48-52% on the same perturbed image |
| **Vibe coding risk** | Non-experts ship AI-generated code with zero security requirements | Plaintext passwords, known vulnerabilities, no review |
| **Prompt hygiene** | Share with a public LLM only what you would publish | The six-prompt exercise, graded from grave error to clean |
| **AI fallibility** | Output is plausible, not verified | Generic medical answers used in specialist settings |

## Security did not start with AI

> Cybersecurity is the branch of computing that protects systems, networks, and data from attacks, damage, or unauthorized access. It comprises techniques, tools, and practices to prevent threats and guarantee information security.

Two things in that definition deserve underlining. First, the object of protection is threefold: systems, networks, and above all data, because

> data is considered the gold mine of the twenty-first century.

Second, the means are plural: techniques, tools, and practices. Security is not a firewall you buy, it is a discipline everyone in the loop has to respect, and the human is routinely the weakest link. The deck opens with the Futurama lottery scam (a character "wins" the Spanish national lottery without ever buying a ticket, mails off personal data and money, and the scammers end up owning his house) because the episode is a complete phishing playbook: unexpected prize, manufactured urgency, request for personal information. Nothing about that attack needs AI, and nothing about AI makes it stop working.

## The CIA triad

> The CIA triad must always be respected.

Not the agency, the acronym:

- **Confidentiality**: data is readable only by those entitled to read it.
- **Integrity**: data is correct and has not been tampered with.
- **Availability**: data and the services around it are there when needed.

The triad predates AI by decades, and it maps onto AI systems without modification, which is exactly why it stays the design test. Confidentiality now covers training data and everything users type into prompts. Integrity now covers labels and model weights, not just database rows: a model trained on tampered labels is an integrity failure with no error message. Availability now covers the inference service and the pipeline feeding it. When evaluating any AI-specific control later in this module, the first question is still which letter it defends.

## What AI changes

AI did not rewrite the threat landscape, it stacked a new layer on top of it. The classic problems (viruses, trojans, phishing) remain fully operational; what the deck adds is four structural reasons the AI layer is hard to secure:

- **Autonomy**: these tools act on their own, without a human approving each step.
- **Uninspectable data**: they train on enormous datasets that can be audited only with difficulty, if at all.
- **Dual use**: the same tools help attackers find flaws faster. The capability is symmetric.
- **Velocity**: the field moves fast enough that controls designed this year target last year's systems.

There is also a behavioral shift on the user side. We increasingly interact with AI intermediaries that handle information on our behalf, and we feed them far more than we should: passwords, medical documents, personal details, without really knowing where any of it ends up. The trust model changed faster than the habits did. A generation trained not to email passwords will paste them into a chat window without blinking, because the interface feels like a conversation rather than a data transfer.

## The model lifecycle as attack surface

The deck frames AI development in four phases, each with its own activities and, consequently, its own exposure:

```
  1. DEVELOPMENT           2. TRAINING              3. TEST                4. DEPLOYMENT
  problem and goals        training on train set    final eval on          production integration
  data collection and      loss and optimizer       the test set           performance monitoring
  cleaning                 hyperparameter tuning    metrics analysis       over time
  labeling (supervised)    overfitting prevention   comparison with        periodic retraining
  train/val/test split     (early stopping,         alternative models     on new data
  algorithm choice         regularization)
```

The security reading: dangerous actions are possible in every one of these phases, not just in production. The deck names three risk families as the running examples:

- **Risks in developing the program itself**: insecure code, insecure defaults, whether human-written or AI-generated.
- **Risks that someone steals or corrupts the datasets**: the training set is a high-value target both to exfiltrate (confidentiality) and to tamper with (integrity).
- **Risks produced by AI-generated activity**: attacks and artifacts that AI itself creates.

Mapping the families onto the phases makes the surface concrete. Development is where data collection and labeling fix integrity before any code runs, so a compromised source poisons everything downstream. Training is where poisoned data becomes poisoned behavior, and where compute and weights concentrate enough value to be worth stealing outright. Test certifies the happy path only, because metrics are measured on clean data. Deployment is the exposed surface, where adversarial inputs, drift, and plain abuse of the service arrive.

This is the same lifecycle module 08 treats from the delivery side, viewed through a different lens: there the question was how to build and operate the pipeline, here it is where the pipeline can be attacked. Notes 03 and 04 turn these families into a proper per-phase threat catalog; the point of this note is that the catalog has entries in every column.

## Vibe coding: capability without competence

The deck demonstrates an AI agent producing a working Python script from a natural-language request in seconds, then names the consequence:

> People with little or no computing knowledge can create programs. This is a new risk: people with no experience can create programs that respect no computer-security requirement whatsoever. The risks are extremely high. Everything has to be rethought.

The failure mode is concrete, not hypothetical. A non-expert user has no way to notice that the generated program stores passwords in plaintext or leans on a known vulnerable pattern, so the program and the data inside it are exposed from day one, and nobody involved knows it. What dropped is the barrier to writing code; the barrier to writing secure code did not move. The uncomfortable implication is that security review can no longer assume a developer in the loop who at least knows what a vulnerability is: the review has to move to where the code is produced, or into the tools producing it. Identifying and fixing exactly this class of problem is the stated job of this course module.

## How a classifier sees, and two ways to fool it

A human recognizes a dog and a cat instantly because the brain learned robust features over years. A model does something narrower: it translates the input into numbers and searches for patterns matching what it has already "seen" in training. That difference is the vulnerability. The deck demonstrates two attacks on an image classifier, one blunt, one subtle.

**Poison the labels.** The deck's deliberately absurd hypothesis: during training, declare that every image, dogs included, is a cat. The resulting model will classify a dog as a cat, confidently, forever. Absurd as stated, but the mechanism generalizes to any attacker who can touch a fraction of the training set: the model has no ground truth beyond its labels, so corrupting labels corrupts the learned world. This is data poisoning, and it reframes dataset integrity from a data-quality concern into a security property. A poisoned model does not crash, it just answers wrong with full confidence.

**Perturb the input.** The subtler strategy leaves the training set alone and attacks at inference. Add a small perturbation to the image, one that changes nothing for a human observer, and the classifier's confidence collapses: on the deck's example the model lands at 41-59% dog, 48-52% cat, which is to say it can no longer tell.

> It was enough to insert a "small" perturbation and the AI has great difficulty recognizing the images. This possible flaw could be exploited by cybercriminals.

The standard name is adversarial example, and the deck's framing is the right one: this is not an edge case, it is a flaw, and flaws get exploited. The model learned statistical patterns over pixels, not the concept of a dog, so a perturbation that preserves semantics for humans can move the input across a decision boundary. Testing on clean data measures only the happy path.

The two attacks are worth holding side by side, because they bracket the lifecycle:

```
  POISONING (training time)              PERTURBATION (inference time)
  attacker touches the dataset           attacker touches the input
  corrupted labels -> wrong model        perturbed image -> confused model
  persistent until retrained             per-request, repeatable at will
  invisible to clean-data evaluation     invisible to human review
```

One corrupts what the model becomes, the other exploits what it already is, and neither produces an error message. Note 03 develops both attack classes properly.

## What you type is attack surface too

The deck closes with an exercise: six prompts submitted to ChatGPT, graded for what is wrong with each. Read as a set, they define prompt hygiene along two axes: what goes in (disclosure) and what comes out (trustworthiness).

| Prompt | Verdict | Why |
|---|---|---|
| Contains a password | Grave error | The model is not designed to hold secrets; the prompt may enter training data and the password could be surfaced to another user |
| Contains personal and health information | Grave error | Equivalent to handing the data to a stranger with no control over what they do with it |
| Requests something illegal | Error | The problem is the request itself, before any model behavior |
| Generic medical question, no personal reference | Delicate | No disclosure, but the answer may be wrong; dangerous if used in a specialist setting, the AI is not infallible |
| Draft of a post about to go public on social media | Acceptable | Content about to be published carries no privacy expectation; any bot could scrape it anyway; still judge case by case |
| Fully generic request, no location, nothing personal | Clean | Zero information handed over |

The working heuristic that falls out of the table: treat a public LLM as a stranger with a good memory. Share only what you would publish, assume anything typed can persist and resurface, and verify anything consequential the model returns. Cases one and two fail on input, case three on intent, case four on output trust; the last two show that "safe" is a property of the information flow, not of using AI at all. In an enterprise this intuition stops being personal discipline and becomes policy and tooling, data classification and loss prevention applied to prompts; notes 02 and 05 pick that up.

## Gotchas

- **Treating the CIA triad as compliance vocabulary.** It is the working design test. If a proposed AI control cannot name which of confidentiality, integrity, availability it defends, it probably defends nothing.
- **Assuming AI threats replace classic ones.** Phishing, trojans, and lottery scams still work fine. AI adds attack surface on top; nothing gets retired, and the old attacks now arrive better written.
- **Trusting the dataset because it is yours.** Labels and training data are integrity-critical assets. A poisoned set produces a model that is confidently wrong with no exception raised, which makes the corruption invisible until someone exploits it.
- **Judging robustness by human perception.** A perturbation a person cannot see can flatten a classifier's confidence. Evaluation on clean data says nothing about behavior under adversarial input.
- **Pasting secrets into public LLMs.** A prompt is a data transfer, not a conversation. Passwords and medical records typed into a chat window may end up in training data and resurface for another user.
- **Shipping AI-generated code unreviewed.** Vibe coding hands program creation to people who cannot recognize a vulnerability. The generated script that works is not the same as the generated script that is safe.
- **Taking model output as verified fact.** Even a privacy-clean prompt can return a wrong answer in a convincing tone. Anything feeding a specialist decision needs independent verification.

## See also

- [02_data_security.md](02_data_security.md) - protecting the data side of the triad: what leaves the perimeter through datasets and prompts
- [03_ai_model_security.md](03_ai_model_security.md) - data poisoning and adversarial examples as proper attack classes, beyond this note's two demos
- [04_classic_threats_in_ai_applications.md](04_classic_threats_in_ai_applications.md) - viruses, trojans, and phishing meeting AI systems, the "old threats, new company" half
- [06_ai_architecture_security.md](06_ai_architecture_security.md) - secure-architecture principles applied across the lifecycle phases sketched here
- [../../08_solutions_architectures_design/notes/05_ai_model_lifecycle_pipeline.md](../../08_solutions_architectures_design/notes/05_ai_model_lifecycle_pipeline.md) - the same four-phase lifecycle from the build-and-operate side
