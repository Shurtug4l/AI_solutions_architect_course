# Policies, Standards, and Frameworks

## TL;DR

Governance rules do not appear from nowhere: the industry has spent forty years codifying them into **frameworks**. Two dominate. **DAMA-DMBOK** (2009) is the descriptive reference, "the Bible" of data management, 11 knowledge areas from metadata to architecture, built on a standard terminology, well-defined areas, distinct roles, and cyclic processes (plan, control, improve). **DCAM** (2015) is the measurement-oriented cousin, leaner and more practical, aimed at finance and regulatory compliance: if DAMA says how to do things well, DCAM scores how well you are doing them. On top of a framework sits a triad that is easy to blur and important to keep separate: **policy** (what to do and why), **standard** (how to do it), **procedure** (who does it, with which roles and responsibilities). The triad only bites if named people own the outcomes, so governance defines roles: **Data Owner** (sets the rules), **Data Steward** (turns rules into practice, guards quality), **CDO** (strategic coordinator). The worked example that ties everything together is a **data retention policy**: the answer to "keep everything forever" is always no, and the right retention differs by data type (billing, HR, research, logs) because each carries a different obligation.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **DAMA-DMBOK** | Descriptive body of knowledge, 11 areas | The reference vocabulary everyone cites |
| **DCAM** | Capability model, measures maturity | You get a score, not just guidance |
| **COBIT** | IT governance for the business (ISACA) | IT controls tied to business goals |
| **ISO/IEC 38505** | ISO standard specific to data governance | A certifiable external benchmark |
| **FAIR principles** | Ethical, responsible use of data | Data handled fairly and for a purpose |
| **CDMC** | Cloud-oriented capabilities (EDM Council) | Governance framed for cloud data |
| **Policy** | What to do and why | A titled rule statement with a scope |
| **Standard** | How to do it, which rules to follow | The concrete convention that binds |
| **Procedure** | Who does it, roles and responsibilities | Named owners and steps |
| **Data Owner** | Sets the rules of the game | Approves access, priorities, dataset changes |
| **Data Steward** | Turns rules into practice, guards quality | Fixes anomalies, documents lineage |
| **Data Custodian** | Technical caretaker of storage and access | Runs the systems the data lives in |
| **CDO** | Strategic guarantor, coordinates roles | Owns the data strategy and framework choice |
| **Data retention** | How long to keep, when to delete | A schedule per data type, not "forever" |

## The frameworks: a short history

> Frameworks are necessary to codify rules and behaviours for managing data and models. The need is old, but it turned crucial in the last twenty years.

The lineage is short and worth knowing so the acronyms stop being noise:

```
1980-2000   first enterprise data management models
2000s       digital data explosion, need to codify
2009        DAMA-DMBOK first edition -> global reference
2015        DCAM -> measurement-oriented, finance / compliance
```

**DAMA-DMBOK** (Data Management Body of Knowledge) is the descriptive standard. It carves the field into stone: a standard terminology, well-defined competence areas (11 of them, from metadata to architecture), distinct roles, and cyclic processes summarised as plan, control, improve. It tells you what a healthy data ecosystem looks like.

**DCAM** (Data Management Capability Assessment Model) differs first in purpose. It targets the financial sector and regulatory compliance (GDPR is the obvious anchor), and its strength is being less theoretical and more practical. The one-line contrast is the useful mnemonic:

| | DAMA-DMBOK | DCAM |
|---|---|---|
| **Nature** | Descriptive body of knowledge | Capability / maturity model |
| **Question** | How do we do data well? | How well are we doing it? |
| **Bias** | Broad, theoretical, universal | Finance, compliance, practical |
| **Output** | Vocabulary and reference model | A measurable maturity score |

DAMA and DCAM are the most used, not the only ones. Four more worth citing:

- **COBIT** (ISACA): IT governance oriented to the business.
- **ISO/IEC 38505**: an ISO standard specific to data governance, so certifiable and externally auditable.
- **FAIR principles**: a reference for the ethics and responsible use of data.
- **CDMC** (EDM Council): more oriented to cloud data management.

**Opinion:** these are not competitors to pick between. DAMA gives you the vocabulary and the map, DCAM gives you the ruler, ISO gives you the audit hook. A real programme borrows from several. Treating "which framework" as a religious choice is a way to avoid doing the actual work.

## Policy, standard, procedure: not synonyms

> They look like three words for the same thing. They are not. They coexist, they are consequential, and collapsing them is how governance turns to mush.

The distinction is precise:

| Layer | Answers | Imposes |
|---|---|---|
| **Policy** | What must be done, and why | The intent and the rule |
| **Standard** | How activities are done, which rules to follow | The concrete convention |
| **Procedure** | Who does it | Roles and responsibilities |

Standards and procedures are not substitutes for policies, they are **consequential** to them. You cannot write a sensible standard for a rule that does not exist yet. This is the same triple from note 01 (**what / how / who**), seen from the policy side: there the third slot was called "roles", here it lives inside the **procedure**, which is where roles and responsibilities are actually pinned down.

Writing a policy means asking the right questions. For retention, for instance:

- What kinds of data do we keep and manage?
- How long do we hold them before declaring them obsolete?
- When are they deleted, and who decides?

A policy then has a defined structure:

```
Title         speaking, e.g. "Data retention"
Scope         field of application
Responsible   who applies it
Standards     the how
Procedures    the who and the steps
```

Why bother: policies, standards, and procedures are the bridge between **theory** (what to do), **practice** (how to do it), and **business** (what value we expect), codifying reality in a scalable way that stays legible at the widest possible level.

## The roles: who applies the rules

> Rules are inert until someone applies them. Governance works only when responsibilities are defined at the key points.

The slides name three roles. The responsibilities are what distinguish them:

| Role | Nature | Key responsibilities |
|---|---|---|
| **Data Owner** | Business, accountable | Defines policy and access; sets quality and security priorities; approves dataset changes |
| **Data Steward** | Technical, hands-on | Maintains quality (accuracy, completeness, consistency); controls anomalies; documents metadata and lineage; flags compliance issues |
| **CDO** | Strategic, apical | Sets the data-strategy vision; supervises frameworks; ensures alignment with laws and standards; coordinates owners and stewards |

Read as a chain:

```
CDO           strategic guarantor       (sets the direction)
  |
Data Owner    makes the rules real      (fixes the rules of the game per area)
  |
Data Steward  turns rules into practice (enforces quality on the ground)
```

**Opinion / inference:** the slides fold the *custodian* into the steward ("the custodian of the data, a technical figure"). Industry practice (DAMA) keeps them apart: the **Data Steward** owns the meaning and quality of the data, while the **Data Custodian** is the IT function that runs the storage, backups, and access mechanics. Merging them is fine for a small org, but the moment infrastructure and data-meaning sit in different teams (internal IT plus an external supplier, exactly the exercise below), the distinction stops being pedantic.

## Worked example: a data retention policy

> Knowing how to keep data is a central governance task. The default urge is "keep everything, just in case". That is precisely wrong.

Retention is never "forever". What changes case by case is *why* you limit it. Four scenarios, each with its own driver:

| Scenario | What you keep, for how long | Retention means... |
|---|---|---|
| **eCommerce** | Billing data for the legal obligation period; account data for a reasonable time; abandoned carts within N days | ...not keeping everything forever |
| **HR** | Active employees kept current; ex-employees discarded past the legal obligation; CVs of non-hired candidates not hoarded; informal interview notes are a liability | ...protection (of the company) |
| **Research** | Data updated and managed for the project lifetime; clinical data only for the legally permitted window | ...conscious management |
| **Logs** | Application, system, and security logs kept only as long as necessary | ...limitation and traceability |

The HR and log cases are the sharp ones. An informal note jotted during an interview, or a security log nobody reads, are both **silent data**: personal or legally relevant content that sits unnoticed until it becomes a problem. Logs are not exempt just because they feel technical. Retention here is a legal control, not housekeeping.

## Exercise: assigning roles in an e-commerce company

> Situation: internal IT plus an external supplier, plenty of data managed chaotically. Assign Data Owner, Data Steward, and CDO. There can be more than one of each.

The rule of the exercise: assign roles **per data area**, and motivate each choice. Minimum areas to cover are customer data, orders and billing, and marketing.

| Data area | Data Owner (why) | Data Steward (why) |
|---|---|---|
| **Customers** | Marketing / Customer Care manager: decides usage purposes, answers for consent and correct use | Customer Care referent: guarantees quality and policy adherence, intervenes on errors and misuse |
| **Orders and billing** | Finance manager: data under legal (fiscal, financial) obligation, responsible for accounting correctness and retention | Accounting operative: keeps orders, payments, and invoices consistent |
| **Marketing** | Marketing manager: owns strategy, campaigns, and KPIs | Marketing Operations / Campaign manager: checks segmentation, correct data use, policy adherence |

And the CDO? No specific area, because the role is **transversal**. The CDO defines the frameworks, sets the policies, and coordinates the Data Owners and Stewards across every area. The exercise makes the earlier chain concrete: owners and stewards multiply per area, the CDO stays singular and above them.

## Gotchas

- **Picking a framework as an identity.** DAMA vs DCAM is not a rivalry. DAMA is the map, DCAM is the ruler, ISO/IEC 38505 is the audit anchor; mature programmes compose them instead of choosing a side.
- **Standards before policy.** A standard or procedure written before the policy it serves has nothing to be consequential to. Order matters: policy first, then how, then who.
- **Owner without steward.** Naming a Data Owner and stopping there leaves the rules unenforced. The owner sets the rules, the steward makes them true day to day; you need both.
- **Steward equals custodian conflation.** Fine when one team runs both meaning and infrastructure. Once IT is a separate (or outsourced) function, split them or accountability blurs across the boundary.
- **Retention as "keep everything".** Any retention answer that is not a schedule is a compliance risk. Logs and stray HR notes are the usual blind spots because they read as harmless.

## See also

- [01_what_is_data_governance.md](01_what_is_data_governance.md) - where the what / how / who triple and the seven principles come from
- [03_data_quality_management.md](03_data_quality_management.md) - the quality dimensions (accuracy, completeness, consistency) the Data Steward is accountable for
- [04_data_lifecycle.md](04_data_lifecycle.md) - retention as one stage of the full data lifecycle, from creation to disposal
