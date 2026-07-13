# LLM, RAG and Semantic Search

## TL;DR

An LLM does not know anything. It collects text, associates it, and predicts what comes next, so its output is plausibility, not truth. That is the whole reason this topic sits inside a governance module: to make an LLM useful on company knowledge you have to feed it governed material at query time, and **RAG (Retrieval-Augmented Generation)** is the mechanism that does it. Three primitives matter and they are easy to confuse. An **LLM** understands natural language but has no memory and cannot tell true from plausible. **Semantic search** interprets the meaning of a request and returns documents or pointers, fast and cheap and transparent, but it is not a chatbot. **RAG = LLM + semantic search**: natural-language answers grounded in retrieved context. The catch, and the course's actual point, is that a RAG is only as trustworthy as the data governance behind it. Ungoverned sources give you an answer that "looks right but is not", delivered with total confidence. The distinctive lens here is not how to build a retriever (module 02 covered that), it is which documents are allowed in, who is permitted to see them, how the answer cites its source, and how freshness is maintained. RAG is the interface, governance is what works behind the scenes to make it reliable, sustainable, and explainable.

## Cheatsheet

| Concept | One-line | Governance signal |
|---|---|---|
| **LLM** | Predicts the next token, understands language, no memory | Plausible, not verified. Never a source of record |
| **Semantic search** | Retrieves by meaning, returns docs/pointers | Fast, cheap, transparent, auditable ranking |
| **RAG** | LLM answer grounded in retrieved context | Answer is only as good as the governed corpus |
| **Chunk** | A document segmented into a retrievable unit | Carries metadata for classification and lineage |
| **Embedding** | Numeric vector of a chunk's meaning | Must be regenerated when sources or model change |
| **Vector store** | DB of embeddings plus their metadata | Access filters and provenance live here |
| **Retrieval** | Query embedded, nearest vectors returned | This is semantic search inside the pipeline |
| **Context injection** | Retrieved texts handed to the LLM | The only knowledge the model is allowed to use |
| **Provenance / citation** | The answer names the document it used | Makes output traceable and explainable |
| **Freshness** | Corpus and index kept current | Expired docs removed, index rebuilt on change |

## Three primitives, and why RAG is the governed one

> The AI does not know. It collects information, associates it, and predicts what happens next. So it is not truth, it is likeness to truth. The job is to let governed knowledge "speak" to the model.

The three tools are not interchangeable, and picking the wrong one is a governance failure before it is an engineering one.

| Primitive | PRO | CONTRO |
|---|---|---|
| **LLM** | Understands natural language | No memory, recognises only the plausible, not the true |
| **Semantic search** | Fast, cheap, transparent | Does not converse, returns pointers not answers |
| **RAG** | Natural language and contextualisable | Complex, costly, governance-heavy, risk of "looks right but is not" |

A distinction the slides make and that people flatten constantly: semantic search is not a chatbot. It reads meaning and hands back documents or links, it does not compose an answer. RAG is what wires the two together, running the search first and letting the LLM speak over the result. Confusing "it found the right document" with "it gave the right answer" is the root of most disappointed RAG expectations.

**Opinion:** the "looks right but is not" failure is the dangerous one precisely because it is fluent. A wrong keyword search returns visibly nothing; a wrong RAG answer returns a confident paragraph with the tone of a manual. That is why the governance controls below are not optional polish.

## What they buy for knowledge management

> They enormously ease the knowledge management cycle. They let you acquire company knowledge in natural language and reduce the risk that information is neither shared nor kept current.

- Query internal knowledge in plain language instead of knowing where every document lives.
- Cut the two chronic KM failures at once: non-sharing (the knowledge exists but nobody finds it) and obsolescence (the knowledge is found but stale).
- Shorten the time to interrogate sources, and fold that interrogation into governance instead of bypassing it.

This is the bridge from [05_from_data_to_knowledge.md](05_from_data_to_knowledge.md) and [06_knowledge_management_techniques.md](06_knowledge_management_techniques.md): RAG is a delivery channel for knowledge that has already been curated, not a shortcut around curating it.

## The RAG pipeline: seven steps

> A real pipeline of consequential events. At which point it is evident that data governance is fundamental for correct handling of traceability and correctness of the data.

```
  [1] Source        internal (docs, DBs) + external (sites, manuals)
        |
  [2] Ingestion     extract -> clean -> chunk -> register metadata (lineage, class)
        |
  [3] Embedding     chunk -> vector of meaning; store vector + metadata
        |
  [4] Retrieval  <--- user query -> embedding -> nearest vectors  (= semantic search)
        |
  [5] Context inj.  retrieved texts handed to the LLM
        |
  [6] Generation    LLM answers; downstream filters + cross-check   <== GOVERNANCE
        |
  [7] Feedback       log queries, collect user feedback, evaluate embeddings
```

1. **Source.** Identify where the data lives: internal (company documents, databases) or external (sites, manuals). Selection starts here, not at the end.
2. **Ingestion and preprocessing.** Extract from the sources, clean, and segment logically into **chunks**, recording **metadata** that is essential to classification and lineage. Chunking is a design decision: split so that one chunk answers one question. Bad chunk boundaries cap retrieval quality no matter how good the model is.
3. **Embedding and indexing.** Produce a numeric representation of the chunk's meaning and store those vectors in a database alongside their metadata. The metadata is what later lets governance filter and trace.
4. **Retrieval.** The heart of the RAG. The query is converted to an embedding and the most similar vectors are found. This is exactly semantic search, running inside the pipeline.
5. **Context injection.** The retrieved texts are handed to the LLM as the context it is allowed to use.
6. **Generation.** The LLM generates the answer, then downstream filters apply: linguistic validation, cross-checking for correctness. This is the stage the course explicitly puts under data governance supervision.
7. **Feedback loop.** Queries are logged and users give feedback, which measures the effectiveness of the process and of the embedding model itself.

Step 7 is easy to read as a product feature and miss as a governance instrument. Logging every query with its result is the audit trail: it records who asked what, in what context, and what the system answered, which is exactly the evidence a high-risk system needs when someone later asks why an answer was given. The user feedback on top is the signal that tells you an embedding model has drifted out of usefulness before it silently degrades the whole corpus.

**Enrichment, anchored:** the slides describe pure vector retrieval. In practice a governed corpus of manuals and error codes benefits from **hybrid retrieval** (semantic plus lexical/BM25) so that exact identifiers like an error code or a station name are not lost to fuzzy meaning, with **reranking** on top to reorder the shortlist. That machinery was covered in module 02; here the point is that whatever retriever you pick, its inputs and its ranking must stay auditable.

## RAG + Data Governance: the actual course topic

> Without data governance the data used for retrieval is not accurate and coherent, so the information can be distorted or wrong. An excellent way to make a RAG generate answers full of holes and errors.

This is the distinctive part of the module. A RAG does not add a governance problem, it inherits and amplifies the one already in the corpus. Four controls map onto the pipeline stages above.

| Governance concern | What it does | Where it bites in the pipeline |
|---|---|---|
| **Quality and validation** | Validate correctness and adherence to company standards: completeness, accuracy, consistency. Often automated control systems | Ingestion (2), before anything is embedded |
| **Access control and security** | Assign roles and permissions. Every query filtered by the caller's access rights. Every query audited: who, in what context, with what result | Retrieval (4) and logging (7) |
| **Lifecycle management** | Data, models, and processes have an expiry. Embeddings refreshed when sources change, expired or obsolete documents removed. When the LLM changes, regenerate everything from scratch | Embedding (3) and feedback (7) |
| **Bias and ethics** | Governance sets the guidelines that contain or at least monitor the errors, whether interpretive or ethical, that the data carries | Generation (6), and upstream at source (1) |

Two of these deserve emphasis because they are where a RAG differs from a plain search box.

**Access-filtered retrieval.** The permission model has to live in the retrieval step, not in a disclaimer after the fact. A query must only ever see the chunks the caller is entitled to, which means the vector store's metadata carries the access labels and retrieval filters on them before ranking. Filtering the generated answer instead of the retrieved context leaks information: the model already saw what it should not have.

**Freshness and the "changed the rules" principle.** The slide states it plainly: "if I change the rules, the game has changed." Change a source document and its embeddings are stale; change the embedding model or the LLM and the whole index has to be regenerated, because vectors from two different models are not comparable. Staleness is the silent failure of a RAG that "invents" on old data, the same pattern flagged in [01_what_is_data_governance.md](01_what_is_data_governance.md).

> While the RAG is the practical interface, data governance works behind the scenes to make the whole process reliable and sustainable. It also makes it explainable. And there is no knowledge without sharing.

Explainability here is concrete, not a slogan: an answer that names the document and section it drew from can be checked, corrected, and trusted. An answer without provenance is just a fluent guess. Citation is therefore a governance requirement, not a UI nicety.

## Which primitive for which job

The examples from the slides sort cleanly by how much "truth" the task needs.

| Job | Use | Why |
|---|---|---|
| Customer support, standard/common-sense reply | **LLM** | The plausible answer is enough, no fresh or external data needed |
| Creative writing, a haiku, a short story | **LLM** | No ground truth to respect |
| Summaries and rewrites | **LLM** | Transforms text already in hand |
| FAQ: ranked list of relevant docs by relevance and recency | **Semantic search** | Wants pointers, not a composed answer |
| Searching for updated procedures | **Semantic search** | Meaning-based lookup over documentation |
| Resolving a precise error (explicit error code) | **RAG** | Contextualised problem, answer must be documented |
| Analytic documentation (contract clauses, precise company-doc answers) | **RAG** | Safe, reliable, well-sourced answer to a specific question |

The rule of thumb from the slides: use an LLM when the plausible is enough, semantic search when you need well-documented pointers, and RAG when you need a safe, reliable, sourced answer to a specific and contextualised problem. Everything depends on the problem and its context.

## Worked exercise: designing a governed RAG flow (railway safety)

The fictional case is a good governance drill because most of the work is deciding what not to trust. **Goal:** help technical managers identify switch safety systems that no longer meet current standards, based on official documentation. **Corpus:** a 1990 and a 2025 technical manual, emergency instructions, international rules, wagon specs, a list of station names. **Constraints:** safety, traceability, updating. **Warning: not all the documents are correct.**

1. **Be clear on the purpose.** The flow does not decide, it supports the decision by separating what is valid for this context from what is no longer valid. An LLM alone cannot do this, because it has no way to know which manual is current.
2. **Select the documentation.** Apply the key principles: review the corpus, keep what is safe, current, and traceable, discard the rest. Concretely, drop the station-name list (irrelevant to conformity), treat wagon specs as optional, and privilege the most up-to-date manual. This is governance's quality-and-validation control applied by hand, before embedding.
3. **Chunking.** Split the documents logically, driven by the operational question "under what conditions does a given rule apply?" The 2025 manual splits into minimum safety requirements, non-conformity conditions, and so on. Chunk quality caps everything downstream.
4. **Embedding.** Reduce each chunk to a semantic vector, grouping the manual into known categories such as components, safety rules, implementation. Crucially this is not compressing the content, it is mapping it onto something already known semantically.
5. **Retrieval.** Retrieve the chunks and compare versions against each other. Comparing the 1990 and 2025 phrasing of the same rule is the whole value, and its quality depends directly on the chunking.
6. **Output (context injection).** Return which elements are no longer implementable and point to the document that explains why. The output answers why something should not be done, in terms of comparison, reference, and context. It indicates the way, it does not decide causally.
7. **Supports.** Code is not mandatory. Writing editors, spreadsheets for chunks, tables, and concept diagrams are all fine, as long as the key principles hold throughout.

**Reading of the exercise:** the interesting decisions are all governance decisions. Discarding the station list, demoting the wagon specs, and preferring the 2025 manual are quality, relevance, and freshness judgements made before a single embedding exists. The retrieval and the model are the easy part.

## Gotchas

- **Trusting fluency.** "Looks right but is not" is the signature RAG failure. A confident paragraph is not evidence, and without a citation it is unverifiable.
- **Filtering the answer instead of the context.** Access control has to happen at retrieval. If forbidden chunks reach the model, the leak already occurred, whatever the output filter says.
- **Forgetting to re-embed.** New source or new model means the index is stale or incomparable. "If I change the rules, the game has changed" applies to every model swap, not just document edits.
- **Chunking as an afterthought.** Retrieval quality is capped by chunk quality. Splitting by fixed character count instead of by logical unit quietly wrecks a governed corpus.
- **Letting bad documents in.** A RAG amplifies whatever is in the corpus. "Not all the documents are correct" is the default assumption, not the edge case.
- **Semantic-only over exact identifiers.** Error codes, part numbers, and station names are lexical. Pure vector search can miss them, which is why hybrid retrieval earns its keep.

## See also

- [01_what_is_data_governance.md](01_what_is_data_governance.md) - the governance baseline; the "stale data, AI that invents" failure pattern is the RAG freshness problem
- [02_policies_standards_frameworks.md](02_policies_standards_frameworks.md) - policy/standard/role, the triple that operationalises access control and validation on the corpus
- [05_from_data_to_knowledge.md](05_from_data_to_knowledge.md) - the DIK pyramid; RAG delivers knowledge that curation already produced
- [06_knowledge_management_techniques.md](06_knowledge_management_techniques.md) - RAG as a KM delivery channel over governed knowledge
- [08_data_knowledge_architectures.md](08_data_knowledge_architectures.md) - where the vector store, knowledge graphs, and retrieval fit in the wider data architecture
- [09_practical_use_cases.md](09_practical_use_cases.md) - end-to-end scenarios that combine these controls
- [02_large_language_models/notes/04_rag_fundamentals.md](../../02_large_language_models/notes/04_rag_fundamentals.md) - Master module 02 covered the RAG mechanics (chunking, embeddings, hybrid retrieval, reranking, evaluation) in technical detail; this note is the governance lens on top
