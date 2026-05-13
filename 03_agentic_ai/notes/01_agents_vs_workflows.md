# Agents, Workflows, and Orchestration

## TL;DR

An **AI agent** is an LLM that loops: it picks an action, calls a tool, observes the result, decides whether to keep going, and stops when a goal is reached. The structure of that loop is the **agentic loop** with four phases (Plan, Act, Observe, Update) driven by a system prompt and a tool catalogue. A **workflow** sits at the opposite end of the same axis: the steps are fixed in Python by the engineer, the LLM is invoked only at chosen points, and the system is predictable at the cost of flexibility. **Pure agents** are the other extreme: the LLM chooses the next step at every iteration, the system is flexible at the cost of determinism. Most production designs sit somewhere in the middle, mixing the two. The loop fails in four canonical ways (tool error, incomplete input, unstructured output, infinite loop) and is controlled by four canonical mechanisms (retry policy with a hard cap, structured output via JSON Schema or Pydantic, feeding the error history back into the prompt, and explicit termination conditions). Once one agent works, you compose them: an **orchestrator** is itself an LLM (or a typed graph) that routes a request to the right specialised agent or workflow. Orchestration earns its cost when specialisation, permissions, and observability matter more than the latency of an extra hop.

## Cheatsheet

| Concept | One-line | Where it shows up |
|---|---|---|
| **LLM** | Stateless text generator: prompt in, completion out | Backbone of any agent |
| **Tool calling** | LLM picks a registered function + arguments; runtime executes | Connects model to the world |
| **AI Agent** | `LLM + tools + loop` oriented to a goal | The unit we build and deploy |
| **Agentic loop** | Plan → Act → Observe → Update, until goal or cap | The inner control flow |
| **Workflow** | Deterministic Python sequence; LLM at edges | Maximum control, minimum flexibility |
| **Pure Agent** | LLM chooses every step; full autonomy | Maximum flexibility, weak determinism |
| **Retry policy** | `max_retries=N` + reformulation | First defence against tool failures |
| **Structured output** | JSON/Pydantic schema enforced on emissions | Eliminates parsing ambiguity |
| **Error replay** | Append failed call + error to prompt for next iteration | Lets the model learn within the session |
| **Orchestrator** | LLM/graph that picks the next agent or workflow | Multi-agent dispatch |

---

## From LLM to AI Agent

The progression is short and worth being precise about, because the three terms get used interchangeably in casual writing and they are not the same thing.

### LLM

A Large Language Model is a function that takes a prompt (input + context) and produces a continuation. It is stateless: the same prompt twice produces an answer that may differ only because of temperature-driven sampling, not because the model remembers anything. The system prompt + user prompt is the *entire* context the model sees. Everything else - memory, history, knowledge - has to be threaded into that string by the caller.

### Tool calling

A mechanism layered on top of the LLM. The caller advertises a set of **tools** (functions with a JSON Schema for their parameters) and the model can respond not with prose but with a structured "call this tool with these arguments" instruction. The runtime then executes the call, captures the result, and the conversation continues.

The value of tool calling is threefold:

- **Accuracy.** The model can reach real data sources (database, file system, API) instead of relying on its parametric memory, which is bounded by the training cutoff.
- **Action.** The model can perform side effects (send an email, book a slot, cancel a subscription) instead of just describing them.
- **Auditability.** Every tool call is logged with its arguments and result, so a post-mortem can reconstruct exactly what the agent did.

### AI Agent: definition

> An AI Agent is a system that uses an LLM with tool calling to reach a goal, running multiple steps and adapting to results.

The three pieces - LLM, tools, loop - are necessary together. An LLM alone is a one-shot answerer; an LLM with tools but no loop is a single-step assistant; an LLM with a loop but no tools is a chain-of-thought generator. The agent is the combination.

---

## The agentic loop

Four phases, repeated until the goal is reached or an explicit cap is hit.

```
                ┌─────────────────────────────────┐
                │  user input + system prompt     │
                └────────────────┬────────────────┘
                                 ▼
                       ┌───────────────────┐
                       │   Plan  🧠         │   LLM decides next step
                       └─────────┬─────────┘
                                 ▼
                       ┌───────────────────┐
                       │   Act  🛠️         │   Tool is invoked
                       └─────────┬─────────┘
                                 ▼
                       ┌───────────────────┐
                       │   Observe  🧐     │   Result captured
                       └─────────┬─────────┘
                                 ▼
                       ┌───────────────────┐
                       │   Update  🔄      │   History appended; goal reached?
                       └─────────┬─────────┘
                                 ▼
                       goal? ──── no ──── loop back to Plan
                                 │
                                yes
                                 ▼
                         final answer
```

A concrete example from an e-commerce agent (the same shape used in module 04's deployment exercise):

```
user: "ship me the cheapest detergent"
agent:
  Plan:   "I need to find detergents, get their prices, pick the cheapest, ship it"
  Act:    find_product("detergent")
  Observe: [item_123: Persil 5L, item_456: Dixan 3L]
  Update: products are known
  Plan:   "compare prices"
  Act:    get_price(item_123); get_price(item_456)
  ...
  Plan:   "apply user discount and ship"
  Act:    apply_discount(user, item_456); add_shipping(user)
  Observe: total = €12.99
  final: "Detergent (item_456) will be shipped to Via Libertà 1 for €12.99"
```

The loop is **controlled iteration**. Three knobs:

1. The **goal** is encoded in the system prompt. A vague goal produces a meandering loop; a sharp goal terminates quickly.
2. The **tool catalogue** is the action space. A small, well-named catalogue is easier for the model to navigate than a large one with overlapping responsibilities.
3. The **iteration cap** is a hard upper bound on the number of Plan-Act-Observe rounds. Without it, a confused agent runs until you kill it.

### Where the loop breaks

Four failure modes show up repeatedly in practice. Each one corresponds to a control mechanism (next section).

| Failure | Example | Where it surfaces |
|---|---|---|
| **Tool error** | `divide(1, 0)` raises | Runtime exception propagates back |
| **Incomplete input** | User asks `"how much is 1 +"` with no second operand | Model has no enough info to call a tool |
| **Unstructured output** | Model emits JSON with wrong keys, prose around the JSON, etc. | Parser fails downstream |
| **Infinite loop** | Model keeps retrying the same failing call | Iteration cap is the only safety net |

---

## Controlling the loop

Four standard mechanisms. None of them is sufficient alone; they compose.

### 1. Retry policy

Reapply a failed action under a bounded, declarative policy: `max_attempts=N`, with optional backoff, and an explicit class of errors that trigger the retry (transport vs. semantic, see exercise 04 for the distinction).

```python
RetryPolicy(max_attempts=3, retry_on=ConnectionError)
```

Two flavours that often coexist:

- **Transport-level retry**: a transient network or transient tool error. Same call, same arguments, retried after a short pause.
- **Domain-level retry**: the result was structurally fine but semantically insufficient (e.g. evidence too thin). The retry runs the same step with a **reformulated** input.

Module 03 exercises 03 and 04 implement both flavours side by side; the distinction matters because the retry budget of one should not be consumed by the other.

### 2. Structured output

Force the model to emit a typed payload (JSON Schema, Pydantic) instead of free-form text. Two benefits:

- The output is **parseable** by deterministic code, not by a second LLM.
- The schema **constrains** the model's choices: if a field is a `Literal["TRUE", "FALSE", "UNVERIFIABLE"]`, the model has to pick one of three values, not produce a paragraph that approximately conveys the meaning.

Across the module 03 exercises, three patterns emerged on local Ollama models:

- **Optional fields with `null`** are an escape route. The model defaults to `null` when uncertain, leaving the workflow blind.
- **Required fields with a `"NONE"` sentinel** force an explicit decision per turn.
- **`Literal[...]` enums** are the safest typing: the model is forced to pick from a small, enumerated set, and the schema rejects anything else.

Exercise 06 went through three iterations on its episodic-memory extractor before settling on `Literal + NONE-sentinel + few-shot prompt`; the journey is documented in that notebook.

### 3. Error replay

When the loop fails, append the failing call, its arguments, and the error message back into the prompt for the next iteration. The model now sees what it tried, why it failed, and can reason about the next step instead of repeating the mistake.

```
[user]: how much is 1 / 0?
[agent calls]: divide(1, 0)
[tool error]: ZeroDivisionError
[append to prompt]: divide(1, 0) failed: ZeroDivisionError
[agent next turn]: "Division by zero is undefined. Could you provide a non-zero denominator?"
```

This is the inner mechanism the Reflexion paradigm generalises (covered in [03_paradigms_react_planexecute_reflexion.md](03_paradigms_react_planexecute_reflexion.md)).

### 4. Iteration cap

The simplest and most important control. A hard upper bound on the number of Plan-Act-Observe iterations - typically 5 to 10 - prevents a confused or pathological model from looping forever.

```python
for step in range(MAX_STEPS):
    message = call_llm(messages, tools)
    if not message.tool_calls:
        return message.content   # goal reached
    ...
return "[agent exceeded the iteration cap]"
```

The cap is *not* a graceful exit; it is a hard cutoff. The agent that hits the cap has failed. The right place to use the cap is detection (`hit the cap → log, alert`), not as a normal termination path.

---

## Workflows vs Pure Agents

The two extremes of a spectrum. Most production designs live somewhere in the middle.

### Workflow

A deterministic sequence of steps, written in Python (or a workflow engine), where the LLM is invoked only at chosen points. Anthropic's *Building effective agents* article calls this the *augmented LLM* end of the taxonomy.

```
user: "what's the weather today?"
workflow:
    step 1: extract city via LLM
    step 2 (if no city): ask user "which city?"
    step 3: call get_weather(city)
    step 4: phrase the answer via LLM
```

The control flow is in the **code**, not in the model. The model is asked specific narrow questions (extract a field, phrase an answer) and that is it.

**Pros**: predictable, testable, controllable. The same input always produces the same control flow. Errors are localised to a step. Auditability is trivial because every transition is in the code.

**Cons**: rigid. Adding a new capability often requires editing the dispatch. Not well-suited to fuzzy intent (e.g. *"compare these three things and tell me which I should buy"*).

### Pure Agent

The LLM decides every step. The system prompt declares the goal and the tools, the loop runs until the agent emits a terminal answer.

**Pros**: flexible, expressive. The system handles intents the engineer did not anticipate. Adding a tool is appending to a catalogue, not editing a dispatch ladder.

**Cons**: less predictable. The same input can take different paths on different runs. Debugging is reading message histories rather than reading code. Testing is asserting on the final answer rather than on intermediate transitions.

### The trade-off in one table

| Aspect | Workflow | Pure Agent |
|---|---|---|
| Control flow | Python | LLM |
| Determinism | High | Low (temperature, sampling) |
| Cost per request | 1-2 LLM calls | 3-N LLM calls |
| Testability | Assert on transitions | Assert on final output |
| Adding a tool | Edit dispatch ladder | Append to catalogue |
| Failure mode | Bug in the code | Confused reasoning |
| Best for | Fixed-shape tasks | Open-ended intent |

Module 03 exercises 01 and 02 build the same problem at both ends: a weather workflow with rule-based dispatch, then a translation + Wikipedia tool agent with LLM-driven dispatch. The trade-off is exactly the one in the table.

---

## Orchestration of agents

Once one agent works, the next step is composing several. An **orchestrator** is the component that decides which agent (or which workflow, or which tool) handles a given request.

```
user: "book a hotel in Pisa for next weekend, weather permitting"
   │
   ▼
 ┌─────────────────────────────────┐
 │ ORCHESTRATOR (LLM + system     │
 │  prompt + structured output)    │
 └────────┬────────────────────────┘
          │
          ├────► Weather Agent ────► is the weather acceptable?
          ├────► Booking Workflow ─► reserve the hotel
          └────► Payment Agent ────► confirm payment
```

The orchestrator is itself an LLM call (or a typed graph), with the structured output telling the runtime which downstream component to invoke. It is *not* a generic dispatcher: it has its own system prompt that describes the available downstream components and the conditions under which each one fires.

### Why not one big agent

Four concrete reasons (this is the angle slide 04 of the deck makes explicit):

1. **Specialisation**. A focused agent with a small system prompt and a small tool catalogue produces better results than one omnivorous agent with everything bolted on. The narrow scope is what lets the model reason cleanly.
2. **Permission control**. The orchestrator can refuse to route to an agent based on the user's role or context. A "delete subscription" agent can be gated to admins; a "send marketing email" agent to a specific team. Centralising the routing is what makes that policy enforceable.
3. **Scalability**. Adding a new capability is a new agent + an entry in the orchestrator's prompt, not a rewrite of the existing one.
4. **Logging and observability**. Every routing decision becomes a structured log line: `orchestrator: route → weather_agent (reason: …)`. The trace tells you not just *what* the agent did but *why this agent and not another*.

### The cost

An orchestrator adds one LLM call per request, on top of whatever the downstream agent does. For interactive systems the latency is the budget that matters; for batch systems the cost per call is. The right time to introduce orchestration is when at least one of the four reasons above starts to bite. Doing it pre-emptively for a system with one specialised task is over-engineering.

This is the territory module 04 (*Framework per l'Agentic AI*) makes explicit: LangGraph models the orchestrator as a typed graph node with conditional edges; CrewAI and AutoGen handle multi-agent setups natively. Cross-link: [04_frameworks.md](04_frameworks.md).

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Vague goal in system prompt | Agent meanders, ends with low-confidence answer | Sharpen the goal: define success in one sentence |
| Large overlapping tool catalogue | Model picks the wrong tool, or two redundant tools | Trim and split: one tool, one responsibility |
| Optional fields in structured output | Model returns `null` to avoid commitment | Make the field required with a `NONE` sentinel |
| No iteration cap | Confused agent loops forever | Hard cap at 5-10 iterations, log the breach |
| `Optional[str]` for an enum-like field | Model produces sentence-long values | Type as `Literal[...]` |
| Tool returns by raising an exception | Exception escapes the loop, breaks the conversation | Return `{"error": ...}` as data; let the model see it |
| Orchestrator with one downstream agent | One extra LLM call, no benefit | Skip orchestration until you have at least two distinct agents |
| Routing decisions only in logs | Hard to audit who got routed where | Put the routing decision in the structured output, persist it |
| Same model for orchestrator and downstream agents | Failure correlations | Consider a different model or sampling config for the orchestrator |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Fixed steps, deterministic behaviour | Workflow | Python in the middle, LLM at the edges |
| Many possible tool sequences, fuzzy intent | Pure Agent | The LLM is allowed to plan freely |
| Mixed: some deterministic core, some free-form output | Hybrid (workflow with an embedded agent step) | Best of both, slightly more code |
| Two or more distinct capabilities under one entry point | Orchestrator + specialised agents | Specialisation and permissioning matter |
| Strict latency budget | Workflow | One LLM call instead of N |
| Strict audit / compliance requirement | Workflow or orchestrator with structured-output routing | Every transition is logged |
| Prototype, fast iteration | Pure Agent | Catalogue + system prompt = working system |
| Long-running multi-step task with errors expected | Pure Agent with explicit retry policy and iteration cap | Loop survives transient failures |

---

## See also

- [02_agent_components.md](02_agent_components.md) — planning, memory, tool calling, structured output in depth
- [03_paradigms_react_planexecute_reflexion.md](03_paradigms_react_planexecute_reflexion.md) — ReAct, Plan-Execute, Reflexion and how they compose with the loop
- [04_frameworks.md](04_frameworks.md) — LangChain and LangGraph, where orchestration becomes a first-class graph
- [05_short_term_memory.md](05_short_term_memory.md) — trimming and summarisation of the conversation history
- [07_deployment.md](07_deployment.md) — wrapping an agent in an HTTP service with sessions, timeouts, container, secrets

### Exercises that exercise the concepts in this note

- [`01_ex_weather_agent_workflow_italian_cities.ipynb`](../exercises/01_ex_weather_agent_workflow_italian_cities.ipynb) — workflow with rule-based dispatch
- [`02_ex_translation_wikipedia_agent.ipynb`](../exercises/02_ex_translation_wikipedia_agent.ipynb) — pure agent with LLM-driven tool calling, agentic loop, retry handling
- [`03_ex_fact_checker_react_reflexion.ipynb`](../exercises/03_ex_fact_checker_react_reflexion.ipynb) — hand-rolled loop with structured output and Reflexion outer loop
- [`07_ex_shopassist_deployment.ipynb`](../exercises/07_ex_shopassist_deployment.ipynb) — the same shape wrapped into a deployable service
