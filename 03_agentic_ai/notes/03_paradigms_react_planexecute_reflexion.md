# Agentic Paradigms: ReAct, Plan-Execute, Reflexion

## TL;DR

An **agentic paradigm** is a pattern that says how the LLM should alternate **reasoning**, **action**, and **verification** to reach a goal. The choice of paradigm is the first big design decision after deciding to build an agent at all: it controls how many LLM calls you spend per question, how robust the system is to bad intermediate results, and how auditable the final answer is. Four families to know: **single-shot tool use** (one LLM call, one optional tool, fast and cheap), **ReAct** (interleave Reason / Act / Observe in a loop, no plan up front), **Plan-Execute** (write a full plan first, then run the steps in order, with optional re-planning), and **Reflexion** (after each attempt, an evaluator scores it and a self-reflector writes a lesson into memory; the actor retries with the lesson in context). The trade-off across these four is the same trade-off everywhere in agents: cost and latency on one axis, quality and robustness on the other. ReAct is the default for uncertain environments where tool results vary; Plan-Execute is the default for long structured business processes; Reflexion is what you reach for when the output is high-stakes or quality-sensitive (compliance text, code generation, fact-checking). The three compose: a Plan-Execute agent can use ReAct for each execution step, and Reflexion can wrap either of them.

## Cheatsheet

| Paradigm | One-line | LLM calls per task | Best for |
|---|---|---|---|
| **Single-shot / tool use** | One call, one optional tool | 1 (+ 1 if a tool fires) | Quick lookups, factual one-offs |
| **ReAct** | Reason → Act → Observe, repeat | N (one per Plan/Act/Observe round) | Uncertain environments, fuzzy intent |
| **Plan-Execute** | Plan all steps, then execute them | 1 (plan) + N (one per step) [+ replan] | Multi-step business processes |
| **Reflexion** | Try → Evaluate → Reflect → Retry | (try + evaluate + reflect) × K iterations | High-stakes outputs, quality-sensitive |
| **Actor / Evaluator / Self-Reflection** | The three roles inside Reflexion | One LLM call each per attempt | Same model, three system prompts |

---

## What is an "agentic paradigm"

A paradigm is an **orchestration pattern**: it tells the runtime in what order to alternate the agent's primitives (LLM call, tool call, evaluation, memory write). It does NOT prescribe a model, a framework, or a specific tool catalogue; it prescribes the *shape* of the loop around those primitives.

```
        ┌────────────────────────┐
        │   user question       │
        └────────────┬───────────┘
                     ▼
        ┌────────────────────────┐
        │  paradigm = pattern   │
        │  of decisions+actions │
        └────────────┬───────────┘
                     ▼
        ┌────────────────────────┐
        │       answer           │
        └────────────────────────┘
```

Choosing a paradigm is a trade-off across four axes:

| Axis | One LLM call | Loop with verification |
|---|---|---|
| **Quality** | Risk of fabrication | Higher, grounded in tool output |
| **Cost** | Low | High (N calls) |
| **Latency** | Low | High (sequential round-trips) |
| **Risk** | Low (cheap to retry) | Higher per-attempt cost |

The right paradigm is the one whose cost matches the stakes of getting it wrong.

---

## Single-shot / Tool use

The simplest paradigm. The LLM answers in one call, optionally invoking a single tool.

```
question ─► LLM ─► (optional) tool call ─► answer
```

Use when the user's intent is clear, the answer fits in one step, and the cost of being wrong is bounded (you can ask again, or the user can verify). This is the baseline; reach for anything richer only when this falls short.

---

## ReAct (Reason + Act)

The pattern that put agentic loops on the map. The agent alternates **reasoning** (a short chain-of-thought about what to do next), **acting** (calling a tool), and **observing** (reading the tool's result). The next reasoning step is conditioned on the latest observation.

```
       ┌────────────────────────────┐
       │   user question           │
       └──────────────┬─────────────┘
                      ▼
            ┌─────────────────┐
            │    🤔 Reason     │
            └────────┬────────┘
                     ▼
            ┌─────────────────┐
            │    🛠️ Act        │
            └────────┬────────┘
                     ▼
            ┌─────────────────┐
            │    👀 Observe    │
            └────────┬────────┘
                     ▼
            goal? ───── no ──── loop
                │
               yes
                ▼
          ✍️ finalize answer
                ▼
          💬 answer
```

### Worked example (verbatim from the deck)

> *"Find a vegetarian restaurant near the Duomo for 20:30."*

```
Reason: I need a list of restaurants + availability check
Action: search_restaurant()
Observe: [La foglia verde, Via Roma; Fairouz, Via Meravigli 12]
Reason: check availability for 20:30
Action: check_booking("la foglia verde", "20:30")
Observe: False
Reason: try the next one
Action: check_booking("fairouz", "20:30")
Observe: True
Reason: Fairouz at 20:30 is available
```

The key property is that every Reason step has access to every previous Observe. The agent does not commit to a plan up front; it reacts. This is what makes ReAct robust to tool failures and to environments where the model cannot predict in advance which call will work.

### When ReAct earns its cost

- The intent is clear but the tool results are unpredictable (search, prices, availability).
- The number of steps cannot be known in advance.
- Tool failures are common enough that recovering mid-loop matters.

### What ReAct costs

- **High token usage.** Every iteration sends the entire history (system prompt + all reasoning + all observations) back into the model.
- **High latency.** Each round-trip serialises.
- **Lower predictability than a plan-up-front approach.** Two runs on the same question may take different sequences of steps.

Mitigations: a hard iteration cap (5-10), per-step timeouts, and an explicit token budget per session. Module 03 exercise 03 builds a hand-rolled ReAct loop that exercises all of these guard-rails.

---

## Plan-Execute

Decouple **planning** from **execution**. A planner LLM proposes an ordered list of steps; an executor LLM (or sub-agent) runs them one by one, with tools at its disposal. After all steps run, an optional **re-planner** can revise the plan based on the results.

```
question ─► 🤔 Planner ─► [step 1, step 2, ..., step N]
                                  │
                                  ▼
                          🤖 Executor (one step at a time)
                                  │
                                  ▼
                          ┌─────────────────┐
                          │  results        │
                          └─────────┬───────┘
                                    ▼
                          🤔 Re-plan? ── yes ── back to executor
                                    │
                                   no
                                    ▼
                            💬 answer
```

### Worked example (verbatim from the deck)

> *"Request extra remote-work for next week."*

```
🤔 Planner output:
   1. Retrieve policy and requirements
   2. Call the API to verify the request
   3. Submit the request into the system
   4. Confirm and send a summary

🤖 Executor:
   step 1 → RAG over policy documents
   step 2 → tool: verify_request_api(...)
   step 3 → tool: create_request_api(...)
   step 4 → output: request_id = REQ-12345
```

The plan is **explicit**: the user (or an auditor) can read the four steps before any tool fires. This is exactly the property that ReAct lacks - and the reason Plan-Execute is the right choice for business processes that need oversight.

### Why split planning from execution

- **Auditability.** The plan is a structured artefact. You can show it, log it, ask for human approval before running, and inspect it post-hoc.
- **Model specialisation.** Planning can use a stronger model (slower, more expensive); execution can use a smaller one. Each step's contract is narrow enough that a cheaper model is often sufficient.
- **Reduced backtracking.** ReAct can paint itself into a corner where the next reasonable action contradicts an earlier one. Plan-Execute commits to a structure up front; only the re-planner can revise it.

### When Plan-Execute earns its cost

- Multi-step processes with dependencies (booking flows, HR workflows, regulated transactions).
- Tasks that need to be auditable.
- Long sequences where ReAct's roundtrips would compound.

### When NOT to use it

- Short or exploratory tasks where the overhead of a separate planning call is wasted.
- Highly dynamic environments where the plan would have to be revised after almost every step (the re-planner cost cancels the benefit).
- Tight token / time budgets.

Module 03 closes that loop by noting: a real fact-checker (exercise 03) is almost a Plan-Execute system in disguise - the system prompt encodes the plan, the ReAct loop executes it. Making the plan explicit in a dedicated planner call is the next step up.

---

## Reflexion

A self-improvement loop. After each attempt, an **evaluator** scores the output, and a **self-reflector** writes a verbal lesson that becomes input to the next attempt. The actor never sees its own raw mistakes; it sees the lesson learned from them.

```
                            ┌────────────────┐
                            │ user question  │
                            └────────┬───────┘
                                     ▼
                    ┌─────────────────────────────┐
                    │ 🤖 Actor                    │
                    │ produces trajectory         │
                    │ (actions + observations)    │
                    └──────────┬──────────────────┘
                               ▼
                    ┌─────────────────────────────┐
                    │ 📏 Evaluator                │
                    │ scores the trajectory       │
                    └──────────┬──────────────────┘
                               ▼
                    ┌─────────────────────────────┐
                    │ 🪞 Self-Reflection          │
                    │ writes a "lesson" to        │
                    │ long-term experience        │
                    └──────────┬──────────────────┘
                               ▼
                       satisfactory? ── yes ──► answer
                               │
                              no
                               ▼
                       loop back to Actor
                       (with experience injected)
```

Three roles, three different system prompts, often the same model weights:

| Role | Input | Output | Purpose |
|---|---|---|---|
| **Actor** | State, observations, long-term experience | Actions + new trajectory | Produce the answer |
| **Evaluator** | Trajectory | Reward score (0-1 or pass/fail) | Quantify how well the actor did |
| **Self-Reflection** | Reward + trajectory + prior experience | Verbal lesson written into experience | Teach the next attempt |

### Worked example (verbatim from the deck)

> *"Reply to a customer: formal tone, include disclaimer X, max 120 words."*

```
Attempt 1
  Actor:           writes a draft (170 words, missing disclaimer X)
  Trajectory:      prompt + draft + constraint check
  Evaluator:       reward = 0.3 / 1
  Self-Reflection: "verify checklist; enforce 120-word max"

Attempt 2
  Actor + Experience: writes a draft (110 words, disclaimer X included)
  Evaluator:          reward = 0.9 / 1
  → answer accepted
```

The reflection is written in **natural language** and stored in the long-term experience channel. The next attempt's actor sees `"verify checklist; enforce 120-word max"` in its context and behaves accordingly. The system gets better within a single session without any weight update.

### When Reflexion earns its cost

- The output is **high-stakes**: a wrong fact, an unprofessional tone, a missed compliance constraint has real consequences.
- The dimension of quality is **subjective enough that an evaluator LLM can judge it** (style, completeness, adherence to a checklist).
- The cost of iteration is acceptable: 3-5x the basic cost is fine when the alternative is a wrong outcome that costs real money to fix.

Module 03 exercise 03 builds Reflexion explicitly: a `Critique` schema with `quality_score`, `is_satisfactory`, `problems`, `suggestions`. The 7/10 threshold gate is exactly the `Evaluator → reward` step; the prompt enrichment with prior critiques is exactly the Self-Reflection step.

### When NOT to use it

- The cost per call is dominant (Reflexion at least doubles it).
- The task has an objective correctness check that does not need an LLM (use a unit test, a SQL query, a regex).
- The actor and evaluator share the same blind spots (same weights, correlated failures). Mitigation: different model for evaluator, or different sampling configuration.

---

## How the three compose

The paradigms are not mutually exclusive. The most flexible designs nest them.

| Combo | What it looks like | When |
|---|---|---|
| **ReAct inside Plan-Execute** | Planner emits steps; each step runs ReAct | Business process where each step is itself exploratory |
| **Reflexion around ReAct** | ReAct agent produces a trajectory; Reflexion critiques the whole thing | Fact-checking, code generation, customer-facing output |
| **Reflexion around Plan-Execute** | The whole plan is critiqued, not just individual steps | Complex workflows where the *plan itself* might be wrong |

The module 03 fact-checker (exercise 03) is the second of these: a ReAct agent wrapped in Reflexion. The Reflector evaluates the whole trajectory (which tools were called, how many sources, whether the verdict is well supported), not just the final string.

---

## Comparison

| | ReAct | Plan-Execute | Reflexion |
|---|---|---|---|
| **Plan visible up front** | No | Yes | Whatever the inner paradigm provides |
| **Reaction to tool results** | Per step | Only at re-plan boundaries | Same as inner paradigm |
| **Number of LLM calls** | N (one per round) | 1 plan + N steps + (replan?) | (try + eval + reflect) × K |
| **Auditability** | Trajectory readable post-hoc | Plan is a structured artefact | All trajectories + critiques persisted |
| **Best for** | Uncertain environments | Multi-step business processes | High-stakes outputs |
| **Typical failure mode** | Wanders, hits iteration cap | Plan too rigid for the actual situation | Score oscillation, ratcheting critic |
| **Hand-rolled in module 03** | Ex 02, 03 (inner loop), 06 | Plan implicit in system prompt of ex 06 | Ex 03 outer loop |

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| ReAct with no iteration cap | Loops forever on a confused intent | Hard cap at 5-10 iterations + log breaches |
| ReAct with overlapping tools | Model alternates between tools or picks the worse one | Trim catalogue, sharpen docstrings |
| Plan-Execute with vague planner prompt | Plan is too generic to execute | The planner gets its own structured-output schema (`steps: list[Step]`) |
| Plan-Execute with no re-planner | Plan goes stale when reality diverges | Insert a re-plan step after step N or on executor failure |
| Reflexion with same model, same temperature for Actor and Evaluator | Correlated failures, both miss the same bug | Different sampling config or different model for the evaluator |
| Reflexion with append-only experience | Memory grows; old lessons drown out new ones | Cap or summarise the experience channel |
| Reflexion with low-quality reward signal | Score oscillates between attempts, loop never converges | Average over K runs, or require two consecutive passes |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Quick fact lookup | Single-shot tool use | Cheapest path |
| Exploratory question, unknown tool sequence | ReAct | Loop reacts to each observation |
| Multi-step process with audit / approval | Plan-Execute | Explicit plan is the audit trail |
| High-stakes output (compliance, code, facts) | Reflexion | Iterative quality wins over speed |
| Long workflow where each step is itself fuzzy | Plan-Execute + ReAct per step | Outer structure + inner flexibility |
| Customer-facing text that must hit constraints | Reflexion | Self-critique against the checklist |
| Tight budget, simple task | Single-shot or workflow | Anything else is over-spending |

---

## See also

### Other notes
- [01_agents_vs_workflows.md](01_agents_vs_workflows.md) — workflow vs pure agent (the next level up)
- [02_agent_components.md](02_agent_components.md) — building blocks each paradigm orchestrates
- [04_frameworks.md](04_frameworks.md) — LangGraph models these paradigms as explicit graphs
- [05_short_term_memory.md](05_short_term_memory.md) — message-history strategies that compose with any paradigm
- [06_long_term_memory.md](06_long_term_memory.md) — where Reflexion's "experience" actually lives

### Exercises that exercise the concepts in this note
- [`02_ex_translation_wikipedia_agent.ipynb`](../exercises/02_ex_translation_wikipedia_agent.ipynb) — pure ReAct agent with two tools
- [`03_ex_fact_checker_react_reflexion.ipynb`](../exercises/03_ex_fact_checker_react_reflexion.ipynb) — ReAct + Reflexion stacked, with `Critique` schema and lesson-write loop
- [`04_ex_fact_checker_langchain_vs_langgraph.ipynb`](../exercises/04_ex_fact_checker_langchain_vs_langgraph.ipynb) — same fact-checker via framework primitives (LangChain create_agent uses an internal ReAct loop)
