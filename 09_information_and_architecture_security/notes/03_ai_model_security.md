# AI model security

## TL;DR

**An ML model can be attacked at every stage of its life.** At **training time**, **data poisoning** corrupts the training set so the model learns wrong behavior, either across the board (**nontargeted**) or on chosen inputs only (**targeted**). At **inference time**, an **evasion attack** feeds the trained model **adversarial examples**: legitimate-looking inputs carrying a crafted, near-invisible perturbation that flips the prediction, the panda that classifies as a gibbon, the fraudulent transaction that looks normal. The **query interface** is a third surface. **Model inversion** interrogates the model until it leaks the training data behind it (a privacy breach), and **model extraction** rebuilds a working clone from request-response pairs (intellectual property theft). The deck's defenses: IAM and strict dataset access control against poisoning and inversion, per-user **query limits** with behavioral anomaly monitoring against extraction, **watermarking** and **fingerprinting** to prove the provenance of outputs and models after the fact. One discipline ties it together: not every wrong prediction is an attack. False positives and false negatives are the normal errors of a statistical component; the security question is whether an adversary induced them.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **Data poisoning** | Corrupt training data so the model learns wrong behavior | Happens at training time; degraded or selectively wrong model |
| **Targeted poisoning** | Change behavior on chosen inputs only | Aggregate metrics stay green, one face is never recognized |
| **Nontargeted poisoning** | Degrade overall accuracy, precision, recall | Noise and irrelevant points injected into the training set |
| **Adversarial example** | Input with a crafted, near-invisible perturbation | Panda plus noise reads as gibbon |
| **Evasion attack** | Use adversarial examples at inference to dodge classification | Training data untouched; malicious input passes as benign |
| **Model inversion** | Recover training data through the model's answers | Repeated synthetic queries leak real people's attributes |
| **Model extraction** | Rebuild the model from query-response pairs | Abnormal query volume, systematic input sweeps |
| **Query rate limiting** | Cap and profile queries per user | Over 300 q/hour suspicious, over 1,000 probable scraping |
| **Watermarking** | Imperceptible mark proving an output's origin | "Like signing a painting"; LinkedIn labeling AI images |
| **Fingerprinting** | Identify a model by its characteristic behavior | Probe a suspected clone, compare answers with the original |
| **False positive / negative** | Ordinary classification error, no adversary | Mask-blocked employee, missed tumor on a radiograph |

## One model, three attack surfaces

The deck opens by returning to the module's opening hypothesis: an antivirus uses AI, the model is trained to recognize malware, and a criminal slips perturbed data into the training phase. Malware starts coming back "clean". That single scenario contains the whole lesson, because every attack in this deck targets a specific stage of the model lifecycle.

```
  training data ---> training ---> deployed model ---> outputs
        ^                               ^                 ^
        |                               |                 |
  DATA POISONING                EVASION ATTACK       WATERMARKING
  corrupt what the              adversarial inputs   (defense: mark
  model learns from             fool the trained      what the model
                                model                 produced)

                                MODEL INVERSION
                                queries leak the
                                training data

                                MODEL EXTRACTION
                                queries rebuild
                                the model itself
```

A symmetry worth keeping in mind: poisoning and evasion attack the **integrity** of predictions, inversion and extraction attack **confidentiality** through the legitimate query interface. The second pair needs nothing beyond ordinary API access.

The deck's practical sections drive the phase distinction home with a deliberately simple move: the same Python-level perturbation is applied first to training data, then to prompt data at test time. Identical operation, different attack class. Injected before training it is poisoning and reshapes what the model learns; injected at inference it is an adversarial example and fools what the model has already learned. The phase, not the technique, determines the attack.

## Data poisoning

> The criminal inserts distorted inputs that will influence the model's capabilities. This happens in the training phase.

The consequences chain directly: the model operates incorrectly or imprecisely, decisions based on it go wrong, and trust in the AI erodes. The deck's security-flavored example is a network monitoring model: attackers introduce data that lowers its accuracy at spotting suspicious activity, so real threats get harder to recognize.

Two variants:

- **Targeted attacks** influence the model's behavior on specific inputs, for example making a facial recognition system fail on one particular individual, without significantly degrading overall performance. The dangerous property is stealth: aggregate metrics keep looking healthy while the implanted behavior sits waiting.
- **Nontargeted attacks** reduce the model's general accuracy, precision, or recall by injecting noise or irrelevant data points, degrading performance across many inputs.

The defense the deck names is preventing unwanted access to the dataset, applying the IAM procedures from the data security section (note 02). Necessary, and not sufficient. The exercise's spam scenario shows poison arriving through the front door: a filter periodically retrained on the emails it labels non-spam will learn from attacker-crafted messages that no access control ever sees, because they enter as ordinary traffic. Any self-retraining loop promotes user-influenced data into training data, and that loop needs validation and provenance checks of its own.

## Evasion attacks and adversarial examples

The classic demonstration: take a panda photo, add noise a human cannot perceive, and the network classifies it as a gibbon. The perturbed input is an **adversarial example**; using one against a deployed model is an **evasion attack**. Every evasion attack uses adversarial examples: the example is the artifact, the evasion is the act.

> An evasion attack is an attack against a machine learning model in which the attacker modifies the input data so as to evade the model's correct classification, without altering the training data.

Its defining properties:

- It happens at inference, not during training.
- It aims to get malicious samples classified as benign.
- It requires no access to the training data.
- It exploits total or partial knowledge of the model (white-box down to black-box).

The deck's examples are the realistic ones: a fraudulent transaction lightly modified to appear legitimate, malware camouflaged so an ML-based antivirus misses it. Against poisoning the contrast is sharp on three axes:

| | Data poisoning | Evasion attack |
|---|---|---|
| When | Training (or retraining) | Inference, on the trained model |
| What is touched | The training set | A single legitimate input, often imperceptibly |
| Goal | Degrade or bias what the model learns | Make the model err on a specific input, training data intact |

The hands-on companion [../exercises/01_adversarial_noise_on_images/](../exercises/01_adversarial_noise_on_images/) blends uniform random noise into a cat photo at four alpha levels (5% to 60%). Random noise is the baseline intuition, not the attack: at 5% nothing changes for a human and little for the model, and by the time a classifier suffers, the image is visibly ruined. A crafted perturbation (FGSM-style, computed from the model's gradient) flips the prediction with far less visible change, because it spends its entire budget along the direction the model is most sensitive to. "Adversarial" means optimized, not merely noisy.

## Model inversion

Another form of data theft, aimed this time at the training set: the attacker steals through the model, recovering the data it was trained on.

The deck's reverse engineering demo makes the threat concrete. A face recognition agent identifies the students of a school. The attacker wants the face of a student, Mario, and crucially has never seen it. By querying the model and studying its responses, they reconstruct an image of Mario that the model itself confirms. The practice section carries the sober version: a medical prediction model exposed as a web service returns disease probabilities, and an attacker feeding it synthetic inputs recovers, with some precision, sensitive information about real people in the training set.

The uncomfortable implication: if personal data went into training, a queryable model is a potential personal data breach in its own right, not just an IP asset. The deck's defenses mirror the poisoning ones, controlling who reaches the dataset through IAM. Since inversion works entirely through legitimate queries, the monitoring and rate limiting of the next section apply here just as much as to extraction.

## Model extraction and intellectual property

An inadequately protected model can be reconstructed and reused by someone who never paid to build it. The mechanism has a name, **model extraction**: the criminal analyzes requests and responses and rebuilds an identical or very similar model. The deck lists the fallout as regulatory problems, copyright violation, and image and economic damage. Someone else funded the data, the compute, and the expertise; the clone competes with the original at marginal cost.

Countermeasures start at the query stream: analyze prompts for anomalies and limit queries per user. The reference bands:

| Band | Queries per hour |
|---|---|
| Normal | 60-300 (1-5 per minute) |
| Suspicious | over 300 |
| Very high risk | over 1,000, probable scraping or bot |

The deck adds the sharper point itself: behavior matters more than the count. 500 requests in 5 minutes is far more suspicious than 500 spread evenly over one hour. In practice the absolute thresholds are illustrative and should be calibrated on real traffic; burst shape and per-user baselines carry more signal than any fixed hourly number.

## Watermarking and fingerprinting

Rate limits slow extraction down; watermarking addresses what happens after. A **watermark** is a set of signals, often imperceptible to the human eye, embedded in outputs to indicate they were generated by that specific model.

> Like signing a painting.

The deck's in-the-wild example is LinkedIn, which labels AI-generated images with a content credential. **Fingerprinting** is the companion concept for the model itself: identifying a model from its characteristic behavior, so a suspected clone can be probed and compared against the original.

Both are attribution controls, not preventive ones. They stop neither extraction nor misuse; they make provenance provable when the dispute reaches a court, a regulator, or an incident review. That is precisely the layer copyright and compliance claims need, and it only works if it was in place before the theft.

## Attack or ordinary error: six scenarios

The deck closes with a classification drill: six scenarios, name the attack if there is one. Worth attempting before reading the verdicts.

| # | Scenario | Verdict |
|---|---|---|
| 1 | Spam filter periodically retrained on emails it labels non-spam; attacker crafts deceptive ads that pass as legitimate and enter the training set | Data poisoning |
| 2 | Cat photo, pixels altered invisibly to a human; model says dog | Adversarial example (evasion) |
| 3 | Medical model as a web service; repeated synthetic queries recover sensitive data about real patients | Model inversion |
| 4 | Face recognition rejects an authorized employee wearing a mask and flags an intruder | False positive, no attack |
| 5 | Radiology model misses an evident tumor, reports the image as clean | False negative, no attack |
| 6 | Fraudster tunes transfer amounts and frequency until the movements look normal and go unflagged | Evasion attack |

Two of the six contain no adversary, and that is the drill's real lesson. A model flagging an intruder who is not there (4) or missing a tumor that is (5) is doing what statistical classifiers do: erring at some rate. The consequences can be severe, the radiology false negative especially, but the remedy is model quality work (thresholds, retraining, better data), not incident response. Before treating a misclassification as hostile, ask whether the error was induced: is there a perturbation, a poisoned feedback loop, an unusual query pattern? Adversarial intent is a hypothesis to verify, not a default.

## Gotchas

- **Poisoning and evasion look alike, and are not.** Both can involve a perturbed image, but poisoning corrupts what the model learns while evasion fools what it has already learned. The defenses differ accordingly: data governance and access control on one side, input hardening and anomaly detection on the other.
- **IAM does not close the poisoning surface by itself.** Locking the dataset store stops direct tampering. A self-retraining pipeline still ingests poison as ordinary user traffic, as the spam scenario shows; the retraining set needs its own validation and provenance.
- **"A perturbed input would be visible" is false comfort.** The exercise's random noise must be heavy before anything changes; a gradient-crafted perturbation stays invisible. Judging adversarial risk by how random noise behaves underestimates the attacker by orders of magnitude.
- **Inversion and extraction use only legitimate access.** No breach, no malware, just queries. If monitoring covers infrastructure but not the query stream, the model can be inverted or cloned without a single alert firing.
- **Watermarking prevents nothing.** It is an attribution control: it proves provenance after the theft. Paired with rate limits and query anomaly monitoring it completes a defense; alone, it documents a loss.
- **Calling every model failure an attack.** Two of the deck's six drill scenarios are plain false positives and negatives. Misdiagnosing them as attacks burns the incident pipeline and hides the real fix, which is model quality.

## See also

- [01_ai_security_fundamentals.md](01_ai_security_fundamentals.md) - the module's threat map this deck drills into; the antivirus hypothesis first appears there
- [02_data_security.md](02_data_security.md) - the IAM procedures the deck names as the first line of defense against poisoning and inversion
- [04_classic_threats_in_ai_applications.md](04_classic_threats_in_ai_applications.md) - the application-layer threats around the model, complementing the model-native ones covered here
- [05_critical_asset_protection.md](05_critical_asset_protection.md) - the model as a critical asset; extraction and cloning are the theft that protection exists for
- [08_ai_forensics.md](08_ai_forensics.md) - the investigation side, where the query logs from the extraction countermeasures become evidence
