# LLM Foundations: from Corpora to Transformers

## TL;DR

Large Language Models are not magic; they are the convergence of three older ideas: a **statistical view of language** (frequency counts on big text collections), a **distributional theory of meaning** (words occurring in similar contexts have similar meanings, Harris, 1954), and **dense vector representations** (each word is a point in a high-dimensional space). The architectural breakthrough is the **Transformer** (Vaswani et al., 2017) with its **self-attention** mechanism: each token's representation is computed as a weighted sum over all other tokens in the context, where the weights come from query / key / value projections of the embeddings themselves. Three model families fall out of this architecture by reusing parts of it: **encoders** (BERT family) trained with masked-language-modelling, good at understanding tasks (classification, NER, similarity); **decoders** (GPT family) trained with next-token prediction and masked self-attention, good at generation; **encoder-decoders** (T5 family) for sequence-to-sequence. The "Large" in LLM refers to the parameter count, which ranges from BERT's 110M to LLaMa 3.1's 405B. The cost story is the same shape across families: training is expensive (rented compute, weeks to months on data centers), inference is comparatively cheap. Tokenization sits before everything: subword tokenizers (Byte-Pair Encoding, WordPiece) learn the vocabulary from the corpus rather than relying on rules, which is the only way to scale to billions of tokens and dozens of languages.

## Cheatsheet

| Concept | One-line | Where it shows up |
|---|---|---|
| **Corpus** | A dataset of text used as raw material for linguistics or training | Foundation of every LM |
| **Distributional hypothesis** | Words in similar contexts have similar meanings | Underlies every embedding method |
| **Zipf's law** | A few words are very common, most are very rare | Why models need huge corpora |
| **Tokenizer** | Splits text into atomic units | First thing every LLM does to its input |
| **Byte-Pair Encoding (BPE)** | Bottom-up subword tokenizer, frequency-driven | GPT, Llama family |
| **WordPiece** | Bottom-up subword tokenizer, likelihood-driven | BERT family |
| **N-gram** | Sequence of N tokens; LM = product of conditional probabilities | Pre-neural LMs |
| **Word embedding** | Dense vector for each word capturing context | Foundation of every neural LM |
| **Word2Vec** | Skip-Gram / CBOW; predicts context from word or vice versa | First widely-used embedding model |
| **Transformer** | Attention-based architecture | "Attention is all you need" (2017) |
| **Self-attention (Q/K/V)** | Each token attends to all others, weighted by query-key affinity | The core operation |
| **Encoder (BERT)** | Bidirectional, masked language modelling, understanding tasks | NER, classification, similarity |
| **Decoder (GPT)** | Autoregressive, masked self-attention, generation | Text completion, chat |
| **Encoder-Decoder (T5)** | Both stacks, sequence-to-sequence | Translation, summarisation |

---

## The distributional view of language

Before any neural network, the idea behind LLMs comes from linguistics. The discipline that studies language with empirical data on large text collections is **corpus linguistics**: it asks what we can learn about a language by counting how words appear in texts, rather than by writing down rules.

### Four practical questions about corpora

A corpus is a collection of texts. To use one for a language model you need to know:

| Dimension | Examples |
|---|---|
| **Genre** | General-language (newspaper, web) vs specialist (medical, legal) |
| **Modality** | Written vs spoken |
| **Language** | Monolingual vs multilingual |
| **Time scale** | Synchronic (single time slice) vs diachronic (across time) |

The choice matters: a model trained on parliamentary transcripts will know parliamentary register; a model trained on Reddit will know internet register. Neither generalises to the other for free.

### Zipf's law and data sparsity

In any natural-language corpus, a few words are extremely frequent ("the", "of", "is") and most words are extremely rare. The frequency is inversely proportional to the rank.

Two consequences for a language model:

- The model sees common words millions of times and learns them well.
- The model sees rare words a handful of times - sometimes once, often never - and has to either generalise from similar words or fail on them.

This is *the* reason language models need ridiculously large corpora: not because the common words are hard to learn but because the long tail of rare words requires that you observe them at all.

### Grammar is not enough

Chomsky's hierarchy gives four formal grammar classes. Natural languages mix Type 2 (context-free, like *"the rider rides the horse"*) and Type 1 (context-sensitive, like *"the riders ride the horses"* with agreement). Even if you could enumerate every grammar rule, the **semantic** problem would remain:

- *"The horses ride the riders"* is grammatically correct but semantically wrong.
- *"Colorless green ideas sleep furiously"* (Chomsky's example) is grammatically well-formed and meaningless.

A purely syntactic model cannot distinguish these. Something else is needed.

### The distributional hypothesis

Zellig Harris, in the 1950s, observed that **words with similar meaning occur in similar contexts**. He formulated the conjecture that the degree of semantic similarity between two linguistic expressions is a function of the similarity of the linguistic contexts in which they can appear.

This is the single most important idea behind every modern language model. Meaning is operationalised as *distribution in context*. Two words that appear in the same neighborhoods of words are claimed to be similar.

All neural language modeling is, at heart, a way to make this claim computational.

---

## Tokenization

Before a model can do anything with text, the text has to be split into atomic units. The naive choice is "a word is a unit"; the practical choice for LLMs is something smaller.

### Two families

**Top-down (rule-based) tokenizers** decide a priori how words are formed and split. They use regular expressions and hand-written rules. Useful for narrow domains where the vocabulary is predictable; impractical for general LLM training because real text is too messy.

**Bottom-up (data-driven) tokenizers** learn the vocabulary directly from a corpus. The same algorithm produces tokens for English, Italian, code, emoji, and URLs without any rule-writing.

### Byte-Pair Encoding (BPE)

The dominant subword tokenizer (GPT, LLaMa, Mistral). The algorithm:

1. Start with each character as a token.
2. Find the most frequent adjacent pair of tokens.
3. Merge it into a new token.
4. Repeat until the vocabulary reaches the target size.

Output for the word "mangiare" might be `["mang", "i", "are"]`. The tokenizer is **fully deterministic**: same input, same split.

### WordPiece

BERT's tokenizer. Similar idea to BPE but the merge criterion is **likelihood under a language model** rather than raw frequency. The output marks subword continuation with `##`:

- `"mangiare"` → `["mang", "##iare"]`
- `"mangiatori"` → `["mang", "##iatori"]`

### Why subwords matter

Word-level tokenizers fail catastrophically on rare or out-of-vocabulary words. Subword tokenizers handle them gracefully: an unknown word is split into known pieces. This is what lets a single tokenizer cover dozens of languages, code, math, and emoji without explicit configuration.

### A practical consequence

The token count is the unit you pay in (cost) and wait on (latency). One English word averages ~1.3 tokens with GPT-4's tokenizer; Italian averages ~1.7; code averages 2-3; non-Latin scripts can be 3-5. The exact ratio matters when you are budgeting context-window usage.

---

## Statistical models: n-grams

Before neural networks, the simplest probabilistic language model was the **n-gram**: estimate the probability of the next token given the last `n-1`.

The full formula relies on the **Markov assumption**: the probability of a word depends only on the immediate previous context, not on the full history.

```
P(w_t | w_1, ..., w_{t-1}) ≈ P(w_t | w_{t-n+1}, ..., w_{t-1})
```

### Worked example: bigrams

Two sentences:

1. *"The cat Matisse sleeps"*
2. *"The cat Matisse eats"*

Bigrams: `("The", "cat")`, `("cat", "Matisse")`, `("Matisse", "sleeps")`, `("Matisse", "eats")`. To predict the word after "Matisse" the model picks one of `{"sleeps", "eats"}` with the frequencies it observed.

### Why n-grams break

Two structural problems:

- **Parameter explosion.** Adding one to `n` multiplies the parameter count by the vocabulary size. Trigrams over a 50k-vocab need 1.25 × 10¹⁴ parameters in principle, almost all of them unobserved.
- **No generalisation.** An n-gram model knows what it has seen and *nothing else*. It cannot learn that "feline" and "cat" are related; if "feline" never appears in the corpus, the model has no representation for it.

Neural networks fix both problems by learning a continuous, low-dimensional representation of each word.

---

## From symbols to vectors

A computer eventually needs a numerical representation of each token. Two strategies, vastly different in usefulness.

### Sparse: one-hot encoding

Each word is a vector with one `1` in the position of that word and zeros everywhere else.

```
"cat"   →  [0, 0, 1, 0, 0, ..., 0]    # vocab-size dimensions
"feline"→  [0, 1, 0, 0, 0, ..., 0]
```

Two fatal problems:

- **Dimensionality.** The vector length is the vocabulary size. For a 100k-word vocabulary, every word is a 100k-dim vector mostly of zeros.
- **No generalisation.** "cat" and "feline" are orthogonal: as far as the geometry knows, they are as different as "cat" and "Monday".

### Dense: word embeddings

Each word is a 100-300 dimensional vector of real numbers, *learned* from a corpus so that words appearing in similar contexts end up close in the embedding space.

```
"cat"    →  [0.21, -0.45, 0.78, ...]   # ~300 dimensions
"feline" →  [0.19, -0.43, 0.81, ...]   # very similar
"banana" →  [0.61, 0.32, -0.55, ...]   # very different
```

Three advantages:

- **Low dimensionality.** Cheap to store, fast to compute distances on.
- **Geometric similarity** that matches semantic similarity.
- **Compositional structure**: the famous `vec("king") - vec("man") + vec("woman") ≈ vec("queen")`.

### Word2Vec

The model that put word embeddings on the map. A shallow feed-forward neural network with one hidden layer, trained to predict context from a word (Skip-Gram) or word from context (CBOW). The hidden-layer activations *are* the embeddings.

| Variant | Input | Output |
|---|---|---|
| **Skip-Gram** | One word | Predict the surrounding context |
| **CBOW** (continuous bag of words) | Context window | Predict the centre word |

Word2Vec embeddings were the first widely-used learned word representations. Every modern LLM still rests on this foundation; only the model that *produces* the embeddings has changed.

---

## The Transformer

The 2017 paper "Attention is all you need" replaced recurrent networks (LSTM, GRU) for sequence modelling with a single mechanism: **self-attention**. The Transformer is the architecture under every modern LLM.

### Self-attention: Q, K, V

For every token, the model computes three projections of its embedding:

- **Query (Q)**: what this token is looking for
- **Key (K)**: what each token contains
- **Value (V)**: the information each token contributes

The attention weights are the affinity between each query and each key: `Q @ K.T`. The output is a weighted sum of the values, where the weights are those affinities (after softmax).

```
output(token_i) = Σ_j softmax(Q_i · K_j / √d) · V_j
```

### Worked example

Sentence: *"The cat chases the mouse."* Consider the token "cat".

| Other token | What it contributes (Value) | How relevant to "cat" (Q · K) |
|---|---|---|
| "The" | Article signalling subject | Low-medium |
| "chases" | Action the cat performs | High |
| "the" (second) | Article for object | Low |
| "mouse" | What is being chased | High |

The output for "cat" mixes information from "chases" and "mouse" heavily, from "The" and "the" weakly. The mechanism captures **what each word is about in its specific sentence**, not just the average meaning of the word in general.

### Multi-head attention

A single Q/K/V projection captures one notion of relevance. Multi-head attention runs `H` independent attention computations in parallel (each with its own Q, K, V projections), then concatenates the results. Different heads end up specialising on different relations (subject-verb agreement, coreference, distant dependencies).

### Self-attention vs masked self-attention

| Variant | Behaviour | Used by |
|---|---|---|
| **Self-attention** | Each token attends to all tokens (past and future) | Encoders (BERT) |
| **Masked self-attention** | Each token attends only to previous tokens | Decoders (GPT) |

The masking is what makes a decoder *autoregressive*: when generating token N, it can use tokens 1..N-1 but not N+1..end. This matches the generation setting at inference time, where future tokens do not yet exist.

---

## Three architectures, three uses

The Transformer paper introduced an encoder-decoder model. Subsequent work showed that either half is independently useful, giving three families.

### Encoder-only: BERT family

**Bidirectional Encoder Representations from Transformers.** Trained on two objectives:

- **Masked Language Modelling (MLM).** Mask 15% of the tokens with `[MASK]`; train the model to predict them using full bidirectional context.
- **Next Sentence Prediction (NSP).** Given two sentences, decide if the second follows the first.

```
input:  "The cat [MASK] the mouse."
target: "chases"
```

The training objective forces the model to *understand* each token's context, including the right side. Fine-tuning the model on a downstream task (NER, classification, similarity) is then a small step.

**Use cases**: Named Entity Recognition, sentence classification, sentence similarity. Not generation - BERT can predict masked tokens but does not produce coherent long outputs.

**Variants**:

| Model | Trade-off |
|---|---|
| **BERT** | The original; 110M (Base) or 340M (Large) parameters |
| **RoBERTa** | More data, longer sequences, no NSP; more robust |
| **DistilBERT** | Knowledge distillation; ~97% of BERT's quality at 60% of the size |
| **ALBERT** | Weight sharing + factorised embeddings; much smaller for the same quality |

### Decoder-only: GPT family

**Generative Pre-trained Transformer.** Trained on one objective:

- **Next-token prediction.** Given a sequence `w_1, ..., w_t`, predict `w_{t+1}`.

```
input:  "The dog runs in the"
target: "park"  (one option among many)
```

The masked self-attention ensures the model only sees previous tokens during training, exactly matching the inference setting. The training objective produces a model that is fundamentally a *generator*: feed it a prompt, sample tokens until a stop condition.

**Use cases**: text completion, dialogue, code generation, anything generative.

**Variants** are essentially "more parameters + better data + RLHF":

| Family | Scale |
|---|---|
| TinyLlama | 1.1B params, ~600 MB |
| Gemma-2B | 2B, ~5 GB |
| Llama 3.1 8B | 8B, ~16 GB |
| Llama 3.1 70B | 70B, ~140 GB |
| Llama 3.1 405B | 405B, ~810 GB |

### Encoder-Decoder: T5 family

**Text-to-Text Transfer Transformer.** Reframes every task as a sequence-to-sequence problem:

```
translate English to French: "The house is wonderful"  →  "La maison est merveilleuse"
summarise: <long article>                              →  <short summary>
question: who wrote 1984?                              →  George Orwell
```

The encoder reads the input, the decoder produces the output, with attention from decoder to encoder bridging the two. T5 versions range from 60M (Small) to 11B (XXL) parameters.

**Use cases**: tasks with a clear input → output structure. Translation, summarisation, question answering. Less common today; decoder-only models with strong prompting reach similar quality on most of these tasks.

---

## What "Large" actually means

Three numbers fully describe a model's scale: **parameter count**, **training data size**, **training compute**.

### Parameters

The number of learnable weights. Sets the floor on memory consumption (FP16 weights take roughly 2 bytes per parameter).

| Model | Params | Storage |
|---|---|---|
| BERT Base | 110M | ~400 MB |
| BERT Large | 340M | ~1.2 GB |
| Gemma-2B | 2B | ~5 GB |
| Llama 3.1 8B | 8B | ~16 GB |
| Llama 3.1 70B | 70B | ~140 GB |
| Llama 3.1 405B | 405B | ~810 GB |

Quantisation (Int8, Int4, 1.58b) reduces these numbers by 2-8x at some quality cost.

### Training data

The volume of text used to train the model. Sources are typically web crawls, books, papers, code repositories, conversations.

| Model | Training text |
|---|---|
| GPT-3 | ~570 GB |
| T5 | ~750 GB |
| Llama 3 | ~15T tokens |

The growth curve has been steeper than parameter growth: state-of-the-art models now train on multi-trillion-token corpora.

### Training cost

A frontier-model training run today costs tens of millions of dollars in rented compute, runs for weeks to months, and emits non-trivial CO₂. Training and inference are fundamentally different cost regimes:

- **Training**: one-time, expensive.
- **Inference**: ongoing, comparatively cheap.

This asymmetry is what makes hosted APIs viable: pay a few dollars per million tokens at inference time, never pay the training cost directly.

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Word-level tokenizer on real text | Out-of-vocabulary errors on rare words | Use a subword tokenizer (BPE / WordPiece) |
| Token count assumed equal to word count | Cost / latency estimates are wrong by 30-50% | Tokenise sample inputs; budget against actual tokens |
| Encoder used for generation | BERT outputs token probabilities, not coherent text | Use a decoder-only or encoder-decoder model |
| Decoder used for sentence classification with no head | Generates a reply instead of a label | Either fine-tune with a classification head or use prompt engineering |
| Comparing models by parameter count alone | Wrong rankings | Match on training data and instruction-tuning too |
| Assuming attention captures all relations | Long-range dependencies past the context window are invisible | Use long-context models or external retrieval |
| One-hot encoding outside of toy problems | Memory explosion, no generalisation | Use dense embeddings |
| Training your own tokenizer for a small downstream task | Loses pretraining vocabulary alignment | Reuse the pretrained tokenizer; fine-tune if you must |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Sentence-level understanding (classification, NER, similarity) | **Encoder** (BERT, RoBERTa, DistilBERT) | Bidirectional context is exactly what these tasks need |
| Free-form generation (chat, completion, summarisation, code) | **Decoder** (GPT, Llama, Mistral) | Autoregressive training matches the inference loop |
| Sequence-to-sequence with a clear input-output mapping | **Encoder-decoder** (T5, BART) | Specialised for the shape; fewer prompt-engineering hacks |
| You want similarity between two pieces of text | Encoder + sentence-embedding model | Embeddings are the natural output |
| You have one model that should do many things | Decoder with strong prompting | Decoders generalise to non-generative tasks via prompting |
| Cheap, small, on-device | Small decoder (TinyLlama, Gemma 2B) or distilled encoder | Quantise to fit |
| Frontier quality | Frontier model via hosted API | Self-hosting 70B+ models needs serious infrastructure |

---

## See also

### Other notes
- [02_model_landscape.md](02_model_landscape.md) — closed vs open weights, modern model families
- [03_prompt_engineering.md](03_prompt_engineering.md) — extracting useful behaviour from decoder models
- [04_rag_fundamentals.md](04_rag_fundamentals.md) — using LLMs with external knowledge
- Module 03 [02_agent_components.md](../../03_agentic_ai/notes/02_agent_components.md) — LLMs as one of the five building blocks of an agent
- Module 03 [06_long_term_memory.md](../../03_agentic_ai/notes/06_long_term_memory.md) — embeddings as the foundation of vector search

### Related work in this repo
- Module 02 exercises 01-04 (text analysis, NER with BERT, LangChain prompt pipeline, RAG chatbot) — first practical contact with these foundations
- `01_machine_learning/notes/08_neural_networks.md` — the upstream context: from neural networks to deep learning to Transformers
