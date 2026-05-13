# Long-Term Memory: RAG, CAG, and Vector Stores

## TL;DR

Short-term memory dies at the end of the session. Long-term memory persists. The mechanism is to write the things worth keeping into an **external store** and retrieve them when relevant - the agent never has to fit everything in the context window, only the relevant slice. Two flavours of long-term memory matter operationally: **episodic** (events and experiences with temporal context, like "this user opened three tickets last month"), **semantic** (general domain knowledge, like a product manual). The standard pattern for surfacing this memory at query time is **RAG** (Retrieval-Augmented Generation): chunk the source documents, embed each chunk into a vector, store the vectors in a **vector database**, and at query time embed the question and retrieve the top-K most similar chunks. Modern long-context models enable an alternative, **CAG** (Cache-Augmented Generation): if the corpus fits in the context window, skip the indexing entirely and load everything once via prompt caching. RAG wins when the corpus is large, dynamic, or fact-specific; CAG wins when the corpus is small, stable, and the questions need a synoptic view. The full retrieval pipeline has multiple knobs: **chunking** strategy (fixed / sentence / recursive / hierarchical / semantic), **embedding** model (symmetric vs asymmetric, dimensionality), **similarity metric** (cosine, euclidean, dot product), **index type** (HNSW, IVF, flat), **reranking** (cross-encoder over the top candidates), and **hybrid search** (dense + sparse fusion via RRF). Quality is measured with RAGAS or DeepEval against a manually-built test set; the four metrics that matter are **faithfulness**, **answer relevancy**, **context precision**, and **context recall**.

## Cheatsheet

| Concept | One-line | Where it shows up |
|---|---|---|
| **Episodic memory** | Events with temporal context | "User asked about X on March 15th" |
| **Semantic memory** | Domain knowledge, facts | Product manual, company policy |
| **Procedural memory** | Learned routines / workflows | Reusable plans, optimised prompts |
| **RAG** | Retrieve from external store at query time | Standard pattern for grounded answers |
| **CAG** | Load full corpus in context (with caching) | Small corpora, long-context models |
| **Embedding** | Text → high-dim vector capturing meaning | Foundation of semantic search |
| **Cosine similarity** | Cosine of angle between vectors | Standard metric for text embeddings |
| **Chunking** | Splitting documents into retrievable pieces | First and most impactful step |
| **Reranking** | Cross-encoder over top-K candidates | Sharpens precision after retrieval |
| **Hybrid search** | Dense + sparse (BM25) fusion via RRF | Catches keyword queries vector search misses |
| **RAGAS** | LLM-as-judge metric framework | Faithfulness, relevancy, context precision/recall |

---

## Why long-term memory

Short-term memory (trimming, summarisation, entity memory - see [05_short_term_memory.md](05_short_term_memory.md)) handles the current conversation well. All three have the same hard limit: **when the session ends, everything goes**. The next time the user comes back, the agent does not know them. The budget they shared, the preferences they expressed, the constraints they specified are gone.

Long-term memory solves this by **moving information out of the context window** into a persistent store, and retrieving only what the current query needs.

```
Session A                            Session B (next week)
─────────────                         ─────────────
"My budget is €9,847"  ──persist──►  "I know your budget is €9,847"
"Python preferred"     ──persist──►  "I know you prefer Python"
```

The store is not in the prompt; only the relevant slice is, at the right moment.

### Three flavours

| Type | What it stores | Example |
|---|---|---|
| **Episodic** | Events and experiences with temporal context | "Marco opened three tickets last month, all on the same issue" |
| **Procedural** | Learned skills and routines | Optimised prompt templates, consolidated workflows |
| **Semantic** | General facts and domain knowledge | Product documentation, company policies, scientific definitions |

The three are not mutually exclusive. A production agent often maintains all three: episodic per user, procedural per task family, semantic over the company's corpus.

---

## Embeddings: the foundation

A traditional database finds documents that contain the exact words you query (`WHERE name = 'Marco'`). For long-term memory the right query is *"find documents that mean something similar to my question"*. The mechanism is **embeddings**: a function that turns text into a vector of numbers (typically 768, 1536, or 3072 dimensions) where sentences with similar meaning produce vectors that are close in space.

```
"the dog barks"        → [0.23, -0.81, 0.45, 0.12, ...]    # 1536 numbers
"the dog makes noise"  → [0.21, -0.79, 0.44, 0.15, ...]    # very similar
"the bag is red"       → [-0.54, 0.33, -0.21, 0.87, ...]   # very different
```

### How embeddings learn

The model is trained on billions of sentence pairs, learning a simple rule:

- Sentences appearing in similar contexts → close vectors.
- Sentences appearing in different contexts → distant vectors.

There is no hard-coded synonym table. The geometry is *learned* from the distribution of language.

### Generating an embedding

```python
from openai import OpenAI
client = OpenAI()
resp = client.embeddings.create(input="the dog barks", model="text-embedding-3-small")
vector = resp.data[0].embedding   # 1536-dim list of floats
```

With Ollama (used across module 03 exercises) the equivalent is `OllamaEmbeddings(model="nomic-embed-text")` from `langchain-ollama` - same interface, local execution, 768 dimensions.

### Choosing a model

| Concern | Default |
|---|---|
| Multilingual corpus | `paraphrase-multilingual-MiniLM-L12-v2` (free, 384-d) or Cohere `embed-multilingual-v4.0` |
| Highest quality, hosted | OpenAI `text-embedding-3-large` (3072-d) |
| Local, free | Ollama `nomic-embed-text` (768-d) |
| Fast and cheap | OpenAI `text-embedding-3-small` (1536-d) |

### Symmetric vs asymmetric

Some embedders are optimised for comparing texts of the **same type** (sentence-vs-sentence). RAG queries are *asymmetric*: a short query vs a longer document. Models like Cohere `embed-v4.0` expose a `search_query` mode and a `search_document` mode that get embedded differently. Using the right mode on each side measurably improves retrieval quality.

### The silent truncation trap

Every embedder has a maximum input length. If the input exceeds the limit, the model **silently truncates** to the first N tokens - no error, no warning. A 50-page PDF passed directly to an embedder produces a vector representing only the first few pages.

This is the reason chunking exists: long documents must be split into chunks that fit cleanly under the embedder's limit.

---

## Similarity metrics

Once everything is a vector, *"similar"* needs a precise definition. Three metrics dominate:

| Metric | Formula | When |
|---|---|---|
| **Cosine similarity** | `cos(θ) = (a · b) / (\|a\| \|b\|)` | Default for text embeddings |
| **Euclidean distance** | `\|a - b\|` | Sensitive to vector magnitude |
| **Dot product** | `a · b = Σ aᵢbᵢ` | Equivalent to cosine when vectors are unit-normalised |

**Cosine similarity** measures the angle between vectors, not the distance. Two documents can have very different lengths (10 words vs 1000) and still be semantically close; cosine ignores magnitude and focuses on direction. It is the standard for text embeddings.

**Dot product** is mathematically equivalent to cosine when vectors are normalised - and computationally cheaper, since it skips a division. Many vector databases use dot product internally for this reason.

**Euclidean distance** is sensitive to magnitude; meaningful only on normalised vectors, even then less common than cosine for text.

### Semantic search in code

```python
def semantic_search(query, corpus, embed_fn, top_k=3):
    query_vec = embed_fn(query)
    corpus_vecs = [embed_fn(doc) for doc in corpus]
    scores = [cosine_similarity(query_vec, dv) for dv in corpus_vecs]
    ranked = sorted(zip(scores, corpus), reverse=True)
    return ranked[:top_k]
```

This is the entire algorithm - and exactly what every vector database does internally, just with an index on top so it does not have to compare against every vector.

---

## RAG: Retrieval-Augmented Generation

An LLM only knows what was in its training data. It does not know your internal documents, anything after its training cutoff, or your domain-specific data. RAG solves this by providing the relevant information at query time, retrieved from an external store.

### The full pipeline

```
OFFLINE (index)                   ONLINE (per query)
                                  
documents                         user question
   │                                  │
   ▼                                  ▼
chunking                          embed query
   │                                  │
   ▼                                  ▼
embedding ──► vector DB ◄────── retrieve top-K
                                      │
                                      ▼
                                  augment prompt:
                                  [system + chunks + query]
                                      │
                                      ▼
                                  LLM generates
```

### Offline phase

The index is built once (or when documents change):

```python
# 1. Chunking
chunks = split_document(document, chunk_size=512, overlap=50)

# 2. Embedding
vectors = [embed(chunk) for chunk in chunks]

# 3. Indexing
for chunk, vector in zip(chunks, vectors):
    vector_db.add(vector=vector, text=chunk)
```

The vector database stores both the vector (for similarity search) and the text + metadata (returned when a hit is found).

### Online phase

Each query goes through:

```python
# 4. Embed the query
query_vector = embed(user_query)

# 5. Retrieve
results = vector_db.search(query_vector, top_k=5)
chunks = [r.text for r in results]

# 6. Augment the prompt
prompt = system_prompt + chunks + user_query

# 7. Generate
response = llm.invoke(prompt)
```

### The augmentation prompt

How the chunks are injected into the prompt matters more than people often realise. A grounded prompt template:

```
You are an assistant that answers questions ONLY based on the documents provided.
If the answer is not in the documents, say so explicitly:
  "I do not have enough information on this topic."

DOCUMENTS:
{chunks}

QUESTION: {query}

Cite the document of reference when possible.
```

The explicit fallback clause is what prevents the model from filling gaps with its parametric knowledge - which is exactly the kind of hallucination RAG is meant to avoid.

### RAG is not magic

A common expectation: RAG will fix bad documents. It will not. RAG retrieves what is there:

- Ambiguous documents → ambiguous retrieval
- Contradictory documents → contradictory retrieval
- Incomplete documents → no answer, possibly hallucinated

Garbage in, garbage out. The quality of the knowledge base is a prerequisite, not a detail.

### RAG vs fine-tuning

The two solve different problems and compose.

| | RAG | Fine-tuning |
|---|---|---|
| Updates with new info | Yes, re-index | No, requires retraining |
| Domain style | No (model writes in its default style) | Yes (model adopts the style) |
| Hallucinations on specifics | Mitigated when retrieval succeeds | Still possible on facts not memorised |
| Cost per query | Low (one embedding + one LLM call) | Same as base model |
| Cost to set up | Pipeline + vector DB | GPU training run |

You can RAG over a fine-tuned model. The two are complementary.

---

## Chunking: the underrated step

Chunking happens **before** anything else - before embedding, before retrieval, before generation. Errors here propagate downstream with no recovery. A badly built chunk produces a misleading embedding, the embedding produces wrong retrieval, the retrieval produces a wrong answer or a hallucination.

**The quality of your chunking sets the ceiling on the quality of your RAG.**

### The fundamental trade-off

| Large chunks | Small chunks |
|---|---|
| Contain more information | More precise embeddings |
| The embedding represents an average of too many concepts | Can cut a concept in half |
| Retrieval finds the right chunk but brings in noise | Lose the surrounding context |
| Approach the embedder's token limit | Many more vectors to index |

### Strategies

| Strategy | How it splits | Trade-off |
|---|---|---|
| **Fixed-size** | Every N tokens with M-token overlap | Simple, predictable; can cut mid-sentence |
| **Sentence splitting** | At natural sentence / paragraph boundaries | Coherent units; variable length |
| **Recursive splitting** | Hierarchy of separators: paragraph → sentence → word | The pragmatic default; LangChain's `RecursiveCharacterTextSplitter` |
| **Hierarchical** | Same document at multiple granularities | Best of small and large chunks; complex; storage cost |
| **Semantic** | An embedder detects topic shifts and splits there | Highest coherence; expensive to compute |

### Overlap matters

Fixed-size and recursive splitting both rely on **overlap** between adjacent chunks. Without it, a concept landing on the boundary between two chunks gets split in two, and neither chunk represents it correctly. A typical overlap is 10% of the chunk size (50 tokens on a 512-token chunk).

### Size guidance

There is no universally optimal chunk size. Sensible defaults:

| Document type | Chunk size |
|---|---|
| Dense technical (code, contracts) | 256-512 tokens |
| Narrative or articles | 512-1024 tokens |
| FAQ / knowledge base | One chunk per Q/A pair |

Start at 512 tokens with 10% overlap and tune from there based on retrieval quality.

---

## Vector databases

A traditional database answers exact queries (`WHERE name = 'Marco'`). A vector database answers similarity queries (`"give me the 5 vectors closest to this"`). Internally it maintains, for each entry:

- The **vector** (for similarity search).
- The **payload**: the original text and associated metadata (source, date, tags, anything else useful at retrieval time).

### Picking one

| Need | Pick | Why |
|---|---|---|
| Prototyping, dev | **ChromaDB** | Zero config, in-process, perfect to start |
| Production without ops | **Pinecone** or **Qdrant Cloud** | Managed, auto-scaling |
| On-prem, maximum performance | **FAISS** or **Milvus** | Full control, billions of vectors |
| Hybrid queries (semantic + keyword + filters) | **Weaviate** | Most flexible retrieval |

There is no "best" vector DB; there is the one that fits the operational context.

### With LangChain

The full pipeline reduces to four components:

```python
# Load
loader = PyPDFLoader("doc.pdf")
docs = loader.load()

# Chunk
splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)
chunks = splitter.split_documents(docs)

# Embed + index
vectorstore = Chroma.from_documents(chunks, embedding=OllamaEmbeddings(model="nomic-embed-text"))

# Retrieval-augmented QA
qa = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever())
qa.invoke({"query": "What is the pricing of the Business plan?"})
```

The only step LangChain does *not* fully abstract is chunking - because the strategy is too critical to delegate to the framework.

### Index types

Exact nearest-neighbor search means comparing the query to every vector in the database. This does not scale; production needs **Approximate Nearest Neighbor (ANN)** algorithms.

| Index | Idea | When |
|---|---|---|
| **HNSW** | Hierarchical navigable small-world graph | The dominant choice; good speed/recall trade-off |
| **IVF** | Partition the space into clusters with k-means; search only the closest clusters | Tunable via `nprobe` (more clusters = higher recall, lower speed) |
| **Flat (brute force)** | No approximation | Small datasets, baseline for measuring ANN recall |
| **PQ (Product Quantization)** | Compress vectors to save RAM | Huge datasets; often combined with IVF (`IVFPQ`) |
| **LSH** | Hash-based bucketing | Mostly historical; HNSW dominates today |

### Evaluation metrics for ANN indices

- **Recall@k**: how often the ANN top-k matches the exact top-k. `recall@10 = 0.95` means in 95% of cases the ANN returns the same results as exhaustive search.
- **Latency**: p95 / p99 query time (not the average - the tail matters).
- **Throughput**: QPS the system can sustain.

---

## RAG vs CAG

Until recently, context windows were 4k or 8k tokens. Chunking and retrieval were mandatory. Modern long-context models change the equation:

| Model | Context window |
|---|---|
| GPT-4o | 128k tokens |
| Claude 3.5 Sonnet | 200k tokens |
| Gemini 1.5 Pro | 1,000k tokens |

If the corpus fits, you can skip the indexing pipeline entirely and just load everything into the context. This is **CAG** (Cache-Augmented Generation).

### How CAG works under the hood

The trick is **prompt caching**, exposed by the major providers. The first time you submit a large context, the model processes it into internal Key/Value tensors (the "KV cache"). On subsequent calls with the same prefix, the cached state is reused - subsequent queries only pay for the new tokens, with discounts that can reach 90% of the input token cost.

### When each wins

| Pick RAG when | Pick CAG when |
|---|---|
| The corpus is large or grows over time | The corpus is small (< 100k tokens) |
| Cost per query matters | Documents change rarely |
| Questions are about specific facts | You are prototyping and want to move fast |
| You need to cite exact sources | Questions need a synoptic view of the corpus |

### Quality differences

- **CAG suffers from Lost in the Middle.** On very long contexts the model neglects information in the middle of the prompt, even if it is technically present.
- **RAG suffers from imprecise retrieval.** If the retriever does not find the right chunks, the model answers with incomplete information or hallucinates.

The two are not mutually exclusive. Module 03 exercise 06 combines them: RAG is the primary path; CAG (in the form of a fixed fallback context) fires when the retriever returns nothing useful. This is the canonical *graceful degradation* pattern for retrieval systems.

---

## Reranking

Vector similarity is not the same as relevance. A chunk can be "close" to the query for the wrong reasons (shared vocabulary, similar topic, but actually unrelated to the question). The fix is a **two-stage retrieval**:

```
1. Vector search: retrieve top-K (e.g. top-20) candidates - fast, recall-oriented.
2. Reranker:      rerank those K candidates - slow, precision-oriented.
3. Take top-N (e.g. top-3) from the reranked list.
```

### Bi-encoder vs cross-encoder

- A **bi-encoder** (used by the vector DB) embeds the query and the chunk *separately*, then compares the vectors. Fast to index, but the query and chunk never "see" each other - the model cannot capture specific interactions between them.
- A **cross-encoder** (used by the reranker) takes the (query, chunk) pair *together* as input and outputs a single relevance score. Much more accurate; too slow to use at index time.

The two-stage pattern combines the strengths: bi-encoder for breadth (recall), cross-encoder for sharpness (precision).

### When reranking is worth the cost

| Pick reranking when... | Skip it when... |
|---|---|
| Questions are specific and factual | Questions are open-ended and exploratory |
| Corpus contains many similar documents | Corpus is varied and distinctive |
| Faithfulness is low and the cause is bad chunks in the top-K | Faithfulness is already high |
| The cost of a wrong answer is high (legal, medical, support) | Cost per query is the bottleneck |

### LLM-based reranking

Instead of a dedicated cross-encoder, ask an LLM to score each chunk against the query. More flexible (the relevance criterion is in the prompt) but with two caveats:

- **N LLM calls for N chunks.** Latency adds up; cap `top-K` aggressively.
- **Inconsistent scores.** The same chunk can score differently across runs; LLMs tend to favour well-written chunks regardless of relevance.

---

## Hybrid search

Vector search is great at finding semantically similar documents. It is bad at finding documents that contain a **specific, unambiguous term** - a product code, an error string, a name. Keyword search (BM25) is the inverse: it nails exact terms but misses synonyms.

The solution is to use both, in parallel, and fuse the results.

```
        query
          │
   ┌──────┴──────┐
   ▼             ▼
 vector       keyword
  search      (BM25)
   │             │
   └──────┬──────┘
          ▼
  Reciprocal Rank Fusion (RRF)
          │
          ▼
     top-K ranked results
```

### Reciprocal Rank Fusion

RRF scores each document by its **position** in the two rankings, not by its absolute score:

```
RRF(doc) = Σ over retrievers of  1 / (k + rank_in_retriever)
```

A document that appears in both retrievers shoots to the top, even if it is not first in either. The hyperparameter `k` (typically 60) controls how aggressively top ranks dominate.

### Hybrid search vs reranking

The two address different problems:

| | Hybrid search | Reranking |
|---|---|---|
| Goal | Increase **recall** (find more relevant docs) | Increase **precision** (filter the noisy ones) |
| Mechanism | Combine multiple retrievers | Re-score with a cross-encoder |
| Where in pipeline | Retrieval stage | After retrieval |

They compose: hybrid search → reranking → final top-N. The first widens the net, the second sharpens it.

---

## RAG Evaluation

A fluent answer does not mean a correct answer. An LLM in a RAG pipeline can:

- Answer "from memory" while ignoring the retrieved chunks.
- Retrieve the wrong chunks and synthesise convincingly anyway.
- Get the right answer by accident, not because the pipeline worked.

Without systematic evaluation you cannot tell which part of the pipeline is the bottleneck, and you cannot tell whether your changes are improvements or regressions.

### RAGAS: the four metrics

RAGAS (and DeepEval) evaluate the pipeline on four LLM-judged metrics:

| Metric | What it measures | Diagnoses |
|---|---|---|
| **Faithfulness** | Is the answer supported by the retrieved chunks? | LLM hallucinating beyond context |
| **Answer relevancy** | Does the answer actually address the question? | LLM going off-topic |
| **Context precision** | Are the retrieved chunks useful for the question? | Retriever returns noise |
| **Context recall** | Did the retriever find all the relevant chunks? | Retriever misses information |

Each metric returns a score in [0, 1]. The test set is a list of `(question, expected_answer)` pairs, built manually or semi-automatically.

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall

results = evaluate(
    dataset=test_dataset,
    metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
)
```

### How the judging works

RAGAS uses an LLM to evaluate each (question, answer, chunks) tuple. For faithfulness, for example:

1. Extract each claim in the answer.
2. Ask the LLM: "is this claim supported by the retrieved chunks?"
3. Compute the ratio supported / total.

### The limits of LLM-as-judge

| Limit | Why it matters |
|---|---|
| **Cost** | N LLM calls per evaluation; 100 questions can add up |
| **Test set effort** | Building good Q/A pairs is manual |
| **Judge can be wrong** | An LLM evaluating an LLM inherits its biases |
| **Not deterministic** | Different runs on the same dataset yield different scores |

### Reading the results: diagnosing the failure mode

| Failure pattern | Likely cause | Fix |
|---|---|---|
| High recall, low precision | Retriever pulls in noise | Reranking, smaller chunks |
| High precision, low recall | Retriever misses information | Larger chunks, hybrid search, higher top-K |
| Low faithfulness | LLM ignores context | Sharper prompt, fewer/better chunks |
| Low answer relevancy | LLM goes off-topic | Better system prompt |

### Optimisation loop

The single most important rule: **change one component at a time**. Otherwise you cannot attribute the change in scores to a specific intervention. Vary chunk size, then embedder, then top-K, then reranker - one at a time, against the same test set.

### Test set design

| Good questions | Avoid |
|---|---|
| Have a unique, verifiable answer in the corpus | Ambiguous or opinion-based |
| Cover different parts of the corpus | Only first-page questions |
| Include questions the pipeline should NOT answer | "What is the document about?" (too generic) |

### Alternatives to RAGAS

**DeepEval** is the main alternative used in production: same metrics plus Hallucination / Toxicity / Bias, integrates with pytest (RAG tests become part of CI/CD), and ships with a dashboard.

---

## Composing it all

A real production RAG agent typically stacks several of the components above:

```
documents
   │
   ▼
chunking (recursive, 512 / 50 overlap)
   │
   ▼
embedding (asymmetric, search_document mode)
   │
   ▼
vector DB (Chroma / Qdrant / Pinecone, HNSW index)
   │
query ──► embedding (search_query mode) ──► retrieval (top-20)
                                              │
                                              ▼
                                          hybrid: + BM25 ──► RRF fusion
                                              │
                                              ▼
                                          reranker (cross-encoder top-5)
                                              │
                                              ▼
                                          augmented prompt ──► LLM
                                              │
                                              ▼
                                          answer + sources
```

Each stage in this stack is optional. The smallest viable RAG is `chunk → embed → vector DB → retrieve top-K → augment`. Every additional component buys quality at the cost of complexity and latency. Add them when the RAGAS scores tell you that you need them, not before.

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Documents pasted directly into the embedder | Silent truncation to first N tokens | Always chunk before embedding |
| Different embedder for indexing vs querying | Vectors are not comparable | Same model on both sides, always |
| Symmetric embedder used for asymmetric task | Lower retrieval quality | Use search_query / search_document modes when available |
| No overlap in fixed-size chunking | Concepts split across two chunks lose meaning | 10% overlap minimum |
| Chunk size much larger than the embedder's limit | Truncation kicks in | Pick chunk size below the embedder's token limit |
| Vector DB only, on a corpus full of codes / names | Vector miss-rate on the unambiguous terms | Add hybrid search (BM25) |
| Top-K too low | Recall is the bottleneck | Increase K, then rerank |
| Top-K too high without reranking | Precision drops, noise in context | Add a reranker after retrieval |
| Augmentation prompt without a fallback clause | Model hallucinates when no chunk is relevant | Explicit "if not in the context, say so" |
| Evaluating with no test set | No way to tell if changes help | Build 50 Q/A pairs as a baseline |
| Changing two components and the chunker at once | Cannot attribute score changes | One change at a time |
| Cached context not invalidated when corpus changes | Stale answers | Track corpus hash; bust cache on change |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Persist facts across user sessions | LTM with vector store | Survives session boundaries |
| Small corpus, model has long context | CAG with prompt caching | No pipeline, lowest latency after first call |
| Large or growing corpus | RAG | Indexing scales; CAG does not |
| Need to cite sources | RAG | Retrieved chunks carry their origin |
| Specific keyword / product codes matter | Hybrid search (BM25 + vector) | Vector alone misses exact terms |
| Many similar documents, low precision | Reranking after retrieval | Cross-encoder sharpens the top-K |
| Quality stagnates and you cannot tell why | RAGAS / DeepEval | Diagnose the bottleneck per metric |
| Prototyping / dev | ChromaDB | Zero config, in-process |
| Managed production | Pinecone, Qdrant Cloud, Weaviate | Pick by hybrid / filter / pricing needs |
| Self-hosted, massive scale | FAISS, Milvus | Full control, billions of vectors |

---

## See also

### Other notes
- [01_agents_vs_workflows.md](01_agents_vs_workflows.md) — agents use LTM as a tool of last resort
- [02_agent_components.md](02_agent_components.md) — memory as the fifth building block; STM vs LTM definitions
- [04_frameworks.md](04_frameworks.md) — LangChain's `Chroma.from_documents`, `RetrievalQA`, vector store integrations
- [05_short_term_memory.md](05_short_term_memory.md) — Entity Memory is the bridge; persist the dict and you have rudimentary LTM
- [07_deployment.md](07_deployment.md) — vector DB persistence and secret management for the embedder API key

### Exercises that exercise the concepts in this note
- [`06_ex_customer_support_rag_cag_episodic.ipynb`](../exercises/06_ex_customer_support_rag_cag_episodic.ipynb) — full RAG pipeline (ChromaDB + nomic-embed-text), CAG fallback for off-topic queries, episodic memory with persistence-trigger
- Also covered in module 02 capstone: `02_large_language_models/PRJ_rag_system_for_company_knowledge/PRJ_sistema_rag_conoscenza_aziendale.py` — hybrid sem + BM25 + recency, category filters, larger corpus
