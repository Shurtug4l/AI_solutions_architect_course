# RAG in Production: Caching, Streaming, Scalability, Cost

## TL;DR

A RAG pipeline that works on a laptop is not a service. The move to production surfaces a set of concerns that the prototyping notebook never had to address: **scalability** (more users, more documents, more queries per second), **latency** (sub-second responses on real corpora), **cost** (token spend grows linearly with traffic), **freshness** (the corpus changes over time), **observability** (you need to know when it breaks and why), and **security** (the agent is now a public-facing service with access to real data). The single biggest lever in production is **caching** at multiple levels: embedding cache (compute each query embedding once), retrieval cache (memoize top-K for repeated queries), prompt cache (provider-side reuse of long prefixes, up to 75% cost reduction). The architectural shape that scales is **microservices on Kubernetes**: the document pipeline, embedder, vector DB, and LLM each run in their own pods, scaled independently. The shift from **batch** to **streaming** ingestion lets the corpus stay fresh; **incremental learning** keeps embeddings aligned without retraining. Production monitoring needs RAG-specific metrics (faithfulness, context relevance) on top of standard infra metrics (latency, throughput, error rate); LLM judges run asynchronously on logged traffic. Security comes from zero-trust access control, end-to-end encryption, prompt-injection defences, GDPR-compliant audit trails. Cost optimisation stacks aggressive caching with quantised smaller models and reserved-instance billing for predictable loads. Each lever has a cost-benefit profile; the right order to add them is data-driven, starting from whichever metric the current pipeline blows.

## Cheatsheet

| Concept | One-line | Where it shows up |
|---|---|---|
| **Caching** | Avoid recomputing the same thing | Single biggest cost lever |
| **Embedding cache** | Memoize query / chunk embeddings | Cheapest cache layer |
| **Result cache** | Memoize top-K retrievals for repeated queries | Reduces vector-DB load |
| **Prompt cache** | Provider-side reuse of long prefixes | 50-90% reduction on long contexts |
| **Streaming RAG** | Continuous ingestion + incremental indexing | When data freshness < hours matters |
| **Incremental learning** | Update embeddings without full retraining | Keeps embeddings aligned with new data |
| **Sharding** | Split the vector DB across nodes | Scales to billions of vectors |
| **Quantisation** | int8 / int4 representations of vectors and weights | 2-8x compression at small quality cost |
| **Kubernetes microservices** | Each component in its own pod, scaled independently | The shape that production wants |
| **LLM judge async** | Evaluate on logged traffic, not on the hot path | Catches drift without latency cost |
| **Zero-trust + RBAC** | Every request authenticates, finest-grain authorisation | Production security baseline |
| **Reserved instances** | Pre-purchase compute for predictable loads | Cost optimisation for steady-state traffic |

---

## From prototype to production

The transition is not gradual; it is a different problem. A notebook RAG handles a single query, single user, predictable data, no SLA. A production RAG handles concurrent queries, evolving corpora, billed cost, latency budgets, audit requirements.

Three components have to scale together:

| Component | What changes |
|---|---|
| **Document pipeline** | From "load PDFs" to "ingest streaming updates from multiple sources" |
| **Embedding** | From "embed once" to "incremental + batched + cached" |
| **Inference** | From "one call" to "load-balanced LLM instances with auto-scaling" |

The injection of retrieved context inflates input tokens; serving them costs both time and money at scale. Distributed architectures and hardware acceleration are not optional past a certain volume.

---

## Scalable architecture

Three foundations the deck flags:

- **Distributed vector databases** for data scale.
- **Kubernetes** for compute auto-scaling.
- **Asynchronous ingestion pipelines** for keeping the corpus fresh without blocking.

### Component breakdown

```
                  ┌──────────────────────────────────┐
                  │            API gateway            │
                  └──────────────┬───────────────────┘
                                 │
                  ┌──────────────┴───────────────────┐
                  │       LLM service (pool)         │
                  └──────────────┬───────────────────┘
                                 │ retrieve
                  ┌──────────────┴───────────────────┐
                  │     Vector DB (sharded)          │
                  └──────────────────────────────────┘
                                 ▲
                                 │
                  ┌──────────────┴───────────────────┐
                  │    Embedder service              │
                  └──────────────┬───────────────────┘
                                 ▲
                                 │
                  ┌──────────────┴───────────────────┐
                  │   Document ingestion pipeline    │
                  │  (Kafka / Airflow / event-driven)│
                  └──────────────────────────────────┘
```

Each layer is **independently scalable**:

- **Document pipeline**: scale based on ingestion volume.
- **Embedder**: scale based on documents-per-minute being processed.
- **Vector DB**: scale storage and query throughput separately.
- **LLM service**: scale based on query rate.

### Microservices in pods

Each component runs in its own Kubernetes pod, with:

- **Persistent volumes** for data (vector DB, embedding cache).
- **Secrets** for credentials (API keys, DB passwords).
- **Service mesh** (e.g. Istio) for routing and observability.
- **Helm charts** for standardised deployment.
- **GitOps** for declarative, traceable infrastructure changes.

### Custom auto-scaling metrics

Default Kubernetes auto-scaling triggers on CPU and memory. For RAG, the **right metrics** are domain-specific:

| Metric | Why it matters |
|---|---|
| **Retrieval latency p95** | The bottleneck when traffic spikes |
| **LLM call queue depth** | The downstream bottleneck |
| **Embedder queue length** | Ingestion pipeline backup |
| **Cache hit rate** | Health of the caching layer |

Auto-scale on these. CPU and memory are lagging indicators.

---

## Caching: the biggest cost lever

The single most impactful optimisation in production RAG. Three caching levels stack.

### Embedding cache

The query embedding is deterministic: the same query always produces the same vector. Cache by query hash:

```python
def embed_cached(query: str) -> Vector:
    if query in cache:
        return cache[query]
    vector = embedder.embed(query)
    cache[query] = vector
    return vector
```

Implementation: Redis or an in-process LRU cache. Hit rate depends on the traffic shape; popular queries (FAQ, common help requests) generate high hit rates.

The same applies to document embeddings during ingestion: once embedded, the vector does not change until the chunk does.

### Result cache

Memoize the top-K retrieval for a (query, top-K) pair. Same trade-off as embedding cache but on a coarser granularity.

```python
def retrieve_cached(query: str, k: int) -> list[Chunk]:
    key = hash((query, k))
    if key in cache:
        return cache[key]
    chunks = vector_db.search(embed_cached(query), k=k)
    cache[key] = chunks
    return chunks
```

Invalidate when the corpus changes. The invalidation strategy is the tricky part:

- **Time-based** (TTL): simple, can serve stale results.
- **Event-based** (invalidate on document update): correct, more complex.
- **Versioned**: include a corpus version in the cache key.

### Prompt cache

The most impactful cache, exposed by major LLM providers. The first time you submit a long prompt, the provider processes it into internal Key/Value tensors (the **KV cache**). On subsequent calls with the same prefix, the cached state is reused and you pay only for the new tokens, with **discounts up to 90%** on the cached portion.

This matters disproportionately for RAG because the augmentation prompt template is the same across calls, and the retrieved chunks for popular queries repeat.

**Provider support**:

- **Anthropic**: explicit `cache_control` markers in the prompt.
- **Google Gemini**: context-caching API.
- **OpenAI**: automatic prefix caching above a threshold (no explicit API needed).

Module 03 exercise 06 uses a CAG fallback that is conceptually the same: a fixed pre-baked context that should be cached aggressively.

### Semantic caching

A more sophisticated cache: instead of matching queries exactly, match queries that are **semantically similar** (embedding cosine > threshold). The cache serves results for queries that are close enough.

```
Query 1:  "How do I reset my password?"
Query 2:  "What is the procedure for password recovery?"
                 │
                 ▼
        cosine similarity > 0.92
                 │
                 ▼
        serve cached result of Query 1
```

Trade-off: faster cache hits, risk of serving slightly inappropriate results. Tune the threshold and validate on held-out queries.

### Intelligent routing

ML-based decision on whether to use the cache or run the full pipeline. Factors:

- Query similarity to cached entries.
- Cache freshness (TTL elapsed?).
- Confidence threshold the user requires.

Production systems use cheap signals (embedding similarity) to decide between cache hit, cache update, and full retrieval.

---

## Streaming RAG: keeping the corpus fresh

A static RAG indexes the corpus once and answers from that snapshot. When the underlying data changes - news, status pages, product catalogues, support tickets - the answers become stale.

**Streaming RAG** ingests data continuously and updates the index incrementally.

### Three components

- **Streaming ingestion**: Kafka, Pulsar, or cloud-native event buses (AWS Kinesis, GCP Pub/Sub) carry new documents into the pipeline as they appear.
- **Incremental indexing**: add new chunks to the vector DB without rebuilding it. HNSW and IVF both support incremental insertion.
- **Dynamic retrieval**: the retriever uses the index version available at query time; new documents become searchable seconds after ingestion.
- **Time-aware reconciliation**: when documents update over time, the retriever needs to know which version is current. Versioning + timestamp filters handle this.

### When streaming matters

| Scenario | Why |
|---|---|
| **Real-time recommendation** | Product catalogue changes by the minute |
| **Operational dashboards** | Status / incident data updates continuously |
| **Predictive maintenance** | Sensor data feeds the corpus |
| **News / financial analysis** | Knowledge has to reflect "as of right now" |

For most enterprise RAG (manuals, policies, support docs), nightly batch updates are enough.

---

## Embedding maintenance

The embedder is part of the pipeline, and the corpus drifts away from it over time.

### Periodic retraining vs incremental learning

| Strategy | Mechanism | Cost | Use |
|---|---|---|---|
| **Periodic retraining** | Re-embed the entire corpus with the new embedder | High | When the embedder is upgraded |
| **Incremental learning** | Update embeddings for new / changed chunks only | Low | Day-to-day operation |

A hybrid pattern: incremental on new chunks during normal operation, full re-embed periodically (e.g. quarterly) when the embedder is upgraded or fine-tuned.

### Embedding versioning

Each embedding has a version tag. Multiple versions can coexist during a migration:

```
chunk_id  |  embedder_version  |  vector
─────────────────────────────────────────
chunk_1   |  v1.0              |  [...]
chunk_1   |  v2.0              |  [...]
```

The retrieval layer reads the current version; rollback is changing a config flag. Critical for production: an embedder upgrade that degrades performance must be reversible within minutes.

---

## Retrieval performance at scale

Three orthogonal levers.

### Distributed and sharded vector DBs

Horizontal scaling: split the vector index across multiple nodes. Each node holds a slice of the vectors; queries are routed to all nodes in parallel and results are merged. Pinecone, Qdrant, Milvus all support sharding natively.

The trade-off: latency on a single query stays low even at billions of vectors; consistency across shards is the operational concern (rebalancing, replication).

### GPU acceleration

The vector similarity computation is embarrassingly parallel and benefits hugely from GPU. FAISS-GPU and Milvus-GPU mode push QPS by an order of magnitude over CPU.

Cost-benefit: GPU instances are expensive. Use them when the query rate justifies it; for low-traffic production systems CPU is enough.

### Quantisation

Compress the vectors:

- **Scalar quantisation**: 32-bit floats → 8-bit ints. 4x compression, small quality loss.
- **Product quantisation (PQ)**: split each vector into sub-vectors, quantise each independently. 8-16x compression.
- **Binary quantisation**: 1 bit per dimension. 32x compression, larger quality loss.

Combine with IVF (IVFPQ): IVF partitions the space, PQ compresses within each partition. The standard for truly large vector stores.

### Index choice trade-off

| Index | Recall@10 | Latency | When |
|---|---|---|---|
| **Flat (brute force)** | 1.0 | High | Small datasets, baseline |
| **HNSW** | 0.95-0.99 | Low | The default for most production |
| **IVF** | 0.85-0.95 (depends on `nprobe`) | Variable | Tunable for large scale |
| **IVFPQ** | 0.80-0.90 | Low | Largest scale, RAM-constrained |
| **LSH** | 0.70-0.85 | Low | Mostly historical |

The choice is empirical: measure recall@10 against an exact-search ground truth on a sample; pick the cheapest index that meets your recall target.

---

## Monitoring and observability

Production needs more metrics than dev.

### Standard infra metrics

- **Latency**: p50, p95, p99 per endpoint.
- **Throughput**: QPS sustained, peak.
- **Error rate**: 4xx, 5xx, timeout.
- **Resource utilisation**: CPU, memory, GPU.

### RAG-specific metrics

| Metric | What it tracks | Frequency |
|---|---|---|
| **Context relevance** | Are retrieved chunks relevant? | Sampled, asynchronous |
| **Faithfulness** | Is the answer grounded in retrieved chunks? | Sampled, asynchronous |
| **Answer relevancy** | Does the answer address the query? | Sampled, asynchronous |
| **Cache hit rate** | Effectiveness of caching | Continuous |
| **Retrieval latency** | Time the vector DB takes | Continuous |
| **LLM latency** | Time the generator takes | Continuous |
| **Hallucination rate** | Proxy: low faithfulness count | Sampled |

The semantic metrics (faithfulness, relevance) use LLM-as-judge from RAGAS / DeepEval (see [06_rag_evaluation.md](06_rag_evaluation.md)). Run them asynchronously on logged traffic to avoid latency cost.

### Logging structure

Every request produces a log line that contains:

- Request ID + user ID + session ID.
- Query text and any preprocessing applied.
- Retrieved chunk IDs with similarity scores.
- Full prompt sent to the LLM.
- LLM response.
- Latency at each stage.

This is what makes post-hoc debugging possible. Use structured logging (JSON) and pipe to a log aggregator (Datadog, Splunk, ELK).

### Alerting

Trigger alerts on:

- Metric drops below threshold (faithfulness < 0.7).
- Cache hit rate drops.
- p99 latency spikes.
- Error rate elevates.

Calibrate thresholds carefully; over-alerting trains the team to ignore alerts.

### A/B testing

Production-grade RAG systems serve experiments: route 5% of traffic to a new chunking strategy, measure metrics, decide to promote or rollback. The decoupled async evaluation pipeline makes A/B testing cheap to set up.

---

## Security: real data, real users

Five layers, all required at some level.

### Access control

- **Zero-trust** architecture: every request authenticates and authorises, no implicit trust based on network location.
- **Role-based access control (RBAC)**: fine-grain permissions on which documents a user can search, which models they can call, which APIs they can invoke.
- **Tenant isolation**: in multi-tenant deployments, each tenant's data is separated at the storage level (separate indexes, separate vector DBs).

### Data protection

- **Encryption at rest**: vector DB, document store, embedding cache.
- **Encryption in transit**: TLS everywhere.
- **PII redaction**: scrub personal information from documents before indexing.
- **Audit trails**: immutable logs of who accessed what, when. Required for GDPR / HIPAA / similar.

### Model security

- **Prompt injection defence**: validate user input, separate system prompt from user input clearly, escape special characters that could break the prompt structure.
- **Output filtering**: scan responses for leaked PII, secret tokens, unauthorised actions.
- **Rate limiting**: per-user and per-endpoint.

### Compliance

- **GDPR**: right to be forgotten requires being able to remove a user's data from the corpus and the embeddings.
- **AI Act (EU)**: classification of use case, documentation, transparency requirements.
- **SOC 2 / ISO 27001**: organisational compliance for enterprise customers.

See [08_ethics_and_governance.md](08_ethics_and_governance.md) for the regulatory landscape in depth.

### SDLC

The development pipeline itself is part of the threat model:

- Code review for security issues.
- Dependency scanning.
- Penetration testing before launch.
- Threat modeling for new features.

---

## Cost optimisation

Cost in production RAG comes from three sources: **LLM token spend**, **embedder compute**, **vector DB hosting**. Levers in order of impact:

| Lever | Typical savings | Effort |
|---|---|---|
| **Prompt caching** | 50-90% on input cost | Low (just enable) |
| **Embedding cache** | 30-50% on embedder cost | Low |
| **Smaller / quantised models** | 50-80% on LLM cost | Medium (need to validate quality) |
| **Reserved instances** | 30-60% on infra cost | Medium (commit to a baseline) |
| **Batch processing** | 50% on LLM cost (via batch APIs) | Medium |
| **Auto-scaling** | Variable | High (architectural) |

### Smaller models with quantisation

A 7B model quantised to int4 can replace a 70B model on many tasks at a fraction of the cost. Validate on your task before swapping; quality differences can be subtle.

### Reserved instances

For predictable workloads, pre-purchasing compute (AWS Reserved Instances, GCP Committed Use, Azure Reservations) is 30-60% cheaper than on-demand. The trade-off: commit to a baseline.

### Spot instances

For batch workloads (initial indexing, periodic re-embedding), spot / preemptible instances are 60-80% cheaper. Tolerate the interruption risk with checkpointing.

### Cost governance

The deck flags three practices:

- **Real-time cost monitoring**: dashboards on token spend per endpoint, per tenant, per feature.
- **Chargeback models**: in multi-team organisations, attribute costs to teams so they have skin in the game.
- **Cost SLO**: budget per query; alert when exceeded.

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| In-memory cache with multiple replicas | Cache miss across replicas, hit rate near zero | Use Redis or a shared cache |
| Result cache without invalidation strategy | Stale answers after document updates | TTL or event-based invalidation |
| Prompt cache without measuring | "Why is the API not cheaper?" | Verify cache hits in the response headers |
| LLM judge on the hot path | Latency spikes | Decouple: log + async evaluation |
| Auto-scaling on CPU only | Lagging response to traffic spikes | Auto-scale on retrieval latency or queue depth |
| One vector DB shard | Single point of failure | Sharding + replication |
| Embedder upgrade without versioning | Inconsistent retrieval, no rollback | Embedding version tag from day one |
| Logging the user's query verbatim with no redaction | PII in logs | Redact at log time |
| Same secret across environments | Compromise in dev = compromise in prod | Per-environment secrets, rotation policy |
| Cost monitoring only at month end | One bad change burns thousands before detection | Real-time dashboards + budget alerts |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Reduce input-token cost | Prompt caching | Largest single lever |
| Repeated identical queries (FAQ, popular questions) | Result cache | Skip the whole pipeline |
| Repeated similar queries | Semantic cache | More cache hits, slight quality risk |
| Corpus updates daily or less | Batch ingestion | Simpler, cheaper |
| Corpus updates hourly or faster | Streaming RAG with Kafka / Kinesis | Real-time freshness |
| Embedder upgrade | Periodic full re-embed with versioning | Safe rollback |
| New documents only | Incremental learning | Cheap, fast |
| < 1M vectors | Single-node vector DB | Sharding adds complexity |
| > 10M vectors | Sharded vector DB | Single node is the bottleneck |
| > 1B vectors | IVFPQ-style compression on a sharded DB | RAM constraints dominate |
| < 10 QPS | CPU-only | GPU not worth the cost |
| > 100 QPS | GPU + sharded DB | CPU cannot keep up |
| Single tenant | Simpler isolation, tenant=org | Less ops complexity |
| Multi-tenant SaaS | Per-tenant namespace + RBAC | Required for security |
| Regulatory environment | RBAC + audit trails + GDPR delete | Compliance baseline |

---

## See also

### Other notes
- [04_rag_fundamentals.md](04_rag_fundamentals.md) — the pipeline being scaled
- [05_advanced_rag.md](05_advanced_rag.md) — the upgrade components added in production
- [06_rag_evaluation.md](06_rag_evaluation.md) — the metrics that drive monitoring
- [08_ethics_and_governance.md](08_ethics_and_governance.md) — GDPR, AI Act, the regulatory ceiling
- Module 03 [07_deployment.md](../../03_agentic_ai/notes/07_deployment.md) — the HTTP-service wrapper around the agent + RAG

### Related work in this repo
- Module 02 capstone (`PRJ_rag_system_for_company_knowledge.py`) — in-memory pipeline that would map cleanly onto these production primitives if it were to ship
- Module 03 exercise 07 — the deployment wrapper covered for a single-agent service
