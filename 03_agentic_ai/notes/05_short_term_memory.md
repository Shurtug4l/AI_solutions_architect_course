# Short-Term Memory: Trimming, Summarisation, Entity Memory

## TL;DR

LLMs are stateless. Whatever the agent "remembers" inside a session has to be threaded into the prompt every turn, which means deciding *what* to thread in. The context window is the budget: it costs money (every input token is billed), it costs latency (more tokens = higher time-to-first-token), and it has a hard physical cap (~128k on current frontier models). Worse, even within the cap the model exhibits **Lost in the Middle**: it remembers the beginning and end of the context but neglects the middle. Three strategies handle this. **Trimming** keeps only the most recent N messages (or N tokens); cheap, simple, irrecoverable - old details are gone for good. **Summarisation** uses an LLM to compress old turns into a running summary; preserves *some* information at the cost of an extra LLM call per compression event and silent loss of detail (exact numbers, proper nouns, negations). **Entity Memory** extracts the *structured facts* about the user (budget, preferences, constraints) into a typed dictionary that gets injected into the system prompt; preserves the parts that matter at the cost of writing an extractor. The three are not exclusive: production agents usually trim recent history, summarise everything older, and maintain an entity record on top for the user-specific facts that must survive forever. The right strategy depends on what gets lost when you forget the wrong thing.

## Cheatsheet

| Strategy | What it keeps | Cost per turn | What it loses |
|---|---|---|---|
| **Trimming (sliding window)** | Last N messages / tokens | 1 LLM call | Everything older than the window |
| **Summarisation** | Compressed summary + last K messages | 1 LLM call + occasional summary call | Numerical precision, proper nouns, negations |
| **Entity Memory** | Structured user-fact dict + recent messages | 1 LLM call + 1 extractor call per turn | Implicit / unstructured information |
| **Hybrid** | Entity dict + summary + recent | Same as above, combined | Less than any single strategy alone |
| **JetBrains finding** | 10 message pairs is usually enough | - | Anything older contributes little anyway |

---

## Why short-term memory matters

LLMs do not have an internal state between calls. The model sees what is in the prompt, nothing else. Every conversational agent eventually faces the same question: **what do I put in the prompt at every turn?**

The mechanical answer is "everything so far". The practical answer is more interesting because of three constraints.

### The context window is the budget

The context window is the total amount of text the model can consider in a single call. On `gpt-4o` and `claude-3.5-sonnet` it is currently around 128k tokens. The window has to fit:

1. The system prompt.
2. The full conversation history.
3. Tool calls and their (often verbose) results.
4. The current user message.

Every token costs money (input tokens are billed) and time (more tokens = higher TTFT, time to first token). The cap is the hard ceiling; the cost and latency curves rise smoothly long before the ceiling is reached.

A rough sense of scale on a 128k-token model:

- A 30-turn back-and-forth dialogue: a few thousand tokens.
- The same dialogue with one RAG retrieval per turn that returns 500-token chunks: ~20k tokens.
- A long agentic session with tool calls returning full documents or DB rows: 60-100k tokens easily.

### Lost in the Middle

Even when everything fits in the context, the model does not weigh all positions equally. **Lost in the Middle** is the empirical finding that LLMs remember the beginning and the end of the context well, and forget the parts in the middle. A user fact stated 10 turns ago is in the prompt, but the model effectively ignores it.

This is *the* reason naive "concatenate everything" approaches degrade past a certain conversation length even when they technically fit.

### The decision: what to put in the context

The agent designer's job is, every turn, to assemble the most useful subset of the available information into the prompt. Three strategies, three trade-offs.

---

## Strategy 1: Trimming (sliding window)

The simplest mechanism. Every turn, before calling the LLM, cut the message list so it stays under a token budget. Keep the system prompt; keep the most recent messages; drop the oldest.

```
Before trim:                After trim:
  [System]                    [System]
  [User 1]      ← drop         [User 3]
  [Assistant 1] ← drop         [Assistant 3]
  [User 2]      ← drop         [User 4]
  [Assistant 2] ← drop         [Assistant 4]
  [User 3]                     [User 5]   ← current message
  [Assistant 3]
  [User 4]
  [Assistant 4]
  [User 5]      ← current
```

Two parameters to set: what to cut on (messages or tokens) and how much to keep.

### Sliding Window

The dynamic implementation: the window of kept messages slides forward by one (or more) every turn, always pointing at the most recent N.

### How many messages to keep

A 2025 JetBrains study found that **the last 10 message pairs preserve performance comparable to the entire history** on typical conversational tasks. Beyond that, the older messages contribute little additional value - and Lost in the Middle would muffle them anyway.

This is a useful default: window of 10 pairs (20 messages) plus the system prompt.

### Token budget vs message count

| Approach | Pros | Cons |
|---|---|---|
| **N most recent messages** | Simple, no tokenizer needed | Long messages weigh as much as short ones; budget is unpredictable |
| **N most recent tokens** | Predictable token cost | Requires a tokenizer; need to handle the edge case of a single message larger than the budget |

In production the token-based approach wins. A long tool result can push a 10-message buffer to 30k tokens; trimming by token count keeps the budget tight.

### Counting tokens

```python
import tiktoken
enc = tiktoken.encoding_for_model("gpt-4o")

def count_tokens(message: dict) -> int:
    return len(enc.encode(message["content"]))
```

`tiktoken` covers the OpenAI family directly; for Anthropic and others use the provider's tokenizer or the model's `usage_metadata` after a sample call (which is what module 03 exercise 05 does for Ollama).

### Edge cases

| Edge case | What can go wrong | Fix |
|---|---|---|
| Single message exceeds the budget | Cannot fit, cannot drop everything around it | Truncate the message or reject the turn |
| System prompt exceeds the budget | Negative budget for history | Refactor the system prompt; nothing else helps |
| Mid-pair cut | Lone user without assistant (or vice versa) confuses the model | Always cut whole user+assistant pairs |
| Long tool result | One observation eats half the budget | Truncate or summarise the tool result before adding to history |

### Implementation

**From scratch** (token-budget trim, preserves the system prompt):

```python
def trim_messages(messages: list, max_tokens: int) -> list:
    system = [m for m in messages if m["role"] == "system"]
    history = [m for m in messages if m["role"] != "system"]
    system_tokens = sum(count_tokens(m) for m in system)
    budget = max_tokens - system_tokens

    kept, total = [], 0
    for message in reversed(history):
        tokens = count_tokens(message)
        if total + tokens > budget:
            break
        kept.insert(0, message)
        total += tokens
    return system + kept
```

**With LangChain** (modern API):

```python
from langchain_core.messages import trim_messages

windowed = trim_messages(
    messages,
    strategy="last",
    token_counter=len,            # count messages instead of tokens
    max_tokens=10 + 1,            # 10 pairs + 1 system message
    include_system=True,
    start_on="human",
)
```

The deprecated `ConversationBufferWindowMemory` and `ConversationChain` you may still find in older tutorials are gone in LangChain v0.3+. Recognise them as legacy; replace with `trim_messages` + `RunnableWithMessageHistory` (or LangGraph's `InMemorySaver`).

### Limits

Trimming is fast and cheap and **irreversibly lossy**. If the user mentioned an important detail 30 turns ago - a name, a budget, an explicit constraint - that detail is gone. The next strategy is the response.

Module 03 exercise 05 makes this concrete: the sentinel fact "I have a maximum budget of €1,200" planted at turn 2 is invisible to a 10-message window by turn 14. Recall test fails.

---

## Strategy 2: Summarisation

Instead of dropping old messages, **compress** them. An LLM reads the old turns and produces a running summary. The summary takes the place of the dropped messages in the prompt.

```
BEFORE:                            AFTER:
[System]                           [System]
[User 1]    ┐                      [Summary: "User wants X, agreed on Y,
[Ass.  1]   │  → summarize() →      budget €10,000, prefers Python"]
[User 2]    │                      [User 8]
[Ass.  2]   ┘                      [Assistant 8]    ← recent verbatim
[User 3]    ┐                      [User 9]
[Ass.  3]   │  recent verbatim     [Assistant 9]
...         ┘                      [User 10]        ← current
[User 10]
```

### When to trigger summarisation

Two common patterns:

- **Token threshold.** When the history exceeds N tokens, compress everything older than the last K messages into the summary.
- **Fixed cadence.** Every K turns, fold the oldest pair into the running summary.

The fixed-cadence pattern is what module 03 exercise 05 implements: when the recent buffer exceeds 6 messages, the oldest 2 get folded into the summary incrementally. Incremental folding (instead of re-summarising the whole history) keeps each summary call short and avoids the drift that comes with repeated re-paraphrasing.

### Where the summary lives

The summary becomes a `system` message (or a synthetic assistant message) inserted after the actual system prompt and before the recent history. The model reads it as compressed context for the past.

### The risks

LLM summarisers have specific failure modes. They tend to drop exactly the kinds of information you most need to keep:

- **Exact numbers.** "Around €10,000" replaces "exactly €9,847".
- **Proper nouns.** Names of people, products, companies get lost or genericised.
- **Specific instructions.** Constraints become generic phrasing.
- **Negations.** "He said he does NOT want X" becomes "he discussed X".

These are not implementation bugs; they are statistical tendencies of paraphrasing. The mitigations are prompt-side: tell the summariser explicitly to preserve numbers verbatim, to keep proper nouns, to copy constraints word-for-word.

### Implementation

**From scratch**:

```python
def summarize_history(messages: list, llm) -> str:
    history = [m for m in messages if m["role"] != "system"]
    text = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in history)
    prompt = (
        "Summarise the conversation below in at most 3 sentences. "
        "Preserve KEY FACTS verbatim (budget, brand preferences, requirements, decisions). "
        "Drop small talk.\n\n"
        f"{text}"
    )
    return llm.invoke(prompt).content
```

**With LangChain (legacy)**:

```python
memory = ConversationSummaryBufferMemory(
    llm=summary_model,
    max_token_limit=1000,
    return_messages=True,
)
chain = ConversationChain(llm=main_model, memory=memory)
chain.predict(input="Do you remember the budget we discussed?")
```

Deprecated in v0.3+; same migration as trimming.

### Trade-offs

| Aspect | Trimming | Summarisation |
|---|---|---|
| Cost per turn | One LLM call | One main LLM call + one summary call when the threshold is hit |
| Information retention | Recent messages only | Compressed access to the entire history |
| Failure mode | Old details disappear | Old details get paraphrased away |
| Determinism | Fully deterministic | Summary depends on the summariser |
| Right when | Sessions are short OR verbatim recall matters | Sessions are long AND only key facts need to survive |

Module 03 exercise 05 implemented both side by side. On the 15-turn dialogue the summary version preserved the budget through turn 14 (recall test passes); the trim version lost it by turn 8 (recall test fails).

---

## Strategy 3: Entity Memory

Trimming and summarisation both work on the *form* of the conversation (how many messages, how compressed). Entity Memory works on the *content*: extract only the discrete facts about the user, store them in a structured dictionary, inject the dictionary into every turn's system prompt.

The question changes from *"how many messages do I keep?"* to *"what should I remember about this user?"*.

### How it works

Three operations per turn:

1. **Extract.** A small LLM (or a NER pipeline) reads the new user message and identifies relevant facts.
2. **Update.** The facts are merged into the existing entity dictionary.
3. **Inject.** The updated dictionary is rendered into the system prompt for the next turn.

```
System prompt
+ "Known about the user:
   - name: Marco
   - preferred language: Python
   - budget: €9,847
   - constraints: no cloud solutions"
+ [last N messages]
```

### Implementation

**From scratch**:

```python
def extract_entities(message: str, current: dict, llm) -> dict:
    prompt = (
        "Given this user message, update the dictionary of known facts. "
        "Return ONLY a JSON object with the fields that changed. "
        "Omit fields that are unchanged.\n\n"
        f"Current entities: {json.dumps(current)}\n"
        f"User message: {message}"
    )
    response = llm.invoke(prompt)
    updates = json.loads(response.content)
    return {**current, **updates}
```

Module 03 exercise 06 builds a slightly richer version: a typed Pydantic schema, `Literal` enums on closed-set fields (e.g. plan name), a `"NONE"` sentinel on optional string fields to force per-turn decisions, and a memory gate that decides whether each extraction is worth keeping.

### Edge cases

The interesting failures are not about extraction quality but about **updates over time**:

| Case | Behaviour |
|---|---|
| **Update** — user corrects a previously stated fact | `entities["budget"] = "15,000€"` overwrites the old value |
| **Conflict** — user states two contradictory things in different turns | Keep the most recent; log the conflict for debugging |
| **Removal** — user revokes a constraint | `entities["constraints"].remove("no cloud")` |

A real production extractor handles all three; a minimal one handles only the update case and accepts the others as known limitations.

### When Entity Memory is the right call

| Use it when... | Skip it when... |
|---|---|
| The important information is discrete and updateable (name, budget, preferences, constraints) | The conversation is open-ended reasoning where context is the meaning |
| The user interacts with the system across multiple sessions | The session is one-off and short |
| You want the agent to "know" the user regardless of when something was said | The important information is implicit and hard to structure |

### A note on persistence

The entity dictionary is small (a few hundred bytes typically). Serialising it to JSON and persisting it across sessions costs almost nothing. This is the cheapest possible form of long-term memory, and the natural bridge to the deeper LTM mechanisms covered in [06_long_term_memory.md](06_long_term_memory.md).

---

## Composing the three

The strategies are not exclusive. A production agent commonly uses all three:

```
   ┌─────────────────────────────────────────────────────┐
   │ system prompt + entity dict (user-fact memory)     │
   ├─────────────────────────────────────────────────────┤
   │ rolling summary of older turns (summarisation)     │
   ├─────────────────────────────────────────────────────┤
   │ last 10 messages verbatim (trimming)                │
   ├─────────────────────────────────────────────────────┤
   │ current user message                                │
   └─────────────────────────────────────────────────────┘
```

Each layer is responsible for a different time scale and granularity. The entity dict carries the structured facts that must survive forever. The summary carries the narrative thread of older turns. The trim window carries the recent verbatim exchange. The current message is the new input.

The pattern generalises beyond chat: any agent that has to remember things within a session is choosing how to combine these three primitives.

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Trimming by message count when tool results are long | Token budget blows up despite the window | Trim by tokens, not by messages |
| Cutting mid-pair (orphan user message) | Model confused about the dialogue structure | Always trim whole user+assistant pairs |
| Summariser drops the exact number / name / negation | Recall test fails on detail | Summary prompt explicitly preserves verbatim |
| Re-summarising from scratch every turn | Summary drifts under repeated paraphrasing | Fold incrementally: each new turn adds to the existing summary |
| `Optional[str]` field in the entity extractor | Model defaults to `null`, never extracts | Required field with `"NONE"` sentinel; few-shot examples |
| Mixed memories without explicit hierarchy | Conflicting facts surface in the prompt | Define which channel wins on conflict (typically entity dict) |
| Lost in the Middle ignored | Long context fits but model forgets the middle | Use summarisation or move key facts to the start/end |

---

## When to use what

| Situation | Strategy | Why |
|---|---|---|
| Short sessions (< 20 turns) with all detail mattering | None (just concatenate) | Cheapest correct option |
| Long sessions, verbatim quotes matter | Trimming with a generous window | No paraphrase risk |
| Long sessions, key facts matter, verbatim does not | Summarisation | Compression preserves the signal |
| Returning users with stable facts (budget, role, preferences) | Entity Memory | Structured facts survive forever |
| Real production agent | Hybrid: entity + summary + trim | Each handles its time scale |
| Costs / latency dominant | Trimming | One LLM call, one trim, no extra summariser |
| Cost / latency acceptable, quality dominant | Summarisation + Entity Memory | Two extra calls, much better recall |

---

## See also

### Other notes
- [01_agents_vs_workflows.md](01_agents_vs_workflows.md) — where this memory plugs into the loop
- [02_agent_components.md](02_agent_components.md) — memory as one of the five building blocks
- [03_paradigms_react_planexecute_reflexion.md](03_paradigms_react_planexecute_reflexion.md) — Reflexion stores lessons in a separate "experience" channel that behaves like Entity Memory at the lesson level
- [04_frameworks.md](04_frameworks.md) — LangChain `trim_messages`, LangGraph `InMemorySaver`, the legacy `ConversationBufferWindowMemory`
- [06_long_term_memory.md](06_long_term_memory.md) — when entity memory grows into a vector store and becomes cross-session

### Exercises that exercise the concepts in this note
- [`05_ex_qa_agent_short_term_memory.ipynb`](../exercises/05_ex_qa_agent_short_term_memory.ipynb) — manual trimming with `trim_messages` and rolling summarisation built side by side on a 15-turn dialogue, with sentinel-fact recall test
- [`06_ex_customer_support_rag_cag_episodic.ipynb`](../exercises/06_ex_customer_support_rag_cag_episodic.ipynb) — entity memory with Pydantic schema, `"NONE"` sentinel, persistent-issue trigger
