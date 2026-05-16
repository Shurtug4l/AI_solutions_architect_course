# DigitServe v2 Agentic Fork — Design Spec

**Date:** 2026-05-16
**Author:** Simone La Porta
**Status:** Draft, pending user review
**Scope:** Module 03 (Agentic AI) capstone fork

## 1. Context

The current Module 03 capstone, `_PRJ_orchestrazione_agenti_servizi_digitali`, is a 36-node n8n workflow that orchestrates internal requests for a fictional digital services company (DigitServe S.r.l.). It pairs an LLM interpretation stage with a deterministic rule-based decision engine and five simulated executors (ticket, CRM, notification, report, analysis), with a human-approval gate on sensitive cases and a structured audit trail keyed by `correlation_id`.

The original is deliberately conservative on agentic depth: interpretation is a one-shot LLM call, the "decision agent" is not really an agent (pure rules, chosen for inspectability and zero cost), and the executors are monolithic. None of Module 03's three signature agentic paradigms (ReAct, Plan-Execute, Reflexion) are demonstrated end-to-end.

This document specifies a **fork** of the project that keeps the original frozen as a reference and adds an upgraded variant which exercises all three paradigms plus a self-critiquing interpretation step, while preserving the same domain, dual-provider LLM setup, audit posture, and single-JSON deliverable form.

## 2. Goals and non-goals

### Goals
1. Demonstrate, in one importable n8n workflow, a coherent end-to-end agentic loop: interpret with self-critique, plan, execute via ReAct, reflect, and optionally re-plan.
2. Make the demonstration earned, not labelled: ReAct must compose multiple fine-grained tool calls per step, the planner must produce a structured plan with dependencies, the critic must produce lessons that change future planner behaviour.
3. Persist Reflexion lessons across executions so the cross-run "learning" loop is visible.
4. Keep the deliverable to a single `.json` file importable into n8n, consistent with the module convention.

### Non-goals
- LLM output-quality evaluation. We assert structure and behaviour, not phrasing quality.
- Replacing the simulated executors with real integrations. Production swap is documented but not implemented.
- A code-based implementation (LangGraph or similar) alongside the n8n version. Explicitly out of scope per the substrate decision below.
- Real concurrency safety on the lesson store. The deliverable assumes single-instance n8n with sequential executions; concurrent-write semantics are documented as a known limitation.

## 3. Constraints

- **Deliverable:** one `.json` workflow file, importable in n8n without external services other than the LLM provider.
- **LLM substrate:** dual provider, Ollama by default (privacy-first, local) and OpenAI as opt-in via payload field. Mirrors the original.
- **Loop substrate:** pure n8n. ReAct and Reflexion iterations live inside Code nodes (JavaScript), not as recursive sub-workflow calls. Trade-off accepted in section 9.
- **Language:** all sticky notes, node descriptions, prompts, response payloads, and audit strings are in English. The original Italian artifact remains the legacy reference.
- **No external storage:** Reflexion memory persists in n8n's `$workflow.staticData`, which lives in the n8n instance database. The JSON export stays free of run-time state.

## 4. File layout

```
03_agentic_ai/
├── _PRJ_orchestrazione_agenti_servizi_digitali/             (original, frozen)
│   └── PRJ_orchestrazione_agenti_servizi_digitali.json
└── _PRJ_orchestrazione_agenti_servizi_digitali_v2_agentic/  (this work)
    └── PRJ_orchestrazione_agenti_servizi_digitali_v2_agentic.json
```

- Folder uses the underscore prefix to match the original.
- The `_v2_agentic` suffix signals intent without renaming the domain.
- Workflow `name` field inside the JSON: `DigitServe v2 — Plan / ReAct / Reflexion`.

## 5. Architecture

### 5.1 Top-level flow

```
Webhook (POST /digitserve-v2-richiesta)
  │
[A] Normalize input + assign correlation_id
[B] Configure provider (ollama default, openai opt-in)
[C] Load Reflexion memory  ←─── reads $workflow.staticData
  │
─── Stage 1: Interpretation with self-critique ───
[1a] LLM Interpret → structured JSON (intent, entities, urgency, sensitivity, confidence)
[1b] LLM Critique → {accept | refine_hints}
[1c] If refine_hints, second Interpret pass with hints (max 1 retry)
[1d] Abstain branch when confidence < τ (τ = 0.6, tunable): skip planner, respond "needs human triage"
  │
─── Stage 2: Plan-Execute planner ───
[2a] LLM Planner (input: interpretation + top-K relevant past lessons)
     output: ordered steps with deps + per-step requires_approval flag
[2b] Plan validator (JSON schema + DAG sanity)
  │
─── Stage 3: Approval gate (plan-level) ───
[3] IF any step.requires_approval → Send & Wait email
    rejected → audit + respond
    approved/auto → continue
  │
─── Stage 4: ReAct executors (one Code-node loop per plan step) ───
[4] Split steps → for each step:
    Code node runs ReAct loop:
       loop (max N=5):
          LLM reason → choose tool from catalog → call tool → observe → maybe stop
       returns step outcome + step trace
  │
─── Stage 5: Reflexion critic ───
[5a] LLM Critic reviews plan + execution traces → {success | partial | failed} + lessons[]
[5b] If failed AND replans_remaining > 0 → loop back to [2a] with critic's feedback
[5c] Persist lessons to $workflow.staticData (capped ring buffer, last 50)
  │
─── Stage 6: Aggregate and respond ───
[6a] Build run summary
[6b] Append audit log row (HTTP request to mock audit sink, X-Correlation-Id header)
[6c] Respond to Webhook (sync)
```

### 5.2 Where iteration actually happens

The workflow is a pure DAG outside three places:

- `[1c]` interpretation refinement: at most one re-call, gated by an IF node. Not really a loop.
- `[4]` ReAct per step: bounded loop inside a single Code node (JS), at most 5 turns per step.
- `[5b]` Reflexion replan: at most one re-plan per run, gated by an IF node with `replans_remaining` counter.

Constraining iteration to these three points is intentional. It is the smallest set that lets all four patterns earn their keep while keeping the canvas readable.

## 6. Run state and audit

### 6.1 Run object

Carried node-to-node via `includeOtherFields: true` on Set nodes. Single shared shape:

```jsonc
{
  "correlation_id": "<execId>-<ms>",
  "received_at": "ISO-8601",
  "channel": "form | email | chat",
  "sender": { "name", "role", "email" },
  "text": "<normalized>",
  "provider": "ollama | openai",
  "model": "<name>",
  "budget": {
    "llm_calls_remaining": 20,
    "react_turns_remaining_per_step": 5,
    "interpret_refines_remaining": 1,
    "replans_remaining": 1
  },
  "interpretation": { "intent", "entities", "urgency", "sensitivity", "confidence", "raw" },
  "plan": { "steps": [ { "id", "action", "args_hints", "depends_on", "requires_approval" } ], "rationale" },
  "execution": [ { "step_id", "trace": [ ... ], "mutations": [ ... ], "outcome" } ],
  "reflexion": { "verdict", "lessons": [ ... ] },
  "audit": { "events": [ { "stage", "t_ms", "summary", "llm_calls_used", "tools_used" } ] }
}
```

`audit.events[]` is the canonical run trace. The response returns it verbatim, so the caller can debug without n8n-side log access.

### 6.2 Reflexion lesson store

Path: `$workflow.staticData.global.reflexion_store`. Schema:

```jsonc
{
  "version": 1,
  "lessons": [
    {
      "id": "L-<uuid>",
      "created_at": "ISO-8601",
      "intent": "<e.g., ticket_open>",
      "tier": "<e.g., gold>",
      "tags": [ "<keyword>", ... ],
      "rule": "<one-sentence prescriptive lesson>",
      "evidence_correlation_id": "<id>",
      "confidence": 0.0..1.0,
      "uses": 0,
      "successes": 0
    }
  ]
}
```

- Capacity: 50 lessons. Ring buffer eviction on overflow, dropping the lesson with the lowest `confidence × max(uses, 1) × recency`.
- Retrieval (planner side): top-K = 3 by `tag_overlap × 0.6 + confidence × 0.3 + recency × 0.1`. No embeddings; tag overlap is enough at this scale and avoids pulling in a vector backend that would break the single-JSON constraint.
- Writes: only the consolidation Code node after Stage 5b mutates `staticData`. Reads happen at the start of every run in `[C]`.

### 6.3 Audit sink

Same pattern as the original: HTTP Request to a configured audit endpoint with the full `audit.events[]` payload and the `X-Correlation-Id` header. Failure to reach the sink is recorded in the response but does not fail the workflow. Production hardening (real endpoint, retry queue, mTLS) is documented in a closing sticky note, not baked in.

## 7. Tool catalog

Twelve tools, exposed inside each ReAct Code node as local JavaScript functions, plus a JSON-schema description list that the LLM sees as part of the system prompt.

| # | Name | Kind | Purpose | Args | Returns |
|---|------|------|---------|------|---------|
| 1 | `lookup_customer` | read | Resolve sender to a customer record. | `{ email }` | `{ id, tier, region, open_tickets }` |
| 2 | `fetch_request_history` | read | Last N requests from this sender. | `{ email, limit=5 }` | `[ { id, intent, outcome, at } ]` |
| 3 | `get_sla` | read | SLA target for tier and intent. | `{ tier, intent }` | `{ response_minutes, resolve_minutes }` |
| 4 | `check_open_tickets` | read | Existing open tickets that may collide. | `{ customer_id, intent }` | `[ { ticket_id, status, age_min } ]` |
| 5 | `dedup_check` | read | Deterministic Jaccard similarity vs recent tickets. | `{ text, window_hours=24 }` | `{ is_duplicate, score, of_ticket_id? }` |
| 6 | `assess_urgency` | read | Rule-based urgency score (tier + SLA + keywords). | `{ tier, intent, text, sla }` | `{ level, score, reasons[] }` |
| 7 | `draft_ticket` | read | LLM-drafted title and body (no creation). | `{ intent, text, urgency }` | `{ title, body, suggested_assignee }` |
| 8 | `create_ticket` | write | Materialize a ticket. ID prefix `TKT-`. | `{ title, body, urgency, assignee, customer_id }` | `{ ticket_id, status: "open" }` |
| 9 | `update_crm` | write | Log a CRM event. ID prefix `EVT-`. | `{ customer_id, kind, payload }` | `{ event_id }` |
| 10 | `send_notification` | write | Notify a channel or email. ID prefix `NTF-`. | `{ audience, channel, subject, body }` | `{ notification_id }` |
| 11 | `schedule_report` | write | Queue a deferred report. ID prefix `RPT-`. | `{ kind, due_at, payload }` | `{ report_id }` |
| 12 | `enqueue_analysis` | write | Push to analysis backlog. ID prefix `AUD-`. | `{ topic, severity, payload }` | `{ analysis_id }` |

Plus one meta-action emitted by the agent to stop the loop:

- `finish({ summary, status })` — terminates the ReAct loop and returns the step outcome.

### 7.1 Behaviour notes

- Reads are pure and idempotent. Writes append to a per-run `mutations[]` array returned with the step outcome.
- Generated entity IDs follow the format `<PREFIX>-<correlation_id_short>-<seq>`, where `correlation_id_short` is the last 8 chars of the run's `correlation_id` and `seq` is a per-tool monotonic counter scoped to the run. Example: `TKT-1a2b3c4d-01`. The prefix discriminates the tool that emitted the ID (`TKT`, `EVT`, `NTF`, `RPT`, `AUD`); the suffix makes IDs traceable back to the originating execution without coordinating an external sequence.
- All tool implementations live in JavaScript inside the ReAct Code node. No external HTTP calls. The only network calls in the loop are LLM calls via `$helpers.httpRequest`.
- Failure injection is deterministic, seeded by `correlation_id`:
  - `lookup_customer` returns `not_found` for unknown senders.
  - `dedup_check` returns `is_duplicate: true` for a curated test input (used by T2 and T5).
  - `create_ticket` returns `conflict` when `check_open_tickets` has not been called first for the same `customer_id`. This is the mechanism that turns Reflexion into a useful pattern rather than a label.
- Total per-step turn budget: max 5 LLM-driven turns. Total per-run LLM-call cap: 20.

### 7.2 Why this catalog

- Splitting `draft_ticket` from `create_ticket` and `check_open_tickets` from `create_ticket` is what gives ReAct real composition work. Without those splits, a single-call planner would dominate and ReAct would degenerate into one tool call per step.
- The forced `check_open_tickets` precondition on `create_ticket` is the smallest failure mode that produces a generalizable lesson on the first failed run. Once the critic emits "always check open tickets before create_ticket on this intent", subsequent runs of the same intent skip the failure altogether. That is the pedagogical payoff of cross-run memory in a single demo.
- Keeping all writes inside the Code node preserves the single-JSON deliverable and the simulation stance of the original. Production swap is one HTTP Request per write tool, documented but not implemented.

## 8. Budgets and error handling

### 8.1 Budgets

| Budget | Cap | Enforced where | On exceed |
|---|---|---|---|
| Total LLM calls per run | 20 | Decremented inside each HTTP node calling the provider | Short-circuit to `budget_exceeded` branch, partial run returned |
| ReAct turns per step | 5 | Inside ReAct Code node loop | Force `finish({ status: "incomplete" })`, lesson candidate emitted |
| Interpretation refines | 1 | Stage 1 IF node | Proceed with confidence-flagged interpretation |
| Reflexion replans | 1 | Stage 5b IF node | Accept current outcome, mark verdict `partial` |
| Per-LLM-call timeout | 30 s | HTTP node `options.timeout` | Caught by Error Trigger sub-flow |
| Total wall-clock per run | 180 s | Workflow `executionTimeout` | n8n native termination, audit row `aborted` |

### 8.2 Cap rationale

The LLM-call cap of 20 was chosen to envelope a *typical* successful run, not a pathological one. A normal end-to-end pass costs roughly 1 interpret + 1 plan + 1 critic + about 3 turns across 2-3 plan steps, which lands near 12-14 calls; an occasional refine or a shallow replan still fits. Runs that trigger a deep replan with full execution twice will trip the cap, which is the intended outcome: budget exhaustion is a first-class termination state (`budget_exceeded` short-circuit, partial run returned to the caller) rather than an error. The single replan limit reflects an empirical observation about Reflexion: cycling more than once on the same input rarely converges and tends to oscillate between two flawed plans. The 5-turn per-step ReAct budget covers the canonical chain `lookup → check → draft → create → notify` with one slot for in-step recovery, matching the failure injection in section 7.1.

### 8.3 Error handling posture

n8n native: every LLM HTTP node has `continueOnFail: true`. After each LLM call a `Validate response` Code node parses the JSON. On parse failure, one retry with a stricter system prompt ("output JSON only, no prose"). Second failure produces a structured `{ ok: false, reason, raw }` item that flows down the normal path under the same budgets. No try-catch theatrics: failures are first-class data in the trace.

A workflow-level `Error Trigger` sub-flow catches unhandled errors (mostly expression failures or provider unreachable). It writes a final audit row and responds with HTTP 500 plus the `correlation_id` so the caller can locate the trace.

## 9. Substrate trade-off: why Code-node loops over alternatives

Four substrate options were considered:

1. **Pure n8n, Code-node loops** — chosen.
2. **Pure n8n, recursive sub-workflow loops** — every ReAct turn becomes its own n8n execution, maximally inspectable but produces a multi-workflow export, which breaks the single-JSON deliverable.
3. **Hybrid (n8n + Python agent service)** — clean separation of concerns, but ships code outside the JSON file. Rejected for the same reason.
4. **Port the fork to LangGraph** — cleanest agent code, but changes the project's identity from "orchestration capstone" to "code-first agent app", and produces no n8n artifact.

Code-node loops keep everything inside one importable JSON. The cost is that ReAct iterations happen inside JavaScript and are not individually visible on the n8n canvas. The mitigation is the structured `trace[]` returned per step: every turn is recorded with reasoning, tool call, and observation, surfaced in `audit.events[]` and returned in the response. Inspectability is moved from the canvas to the response payload, which is an acceptable trade-off for this deliverable.

## 10. Testing strategy

No automated harness inside the JSON. Deliverables for verification are curated payloads in a sticky note plus three inspection Code nodes off the main path, exercised manually via n8n's "Execute Node".

### 10.1 Scenario matrix

| # | Scenario | What it exercises | Expected trace signature |
|---|---|---|---|
| T1 | Silver customer, simple ticket | Baseline happy path | `interpret(1) → critique:accept → plan(1 step) → react(≤3 turns) → reflexion:success`. No refine, no replan. |
| T2 | Gold customer, dedup + create + notify | Multi-step plan with deps; ReAct composition | Plan has ≥3 steps with `depends_on`. Step traces include `dedup_check → lookup_customer → check_open_tickets → create_ticket → send_notification`. |
| T3 | Key-account, sensitive intent | Plan-level approval gate | At least one `plan.steps[*].requires_approval === true`. Approval branch `approved` taken. Verdict `success`. |
| T4 | Approval rejected | Rejection branch, no writes | `mutations[]` empty across all steps. Response `status: "rejected_by_human"`. |
| T5 | Forced tool failure | In-step recovery via ReAct | `create_ticket` returns `conflict`, agent recovers within turn budget by calling `check_open_tickets` and retrying. No replan. |
| T6 | Reflexion replan | Cross-stage critic loop | Two plan blocks in `audit.events`. `replans_remaining === 0`. New lesson with `tags ⊇ { missing_lookup }`. |
| T7 | Cross-run lesson reuse | Lesson primes future planning | Re-fire T6 input with a new `correlation_id`. Planner audit row includes the T6 lesson text. New plan starts with `lookup_customer`. No replan. Lesson `uses` incremented. |
| T8 | Low-confidence abstain + budget exhaustion | Abstain branch and budget short-circuit | Ambiguous input: `interpretation.confidence < τ`, response `status: "needs_human_triage"`. Forced-loop input: `budget_exceeded` short-circuit with partial run. |

### 10.2 Inspection primitives

A `Sticky group "Self-checks"` containing three Code nodes, all off the main path:

1. `assert_trace(case_id, run_json)` — compares `audit.events[]` against the expected sequence for `case_id`. Returns `{ passed, mismatches[] }`.
2. `assert_mutations(case_id, run_json)` — checks `mutations[]` cardinality and ID prefixes.
3. `assert_lesson_store(expected_tags[])` — reads `$workflow.staticData.global.reflexion_store` and verifies a lesson with the expected tags exists.

These are inspection helpers, not gates. They are not on the request path.

### 10.3 Sticky-note deliverables inside the workflow JSON

- `Sticky — Test cases`: full payload JSON for T1 through T8 with one-line intent and the expected trace summary.
- `Sticky — How to run`: `curl` invocation skeleton, env-var hint for the Ollama URL, instruction to reset `staticData` between cold runs.

### 10.4 What this does not test

- LLM output phrasing quality. Asserted: structure, tool sequencing, budget compliance, lesson persistence.
- Wall-clock performance. n8n execution time varies with Ollama load; we cap, we do not benchmark.
- Concurrent runs against the same lesson store. `staticData` writes are not atomic across parallel executions; single-instance sequential usage is assumed.

## 11. Justification log

Per the project's authorial-voice requirement, the meaningful choices and their alternatives:

| Choice | Alternatives considered | Reason for the pick |
|---|---|---|
| All four patterns: critique-interp + plan + ReAct + Reflexion | Subset (e.g., only plan + ReAct) | The user's explicit selection. The four compose into a single coherent loop where each pattern produces a signal the next consumes; partial picks would leave the critic without a planner to influence or the planner without a critic to learn from. |
| Decomposed 12-tool catalog | Keep 5 monolithic executors | Without decomposition, ReAct degenerates to "pick one tool, call, finish", which is not ReAct. Decomposition adds nodes but is the only way the pattern earns its keep. |
| Code-node loops | Sub-workflow loops, hybrid Python service, LangGraph port | Single-JSON deliverable constraint. Trade-off compensated by structured `trace[]` in the response. See section 9. |
| Cross-run lesson persistence | In-run replanning only | The user's explicit selection. Persistence is what makes Reflexion's "learning" angle visible in a demo; in-run replanning alone is hard to distinguish from a retry. |
| `$workflow.staticData` for lesson store | External JSONL file, SQLite, vector DB | Single-JSON constraint. staticData is n8n-native, survives across executions, and is not part of the exported JSON, so the deliverable stays clean. |
| Plan-level approval (not per-action) | Keep per-action approval as in original | Once a plan is the unit, the gate should be on the plan. Per-action approval would fragment the human's view of the proposed work. |
| Deterministic failure injection seeded by `correlation_id` | Random failures, no failures | Reproducibility. Lessons learned by the critic only generalize if the same input deterministically reproduces the failure across runs T6 and T7. |
| Tag-overlap retrieval, no embeddings | Vector similarity over lesson rules | 50-lesson cap means tag overlap is sufficient and avoids embedding the lesson store into a vector index that would not survive JSON export. |
| Manual verification via curated payloads | Automated test harness in CI | This is an n8n workflow, not a code module. The natural driver is n8n's Executions panel; a CI harness would belong in module 06. |
| 5 turns per step, 20 LLM calls per run, 1 replan | Looser caps | Envelopes the worst-case successful run with a small margin. Looser caps hide cost rather than control it. |

## 12. Open items and future work

- **Real integrations.** Each write tool maps cleanly to an HTTP Request; production swap is documented in a closing sticky note.
- **Concurrent-write safety on the lesson store.** Single-instance sequential usage is assumed. A future version could move the store to Redis or Postgres and acquire a lock around the consolidation step.
- **LLM-as-judge eval for output phrasing.** Out of scope here; natural fit for a module 06 extension where eval harnesses are introduced.
- **Parallel ReAct execution for independent plan steps.** Considered as Approach 3, dropped for canvas readability. Could be added as an optional branch later if the deliverable rewards concurrency.
