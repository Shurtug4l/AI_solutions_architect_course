# Architectures for LLM and generative AI

## TL;DR

Generative AI **creates** content instead of classifying or forecasting it, and the engine behind the text side is the **LLM**: a Transformer trained on trillions of words that does **next-token prediction**, with all its "knowledge" compressed into the network weights. Out of the box that engine ships with two factory defects that drive every architectural decision: **hallucinations** (plausibility wins over factual truth, delivered with full confidence) and the **knowledge cut-off** (frozen at training time, blind to recent events and to private company data). The architect answers two strategic questions. Hosting: **external API** (fast, SOTA, data leaves the building) vs **self-hosted** open source (privacy and control, you own the GPU and MLOps burden). Knowledge: **fine-tuning** with **LoRA** (implicit memory, cheap adapters, good for style and format) vs **RAG** (explicit memory, retrieve-augment-generate, good for facts). The slide-level golden rule holds up in practice: **RAG for the "what", fine-tuning for the "how"**. Production systems then compose these blocks: **hybrid search** (vectors + BM25 + reranking) inside the RAG retrieval stage, **multi-model routing** to keep cost and latency sane, and **workflows before agents**, promoting a deterministic pipeline to an autonomous ReAct loop only when rigidity actually hurts.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **Generative AI** | Creates new content, does not just predict | Output is produced token by token, not picked from a list |
| **LLM** | Transformer doing next-token prediction | Knowledge lives compressed in the parameters |
| **Hallucination** | Syntactic plausibility beats factual truth | Invented facts stated with high confidence |
| **Knowledge cut-off** | Training ends on a date, memory freezes | Model is blind to recent and private data |
| **API hosting** | Someone else's model over HTTPS | Prototype in minutes, data leaves the company |
| **Self-hosted** | Open-source model on your infrastructure | Full privacy and control, GPU + MLOps cost |
| **Fine-tuning (LoRA)** | Train tiny adapters, freeze the base | MB-sized files, hours on one GPU, style transfer |
| **RAG** | Retrieve documents, paste into the prompt | Fresh facts without retraining, citable sources |
| **Hybrid search** | Vectors + keywords + reranking | Semantics for concepts, BM25 for exact codes |
| **Model router / cascading** | Small model triages, big model reasons | Big cost cut with quality where it matters |
| **AI workflow** | Deterministic pipeline, LLM as one node | Testable, predictable, the enterprise default |
| **AI agent** | LLM decides the steps (ReAct loop) | Flexible, less predictable, variable cost |

## Generative vs predictive AI

Predictive AI, the kind covered since module 01, analyses existing data to classify or forecast: sales history in, revenue prediction out; email in, spam or not-spam out. It is analytical, it discriminates among known answers. Generative AI produces new data: an answer that did not exist before, token by token for text (GPT, Qwen, Gemini on the Transformer architecture) or pixel by pixel for images (Midjourney, Flux, diffusion models). The deck focuses on text, but the architectural principles below transfer to image and audio generation mostly unchanged.

## The engine and its factory defects

> An LLM is a neural network (Transformer architecture) trained on trillions of words. It statistically predicts the next token from the preceding context; its "knowledge" is compressed into the parameters, the weights of the network.

The framing that matters for an architect: an LLM does not reason the way a person does, it is a very good statistical engine for continuation. That single fact explains both defects the slides call "difetti di fabbrica", and the deck is right to put them before any architecture, because everything that follows exists to mitigate them:

- **Hallucinations.** The model privileges syntactic plausibility over factual truth. When it does not know, it completes the sentence anyway, inventing facts, laws, or figures with total confidence. For an enterprise this is poison: the failure mode is not silence, it is a fluent wrong answer.
- **Knowledge cut-off.** Training ends on a specific date. Everything after it, and everything private (your products, your prices, a customer's account balance), simply does not exist for the model.

The two defects compound. A cut-off model asked about recent facts does not say "I don't know", it hallucinates. Which is why the slides' bottom line is blunt and correct: a naked LLM is unreliable for enterprise use. The architectures below are the mitigation.

## The architect's two forks

Building a GenAI solution means answering two strategic questions before writing any code:

```
  Q1  Infrastructure: where does the model live?
        API (SaaS)  vs  Self-hosted (open source)
        trade-off: privacy & control  vs  convenience & raw power

  Q2  Knowledge: how does it learn my data?
        Fine-tuning (implicit memory)  vs  RAG (explicit memory)
        trade-off: adaptation to style  vs  precision on facts
```

This is note 06's build-vs-reuse decision reappearing at the LLM layer: Q1 is "whose infrastructure", Q2 is "whose knowledge, injected how". The two axes are independent; a self-hosted model with RAG and an API model with fine-tuning are both legitimate quadrants.

## Fork 1, hosting: API vs self-hosted

| Dimension | External API | Self-hosted |
|---|---|---|
| **Data privacy** | Data leaves the company | Data stays on-premise |
| **Cost** | Expensive at high volume | GPU infrastructure cost |
| **Maintenance** | Managed by the provider | Requires MLOps skills |
| **Performance** | SOTA models | Optimized (smaller) models |

The deck's verdict: **API for prototypes and generalist use cases, self-hosted for sensitive data and total control**. An API gets you started in five minutes with a frontier model; the price is that patents, health records, or client data transit a third party, which for many organisations is a non-starter regardless of contractual assurances. Self-hosting open weights (Llama, Mistral) buys total privacy and control and charges you in GPUs and operational competence. There is no a-priori right answer, only project requirements. The cost side of this trade-off (per-token pricing vs amortised infrastructure) is a FinOps question, picked up in note 11; the on-premise end of the spectrum shades into the edge-vs-cloud discussion of note 08.

## Fork 2a, knowledge via fine-tuning: LoRA

Full fine-tuning rewrites the whole model. **LoRA** (low-rank adaptation) does something far cheaper: instead of modifying the entire brain, it adds small adapters.

- **Freeze**: the original model is frozen, 99.9% of parameters untouched.
- **Inject**: very small matrices (the adapters) are inserted between the layers.
- **Train**: only the adapters are trained.

The payoff is concrete. Hours instead of weeks, far less VRAM (a single consumer GPU can do it), and modularity: one base model plus many LoRA files, one per task, each a few MB. The slides' enciclopedia metaphor is apt, you do not rewrite the encyclopedia, you attach post-its. Module 02 covered the fine-tuning spectrum in more depth; what this deck adds is the architectural role: fine-tuning is **implicit memory**, good at teaching the model how to sound and how to format, bad at keeping facts current, because every fact update means another training run.

## Fork 2b, knowledge via RAG

RAG teaches the model nothing. It hands the model the right information at question time:

```
  User question
       |
       v
  Retrieval ------> search the company store for relevant documents
       |
       v
  Augment --------> paste the retrieved documents into the prompt
       |
       v
  Generation -----> the LLM answers using only the supplied documents
```

The philosophical shift is the useful part: RAG turns the LLM from an oracle into an analyst. Why force the model to memorise a price list that changes weekly, when you can hand it the current list to read only when needed?

### Retrieval is the product: hybrid search

The success of RAG depends on retrieval quality, and the deck makes a point that matches hard-won experience: **RAG is not just a vector DB**.

- **Semantic search (vectors/embeddings)**: understands meaning, finds similar concepts ("documents about heating problems"). Imprecise on exact identifiers.
- **Lexical search (BM25 keywords)**: matches exact strings. Infallible on SKUs, names, error codes ("error 504").
- **Best practice, hybrid search**: combine vectors + keywords + **reranking** for maximum precision.

Having built exactly this stack in the module 02 capstone (ChromaDB for the dense side, BM25 for the lexical side, a reranking pass to merge), the slide is understated if anything. Pure vector retrieval fails embarrassingly on the queries users care most about, the ones containing a product code or a policy number, because embeddings smear exact tokens into fuzzy semantic space. BM25 costs almost nothing and catches precisely those. The reranker then earns its latency by fixing the ordering neither retriever gets right alone. The module 08 hands-on rebuilds this: exercise 03_mini_rag_with_python, hybrid RAG with BM25 + ChromaDB against a local model in LM Studio.

### Why RAG dominates in the enterprise

- **Hallucination mitigation**: the model is constrained to the supplied documents, and can cite sources, which is what buys user trust.
- **Live knowledge**: update the document in the store and the system knows it immediately; no retraining. This kills the cut-off problem at its root.
- **Access control (ACL)**: retrieval can filter out documents the requesting user is not allowed to see before they ever reach the LLM.
- **Efficiency**: the model only needs to comprehend and synthesise, not memorise, so smaller and cheaper models suffice.

The ACL point deserves a security reading the slide only implies: the filter sits **before** the LLM, and that placement is the whole control. Once text is in the context window, no prompt instruction reliably prevents it leaking into an answer; the only robust place to enforce permissions is the retrieval layer. The catch on the trust side, and it is a real one: "constrained to the documents" is an instruction, not a guarantee. RAG shifts the failure mode from inventing facts to misreading or over-trusting retrieved ones, so retrieval quality and grounding checks remain part of the architecture, not an afterthought.

The recap slide compresses the fork into a rule worth memorising: **RAG for facts and company knowledge (the "what"), fine-tuning for style and format (the "how")**. The corollary, mine but safe: the two compose, and a LoRA-tuned model for tone fed by RAG for facts is a common production shape.

## Composing the blocks

### Multi-model and router

One frontier model for everything is the Nobel-laureate-making-coffee anti-pattern: expensive and inefficient. A modern architecture orchestrates a pyramid of models by task complexity:

```
        +------------------+
        |   SOTA models    |  reasoning, creative writing, strategic
        +------------------+  analysis: high intelligence, slow, costly
      +----------------------+
      | Specialized models   |  vertical, domain-specific tasks
      +----------------------+
    +--------------------------+
    |  Light & fast models     |  routing, classification, simple
    +--------------------------+  extraction: minimal latency and cost
```

A small, fast model acts as the **router**: it triages incoming requests and handles the trivial ones; frontier models are called only when genuine reasoning is required. The slides call this **cascading** and claim up to a 90% inference cost reduction with quality preserved where it matters. The claim is plausible precisely because request distributions are skewed: most traffic is classification and extraction dressed up as conversation. This is also the main FinOps lever for LLM systems, revisited in note 11.

### Workflows vs agents

The deck closes on a distinction that enterprise work makes critical, and that module 03 explored hands-on:

```
  AI workflow (deterministic pipeline):
    Input -> Task A (Python) -> Task B (LLM) -> Task C (SQL) -> Output

  AI agent (probabilistic loop, ReAct):
    Goal -> [ Thought -> Tool choice -> Action -> Observation ] x N -> Output
```

In a **workflow** the path is hard-coded by the architect; the LLM is just one node in the chain, used only where semantic intelligence is needed. Total control, easy testing and debugging, AI spent only on what traditional code cannot do. In an **agent** the LLM is the brain: it decides the steps, picks the tools, loops until done. Extreme flexibility for open-ended tasks, paid for in predictability, variable cost, and the risk of infinite loops. The train-vs-taxi metaphor from the slides is the right intuition: rails you laid vs a driver choosing the route.

The architect's advice from the deck, seconded without reservation after building both shapes in module 03: **start with a workflow, escalate to an agent only when the workflow's rigidity actually fails the use case**. Most "we need an agent" requirements are a three-step pipeline in disguise, and the pipeline version is the one you can test, bound in cost, and defend in a review. The governance and security implications of giving an LLM decision authority are exactly the note 10 material.

## Gotchas

- **Shipping a naked LLM.** Hallucinations plus cut-off make an unmitigated model unfit for enterprise use. Every production design carries at least one mitigation, usually RAG.
- **"RAG = vector database."** Reductive and costly. Semantic search alone fumbles exact codes and identifiers; hybrid search with BM25 and reranking is the professional baseline, not an optimisation.
- **Fine-tuning to inject facts.** Wrong tool: facts go stale and every update is a training run. Fine-tune for the "how" (style, format), RAG for the "what". LoRA makes the tuning cheap, not the fact-maintenance.
- **Enforcing permissions in the prompt.** ACL belongs in the retrieval layer, before the context window. Anything the LLM has already read must be assumed leakable.
- **One SOTA model for all traffic.** Cost and latency scale with the worst case. Route with a light model, cascade upward only on demonstrated need.
- **Reaching for agents first.** An agent is a probabilistic loop with variable cost and loop risk. If the steps can be enumerated in advance, it is a workflow; build that.

## See also

- [05_ai_model_lifecycle_pipeline.md](05_ai_model_lifecycle_pipeline.md) - the training and deployment pipeline that fine-tuning plugs into
- [06_pretrained_vs_custom_models_and_model_registry.md](06_pretrained_vs_custom_models_and_model_registry.md) - build vs reuse, the general decision this note's hosting fork specialises
- [08_edge_ai_vs_cloud_ai_and_cross_industry_architectures.md](08_edge_ai_vs_cloud_ai_and_cross_industry_architectures.md) - where self-hosting shades into edge deployment
- [10_enterprise_ready_architectures_and_governance.md](10_enterprise_ready_architectures_and_governance.md) - governance and security of systems where an LLM holds decision authority
- [11_compliance_auditing_and_finops.md](11_compliance_auditing_and_finops.md) - FinOps; model routing and cascading as the main LLM cost lever
- Module 08 exercise 03_mini_rag_with_python - the hands-on for this note: hybrid RAG with BM25 + ChromaDB + LM Studio
- Module 02 notes and `_PRJ_rag_system_for_company_knowledge` - the full hybrid RAG implementation this note's retrieval section draws on; module 03 notes for agent patterns (ReAct, orchestration) in depth
