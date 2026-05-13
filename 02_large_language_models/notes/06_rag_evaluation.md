# RAG Evaluation: Metrics and Frameworks

## TL;DR

A fluent answer is not a correct answer. An LLM in a RAG pipeline can answer "from memory" while ignoring the retrieved chunks, synthesise convincingly from the wrong chunks, or get the right answer by accident. Without a metrics framework, you cannot tell which of these is happening, and you cannot tell whether your last change improved the system or made it worse. **RAG evaluation** decomposes the pipeline into the **RAG Triad** (query - context - answer) and measures the three interactions: how well the retrieval matches the query (**context precision / recall**), how well the answer matches the retrieved evidence (**faithfulness**), how well the answer matches the user's intent (**answer relevancy**). The dominant Python frameworks are **RAGAS** and **DeepEval**, both of which use an LLM as judge: the metric is computed by asking another LLM to score the relationship. The mechanism is non-deterministic and expensive (N LLM calls per evaluation), but it is the only way to evaluate at scale without building a hand-labelled gold set. The single most important rule is **change one component at a time**: vary chunking, then embedder, then top-K, then reranker, on the same test set, so each score delta is attributable. In production the evaluation moves from one-off runs to **continuous monitoring**: a background pipeline scores a sample of real queries, dashboards show drift, alerts fire when a metric drops.

## Cheatsheet

| Concept | One-line | Diagnoses |
|---|---|---|
| **RAG Triad** | Query - Context - Answer; measure all three interactions | Where the bottleneck lives |
| **Faithfulness** | Is the answer supported by the retrieved chunks? | LLM hallucinating beyond context |
| **Answer relevancy** | Does the answer address the query? | LLM going off-topic |
| **Context precision** | Are the top-K chunks ranked usefully? | Retriever brings noise high up |
| **Context recall** | Did the retriever find all relevant chunks? | Retriever misses information |
| **RAGAS** | Python framework, LLM-as-judge, 4 core metrics | Standard for offline evaluation |
| **DeepEval** | Pytest-integrated; same core metrics + hallucination/toxicity/bias | Standard for CI/CD |
| **Aggregated score** | Combine metrics into one number | Production-readiness signal |
| **LLM judge** | Use another LLM to score the pipeline's output | Cheap proxy for human evaluation |

---

## Why evaluation matters in RAG

A pipeline can fail in three subtly different ways that produce the same observable symptom (a wrong answer):

| Failure | Where | Why classical metrics miss it |
|---|---|---|
| **Retrieval failure** | Wrong chunks returned | A fluent answer can still be produced from wrong chunks |
| **Generation failure** | Right chunks, LLM ignores them | Output is fluent and confident |
| **Both** | Wrong chunks + LLM fills in from training data | The answer reads like the right one |

Without per-component metrics you cannot tell these apart. Without telling them apart you cannot fix the right thing.

---

## The RAG Triad

A conceptual framework that decomposes the pipeline into the three interactions and measures each.

```
            ┌────────────────┐
            │     QUERY      │
            └────────────────┘
              ╱            ╲
             ╱              ╲
  Context Precision     Answer Relevancy
  Context Recall              ╲
            ╱                  ╲
           ▼                    ▼
   ┌──────────────┐    ┌──────────────┐
   │   CONTEXT    │───►│    ANSWER    │
   │  (retrieved  │    │ (generated  │
   │   chunks)    │    │   by LLM)    │
   └──────────────┘    └──────────────┘
            │   Faithfulness   │
            └──────────────────┘
```

| Edge | Metric | Question it answers |
|---|---|---|
| Query ↔ Context | Context precision / recall | Did retrieval find the right chunks? |
| Context ↔ Answer | Faithfulness | Did the LLM stick to the retrieved evidence? |
| Query ↔ Answer | Answer relevancy | Did the LLM actually address the question? |

Reading a low score on one specific edge tells you exactly which component to fix.

---

## Faithfulness: did the LLM stay grounded?

**Faithfulness** measures whether every claim in the generated answer is supported by the retrieved chunks. Low faithfulness means the LLM is hallucinating - adding facts that the context does not justify.

### How it is computed

A three-step process:

1. **Decompose the answer.** An LLM extracts individual atomic claims (propositions) from the response.
2. **Verify each claim.** For each claim, an LLM asks: "is this claim supported by the retrieved chunks?". The output is a binary yes / no.
3. **Score.** The metric is the ratio of supported claims to total claims.

```
Answer: "The Eiffel Tower is 330 metres tall and was built in 1889 by Gustave Eiffel."

Decomposition:
  - "The Eiffel Tower is 330 metres tall."
  - "The Eiffel Tower was built in 1889."
  - "The Eiffel Tower was built by Gustave Eiffel."

For each claim, check against the retrieved chunks:
  - 330 metres: SUPPORTED (chunk mentions 330 m)
  - 1889: SUPPORTED (chunk mentions 1889)
  - Gustave Eiffel: SUPPORTED (chunk mentions Eiffel)

Faithfulness = 3 / 3 = 1.0
```

### What a low faithfulness tells you

| Pattern | Likely cause | Fix |
|---|---|---|
| Many unsupported claims | Model ignores the context, falls back on parametric knowledge | Sharpen the augmentation prompt ("answer ONLY from the documents") |
| Mostly supported, one fabricated claim | Specific fact missing from retrieval | Improve retrieval (more chunks, hybrid search, reranking) |
| All claims technically in context but reinterpreted | Model over-paraphrases | Constrain output format; require citation |

### Robustness

The metric itself is non-deterministic (the judging LLM gives different scores across runs). Two practical mitigations:

- **Ensemble averaging**: run the judge N times, average the scores.
- **Cross-model validation**: judge with two different LLMs and confirm agreement.

Both are expensive; use them on the cases where the score is borderline.

---

## Answer relevancy: did the answer address the question?

**Answer relevancy** measures how well the answer matches the user's intent, independent of whether the facts are correct.

### How it is computed

The technique is **reverse engineering by semantic similarity**:

1. **Generate candidate questions from the answer.** An LLM generates N plausible questions that the answer would naturally address.
2. **Embed all questions.** The original query and each generated question are embedded.
3. **Compute mean cosine similarity** between the original query and the generated questions.

```
Original query:    "What is the capital of France?"
Answer:            "Paris is the capital of France, a city of about 2.1 million people."

Generated questions from the answer:
  1. "What is the capital of France?"
  2. "What is the population of Paris?"
  3. "Where is Paris?"

Embed all 4. Cosine similarity:
  q ↔ gen_1: 0.97  (almost identical)
  q ↔ gen_2: 0.41  (off-topic)
  q ↔ gen_3: 0.65  (related but different)

Answer relevancy = mean = 0.68
```

A high score means the answer's content closely matches what the original query would naturally ask. A low score means the answer drifted from the question - either it answered a different question, or it produced too much off-topic content.

### What a low answer relevancy tells you

| Pattern | Likely cause | Fix |
|---|---|---|
| Answer is verbose with off-topic content | LLM over-explains | Constrain length and focus in the prompt |
| Answer addresses a related but different question | LLM misinterprets the query | Query expansion or step-back retrieval |
| Answer is short and concise but seems unrelated | Retrieval found irrelevant context, model hedged | Improve retrieval; relevant context guides on-topic answers |

### Production-friendliness

Answer relevancy is **reference-free**: it does not need a gold answer to compare against. This makes it cheap to run on production traffic - sample real queries, score their responses, no labelling needed. Faithfulness is also reference-free in the same sense; context recall is the one metric that does need a gold standard.

---

## Context precision: was retrieval ranked well?

**Context precision** measures whether the most relevant retrieved chunks are at the top of the ranking. Two top-K chunks of which only the second is relevant scores worse than the same two chunks reordered.

### How it is computed

Standard form is **precision@K with positional weighting**:

```
context_precision = Σ_{k=1..K} (precision@k × relevance(k)) / total_relevant_in_top_K
```

`precision@k` is the fraction of relevant chunks in the top `k`; `relevance(k)` is 1 if chunk `k` is relevant, 0 otherwise. Relevance is judged by an LLM (or by ground-truth labels if available).

The effect: a relevant chunk at position 1 contributes more than the same chunk at position 5.

### Three variants

The framework offers three implementations of context precision that trade accuracy for cost:

| Variant | Mechanism | Cost | Use |
|---|---|---|---|
| **LLM-based, with ground truth** | LLM compares each chunk to the expected answer | High | Best accuracy; needs a gold answer |
| **LLM-based, without ground truth** | LLM compares each chunk to the query and the generated answer | High | Production-friendly |
| **Traditional metric** (BLEU, cosine) | No LLM; lexical / semantic similarity only | Low | Cheap baseline |

The recommendation: use the LLM-based variants for offline evaluation; consider the traditional variant for high-frequency monitoring where cost matters.

### What a low context precision tells you

| Pattern | Likely cause | Fix |
|---|---|---|
| Relevant chunks present but ranked low | Embedder picks wrong | Reranking with cross-encoder |
| Relevant chunks scattered with noise | Naive top-K returns too many noisy candidates | Better filtering, smaller K, reranking |
| Different chunks rank top each time | Embedding model unstable | Switch embedder; consistency matters |

---

## Context recall: did retrieval find everything?

**Context recall** measures the fraction of relevant chunks (in the entire corpus) that the retrieval brought into the top-K. Unlike the other three metrics, it **requires a ground truth** - you need to know which chunks should have been retrieved.

### How it is computed

```
context_recall = (relevant chunks in top-K) / (all relevant chunks in the corpus)
```

The denominator is the cost: you need either an exhaustive gold-labelled corpus or sampled annotations. RAGAS computes this approximately by checking whether each fact in the **ground-truth answer** is supported by some chunk in the top-K. The metric is then "fraction of ground-truth facts that retrieval covered".

### What a low context recall tells you

The retriever does not find what is needed. Fixes are at the retrieval side:

| Pattern | Fix |
|---|---|
| Specific facts missing | Increase top-K |
| Specific terms missing | Hybrid search (BM25) |
| Specific phrasings missing | Query expansion (multi-query, HyDE) |
| Whole topic missing | Re-index; check that the corpus actually covers the topic |

### Why this metric is expensive

Both LLM-as-judge and ground-truth labels cost. RAGAS uses the ground-truth answer as a proxy for the labels, which works if the ground-truth answer is well-constructed but not otherwise. DeepEval has similar trade-offs.

---

## RAGAS in code

The Python interface, condensed:

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)

results = evaluate(
    dataset=test_dataset,           # list of {question, contexts, answer, ground_truth}
    metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
)

print(results)
# {"faithfulness": 0.87, "answer_relevancy": 0.92, ...}
```

The `test_dataset` is the work. Each entry has:

- `question`: the user query.
- `contexts`: the chunks the retrieval returned.
- `answer`: what the LLM produced.
- `ground_truth`: the expected answer (needed for context_recall).

Building 50-200 such entries is the actual cost of starting an evaluation discipline. RAGAS can semi-automate it by generating synthetic questions from a corpus, but the gold answers still need human review.

---

## DeepEval: the CI/CD-friendly alternative

DeepEval is the alternative most widely used in production. Same core metrics as RAGAS plus:

- **Hallucination**, **Toxicity**, **Bias** as standalone metrics.
- **Pytest integration**: RAG tests become unit tests in CI.
- **Dashboard**: web UI for tracking metric drift over time.

A DeepEval test in pytest:

```python
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric

def test_faq_answer():
    metric = AnswerRelevancyMetric(threshold=0.7)
    assert_test(test_case, [metric])
```

A failed test means a metric dropped below threshold; CI surfaces it like any other regression.

When to pick which:

| Use RAGAS | Use DeepEval |
|---|---|
| Offline evaluation, research | Continuous evaluation in CI/CD |
| Quick comparison across variants | Long-running production system |
| Lightweight pytest integration not needed | Want test results in CI summaries |
| Mostly working in notebooks | Mostly working in services |

---

## Aggregated scores

Reporting four numbers is informative but hard to track over time. A single **aggregated score** is useful for dashboards and regression alerts.

Three common aggregation methods:

| Method | Formula | Behaviour |
|---|---|---|
| **Arithmetic mean** | `(A + B + C + D) / 4` | All metrics equally important; one weak metric pulls down evenly |
| **Weighted mean** | `Σ wᵢ · metricᵢ` with custom weights | Specific metrics get prioritised |
| **Harmonic mean** | `4 / (1/A + 1/B + 1/C + 1/D)` | Strongly penalises any single low metric |

The **harmonic mean** is the right default for RAG: a pipeline that scores 0.9 on three metrics and 0.1 on the fourth should not look "average". Harmonic mean reflects the bottleneck.

A score above 0.8 (combined, harmonic) is a rough threshold for production-readiness. Continuous monitoring after deployment catches drift below the threshold early.

---

## The optimisation loop

The single most important rule:

> **Change one component at a time.**

The full workflow:

```
1. Build test set (~50 Q/A pairs covering different intents and document types).
2. Baseline: run RAGAS / DeepEval on the current pipeline. Record all four metrics.
3. Diagnose: which metric is lowest? That points at the bottleneck component.
4. Change one component (chunking, embedder, top-K, reranker, prompt, ...).
5. Re-evaluate: did the targeted metric improve? Did others get worse?
6. Repeat.
```

The point of changing one at a time is that the score delta is attributable. Change two components and you cannot tell which one mattered.

### Diagnostic patterns

| Low metric | Likely component | What to try |
|---|---|---|
| Context recall | Retriever | Hybrid search, query expansion, larger top-K |
| Context precision | Retriever ranking | Reranking, smaller top-K with better quality |
| Faithfulness | Generator + prompt | Sharper augmentation prompt; fewer / better chunks |
| Answer relevancy | Generator + prompt | Constrain length; clearer task instruction |
| All four low | Foundational issue | Re-check chunking; ensure embedder matches the domain |

### Test set design

Good test questions:

- Have a **unique, verifiable answer** in the corpus.
- Cover **different parts** of the corpus (not just the first pages).
- Include questions the pipeline **should not** answer (to test the fallback clause).

Bad test questions:

- Ambiguous or opinion-based.
- Too generic ("What is this document about?").
- Multi-step reasoning beyond what RAG is designed to do.

Build at least 50 questions to start; expand to 200+ for production. Synthetic generation (via an LLM) can bootstrap the set, but human review is needed before you trust the gold answers.

---

## Moving to production: continuous evaluation

In development, evaluation is episodic: you run RAGAS after every change. In production, it becomes **continuous**:

| Aspect | Development | Production |
|---|---|---|
| Frequency | After each change | Continuously, on real traffic |
| Sample | Full test set | Sampled subset of live queries |
| Storage | Notebook output | Time-series DB (Datadog, Grafana) |
| Alerts | None | Slack / PagerDuty on threshold breach |
| Action | Tune the pipeline | Trigger an investigation |

### Architectural notes

- **Decouple evaluation from the main pipeline.** The LLM judge does not live on the critical path. Compute metrics asynchronously on logged interactions.
- **Cache aggressively.** Faithfulness decompositions are expensive; cache the claim extraction.
- **Batch evaluations.** Score in batches of N to amortise LLM call setup overhead.
- **Ensemble for production.** Use 2-3 different LLM judges for the metrics; their consensus is more reliable than a single judge.
- **Calibrate against humans periodically.** Sample N production interactions, get human ratings, check the automatic metric correlates with human judgment.

### Compliance angle

LLM judges may introduce **bias** into the scoring. Audit periodically: do the metrics produce systematically different scores across user demographics, languages, or topics? If yes, the judging LLM is the cause and needs to be swapped.

Long-term retention of evaluation data also matters for compliance. GDPR-style audit trails on what was evaluated, by whom, and what score was assigned can be required in regulated industries.

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Reporting fluent answers as the success metric | Confident hallucinations slip through | Faithfulness is the right metric |
| Hand-grading a test set once and never updating it | Test set drifts from production; alerts stop reflecting reality | Refresh the test set quarterly |
| Using the same LLM as generator and judge | Confirmation bias: the judge accepts its own outputs | Different judge model |
| Reporting an average score without per-metric breakdown | Loss of diagnostic value | Always report all four |
| Changing chunker AND embedder AND reranker in one experiment | No attribution; gain or loss could come from any | One change at a time |
| Trusting LLM-as-judge as ground truth | The judge can be wrong | Calibrate against humans periodically |
| Optimising one metric to the detriment of others | One number goes up, the others quietly drop | Track the harmonic mean |
| Evaluation runs in the request hot path | Latency suffers | Decouple: log → async eval |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Quick offline test of a pipeline | RAGAS in a notebook | Smallest viable evaluation |
| CI/CD-integrated tests | DeepEval with pytest | Fails the build on regression |
| One bottleneck unclear | All four RAG Triad metrics | The lowest one points at the fix |
| Hallucination is the suspected issue | Faithfulness | Direct measurement |
| Retrieval is the suspected issue | Context precision + recall | Pinpoints retrieval problems |
| Production monitoring | Decoupled async pipeline | Real-time without latency hit |
| Vendor-agnostic, ML-flexible | RAGAS | Pluggable with any LLM/embedder |
| Enterprise governance | DeepEval + dashboards + alerts | Built for the operational shape |

---

## See also

### Other notes
- [04_rag_fundamentals.md](04_rag_fundamentals.md) — the pipeline these metrics evaluate
- [05_advanced_rag.md](05_advanced_rag.md) — the upgrades a low metric tells you to add
- [07_rag_production.md](07_rag_production.md) — caching, monitoring, scaling
- [08_ethics_and_governance.md](08_ethics_and_governance.md) — bias in LLM judges, audit requirements
- Module 03 [06_long_term_memory.md](../../03_agentic_ai/notes/06_long_term_memory.md) — RAGAS metrics also covered there from the agent-memory angle

### Related work in this repo
- Module 02 capstone (`PRJ_sistema_rag_conoscenza_aziendale.py`) — confidence score from top-K similarity used as a proxy faithfulness signal
- Module 03 exercise 06 — the structured-extraction iteration story is a small evaluation loop in miniature: each fix was driven by a specific failure mode in the verify node's behaviour
