# Agentic Frameworks: LangChain, LangGraph, and the Enterprise Stack

## TL;DR

An agentic framework is the boilerplate you don't write. The hand-rolled agentic loop (notes [01](01_agents_vs_workflows.md) and [02](02_agent_components.md)) is correct but expensive: tool parsing, retry, JSON repair, error handling, memory wiring, logging, token budget, guardrails. A framework wraps that recurring scaffolding into reusable primitives. The dominant choice in the open-source ecosystem is the **LangChain / LangGraph pair**: LangChain is the high-level declarative layer where everything is a `Runnable` and pipelines compose with `|`; LangGraph is the lower-level layer where the control flow is an **explicit typed graph** with state, conditional edges, cycles, retries, and human-in-the-loop. Use **LangChain** for ReAct-shaped agents with standard tools and linear flows; use **LangGraph** when you need cycles, branching, shared state, retries, or anything that has to ship to production. The two are not competitors: LangGraph builds on LangChain primitives (the same `ChatModel`, the same `@tool`, the same structured output), it just makes the orchestration first-class. The **cloud-native** alternatives (Google ADK, Microsoft Agent Framework) trade flexibility for tight integration with their respective clouds: managed runtime, native auth, observability, but vendor lock-in. The right pick is rarely "which framework is best" in the abstract; it is which one matches the infrastructure you already have.

## Cheatsheet

| Framework | Layer | Best for | One-line |
|---|---|---|---|
| **LangChain** | High-level declarative | ReAct agents, linear flows, prototyping | `agent = create_agent(model, tools, prompt)` |
| **LangGraph** | Low-level explicit graph | Cycles, branching, production workflows | `graph = StateGraph(MyState); graph.add_node(...)` |
| **LCEL** | Composition syntax | Chaining `Runnable`s with `|` | `chain = prompt | model | parser` |
| **`@tool`** | LangChain decorator | Python function → tool schema | One decorator, two lines |
| **`with_structured_output`** | Both | Force Pydantic-typed output | Schema-level constraint, not prompt-level |
| **Google ADK** | Cloud-native | Already on GCP, Gemini-first | `SequentialAgent`, `LoopAgent`, Vertex AI Engine |
| **Microsoft Agent Framework** | Cloud-native | Already on Azure, enterprise | Unifies AutoGen + Semantic Kernel; `ChatAgent` + threads |
| **CrewAI / OpenAI Agent SDK / Bedrock Agents** | Specialised | Multi-agent / minimal / serverless | Pick when your specific need maps to their primitive |

---

## Why frameworks at all

The hand-rolled loop (see exercises 02 and 03) looks short on paper:

```python
messages = [{"role": "system", "content": "You are a helpful assistant"}]
while True:
    response = llm.invoke(messages)
    if "tool_call" in response:
        result = call_tool(response["tool_call"]["name"], response["tool_call"]["arguments"])
        messages.append(response)
        messages.append({"role": "tool", "content": result})
    else:
        break
print(response["content"])
```

What this *does not* show is the boilerplate the production version has to handle on top:

- Tool error handling (timeout, exception, malformed result).
- Retries on transient LLM failures (rate limit, network).
- Robust JSON parsing (markdown fences, prose around the JSON, missing keys).
- Conversation memory (buffer vs database, summarisation, trimming).
- Token budgeting per turn and per session.
- Logging and tracing of every model call and every tool call.
- Guardrails on content (PII redaction, profanity, structured-output validation).
- Provider-specific quirks (OpenAI vs Anthropic vs Ollama tool-call formats).

A framework absorbs the recurring parts so the application code stays focused on what is actually unique to its use case. The same loop with a framework collapses to:

```python
agent = create_agent(model=model, tools=[get_weather], system_prompt="You are a helpful assistant")
agent.invoke({"messages": [{"role": "user", "content": "What is the weather in Rome?"}]})
```

The framework does NOT change the underlying paradigm. It encapsulates the recurring pattern.

### The two axes of framework choice

The differences across frameworks are not in *what* they offer but in two orthogonal axes:

| Axis | Range | Examples |
|---|---|---|
| **Abstraction level** | Declarative (high-level) ↔ Explicit graph (low-level) | LangChain ←→ LangGraph |
| **Ecosystem coupling** | Cloud-agnostic ↔ Cloud-native | LangChain/LangGraph/CrewAI ←→ Google ADK / Microsoft Agent Framework |

A high-level framework gets you running faster; a low-level one gives you more control when the runtime needs it. A cloud-agnostic framework keeps the option to switch providers; a cloud-native one buys deep integration with managed services at the cost of portability.

---

## LangChain: everything is a Runnable

The core abstraction is the **Runnable**: every component (prompt, model, tool, parser, chain) exposes the same interface - `invoke`, `stream`, `batch` - so they can be composed uniformly.

### LCEL (LangChain Expression Language)

The composition operator is `|`. The mental model is exactly Unix pipes for LLM components:

```python
chain = prompt | model | parser
result = chain.invoke({"input": "Explain agents"})
```

Four properties this gives you:

- **Declarative.** The pipeline is the structure; reading the code is reading the architecture.
- **Readable.** Each `|` step has one job.
- **Composable.** Any subset of the chain is itself a `Runnable` you can reuse.
- **Extendable.** Custom `Runnable`s slot in without subclassing anything.

### Model abstraction

LangChain hides the provider. Switching from Anthropic to OpenAI is changing a string:

```python
model = init_chat_model(
    "claude-sonnet-4-5-20250929",
    temperature=0.5,
    timeout=10,
    max_tokens=1000,
)
```

The same `init_chat_model` accepts `"gpt-4o-mini"`, `"ollama:qwen2.5:14b"`, and so on. The downstream chain is unchanged. This is the property module 03 exercise 04 used to keep the agent + Reflexion code identical across two backends.

### The `@tool` decorator

A function with a docstring + type hints becomes a tool schema in one line:

```python
@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b
```

LangChain reads the type hints and the docstring to build the JSON Schema the LLM sees. There is no separate schema definition step, no manual JSON to maintain. Two consequences worth knowing:

- The docstring is the tool description the model uses to *choose* the tool. Sentences-quality docstrings matter for dispatch quality.
- The type hints become the parameter schema. `Literal[...]` and Pydantic models flow through correctly; loose types like `str` give the model freedom to invent values.

### Structured output

Force the agent to reply with a Pydantic model (or a dataclass) instead of free prose:

```python
from dataclasses import dataclass
from langchain.agents.structured_output import ToolStrategy

@dataclass
class ResponseFormat:
    answer: str
    confidence: str | None = None

agent = create_agent(..., response_format=ToolStrategy(ResponseFormat))
# Output:  ResponseFormat(answer="Sunny!", confidence="high")
```

The mechanism uses tool calling under the hood: the model is forced to call a synthetic "respond" tool whose parameters are the response schema. Same model, same protocol, just a typed envelope on the output.

### ReAct and `create_agent`

LangChain's default agent is ReAct. The system prompt tells the model to think (Thought), choose a tool (Action), and observe (Observation); `create_agent` wires the loop. The application code does not see the loop - which is the abstraction's strength on simple agents and its weakness on complex ones.

```python
agent = create_agent(model=model, tools=[get_weather], system_prompt="You are a helpful assistant")
```

### Runtime context

Some tools need information about the runtime (current user, session id, organisation). `ToolRuntime` injects this without making it part of the tool's public parameter schema, so the LLM cannot accidentally specify or override it.

### LangSmith

The observability layer. Every model call and every tool call is captured: arguments, latency, cost, the full execution graph. LangSmith is what turns an agent in production from a black box into a debuggable system. Independent of LangChain in theory; tightly coupled in practice.

---

## LangGraph: the orchestration layer

LangChain handles single-shot or linear flows well. Real workflows are rarely linear: they have cycles (retry until the result is good enough), conditional branches (route based on intent), parallel branches, and shared state across nodes. **LangGraph** is the layer that makes those flows explicit.

```
                ┌──────────────┐
                │   START      │
                └──────┬───────┘
                       ▼
                ┌──────────────┐
                │  classify    │ ← reads state
                └──────┬───────┘
                       ▼
                if intent == "search":
                       │
                       ▼
                ┌──────────────┐
                │  search +     │
                │  answer       │
                └──────┬───────┘
                       ▼
                ┌──────────────┐
                │  evaluate     │
                └──────┬───────┘
                       │
                quality < 0.8?
                       │
                       ├─ yes ── back to search
                       │
                       └─ no  ──► END
```

### `StateGraph`: typed shared state

The central abstraction. Every node receives the current state and returns a partial update. The state is the **only** communication channel - no globals, no side effects.

```python
class AssistantState(TypedDict):
    messages: Annotated[list, operator.add]
    orders:   Annotated[list, operator.add]
    total:    Annotated[float, operator.add]
    step:     int
    done:     bool

graph = StateGraph(AssistantState)
```

`Annotated[..., operator.add]` is the reducer that says how multiple node updates to the same field combine. For lists it appends; for floats it sums; for scalars without a reducer the latest write wins.

### Building a graph

Three primitives: `add_node`, `add_edge`, `add_conditional_edges`.

```python
graph = StateGraph()
graph.add_node("llm",  llm_step)
graph.add_node("tool", tool_step)
graph.add_edge("llm", "tool")
graph.add_conditional_edges("tool", router)
app = graph.compile()
app.invoke({"input": "Analyze this document"})
```

The router function returns the next node's name as a plain Python string. Reading the graph is reading the routing logic; no hidden control flow inside an LLM's reasoning.

### Cycles

The thing LCEL cannot express. A node can route back to a previous node:

```python
def should_retry(state: MyState) -> str:
    if state["quality_score"] < 0.8:
        return "generate"   # cycle back
    return "end"

graph.add_node("generate", generate_fn)
graph.add_node("evaluate", evaluate_fn)
graph.add_conditional_edges("evaluate", should_retry)
```

This is exactly the Reflexion pattern (note [03](03_paradigms_react_planexecute_reflexion.md)): generate, evaluate, retry on low score. Without a graph runtime, you build this loop by hand.

> ⚠️ **Always set `max_iterations` or an explicit exit condition.** A cycle without a bound is an infinite loop waiting to happen. Module 03 exercise 04 hits this twice while tuning the verify-node threshold.

### Parallelism

Multiple nodes on independent branches can execute concurrently; LangGraph joins them automatically when the branches reconverge.

```
                node_1
                  │
            ┌─────┴─────┐
            ▼           ▼
         node_2      node_3
            │           │
            └─────┬─────┘
                  ▼
                node_4
```

Useful when two retrievals or two tool calls can be issued in parallel (different sources, different specialised agents).

### When LangGraph earns its cost

| Advantage | What it buys |
|---|---|
| Explicit, readable workflow | The graph is the documentation |
| Typed state | Reducers + TypedDict make data flow explicit |
| Native LangSmith integration | Trace every node, every state update |
| Memory, parallelism, cycles, multi-agent | First-class, not bolted on |

### The cost

- **Steeper learning curve** than LangChain.
- **State schema design is a skill.** Choosing what goes in the state and how reducers combine takes practice.
- **Debugging a wrong route or an infinite cycle is harder** than debugging a linear chain.
- **Overhead is excessive for simple tasks.** A single-shot ReAct agent should not have its own graph.

### Advanced features

- **Subgraphs.** A node can itself be a full graph. This is the mechanism for multi-agent systems: each agent is a subgraph, a supervisor graph routes among them.
- **Human-in-the-loop.** Native pause-resume support: a node can suspend execution, wait for a human approval / correction / choice, then continue. Critical for high-stakes actions (deletion, transfer, contract approval).

Module 03 exercise 04 builds the same fact-checker in both LangChain and LangGraph. The graph version's `should_retry` predicate is exactly the cycle pattern above; the typed `FactCheckerState` is exactly the shared-state pattern.

---

## LangChain vs LangGraph: same task, two tools

When to pick which one. The decision is rarely about which is "more powerful" - it is about what shape the problem actually has.

### What changes between the two

| Aspect | LangChain | LangGraph |
|---|---|---|
| Control flow | Implicit inside `create_agent` | Explicit in the graph |
| Readability | One-line agent factory | Each node is a function with a clear role |
| Adding a new behaviour | New tool or edit the system prompt | New node and new edge |
| Debugging | Read the message history | Inspect state at each node |
| Cycles | Indirect (system prompt) | First-class (`add_conditional_edges` back to a prior node) |
| Human-in-the-loop | Not directly | Native |
| Code volume | Less | More (typed state + node defs + edges) |

### When to use LangChain

- The task is a **ReAct agent with standard tools**.
- The flow is **linear**: no cycles, no branches, no parallel paths.
- **Prototyping speed** matters more than long-term maintainability.
- The system **will not** be touched by an ops team or auditor who needs to read the workflow.

### When to use LangGraph

- You need **cycles or conditional retry** (e.g. evaluate-and-retry loops).
- **Multiple nodes share state** and the dependencies between them need to be explicit.
- Workflow has **non-trivial branching**.
- The thing will **ship to production** and people other than its author need to understand it.
- You want **human-in-the-loop** at sensitive steps.

Both frameworks build on the same `Runnable` primitives, the same `@tool`, the same `with_structured_output`. Switching costs are low; pick the one whose abstraction matches the problem.

---

## The enterprise stack

The other axis of framework choice is whether you want **agnostic** (portable across clouds) or **native** (deep integration with one cloud). Three serious enterprise options live on the native end.

### Google ADK

A Python library optimised for Gemini on Vertex AI.

```python
agent = SequentialAgent(model="gemini-1.5-pro", steps=[step1, step2])
response = agent.run("Summarize this report")
```

Key features:

- **Code-first** in Python, TypeScript, Java, Go.
- **Vertex AI Agent Engine** as the managed runtime (fully hosted, no self-hosting needed).
- **Memory Service** for long-running sessions.
- **Built-in Developer UI** for local debugging and event inspection.
- **Two agent types**: *Workflow Agents* (`SequentialAgent`, `ParallelAgent`, `LoopAgent`) for deterministic orchestration; *LLM Agents* for autonomous routing.

Best when you are already on GCP, Gemini is acceptable as primary model, and you want a managed runtime.

### Microsoft Agent Framework

The October 2025 unification of Semantic Kernel and AutoGen. Both originals are now in maintenance.

```python
agent = Agent(model="gpt-4", tools=[calculator, search])
workflow = Workflow(agent)
result = workflow.run("Plan a business trip")
```

Key features:

- **`ChatAgent` + threads** as the central abstractions for conversation state.
- **Plugin / Tool model** that wraps any function, OpenAPI spec, or Microsoft Graph endpoint as a tool.
- **OpenTelemetry** integration for production observability.
- **Entra ID** for authentication, which matters in any corporate environment.
- **Azure AI Foundry** as the managed deployment target.

Best when the enterprise is already on Azure, governance and compliance matter, and integration with Microsoft Graph / Office is a requirement.

### Others worth knowing

- **OpenAI Agent SDK** - minimal loop + runner. Lighter than LangChain, fewer features; closer to primitives.
- **AWS Bedrock Agents** - serverless agents on Lambda with managed memory. Less customisation, very scalable.
- **CrewAI** - opinionated multi-agent orchestration with explicit roles and task decomposition. Powerful for collaborative agent scenarios; trade-off between power and complexity.

### Vendor lock-in: how to think about it

| You want this | Pick this |
|---|---|
| Native integration with existing GCP / Azure infrastructure | ADK / MAF |
| Compliance requirements satisfied by the cloud provider | ADK / MAF |
| Managed runtime, no self-hosting | ADK (Vertex AI Engine), MAF (Azure AI Foundry) |
| Model freedom, swap providers per task | LangChain / LangGraph |
| Portability across cloud providers | LangChain / LangGraph |
| Building a product that cannot depend on one vendor | LangChain / LangGraph |

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Treating `create_agent` as the only LangChain primitive | Stuck reaching for it on every problem | Use plain `Runnable`s for non-agentic flows |
| Building a graph in LangGraph for a one-shot task | Excess complexity, slower than needed | Use LangChain when the flow is linear |
| Cycle in LangGraph without a max-iteration | Infinite loop | Always cap iterations or have a terminating predicate |
| Mutating the state in place inside a node | Subtle bugs, lost updates | Return a partial dict; let the reducer combine |
| Skipping `Annotated[..., operator.add]` on a list field in state | Each node's update overwrites the previous list | Add the reducer explicitly |
| Tool docstrings as placeholders | Model picks the wrong tool | Treat the docstring as the dispatch hint |
| Cloud-native framework + cross-cloud requirement | Vendor lock-in shows up at the worst moment | Pick a cloud-native framework only if the cloud is the strategic decision |
| LangSmith disabled in production | Hard to debug a real incident | Wire it up early, use it for regression tests |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Single-shot tool use, prototype | LangChain `create_agent` | One line, ReAct built in |
| Multi-step with branching and cycles | LangGraph `StateGraph` | Cycles are first-class |
| Human approval needed on a sensitive action | LangGraph human-in-the-loop | Native pause/resume |
| Stateful multi-agent system | LangGraph subgraphs (or CrewAI) | Composable supervisor + agents |
| Already on Vertex AI, Gemini-first | Google ADK | Managed runtime + native integration |
| Already on Azure, governance heavy | Microsoft Agent Framework | Entra ID + OpenTelemetry + Foundry |
| Multi-cloud product | LangChain / LangGraph | Portability |
| Minimal serverless agent | AWS Bedrock Agents | Lambda integration |
| Tight team of multi-agent enthusiasts | CrewAI | Built specifically for that |

---

## See also

### Other notes
- [01_agents_vs_workflows.md](01_agents_vs_workflows.md) — what the framework wraps around
- [02_agent_components.md](02_agent_components.md) — primitives every framework exposes
- [03_paradigms_react_planexecute_reflexion.md](03_paradigms_react_planexecute_reflexion.md) — patterns that map cleanly onto LangGraph nodes and edges
- [05_short_term_memory.md](05_short_term_memory.md) — message-history strategies; both frameworks have native support
- [07_deployment.md](07_deployment.md) — wrapping a LangChain/LangGraph agent in an HTTP service

### Exercises that exercise the concepts in this note
- [`04_ex_fact_checker_langchain_vs_langgraph.ipynb`](../exercises/04_ex_fact_checker_langchain_vs_langgraph.ipynb) — same fact-checker in both frameworks, with a 300-word reasoned choice document at the end
- [`06_ex_customer_support_rag_cag_episodic.ipynb`](../exercises/06_ex_customer_support_rag_cag_episodic.ipynb) — `ChatOllama` + LangChain primitives + `with_structured_output` for episodic memory extraction
