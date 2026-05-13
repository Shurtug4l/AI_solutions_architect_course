# Model Landscape: Training, Closed vs Open Weights

## TL;DR

Modern LLMs reach their quality through a **two-stage training**: **pre-training** (predict the next token on a huge corpus, learn grammar and world knowledge) and **fine-tuning** (adapt the model to follow instructions and respond helpfully). The instruction-tuning stage is increasingly done with **RLHF** (Reinforcement Learning from Human Feedback): humans rank multiple candidate responses, a reward model is trained on those preferences, and the LLM is optimised to maximise the reward. RLHF is what turned GPT-3 into ChatGPT; it is also what makes models feel polite, structured, and "aligned" with human expectations. The model market splits along an **access axis**: **closed** models (GPT, Claude, Gemini) hide weights, architecture, and training data, exposing only an API and charging per token; **open-weights** models (Llama, Mistral, Qwen, Gemma, Phi) publish the trained weights, sometimes the architecture, rarely the training recipe; **open-source** models (BLOOM and a few others) publish everything including the training pipeline. The choice between closed and open-weights is **rarely about quality** at the frontier - it is about cost, latency control, data residency, vendor lock-in, and the ability to fine-tune. Hosting open-weights locally is realistic for everything up to ~70B parameters with consumer or workstation hardware; ecosystems like Hugging Face, Ollama, Apple MLX, and `llama.cpp` make this routine.

## Cheatsheet

| Concept | One-line | Where it shows up |
|---|---|---|
| **Pre-training** | Next-token prediction on a giant corpus | Stage 1; learns language and world knowledge |
| **Instruction tuning** | Supervised fine-tuning on (prompt, response) pairs | Stage 2a; makes the model follow instructions |
| **RLHF** | Reinforcement learning from human preference labels | Stage 2b; aligns the model with human ratings |
| **DPO / RLAIF** | Newer RLHF alternatives (Direct Preference Optimisation, AI Feedback) | Cheaper than full RLHF, similar quality |
| **Closed model** | API only, no weights | GPT-4, Claude, Gemini |
| **Open-weights** | Weights released, training mostly opaque | Llama, Mistral, Qwen, Gemma, Phi |
| **Open-source** | Weights + code + training recipe | BLOOM, OLMo |
| **Hugging Face** | The hub: model registry, datasets, inference API | First stop for any open model |
| **Ollama** | Local-runtime daemon for quantised open models | `ollama pull qwen2.5:14b` |
| **Apple MLX / llama.cpp** | Optimised inference runtimes (Apple Silicon, generic C++) | Run 7B-70B models locally |
| **Function calling** | Provider-side tool-calling protocol | OpenAI, Anthropic, Google, others |

---

## How an LLM is trained

The pipeline is short on slides and long in practice. Three ingredients: **data** (hundreds of GBs to trillions of tokens), **compute** (rented GPU/TPU cluster), and **objective** (what the model is optimised to do).

### Pre-training: next-token prediction

The first and most expensive stage. The model is shown an enormous corpus of unlabeled text and trained to predict the next token given the previous ones.

```
input:  "The cat plays with the"
target: "ball"
```

After billions of such predictions across a varied corpus (books, web crawls, code, papers, conversations), the model has learned:

- **Grammar and syntax** by statistical exposure.
- **Factual knowledge** present in the corpus.
- **Style and register** of different domains.
- **Linguistic regularities** (synonyms, idioms, multi-word expressions).

The pre-trained model is *not yet useful* in a chat sense: it completes text, it does not respond to instructions. Asking GPT-3 base "What is the capital of France?" might continue with "and what is the capital of Germany?" rather than answer.

### Fine-tuning: instruction tuning

To turn a text completer into an assistant, train on (instruction, response) pairs:

```
input:   "What is the photosynthesis process in plants?"
target:  "Plants absorb carbon dioxide from the air and convert it into sugars using chlorophyll and sunlight."
```

This is supervised fine-tuning (SFT). The model learns the *shape* of a helpful response: complete sentences, no continuations, answer the question. SFT alone produces something usable; pairing it with RLHF makes it good.

### RLHF: aligning with preferences

How do you tell the model that "Response 3 is better than Response 1 because it is more detailed and practical"? The supervised signal alone cannot express ranking; you need preference data.

**Reinforcement Learning from Human Feedback** has three steps:

1. **Sample responses.** The model generates multiple candidates for the same prompt.
2. **Human ranking.** Annotators rank the candidates by quality.
3. **Optimisation.** A reward model is trained on the rankings; the LLM is then optimised (via PPO or similar) to maximise the reward.

Concrete example from the deck:

> *Prompt: "Tell me how to grow a vegetable garden at home."*
>
> 1. "Plant seeds in pots and put them in the sun."
> 2. "Building a home garden needs space, light, and regular care."
> 3. "Choose plants suited for indoors, use well-draining containers, consider artificial lights if needed."
>
> Human ranking: 3 > 1 > 2 (more detailed and practical wins).
>
> RLHF: update the model to make responses look more like 3.

### Benefits and limits

| RLHF benefits | RLHF limits |
|---|---|
| Aligns the model with human expectations | Encodes human biases (annotators' opinions) |
| Reduces offensive / dangerous outputs | Expensive: needs thousands of high-quality human rankings |
| Continuous improvement loop (reward model + new feedback) | Trade-off between exploration and reliability |

Newer alternatives reduce the cost. **DPO** (Direct Preference Optimisation) trains the LLM directly from preference pairs without an explicit reward model. **RLAIF** (RL from AI Feedback) uses a stronger LLM to rank responses instead of humans. The combination of SFT + DPO is now the most common training recipe for open-weights models.

---

## The access axis: closed, open-weights, open-source

The hardest decision in choosing a model is rarely about quality at the frontier. It is about **what you get with the model**.

### Closed

API-only access. No weights, no architecture details, no training data. Examples: **GPT-4** family (OpenAI), **Claude** family (Anthropic), **Gemini** family (Google).

| What you get | What you do not get |
|---|---|
| State-of-the-art quality | The weights |
| Operational simplicity (no infra) | Inference control |
| Pay-per-token billing | Data residency choice |
| Function calling, vision, etc. | Fine-tuning beyond what the API exposes |

The trade is **quality and simplicity for cost and lock-in**. A closed model on a third-party data centre is a non-starter for regulated domains (healthcare, defence, finance with strict data-residency requirements).

### Open-weights

Trained weights are public, often with the architecture. The training data and full training recipe are usually not. Examples: **Llama** (Meta), **Mistral** (Mistral AI), **Qwen** (Alibaba), **Gemma** (Google), **Phi** (Microsoft).

| What you get | What you do not get |
|---|---|
| The actual weights to run anywhere | The exact training recipe |
| Full inference control | Full reproduction of the training |
| Free to fine-tune within licence terms | Sometimes commercial restrictions (Llama: certain user-count thresholds; Gemma: commercial allowed) |
| No per-token cost (only compute) | Frontier quality on every task (gap is narrowing) |

The trade is **lower cost and full control for higher operational burden**. You handle hosting, scaling, monitoring, updates. For high-volume applications the per-token cost of a closed model exceeds the rented GPU cost of an open-weights one fairly quickly.

### Open-source

Everything is public: code, weights, training data, recipe. Examples: **BLOOM** (BigScience, 170B), **OLMo** (Allen AI). Rare; the training cost makes truly open releases hard to fund.

| What you get | What you do not get |
|---|---|
| Full reproducibility | Frontier quality (older, smaller models) |
| Full audit of training data | Always be the latest |
| Research-grade transparency | Compete with closed-frontier on most benchmarks |

The trade is **transparency for currency**. Useful for research, audit, regulated environments where the training data composition needs to be known.

### Picking the right tier

| Situation | Pick |
|---|---|
| Production launch, frontier quality needed, OK with vendor lock-in | Closed (GPT-4, Claude, Gemini) |
| Data must not leave premises, high volume | Open-weights, self-hosted |
| Need to fine-tune on private data | Open-weights |
| Need full audit / reproducibility | Open-source |
| Prototype, MVP, fast iteration | Closed (cheapest to start) |
| On-device / edge | Open-weights small (Phi, Gemma 2B, TinyLlama) |

---

## The closed-model landscape

The closed market is a small number of providers each with a model family of varying sizes and capabilities. **As of late 2025** the picture is roughly:

| Provider | Family | Notable for |
|---|---|---|
| OpenAI | GPT-4, GPT-4o, o1, o3 | Frontier quality, reasoning models, vision, function calling |
| Anthropic | Claude 3.x, Claude 4.x | Long context (200k), strong on coding and reasoning |
| Google | Gemini 1.5/2 Pro, Flash | Largest context window (up to 2M tokens), tight Workspace integration |
| Mistral (mixed) | Mistral Large | European provenance, balanced quality / cost |

### Capabilities every closed API exposes today

Three capabilities that started as add-ons and are now table stakes:

- **Text generation**: the baseline.
- **Vision**: multimodal input (image + text) for description, OCR, visual reasoning.
- **Function / tool calling**: a structured way for the model to request a Python function be called, with the runtime executing it and returning the result. The protocol is roughly the same across providers, with provider-specific JSON shapes.

The deck flags an example: *"What's the weather in Milan?"* triggers `get_weather("Milan")` rather than the model guessing. This is the foundation of every agent built on top of these APIs (see [Module 03 / 02_agent_components.md](../../03_agentic_ai/notes/02_agent_components.md)).

### Billing

Pay-per-token. The pricing structures differ:

- **Input tokens** are cheaper than output tokens (typically 3-5x cheaper).
- **Context caching** (Anthropic, Google) reduces input cost on repeated prefixes.
- **Batch APIs** offer 50% discounts in exchange for higher latency.
- **Reasoning models** (o1, o3) charge for hidden "thinking" tokens too.

A rough sense of scale: GPT-4o-mini at the time of this note is about $0.15 / $0.60 per million input/output tokens. A typical chat-style request is hundreds of input tokens and hundreds of output tokens; you can spend hours interacting before the bill becomes noticeable. RAG over a large corpus or long-context use shifts the picture: input tokens dominate, costs add up.

---

## The open-weights landscape

The open-weights ecosystem moves fast. As of late 2025 the dominant families are:

### Llama (Meta)

The series that mainstreamed open-weights LLMs. Llama 3.x series spans 1B, 8B, 70B, 405B parameters. Trained on multi-trillion-token corpora. Licence permits commercial use with a user-count cap for the largest operators.

Variants: **Llama 3.1** (general purpose), **Llama 3.2** (added 1B/3B for edge + vision variants), **Llama 3.3** (improved quality at the 70B size).

### Mistral

A European provider with both open-weights and closed models. **Mistral 7B**, **Mixtral 8x7B** (mixture of experts), **Mistral Small / Medium / Large** form a tier. Strong instruction-following at small sizes.

### Qwen (Alibaba)

The Chinese open-weights line. **Qwen 2.5** spans 0.5B to 72B parameters. Strong multilingual capability and instruction following; the 14B variant is the model used in module 03 exercises 03-06 because of its consistent JSON-mode behaviour.

### Gemma (Google)

Open-weights based on the Gemini architecture. **Gemma 2** at 2B, 9B, 27B parameters. Tight integration with Google's ecosystem; permissive licence.

### Phi (Microsoft)

Small models that punch above their weight. **Phi-3.5 Mini** (3.8B) is competitive with much larger models on reasoning benchmarks. The Phi series uses heavily curated synthetic training data.

---

## Tools for running open-weights models

The ecosystem that makes self-hosting realistic.

### Hugging Face

The hub for everything: models, datasets, evaluations, inference API. Three things to know:

- **Models repository.** Over 50k models, every open-weights release shows up here.
- **`transformers` library.** Standard Python API for loading any pretrained model: `AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")`.
- **Inference endpoints.** Hosted inference if you do not want to run the model yourself.

### Ollama

A daemon that runs quantised open-weights models locally, with a one-line command:

```bash
ollama pull qwen2.5:14b
ollama run qwen2.5:14b
```

Models are quantised to int4 or int8 by default; 14B parameters fit in ~9 GB. The daemon exposes an OpenAI-compatible API on `localhost:11434`, which is what most clients (including LiteLLM, LangChain) use. Ollama is the de-facto local-development tool; module 03 exercises 02-07 all run against it.

### Apple MLX

Apple's machine-learning framework optimised for the M-series Silicon. Native support for the Metal Performance Shaders accelerates inference on MacBooks and Mac Studios significantly over generic frameworks. Two packages:

- `mlx-examples` (Apple official): example models and training/inference scripts.
- `mlx-llm` (Riccardo Musmeci, the course's author): higher-level interface for running open LLMs on Apple Silicon.

For Apple Silicon users, MLX is what gives Ollama its speed.

### llama.cpp

A C++ inference runtime, the source of most of the "small model on CPU" magic. Quantises models to formats like `GGUF`, supports CPU and GPU inference on a wide range of hardware. Even Ollama uses llama.cpp under the hood.

---

## Reading the leaderboards

Most LLM leaderboards rank models by aggregate scores on benchmark suites: MMLU (general knowledge), HumanEval (code), GSM8K (math), MT-Bench (chat quality), Chatbot Arena (human preference). Three things to know about leaderboards:

- **Aggregate scores compress trade-offs.** A model that is great at coding and weak at chat can rank above a model with the opposite strengths if the suite weighs coding more.
- **Benchmarks leak into training data.** Models trained after a benchmark was published may have effectively seen the test set.
- **Production quality often differs from benchmark quality.** A model with strong MMLU might be unusable in production because its instruction-following is poor on your domain.

Use leaderboards to **narrow** the candidate set; pick the final model with an evaluation on **your** task.

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Choosing a model by parameter count alone | Bigger model that is worse on your task | Evaluate on a domain-relevant test set |
| Using a base (pre-trained) model instead of an instruction-tuned one | Model completes text instead of answering | Always use the `-Instruct` or `-Chat` variant for assistant use cases |
| Comparing closed and open-weights on cost without volume | Closed looks cheap, open-weights looks complicated | Closed is cheaper at low volume; the crossover happens fast as volume grows |
| Open-weights licence assumed to be MIT | Compliance issues at scale | Read the actual licence: Llama, Gemma, Qwen each have different rules |
| RLHF preferences treated as ground truth | Models inherit annotator biases | Evaluate against your end users, not against the same annotator pool |
| Function calling expected to work identically across providers | Subtle JSON-shape differences break code | Use a wrapper like LiteLLM that normalises across providers |
| Frontier quality assumed needed everywhere | Over-provisioning by 5-10x | Many tasks work on 7-14B local models |
| Ollama on CPU at 70B | Glacial inference | Either 8-14B locally or 70B+ on serious GPU hardware (or hosted) |

---

## When to use what

| Need | Pick | Why |
|---|---|---|
| Production launch, frontier quality | Closed API (GPT, Claude, Gemini) | Lowest operational burden, best out-of-the-box quality |
| Sensitive data, no third-party | Open-weights, self-hosted | Data never leaves your perimeter |
| Fine-tuning on private domain data | Open-weights with LoRA / QLoRA | Closed APIs offer limited fine-tuning |
| Edge / on-device | Small open-weights (Phi 3.5 Mini, Gemma 2B, TinyLlama) | Fits in a few GB |
| Local development | Ollama with `qwen2.5:14b` or `llama3.1:8b` | Free, fast enough for development |
| Mac development | Apple MLX-LM | Native acceleration |
| Production self-hosting at scale | vLLM or TGI on GPU servers | Optimised for throughput |
| Research / audit | Open-source (BLOOM, OLMo) | Reproducibility matters |
| Multimodal (vision + text) | Closed APIs or open-weights with vision (Llama 3.2 vision, Phi 3.5 vision) | Vision is becoming standard |
| Tool calling | Any model that exposes function-calling natively | All major closed and most open-weights ≥7B support it |

---

## See also

### Other notes
- [01_llm_foundations.md](01_llm_foundations.md) — the architectural foundations these models build on
- [03_prompt_engineering.md](03_prompt_engineering.md) — extracting useful behaviour from any of these models
- [04_rag_fundamentals.md](04_rag_fundamentals.md) — augmenting any of these models with external knowledge
- [08_ethics_and_governance.md](08_ethics_and_governance.md) — the responsibility side: bias, hallucination, EU AI Act, GDPR
- Module 03 [04_frameworks.md](../../03_agentic_ai/notes/04_frameworks.md) — LangChain abstracts most provider differences; LangGraph builds graphs across them
- Module 03 [07_deployment.md](../../03_agentic_ai/notes/07_deployment.md) — running these models behind an HTTP service

### Related work in this repo
- Module 02 exercises 03 and 04 (LangChain prompt pipeline, RAG chatbot) — use Ollama with `llama3.2` and `mistral` locally
- Module 03 exercises 02-07 — settle on `qwen2.5:14b` for tool-calling and structured-output reliability
- Module 02 PRJ (`PRJ_sistema_rag_conoscenza_aziendale.py`) — hybrid retrieval pipeline that could front any of these models
