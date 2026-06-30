# Advanced RAG: Modular Architectures, Hybrid, Reranking, Query Expansion, Multimodal

## TL;DR

Naive RAG (chunk → embed → top-K → augment → generate) is fast to build and usually disappointing in production. The reasons are well-documented: irrelevant chunks pollute the prompt, the model loses information across passes, the retriever fails on keyword-heavy or off-distribution queries. **Advanced RAG** is the family of techniques that fixes these failure modes by adding components **before** the retrieval (better indexing, query expansion, hybrid search) and **after** it (reranking, filtering, fusion). **Modular RAG** is the next step up: instead of a fixed pipeline, you build a graph of specialised modules with a router that picks the right path per query. The three workhorse upgrades are **hybrid search** (combine dense embeddings with sparse keyword search via reciprocal rank fusion - covered in module 03), **reranking** (a cross-encoder reorders the top-K candidates by joint query-document relevance), and **query expansion** (use an LLM to rewrite or augment the query before retrieval: multi-query, HyDE, decomposition, step-back). These three compose: expand the query (recall), retrieve candidates (broad), rerank (precision), then generate. **Multimodal RAG** extends the same pattern to images, tables, and audio via Vision-Language Models and joint embedding spaces. Each upgrade adds cost and latency; the right time to add one is when an evaluation (see [06_rag_evaluation.md](06_rag_evaluation.md)) shows the metric it targets has become the bottleneck.

## Cheatsheet

| Concept | One-line | When |
|---|---|---|
| **Naive RAG** | Chunk → embed → top-K → augment → generate | Default; works until it does not |
| **Advanced RAG** | Add pre-retrieval and post-retrieval components | Naive starts producing wrong answers |
| **Modular RAG** | Graph of specialised modules with a router | The pipeline shape needs to vary by query |
| **Hybrid search** | Dense (vector) + sparse (BM25), fused via RRF | Vector alone misses exact terms |
| **Reranking** | Cross-encoder reorders the top-K | Top-K has the right docs in the wrong order |
| **Query expansion** | Rewrite the query (multi-query, HyDE, step-back, decomposition) | The query phrasing is bad for retrieval |
| **HyDE** | LLM generates a hypothetical answer, embed and retrieve on that | Query is short, documents are long |
| **Multi-query** | LLM generates N query variants, run retrieval N times, merge | Single phrasing is hit-or-miss |
| **Multimodal RAG** | Same pipeline, but images / tables / audio in the corpus | The answers need non-textual evidence |
| **VLM** | Vision-Language Model that handles image + text jointly | Image-heavy documents |

---

## Why naive RAG breaks

Three failure modes show up reliably once a naive pipeline meets real users:

| Failure mode | What it looks like | Where it lives |
|---|---|---|
| **Low retrieval precision** | Irrelevant chunks in the top-K, prompt is polluted | Retriever |
| **Low retrieval recall** | The right chunk is not in the top-K | Retriever |
| **Weak generation** | Model produces redundant, contradictory, or shallow answers despite good chunks | Generator + prompt |
| **Brittleness across queries** | Works on test queries, fails on phrasings the engineer did not anticipate | Whole pipeline |

The Advanced and Modular architectures address these failure modes by adding components at the right stage of the pipeline.

---

## The three architectural tiers

The slides organise RAG into three architectures of increasing sophistication.

### Naive RAG

The pipeline from [04_rag_fundamentals.md](04_rag_fundamentals.md). One retriever, one generator, no extra components.

**Use when**: prototyping, low-stakes assistants, your corpus is small and the queries are predictable.

**Fails when**: production volume, varied query shapes, or quality requirements exceed what one-shot retrieval delivers.

### Advanced RAG

Naive RAG with **pre-retrieval** and **post-retrieval** modules added.

**Pre-retrieval upgrades**:

- Advanced indexing (semantic chunking, hierarchical chunks, structured metadata).
- Query optimisation (expansion, decomposition, HyDE - see below).
- Multi-strategy search (vector + keyword in parallel).

**Post-retrieval upgrades**:

- Reranking with a cross-encoder.
- Filtering and de-duplication.
- Context fusion across multiple retrieved chunks.
- Context-window optimisation before passing to the LLM.

**Use when**: naive RAG hits a quality ceiling and a metric framework (RAGAS, DeepEval) tells you which part of the pipeline to fix.

### Modular RAG

The pipeline is no longer fixed. Specialised modules are arranged in a graph, and a **router** decides which path to take per query.

**Components in a modular system**:

- Multiple retrievers (vector, keyword, knowledge graph, structured DB).
- A **memory module** that remembers previous turns / earlier user state.
- A **router** that classifies the query (intent, complexity, domain) and dispatches it.
- An **orchestrator** that coordinates the modules.
- Per-pipeline custom **algorithms** (hybrid search, ensemble retrieval).
- **Multi-agent coordination** for complex queries where a master agent delegates to specialised retrieval agents.

**Use when**: the system has to handle very different query types (factual lookup vs broad analytical question vs personalisation), or the retrieval needs depend on intent.

The modular pattern starts to overlap with the agent paradigms covered in module 03: routing is orchestration, the memory module is the long-term memory, multi-agent retrieval is a multi-agent system. Cross-link: [Module 03 / 04_frameworks.md](../../03_agentic_ai/notes/04_frameworks.md) for the framework side, [Module 03 / 06_long_term_memory.md](../../03_agentic_ai/notes/06_long_term_memory.md) for the memory side.

---

## Hybrid search

Pure vector search excels at semantic similarity and **fails on exact keyword matches**. A query that references a specific product code (`X-9000B`), a unique error string, or a proper noun may not produce a vector close to the chunk that contains those tokens.

Pure keyword search (BM25) has the inverse problem: it finds exact matches but misses paraphrases and synonyms.

**Hybrid search** runs both in parallel and fuses the results.

```
        user query
            │
   ┌────────┴────────┐
   ▼                 ▼
 dense            sparse
 (vector)         (BM25 keyword)
   │                 │
   └────────┬────────┘
            ▼
   Reciprocal Rank Fusion
            │
            ▼
       top-K results
```

### Reciprocal Rank Fusion (RRF)

The standard fusion algorithm. Each document gets a score based on its **position** in each retriever's ranking, not its absolute similarity score (the scales of dense and sparse scorers are incomparable).

```
RRF(doc) = Σ over retrievers of  1 / (k + rank_in_retriever)
```

A document appearing in the top of both retrievers shoots to the top of the fused list, even if it is not first in either. `k` (typically 60) controls how aggressively top ranks dominate.

### When hybrid search wins

- The corpus has technical vocabulary (codes, names, identifiers) that exact-match queries hit.
- Users alternate between conversational and keyword-style queries.
- Domain has many similar documents where exact distinguishing terms matter.

### When it does not help

- The corpus is mostly narrative, queries are conversational.
- Either retriever is so weak that fusion drags it back into the result set.

Module 03 exercise 04's LangChain agent uses a single vector retriever; the module 02 PRJ capstone uses semantic + BM25 + recency fusion and tunes the weights empirically.

---

## Reranking

The vector DB's similarity score is **not the same as the user's notion of relevance**. A chunk can be "close" to the query for the wrong reasons - shared vocabulary, similar topic but different focus.

**Reranking** is a two-stage retrieval pattern:

```
1. Retrieve top-K (e.g. top-20) via the fast bi-encoder vector search.
2. Rerank those K candidates with a cross-encoder (slow, accurate).
3. Take the top-N (e.g. top-3) from the reranked list.
```

### Bi-encoder vs cross-encoder

| | Bi-encoder | Cross-encoder |
|---|---|---|
| Mechanism | Embed query and chunk **separately**, compare vectors | Take query + chunk **as a pair**, output a relevance score |
| Speed | Fast at indexing and query time | Slow per pair |
| Quality | Recall-oriented | Precision-oriented |
| Used for | Initial retrieval over the whole corpus | Reordering the top-K |

The cross-encoder sees the two pieces of text *together* and can capture interactions a bi-encoder cannot. The cost is that you cannot precompute cross-encoder scores; every query + candidate pair has to be evaluated at query time.

### Architecture in practice

```
Query → bi-encoder → retrieve 100 candidates from vector DB
                     │
                     ▼
              cross-encoder reranker scores each candidate against the query
                     │
                     ▼
              keep top-K (5-10) by score
                     │
                     ▼
              feed to LLM
```

Cross-encoders for reranking come from a few sources:

- **Sentence-Transformers cross-encoders** like `cross-encoder/ms-marco-MiniLM-L-6-v2` (free, runs locally, fast for batches).
- **Cohere Rerank** (managed API, strong quality, paid).
- **LLM-based reranking** (use a regular LLM to score each candidate; flexible but slow and inconsistent).

### LLM-based reranking

Instead of a dedicated cross-encoder, ask an LLM to score each chunk's relevance to the query. The prompt is something like:

```
Given the query "{query}" and the document "{chunk}", rate the relevance
from 0 to 10. Return only the number.
```

Advantages: the relevance criterion is customisable in the prompt. Disadvantages: N LLM calls for N chunks (latency), inconsistent scores across calls (the model judges the same chunk differently on different runs), tendency to favour well-written chunks regardless of actual relevance.

### When reranking is worth the cost

- Queries are **specific and factual** - the right chunk matters more than the topical area.
- Corpus contains **many similar documents** - the bi-encoder can find the cluster but cannot pick the best member.
- **Faithfulness is low** in your evaluation - the LLM is hallucinating because the top-K does not actually contain the answer.
- **High-stakes outputs**: customer support escalations, legal, medical, anything where a wrong answer is expensive.

### Cost mitigation

Reranking adds real latency. Production deployments use:

- **Batch processing**: rerank multiple queries together.
- **Quantisation** of the cross-encoder.
- **Asynchronous reranking**: return preliminary results, refine in background (only viable for non-conversational UX).
- **Graceful degradation**: under load, fall back to the bi-encoder's top-K, accept the precision drop.

---

## Query expansion

Sometimes the bottleneck is not the retriever or the reranker; it is the **query itself**. A short, ambiguous, or jargon-poor query gets a bad embedding and the retrieval starts wrong.

Query expansion uses an LLM to rewrite or augment the query before retrieval. Four techniques.

### Multi-query

Generate N variants of the query, run retrieval on each, merge the results.

```
original: "How do I reset my password?"
variants:
  - "What is the procedure to reset a forgotten password?"
  - "Where can I find the password recovery option?"
  - "Steps to change account credentials"
```

Each variant retrieves a different set of chunks. Merging via RRF or deduplication gives a more diverse candidate pool than any single phrasing would. Helpful when users phrase the same need in many different ways.

Cost: N retrievals, N embeddings; the LLM call that generates the variants is small.

### HyDE (Hypothetical Document Embedding)

The query is short (a question), the documents are long (passages). Their embeddings live in slightly different parts of the space. **HyDE** has the LLM generate a **hypothetical answer** to the query, then embeds and searches on that.

```
query:              "What is photosynthesis?"
hypothetical doc:   "Photosynthesis is the process by which plants use
                     sunlight, water, and CO2 to produce sugars and
                     oxygen. The reaction occurs in chloroplasts..."
search vector:      embedding of the hypothetical doc
```

The hypothetical answer is in the *shape* of a document (a paragraph), not a question, so its embedding sits in the document region of the space. Documents that talk about photosynthesis become closer matches. The hypothetical answer can be wrong - that does not hurt; only its *vocabulary and topical signature* matter for retrieval.

### Decomposition (Chain-of-Thought retrieval)

Use the LLM to split a complex query into simpler sub-queries; retrieve for each.

```
query:    "What did Apple say about iPhone sales in Q3 2024?"
sub-queries:
  - "Apple iPhone sales 2024"
  - "Apple Q3 2024 earnings report"
  - "Apple quarterly results 2024"
```

Then either combine the results or use them sequentially (retrieve for sub-query 1, then sub-query 2 conditioned on the first result). The technique mirrors **Plan-Execute** at the retrieval layer: plan the retrieval steps first.

### Step-back (Least-to-Most)

The opposite move: when the query is very specific, ask the LLM to **broaden** it to higher-level concepts that documents might cover more abstractly.

```
specific query:    "Did the 2017 Lisbon Treaty amendment apply to ratification quorum?"
step-back query:   "EU treaty amendments and ratification procedures"
```

Retrieve on the step-back query, then ground the answer in the specific facts.

### Costs and trade-offs

Every query expansion technique adds an LLM call before retrieval. The LLM call cost is small relative to the LLM call for generation; the retrieval cost can grow significantly (multi-query at N=5 means 5× the retrieval work). The right time to use expansion is when the metric framework shows that retrieval recall is the bottleneck.

---

## How the three compose

Hybrid search, reranking, and query expansion **stack**:

```
                user query
                    │
                    ▼
        query expansion (multi-query, HyDE, ...)
                    │
                    ▼
      ┌─────────────┴─────────────┐
      ▼                           ▼
  dense retrieval         sparse (BM25) retrieval
      │                           │
      └─────────────┬─────────────┘
                    ▼
              RRF fusion
                    │
                    ▼
              top-100 candidates
                    │
                    ▼
          cross-encoder reranker
                    │
                    ▼
              top-10
                    │
                    ▼
           augmentation prompt
                    │
                    ▼
               LLM generates
```

The three layers do different jobs:

- **Query expansion** broadens the **recall**.
- **Hybrid search** ensures both keyword and semantic matches are caught.
- **Reranking** sharpens the **precision** before the LLM sees the chunks.

Each addition has a measurable cost and a measurable quality gain. The right time to add one is when the next note's metrics ([06_rag_evaluation.md](06_rag_evaluation.md)) say the corresponding bottleneck has become the main one.

---

## Multimodal RAG

The pipeline extends naturally to images, tables, and audio. The retrieval mechanism is the same (embed query, search for similar vectors); what changes is the embedder.

### Vision-Language Models (VLMs)

A VLM combines a **vision encoder** (CNN, ViT, etc.) with an **LLM**, trained so that paired image + text examples map close in a joint embedding space.

Two training paradigms:

- **Contrastive training** (CLIP-style): the model learns to map matching image-text pairs close, unmatched pairs far. Produces a shared embedding space where a text query can retrieve images and vice versa.
- **Generative training** (LLaVA-style): the VLM is trained to answer questions about images, building on a pretrained LLM with a vision encoder added.

VLMs power the multimodal RAG pipeline: same embedding step, but now images and text both end up in the same vector space.

### Multimodal embeddings

Three architectural patterns:

- **Unified embedder** (CLIP): one model encodes both text and images into the same space. Simple, direct cross-modal retrieval.
- **Dual encoder** with separate encoders per modality, plus a shared training objective. More flexibility per modality.
- **Multi-vector embeddings** (ColPali, ColBERT-style): generate multiple vectors per image or document. Higher granularity, more retrieval power, more storage.

### Beyond chunking

For documents with complex layouts (PDFs with tables, charts, embedded images), traditional chunking destroys the spatial relations between elements. VLMs like ColPali bypass chunking by **embedding the entire page** as a vector that preserves layout. Trade-off: higher quality retrieval, much more storage and compute.

### Retrieval strategies

| Strategy | When |
|---|---|
| **Unified cross-modal search** (CLIP) | Both modalities in the corpus; text query retrieves images and vice versa |
| **Modality-to-text preprocessing** | Convert images / tables to text via VLM summaries, then index as text | When the downstream LLM is text-only |
| **Multi-vector for tables** | Replace naive chunking with structured summaries | Tables benefit massively from this |

### Generation

The final answer is produced by a multimodal LLM. The leading options:

- **GPT-4o / GPT-4V**: handle interleaved text + image input natively.
- **LLaVA**: open-source multimodal LLM.
- **Claude 3.5 / Gemini 1.5 Pro**: strong multimodal capabilities.

### Evaluation

Multimodal RAG needs benchmarks adapted to cross-modal precision and recall. **ViDoRe** is the standard for document retrieval with mixed content. The cross-modal faithfulness metric measures how well the answer is supported by retrieved evidence across modalities.

### When multimodal RAG matters

- **Finance / legal**: contracts and reports mix text, charts, tables.
- **Medical**: case files include clinical notes, lab values, imaging.
- **Education / customer support**: manuals include diagrams and screenshots.

Multimodal pipelines are heavier than text-only ones (more storage, slower indexing, more expensive embedders). Use them when the answer genuinely needs non-textual evidence.

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Adding all three (hybrid + rerank + expansion) without measuring | Production cost explodes, quality gain unclear | Add one at a time, measure with RAGAS / DeepEval |
| Query expansion at N=10 with no reranking | Many retrieved chunks of varied relevance pollute the prompt | Pair expansion with reranking |
| Cross-encoder reranker too slow under load | p99 latency spikes | Quantise, batch, or fall back gracefully under load |
| HyDE on a query that already has document-shaped phrasing | No gain over plain retrieval | Use HyDE only on short questions |
| Hybrid fusion weights tuned on the wrong test set | Weights overfit the test, fail in production | Tune on a held-out query set; revisit periodically |
| Modular RAG built upfront for a small corpus | Over-engineered, slow to iterate | Start naive; add modules when the metrics demand it |
| Multimodal pipeline on a text-only corpus | Storage and compute overhead with no benefit | Stay text-only unless images / tables are real |
| Generator that ignores the retrieved context | Hallucinations even with good retrieval | Sharpen the augmentation prompt: "answer ONLY from the documents" |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Prototype, small corpus | Naive RAG | Cheapest path to first working system |
| Production, naive RAG underperforms | Advanced RAG (add one component at a time) | Targeted improvement |
| Production with diverse query shapes (factual, analytical, personalised) | Modular RAG with a router | One pipeline cannot fit all queries |
| Specific terms / codes matter | Hybrid search (dense + BM25) | Vector alone misses exact matches |
| Top-K has the right documents in the wrong order | Reranking with a cross-encoder | Sharpens precision |
| Query phrasing is highly variable | Query expansion (multi-query, HyDE) | Catches retrievals one phrasing alone misses |
| Specific questions over a large abstract corpus | Step-back query expansion | Find the broad concepts the documents cover |
| Multi-hop questions ("X did Y about Z in T") | Decomposition | Sub-queries map to retrievable sub-questions |
| Corpus has images, tables, charts | Multimodal RAG with VLMs | Text-only loses the visual evidence |
| Heavy PDFs with layout | ColPali-style page-level embedding | Skip the chunking, preserve layout |
| Quality bottleneck unclear | Run RAGAS, identify the bad metric | Then pick the matching upgrade |

---

## See also

### Other notes
- [04_rag_fundamentals.md](04_rag_fundamentals.md) — the naive pipeline this note extends
- [06_rag_evaluation.md](06_rag_evaluation.md) — RAGAS metrics; identify the bottleneck before adding components
- [07_rag_production.md](07_rag_production.md) — caching, streaming, scaling all interact with the advanced components
- Module 03 [03_paradigms_react_planexecute_reflexion.md](../../03_agentic_ai/notes/03_paradigms_react_planexecute_reflexion.md) — Plan-Execute is the agentic shape of query decomposition
- Module 03 [04_frameworks.md](../../03_agentic_ai/notes/04_frameworks.md) — LangGraph as the natural fit for modular RAG (each module is a node)
- Module 03 [06_long_term_memory.md](../../03_agentic_ai/notes/06_long_term_memory.md) — Reranking, hybrid search and RAG vs CAG also covered there with the agent-memory lens

### Related work in this repo
- Module 02 capstone (`PRJ_rag_system_for_company_knowledge.py`) — production-shaped hybrid retrieval with semantic + BM25 + recency, category and date filters
- Module 03 exercise 06 (`06_ex_customer_support_rag_cag_episodic.ipynb`) — RAG + CAG fallback (modular pattern in miniature)
