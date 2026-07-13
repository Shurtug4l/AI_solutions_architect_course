# What is Data Governance

## TL;DR

**Data governance** is the set of rules, processes, and roles that keep data accurate, secure, accessible, and compliant across its whole life. It is not a gate bolted onto a pipeline, it permeates every stage: it acts before, during, and after the process. The framing that makes it operational is three questions: **policy** (what to do), **standard** (how to do it), **roles** (who does it). For AI specifically there are four entry points where governance has to show up: **data collection**, **preparation and cleaning**, **training and validation**, **deployment and monitoring**. The reason it matters more for AI than for a classic report is amplification: a model does not just report bad data, it generalises it, so ungoverned data becomes systematically wrong output. Two things are worth internalising up front because everything else follows from them: **data is not neutral**, and **quality is not automatic**. Governance is the discipline that turns those two facts into procedures instead of hope.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **Data** | Raw element, no context | A value with no story attached |
| **Information** | Data placed in a context | You can extract something from it |
| **Knowledge** | Information confirmed by experience, decision-usable | It changes what someone does |
| **Metadata** | Data about data | Owner, source, schema, lineage |
| **Data governance** | Rules + processes + roles over data | Accurate, secure, accessible, compliant |
| **Policy** | What to do | The rule statement |
| **Standard** | How to do it | The concrete convention |
| **Role** | Who does it | A named accountable person |
| **Bias** | Systematic error that distorts output | The model is confidently wrong in one direction |
| **High-risk system** | AI whose failure harms people or rights | EU AI Act obligations attach |

## From data to knowledge: the DIK pyramid

> Clear governance needs clear rules, and clear rules need clear definitions. Less ambiguity, more collaboration. This is not pedantry: it is the precondition for anyone to be accountable for anything.

```
        KNOWLEDGE     verified by experience, has value, drives decisions
       ------------
      INFORMATION     data with a context, something can be extracted
     --------------
         DATA         raw, no context, many forms and places
```

- **Data** is the raw element. It has no context and shows up in different forms, structures, and locations. Turning it into value takes deliberate work (data engineering).
- **Information** is data that has been given a habitat, a context to live in. It is refined enough that you can read something off it.
- **Knowledge** is information that experience has confirmed. It has a reference context, a measurable value, and can feed a decision.

The pyramid has a twist: even raw data needs references to be usable, and that is where **metadata** comes in, a datum that carries information about the datum itself (owner, source, format, time, lineage). The operational point is that information carries information depending on the reference context. A column of numbers is data; the same column with a schema, an owner, and a definition is on its way to being knowledge.

## The definition

> The set of rules, processes, and roles that guarantee data is accurate, secure, accessible, and compliant.

Read that as four commitments, not four adjectives. **Accurate** is a quality commitment, **secure** is a protection and compliance commitment, **accessible** is a findability commitment (this is where metadata earns its keep), **compliant** is a legal commitment (GDPR in Europe is the obvious anchor). Governance is what makes those commitments hold under pressure, when the team is busy and the deadline is close, which is exactly when data discipline usually collapses.

## The seven principles

The course frames governance around seven principles. They are not independent, they reinforce each other, and the last one is the bridge to knowledge management.

| Principle | What it demands |
|---|---|
| **Accountability** | Every datum has an identifiable owner who is responsible for it. This is where roles are born. |
| **Quality** | Data must be accurate, complete, up to date, and consistent. AI distorts and amplifies errors from dirty data, so this is not optional. |
| **Security and compliance** | Balance access against protection, and adhere to regulation (GDPR, and for AI the EU AI Act). |
| **Accessibility** | A datum you cannot find is a datum you do not have. Findability rests on metadata. |
| **Value and purpose** | Data must have a purpose and a context, otherwise it is cost without value. |
| **Transparency and traceability** | A datum needs a documented history: its whole lifecycle, owners, and changes must be reconstructable. |
| **Collaboration** | Roles must be defined and must cooperate. Knowledge is created by managing data collaboratively along its whole chain. |

**Opinion:** accountability is the load-bearing one. Quality, traceability, and compliance all degrade to good intentions the moment no single person owns the outcome. Naming an owner is the cheapest governance intervention with the highest leverage.

## Where governance enters the AI lifecycle

> Governance is not a step in the process, it permeates every part of it, at every point of the data lifecycle, from extraction to its transformation into knowledge. So it acts before, during, and after the process.

Ambiguity is the enemy here. Rules that have to be interpreted introduce uncertainty, and uncertainty in an AI pipeline propagates silently. Governance reduces interpretation by being explicit. It has four concrete entry points in an AI workflow:

```
  Collection  ->  Preparation/Cleaning  ->  Training/Validation  ->  Deploy/Monitoring
      |                  |                          |                        |
  traceable,        standards,                 bias checks,            drift, staleness,
  owner, quality    metadata, lineage          ethics, correctness     re-validation
```

1. **Collection.** Verify the datum is traceable and transparent, identify its owner, assess its quality. This is where the datum's story begins.
2. **Preparation and cleaning.** Clean and prepare data to generate knowledge. Define standards, classify metadata, and through metadata track the history and responsibility of the data.
3. **Training and validation.** The technical point. Data is clean and ready to train. Watch for bias, keep the data correct and ethical, and it is the owner's job to guarantee it.
4. **Deployment and monitoring.** The system is validated, trained, and live. Data can become wrong or obsolete over time, so results need maintenance too. Governance does not stop at go-live.

The framing that operationalises all four is the framework triple: **policy = what to do**, **standard = how to do it**, **roles = who does it**. That triple is developed in [02_policies_standards_frameworks.md](02_policies_standards_frameworks.md).

## Feeding the models

> Applying these principles is like prescribing a healthy diet for the models. Governance decides what goes in.

Two reminders sit under this whole section: data is not neutral, and quality is not automatic. Governance is what separates useful AI from dangerous AI. Selecting data has several faces:

- **Sources.** A good model rests on good data. Sources vary widely: internal (logs), external (open data, web scraping), or produced by other processes. Without governance the risk is feeding the model anything at all.
- **Pipelines.** If the datum matters, so does the process that refines it. Doing governance means ensuring those steps are logically consequential and well built, from collection to training, while avoiding bias.
- **Quality policies.** Quality is a principle, but it needs policies to be guaranteed. Governance defines, upfront and before the process, the policies and activities needed to ensure the data is sound and coherent in its operating context.

Every choice has consequences, and if the premises are wrong the output is wrong with confidence. That is the bridge to bias.

## Bias: the four types

> Ex falso sequitur quodlibet, from the false follows anything. A biased premise does not fail loudly, it produces plausible wrong answers.

Bias is a systematic error that distorts the output of a process or model. Causes range from the data, to poor metric choices, to the chosen process, and sometimes to our own expectations. Four common types, with how governance intervenes:

| Type | What goes wrong | Governance response |
|---|---|---|
| **Selection** | Data represents a subset, not the world (medical data on men only; income data from one wealthy district) | Inspect the dataset for balance and traceability |
| **Labeling (classification)** | Wrong labels, human slips or errors inherited from earlier processes (sarcastic film reviews tagged positive) | Check documentation, run double or cross checks |
| **Representation** | Data is balanced but the model answers from entrenched stereotypes ("doctor" imagined as a man) | Audit the dataset with defined procedures |
| **Measurement** | The error is in the sensor or the measurement parameter, or the metric ignores context | Validate measurement systems, define metrics unambiguously and, ideally, in a standardised way |

## Ethics and accountability

When a model produces a wrong result, governance has to trace back what led to the error, and that is also an ethical question. The course splits ethics into two non-exclusive halves that in practice reinforce each other:

- **Data ethics.** Does the data come from reliable sources? Was it collected legally and correctly? Are we using it for a legitimate purpose?
- **Model ethics.** Is the model fair? How high is the bias risk? Are its results interpretable? Who supervises it?

Because neither data nor models are neutral, there are rules that impose transparency, traceability, and supervision. **High-risk AI systems** (for example those handling sensitive data) always carry the obligation of particularly solid governance. In the EU this is codified in the **AI Act**. This is the point where the course's material meets real regulatory obligation: governance stops being good practice and becomes a compliance requirement with teeth.

## When governance is absent: failure patterns

Without governance the data world is a mess, and with AI in the loop it goes particularly badly, because the model amplifies whatever is wrong. Four patterns, all set in the same e-commerce "high-value customer" scenario:

1. **Bad data, nobody checks.** Duplicated, undocumented, unowned data. The model targets the wrong customers, the whole decision chain concentrates on them, and the error is untraceable because nobody can say where it started. It propagates across departments.
2. **Dangerous data.** Unsafe, out-of-context, or legally forbidden data feeds the model. Best case, wrong results; worst case, legal exposure. Governance blocks the use of unsafe or illegitimate data.
3. **Stale data, AI that "invents".** With no ordering or updating of documentation, the model predicts on old data and its output is treated as absolute truth without verification. Governance sets rules for traceability, consistency, and updating.
4. **Biased processes.** Choosing which products to back on trends from fifteen years ago. Demand changes, the data does not, and customer interaction fails. Governance reduces this risk.

The common thread: governance is a guarantee, not a guardian. It exists so that enormous volumes of information stay ordered enough that AI produces answers that are correct, complete, unbiased, legal, and traceable.

## Gotchas

- **Governance treated as a final gate.** The whole point is that it acts before, during, and after. A review only at deploy time catches nothing that collection and preparation let through.
- **Naming principles without naming owners.** The seven principles are inert until accountability assigns a person. Unowned quality is aspirational.
- **Confusing "balanced dataset" with "unbiased model".** Representation bias survives a balanced dataset. Balance is necessary, not sufficient.
- **Compliance as paperwork.** GDPR and the EU AI Act are constraints on the pipeline, not a document produced after the fact. For high-risk systems the governance has to be real and auditable.

## See also

- [02_policies_standards_frameworks.md](02_policies_standards_frameworks.md) - the policy/standard/role framework and the industry frameworks (DAMA-DMBOK, DCAM)
- [03_data_quality_management.md](03_data_quality_management.md) - the quality principle made measurable (dimensions, profiling, metrics)
- [05_from_data_to_knowledge.md](05_from_data_to_knowledge.md) - the DIK pyramid taken further into knowledge representation
- Module 06 [09_production_deployment_monitoring_orchestration.md](../../06_AI_services_deployment/notes/09_production_deployment_monitoring_orchestration.md) - drift and monitoring, the "deploy and monitoring" entry point in practice
