# Practical Use Cases

## TL;DR

This is the closing note of the module, so the job is to make the abstractions land on concrete systems. Four use cases carry the weight: a **document-analysis AI** that failed for lack of governance, an **enterprise virtual assistant** (Copilot on Microsoft 365) read as a governed RAG system, a **governance maturity assessment** on an email-classification model, and an **end-to-end knowledge flow** for an internal chatbot. The recurring lesson across all of them is one sentence: **effective AI equals effective knowledge management**. A model does not know your company. It borrows what your knowledge base and your governance make retrievable, with the right owner, the right freshness, and the right permissions. Governance is not the paperwork around the AI, it is the substrate that decides whether the AI is reliable, auditable, and legal. Everything the module taught (definitions, policies, quality, lifecycle, knowledge representation, RAG, architectures) shows up here as a checklist you run against a real project.

## Cheatsheet

| Use case | System type | Governance angle that decides success |
|---|---|---|
| **Document analysis** | AI over contracts, invoices, internal comms | Classification, lineage, Data Owner, explainability |
| **Enterprise assistant** | Copilot / governed RAG on M365 | Permission-trimmed retrieval, post-generation controls, HITL |
| **Maturity assessment** | Email/ticket classifier in production | Six dimensions scored 1-5, prioritised improvement plan |
| **Knowledge flow** | Internal HR/IT chatbot | Sources to organisation to retrieval to use to update loop |
| **Predictive maintenance** | Expert system over engineer know-how | Formalising tacit knowledge into decision rules |
| **Governed RAG** | Retrieval + LLM + controls | Retrieval respects ACLs, output passes Responsible AI checks |

## Governance for AI projects: what actually changes

> In an AI context data governance becomes more critical, not less. The model does not just report the data, it generalises it, so ungoverned data becomes systematically wrong output at scale.

The slides name three things regulation and stakeholders demand from an AI project: rules, control, transparency. Translated into the module's vocabulary, that is the framework triple (policy, standard, role) plus lineage plus auditability. Five key areas carry the governance load in any AI initiative:

- **Data quality**: accuracy, completeness, consistency of training and input data.
- **Lineage and traceability**: where data came from, how it was transformed, how it is used.
- **Access, security, privacy**: access control including PII, security across pipeline and storage.
- **Lifecycle governance**: from collection to retirement, with updates, monitoring, maintenance.
- **Transparency and explainability**: data and model outputs must be understandable and justifiable.

The non-negotiable operational point from the slides: **governance of the data must not be separate from governance of the AI** (models, outputs, decisions). Split them and you get a well-audited dataset feeding an unaccountable model, which fools an auditor and nobody else.

The slides give a compact example worth keeping. A company builds an **AI customer-support assistant** drawing on documents, call transcripts, and a CRM. To govern it, three concrete controls: a **policy for access and anonymisation** of customer data, **traceability of sources and transformations** used for training, and **monitoring plus a dashboard** for bias or anomalies in the predictions. In regulated sectors (health, finance) two more become mandatory: training and inference data must be **documented and versioned**, and AI decisions must be **explainable and attributable**. Skip these and the initiative risks not just weak results but sanctions, lost trust, or a regulatory block. That last line is the whole argument for governance in one sentence: the downside is no longer a bad metric, it is a stopped project.

**Benefits versus the core tension.** Done right, governance buys more reliable outputs, lower reputational and regulatory risk, better stakeholder trust, and safe reuse of data at scale. The hard part is the standing tension the slides name explicitly: **fast AI innovation against the control and rigour of governance**. Add to that heterogeneous unstructured data (text, images) that resists classic governance, unclear roles across the org, and the cost of continuous lifecycle monitoring. The tension does not resolve, it gets managed, and the maturity model below is how you make that management visible.

## A governance maturity model

The assessment exercise asks for a score from 1 (very immature) to 5 (very mature) across six dimensions, with a two-line justification each and a prioritised improvement plan. That is a maturity model in disguise, so it helps to name the rungs.

```
  1  Ad-hoc        no rules, no owners, tribal knowledge
  2  Aware         some rules exist, applied inconsistently, roles informal
  3  Defined       policies written, owners named, controls partly automated
  4  Managed       automated checks, metrics tracked, audit trail present
  5  Optimising    continuous monitoring, drift + bias alerts, self-correcting
```

The six dimensions to score: **data quality**, **security and privacy**, **roles and responsibilities**, **data lineage**, **ethics and bias**, **post-production monitoring**. The worked example (an internal email/ticket classifier already in production, no formal framework) scores like this:

| Dimension | Score | Reading |
|---|---|---|
| Data quality | 3/5 | Basic rules, no automated checks |
| Security and privacy | 4/5 | Strong auth and audit, weak PII classification |
| Roles and responsibilities | 2/5 | No formal Data Owner or Data Steward |
| Data lineage | 2/5 | Partial pipeline tracing |
| Ethics and bias | 1/5 | No systematic bias analysis |
| Post-production monitoring | 3/5 | Only accuracy tracked, no drift monitoring |

**Opinion**: the two lowest scores (roles and bias) are the tell. A system can look secure and accurate while nobody owns it and nobody checks who it discriminates against. The improvement plan the slides propose is sensible and concrete: introduce a Data Catalog to fix ownership, automate quality checks (dedup, missing fields, language detection), add lineage via OpenLineage or Marquez, add periodic bias and fairness tests, set up input/bias drift alerts, and document the training process (datasets, versions, features).

## The enterprise virtual assistant as a governed RAG system

Copilot on Microsoft 365 is the cleanest example the module has of a governed RAG pipeline, so it is worth reading step by step. Copilot does not know your company. It grounds every answer in knowledge already sitting in documents, email, chat, meetings, and calendar, with **Microsoft Graph as the KM layer** that makes that knowledge retrievable with context and permissions.

```
  1 Prompt      user asks: "summarise the Q3 report, propose actions"
  2 Grounding   Graph retrieves relevant content the user MAY access
  3 LLM         model receives prompt + retrieved context, generates
  4 Controls    quality, security, privacy, Responsible AI post-checks
  5 Output      answer in Word/Outlook/Teams, user decides (HITL)
```

Two governance controls make this safe rather than a data-exfiltration engine. First, **grounding retrieves only what the user is already allowed to see**, so retrieval inherits the existing permission model instead of bypassing it. This is the single most important RAG governance control and the one hand-rolled systems most often skip. Second, **post-generation controls** run quality, privacy, and Responsible AI checks before the answer reaches the user, and the human stays in the loop as the final decision-maker. The lesson the slides close on is blunt and correct: if the knowledge is fresh and organised, Copilot works; if it is stale and messy, the AI produces incoherent answers. The retrieval mechanics are covered in [07_llm_rag_semantic_search.md](07_llm_rag_semantic_search.md), the surrounding system in [08_data_knowledge_architectures.md](08_data_knowledge_architectures.md).

## Knowledge management: turning tacit into usable

Knowledge management is the process of identifying, organising, storing, and sharing information across an organisation. Without it, retrieving information is slow and expensive, and knowledge walks out the door when people do. Three types matter, and they get harder to capture left to right:

- **Explicit**: documents, manuals, reports. Already written down.
- **Implicit**: not yet documented, but documentable.
- **Tacit**: lives in experience, hardest to formalise, most valuable to keep.

Good KM pays back in faster decisions, simpler processes, and better cross-team collaboration, and its sharpest benefit is one the slides call out: it **reduces the loss of tacit knowledge** in organisations with high turnover or complexity. The three phases are creation, storage, and sharing, supported by document management systems, content management, intranets, wikis, and data warehouses. AI changes the leverage: it makes the retrieval and reuse step cheap, which is exactly the bottleneck. The residual challenges are worth stating plainly: formalising expert tacit knowledge into usable models, integrating heterogeneous tech (ontologies, AI, repositories) into real workflows, keeping knowledge current, and holding the balance between automation and human control. The slides give three applied shapes: an **expert system** for predictive maintenance that formalises engineers' cause-effect knowledge into automatic decisions, an **enterprise virtual assistant** backed by a knowledge base, and **smart-city platforms** that formalise infrastructure and sensor knowledge to optimise services. The hard part in all three is the same, formalising tacit expert knowledge into something a system can use, and keeping it current as the domain moves. Techniques for this sit in [06_knowledge_management_techniques.md](06_knowledge_management_techniques.md).

## Case study: governance on a document-analysis AI

A company runs an AI over corporate documents (contracts, invoices, internal communications). The first test surfaces a familiar mess: documents not classified by sensitivity or type, duplicates and multiple versions, a stale training dataset with no quality procedure, no Data Owner, no lineage (the path from source to model output cannot be reconstructed), and outputs auditors cannot follow. The exercise frames it as five questions worth internalising as a template: what are the operational, legal, and bias risks; which roles to introduce; which quality controls; how to build end-to-end lineage; and which tools (data catalog, DLP, dataset versioning, model registry) fit. The answers assemble into a full governance stack, not a single tool:

| Problem | Governance response |
|---|---|
| No ownership | Define **Data Owner**, **Data Steward**, **Model Owner** |
| No classification | **Data Catalog** (Collibra, Atlan, DataHub) with sensitivity/category/status metadata |
| Stale, unversioned data | **DVC / LakeFS** versioning + automated quality gates (OCR > 90%, no dupes, corrupt < 0.1%) |
| No lineage | Centralised transformation logging, reconstructable end-to-end for audit or incident |
| Unexplainable output | **SHAP / LIME**, auto-generated rationale reports, confidence indicators |
| Weak security | **RBAC**, encryption at rest and in transit, sensitive data limited to Steward and Model Owner |

The point of the case is that these are not six independent fixes, they are one governance program. Ownership makes classification enforceable, classification makes lineage meaningful, lineage makes explainability auditable. Skip ownership and the rest degrades to good intentions, the same lesson [01_what_is_data_governance.md](01_what_is_data_governance.md) opens with.

## The end-to-end flow: data to knowledge to value

The final exercise designs a knowledge flow for an internal chatbot (HR, IT, procedures) that must use only company knowledge, give reliable answers, and respect roles and permissions. The five-stage loop is the spine that ties governance and KM together:

```
  Sources  ->  Organisation  ->  Retrieval  ->  Use  ->  Update
  policies     domain tags       content +      chatbot    periodic
  FAQ          versioning        context        answers,   review,
  manuals      metadata          role-based     no source  owner
                                 access         mutation   assigned
```

Read each stage as a governance obligation, not a technical step. **Sources** need an owner and a legitimate purpose. **Organisation** is where metadata and versioning earn their keep. **Retrieval** must be role-based, the same permission-trimming Copilot does. **Use** must not mutate the source of truth. **Update** needs a named Knowledge Owner and a review cadence, because stale knowledge is where governed AI quietly starts inventing. This flow is the operational form of the data-to-knowledge pyramid from [05_from_data_to_knowledge.md](05_from_data_to_knowledge.md).

## Tying the module together

One paragraph to close the loop across the whole module. Governance gives you the **rules, roles, and quality** ([01](01_what_is_data_governance.md), [02](02_policies_standards_frameworks.md), [03_data_quality_management.md](03_data_quality_management.md)) and the **lifecycle discipline** ([04_data_lifecycle.md](04_data_lifecycle.md)) that decide whether data is trustworthy. Knowledge management turns that trustworthy data into something a system can act on ([05](05_from_data_to_knowledge.md), [06_knowledge_management_techniques.md](06_knowledge_management_techniques.md)). RAG and semantic search are the retrieval machinery ([07](07_llm_rag_semantic_search.md)), and the architecture ([08](08_data_knowledge_architectures.md)) is how the pieces run together in production. The use cases here are the exam: take any AI project, run it against the six maturity dimensions, and the gaps tell you exactly which of the earlier notes you skipped. A one-pass checklist to carry out of the module:

- Is there a named **Data Owner** and **Model Owner** for this system? If not, stop here.
- Can you **reconstruct lineage** from source to output for an audit or an incident?
- Does **retrieval respect permissions** before generation, not after?
- Are **quality and drift** checked automatically, or only accuracy at go-live?
- Is there a **bias and fairness** process, and a **freshness cadence** with an owner?

## Gotchas

- **Governance of data separated from governance of the AI.** A pristine dataset feeding an unaccountable model passes a shallow audit and fails a real one. Govern the model outputs and decisions too.
- **RAG retrieval that ignores permissions.** Grounding that fetches everything, not just what the user may see, turns an assistant into a data-exfiltration path. Permission-trim at retrieval, not after generation.
- **Scoring maturity without an improvement plan.** A 2/5 on lineage is a finding, not a deliverable. The plan (three prioritised actions minimum) is the point of the assessment.
- **Treating stale knowledge as harmless.** An out-of-date knowledge base does not fail loudly, it produces confident wrong answers. The Update stage needs an owner and a cadence, not good intentions.
- **Formalising tacit knowledge once and calling it done.** Expert know-how drifts as the domain moves. Capture is a loop, not a project.

## See also

- [01_what_is_data_governance.md](01_what_is_data_governance.md) - the definition, principles, and the accountability-first stance the case study leans on
- [02_policies_standards_frameworks.md](02_policies_standards_frameworks.md) - the policy/standard/role triple that operationalises every use case here
- [03_data_quality_management.md](03_data_quality_management.md) - the automated quality checks the maturity plan calls for
- [04_data_lifecycle.md](04_data_lifecycle.md) - the collection-to-retirement discipline behind lineage and freshness
- [05_from_data_to_knowledge.md](05_from_data_to_knowledge.md) - the data-to-knowledge pyramid the end-to-end flow instantiates
- [06_knowledge_management_techniques.md](06_knowledge_management_techniques.md) - formalising tacit knowledge and keeping it current
- [07_llm_rag_semantic_search.md](07_llm_rag_semantic_search.md) - the retrieval mechanics behind the governed assistant
- [08_data_knowledge_architectures.md](08_data_knowledge_architectures.md) - how retrieval, controls, and knowledge base run together in production
- Module 04 (Business Case and AI PM) - framing the governance program as a business case with owners and budget
- Module 06 (AI Service Deployment) - the deploy-and-monitor entry point where drift and staleness are caught in production
