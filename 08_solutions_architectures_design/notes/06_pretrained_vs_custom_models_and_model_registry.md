# Pretrained vs custom models and the model registry

## TL;DR

Note 05 walked through the model lifecycle assuming one thing: that the model is built from scratch. This lesson challenges that premise. The **build vs buy** decision has two extremes: **custom models**, trained from zero on proprietary data, with maximum specificity and full architectural control but heavy costs in labelled data, compute, and expertise; and **pretrained models**, built by large vendors on huge generic datasets (ImageNet and friends), consumed via API or downloaded from Hugging Face, ready in minutes but generic, opaque, and often requiring sensitive data to leave the building. The answer for most real cases sits in the middle: **transfer learning**, operationalised as **fine-tuning**. Take a model that already learned the base features, replace its final layer with one shaped for the specific task, and retrain only that part on a fraction of the data. The slides' decision rule: start from the pretrained API to validate the idea, move to fine-tuning when precision demands it (where roughly 90% of enterprises stop), and go custom only for genuinely unique problems. Whatever the route, training ends in an **artifact**: a binary file that has to live somewhere findable, versioned, and trusted. That is the **model registry**: a central, versioned repository that tracks not just the file but its history, enabling **versioning and staging** (safe deployments, fast rollback) and **lineage** (which data and parameters produced the model in production), which is what traceability and compliance hang on.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **Custom model** | Trained from scratch for the specific problem | Unique problem, proprietary data, big budget, deep expertise |
| **Pretrained model** | Trained by others on huge generic datasets | API call or Hugging Face download, running in minutes |
| **Transfer learning** | Reuse general learning for a specific task | Base features already learned; teach only the last mile |
| **Fine-tuning** | The practical application of transfer learning | Swap the final layer, retrain only that on your data |
| **Decision ladder** | API first, fine-tune next, custom last | Escalate only when the cheaper rung fails on precision |
| **Model artifact** | The binary file(s) training produces | 500 MB to 2 GB that must not live on a laptop |
| **Model registry** | Central versioned repository for model lifecycle | Answers "what is in production, how do I roll back" |
| **Versioning and staging** | Tracked versions with stage labels | Safe deployment promotion, instant rollback target |
| **Lineage** | The data and parameters behind each version | Traceability and compliance as a query, not forensics |

## The build vs buy question

Everything in note 05 (training, validation, deployment, monitoring) quietly assumed the model is ours, built from zero. That assumption deserves scrutiny, because training from scratch is the most expensive possible answer to a question that often has cheaper ones. The spectrum has two poles and a middle that the slides call the winning move.

### Custom models

Models trained from scratch for the specific problem. The tailored suit: cut exactly to measure.

- Pro: maximum specificity and optimisation for the use case; full control over the architecture.
- Con: they demand large volumes of labelled data, high training costs, and high-level expertise.

The honest framing from the slides: this is the right choice when the problem is genuinely unique and the data is proprietary, something no existing model has ever seen. Today, training a performant model from zero requires compute and data volumes that few organisations actually possess. It is an uphill road, and most teams that start on it do so for the wrong reason (pride of ownership) rather than the right one (no pretrained model covers the domain).

### Pretrained models

Models already trained by large companies on enormous generic datasets (the canonical example is ImageNet). They are consumed "ready to use" via API, or downloaded from hubs like Hugging Face.

- Pro: ready in five minutes; low or zero cost to start (pay-per-use).
- Con: not optimised for the specific domain; no control over how they were built; often they require sending sensitive data to an external provider.

Recognising a cat in a photo does not justify training a network: an API call or a downloaded model does the job, fast and cheap. But generic means generic. Point the same model at internal legal documents or microscopic defects on a production line and it fails, because it has never seen that world. The third con deserves more weight than a bullet point gives it: routing data through a vendor's API is a data-governance decision wearing a convenience costume. If the input is regulated or commercially sensitive, "ready in five minutes" has a hidden approval cycle attached.

## The middle ground: transfer learning and fine-tuning

> Transfer learning: transfer what a model has learned on a general task to a new, specific task. The pretrained model has already learned the base features; it only needs to be taught to specialise on the new problem.

The intuition from the slides is the strongest mental model in the deck: you do not teach a newborn to see from scratch every time. A model trained on millions of generic images already knows edges, shapes, and colours. What remains is the last mile: recognising the three specific products, or the one defect class, that matter to the business. General culture, reused for a particular problem.

**Fine-tuning** is transfer learning made operational. The process:

1. Load a pretrained model (ResNet50 for images, BERT for text).
2. Replace the final layer with one shaped for the specific task (from 1,000 generic classes down to, say, 2 proprietary ones).
3. Train only that final part, using your own data.

```
  original:    [ pretrained body: ResNet50 / BERT ] -> [ head: 1,000 generic classes ]
                                                              cut here
  fine-tuned:  [ pretrained body: reused as-is    ] -> [ new head: defect / no defect ]
                                                        train only this, on our data
```

The body already knows how to see (or read); only the new head learns. The payoff the slides quote: efficient, fast, and roughly a hundredth of the data a from-scratch build would need. That number is the whole argument. Labelled data is usually the binding constraint in enterprise ML, so an approach that divides the data requirement by 100 does not just cut cost, it flips projects from infeasible to feasible. Module 02 covered the LLM-specific version of this hands-on; note 07 picks up the generative-AI angle where RAG becomes a competing lever.

## Choosing: the decision ladder

The slides give a three-rung decision rule, and the rungs are ordered by cost:

```
  start
    |
    v
  pretrained API good enough? --yes--> ship it
    |            (generic task, non-core business, rapid prototype)
    | no: precision insufficient
    v
  fine-tune a pretrained model
    |            (most enterprise cases: specific task, high precision required)
    | no: data no existing model has ever seen
    v
  custom from scratch
                 (unique problems, scientific R&D, novel data, extreme performance)
```

- **Pretrained API** when the task is generic, not core business, or a rapid prototype. It is the fastest way to validate the idea.
- **Fine-tuning** for most enterprise cases: specific tasks that demand high precision. Per the slides, this is where about 90% of companies stop, and rightly so.
- **Custom** for unique problems, scientific R&D, totally new data, or extreme performance demands. The slides' examples are telling: seismic signals, novel molecular data. Domains where no pretrained model has relevant "general culture" to transfer.

The ladder is also a de-risking sequence. Each rung answers a question the next rung depends on: the API run proves the use case has value before any training budget is spent; the fine-tune proves the domain gap is the real problem before anyone proposes a from-scratch build. Skipping rungs means paying custom-model prices to learn things an API call would have taught you.

## The result is an artifact, and artifacts need a home

Custom or fine-tuned, the end of the process is the same: a binary file, or set of files, weighing anywhere from 500 MB to 2 GB. The slides call this the logistics problem, and it is sneakily important:

- Where is this file stored?
- Where is the information about the data and parameters used to train it?

Leave it on the laptop of whoever trained it and it is effectively lost. Put it on a shared drive and nobody can guarantee it is the right version. And the production pipeline from note 05 needs a deterministic way to find it. The answer has to be a central, secure, queryable place.

## Model registry

> A central, versioned repository designed specifically for managing the lifecycle of ML models. It tracks not just the file, but its history.

The slides' analogy: a GitHub for models, or an intelligent digital warehouse. Not a folder; a system that catalogues, protects, and manages models, and lets data scientists hand off to engineers without USB sticks or email attachments. The questions that have no good answer without one:

- Which of these files is currently in production?
- Who created this model, and when?
- If the production model breaks, where is the previous working version, right now?
- Which data was the production model trained on?

Without a registry, reality is filename chaos: `model_finale_v2_Luigi.pkl`. Funny until an incident, at which point the last question on that list stops being hygiene and becomes the business risk the slides name explicitly: the production model misbehaves and nobody knows how to roll back to yesterday's version quickly. Rollback without a registry is an archaeology exercise conducted during an outage.

```
  training run ---registers---> MODEL REGISTRY
                                +------------------------------------------+
                                | defect_classifier                        |
                                |   v3   stage: Production   lineage: ...  |
                                |   v2   stage: Archived   <---- rollback  |
                                |   v1   stage: Archived        target     |
                                +------------------------------------------+
                                     |                          ^
                                     v                          |
                              deployment pipeline        monitoring alert
                                 (note 05)                  (note 05)
```

The registry earns its place in the architecture through two mechanisms, per the closing slide:

- **Versioning and staging**: every model version is tracked and carries a stage label (the deck's flow ends with the model marked "Production" in the registry). Promotion between stages is what makes deployment safe, and the version history is what makes rollback a label change instead of a scramble.
- **Lineage**: the full trace of which data and parameters produced each version. This is traceability and compliance in one move: "what was the production model trained on" becomes a registry query. Anyone who has faced that question from an auditor knows the difference between answering it in a minute and reconstructing it over a week.

Architecturally, the registry is the handoff point in the note 05 pipeline: training and validation write into it, deployment reads from it, and monitoring points back at it when a rollback is needed. It is the component that decouples the people and systems producing models from the people and systems serving them. The deck closes on exactly that next step: the model is versioned and labelled Production; serving it to the world through an API is the enterprise-integration story, which exercise 02 (the FastAPI image classifier) makes concrete and module 06 notes cover in deployment depth.

## Gotchas

- **Treating build vs buy as binary.** The deck's own conclusion is that the answer is usually neither: fine-tuning is the default enterprise move, and the two pure extremes are the special cases.
- **Generic model, specific domain.** A pretrained model fails on legal documents or machinery defects not noisily but plausibly. Validate on domain data before trusting the five-minute win.
- **The API con that hides in plain sight.** Pay-per-use pricing is visible; sending sensitive data to an external provider is the cost that surfaces later, in a privacy review. Check what leaves the building before the prototype becomes a dependency.
- **Custom as a prestige choice.** Training from scratch because "our problem is special" without checking whether a pretrained backbone covers 90% of it burns data, compute, and expertise that fine-tuning would not need.
- **A shared drive is not a registry.** Folders store files; a registry stores versions, stages, owners, and lineage. If "which model is in production" requires asking a person, there is no registry, whatever the folder is called.
- **Rollback discovered during the incident.** The moment to know where the previous working version lives is before the production model breaks. Registry staging makes rollback a decision; its absence makes it an investigation.

## See also

- [05_ai_model_lifecycle_pipeline.md](05_ai_model_lifecycle_pipeline.md) - the training, validation, deployment, monitoring pipeline the registry plugs into; this note removes that pipeline's from-scratch assumption
- [07_architectures_for_llm_and_generative_ai.md](07_architectures_for_llm_and_generative_ai.md) - the same reuse-vs-specialise decision at LLM scale, where RAG joins fine-tuning as an option
- exercises/02_api_and_enterprise_integration - the FastAPI image classifier: serving a registered model through an API, the deck's declared next step
- Module 02 notes for hands-on LLM fine-tuning; module 06 notes for deployment and MLOps depth, covered compactly here on purpose
