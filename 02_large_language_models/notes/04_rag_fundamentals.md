# RAG Fundamentals: Pipeline, Chunking, Vector Stores

## TL;DR

**Retrieval-Augmented Generation** is the pattern that lets an LLM answer questions about documents it was not trained on. The pipeline is short and the same in every implementation: **chunk** the source documents, **embed** each chunk into a vector, **store** the vectors in a database with their original text and metadata, **retrieve** the top-K most similar chunks for each new query, **augment** the prompt with those chunks, **generate** the answer. The retrieval half is the part that decides quality; the generation half is mostly the same LLM you would use anyway. **Chunking** is the most underrated step: a bad chunk produces a bad embedding produces bad retrieval produces a bad answer, and there is no recovery downstream. The five chunking strategies that matter in practice (fixed-size, recursive, structural, semantic, adaptive/LLM-based) trade simplicity for context preservation. The right **vector store** depends on scale and ops appetite: **ChromaDB** for prototyping and small projects, **Pinecone** for managed production, **Weaviate** for hybrid queries that mix semantic + keyword + graph + filters, **FAISS / Qdrant / Milvus** for self-hosted scale. The full advanced toolbox - hybrid search, reranking, query expansion, multimodal RAG - lives in the [next note](05_advanced_rag.md). This note is the foundation: the seven steps every RAG pipeline performs, plus the two infrastructure decisions (chunking, vector store) that bound the quality ceiling.

## Cheatsheet

| Concept | One-line | Where it shows up |
|---|---|---|
| **RAG** | Retrieve relevant chunks, inject into the prompt, generate | The whole point of this note |
| **Retriever** | The component that finds relevant chunks; the "search engine" half | Roughly 60% of RAG quality lives here |
| **Generator** | The LLM that produces the final answer from the augmented prompt | The other 40% |
| **Chunking** | Splitting documents into retrievable pieces | The first step; sets the ceiling |
| **Embedding** | Text → high-dimensional vector | Foundation of semantic search |
| **Vector store** | Database optimised for nearest-neighbour vector search | Where the retrieved chunks live |
| **Indexing** | Organising vectors for efficient retrieval (HNSW, IVF, etc.) | The thing that makes search scale |
| **Top-K retrieval** | Return the K vectors closest to the query | The basic operation |
| **Augmentation prompt** | The template that injects retrieved chunks into the LLM call | Shapes how the model uses the context |
| **LangChain / LlamaIndex** | The two dominant Python frameworks for RAG | LangChain for workflows, LlamaIndex for retrieval depth |

---

## What RAG is and what it solves

A pre-trained LLM only knows what was in its training data. It does not know:

- Your internal documents.
- Anything that happened after the training cutoff.
- Domain-specific data it never saw.

The naive fix is fine-tuning, which is expensive, slow to iterate, and irreversible. **RAG** is the cheap fix: give the model the relevant information *at query time*, by fetching it from an external database.

### When RAG is the right answer

Three scenarios from the deck:

- **Accuracy and reliability.** The model would hallucinate or guess. RAG grounds the answer in real text.
- **Information that changes.** News, scientific literature, product catalogues. RAG retrieves fresh; fine-tuning would need a retrain.
- **Personalisation.** RAG over the user's own data tailors answers to their context.

A practical heuristic: if "the answer is in the documents" is true for your task, RAG is usually the right pattern.

### What RAG does not solve

Three things RAG does NOT do, and that should not be expected of it:

- **Fix bad documents.** Garbage in, garbage out. If the source material is contradictory, ambiguous, or incomplete, retrieval brings those problems forward, not solves them.
- **Replace fine-tuning for style.** RAG injects facts; the model's tone, register, and writing style come from its pretraining + instruction tuning.
- **Eliminate hallucination.** A good augmentation prompt reduces hallucination significantly. A poor one (or a model that does not respect the context) lets hallucination through anyway.

---

## The seven steps

Every RAG pipeline performs the same seven operations, split into an offline phase (build the index) and an online phase (answer each query).

```
OFFLINE                              ONLINE (per query)
─────────                            ─────────────────

documents                            user query
    │                                    │
    ▼ (1) chunk                          ▼ (4) embed query
    │                                    │
    ▼ (2) embed each chunk               ▼ (5) retrieve top-K
    │                                    │
    ▼ (3) store in vector DB             ▼ (6) augment prompt
                                          │
                                          ▼ (7) generate
                                          │
                                          ▼
                                       answer
```

### 1. Chunking

Split the source documents into pieces small enough to embed, large enough to retain context. Detail in the [chunking strategies](#chunking-strategies-the-most-underrated-step) section below.

### 2. Embedding

Convert each chunk into a vector. The embedding model determines the geometric structure of the search space. Common choices: `text-embedding-3-small` (OpenAI, 1536-d), `nomic-embed-text` (Ollama, 768-d), `paraphrase-multilingual-MiniLM-L12-v2` (multilingual).

The same embedding model **must** be used both when indexing the documents and when embedding the query. Different models produce vectors that are not in the same space and cannot be compared meaningfully.

### 3. Indexing and storing

Store each (vector, chunk text, metadata) triple in a vector database. The database builds an **index** structure - HNSW, IVF, or similar - that makes the nearest-neighbour search fast. See the [vector stores](#vector-stores-where-the-retrieved-chunks-live) section below.

### 4. Query embedding

Embed the user's query with the same model. The result is a vector in the same space as the chunks.

### 5. Retrieval

Search the vector database for the K vectors closest to the query vector (cosine similarity is the standard metric). Return both the vectors and their original text + metadata.

Two patterns of retriever beyond the basic top-K:

- **Parent Document Retriever**: index small chunks for retrieval, return the larger parent chunk to the LLM. Combines precision with context.
- **Self-Query Retriever**: parse the query into a semantic part + a metadata filter. "Show me bug reports from Q3 2025 about authentication" becomes vector search over bug-report chunks with a `date in [2025-07, 2025-09]` filter.
- **Ensemble Retriever**: query multiple retrievers in parallel (different embedders, different indices, dense + sparse) and fuse the results.

### 6. Augmentation

Build the LLM prompt with the retrieved chunks. The prompt template is where most of the grounding quality comes from. A typical shape:

```
You are an assistant that answers questions ONLY based on the documents provided.
If the answer is not in the documents, say so explicitly:
  "I do not have enough information on this topic."

DOCUMENTS:
{chunks}

QUESTION: {query}

Cite the document of reference when possible.
```

The explicit fallback clause is what prevents the model from filling gaps with parametric knowledge. The citation requirement keeps the answer auditable.

### 7. Generation

Call the LLM with the augmented prompt and return the response. This is the same LLM call you would make anyway, with a different prompt.

---

## Chunking strategies: the most underrated step

Chunking happens before everything else - before embedding, before retrieval, before generation. Errors here propagate downstream with no recovery. A bad chunk produces an inaccurate embedding, the embedding produces wrong retrieval, the retrieval produces a wrong answer or a hallucination. **The quality of your chunking sets the ceiling on the quality of your RAG.**

### The fundamental trade-off

| Large chunks | Small chunks |
|---|---|
| Contain more information | More precise embeddings |
| The embedding represents an average of too many concepts | Can cut a concept in half |
| Retrieval finds the right chunk but with noise | Lose the surrounding context |
| Approach the embedder's token limit | Many more vectors to index |

The right size depends on the document, the embedder, and the query type. Defaults that work well: 512 tokens with 10% overlap for general text; 256-512 for dense technical material; 1024 for narrative or articles; one chunk per Q/A for FAQs.

### Strategies

**Fixed-size chunking.** Split every N tokens with M tokens of overlap. The simplest method. Predictable, fast, language-agnostic. Cuts sentences and concepts in half; over-rejects on structure-aware corpora. The right default for prototyping.

**Recursive chunking.** Try paragraph-level splits first; if a piece is still too big, recurse into sentences; then into words. LangChain's `RecursiveCharacterTextSplitter` is the pragmatic default for most cases. Preserves natural structure while guaranteeing a maximum size.

**Structural chunking.** Use the document's own structure as the split criterion: Markdown headers, HTML sections, code function definitions. Best when the input has reliable structure (technical docs, code).

**Semantic chunking.** Use an embedder to detect topic shifts. Compute embeddings for consecutive sentences or windows; when the similarity drops below a threshold, insert a split. Produces semantically coherent chunks at the cost of an embedding call per split. Worth it on stable corpora where retrieval quality matters more than indexing speed.

**Adaptive / LLM-based chunking.** Use an LLM to decide where to split. Extract individual propositions and let the model decide whether each one belongs to the current chunk or starts a new one. The most intelligent and contextual approach; also the slowest and most expensive. Useful for high-value corpora where retrieval quality matters most.

### Sliding window and overlap

Across strategies, overlap is what prevents concepts from being lost at boundaries. Without overlap, a sentence landing on the split is partially in two chunks but fully represented in neither. 10-20% overlap is the typical compromise between context preservation and storage cost.

The trade-off: overlap increases redundancy (same text appears in multiple chunks) and storage. Some pipelines add deduplication on the retrieval side to avoid returning multiple near-identical chunks as separate "documents".

### Metadata: filter before you search

Each chunk should carry metadata that lets you filter *before* the vector search:

```python
chunk = {
    "text": "...",
    "embedding": [...],
    "metadata": {
        "source": "policy_2025_q3.pdf",
        "section": "Authentication",
        "date": "2025-09-15",
        "category": "policy",
        "language": "en",
    }
}
```

A self-query retriever can then run `"How does auth work?"` over chunks where `category == "policy"` AND `date >= 2025-01-01`, drastically cutting noise.

### Preprocessing matters

The deck flags three things to do before chunking:

- **Cleaning and normalisation**: remove extra whitespace, fix encoding, normalise unicode. Reduces token waste and improves embedding quality.
- **Multimodal handling**: tables and images need to be extracted to text (OCR for images, structured extraction for tables) before being chunked.
- **Strategic summarisation**: for very long documents, summarise sections before indexing to keep chunk count manageable.

### Choosing a strategy

There is no universal answer. The right approach is **systematic evaluation**: build a test set of queries with known correct answers, vary the chunking strategy, measure retrieval precision and recall. See [06_rag_evaluation.md](06_rag_evaluation.md) for the metrics framework.

---

## Vector stores: where the retrieved chunks live

A vector database answers `"give me the K vectors closest to this query"` efficiently. Internally each entry has two parts:

- **The vector** (used for similarity search).
- **The payload**: the original text + metadata (returned with each hit).

The choice depends on scale, hosting, ops appetite, and the query shape you need.

### ChromaDB: prototyping and small projects

Open-source, simple, flexible. Uses SQLite for storage and HNSW for vector search. Three deployment modes:

- **In-memory** (zero config, perfect for notebooks and tests).
- **Local persistent** (file-based, single-process).
- **Client-server** (a separate Chroma server for multiple clients).

| Strengths | Limits |
|---|---|
| Zero config to start | Performs well up to ~1M vectors |
| Native Python integration (LangChain, LlamaIndex) | No high availability built-in |
| Powerful metadata filtering | Not designed for billions of vectors |
| Free, self-hosted | No managed cloud option |

The right choice for **prototyping**, **educational projects**, **internal tools**. The choice we use in module 03 exercise 06 and the module 02 capstone.

### Pinecone: managed production

Fully-managed serverless vector database. You hand it vectors and queries; Pinecone handles scaling, replication, and ops.

| Strengths | Limits |
|---|---|
| Sub-100ms latency at billions of vectors | Pay-per-use can be expensive at high constant load |
| 10k+ QPS sustained throughput | Vendor lock-in |
| Automatic scaling, no infra | Less control over the storage backend |
| Multi-tenancy via namespaces | |
| Hybrid search (dense + sparse) built-in | |

The right choice when **production reliability matters more than infrastructure control**, especially for companies without a dedicated platform team.

### Weaviate: hybrid queries

Open-source vector database with a built-in knowledge graph. Indexes vectors, keywords, and graph relations together; queries can combine them in a single GraphQL call.

| Strengths | Limits |
|---|---|
| Hybrid search (semantic + keyword + filter + relations) natively | Steeper learning curve |
| Multimodal data (text, image, audio) in the same store | More moving parts |
| Generative search: LLMs called from the DB | Self-hosted needs more competence than Chroma |
| Flexible deployment (Docker, K8s, managed cloud) | |

The right choice when **the query shape needs multiple retrieval mechanisms**, when **multimodal data** is in scope, or when **relations between data items** matter (knowledge-graph-style use cases).

### FAISS, Qdrant, Milvus

Three other production options worth knowing:

- **FAISS** (Meta): a library, not a server. Maximum performance for embedded retrieval. Best when you control the application and want to integrate retrieval inline.
- **Qdrant**: open-source, written in Rust. Strong filtering, fast indexing. Cloud and self-hosted.
- **Milvus**: open-source, distributed, scales to billions of vectors. Strong for large-scale on-prem deployments.

### Choosing

| Need | Pick |
|---|---|
| Prototype, learn RAG, small project | **ChromaDB** |
| Production without ops headache | **Pinecone** or **Qdrant Cloud** |
| Hybrid queries + multimodal + relations | **Weaviate** |
| Self-hosted, maximum performance, billions of vectors | **FAISS** or **Milvus** |
| Pure speed, embedded in an application | **FAISS** |
| Managed but want some self-hosting flexibility | **Qdrant** (offers both) |

---

## Query optimisation: making the search better

Sometimes the retrieval quality is bottlenecked by the query itself. Four techniques the deck mentions for **rewriting the query** before retrieval:

- **Multi-query.** Use an LLM to generate several variants of the query, run retrieval on each, merge the results. Catches retrievals that would miss if the user's phrasing happened to mismatch the documents.
- **Decomposition (Chain-of-Thought style).** Use the LLM to break the query into simpler sub-queries; retrieve for each. Useful for multi-hop questions ("What did X say about Y in 2023?" → retrieve X's statements about Y, filter by date).
- **Step-back (Least-to-Most).** Use the LLM to find the broader concepts the query touches on, then retrieve for those. Useful when the user's question is very specific and the documents talk about it more abstractly.
- **Hypothetical Document Embedding (HyDE).** Use the LLM to generate a *hypothetical answer* to the query, then embed and search using that. The hypothetical answer is in the same "shape" as the documents (a full passage rather than a question), which often improves retrieval similarity.

These belong technically to advanced RAG; deeper coverage is in [05_advanced_rag.md](05_advanced_rag.md).

---

## LangChain and LlamaIndex

Two Python frameworks that dominate the RAG ecosystem. They are complementary and overlapping.

### LlamaIndex

Designed for **indexing and retrieval depth**. Strong granularity in document organisation, with several index types:

- **Summary Index**: simple list of documents with summaries.
- **Keyword Table Index**: documents organised by keywords.
- **Tree Index**: documents in a hierarchical tree where parent nodes summarise children.
- **Knowledge Graph Index**: explicit graph of entities and relations.
- **Vector Store Index**: classical embedding-based semantic search.

Three core components: **data indexing**, **retriever**, **query engine** (the interface that ties query to retriever to answer).

### LangChain

Designed for **complex workflows**. Integrates LlamaIndex (and many other retrievers); the integration point is mostly at the **query engine** level. LangChain handles:

- Query contextualisation (rewriting the user's question into a better retrieval query).
- Conversation history and memory.
- Chaining the retriever to the LLM with prompt templates.
- Post-processing the response (summarising, filtering, validating).

### Worked example of integration

```
Original query:           "What is a neural network?"
Contextualised query:     "Explain in simple terms what a neural network is,
                           assuming the user has no computer-science background."

Pipeline:
1. User submits the query.
2. Query Engine contextualises it using an LLM.
3. Retriever returns relevant documents.
4. Query Engine summarises and synthesises the key content via a prompt chain.
```

### The summary

| Tool | Sweet spot |
|---|---|
| **LlamaIndex** | Optimises indexing and retrieval; best when retrieval quality is the bottleneck |
| **LangChain** | Manages the workflow; best when the system has memory, branching, conversational context |

In practice, both. LangChain's `Retrieval-QA` chain composes any LlamaIndex retriever; LlamaIndex's query engines can be wrapped in LangChain agents.

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Different embedder for indexing and querying | Vectors not in the same space, retrieval returns junk | Always use the same model on both sides |
| Documents fed directly to the embedder | Silent truncation past the model's max-token limit | Chunk before embedding |
| Top-K too high without reranking | Many noisy chunks in the prompt, model drifts | Reranking (next note) or smaller K + better embedder |
| No metadata, no filtering | Vector search alone returns noise on filterable queries | Add structured metadata, filter before search |
| Same chunk size for every document type | Either too granular for FAQs or too coarse for technical docs | Per-document-class chunking strategy |
| Augmentation prompt with no fallback clause | Model fabricates an answer when retrieval misses | "If not in the context, say so" |
| Augmentation prompt with the chunks at the end | Lost in the Middle: model ignores them | Place chunks early; query at the end |
| Vector DB chosen for the right reason | Outgrown three months later | Plan for the next 10x of scale; consider migration cost |
| Chunks without source metadata | Cannot cite, cannot audit | Always store source + chunk index in metadata |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| LLM should answer about private documents | RAG | Cheapest grounding |
| Frequently changing knowledge | RAG | Re-index instead of retrain |
| Personalised answers using user history | RAG over the user's data | Tailored, no fine-tune |
| Prototyping | ChromaDB + LangChain | Fastest to first running RAG |
| Production, managed | Pinecone or Qdrant Cloud | Scales without ops |
| Self-hosted scale | Qdrant / Milvus / FAISS | Choose by interface preference |
| Hybrid + multimodal + filter-heavy | Weaviate | Built for that shape |
| Pure speed, embedded | FAISS | Library, not server |
| Long-form narrative documents | Recursive or semantic chunking, 512-1024 tokens | Preserves continuity |
| Code / technical docs | Structural chunking on headers / functions | Respects structure |
| FAQs | One chunk per Q/A pair | Natural unit |
| Hard-to-retrieve specific terms | Add hybrid search (next note) | Pure vector misses exact matches |

---

## See also

### Other notes
- [01_llm_foundations.md](01_llm_foundations.md) — the LLM half of every RAG pipeline
- [02_model_landscape.md](02_model_landscape.md) — picking the generator model
- [03_prompt_engineering.md](03_prompt_engineering.md) — the augmentation prompt is a special case
- [05_advanced_rag.md](05_advanced_rag.md) — hybrid search, reranking, query expansion, multimodal RAG
- [06_rag_evaluation.md](06_rag_evaluation.md) — RAGAS metrics; how to know whether your RAG works
- [07_rag_production.md](07_rag_production.md) — caching, streaming, scaling
- Module 03 [06_long_term_memory.md](../../03_agentic_ai/notes/06_long_term_memory.md) — RAG as long-term memory for agents

### Related work in this repo
- Module 02 exercise 04 (`04_ex_rag_chatbot_company_faq.ipynb`) — first hands-on RAG pipeline
- Module 02 capstone (`PRJ_sistema_rag_conoscenza_aziendale.py`) — production-flavoured hybrid retrieval (sem + BM25 + recency, category filters)
- Module 03 exercise 06 (`06_ex_customer_support_rag_cag_episodic.ipynb`) — RAG + CAG fallback + episodic memory on Ollama
