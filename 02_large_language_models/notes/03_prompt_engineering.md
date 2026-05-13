# Prompt Engineering

## TL;DR

A **prompt** is the input you hand to an LLM; **prompt engineering** is the discipline of optimising that input to get the output you want. It splits into two parts: **pattern engineering** (how the prompt is *structured* - persona, refine, explain, instruction-following) and **strategy** (how examples or reasoning are *included* - zero-shot, few-shot, chain-of-thought and its variants). Instruction-tuned models are optimised to follow well-formed instructions, so a clearly-stated task ("Summarise X in two paragraphs") gets you a long way before any sophisticated technique is needed. When that is not enough, **few-shot** examples teach the model the format and style without fine-tuning, **chain-of-thought** asks the model to reason step by step before answering, **self-consistency** samples multiple reasoning paths and picks the majority answer, **tree-of-thought** branches the reasoning explicitly, **least-to-most** decomposes a complex problem into ordered sub-problems. The cost story is the same shape throughout: more reasoning tokens cost more money and more time, but on reasoning-heavy tasks the quality gain is substantial. The same model in the same setting can be a sentiment classifier, a summariser, a translator, or a chatbot - the determining factor is the prompt, not retraining.

## Cheatsheet

| Concept | One-line | Where it shows up |
|---|---|---|
| **Prompt** | Any input to a generative model | The whole field rests on this |
| **System prompt** | Persistent instruction at the top of the conversation | Defines persona, constraints, output format |
| **Persona pattern** | "You are an X, do Z" | Tone, expertise, occasionally bypass safety filters |
| **Refine pattern** | "Given X, propose improved versions" | Variant generation, A/B prompt iteration |
| **Explain pattern** | "Solve X and explain each step" | Probes the model's reasoning, useful for debugging |
| **Zero-shot** | Instruction, no examples | Default; works on instruction-tuned models for clear tasks |
| **Few-shot** | Instruction + a handful of input/output examples | Teaches format and style without fine-tuning |
| **Chain-of-Thought (CoT)** | "Think step by step" | Reasoning quality jump on math, logic, multi-step tasks |
| **Self-consistency** | Sample N CoT runs, take majority | Higher quality at N× cost |
| **Tree of Thoughts** | Branch and explore alternate reasoning paths | Hard problems; expensive |
| **Least-to-most** | Decompose problem into ordered sub-problems | Multi-step procedural tasks |
| **Thread-of-thought** | Non-linear reasoning across multiple threads | When the answer requires synthesising disconnected chains |

---

## What prompt engineering is

A prompt is the text fed to a model to produce a response. Prompt engineering is two things at once:

1. **Optimising textual patterns** given to the model.
2. **Choosing prompting strategies** that organise how those patterns are presented.

A well-tuned prompt can change a model's behaviour from "vaguely on-topic prose" to "structured, useful answer that respects the required format". It is not magic - the model still has the same parameters - but it is the cheapest possible lever, applied at inference time, that does not require any training.

### Two reasons it works

Modern decoder LLMs are **instruction-tuned** (see [02_model_landscape.md](02_model_landscape.md)). The fine-tuning stage made them sensitive to clear instructions and structural conventions in their input. A well-formed instruction triggers the behavior the model was trained to associate with that shape.

Decoder LLMs are also **in-context learners**: they can adapt their behaviour from examples placed in the prompt without any gradient update. A few input/output pairs in the prompt act as a tiny on-the-fly fine-tune.

These two properties are what every prompt-engineering technique exploits.

---

## Common patterns

The first half of prompt engineering is the *shape* of the instruction.

### Persona pattern

> "You are an X, generate Z."

The model conditions its output on the assigned role. Two effects:

- The **tone, vocabulary, and depth** match the persona's domain.
- For some tasks the persona **changes what the model is willing to do** (a "thoughtful editor" persona produces gentler feedback than a "harsh critic").

```
Prompt:  "You are an expert sommelier. Write a wine list for a Bolognese restaurant."
Output:  curated list with appropriate Lambruscos, balanced reds, food-pairing notes.
```

Bare instructions without a persona are not wrong; they just produce more generic outputs.

### Refine pattern

> "Given X, propose improved versions."

Useful for variant generation: you give the model one item and ask for alternatives. Foundational pattern for "rewrite this in a different tone", "generate three more questions on this topic", "find three weaknesses in this argument".

### Explain pattern

> "Provide a solution for [task] and explain each step of the reasoning."

Forces the model to make its reasoning visible. Two benefits:

- **Debugging**: you see *why* the model produced the answer.
- **Probe of capability**: a confident wrong answer in step 3 tells you exactly where the model's knowledge fails.

A precursor to chain-of-thought as a deliberate technique (below).

### Task-oriented prompts

Instruction-tuned models respond to task verbs. The same model becomes a different specialist depending on the verb:

| Verb | Task |
|---|---|
| "Summarise" | Summarisation |
| "Translate" | Translation |
| "Rewrite" | Style transfer |
| "Extract" | NER / information extraction |
| "Classify" | Classification |

A single base model can be a translator, classifier, summariser, NER tagger - chosen by the leading verb. The point is not that the model is good at all of these; the point is that no retraining is needed to switch.

### Invisible system prompts

Many production LLM products (ChatGPT, Claude, Gemini) ship with an **invisible system prompt** added before the user's input. It sets default persona, safety constraints, and output style. The model the user actually talks to is the model + this hidden context. This explains why the same underlying model can behave very differently when accessed via two different products.

---

## Prompting strategies

The second half: how examples and reasoning hints are organised.

### Zero-shot

Give the model an instruction, ask for the output. No examples.

```
Prompt:  "Write three lines of introduction about Leonardo Sanna."
GPT-4o:  "Leonardo Sanna is a professional in technology and innovation..."
```

Two observations from the deck:

- Zero-shot works when the model **already knows** what it needs (Leonardo Sanna here is too obscure for the model to know; it produced a plausible-sounding fabrication).
- Adding even a tiny amount of context inside the prompt anchors the output:

```
Prompt:  "Write three lines about Leonardo Sanna. Leonardo is a researcher
          working on chatbots in the medical domain, with a degree in
          Communication Sciences."
GPT-4o:  "Leonardo Sanna is a researcher specialising in medical-domain
          chatbots, combining a Communication Sciences background with
          technical depth..."
```

This is the gap between "the model knows the world" and "the model knows what to say". Adding facts inline closes it without retraining.

### Few-shot

Show the model what you want by example. Each example is a complete input/output pair in the same format the model should produce.

The deck's worked example: explain a quirky idiom (*"colore cane che fugge"* - "colour of a fleeing dog", an Italian idiom for an undefined faded shade). Zero-shot, the model takes the phrase literally. One example anchored to the idiom's meaning fixes it:

```
Prompt:
  '"Colore cane che fugge" is an idiom meaning an indistinct, faded shade -
   the colour of a dog seen running away too fast to identify clearly.

   Now use this idiom in a sentence about an old dress.'

GPT-4o:
  "When I saw that dress in the shop, it caught my eye with its colore cane
   che fugge - a shade so faded and indefinite that it seemed to shift in
   the light."
```

Few-shot works when:

- The task is **specific or non-standard** enough that the model needs to be shown.
- The **format** matters more than the model can infer from the instruction alone.
- You have a small set of **good examples** that are representative.

It fails when:

- The examples are **inconsistent** (the model learns the inconsistency, not the task).
- The examples leak **the answer** to a test case (test-set contamination).
- The prompt becomes **too long** (you are paying for input tokens on every call).

### Chain-of-Thought (CoT)

> Ask the model to reason step by step before producing the final answer.

The single most useful prompting trick on reasoning-heavy tasks (math, multi-hop questions, planning).

```
Prompt:  "Maria has 12 apples and divides them equally among 3 friends.
          How many apples does each friend receive?

          1. First compute how many apples Maria has.
          2. Determine the number of friends to share with.
          3. Divide total apples by the number of friends.

          Answer:"

GPT-4o:  "1. Maria has 12 apples.
          2. She has 3 friends.
          3. 12 ÷ 3 = 4.
          Each friend receives 4 apples."
```

Two flavours:

- **Manual CoT**: the prompt itself contains the step-by-step structure (as above).
- **Zero-shot CoT**: the trigger phrase `"Let's think step by step."` at the end of the instruction. Astonishingly, this alone improves performance on many tasks - the model has learned to produce intermediate reasoning when invited to.

The cost: chain-of-thought multiplies output tokens by the length of the reasoning chain. The benefit on a hard task usually justifies it.

### Self-consistency

CoT generates one reasoning path; one wrong intermediate step ruins the final answer. **Self-consistency** runs CoT N times with different sampling, then picks the **majority answer** across runs.

```
Run 1:   ...reasoning... → answer A
Run 2:   ...reasoning... → answer A
Run 3:   ...reasoning... → answer B
Run 4:   ...reasoning... → answer A
Run 5:   ...reasoning... → answer B
                                      → majority: A
```

The intuition is voting: each reasoning chain has some chance of being wrong, but the majority across many independent chains is more likely to be right. Cost scales linearly with N. On math benchmarks (GSM8K), self-consistency at N=40 lifts model quality by several percentage points.

### Tree of Thoughts (ToT)

Self-consistency runs **independent** chains in parallel. **Tree of Thoughts** structures the reasoning as a **tree**: each node is a partial state, branches are alternative next steps, the model can backtrack from a dead end.

Useful when:

- The problem has **multiple valid intermediate steps** and no single path is obviously best.
- **Backtracking** matters (a step that looked good turns out to fail; another branch should be tried).

The cost is the highest of the four strategies in this list, often by an order of magnitude. Reserved for genuinely hard problems where the cheaper strategies fail.

### Least-to-most

> Decompose the problem into ordered sub-problems, smallest first, and solve them in sequence.

Example from the deck:

> A shop offers a 15% discount on a 120-euro product. The customer pays with a 100-euro and a 50-euro note. How much change do they receive?

Decomposed:

- Sub-problem 1: What is 15% of 120?
- Sub-problem 2: What is the final price after the discount?
- Sub-problem 3: How much does the customer pay?
- Sub-problem 4: How much change?

The model attacks the sub-problems one at a time, each one easier than the original. Useful for procedural tasks (multi-step workflows, business processes); same family as Plan-Execute in agentic terms (see [Module 03 / 03_paradigms_react_planexecute_reflexion.md](../../03_agentic_ai/notes/03_paradigms_react_planexecute_reflexion.md)).

### Thread-of-thought

Reasoning is not always linear. Some tasks require following **multiple parallel threads** of reasoning that converge at the end (synthesising a multi-faceted answer, weighing pros and cons across orthogonal criteria). Thread-of-thought asks the model to maintain and synthesise these threads explicitly.

Less established than CoT; treat as a pattern to reach for when CoT feels too linear for the task.

---

## What you can do with prompting alone

The Transformer's flexibility is the underlying reason the same model can do so many things. Prompting unlocks them.

### Standard generative tasks

What LLMs were trained to do:

- **Summarisation** ("Summarise X in two paragraphs.")
- **Translation** ("Translate Y to French.")
- **Free generation** ("Write a story about a robot.")

### Adjacent tasks

The architecture lets prompting cover tasks that classically needed dedicated models:

- **Text classification** ("Classify the tone of this email as positive, neutral, or negative.")
- **Question answering** ("What is the capital of Burkina Faso?")
- **Sentiment analysis** (a special case of classification)
- **Named Entity Recognition** ("Extract every city name from the text below.")

A concrete example from the slides: sentiment analysis on a multilingual BERT-based classifier achieves >0.9 confidence on clear cases. The same task can be done by a decoder LLM zero-shot, with the trade-off being latency and cost vs the specialised model's speed.

### Instruction-tuning vs fine-tuning

Two ways to specialise a model on a task:

| | Instruction-tuning (prompt) | Fine-tuning |
|---|----------------------------|-------------|
| Cost | Zero (just craft the prompt) | Compute time, data preparation |
| Speed of iteration | Seconds | Hours to days |
| Quality ceiling | Depends on the base model | Higher when domain-specific |
| Best for | Common tasks, varied input | Narrow tasks, consistent format |
| Per-call cost | Pays full input tokens every time | Lower at inference (smaller prompt) |

For most tasks, **prompting beats fine-tuning** on time-to-value. Fine-tuning is worth it when you have a high-volume use case where the prompt has grown long, or when prompting cannot achieve the quality you need.

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Long prompt assumed to anchor better | Model ignores middle context (Lost in the Middle) | Put critical instructions at the start and end |
| Few-shot examples that contradict each other | Model picks the wrong pattern | Curate examples; consistency matters more than quantity |
| Few-shot examples that contain the answer to the question | Test-set leakage; production performance disappoints | Hold examples out from the evaluation set |
| Chain-of-thought asked on a trivial task | Verbose answer, costs more, no quality gain | Use CoT only on reasoning-heavy tasks |
| Persona prompt overused | Model spends tokens on character, less on content | Keep persona one short sentence |
| Self-consistency at high N on cheap-to-fix tasks | High cost for marginal quality gain | Use only when the question is hard and the answer is critical |
| "Let's think step by step" applied indiscriminately | Pointless extra latency | Reserved for arithmetic, logic, multi-hop questions |
| Output format implied, not specified | Model picks an inconsistent format across calls | Require a specific format (JSON, XML) in the prompt |
| Long prompt to compensate for model weakness | The right model for the job would be cheaper end-to-end | Upgrade the model before further prompt-engineering |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Simple, factual task on a modern instruction-tuned model | Zero-shot | Cheap, fast, usually enough |
| Task with a specific format that is hard to describe | Few-shot | Show the format with 2-5 examples |
| Math, logic, multi-step reasoning | Chain-of-thought | Reasoning gain is substantial |
| Critical reasoning where one wrong step kills the answer | Self-consistency over CoT | Voting absorbs single-path errors |
| Genuinely hard problem with multiple plausible paths | Tree of Thoughts | Explicit branching, expensive but powerful |
| Multi-step procedure | Least-to-most | Tackles sub-problems in order |
| Task with a clear role and style requirements | Persona pattern + task instruction | Sets the tone before the work |
| One-off variant generation | Refine pattern | Cheap way to explore alternatives |
| Debugging why a model says X | Explain pattern | Makes reasoning visible |
| Sentiment / classification on cheap deploys | Specialised model (BERT fine-tune) | Faster, smaller than an LLM call |
| Same task at high volume in production | Fine-tuning | Smaller per-call cost, more reliable |

---

## See also

### Other notes
- [01_llm_foundations.md](01_llm_foundations.md) — why decoder LLMs are amenable to prompting at all (next-token training + instruction tuning)
- [02_model_landscape.md](02_model_landscape.md) — choice of model is upstream of prompt design
- [04_rag_fundamentals.md](04_rag_fundamentals.md) — the prompt + retrieved context pattern
- [05_advanced_rag.md](05_advanced_rag.md) — query expansion is a prompting technique on the retrieval side
- Module 03 [02_agent_components.md](../../03_agentic_ai/notes/02_agent_components.md) — system prompts as the spec for agent behaviour
- Module 03 [03_paradigms_react_planexecute_reflexion.md](../../03_agentic_ai/notes/03_paradigms_react_planexecute_reflexion.md) — ReAct extends chain-of-thought into the agent loop

### Related work in this repo
- Module 02 exercise 03 (`03_ex_langchain_prompt_pipeline.ipynb`) — system prompt + few-shot, RAG-grounding, CoT+self-critique side by side
- Module 03 exercise 01 (weather workflow) — extraction prompt design that pays off the few-shot rules above
