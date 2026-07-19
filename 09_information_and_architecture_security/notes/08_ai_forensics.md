# AI forensics

## TL;DR

**Digital forensics** is the scientific discipline that **identifies, acquires, and analyzes digital evidence while preserving it from alteration**. Both words in the name are load-bearing: **scientific** means repeatable (same method, same result, anyone can redo it), **evidence** means the output must survive a courtroom. The workflow runs through **four phases**: **identification** (map every device that could hold evidence, no rushing, no improvised tools), **acquisition** (bit-for-bit conforming copies, hashes to prove integrity, never write to the source), **analysis and evaluation** (physical, logical, or live), **presentation** (a report readable by non-experts). AI enters the picture twice. As a **tool**, it accelerates the sifting of enormous evidence volumes, at the cost of an aseptic reading that misses the emotional nuance a human investigator would chase. As the **object under investigation**, because models fail for reasons (poisoned training data, perturbed inputs, tampered logs) that only a forensic reconstruction can attribute: the module's worked case follows a classifier that suddenly misclassifies, and dataset, git history, and logs answer what happened, how, when, and who. The deliverable is an **incident report in plain language**: "data poisoning" means nothing to a decision maker, while "the system can no longer guarantee reliable decisions" lands, and it frames the damage correctly as a **reliability problem, not a bug**. The posture throughout: forensic analysis never says "in my opinion", it says "based on this evidence, this is what happened".

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **Digital forensics** | Identify, acquire, analyze digital evidence, preserving it from alteration | Repeatable method, court-grade output |
| **The four phases** | Identification, acquisition, analysis and evaluation, presentation | Skip or rush one and the evidence loses value |
| **Identification** | Map every device that could contain evidence | PCs, SD cards, SIMs... and the DVD with a movie cover |
| **Acquisition** | Bit-for-bit copy conforming to the original | Hash computed at seizure, recomputable by anyone |
| **Physical / logical / live analysis** | Whole drive vs filesystem-aware vs running system | Physical is thorough and very slow; live captures processes and connections |
| **Chain of custody discipline** | Never alter the source, document every operation | Video-record the acquisition when possible |
| **AI as forensic tool** | Speeds up analysis of huge data volumes | No empathy: misses the nuance a human would probe |
| **AI forensics** | The same four phases applied to a misbehaving model | Dataset, git repo, training server, logs as evidence sources |
| **Data poisoning** | Training data altered to corrupt model behavior | Distribution shifts, near-duplicates, targeted class impact |
| **Data drift vs attack** | Not every degradation is malicious | Gradual decay, coherent data, clean logs: that is drift |
| **Incident report** | Findings translated for non-technical readers | Jargon out, reliability framing in |
| **Evidence-based conclusion** | Reconstruction, not opinion | Repeatable, verifiable sequence of events |

## What digital forensics is

> Digital forensics is the scientific discipline that identifies, acquires, and analyzes digital evidence, preserving it from alteration.

The definition packs two constraints. **Scientific** means the method is repeatable in the Galilean sense the slides nod to: a second analyst with the same acquisition must reach the same findings. **Evidence** (the legal kind) means every step has to guarantee admissibility in court, which disciplines the whole process even when no trial is in sight, because an internal case can escalate into a legal one at any point.

The scope is wider than cybercrime. The same analysis serves internal corporate investigations, damage assessment, fraud, policy violations, and ordinary judicial cases where a device happens to hold the decisive trace. The deck's real-world example is an Italian murder case (the Garlasco case, via a Corriere della Sera article) where computer evidence and its handling became central to the verdict.

## The four phases

```
  Identification  ->  Acquisition   ->  Analysis and   ->  Presentation
  (map every          (conforming        evaluation         (report for
   device that         copies,           (physical,          the widest
   could hold          hashes, no        logical,            possible
   evidence)           writes)           live)               audience)
```

**Identification** comes first: map every device that might contain evidence before touching anything. PCs, SD cards, SIM cards, external media. The slides issue three warnings that read like scars: do not rush, do not improvise expertise on systems you do not know, do not use improvised tools. And do not trust the obvious location: the most important evidence is not necessarily on the computer where everyone assumes it is. The deck's example is a DVD hiding behind the cover of a famous film.

**Acquisition** produces copies that must conform to the original. The operating rules:

- Never alter the data source: no writes to the media under examination.
- Record every characteristic of the device, BIOS data included (the slides mark BIOS as not strictly necessary, but cheap to note).
- Do not contaminate the device physically either: dust and classic traces belong to the investigation too.
- Create a bit-for-bit copy, as close to identical to the original as technically possible.
- Compute a hash of the acquisition. This is what makes the phase scientific: anyone can recompute it later and confirm nothing changed between seizure and courtroom.
- When possible, video-record the whole operation.

**Analysis and evaluation** starts only once acquisition is closed, and comes in three flavors:

- **Physical analysis**: recover data across the entire drive ignoring the file system. Exhaustive and very slow.
- **Logical analysis**: recover files through the installed operating system and its file system.
- **Live analysis**: born to capture a running system on the fly: users, processes, network connections that would vanish at power-off.

**Reporting and presentation** closes the loop: document every operation performed, reconstruct the sequence of events, and write the report so that the widest possible audience can follow it. Readability is not a courtesy, it is part of the evidentiary value.

## AI on both sides of the investigation

AI shows up in forensics in two directions. As a **tool**, it addresses the volume problem: modern investigations mean sifting enormous datasets, and AI shortens the triage dramatically. The deck flags the cost with an unusual word for a security course: **empathy**. An AI reads the material aseptically; a human investigator picks up emotional nuance or discomfort in a message thread and knows to dig there. The practical stance is to treat AI triage as a lead generator, never as a conclusion, since conclusions need the evidence chain.

The second direction is the one that names the module: the same forensic discipline applied when the suspect artifact is an **AI model**. A model that misbehaves is a system whose failure has causes sitting in datasets, code, and logs, such as corrupted data slipped into training, and those causes can be identified, acquired, and analyzed like any other digital evidence.

## Worked case: the poisoned classifier

The scenario the lessons build on: a company's image model suddenly stops classifying cats correctly. Nobody knows why. Decisions that used to be right are now wrong, and the suspicion is that the training data was altered: **data poisoning**. (The deck plants the seed itself, reusing an image perturbation deliberately introduced in an earlier module exercise.)

Phase 1, identification: where could evidence live?

| Evidence source | Why it matters |
|---|---|
| Training dataset | May have been altered |
| Git repository | Shows who changed what |
| Training server | May hold previous versions |
| Logs | May record accesses and modifications |

Phase 2, acquisition: copy the datasets without modifying them, clone the code as it stands (the git repository ideally), save logs and files exactly as found, and hash everything to prove later that nothing changed in your hands.

Phase 3, analysis: the classifications flip after a perturbation, and corrupted images sit in the training set. The repository contains the script that perturbs the images, and git answers the attribution questions natively: who modified the code, when, what changed, in what order. The perpetrator who pushed the perturbation code falls out of the commit history.

Phase 4, evaluation: each acquired object proves one link of the chain.

| Artifact | What it proves |
|---|---|
| Dataset | The data was altered |
| Code | How it was altered |
| Git history | When, and by whom |
| Model | What effect the alteration had |

> Forensic analysis does not say "in my opinion". It says "based on this evidence, this is what happened".

What happened, how, and who did it: at that point the technical task is done. Disciplinary or legal follow-up belongs to management, not to the analyst.

## Writing the incident report

The findings become a document, and the document has one hard requirement: it must be readable by people with no IT background who need to understand what happened. Using "data poisoning" in this phase may carry zero meaning for a decision maker. The deck iterates the phrasing until it lands, settling on:

> An error in the data preparation phase influenced the training of the model. The anomaly was identified by observing results inconsistent with those expected.

The explanation walks the reader through the system in three plain steps: there is source data, there is an automatic process that prepares it, the model learns from that data. After the malicious change, part of the data looked normal but contained incorrect information, and the system learned from it too. The consequence is the sentence that actually matters to the business:

> The system, in this state, cannot guarantee reliable decisions in all foreseen situations.

Impacts: wrong decisions, loss of trust, operational risk, problems with customers. The nuance worth spelling out is that not everything the model does is wrong, but full trust is gone, and that partial unreliability is the main risk. This is not a bug to patch and close; it is a reliability problem. The reconstruction backing the report must carry three properties: it is not a hypothesis, it is based on evidence, it is repeatable and verifiable.

For internal incidents, anticipate the hostile questions before they arrive: "how did you allow this to happen?", "who failed to check?". The defensible answer targets the process, not a scapegoat: the failure was not a single mistake but the absence of structured controls on changes to the data preparation process, and now the gap is known and closable. The analysis establishes when the data changed, where, and who did it; the next steps are management's call.

## Five triage scenarios

The exercise deck presents five "identifications" and asks for the analysis: what likely happened, and where to look for evidence. The verdicts are the interesting part, because the same surface symptom (the model got worse) splits into very different diagnoses depending on the surrounding evidence.

**Scenario 1: retrained image classifier drops from 92% to 71% accuracy.** 3% of one class mislabeled, the images themselves visually correct, all wrong labels traceable to a single batch, no code changes.

- Verdict: **operational error, not an attack**. The share is small and concentrated, the origin identifiable, and there is no malicious pattern: a classic human labeling mistake, with neither intent nor persistence.
- Where to look: the disks. Original dataset files, previous data versions, temporary files, access permissions, creation and modification timestamps.

**Scenario 2: after a weekly automatic retraining, one class's precision falls from 89% to 40%.** New data arriving from a new external API, anomalous statistical distribution, near-identical duplicates, upload performed with a valid API key.

- Verdict: **probable data poisoning**. A significant distribution shift, repeated duplicates capable of inducing bias, a legitimate channel exploited, and an impact targeted on a single class.
- Where to look: git first (recent commits, diffs, authors, timestamps, branches and merges), then the API logs and the dataset itself.

**Scenario 3: anomalous model behavior, and the logs themselves look wrong.** A 4-hour temporal gap, log hashes that do not match, filesystem permissions modified, no anomaly in the dataset.

- Verdict: **system compromise, not a model problem**. The logs were altered while the data shows nothing, which reads as a cover-up attempt: an IT security incident, not an ML one.
- Where to look: ingestion logs, training logs, API logs, errors and warnings, and the temporal gaps themselves.

**Scenario 4: the model degrades slowly over time.** A real change in user behavior, coherent dataset, clean logs, no evident outliers.

- Verdict: **legitimate data drift, no attacker**. The real-world context changed, the data is coherent and tracked, and the decay is gradual rather than sudden.
- Where to look: training tables, change history, audit logs, automatic retraining triggers, and user behavior analyses, suitably anonymized.

**Scenario 5: a new dataset lifts accuracy to 99.8%, then the model collapses on real data.** Near-identical repeated patterns, low variability, undocumented origin.

- Verdict: **probable data poisoning or induced overfitting**. The dataset is artificially clean, generalization is gone, provenance is untracked, and production behavior is incoherent with the eval.
- Where to look: retraining jobs, configurations, model versions, and the rollbacks available.

Scenarios 3 and 4 make the sharpest pair: one turns out not to be an ML incident at all, the other not to be an incident at all. Attribution before accusation.

## Gotchas

- **Rushing the identification phase.** Improvised expertise on unknown systems and improvised tools destroy evidence before the investigation starts. The slides say it three ways for a reason.
- **Trusting the obvious device.** Evidence is not necessarily on the computer where everyone expects it; sometimes it is on a DVD wearing a movie's cover. Map broadly, then acquire.
- **Writing to the source.** One careless read-write mount and the copy can no longer be proven conform to the original. Bit-for-bit copy plus hash, or the evidence dies in court.
- **Shipping technical jargon into the incident report.** "Data poisoning" is precise for engineers and opaque for the decision maker who must act on the report. Two registers, one truth.
- **Calling every degradation an attack.** Gradual decay with a coherent dataset and clean logs is drift, not sabotage. Jumping to the attack verdict burns credibility the next report will need.
- **Framing a poisoned model as a bug.** A bug gets fixed and closed; a model trained on altered data delivers some correct and some wrong decisions with no way to tell which, and that reliability gap is the real damage.
- **Stopping at attribution without a process fix.** In the worked case the root cause is not one bad commit but the absence of structured controls on changes to the data pipeline. Naming the culprit does not close that hole.

## See also

- [01_ai_security_fundamentals.md](01_ai_security_fundamentals.md) - the threat landscape whose incidents this note investigates after the fact
- [02_data_security.md](02_data_security.md) - poisoning enters through the data layer; the controls there are what the forensic reconstruction wishes had existed
- [03_ai_model_security.md](03_ai_model_security.md) - the perturbation and poisoning mechanics behind the worked case
- [05_critical_asset_protection.md](05_critical_asset_protection.md) - the logs, audit trails, and access controls every scenario leans on as evidence sources
- [07_compliance_and_regulations.md](07_compliance_and_regulations.md) - the incident reporting obligations the plain-language report ultimately feeds
