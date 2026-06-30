# Ethics, Bias, and Governance

> Note: the course's slide deck for this module is a template placeholder; this note is a synthesis from the broader literature, the EU AI Act text, GDPR articles, and the ethics-relevant points that surface in the other course modules (training data composition, RLHF biases, RAG faithfulness, deployment security). It is the angle a Solutions Architect needs - the regulatory and operational view, not the philosophical one.

## TL;DR

LLM systems pull in three sets of ethical concerns at once: the **model itself** (what biases it has learned, what it hallucinates, what its training data licensed and exposed), the **data pipeline around it** (what user information you collect, where it lives, who can access it, how long you keep it), and the **operational deployment** (who is accountable when it makes a wrong decision that affects a person). The dominant regulatory frameworks are **GDPR** (EU data protection, in force since 2018) and the **EU AI Act** (in force in stages from 2024-2027); together they shape what is legally allowed and what proof of compliance is required. The technical concerns - **bias**, **hallucination**, **privacy leakage**, **explainability**, **environmental cost** - are not separate from the regulatory ones; the regulations exist precisely to make organisations address them. A practical compliance posture has four pillars: **transparency** (document the training data, the model, the use case), **accountability** (a human decision-maker can be identified for every consequential output), **auditability** (logs and audit trails are kept long enough), and **technical safeguards** (PII redaction, bias evaluation, content filters, secret hygiene). None of this is optional in production; the right time to design for it is at the start of the project, not in response to a breach or a fine.

## Cheatsheet

| Concern | One-line | Where it surfaces |
|---|---|---|
| **Bias** | Models inherit the biases of their training data and annotators | Quality varies across demographics, languages, contexts |
| **Hallucination** | Confident-sounding fabricated facts | The single most discussed model failure |
| **Privacy** | Training data and user prompts may contain PII | GDPR-relevant in every EU jurisdiction |
| **Copyright / IP** | Training data ownership, output ownership | Open question, active litigation |
| **Transparency** | Documentation of model, data, and use case | AI Act requirement for high-risk systems |
| **Explainability** | Why did the model produce this output? | Required for consequential decisions |
| **Accountability** | Identifiable human responsible for AI-mediated decisions | The compliance constant |
| **Environmental cost** | Training and inference compute = energy = CO₂ | Disclosable for some uses; not yet mandated for most |
| **Misuse / dual-use** | A tool that helps a user can help a bad actor | The hardest design problem |
| **GDPR** | EU data protection regulation | Personal data, retention, right to be forgotten |
| **EU AI Act** | EU-wide AI regulation by risk tier | Compliance phased in 2024-2027 |
| **Audit trails** | Immutable logs of every model decision | Compliance + post-mortem |

---

## Bias

LLMs reflect the statistical properties of their training data. If the training corpus is 70% English, dominated by male authors, written between 2000 and 2023, with US-centric examples, the resulting model encodes those properties in subtle and not-subtle ways.

### Where bias enters the pipeline

| Stage | How bias appears |
|---|---|
| **Training data** | Demographic, linguistic, geographic, temporal skew |
| **Tokenisation** | Sub-word tokenisers represent some languages much more efficiently than others; tokens-per-word ratio doubles or triples on non-Latin scripts |
| **Pre-training objective** | Next-token prediction propagates whatever associations dominate the corpus (gendered occupations, racial stereotypes, regional defaults) |
| **Fine-tuning data** | If annotators are a homogeneous group, their stylistic preferences become "the right answer" for everyone |
| **RLHF preferences** | Reward model reflects the rankings of the human raters, with their cultural biases |
| **Evaluation set** | Test data shapes what gets optimised for |

The bias is rarely a single decision point; it accumulates across stages.

### Observable failure modes

- **Demographic disparities**: a model that summarises résumés may favour names associated with one gender or ethnicity.
- **Language quality gaps**: a multilingual model that is fluent in English is often noticeably worse in Italian, Swahili, or Bengali.
- **Cultural defaults**: "the typical family" defaults to a US suburban household; "a doctor" defaults to male; "a nurse" defaults to female.
- **Temporal bias**: knowledge cutoff and corpus weighting make the model see the world as it was in its training window, not as it is now.
- **Class disparities**: poorer-resourced domains (regional dialects, specialist domains, low-volume languages) get worse representation.

### Mitigations

| Mitigation | Mechanism |
|---|---|
| **Diverse training data** | Curated representation across demographics, languages, sources |
| **Fairness-aware fine-tuning** | Counter-examples explicitly added during instruction tuning |
| **Output filters** | Post-process to detect biased outputs (toxicity scoring, fairness checks) |
| **Bias evaluation** | Periodic measurement on a fairness benchmark (BBQ, StereoSet, HolisticBias) |
| **User feedback loops** | Channel for users to report bias; ingested back into training |
| **Audit across cohorts** | Run the system on equivalent inputs from different demographic groups; compare quality |

None of these eliminate bias. The honest claim is "we measured and reduced it"; not "we removed it".

---

## Hallucination

LLMs generate text that is statistically plausible. They do not have a fact-checker built in. When the right answer is in the training data and the prompt is unambiguous, the answer is usually correct. When the right answer is rare, contradicted by the training data, or simply absent, the model generates something that **sounds correct** but is wrong.

### Types

| Type | Example |
|---|---|
| **Factual fabrication** | Inventing a citation, a date, a name |
| **Conflation** | Mixing details from two real entities |
| **Misattribution** | Crediting a quote to the wrong person |
| **Confabulation under pressure** | The user asks something the model does not know; the model produces a plausible answer rather than admitting uncertainty |
| **Confident wrongness** | The model is wrong and its confidence does not signal it |

### Mitigations

The two most effective: **RAG** (ground the answer in real documents) and **citations** (force the model to point at the source of each claim).

Other mitigations that help less but matter:

- **Temperature 0** for factual tasks (reduces creative paraphrasing).
- **Explicit "say you do not know"** clauses in the system prompt.
- **Faithfulness measurement** (see [06_rag_evaluation.md](06_rag_evaluation.md)).
- **Tool calling for facts that can be checked** (a calculator for arithmetic, a database for company data).
- **Reflexion-style self-critique** (see [Module 03 / 03_paradigms_react_planexecute_reflexion.md](../../03_agentic_ai/notes/03_paradigms_react_planexecute_reflexion.md)).

No mitigation gives zero hallucination. Production systems must assume some non-zero rate and design the human-in-the-loop around it.

---

## Privacy: PII, training data, user prompts

Three distinct privacy concerns; production needs to handle all three.

### Training data privacy

What was the model trained on? Did it ingest personal data without consent? This is the question that powers the active **EU AI Act** discourse and several pending lawsuits in the US and UK.

Practical implications:

- A closed model trained on scraped web data may have ingested names, addresses, and identifying details. Extracting them via clever prompting is **possible** and has been demonstrated in research.
- For the application developer, the practical defence is: do not rely on the model to keep its training data private. Assume that information visible in the model's outputs could leak.

### User prompt privacy

What happens to the data the user types into the system? Three patterns:

| Pattern | Privacy posture |
|---|---|
| **Cloud LLM API** | Provider sees the prompt. May log, may use for training (depending on contract). |
| **Self-hosted open-weights** | No external party sees the prompt. |
| **Cloud LLM with no-training contract** | Provider commits not to train on the data; logs may still exist. |

For regulated environments (healthcare, finance, defence) the only safe pattern is **self-hosted**. The data never leaves the controlled perimeter.

### Output privacy

The model's output can leak information it has memorised from training (rare but possible) or from injected context (more likely). Mitigations:

- **PII redaction** before injecting context into the prompt.
- **Output scanning** for emails, phone numbers, account identifiers.
- **Refusal patterns** for queries that ask the model to disclose information about specific people.

---

## GDPR for AI systems

The **General Data Protection Regulation** governs personal-data processing for EU citizens, regardless of where the processor is located. Key obligations for AI systems:

| Article | Obligation |
|---|---|
| **Art 5** | Personal data must be processed lawfully, fairly, transparently |
| **Art 6** | Legal basis for processing (consent, legitimate interest, contract, etc.) |
| **Art 13-14** | Inform the user about how their data is used |
| **Art 15** | Right to access their data |
| **Art 17** | Right to erasure ("right to be forgotten") |
| **Art 22** | Right not to be subject to a decision based solely on automated processing |
| **Art 25** | Data protection by design and by default |
| **Art 35** | DPIA (Data Protection Impact Assessment) for high-risk processing |

### Operational consequences for an LLM system

- **Document the lawful basis** for processing user data through the LLM.
- **Inform the user** when they are talking to an AI; document the model used.
- **Implement deletion** at the user level. This is hard for LLM systems because the model itself has effectively "trained" on the data (RLHF, fine-tuning); the practical answer is to delete the user's data from the operational pipeline (prompts, logs, vector store) even if it cannot be excised from the model weights.
- **DPIA** for high-stakes systems (HR screening, credit decisions, healthcare).
- **Audit trails**: keep enough records to demonstrate compliance.

### The deletion problem

GDPR's Art 17 right to erasure is technically incompatible with a model that has been fine-tuned on user data. The two practical positions:

- **Treat the model weights as anonymous**: argue that the user's data has been "anonymised" by the training process and is no longer identifiable. Legally untested.
- **Avoid training on user data in the first place**: use RAG where the user's data lives in the retrievable corpus (deletable on demand), not in the model weights. This is the safer architectural choice.

The second is the dominant pattern in regulated production. Fine-tune the base model on generic data; put user-specific knowledge in the RAG store.

---

## The EU AI Act

The **EU AI Act** is the first comprehensive AI regulation. Passed in 2024, phased compliance through 2027. It classifies AI systems by risk tier and imposes obligations accordingly.

### Risk tiers

| Tier | Examples | Treatment |
|---|---|---|
| **Unacceptable** | Social scoring, manipulation of vulnerable groups, real-time biometric surveillance in public spaces | **Banned** |
| **High-risk** | Hiring, credit, education access, critical infrastructure, medical devices, justice administration | Strict compliance: documentation, audit, human oversight, accuracy / robustness testing |
| **Limited risk** | Chatbots, deepfakes | Transparency: users must know they are interacting with AI |
| **Minimal risk** | Spam filter, video game AI | No specific obligation |

### Obligations for high-risk systems

| Obligation | What it requires |
|---|---|
| **Conformity assessment** | Document the system, its training data, its accuracy, its limits |
| **Risk management system** | Iterative risk analysis throughout the lifecycle |
| **Data governance** | Quality, relevance, bias-checking of training data |
| **Technical documentation** | Detailed enough that an auditor can verify compliance |
| **Logging** | Sufficient to enable post-hoc audit |
| **Transparency to users** | The user knows it is AI; knows what data it uses; knows its limitations |
| **Human oversight** | A person can supervise, override, and stop the system |
| **Robustness, accuracy, cybersecurity** | Tested and reported |

A general-purpose LLM (GPT-4, Claude, Gemini) becomes high-risk when **integrated into a high-risk use case**. The application developer is responsible for the compliance of their use case.

### Foundation Model obligations

The Act has specific provisions for foundation models (the LLMs themselves):

- Training data **summary** disclosure.
- Copyright compliance for training data.
- Energy consumption reporting.
- Cybersecurity assessment.

Higher requirements for the most capable models (FLOPs threshold) including systemic risk assessment.

### What this means for a Solutions Architect

- **Determine your risk tier early.** Most enterprise applications fall into "limited risk" (chatbots, assistants) or "high-risk" (HR / credit / health).
- **Document the model and the data flows from day one.** Retrofitting documentation after launch is more expensive than building it in.
- **Plan for the audit before it is requested.** Logging, monitoring, evaluation metrics, bias measurements - the auditor expects them to exist.
- **Identify the human oversight role.** Who can override the model? How is the override logged? What happens if the human is wrong?

---

## Copyright and IP

The two open questions:

### Training data ownership

If the model was trained on copyrighted text, does the model's output count as derivative work? Active litigation in multiple jurisdictions; no settled answer.

Practical defensive position:

- For commercial deployment, **prefer open-weights models with permissive licences** (Llama, Mistral, Qwen). The licence terms govern your right to use the outputs commercially.
- Read the licence. Llama's licence has a user-count threshold; Gemma's is permissive; Mistral's varies by model.
- Closed-model providers (OpenAI, Anthropic, Google) include indemnification clauses in their enterprise contracts. Read them.

### Output ownership

Who owns the text the model generates? Most jurisdictions hold that AI-generated content is **not** copyrightable as such (a human needs to be the author). Implications:

- The user can use the output but may not have a copyright on it.
- Re-using output in your own products is generally legal but you cannot prevent others from doing the same.
- For tasks where attribution matters (writing, art, code), the human's involvement (selection, editing, judgment) is what creates the copyrightable contribution.

---

## Transparency and explainability

Two related but distinct concepts.

### Transparency

**Documentation of the system**: what model, trained on what data, used for what purpose, with what known limitations. Required by the AI Act for high-risk systems.

Practical artefacts:

- **Model card**: summary of the model's properties, performance, limitations, intended use cases. Hugging Face hosts model cards as a convention.
- **Data card**: summary of the training data (provenance, demographics, time span, biases observed).
- **System card**: documentation of the deployment (your specific application).

### Explainability

**The ability to articulate why a specific output was produced**. This is fundamentally harder for LLMs than for classical ML.

- For a logistic regression, you can list the feature weights.
- For a tree, you can trace the decision path.
- For an LLM, the closest thing is **attention visualisation** or **chain-of-thought reasoning** - both of which are approximations, not the actual computation.

For consequential decisions (loan approval, hiring), the AI Act requires explainability. The practical pattern: **structure the system so the LLM's role is a sub-step**, with the consequential decision still made by deterministic logic that *can* be explained. The LLM extracts features, suggests labels, summarises documents; a rule engine or a simpler model makes the decision.

---

## Environmental cost

Training a frontier model uses on the order of tens to hundreds of millions of dollars of compute, which corresponds to tens of thousands of MWh of electricity. The carbon footprint depends on the grid mix where the data centre runs.

Inference is comparatively cheap per query, but at scale (billions of queries per day across the world) it adds up. Each query is a few cents of compute and a measurable amount of CO₂.

### Where this matters

- **Sustainability reporting**: increasingly required for large organisations, with AI use disclosed as part of Scope 2/3 emissions.
- **Vendor selection**: providers running on renewable-powered data centres (some European Azure / GCP regions) have lower per-query emissions.
- **Model selection**: a 7B model running locally costs a fraction of GPT-4 in energy; for tasks that the smaller model handles, the larger one is overkill in every sense.

The honest disclosure: this is a topic with active research; numbers vary widely; precise accounting is hard. Treat it as a real but not yet quantifiable concern in most deployments.

---

## Misuse and dual-use

The most uncomfortable design problem: a tool useful for a legitimate user is also useful for a malicious one. A summariser that helps a lawyer also helps a phishing campaign. A code-writing assistant that helps a developer also helps a malware author.

### Categories

| Category | Example |
|---|---|
| **Disinformation** | Generating misleading news, deepfake-style impersonation |
| **Fraud** | Impersonation, social engineering, scam content |
| **Cybercrime assistance** | Malware generation, phishing kits, vulnerability exploitation |
| **Harassment** | Targeted abuse content |
| **Privacy violation** | Doxxing, OSINT compilation |

### Defences

Model providers ship **safety training** that refuses obviously malicious requests. The defences are imperfect:

- **Jailbreaking** continually finds new ways around the safety training.
- **Open-weights models** can be fine-tuned to remove the safety filters (already done by communities focused on "uncensored" variants).
- **Legitimate dual-use requests** (security research, education, fiction) are often refused alongside genuinely malicious ones.

The application developer's role:

- **Layer your own filters** on top of the model's safety. Do not rely on the provider's filters alone.
- **Rate-limit and audit**. Even if a query gets through, the volume should be visible in logs.
- **Refuse known-harmful patterns**: weapons synthesis, child-safety violations, targeted harassment.
- **Document your refusal policies** so users (and auditors) know what the system will and will not do.

---

## Accountability

The constant under every regulation: **who is responsible when the AI is wrong?**

The answer is never "the AI". It is always one or more of:

- The **deployer** (the organisation that operates the system).
- The **provider** (the organisation that built the model).
- The **user** (in some bounded cases, when they misused the system).

### Practical implications

- **Identify the human decision-maker** for every consequential output. A loan rejection cannot be a black-box AI decision; a person signs off (and is responsible).
- **Document the chain of accountability**. When the output is used, who approved it? When an exception is made, who authorised it?
- **Insurance**: increasingly important for AI deployments. Cyber liability, professional indemnity, errors and omissions cover may need to be extended to cover AI-mediated decisions.

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| "Bias" treated as a marketing concern | Quality gaps across user cohorts | Measure on cohort-specific benchmarks; report disparities |
| Hallucination assumed to be a model fault to fix | Hallucination keeps appearing despite "better" models | Design for it: human review, citations, RAG |
| GDPR considered "for the legal team to handle" | Deletion requests cannot be fulfilled | Architect deletion in from day one |
| AI Act compliance left until launch | Documentation, audit trails, evaluations not in place | Build them in early; far cheaper than retrofitting |
| Open-weights model on commercial product, licence not read | Compliance / licensing claim | Read every licence; some have user-count or use-case restrictions |
| All output assumed copyright-free | Re-using a competitor's similar outputs without attribution | Add human review and editing to claim copyright protection |
| Safety filters assumed sufficient | Jailbreak in the wild becomes a PR incident | Multiple layers of filtering; monitoring; rate limiting |
| No identified human decision-maker | When the system makes a wrong call, no one to escalate to | Pin a person; document the escalation path |
| Energy use not disclosed | Sustainability audit fails | Track usage; ask vendors for their grid mix |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Deploying a customer-facing chatbot in the EU | Transparency disclosure + AI Act limited-risk obligations | Required by the AI Act |
| Deploying in a high-risk domain (HR, credit, health) | Full AI Act high-risk programme | Required; non-compliance is a fine |
| Handling EU personal data | GDPR architecture from day one | Required; deletion + audit trail are not optional |
| Sensitive data (PII, medical, financial) | Self-hosted open-weights | Cloud APIs expose the data to a third party |
| Building public-facing AI feature | Layer your own safety filters | Provider filters are not enough alone |
| Open-weights model | Read the licence | Especially Llama, Gemma; varying terms |
| Consequential automated decisions | Human-in-the-loop for the final decision | Explainability + accountability + AI Act |
| Documenting for the audit | Model card + data card + system card | The artefacts auditors expect |
| Bias audit | Cohort-specific benchmarks | Aggregate metrics hide cohort gaps |

---

## See also

### Other notes
- [01_llm_foundations.md](01_llm_foundations.md) — where the biases are baked in during pretraining
- [02_model_landscape.md](02_model_landscape.md) — closed vs open-weights affects data residency and licensing
- [04_rag_fundamentals.md](04_rag_fundamentals.md) — RAG as the architectural answer to GDPR deletion (user data in retrieval, not in weights)
- [06_rag_evaluation.md](06_rag_evaluation.md) — faithfulness measurement is the hallucination defence; bias measurement is the same shape
- [07_rag_production.md](07_rag_production.md) — security, audit, compliance as operational concerns
- Module 03 [07_deployment.md](../../03_agentic_ai/notes/07_deployment.md) — secret hygiene, access control, the deployment side

### Related work in this repo
- Module 02 capstone (`PRJ_rag_system_for_company_knowledge.py`) — uses a multilingual embedder for an Italian corpus; the licensing posture of the embedder is the kind of audit item this note demands
- Module 03 exercise 06 — episodic memory dict is structured precisely so it can be deleted per-user (GDPR Art 17 compliance shape)
