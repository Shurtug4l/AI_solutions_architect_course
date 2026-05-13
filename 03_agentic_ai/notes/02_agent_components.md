# Agent Components

## TL;DR

A working AI agent decomposes into **five building blocks** that have to fit together cleanly: the **LLM** (the brain that decides), the **tools** (the actions it can take), the **structured output** (the parseable form of every decision), the **planning** (the step decomposition), and the **memory** (what it remembers across turns and across sessions). The first three are infrastructure: they are present in every non-trivial agent and they have predictable interfaces. The last two are design choices: planning can live in the system prompt or be split between a planner LLM and an executor LLM, and memory splits into a short-term channel (RAM-equivalent: this session's context) and a long-term channel (disk-equivalent: persisted across sessions). Tools are advertised to the model as **JSON Schemas**, not as Python code; in practice frameworks generate the schema from a Python function plus a docstring. The structured output format that has actually won the field is JSON: YAML, XML, TOML are all parseable but JSON is what tool-calling APIs across providers expect. Every meaningful design choice in an agent reduces to: which of these five blocks am I touching and what is the contract with the others.

## Cheatsheet

| Component | One-line | Where to look |
|---|---|---|
| **LLM** | Stateless next-token generator | The brain |
| **Tool** | External function the LLM can call via a typed call | The hands |
| **Structured Output** | Typed payload (JSON) the LLM emits instead of prose | The mouth |
| **Planning** | Decomposing a goal into ordered sub-tasks | The reasoning layer |
| **Memory** | What the agent remembers (short or long term) | The recall layer |
| **Tool schema** | `name + description + JSON-schema parameters` | What the model sees |
| **`tool_choice`** | `auto / none / required` policy on the call | How the runtime forces the choice |
| **Plan-Execute split** | Planner LLM proposes steps, Executor LLM runs them | A specific paradigm; see [03](03_paradigms_react_planexecute_reflexion.md) |
| **STM** | Conversation context, in-session | Trimmed or summarised; see [05](05_short_term_memory.md) |
| **LTM** | Vector store + metadata, cross-session | Memory-augmented retrieval; see [06](06_long_term_memory.md) |

---

## The five building blocks

```
┌──────────────────────────────────────────────────────┐
│                   AI AGENT                            │
│                                                       │
│      🧠 LLM ────────► reasoning + decision            │
│         │                                             │
│         ├── 🛠️  Tools ──► action surface             │
│         ├── 📋  Structured Output ──► parseable form │
│         ├── 🎯  Planning ──► step decomposition       │
│         └── 💾  Memory ──► state across turns        │
└──────────────────────────────────────────────────────┘
```

The deck makes this concrete with a single running example: *"Plan a trip to Paris"*. The LLM is the central reasoner, the tools are the booking-and-search functions, the structured output is what the LLM emits when it decides which tool to call, planning is the decomposition into book-flight / book-hotel / build-itinerary, and memory keeps track of decisions the user has already made (date constraints, budget, preferences).

A useful litmus test when reading an agent codebase for the first time: identify which of these five blocks each piece of code touches. Code that touches more than one block usually deserves splitting.

---

## Tools

> A tool is an external function the LLM can invoke. It is NOT Python code; it is a schema the LLM has to understand.

This is the line that matters: the model never sees the function body. It sees three pieces of metadata, generated from the function signature plus its docstring.

```python
def add(a: int, b: int) -> int:
    """Sum of two integers.

    Args:
        a: first integer number.
        b: second integer number.
    Returns:
        the sum of a and b.
    """
    return a + b
```

Converted to a tool schema (OpenAI / LiteLLM / LangChain shape):

```json
{
  "type": "function",
  "function": {
    "name": "add",
    "description": "Sum of two integers.",
    "parameters": {
      "type": "object",
      "properties": {
        "a": {"type": "integer", "description": "first integer number."},
        "b": {"type": "integer", "description": "second integer number."}
      },
      "required": ["a", "b"]
    }
  }
}
```

Three rules that show up across every tool the model actually picks correctly:

- **Docstring quality is selection quality.** The model reads the description when it decides which tool fits the user's request. A vague description (`"do math"`) loses to a sharp one (`"add two integers, return their sum"`). With ten tools in the catalogue, the docstrings are the dispatch table.
- **Enum reduces wrong values.** When a parameter has a fixed set of valid values, advertise it as a JSON Schema `enum`. The model is far less likely to invent `"english"` when the schema says `["italian", "english", "french"]`. The cleanest way to do this in Python is `Literal[...]` on a Pydantic field.
- **Required flags force decisions.** Marking a field as required removes the temptation to omit it. Module 03 exercise 06 traced an entire bug class to optional fields defaulting to `null`; switching to required with a sentinel value fixed it.

### `tool_choice`

A single parameter on the request that controls whether the model is allowed to call a tool.

| Value | Behaviour | When to use |
|---|---|---|
| `auto` | Model decides whether to call a tool or reply with text | Default: most chat-style agents |
| `none` | Model must reply with text, no tools | Final-answer turn after evidence is collected |
| `required` (or `any`) | Model must call at least one tool | First turn of a strict ReAct loop |

### Schemas in practice

In real codebases the JSON Schema is almost never hand-written. The framework generates it from a decorated Python function (`@tool` in LangChain) or from a Pydantic model. Two patterns we used in the exercises:

```python
# Pydantic-based (used in module 03 exercises 02-06)
class SearchWikipediaParams(BaseModel):
    term: str = Field(..., description="Term to look up on Wikipedia.")
    language: Literal["en", "it", "fr"] = Field(default="en")

# Decorator-based (used in module 03 exercise 04)
@tool
def search_web(query: str) -> str:
    """Search the web for evidence about a claim. ..."""
    ...
```

Both produce the same tool-call interface. The Pydantic path is more verbose but composes cleanly with `with_structured_output` for the agent's own emissions; the `@tool` path is one line and best for quick prototypes.

### Output shape

When the model decides to call a tool, the response is a JSON object containing the tool name and its arguments. The OpenAI shape (which most providers now follow, including Anthropic with a small variant and Ollama via litellm's translation):

```json
{
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "add",
        "arguments": "{\"a\": 1, \"b\": 2}"
      }
    }
  ]
}
```

Two things to notice: the `arguments` field is a *JSON string*, not a parsed object (the model writes a quoted string that the runtime then parses), and the `id` ties this call to the eventual `tool` message that carries the result. Lose the id and the model cannot correlate the response with the call.

---

## Structured Output

> To interpret the LLM's decision correctly, it must be in a parseable format.

The argument is short: a tool call expressed as prose (*"call book_flight for 25 December 2025"*) cannot be dispatched mechanically without a second LLM call to parse it. A tool call expressed as JSON (`{"tool": "book_flight", "date": "2025-12-25"}`) can. Multiply this across thousands of agent turns per day and the prose path becomes unaffordable.

### Why JSON specifically

The deck lists four formats; only one of them is actually used in practice.

| Format | Strengths | Weaknesses |
|---|---|---|
| **JSON** ✓ | Universal, native to every web stack, supported by every tool-calling API | Strict about quotes and commas |
| YAML | Human-readable, optional quoting | Indentation-sensitive, parsing nuances |
| XML | Self-describing, schema-rich | Verbose, painful by hand |
| TOML | Good for config files | Limited type system |

The tool-calling protocols across providers (OpenAI, Anthropic, Google, the open-weight ecosystem) all standardised on JSON. The other formats are still occasionally useful for human-facing configuration, but inside the agent loop JSON is the only sensible choice.

### Where structured output is enforced

Three layers, in order of strictness:

- **Prompt-level**: the system prompt tells the model "reply with valid JSON only". Cheapest, also weakest. Smaller models ignore the constraint frequently. Module 03 exercise 06 went through three iterations precisely because of this fragility.
- **Schema-level**: `with_structured_output(MyModel)` (LangChain), `response_format={"type": "json_object"}` (litellm/OpenAI), or `format=MySchema` (Ollama). The provider's JSON-mode constrains decoding so the output is guaranteed to parse as JSON. The schema is then validated against a Pydantic model client-side.
- **Tool-call-level**: when the response is a tool call, the provider already enforces the JSON Schema of the tool's parameters. The downstream parser sees a typed call, not free prose.

Choose schema-level by default; fall back to prompt-level only when the provider does not support JSON mode for the model in question.

---

## Planning

> Planning is the ability to decompose a task into simpler sub-tasks.

The example used in the deck: *"plan a trip"* decomposes into *"check dates / preferences / budget"*, then *"book a flight / book a train / book a hotel"*. The decomposition itself is a chain of small reasoning steps that the LLM is good at; the *execution* of each step is what calls the tools.

### Two ways to express planning

The planning logic can live in different places depending on how much agency the agent has.

**Workflow style**: the plan is hard-coded in the system prompt and the surrounding Python.

```
system prompt:
  Step 1: ask the user for dates.
  Step 2: ask the user for budget.
  Step 3: call search_flights(...).
  Step 4: call book_flight(...).
```

The model sees the plan as a recipe. Branching (`if-else`) is encoded in the prompt or in the Python wrapper around the calls.

**Pure-agent style**: the system prompt describes the goal and the tools, the model improvises the plan at every turn.

```
system prompt:
  Your goal is to plan a complete trip to <destination> within <budget>.
  Use the available tools as needed.
```

The model decides the order, the branching, and when to stop.

### Plan-Execute as a paradigm

A third way: **split planning from execution** across two LLM calls.

- **Planner**: receives the goal and produces an ordered list of steps as structured output. Does not call tools.
- **Executor**: takes one step at a time from the planner's output and runs the tools to fulfil it.

This is the **Plan-Execute paradigm**, covered in depth in [03_paradigms_react_planexecute_reflexion.md](03_paradigms_react_planexecute_reflexion.md). The split has three practical effects:

- The planner can use a stronger / slower / more expensive model for the strategic step; the executor can use a cheaper one for the tactical steps.
- The full plan is inspectable before any action is taken (good for audit, dry-run, user confirmation).
- The executor cannot drift from the plan, because the plan is fixed input rather than emergent state.

The trade-off is that the planner cannot react to results it has not yet seen. ReAct and Reflexion (next note) sit at the other end: they interleave planning and execution turn by turn.

### Practical considerations

- **The system prompt does the planning work.** Even in pure-agent style, what the model produces is heavily shaped by how the goal is described. A vague goal yields a wandering plan; a sharp goal with constraints yields a tight one.
- **Planner and Executor can be the same model.** They do not have to be different weights; what differs is the prompt and (sometimes) the temperature.
- **Plan-Execute is a tradeoff between speed, quality, and cost.** Two LLM calls per step always cost more than one. Use the split when the planning step genuinely benefits from being separated (long plans, audit requirements, multi-stakeholder approval before execution).

---

## Memory

> Memory is the mechanism by which an agent retains information over time.

Two channels, each with a different time scale and a different storage medium.

| | Short-Term Memory (STM) | Long-Term Memory (LTM) |
|---|--------------------------|-------------------------|
| Analogy | RAM | Disk / database |
| Scope | Current session | Persistent across sessions |
| Content | Conversation history, tool results | Entities, facts, episodes the agent has decided are worth keeping |
| Capacity | Bounded by context window | Effectively unbounded |
| Update | Append on every turn | Selective writes via an extractor |
| Read | Concatenation into the prompt | Retrieval via similarity search |

### Short-Term Memory variants

Three patterns, in order of sophistication, cost, and detail-preservation.

**Context window memory** (the simplest): concatenate the entire history into the prompt at every turn. Limit: cost grows linearly, eventually hits the context-window cap.

```
[system prompt]
[turn 1: user]
[turn 1: agent]
...
[turn N: user]      ← LLM call
```

**Summarisation memory**: a separate LLM periodically compresses old turns into a running summary. The prompt at each turn becomes `[system + summary + recent turns]` instead of `[system + all turns]`.

- Pros: scalable, cheaper per turn, retains the global thread.
- Cons: detail loss is irreversible; the summariser has to decide what counts as a "key fact" worth keeping.

**Priority memory** (semantic retrieval over recent turns): embed every past turn, and at the current turn retrieve the K most similar ones to inject into the prompt. The agent has access to *relevant* history rather than *recent* history.

```
[system prompt]
[turn 1 (retrieved as similar)]
[turn 3 (retrieved as similar)]
[current turn]      ← LLM call
```

Each pattern has its sweet spot. Module 03 exercise 05 walked through the trim-vs-summarise comparison directly; see [05_short_term_memory.md](05_short_term_memory.md) for the full picture.

### Long-Term Memory

Persistence across sessions requires writing things out and reading them back in. The standard pattern is **retrieval-augmented memory**:

```
write path:
  conversation → Extractor (LLM or NER) → Memory Gate → VectorDB + Metadata

read path:
  current question → Memory Retrieval (vector similarity) → prepended to prompt
```

The **Memory Gate** is the cheap-but-important guardrail: not every utterance deserves to be stored. The gate is usually a small LLM or rule that decides "this is worth remembering" before the entity reaches the store.

The full LTM treatment lives in [06_long_term_memory.md](06_long_term_memory.md), which also covers the RAG-vs-CAG distinction, embedders, vector stores, reranking, and hybrid search.

### The Memory Manager

A higher-level component that orchestrates both channels.

```
user question → Memory Manager ──► fetch from LTM (vector retrieval)
                       │
                       └─► assemble STM (trim or summarise recent turns)
                       │
                       └─► compose final prompt: system + LTM hits + STM + question → agent
```

The Memory Manager is what makes the agent feel coherent across both timescales without flooding the context window. Module 03 exercise 06 builds a tiny version of this for the customer-support agent.

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Tool docstring is a one-liner | Model picks the wrong tool from the catalogue | Write a sentence-long description with the parameters explained |
| Tool parameters as `str` instead of `Literal[...]` | Model invents values outside the valid set | Type as `Literal` so the schema advertises an enum |
| Optional fields in structured output | Model returns `null` to avoid commitment | Make required + use a sentinel value (e.g. `"NONE"`) |
| Two tools with overlapping responsibilities | Model alternates between them or picks the worse one | Merge or split: one tool, one job |
| Plan in the system prompt for a pure agent | Model follows the recipe verbatim even when wrong | Either commit to workflow style or trust the model to plan |
| Memory dumped verbatim into every prompt | Cost grows linearly with conversation length | Trim, summarise, or retrieve selectively |
| Long-term memory without a gate | Vector store grows uncontrolled, retrieval quality degrades | Cheap LLM or rule decides what to persist |
| `tool_choice="required"` on a chat-style endpoint | Model is forced to call a tool even on greetings | Use `"auto"` unless you are inside a strict step that needs a tool |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| One off, no follow-up | LLM only, no agent | Cheapest path |
| User wants the agent to look something up | LLM + one tool | Tool calling adds the action surface |
| Result must be machine-parseable | Structured output (Pydantic + `with_structured_output`) | Eliminates parsing ambiguity |
| Sequence of steps with clear branching | Workflow + LLM at edges | Determinism wins on bounded tasks |
| Open-ended multi-step task | Pure agent with tools | Flexibility wins on fuzzy intent |
| Planning matters more than execution speed | Plan-Execute split | Strategic step gets its own model + audit |
| Conversation lasts > ~20 turns | Summarisation or priority memory for STM | Context window cost becomes the bottleneck |
| User identity persists across sessions | LTM with vector store + memory gate | Cheap to set up, big quality win |
| Strict audit / compliance | Structured output everywhere, tool choice logs | Each decision is replayable |

---

## See also

### Other notes
- [01_agents_vs_workflows.md](01_agents_vs_workflows.md) — the framing this note expands on
- [03_paradigms_react_planexecute_reflexion.md](03_paradigms_react_planexecute_reflexion.md) — Plan-Execute as a paradigm, in detail
- [04_frameworks.md](04_frameworks.md) — LangChain decorators that turn Python functions into tool schemas
- [05_short_term_memory.md](05_short_term_memory.md) — trimming and summarisation in depth
- [06_long_term_memory.md](06_long_term_memory.md) — vector stores, RAG, CAG, episodic memory

### Exercises that exercise the concepts in this note
- [`02_ex_translation_wikipedia_agent.ipynb`](../exercises/02_ex_translation_wikipedia_agent.ipynb) — tools with Pydantic schemas, `tool_choice="auto"`, JSON tool-call protocol
- [`03_ex_fact_checker_react_reflexion.ipynb`](../exercises/03_ex_fact_checker_react_reflexion.ipynb) — structured output for a `Critique` schema, planning-via-system-prompt
- [`04_ex_fact_checker_langchain_vs_langgraph.ipynb`](../exercises/04_ex_fact_checker_langchain_vs_langgraph.ipynb) — `@tool` decorator vs Pydantic schemas, `with_structured_output`, two framework patterns side by side
- [`06_ex_customer_support_rag_cag_episodic.ipynb`](../exercises/06_ex_customer_support_rag_cag_episodic.ipynb) — episodic memory with extractor + memory gate, three-iteration journey on the structured-output schema
