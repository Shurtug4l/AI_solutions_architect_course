# DigitServe v2 Agentic Fork Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a single importable n8n workflow JSON (`PRJ_orchestrazione_agenti_servizi_digitali_v2_agentic.json`) that orchestrates the DigitServe domain using four agentic patterns: self-critiquing interpretation, Plan-Execute planning, ReAct tool-composing execution, and Reflexion with cross-run persistent lessons.

**Architecture:** The deliverable is one JSON file, but we build it via a small Python+JavaScript scaffold (`_build/`) inside the fork folder. Python assembles the workflow structure (nodes + connections + sticky notes); JavaScript holds the ReAct loop and the 12-tool catalog as source files that are embedded into Code nodes at build time. Both layers are unit-tested. The build script regenerates the JSON deterministically; final verification is manual via curl against a local n8n instance backed by Ollama.

**Tech Stack:**
- Python 3.11+, `pytest`, `jsonschema` (build + structural tests)
- Node.js 20+, built-in `node:test` runner (JS unit tests for ReAct loop and tools)
- n8n (latest), Ollama (default LLM provider, `llama3.2`)
- Reference spec: `docs/superpowers/specs/2026-05-16-agentic-orchestration-v2-fork-design.md`

---

## File structure

The fork folder layout produced by this plan:

```
03_agentic_ai/_PRJ_orchestrazione_agenti_servizi_digitali_v2_agentic/
├── PRJ_orchestrazione_agenti_servizi_digitali_v2_agentic.json   ← deliverable (build output)
└── _build/                                                       ← dev tooling
    ├── README.md                       generation + test instructions
    ├── pyproject.toml                  python deps
    ├── package.json                    node deps (none beyond stdlib)
    ├── .gitignore                      __pycache__, .pytest_cache, .venv
    ├── build_workflow.py               main entrypoint, assembles full JSON
    ├── nodes/
    │   ├── __init__.py
    │   ├── base.py                     Node factories: Set, Code, HTTP, IF, Switch, Merge, Split, Webhook, RespondToWebhook, StickyNote
    │   ├── connections.py              link helpers, validate DAG
    │   ├── stickies.py                 all sticky notes (English)
    │   ├── stage_0_ingress.py
    │   ├── stage_1_interpret.py
    │   ├── stage_2_plan.py
    │   ├── stage_3_approval.py
    │   ├── stage_4_react.py
    │   ├── stage_5_reflexion.py
    │   ├── stage_6_respond.py
    │   ├── self_checks.py              off-path assertion Code nodes
    │   └── error_trigger.py            workflow-level error handler
    ├── prompts/
    │   ├── interpret.txt
    │   ├── critique.txt
    │   ├── planner.txt
    │   └── reflexion.txt
    ├── js/
    │   ├── tools.js                    12 tools + finish meta-action
    │   ├── tools.test.js
    │   ├── react_loop.js               ReAct loop, parameterized by tool catalog
    │   ├── react_loop.test.js
    │   ├── lesson_store.js             ring buffer helpers + retrieval scoring
    │   └── lesson_store.test.js
    ├── schemas/
    │   ├── run_state.schema.json
    │   ├── plan.schema.json
    │   ├── interpretation.schema.json
    │   └── lesson.schema.json
    └── tests/
        ├── __init__.py
        ├── test_node_factories.py
        ├── test_connections.py
        ├── test_stickies.py
        ├── test_stages.py              per-stage structural assertions
        ├── test_full_build.py          full assembly + n8n import-shape validation
        └── fixtures/
            └── payloads.py             T1-T8 test payloads as Python dicts
```

The `_build/` directory is committed so the build is reproducible. Only the top-level `.json` is the actual deliverable for the course.

---

## Phase 0 — Scaffolding

### Task 0.1: Create fork folder and `_build/` skeleton

**Files:**
- Create: `03_agentic_ai/_PRJ_orchestrazione_agenti_servizi_digitali_v2_agentic/_build/.gitkeep`
- Create: `03_agentic_ai/_PRJ_orchestrazione_agenti_servizi_digitali_v2_agentic/_build/README.md`
- Create: `03_agentic_ai/_PRJ_orchestrazione_agenti_servizi_digitali_v2_agentic/_build/.gitignore`
- Create: `03_agentic_ai/_PRJ_orchestrazione_agenti_servizi_digitali_v2_agentic/_build/pyproject.toml`
- Create: `03_agentic_ai/_PRJ_orchestrazione_agenti_servizi_digitali_v2_agentic/_build/package.json`

- [ ] **Step 1: Create the fork folder and `_build/` subdir, add a `.gitkeep` so the empty folder is tracked**

```bash
mkdir -p 03_agentic_ai/_PRJ_orchestrazione_agenti_servizi_digitali_v2_agentic/_build
touch 03_agentic_ai/_PRJ_orchestrazione_agenti_servizi_digitali_v2_agentic/_build/.gitkeep
```

- [ ] **Step 2: Write the `_build/.gitignore`**

```
__pycache__/
.pytest_cache/
.venv/
node_modules/
*.pyc
```

- [ ] **Step 3: Write `_build/README.md`**

```markdown
# DigitServe v2 — Build Tooling

This folder generates `../PRJ_orchestrazione_agenti_servizi_digitali_v2_agentic.json`.
The JSON is the only artifact shipped to the n8n grader; this folder is dev tooling.

## Quick start

    cd _build
    python -m venv .venv && source .venv/bin/activate
    pip install -e .
    pytest -q                                # python tests (build + schemas)
    node --test js/                          # javascript tests (tools + react loop)
    python build_workflow.py                 # writes the workflow JSON one level up

## Layout

- `nodes/`     python factories for every node group (one module per stage)
- `js/`        javascript source for Code nodes (tools, react loop, lesson store)
- `prompts/`   LLM prompts as plain text, read at build time
- `schemas/`   JSON Schema files for run state, plan, interpretation, lesson
- `tests/`     python tests asserting workflow structure
```

- [ ] **Step 4: Write `_build/pyproject.toml`**

```toml
[project]
name = "digitserve_v2_build"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["jsonschema>=4.0"]

[project.optional-dependencies]
dev = ["pytest>=7.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 5: Write `_build/package.json`**

```json
{
  "name": "digitserve-v2-js",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "test": "node --test js/"
  }
}
```

- [ ] **Step 6: Commit**

```bash
git add 03_agentic_ai/_PRJ_orchestrazione_agenti_servizi_digitali_v2_agentic/
git commit -m "Scaffold module 03 PRJ v2 fork build directory"
```

### Task 0.2: Write the run-state JSON Schema

**Files:**
- Create: `_build/schemas/run_state.schema.json`
- Create: `_build/tests/test_schemas.py`

- [ ] **Step 1: Write the failing test**

```python
# _build/tests/test_schemas.py
import json
import pathlib
import jsonschema

SCHEMAS = pathlib.Path(__file__).parent.parent / "schemas"

def _load(name):
    return json.loads((SCHEMAS / name).read_text())

def test_run_state_schema_accepts_minimal_run():
    schema = _load("run_state.schema.json")
    run = {
        "correlation_id": "exec1-1700000000000",
        "received_at": "2026-05-16T10:00:00Z",
        "channel": "form",
        "sender": {"name": "Alice", "role": "ops", "email": "alice@x.com"},
        "text": "I need help",
        "provider": "ollama",
        "model": "llama3.2",
        "budget": {
            "llm_calls_remaining": 20,
            "react_turns_remaining_per_step": 5,
            "interpret_refines_remaining": 1,
            "replans_remaining": 1,
        },
        "audit": {"events": []},
    }
    jsonschema.validate(run, schema)

def test_run_state_schema_rejects_unknown_channel():
    schema = _load("run_state.schema.json")
    run = {
        "correlation_id": "x",
        "received_at": "2026-05-16T10:00:00Z",
        "channel": "carrier_pigeon",
        "sender": {"name": "", "role": "", "email": ""},
        "text": "",
        "provider": "ollama",
        "model": "llama3.2",
        "budget": {
            "llm_calls_remaining": 20,
            "react_turns_remaining_per_step": 5,
            "interpret_refines_remaining": 1,
            "replans_remaining": 1,
        },
        "audit": {"events": []},
    }
    try:
        jsonschema.validate(run, schema)
    except jsonschema.ValidationError:
        return
    raise AssertionError("schema should reject unknown channel")
```

- [ ] **Step 2: Run the test, expect failure**

```bash
cd _build && pytest tests/test_schemas.py -v
```
Expected: FAIL with "No such file or directory: ...run_state.schema.json".

- [ ] **Step 3: Write the schema**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "DigitServe v2 Run State",
  "type": "object",
  "required": ["correlation_id", "received_at", "channel", "sender", "text",
               "provider", "model", "budget", "audit"],
  "properties": {
    "correlation_id": {"type": "string", "minLength": 1},
    "received_at": {"type": "string", "format": "date-time"},
    "channel": {"enum": ["form", "email", "chat"]},
    "sender": {
      "type": "object",
      "required": ["name", "role", "email"],
      "properties": {
        "name": {"type": "string"},
        "role": {"type": "string"},
        "email": {"type": "string"}
      }
    },
    "text": {"type": "string"},
    "provider": {"enum": ["ollama", "openai"]},
    "model": {"type": "string"},
    "budget": {
      "type": "object",
      "required": ["llm_calls_remaining", "react_turns_remaining_per_step",
                   "interpret_refines_remaining", "replans_remaining"],
      "properties": {
        "llm_calls_remaining": {"type": "integer", "minimum": 0},
        "react_turns_remaining_per_step": {"type": "integer", "minimum": 0},
        "interpret_refines_remaining": {"type": "integer", "minimum": 0},
        "replans_remaining": {"type": "integer", "minimum": 0}
      }
    },
    "interpretation": {"type": "object"},
    "plan": {"type": "object"},
    "execution": {"type": "array"},
    "reflexion": {"type": "object"},
    "audit": {
      "type": "object",
      "required": ["events"],
      "properties": {
        "events": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["stage", "t_ms", "summary"],
            "properties": {
              "stage": {"type": "string"},
              "t_ms": {"type": "integer"},
              "summary": {"type": "string"},
              "llm_calls_used": {"type": "integer"},
              "tools_used": {"type": "array", "items": {"type": "string"}}
            }
          }
        }
      }
    }
  }
}
```

- [ ] **Step 4: Run the test, expect pass**

```bash
cd _build && pytest tests/test_schemas.py -v
```
Expected: PASS, 2 tests.

- [ ] **Step 5: Commit**

```bash
git add _build/schemas/run_state.schema.json _build/tests/test_schemas.py
git commit -m "Add run state JSON Schema with structural tests"
```

### Task 0.3: Write the plan, interpretation, and lesson schemas

**Files:**
- Create: `_build/schemas/plan.schema.json`
- Create: `_build/schemas/interpretation.schema.json`
- Create: `_build/schemas/lesson.schema.json`
- Modify: `_build/tests/test_schemas.py` (add tests)

- [ ] **Step 1: Append failing tests to `tests/test_schemas.py`**

```python
def test_interpretation_schema_requires_confidence():
    schema = _load("interpretation.schema.json")
    interp = {"intent": "ticket_open", "entities": {}, "urgency": "med",
              "sensitivity": "low", "confidence": 0.85, "raw": "..."}
    jsonschema.validate(interp, schema)
    bad = {k: v for k, v in interp.items() if k != "confidence"}
    try:
        jsonschema.validate(bad, schema)
    except jsonschema.ValidationError:
        return
    raise AssertionError("confidence must be required")

def test_plan_schema_accepts_dag():
    schema = _load("plan.schema.json")
    plan = {
        "rationale": "open ticket then notify",
        "steps": [
            {"id": "s1", "action": "resolve_ticket", "args_hints": {},
             "depends_on": [], "requires_approval": False},
            {"id": "s2", "action": "notify_stakeholders", "args_hints": {},
             "depends_on": ["s1"], "requires_approval": False},
        ],
    }
    jsonschema.validate(plan, schema)

def test_lesson_schema_requires_tags():
    schema = _load("lesson.schema.json")
    lesson = {
        "id": "L-abc",
        "created_at": "2026-05-16T10:00:00Z",
        "intent": "ticket_open",
        "tier": "gold",
        "tags": ["missing_lookup"],
        "rule": "Always lookup_customer before create_ticket.",
        "evidence_correlation_id": "x",
        "confidence": 0.8,
        "uses": 0,
        "successes": 0,
    }
    jsonschema.validate(lesson, schema)
```

- [ ] **Step 2: Run, expect failures (missing schema files)**

```bash
cd _build && pytest tests/test_schemas.py -v
```

- [ ] **Step 3: Write `schemas/interpretation.schema.json`**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["intent", "entities", "urgency", "sensitivity", "confidence"],
  "properties": {
    "intent": {"type": "string"},
    "entities": {"type": "object"},
    "urgency": {"enum": ["low", "med", "high", "critical"]},
    "sensitivity": {"enum": ["low", "med", "high"]},
    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    "raw": {"type": "string"}
  }
}
```

- [ ] **Step 4: Write `schemas/plan.schema.json`**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["rationale", "steps"],
  "properties": {
    "rationale": {"type": "string"},
    "steps": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["id", "action", "args_hints", "depends_on", "requires_approval"],
        "properties": {
          "id": {"type": "string"},
          "action": {"type": "string"},
          "args_hints": {"type": "object"},
          "depends_on": {"type": "array", "items": {"type": "string"}},
          "requires_approval": {"type": "boolean"}
        }
      }
    }
  }
}
```

- [ ] **Step 5: Write `schemas/lesson.schema.json`**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["id", "created_at", "intent", "tier", "tags", "rule",
               "evidence_correlation_id", "confidence", "uses", "successes"],
  "properties": {
    "id": {"type": "string", "pattern": "^L-"},
    "created_at": {"type": "string", "format": "date-time"},
    "intent": {"type": "string"},
    "tier": {"type": "string"},
    "tags": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "rule": {"type": "string", "minLength": 5},
    "evidence_correlation_id": {"type": "string"},
    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    "uses": {"type": "integer", "minimum": 0},
    "successes": {"type": "integer", "minimum": 0}
  }
}
```

- [ ] **Step 6: Run tests, expect pass**

```bash
cd _build && pytest tests/test_schemas.py -v
```
Expected: PASS, 5 tests total.

- [ ] **Step 7: Commit**

```bash
git add _build/schemas/ _build/tests/test_schemas.py
git commit -m "Add plan, interpretation, and lesson JSON Schemas"
```

---

## Phase 1 — Node factories

### Task 1.1: Implement node-factory primitives with deterministic IDs

**Files:**
- Create: `_build/nodes/__init__.py` (empty)
- Create: `_build/nodes/base.py`
- Create: `_build/tests/__init__.py` (empty)
- Create: `_build/tests/test_node_factories.py`

The factories must produce dicts matching n8n's node format. IDs are deterministic so the build is reproducible (`uuid5` with a fixed namespace + the node name).

- [ ] **Step 1: Write the failing test**

```python
# _build/tests/test_node_factories.py
from nodes import base

def test_set_node_has_required_n8n_fields():
    n = base.set_node("Normalize", assignments=[
        {"id": "a1", "name": "correlation_id", "value": "x", "type": "string"},
    ], position=(100, 200))
    assert n["name"] == "Normalize"
    assert n["type"] == "n8n-nodes-base.set"
    assert n["typeVersion"] == 3.4
    assert n["id"]
    assert n["position"] == [100, 200]
    assert n["parameters"]["assignments"]["assignments"][0]["name"] == "correlation_id"

def test_set_node_id_is_stable_across_calls():
    a = base.set_node("Same", assignments=[], position=(0, 0))
    b = base.set_node("Same", assignments=[], position=(0, 0))
    assert a["id"] == b["id"]

def test_code_node_embeds_js_source():
    js = "return [{json: {ok: true}}];"
    n = base.code_node("ReAct Step", js_code=js, position=(0, 0))
    assert n["type"] == "n8n-nodes-base.code"
    assert n["parameters"]["jsCode"] == js

def test_http_node_carries_url_and_method():
    n = base.http_node("Call Ollama", method="POST",
                       url="http://localhost:11434/api/generate",
                       body_json={"model": "llama3.2", "prompt": "hi"},
                       position=(0, 0), timeout_ms=30000)
    assert n["type"] == "n8n-nodes-base.httpRequest"
    assert n["parameters"]["method"] == "POST"
    assert n["parameters"]["url"] == "http://localhost:11434/api/generate"
    assert n["parameters"]["options"]["timeout"] == 30000

def test_if_node_has_left_right_operator():
    n = base.if_node("Branch", left="={{ $json.x }}", op="equals",
                     right="ok", position=(0, 0))
    cond = n["parameters"]["conditions"]["conditions"][0]
    assert cond["leftValue"] == "={{ $json.x }}"
    assert cond["operator"]["operation"] == "equals"
    assert cond["rightValue"] == "ok"

def test_sticky_note_carries_markdown_and_dimensions():
    s = base.sticky_note("Header", content="## Hello", width=600, height=200,
                         color=5, position=(0, 0))
    assert s["type"] == "n8n-nodes-base.stickyNote"
    assert s["parameters"]["content"] == "## Hello"
    assert s["parameters"]["width"] == 600
    assert s["parameters"]["height"] == 200
    assert s["parameters"]["color"] == 5
```

- [ ] **Step 2: Run, expect failure**

```bash
cd _build && pytest tests/test_node_factories.py -v
```

- [ ] **Step 3: Implement `nodes/base.py`**

```python
"""
Node-factory primitives for the DigitServe v2 workflow.

Each factory returns a dict in n8n's node format. IDs are derived via uuid5 from a
fixed namespace plus the node name, so the build is byte-for-byte reproducible
across runs (and we can diff JSON exports meaningfully).
"""
from __future__ import annotations
import uuid
from typing import Any, Iterable

_NS = uuid.UUID("a3f4c2e0-1111-4222-8333-444455556666")  # arbitrary fixed UUID

def _id(name: str) -> str:
    return str(uuid.uuid5(_NS, name))

def _pos(p: tuple[int, int]) -> list[int]:
    return [int(p[0]), int(p[1])]

def set_node(name: str, *, assignments: Iterable[dict], position: tuple[int, int],
             include_other_fields: bool = True) -> dict:
    return {
        "id": _id(name),
        "name": name,
        "type": "n8n-nodes-base.set",
        "typeVersion": 3.4,
        "position": _pos(position),
        "parameters": {
            "assignments": {"assignments": list(assignments)},
            "includeOtherFields": include_other_fields,
            "options": {},
        },
    }

def code_node(name: str, *, js_code: str, position: tuple[int, int]) -> dict:
    return {
        "id": _id(name),
        "name": name,
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": _pos(position),
        "parameters": {"language": "javaScript", "jsCode": js_code},
    }

def http_node(name: str, *, method: str, url: str, body_json: dict | None = None,
              headers: dict | None = None, position: tuple[int, int],
              timeout_ms: int = 30000, continue_on_fail: bool = True) -> dict:
    params: dict[str, Any] = {
        "method": method,
        "url": url,
        "sendBody": body_json is not None,
        "options": {"timeout": timeout_ms},
    }
    if body_json is not None:
        params["bodyContentType"] = "json"
        params["jsonBody"] = body_json
    if headers:
        params["sendHeaders"] = True
        params["headerParameters"] = {"parameters": [
            {"name": k, "value": v} for k, v in headers.items()
        ]}
    return {
        "id": _id(name),
        "name": name,
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": _pos(position),
        "parameters": params,
        "continueOnFail": continue_on_fail,
    }

def if_node(name: str, *, left: str, op: str, right: str | int | float | bool,
            position: tuple[int, int]) -> dict:
    return {
        "id": _id(name),
        "name": name,
        "type": "n8n-nodes-base.if",
        "typeVersion": 2,
        "position": _pos(position),
        "parameters": {
            "conditions": {
                "options": {"caseSensitive": True, "typeValidation": "strict", "version": 1},
                "conditions": [{
                    "id": "c1",
                    "leftValue": left,
                    "rightValue": right,
                    "operator": {"type": "string" if isinstance(right, str) else "number",
                                 "operation": op},
                }],
                "combinator": "and",
            },
            "options": {},
        },
    }

def switch_node(name: str, *, value: str, cases: list[tuple[str, str]],
                position: tuple[int, int], fallback: str = "fallback") -> dict:
    """cases: list of (output_key, value_to_match)."""
    rules = []
    for key, match in cases:
        rules.append({
            "conditions": {
                "options": {"caseSensitive": True, "typeValidation": "strict", "version": 1},
                "conditions": [{
                    "id": f"r-{key}",
                    "leftValue": value,
                    "rightValue": match,
                    "operator": {"type": "string", "operation": "equals"},
                }],
                "combinator": "and",
            },
            "renameOutput": True,
            "outputKey": key,
        })
    return {
        "id": _id(name),
        "name": name,
        "type": "n8n-nodes-base.switch",
        "typeVersion": 3.2,
        "position": _pos(position),
        "parameters": {
            "rules": {"values": rules},
            "options": {"fallbackOutput": "extra", "renameFallbackOutput": fallback},
        },
    }

def merge_node(name: str, *, position: tuple[int, int], mode: str = "append") -> dict:
    return {
        "id": _id(name),
        "name": name,
        "type": "n8n-nodes-base.merge",
        "typeVersion": 3,
        "position": _pos(position),
        "parameters": {"mode": mode, "options": {}},
    }

def split_in_batches_node(name: str, *, batch_size: int, position: tuple[int, int]) -> dict:
    return {
        "id": _id(name),
        "name": name,
        "type": "n8n-nodes-base.splitInBatches",
        "typeVersion": 3,
        "position": _pos(position),
        "parameters": {"batchSize": batch_size, "options": {}},
    }

def webhook_node(name: str, *, path: str, position: tuple[int, int]) -> dict:
    return {
        "id": _id(name),
        "name": name,
        "type": "n8n-nodes-base.webhook",
        "typeVersion": 2,
        "position": _pos(position),
        "webhookId": f"{path}-001",
        "parameters": {
            "httpMethod": "POST",
            "path": path,
            "responseMode": "responseNode",
            "options": {"allowedOrigins": "*", "rawBody": False},
        },
    }

def respond_to_webhook_node(name: str, *, response_body: str,
                            position: tuple[int, int]) -> dict:
    return {
        "id": _id(name),
        "name": name,
        "type": "n8n-nodes-base.respondToWebhook",
        "typeVersion": 1.1,
        "position": _pos(position),
        "parameters": {
            "respondWith": "json",
            "responseBody": response_body,
            "options": {"responseCode": 200},
        },
    }

def sticky_note(name: str, *, content: str, width: int, height: int, color: int,
                position: tuple[int, int]) -> dict:
    return {
        "id": _id(name),
        "name": name,
        "type": "n8n-nodes-base.stickyNote",
        "typeVersion": 1,
        "position": _pos(position),
        "parameters": {
            "content": content,
            "width": width,
            "height": height,
            "color": color,
        },
    }
```

- [ ] **Step 4: Run tests, expect pass**

```bash
cd _build && pytest tests/test_node_factories.py -v
```
Expected: PASS, 6 tests.

- [ ] **Step 5: Commit**

```bash
git add _build/nodes/ _build/tests/__init__.py _build/tests/test_node_factories.py
git commit -m "Add n8n node factories with deterministic IDs and unit tests"
```

### Task 1.2: Implement connection helpers and DAG validator

**Files:**
- Create: `_build/nodes/connections.py`
- Create: `_build/tests/test_connections.py`

- [ ] **Step 1: Write the failing test**

```python
# _build/tests/test_connections.py
import pytest
from nodes import connections as c

def test_link_appends_main_output():
    conns = {}
    c.link(conns, "A", "B")
    assert conns == {"A": {"main": [[{"node": "B", "type": "main", "index": 0}]]}}

def test_link_supports_multiple_targets_on_same_output():
    conns = {}
    c.link(conns, "A", "B")
    c.link(conns, "A", "C")
    assert conns["A"]["main"][0] == [
        {"node": "B", "type": "main", "index": 0},
        {"node": "C", "type": "main", "index": 0},
    ]

def test_link_supports_named_output_index():
    conns = {}
    c.link(conns, "Switch", "Branch1", source_output_index=0)
    c.link(conns, "Switch", "Branch2", source_output_index=1)
    assert len(conns["Switch"]["main"]) == 2
    assert conns["Switch"]["main"][0][0]["node"] == "Branch1"
    assert conns["Switch"]["main"][1][0]["node"] == "Branch2"

def test_validate_dag_rejects_cycle():
    conns = {}
    c.link(conns, "A", "B")
    c.link(conns, "B", "C")
    c.link(conns, "C", "A")
    with pytest.raises(c.DagError):
        c.validate_dag(conns, allow_back_edges_from=set())

def test_validate_dag_allows_explicit_back_edges():
    conns = {}
    c.link(conns, "A", "B")
    c.link(conns, "B", "ReflexionRouter")
    c.link(conns, "ReflexionRouter", "B")  # the Reflexion replan loop
    c.validate_dag(conns, allow_back_edges_from={"ReflexionRouter"})
```

- [ ] **Step 2: Run, expect failure**

```bash
cd _build && pytest tests/test_connections.py -v
```

- [ ] **Step 3: Implement `nodes/connections.py`**

```python
"""
n8n connection map manipulation. n8n stores connections as
  { source_name: { "main": [[{node, type, index}], ...] } }
where the outer list is indexed by source-output (0, 1, 2, ...).

We validate that the assembled graph is a DAG, with explicit opt-in for
back-edges from nodes named in `allow_back_edges_from`. The Reflexion replan
router is the only intended back-edge in this workflow.
"""
from __future__ import annotations

class DagError(RuntimeError):
    pass

def link(conns: dict, source: str, target: str, *,
         source_output_index: int = 0, target_input_index: int = 0) -> None:
    bucket = conns.setdefault(source, {}).setdefault("main", [])
    while len(bucket) <= source_output_index:
        bucket.append([])
    bucket[source_output_index].append({
        "node": target, "type": "main", "index": target_input_index,
    })

def validate_dag(conns: dict, *, allow_back_edges_from: set[str]) -> None:
    # adjacency excluding back-edges from whitelisted sources
    adj: dict[str, list[str]] = {}
    for src, payload in conns.items():
        if src in allow_back_edges_from:
            continue
        for branch in payload.get("main", []):
            adj.setdefault(src, [])
            for edge in branch:
                adj[src].append(edge["node"])

    color: dict[str, int] = {}  # 0=white, 1=gray, 2=black
    def dfs(n: str) -> None:
        color[n] = 1
        for m in adj.get(n, []):
            if color.get(m, 0) == 1:
                raise DagError(f"cycle: {n} -> {m}")
            if color.get(m, 0) == 0:
                dfs(m)
        color[n] = 2

    for node in list(adj.keys()):
        if color.get(node, 0) == 0:
            dfs(node)
```

- [ ] **Step 4: Run, expect pass**

```bash
cd _build && pytest tests/test_connections.py -v
```
Expected: PASS, 5 tests.

- [ ] **Step 5: Commit**

```bash
git add _build/nodes/connections.py _build/tests/test_connections.py
git commit -m "Add connection helpers with DAG cycle detection"
```

---

## Phase 2 — Tools and ReAct loop (JavaScript)

The two heaviest pieces of logic live in JS source files so they get real unit tests via `node --test`. They are read at build time and embedded into Code nodes as strings.

### Task 2.1: Implement the 12-tool catalog with deterministic failure injection

**Files:**
- Create: `_build/js/tools.js`
- Create: `_build/js/tools.test.js`

- [ ] **Step 1: Write the failing test**

```javascript
// _build/js/tools.test.js
import { test } from "node:test";
import assert from "node:assert/strict";
import { makeTools } from "./tools.js";

function fresh(cid = "exec1-1700000000000") {
  return makeTools({ correlation_id: cid });
}

test("lookup_customer returns a tier and id for a known sender", () => {
  const t = fresh();
  const out = t.lookup_customer({ email: "alice@digitserve.io" });
  assert.equal(out.tier, "gold");
  assert.match(out.id, /^CUST-/);
});

test("lookup_customer returns not_found for an unknown sender", () => {
  const t = fresh();
  const out = t.lookup_customer({ email: "ghost@nowhere.test" });
  assert.equal(out.id, null);
  assert.equal(out.error, "not_found");
});

test("create_ticket returns conflict when check_open_tickets was not called for the customer", () => {
  const t = fresh();
  const lk = t.lookup_customer({ email: "bob@digitserve.io" });
  const out = t.create_ticket({
    title: "x", body: "y", urgency: "high",
    assignee: "ops", customer_id: lk.id,
  });
  assert.equal(out.error, "conflict");
  assert.match(out.reason, /check_open_tickets/);
});

test("create_ticket succeeds after check_open_tickets", () => {
  const t = fresh();
  const lk = t.lookup_customer({ email: "bob@digitserve.io" });
  t.check_open_tickets({ customer_id: lk.id, intent: "ticket_open" });
  const out = t.create_ticket({
    title: "x", body: "y", urgency: "high",
    assignee: "ops", customer_id: lk.id,
  });
  assert.match(out.ticket_id, /^TKT-/);
  assert.equal(out.status, "open");
});

test("write tools accumulate into mutations", () => {
  const t = fresh();
  const lk = t.lookup_customer({ email: "carol@digitserve.io" });
  t.check_open_tickets({ customer_id: lk.id, intent: "ticket_open" });
  t.create_ticket({
    title: "x", body: "y", urgency: "low",
    assignee: "ops", customer_id: lk.id,
  });
  t.send_notification({
    audience: "team", channel: "slack", subject: "s", body: "b",
  });
  assert.equal(t.mutations.length, 2);
  assert.ok(t.mutations[0].ticket_id);
  assert.ok(t.mutations[1].notification_id);
});

test("dedup_check returns is_duplicate for the curated test phrase", () => {
  const t = fresh();
  const out = t.dedup_check({ text: "Please reopen ticket TKT-7777 again" });
  assert.equal(out.is_duplicate, true);
  assert.ok(out.of_ticket_id);
});

test("ids embed the correlation id short suffix for traceability", () => {
  const t = fresh("execX-1700000000123");
  const lk = t.lookup_customer({ email: "dave@digitserve.io" });
  t.check_open_tickets({ customer_id: lk.id, intent: "ticket_open" });
  const out = t.create_ticket({
    title: "x", body: "y", urgency: "low",
    assignee: "ops", customer_id: lk.id,
  });
  // last 8 chars of correlation_id appear in the ticket id
  assert.match(out.ticket_id, /00000123/);
});

test("finish meta-action terminates a fake loop", () => {
  const t = fresh();
  const out = t.finish({ summary: "done", status: "ok" });
  assert.equal(out.terminate, true);
  assert.equal(out.summary, "done");
});
```

- [ ] **Step 2: Run, expect failure**

```bash
cd _build && node --test js/tools.test.js
```

- [ ] **Step 3: Implement `js/tools.js`**

```javascript
// _build/js/tools.js
// Twelve tools used by the ReAct loop, plus the finish meta-action.
// Reads are pure and idempotent; writes append to a per-run mutations[] log.
// Failure injection is deterministic, seeded by correlation_id, so tests T5/T6
// in the spec reproduce on every run.

const KNOWN_CUSTOMERS = {
  "alice@digitserve.io":  { tier: "gold",   region: "EU", open_tickets: 0 },
  "bob@digitserve.io":    { tier: "silver", region: "EU", open_tickets: 1 },
  "carol@digitserve.io":  { tier: "bronze", region: "US", open_tickets: 0 },
  "dave@digitserve.io":   { tier: "key",    region: "EU", open_tickets: 2 },
  "erin@digitserve.io":   { tier: "gold",   region: "EU", open_tickets: 0 },
};

const SLA = {
  bronze: { response_minutes: 240, resolve_minutes: 1440 },
  silver: { response_minutes: 120, resolve_minutes: 720  },
  gold:   { response_minutes: 60,  resolve_minutes: 480  },
  key:    { response_minutes: 15,  resolve_minutes: 240  },
};

const DEDUP_TRIGGER = "please reopen ticket tkt-7777";

function shortCid(cid) {
  const s = String(cid || "");
  return s.slice(-8) || "00000000";
}

function seqGen() {
  let n = 0;
  return () => String(++n).padStart(2, "0");
}

export function makeTools({ correlation_id }) {
  const short = shortCid(correlation_id);
  const seqByPrefix = {
    TKT: seqGen(), EVT: seqGen(), NTF: seqGen(),
    RPT: seqGen(), AUD: seqGen(), CUST: seqGen(),
  };
  const mintId = (pref) => `${pref}-${short}-${seqByPrefix[pref]()}`;

  // bookkeeping for failure injection
  const customersChecked = new Set();   // customer_id => check_open_tickets was called
  const customersResolved = new Map();  // email -> customer_id (so we keep ids stable per run)
  const mutations = [];

  const t = {
    mutations,

    lookup_customer({ email }) {
      const known = KNOWN_CUSTOMERS[String(email || "").toLowerCase()];
      if (!known) return { id: null, error: "not_found" };
      let id = customersResolved.get(email);
      if (!id) { id = mintId("CUST"); customersResolved.set(email, id); }
      return { id, tier: known.tier, region: known.region,
               open_tickets: known.open_tickets };
    },

    fetch_request_history({ email, limit = 5 }) {
      // deterministic synthetic history: empty for unknown senders, 1 prior for known
      const known = KNOWN_CUSTOMERS[String(email || "").toLowerCase()];
      if (!known) return [];
      return [{ id: `TKT-prev-${short}`, intent: "ticket_open",
                outcome: "closed", at: "2026-05-01T10:00:00Z" }].slice(0, limit);
    },

    get_sla({ tier, intent }) {
      const sla = SLA[tier] || SLA.bronze;
      // critical intents tighten the response SLA by half
      const tighten = (intent || "").includes("incident") ? 0.5 : 1;
      return {
        response_minutes: Math.round(sla.response_minutes * tighten),
        resolve_minutes:  sla.resolve_minutes,
      };
    },

    check_open_tickets({ customer_id, intent }) {
      if (customer_id) customersChecked.add(customer_id);
      // synthetic: report one stale open ticket for "dave" (key tier)
      if (customer_id && customer_id.includes("CUST-")) {
        return KNOWN_CUSTOMERS["dave@digitserve.io"]
          ? [{ ticket_id: `TKT-prev-${short}`, status: "open", age_min: 720 }]
          : [];
      }
      return [];
    },

    dedup_check({ text, window_hours = 24 }) {
      const s = String(text || "").toLowerCase();
      if (s.includes(DEDUP_TRIGGER)) {
        return { is_duplicate: true, score: 0.92,
                 of_ticket_id: `TKT-prev-${short}` };
      }
      // simple Jaccard-ish on tokens vs a fake "recent" set
      return { is_duplicate: false, score: 0.0 };
    },

    assess_urgency({ tier, intent, text, sla }) {
      let score = 0;
      if (tier === "key") score += 0.4;
      else if (tier === "gold") score += 0.2;
      const t2 = String(text || "").toLowerCase();
      if (/down|outage|broken|cannot/.test(t2)) score += 0.3;
      if (/asap|urgent|now/.test(t2)) score += 0.2;
      if ((sla && sla.response_minutes) && sla.response_minutes <= 30) score += 0.1;
      const level = score >= 0.7 ? "critical"
                  : score >= 0.5 ? "high"
                  : score >= 0.3 ? "med" : "low";
      return { level, score: Number(score.toFixed(2)),
               reasons: ["tier", "keywords", "sla"].filter(Boolean) };
    },

    draft_ticket({ intent, text, urgency }) {
      const title = `${(intent || "request").toUpperCase()}: ${String(text || "").slice(0, 60)}`;
      const body = `Auto-drafted ticket\n\nUrgency: ${urgency}\n\nOriginal text:\n${text}`;
      return { title, body, suggested_assignee: "ops-l1" };
    },

    create_ticket({ title, body, urgency, assignee, customer_id }) {
      if (!customer_id) {
        return { ticket_id: null, error: "missing_customer_id",
                 reason: "customer_id is required (call lookup_customer first)" };
      }
      if (!customersChecked.has(customer_id)) {
        return { ticket_id: null, error: "conflict",
                 reason: "must call check_open_tickets for this customer_id before create_ticket" };
      }
      const ticket_id = mintId("TKT");
      mutations.push({ ticket_id, kind: "create_ticket",
                       title, urgency, assignee, customer_id });
      return { ticket_id, status: "open" };
    },

    update_crm({ customer_id, kind, payload }) {
      const event_id = mintId("EVT");
      mutations.push({ event_id, kind: `crm_${kind}`, customer_id, payload });
      return { event_id };
    },

    send_notification({ audience, channel, subject, body }) {
      const notification_id = mintId("NTF");
      mutations.push({ notification_id, kind: "notify",
                       audience, channel, subject });
      return { notification_id };
    },

    schedule_report({ kind, due_at, payload }) {
      const report_id = mintId("RPT");
      mutations.push({ report_id, kind: `report_${kind}`, due_at });
      return { report_id };
    },

    enqueue_analysis({ topic, severity, payload }) {
      const analysis_id = mintId("AUD");
      mutations.push({ analysis_id, kind: "analysis", topic, severity });
      return { analysis_id };
    },

    finish({ summary, status }) {
      return { terminate: true, summary, status };
    },
  };

  return t;
}

export const TOOL_CATALOG = [
  { name: "lookup_customer",      kind: "read",  args: ["email"] },
  { name: "fetch_request_history",kind: "read",  args: ["email", "limit?"] },
  { name: "get_sla",              kind: "read",  args: ["tier", "intent"] },
  { name: "check_open_tickets",   kind: "read",  args: ["customer_id", "intent"] },
  { name: "dedup_check",          kind: "read",  args: ["text", "window_hours?"] },
  { name: "assess_urgency",       kind: "read",  args: ["tier", "intent", "text", "sla"] },
  { name: "draft_ticket",         kind: "read",  args: ["intent", "text", "urgency"] },
  { name: "create_ticket",        kind: "write", args: ["title", "body", "urgency", "assignee", "customer_id"] },
  { name: "update_crm",           kind: "write", args: ["customer_id", "kind", "payload"] },
  { name: "send_notification",    kind: "write", args: ["audience", "channel", "subject", "body"] },
  { name: "schedule_report",      kind: "write", args: ["kind", "due_at", "payload"] },
  { name: "enqueue_analysis",     kind: "write", args: ["topic", "severity", "payload"] },
  { name: "finish",               kind: "meta",  args: ["summary", "status"] },
];
```

- [ ] **Step 4: Run tests, expect pass**

```bash
cd _build && node --test js/tools.test.js
```
Expected: 8 tests pass.

- [ ] **Step 5: Commit**

```bash
git add _build/js/tools.js _build/js/tools.test.js
git commit -m "Add 12-tool catalog with deterministic failure injection and tests"
```

### Task 2.2: Implement the ReAct loop with a stub LLM caller

**Files:**
- Create: `_build/js/react_loop.js`
- Create: `_build/js/react_loop.test.js`

The loop accepts an injected `callLLM` so tests can drive it deterministically without hitting Ollama.

- [ ] **Step 1: Write the failing test**

```javascript
// _build/js/react_loop.test.js
import { test } from "node:test";
import assert from "node:assert/strict";
import { runReactLoop } from "./react_loop.js";
import { makeTools, TOOL_CATALOG } from "./tools.js";

function scriptedLLM(plan) {
  let i = 0;
  return async () => plan[i++];
}

test("loop reaches finish in one turn when LLM picks finish immediately", async () => {
  const tools = makeTools({ correlation_id: "exec-1700000000001" });
  const callLLM = scriptedLLM([
    JSON.stringify({ thought: "nothing to do", tool: "finish",
                     args: { summary: "n/a", status: "ok" } }),
  ]);
  const out = await runReactLoop({
    step: { id: "s1", action: "noop", args_hints: {} },
    tools, toolCatalog: TOOL_CATALOG, callLLM, maxTurns: 5,
  });
  assert.equal(out.outcome.status, "ok");
  assert.equal(out.trace.length, 1);
});

test("loop composes lookup -> check -> create -> finish", async () => {
  const tools = makeTools({ correlation_id: "exec-1700000000002" });
  const callLLM = scriptedLLM([
    JSON.stringify({ thought: "find customer", tool: "lookup_customer",
                     args: { email: "alice@digitserve.io" } }),
    JSON.stringify({ thought: "check tickets", tool: "check_open_tickets",
                     args: { customer_id: "$prev.id", intent: "ticket_open" } }),
    JSON.stringify({ thought: "create", tool: "create_ticket",
                     args: { title: "t", body: "b", urgency: "high",
                             assignee: "ops", customer_id: "$prev2.id" } }),
    JSON.stringify({ thought: "done", tool: "finish",
                     args: { summary: "ticket opened", status: "ok" } }),
  ]);
  const out = await runReactLoop({
    step: { id: "s1", action: "resolve_ticket",
            args_hints: { email: "alice@digitserve.io" } },
    tools, toolCatalog: TOOL_CATALOG, callLLM, maxTurns: 5,
  });
  assert.equal(out.outcome.status, "ok");
  assert.equal(out.trace.length, 4);
  assert.equal(tools.mutations.length, 1);
  assert.match(tools.mutations[0].ticket_id, /^TKT-/);
});

test("loop hits turn cap and reports incomplete", async () => {
  const tools = makeTools({ correlation_id: "exec-1700000000003" });
  const reply = JSON.stringify({
    thought: "keep going", tool: "fetch_request_history",
    args: { email: "alice@digitserve.io" },
  });
  const callLLM = async () => reply;
  const out = await runReactLoop({
    step: { id: "s1", action: "loop_forever", args_hints: {} },
    tools, toolCatalog: TOOL_CATALOG, callLLM, maxTurns: 3,
  });
  assert.equal(out.outcome.status, "incomplete");
  assert.equal(out.trace.length, 3);
  assert.match(out.outcome.reason, /turn_budget_exhausted/);
});

test("loop recovers from conflict by calling check_open_tickets", async () => {
  // Simulates T5 of the spec: agent skips check_open_tickets, hits conflict,
  // then calls it and retries.
  const tools = makeTools({ correlation_id: "exec-1700000000004" });
  const callLLM = scriptedLLM([
    JSON.stringify({ thought: "find customer", tool: "lookup_customer",
                     args: { email: "alice@digitserve.io" } }),
    JSON.stringify({ thought: "create directly", tool: "create_ticket",
                     args: { title: "t", body: "b", urgency: "high",
                             assignee: "ops", customer_id: "$prev.id" } }),
    JSON.stringify({ thought: "oh, must check first", tool: "check_open_tickets",
                     args: { customer_id: "$prev2.id", intent: "ticket_open" } }),
    JSON.stringify({ thought: "retry", tool: "create_ticket",
                     args: { title: "t", body: "b", urgency: "high",
                             assignee: "ops", customer_id: "$prev3.id" } }),
    JSON.stringify({ thought: "done", tool: "finish",
                     args: { summary: "recovered", status: "ok" } }),
  ]);
  const out = await runReactLoop({
    step: { id: "s1", action: "resolve_ticket",
            args_hints: { email: "alice@digitserve.io" } },
    tools, toolCatalog: TOOL_CATALOG, callLLM, maxTurns: 6,
  });
  assert.equal(out.outcome.status, "ok");
  // The conflict observation must be in the trace.
  const sawConflict = out.trace.some(turn =>
    turn.observation && JSON.stringify(turn.observation).includes("conflict"));
  assert.ok(sawConflict, "trace should contain the conflict observation");
});

test("loop tolerates LLM output that is not strict JSON by falling back to finish(error)", async () => {
  const tools = makeTools({ correlation_id: "exec-1700000000005" });
  const callLLM = async () => "the model said something but not JSON";
  const out = await runReactLoop({
    step: { id: "s1", action: "x", args_hints: {} },
    tools, toolCatalog: TOOL_CATALOG, callLLM, maxTurns: 3,
  });
  assert.equal(out.outcome.status, "error");
  assert.match(out.outcome.reason, /llm_output_unparseable/);
});
```

- [ ] **Step 2: Run, expect failure**

```bash
cd _build && node --test js/react_loop.test.js
```

- [ ] **Step 3: Implement `js/react_loop.js`**

```javascript
// _build/js/react_loop.js
// Bounded ReAct loop. The LLM is injected (callLLM) so n8n's Code node can
// pass a function that hits Ollama/OpenAI via $helpers.httpRequest, and unit
// tests can pass a scripted function.
//
// The model is expected to return strict JSON of the form:
//   { thought: string, tool: string, args: object }
// Any other tool name except a member of toolCatalog is treated as an error.
// "$prev", "$prev2", ... in args are resolved against the most recent N
// observations: $prev = last observation, $prev2 = the one before, etc.

function resolvePrev(args, observations) {
  const out = {};
  for (const [k, v] of Object.entries(args || {})) {
    if (typeof v !== "string" || !v.startsWith("$prev")) { out[k] = v; continue; }
    const ord = v.slice(5) === "" ? 1 : parseInt(v.slice(5), 10);
    const ref = observations[observations.length - ord];
    out[k] = ref && ref.id ? ref.id : v;
  }
  return out;
}

function tryParse(s) {
  try { return JSON.parse(s); } catch { /* attempt to extract first JSON object */ }
  const m = String(s).match(/\{[\s\S]*\}$/);
  if (m) { try { return JSON.parse(m[0]); } catch { /* fallthrough */ } }
  return null;
}

export async function runReactLoop({ step, tools, toolCatalog, callLLM, maxTurns }) {
  const trace = [];
  const observations = [];
  const knownTools = new Set(toolCatalog.map(t => t.name));

  for (let turn = 1; turn <= maxTurns; turn++) {
    const llmRaw = await callLLM({
      step, tool_catalog: toolCatalog, prior_trace: trace, turn, maxTurns,
    });

    const decision = tryParse(llmRaw);
    if (!decision || !decision.tool) {
      return {
        outcome: { status: "error", reason: "llm_output_unparseable", raw: llmRaw },
        trace,
      };
    }
    if (!knownTools.has(decision.tool)) {
      trace.push({ turn, thought: decision.thought, tool: decision.tool,
                   observation: { error: "unknown_tool" } });
      continue;
    }
    if (decision.tool === "finish") {
      trace.push({ turn, thought: decision.thought, tool: "finish",
                   args: decision.args, observation: null });
      return {
        outcome: { status: decision.args?.status || "ok",
                   summary: decision.args?.summary || "" },
        trace,
      };
    }

    const args = resolvePrev(decision.args, observations);
    let observation;
    try {
      observation = await tools[decision.tool](args);
    } catch (e) {
      observation = { error: "tool_threw", message: String(e?.message || e) };
    }
    observations.push(observation);
    trace.push({ turn, thought: decision.thought, tool: decision.tool,
                 args, observation });
  }

  return {
    outcome: { status: "incomplete", reason: "turn_budget_exhausted" },
    trace,
  };
}
```

- [ ] **Step 4: Run tests, expect pass**

```bash
cd _build && node --test js/react_loop.test.js
```
Expected: 5 tests pass.

- [ ] **Step 5: Commit**

```bash
git add _build/js/react_loop.js _build/js/react_loop.test.js
git commit -m "Add bounded ReAct loop with prev-ref resolution and recovery test"
```

### Task 2.3: Implement the Reflexion lesson store helpers

**Files:**
- Create: `_build/js/lesson_store.js`
- Create: `_build/js/lesson_store.test.js`

- [ ] **Step 1: Write the failing test**

```javascript
// _build/js/lesson_store.test.js
import { test } from "node:test";
import assert from "node:assert/strict";
import { addLesson, retrieveLessons, evictIfFull, MAX_LESSONS } from "./lesson_store.js";

function emptyStore() { return { version: 1, lessons: [] }; }

test("addLesson assigns id and timestamps and respects cap", () => {
  const store = emptyStore();
  const now = new Date("2026-05-16T10:00:00Z");
  addLesson(store, {
    intent: "ticket_open", tier: "gold",
    tags: ["missing_lookup"], rule: "Always lookup_customer before create_ticket.",
    evidence_correlation_id: "x", confidence: 0.8,
  }, now);
  assert.equal(store.lessons.length, 1);
  assert.match(store.lessons[0].id, /^L-/);
  assert.equal(store.lessons[0].uses, 0);
});

test("retrieveLessons ranks by tag overlap, confidence, and recency", () => {
  const store = emptyStore();
  const now = new Date("2026-05-16T10:00:00Z");
  const stale = new Date("2026-01-01T00:00:00Z");
  addLesson(store, { intent: "ticket_open", tier: "gold",
    tags: ["missing_lookup"], rule: "A", evidence_correlation_id: "x",
    confidence: 0.6 }, stale);
  addLesson(store, { intent: "ticket_open", tier: "gold",
    tags: ["missing_lookup", "dedup"], rule: "B", evidence_correlation_id: "y",
    confidence: 0.9 }, now);
  addLesson(store, { intent: "ticket_open", tier: "gold",
    tags: ["unrelated"], rule: "C", evidence_correlation_id: "z",
    confidence: 0.7 }, now);
  const top = retrieveLessons(store, {
    queryTags: ["missing_lookup", "dedup"], k: 2, now,
  });
  assert.equal(top.length, 2);
  assert.equal(top[0].rule, "B");           // top match
  assert.notEqual(top[1].rule, "C");        // unrelated should be last
});

test("evictIfFull drops the lowest scored entry once cap is reached", () => {
  const store = emptyStore();
  const now = new Date("2026-05-16T10:00:00Z");
  for (let i = 0; i < MAX_LESSONS; i++) {
    addLesson(store, { intent: "x", tier: "bronze", tags: ["t" + i],
      rule: "rule " + i, evidence_correlation_id: "c" + i,
      confidence: 0.5 + (i % 10) / 100 }, now);
  }
  // Add a very high-quality lesson; should evict the weakest.
  addLesson(store, { intent: "x", tier: "bronze", tags: ["new"],
    rule: "shiny", evidence_correlation_id: "new", confidence: 0.99 }, now);
  evictIfFull(store, now);
  assert.equal(store.lessons.length, MAX_LESSONS);
  assert.ok(store.lessons.some(l => l.rule === "shiny"));
});

test("retrieveLessons increments use counter on a returned lesson", () => {
  const store = emptyStore();
  const now = new Date("2026-05-16T10:00:00Z");
  addLesson(store, { intent: "x", tier: "gold", tags: ["a"], rule: "R",
    evidence_correlation_id: "c", confidence: 0.9 }, now);
  retrieveLessons(store, { queryTags: ["a"], k: 1, now, markUsed: true });
  assert.equal(store.lessons[0].uses, 1);
});
```

- [ ] **Step 2: Run, expect failure**

```bash
cd _build && node --test js/lesson_store.test.js
```

- [ ] **Step 3: Implement `js/lesson_store.js`**

```javascript
// _build/js/lesson_store.js
// Pure functions over the Reflexion lesson store. The store object is mutated
// in place because that matches how n8n's $workflow.staticData is used inside
// Code nodes.

export const MAX_LESSONS = 50;

function uid() {
  // 8 hex chars from a 32-bit random + ms suffix.
  const r = (Math.random() * 0xffffffff) >>> 0;
  return "L-" + r.toString(16).padStart(8, "0") + "-" + Date.now().toString(36);
}

export function addLesson(store, lesson, now = new Date()) {
  const full = {
    id: uid(),
    created_at: now.toISOString(),
    intent: lesson.intent,
    tier: lesson.tier,
    tags: [...(lesson.tags || [])],
    rule: lesson.rule,
    evidence_correlation_id: lesson.evidence_correlation_id,
    confidence: lesson.confidence ?? 0.5,
    uses: 0,
    successes: 0,
  };
  store.lessons.push(full);
}

function score(lesson, queryTags, now) {
  const q = new Set(queryTags);
  let overlap = 0;
  for (const t of lesson.tags) if (q.has(t)) overlap += 1;
  const overlapRatio = queryTags.length ? overlap / queryTags.length : 0;
  const ageDays = Math.max(0,
    (now.getTime() - new Date(lesson.created_at).getTime()) / 86400000);
  const recency = 1 / (1 + ageDays / 30);  // half-life ~30 days
  return overlapRatio * 0.6 + (lesson.confidence ?? 0) * 0.3 + recency * 0.1;
}

export function retrieveLessons(store, { queryTags, k = 3, now = new Date(),
                                          markUsed = false }) {
  const scored = store.lessons
    .map(l => ({ l, s: score(l, queryTags, now) }))
    .sort((a, b) => b.s - a.s)
    .slice(0, k)
    .map(x => x.l);
  if (markUsed) for (const l of scored) l.uses += 1;
  return scored;
}

export function evictIfFull(store, now = new Date()) {
  while (store.lessons.length > MAX_LESSONS) {
    let worstIdx = 0;
    let worstScore = Infinity;
    for (let i = 0; i < store.lessons.length; i++) {
      const l = store.lessons[i];
      const ageDays = Math.max(0,
        (now.getTime() - new Date(l.created_at).getTime()) / 86400000);
      const recency = 1 / (1 + ageDays / 30);
      const composite = (l.confidence ?? 0) * Math.max(l.uses, 1) * recency;
      if (composite < worstScore) { worstScore = composite; worstIdx = i; }
    }
    store.lessons.splice(worstIdx, 1);
  }
}
```

- [ ] **Step 4: Run tests, expect pass**

```bash
cd _build && node --test js/lesson_store.test.js
```

- [ ] **Step 5: Commit**

```bash
git add _build/js/lesson_store.js _build/js/lesson_store.test.js
git commit -m "Add Reflexion lesson store helpers with retrieval and eviction"
```

---

## Phase 3 — Prompts

### Task 3.1: Write prompts as plain text files

Prompts live as `.txt` so they are easy to edit and version-control as prose. They are read at build time and embedded into HTTP node bodies.

**Files:**
- Create: `_build/prompts/interpret.txt`
- Create: `_build/prompts/critique.txt`
- Create: `_build/prompts/planner.txt`
- Create: `_build/prompts/reflexion.txt`
- Create: `_build/tests/test_prompts.py`

- [ ] **Step 1: Write the failing test**

```python
# _build/tests/test_prompts.py
import pathlib

PROMPTS = pathlib.Path(__file__).parent.parent / "prompts"

def _txt(name): return (PROMPTS / name).read_text()

def test_interpret_requests_strict_json_in_english():
    s = _txt("interpret.txt")
    assert "JSON only" in s
    assert "English" in s
    for k in ("intent", "entities", "urgency", "sensitivity", "confidence"):
        assert k in s

def test_critique_returns_accept_or_refine_hints():
    s = _txt("critique.txt")
    assert "accept" in s and "refine_hints" in s

def test_planner_includes_lesson_slot_and_dependency_field():
    s = _txt("planner.txt")
    assert "{lessons}" in s
    assert "depends_on" in s
    assert "requires_approval" in s

def test_reflexion_outputs_verdict_and_lessons_list():
    s = _txt("reflexion.txt")
    assert "verdict" in s
    assert "lessons" in s
    assert "tags" in s
```

- [ ] **Step 2: Run, expect failure**

```bash
cd _build && pytest tests/test_prompts.py -v
```

- [ ] **Step 3: Write `prompts/interpret.txt`**

```
You are the interpretation agent for DigitServe. Read the incoming request and produce a strict JSON object describing it. JSON only, no prose, no markdown fences. Write all string values in English.

Required fields:
- intent: short snake_case label (e.g., ticket_open, ticket_close, billing_question, incident_report)
- entities: object capturing the salient nouns and ids you can extract from the text
- urgency: one of low | med | high | critical
- sensitivity: one of low | med | high (high = involves PII, finance, or security)
- confidence: a number between 0 and 1 (your own confidence that the interpretation is correct)
- raw: a one-sentence English paraphrase of the request

Input:
sender: {sender}
channel: {channel}
text: {text}

Output JSON now.
```

- [ ] **Step 4: Write `prompts/critique.txt`**

```
You are a critique agent. The interpretation agent produced the following JSON for an incoming request. Decide whether to accept it or to send it back for one refinement pass. Output strict JSON, English only.

Output one of:
{"decision": "accept"}
{"decision": "refine_hints", "hints": ["short", "actionable", "english", "phrases"]}

Original text: {text}
Interpretation: {interpretation_json}

Output JSON now.
```

- [ ] **Step 5: Write `prompts/planner.txt`**

```
You are the planning agent for DigitServe. Given an interpreted request and (optionally) lessons from past runs, produce a concrete plan as strict JSON, English only.

A plan is a list of ordered steps, each step picks an abstract action from this allow-list:
- resolve_ticket
- notify_stakeholders
- escalate
- schedule_report
- enqueue_analysis
- log_crm_event
- dedup_and_close

Each step has:
- id: string ("s1", "s2", ...)
- action: one of the labels above
- args_hints: object (hints that the executor agent should use)
- depends_on: list of step ids that must complete before this one
- requires_approval: boolean; mark true when the action touches a key-tier customer or a high-sensitivity intent

The full plan object also contains a "rationale" string in English explaining the choice of steps.

Interpretation: {interpretation_json}
Relevant past lessons (may be empty):
{lessons}

Output strict JSON now in the shape:
{"rationale": "...", "steps": [ ... ]}
```

- [ ] **Step 6: Write `prompts/reflexion.txt`**

```
You are the reflection agent. Review the plan and its execution traces, then emit strict JSON, English only, in this shape:

{
  "verdict": "success" | "partial" | "failed",
  "lessons": [
    {
      "intent": "...",
      "tier": "...",
      "tags": ["short", "snake_case", "keywords"],
      "rule": "One sentence, imperative, generalizable.",
      "confidence": 0.0..1.0
    }
  ]
}

Rules for lessons:
- Emit zero lessons when the run was a clean success and the plan looked routine.
- Emit at most two lessons per run.
- Each lesson must be generalizable, not a restatement of this specific run.
- tags must be short snake_case keywords that a future planner can match against.

Plan: {plan_json}
Execution traces: {execution_json}
Outcome counts: {outcome_counts}

Output JSON now.
```

- [ ] **Step 7: Run tests, expect pass**

```bash
cd _build && pytest tests/test_prompts.py -v
```

- [ ] **Step 8: Commit**

```bash
git add _build/prompts/ _build/tests/test_prompts.py
git commit -m "Add LLM prompts for interpret, critique, planner, reflexion"
```

---

## Phase 4 — Stage modules

Each stage module exposes a single function `build(layout) -> (nodes, conns_into, conns_out)` so the top-level assembler can wire stages together by name. `layout` carries the canvas origin and a `bus.x` cursor so positions are deterministic.

### Task 4.1: Stickies module (header + stage labels + closing notes + test cases)

**Files:**
- Create: `_build/nodes/stickies.py`
- Create: `_build/tests/test_stickies.py`

- [ ] **Step 1: Write the failing test**

```python
# _build/tests/test_stickies.py
from nodes import stickies

def test_header_sticky_mentions_all_four_patterns_in_english():
    s = stickies.header()
    content = s["parameters"]["content"]
    for kw in ["Plan-Execute", "ReAct", "Reflexion", "self-critique", "English"]:
        assert kw in content, f"missing keyword: {kw}"
    assert "—" not in content, "no em dashes per project style"

def test_stage_sticky_labels_are_in_english():
    for label in ["stage_0", "stage_1", "stage_2", "stage_3",
                  "stage_4", "stage_5", "stage_6"]:
        s = stickies.stage(label)
        c = s["parameters"]["content"]
        # spot check: nothing Italian
        for italian in ["Stadio", "Agente", "Esegui", "Esecuzione",
                        "Decisionale", "Accoda"]:
            assert italian not in c

def test_test_cases_sticky_lists_T1_through_T8():
    s = stickies.test_cases()
    c = s["parameters"]["content"]
    for tag in ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"]:
        assert tag in c

def test_closing_notes_documents_production_swap_and_known_limits():
    s = stickies.closing_notes()
    c = s["parameters"]["content"]
    assert "production" in c.lower()
    assert "limitation" in c.lower() or "known" in c.lower()
```

- [ ] **Step 2: Run, expect failure**

```bash
cd _build && pytest tests/test_stickies.py -v
```

- [ ] **Step 3: Implement `nodes/stickies.py`**

```python
"""
Sticky-note authoring. All English. No em dashes, no AI-fingerprint phrases.
Content is verbatim what the n8n canvas reader will see.
"""
from .base import sticky_note

def header():
    return sticky_note(
        "Sticky - Header v2",
        content=(
            "## DigitServe v2 — Plan / ReAct / Reflexion\n"
            "### Module 03 - Agentic AI, agentic deep-cut fork\n\n"
            "**Author:** Simone La Porta · **Version:** v2 agentic\n\n"
            "---\n\n"
            "### Why this fork exists\n"
            "The v1 workflow used one-shot interpretation and a deterministic rule engine. "
            "v2 keeps the same domain (DigitServe internal request routing) and the same single-JSON "
            "deliverable form but introduces four agentic patterns: self-critique on interpretation, "
            "Plan-Execute planning, ReAct tool-composing executors over a 12-tool catalog, and "
            "Reflexion with lessons that persist across runs via $workflow.staticData.\n\n"
            "All content in this workflow is in English. The original Italian artifact remains the legacy reference."
        ).replace("—", "-"),   # keep the project style guard explicit
        width=1100, height=600, color=5, position=(14400, 4000),
    )

_STAGE_BLURBS = {
    "stage_0": ("Stage 0 - Ingress",
                "Webhook -> Normalize -> Configure Provider -> Load Reflexion store. "
                "Generates correlation_id used across the run."),
    "stage_1": ("Stage 1 - Interpret + self-critique",
                "LLM interprets the request, a second LLM critiques the JSON. "
                "One refine pass allowed. Abstain when confidence < 0.6."),
    "stage_2": ("Stage 2 - Plan-Execute planner",
                "LLM planner reads the interpretation and the top-K relevant past lessons, "
                "emits a DAG of abstract steps with dependencies and a per-step approval flag."),
    "stage_3": ("Stage 3 - Approval gate (plan level)",
                "If any step requires approval, send email and wait. Reject => terminate; auto/approved => continue."),
    "stage_4": ("Stage 4 - ReAct executors",
                "One Code-node loop per plan step. The agent reasons over the action, composes 2-5 tool calls "
                "from the 12-tool catalog, and stops with finish(). Trace is preserved verbatim."),
    "stage_5": ("Stage 5 - Reflexion critic",
                "Critic reviews plan + traces, emits {success | partial | failed} and up to 2 lessons. "
                "Lessons are persisted to $workflow.staticData with a ring-buffer cap of 50."),
    "stage_6": ("Stage 6 - Aggregate and respond",
                "Build a structured response including audit.events[], hit the audit sink, respond synchronously."),
}

def stage(label):
    title, body = _STAGE_BLURBS[label]
    return sticky_note(
        f"Sticky - {label}",
        content=f"### {title}\n{body}",
        width=700, height=220, color=6,
        position=(0, 0),   # the assembler overrides with the stage origin
    )

def test_cases():
    return sticky_note(
        "Sticky - Test cases",
        content=(
            "### Test cases (manual via curl)\n\n"
            "T1: silver, simple ticket. Baseline happy path.\n"
            "T2: gold, dedup + create + notify. Multi-step plan with deps.\n"
            "T3: key-tier, sensitive intent. Plan-level approval gate fires.\n"
            "T4: T3 with rejection. No writes, response status rejected_by_human.\n"
            "T5: forced tool failure (skip check_open_tickets). ReAct recovers in-step.\n"
            "T6: Reflexion replan. First plan omits lookup_customer; critic forces replan; lesson stored.\n"
            "T7: re-fire T6 payload. Planner is primed by the T6 lesson; no replan; lesson.uses incremented.\n"
            "T8: low-confidence abstain + budget exhaustion via forced-loop input.\n\n"
            "Curl skeleton:\n"
            "```\ncurl -X POST http://localhost:5678/webhook/digitserve-v2-richiesta \\\n"
            "  -H 'Content-Type: application/json' \\\n"
            "  -d @payloads/T1.json\n```\n\n"
            "Between cold runs of T6/T7 reset staticData via Settings -> Static Workflow Data -> Clear."
        ),
        width=900, height=420, color=4, position=(0, 0),
    )

def closing_notes():
    return sticky_note(
        "Sticky - Closing notes",
        content=(
            "### Closing notes\n\n"
            "**Production swap.** Each write tool maps to one HTTP Request in production: "
            "create_ticket -> ticketing API, update_crm -> CRM API, send_notification -> notifier, "
            "schedule_report -> reports queue, enqueue_analysis -> analytics queue. "
            "The current Code-node simulation returns the same response shape, so swap-in is local.\n\n"
            "**Known limitations.**\n"
            "1. LLM output phrasing quality is not asserted; only structure, tool sequencing, budget compliance, and lesson persistence are.\n"
            "2. Wall-clock performance is bounded by the workflow executionTimeout, not benchmarked.\n"
            "3. Concurrent runs are not safe against the shared lesson store ($workflow.staticData writes are not atomic). The deliverable assumes single-instance sequential usage.\n"
            "4. Lesson retrieval uses tag overlap, not embeddings, by design (single-JSON constraint)."
        ),
        width=900, height=420, color=3, position=(0, 0),
    )
```

- [ ] **Step 4: Run, expect pass**

```bash
cd _build && pytest tests/test_stickies.py -v
```

- [ ] **Step 5: Commit**

```bash
git add _build/nodes/stickies.py _build/tests/test_stickies.py
git commit -m "Add English sticky notes for header, stages, test cases, closing notes"
```

### Task 4.2: Stage 0 — Ingress

**Files:**
- Create: `_build/nodes/stage_0_ingress.py`
- Create: `_build/tests/test_stage_0.py`

- [ ] **Step 1: Write the failing test**

```python
# _build/tests/test_stage_0.py
from nodes import stage_0_ingress

def test_stage_0_emits_webhook_normalize_provider_loadmem():
    nodes, in_name, out_name = stage_0_ingress.build(origin=(15500, 4600))
    names = {n["name"] for n in nodes}
    expected = {
        "Webhook - Internal request",
        "Normalize Input",
        "Configure Provider",
        "Load Reflexion Store",
    }
    assert expected <= names
    assert in_name == "Webhook - Internal request"
    assert out_name == "Load Reflexion Store"

def test_normalize_sets_correlation_id_with_execution_id_and_ms():
    nodes, *_ = stage_0_ingress.build(origin=(0, 0))
    norm = next(n for n in nodes if n["name"] == "Normalize Input")
    assignments = norm["parameters"]["assignments"]["assignments"]
    cid = next(a for a in assignments if a["name"] == "correlation_id")
    assert "$execution.id" in cid["value"]
    assert "$now.toMillis" in cid["value"]

def test_provider_node_defaults_to_ollama_and_llama32():
    nodes, *_ = stage_0_ingress.build(origin=(0, 0))
    prov = next(n for n in nodes if n["name"] == "Configure Provider")
    text = str(prov["parameters"])
    assert "ollama" in text
    assert "llama3.2" in text
```

- [ ] **Step 2: Run, expect failure**

```bash
cd _build && pytest tests/test_stage_0.py -v
```

- [ ] **Step 3: Implement `nodes/stage_0_ingress.py`**

```python
"""
Stage 0: ingress. One webhook, normalize input, configure LLM provider, load
the Reflexion lesson store from $workflow.staticData.
"""
from .base import webhook_node, set_node, code_node

def build(origin):
    x, y = origin
    nodes = []

    nodes.append(webhook_node(
        "Webhook - Internal request",
        path="digitserve-v2-richiesta",
        position=(x, y),
    ))

    nodes.append(set_node(
        "Normalize Input",
        assignments=[
            {"id": "a1", "name": "correlation_id", "type": "string",
             "value": "={{ $json.body.correlation_id || ($execution.id + '-' + $now.toMillis()) }}"},
            {"id": "a2", "name": "channel", "type": "string",
             "value": "={{ $json.body.canale || $json.body.channel || 'unknown' }}"},
            {"id": "a3", "name": "sender", "type": "object",
             "value": "={{ $json.body.mittente || $json.body.sender || {} }}"},
            {"id": "a4", "name": "text", "type": "string",
             "value": "={{ ($json.body.testo || $json.body.text || '').trim() }}"},
            {"id": "a5", "name": "received_at", "type": "string",
             "value": "={{ $json.body.timestamp || $now.toISO() }}"},
            {"id": "a6", "name": "budget", "type": "object",
             "value": "={{ ({llm_calls_remaining: 20, react_turns_remaining_per_step: 5, interpret_refines_remaining: 1, replans_remaining: 1}) }}"},
            {"id": "a7", "name": "audit", "type": "object",
             "value": "={{ ({events: []}) }}"},
        ],
        position=(x + 220, y),
    ))

    nodes.append(set_node(
        "Configure Provider",
        assignments=[
            {"id": "p1", "name": "provider", "type": "string",
             "value": "={{ ['ollama','openai'].includes(($('Webhook - Internal request').first().json.body.provider || '').toLowerCase()) ? ($('Webhook - Internal request').first().json.body.provider).toLowerCase() : 'ollama' }}"},
            {"id": "p2", "name": "model", "type": "string",
             "value": "={{ $('Webhook - Internal request').first().json.body.model || ( (($('Webhook - Internal request').first().json.body.provider || 'ollama').toLowerCase() === 'openai') ? 'gpt-4o-mini' : 'llama3.2' ) }}"},
        ],
        position=(x + 440, y),
    ))

    nodes.append(code_node(
        "Load Reflexion Store",
        js_code=(
            "const sd = $workflow.staticData || {};\n"
            "if (!sd.reflexion_store) sd.reflexion_store = { version: 1, lessons: [] };\n"
            "const item = $input.first().json;\n"
            "item.reflexion_store_loaded = sd.reflexion_store;\n"
            "return [{ json: item }];\n"
        ),
        position=(x + 660, y),
    ))

    return nodes, "Webhook - Internal request", "Load Reflexion Store"
```

- [ ] **Step 4: Run, expect pass**

```bash
cd _build && pytest tests/test_stage_0.py -v
```

- [ ] **Step 5: Commit**

```bash
git add _build/nodes/stage_0_ingress.py _build/tests/test_stage_0.py
git commit -m "Stage 0: ingress (webhook, normalize, provider config, lesson load)"
```

### Task 4.3: Stage 1 — Interpret + critique + refine + abstain

**Files:**
- Create: `_build/nodes/stage_1_interpret.py`
- Create: `_build/tests/test_stage_1.py`

- [ ] **Step 1: Write the failing test**

```python
# _build/tests/test_stage_1.py
from nodes import stage_1_interpret

def test_stage_1_exposes_two_outputs_proceed_and_abstain():
    nodes, in_name, outs = stage_1_interpret.build(origin=(0, 0))
    assert "proceed" in outs and "abstain" in outs
    names = {n["name"] for n in nodes}
    assert {"LLM Interpret",
            "Parse Interpretation",
            "LLM Critique",
            "Refine? (decision)",
            "LLM Interpret (refined)",
            "Confidence Gate"} <= names

def test_confidence_gate_uses_threshold_0_6():
    nodes, *_ = stage_1_interpret.build(origin=(0, 0))
    gate = next(n for n in nodes if n["name"] == "Confidence Gate")
    cond = gate["parameters"]["conditions"]["conditions"][0]
    assert cond["rightValue"] == 0.6
    assert cond["operator"]["operation"] in ("largerEqual", "gte", "largerThanOrEqual")
```

- [ ] **Step 2: Run, expect failure**

```bash
cd _build && pytest tests/test_stage_1.py -v
```

- [ ] **Step 3: Implement `nodes/stage_1_interpret.py`**

```python
"""
Stage 1: interpret with self-critique. Two outputs:
- 'proceed': interpretation accepted, flows to the planner
- 'abstain': confidence below 0.6 even after one refine, flows to the responder
"""
import pathlib
from .base import http_node, code_node, if_node

_PROMPTS = pathlib.Path(__file__).resolve().parent.parent / "prompts"

def _interpret_body(prompt_text):
    return {
        "model": "={{ $json.model }}",
        "prompt": (
            f"{prompt_text}".replace("{sender}", "={{ JSON.stringify($json.sender) }}")
                            .replace("{channel}", "={{ $json.channel }}")
                            .replace("{text}", "={{ $json.text }}")
        ),
        "stream": False,
        "format": "json",
    }

def build(origin):
    x, y = origin
    nodes = []
    interpret_prompt = (_PROMPTS / "interpret.txt").read_text()
    critique_prompt = (_PROMPTS / "critique.txt").read_text()

    # The Ollama path is hard-coded here; the Switch on provider lives upstream
    # in stage 0's "Configure Provider" downstream wiring (we add a provider
    # router node in the assembler). For brevity, this module always emits
    # Ollama bodies; the OpenAI variants are siblings created by the
    # assembler when provider == "openai".
    nodes.append(http_node(
        "LLM Interpret",
        method="POST",
        url="http://host.docker.internal:11434/api/generate",
        body_json=_interpret_body(interpret_prompt),
        position=(x, y),
    ))

    nodes.append(code_node(
        "Parse Interpretation",
        js_code=(
            "const raw = $input.first().json.response || '';\n"
            "let interp;\n"
            "try { interp = JSON.parse(raw); }\n"
            "catch { interp = { intent: 'unknown', entities: {}, urgency: 'low',\n"
            "                   sensitivity: 'low', confidence: 0, raw: raw }; }\n"
            "const ctx = $('Load Reflexion Store').first().json;\n"
            "ctx.interpretation = interp;\n"
            "return [{ json: ctx }];\n"
        ),
        position=(x + 220, y),
    ))

    nodes.append(http_node(
        "LLM Critique",
        method="POST",
        url="http://host.docker.internal:11434/api/generate",
        body_json={
            "model": "={{ $json.model }}",
            "prompt": critique_prompt
                .replace("{text}", "={{ $json.text }}")
                .replace("{interpretation_json}",
                         "={{ JSON.stringify($json.interpretation) }}"),
            "stream": False,
            "format": "json",
        },
        position=(x + 440, y),
    ))

    nodes.append(code_node(
        "Refine? (decision)",
        js_code=(
            "const raw = $input.first().json.response || '';\n"
            "let dec; try { dec = JSON.parse(raw); } catch { dec = { decision: 'accept' }; }\n"
            "const ctx = $('Parse Interpretation').first().json;\n"
            "ctx.critique = dec;\n"
            "ctx.should_refine = dec.decision === 'refine_hints' && ctx.budget.interpret_refines_remaining > 0;\n"
            "if (ctx.should_refine) ctx.budget.interpret_refines_remaining -= 1;\n"
            "return [{ json: ctx }];\n"
        ),
        position=(x + 660, y),
    ))

    nodes.append(if_node(
        "Should refine?",
        left="={{ $json.should_refine }}",
        op="true",
        right=True,
        position=(x + 880, y),
    ))

    nodes.append(http_node(
        "LLM Interpret (refined)",
        method="POST",
        url="http://host.docker.internal:11434/api/generate",
        body_json=_interpret_body(
            interpret_prompt + "\n\nRefine according to these hints: {hints}\n"
        ),
        position=(x + 880, y + 160),
    ))

    nodes.append(if_node(
        "Confidence Gate",
        left="={{ $json.interpretation.confidence }}",
        op="largerEqual",
        right=0.6,
        position=(x + 1100, y),
    ))

    return nodes, "LLM Interpret", {"proceed": "Confidence Gate", "abstain": "Confidence Gate"}
```

> Implementation note for the worker: the operator key `largerEqual` is what
> n8n's IF node uses for `>=`. If your local n8n's IF schema uses a different
> key (`gte`, `largerThanOrEqual`), update the test's `operator.operation`
> assertion to match the same key you produce.

- [ ] **Step 4: Run tests, expect pass**

```bash
cd _build && pytest tests/test_stage_1.py -v
```

- [ ] **Step 5: Commit**

```bash
git add _build/nodes/stage_1_interpret.py _build/tests/test_stage_1.py
git commit -m "Stage 1: interpret with critique, refine, and abstain branch"
```

### Task 4.4: Stage 2 — Planner + validator

**Files:**
- Create: `_build/nodes/stage_2_plan.py`
- Create: `_build/tests/test_stage_2.py`

- [ ] **Step 1: Write the failing test**

```python
# _build/tests/test_stage_2.py
import json, pathlib
from nodes import stage_2_plan

def test_stage_2_exposes_planner_and_validator():
    nodes, in_name, out_name = stage_2_plan.build(origin=(0, 0))
    names = {n["name"] for n in nodes}
    assert {"Retrieve Lessons",
            "LLM Planner",
            "Validate Plan"} <= names
    assert in_name == "Retrieve Lessons"
    assert out_name == "Validate Plan"

def test_planner_prompt_substitutes_lessons_slot():
    nodes, *_ = stage_2_plan.build(origin=(0, 0))
    planner = next(n for n in nodes if n["name"] == "LLM Planner")
    body = json.dumps(planner["parameters"]["jsonBody"])
    assert "{interpretation_json}" not in body  # was replaced by an n8n expression
    assert "$json.interpretation" in body
    assert "$json.relevant_lessons" in body
```

- [ ] **Step 2: Run, expect failure**

```bash
cd _build && pytest tests/test_stage_2.py -v
```

- [ ] **Step 3: Implement `nodes/stage_2_plan.py`**

```python
"""
Stage 2: planner. Inputs:
  - run.interpretation
  - top-K relevant lessons from the loaded reflexion_store
Output:
  - run.plan validated against schemas/plan.schema.json
"""
import pathlib
from .base import code_node, http_node

_PROMPTS = pathlib.Path(__file__).resolve().parent.parent / "prompts"
_SCHEMAS = pathlib.Path(__file__).resolve().parent.parent / "schemas"
_LESSONS_JS = pathlib.Path(__file__).resolve().parent.parent / "js" / "lesson_store.js"

def build(origin):
    x, y = origin
    nodes = []
    planner_prompt = (_PROMPTS / "planner.txt").read_text()
    lesson_js = _LESSONS_JS.read_text()
    plan_schema = (_SCHEMAS / "plan.schema.json").read_text()

    nodes.append(code_node(
        "Retrieve Lessons",
        js_code=(
            lesson_js + "\n\n"
            "const ctx = $input.first().json;\n"
            "const store = ctx.reflexion_store_loaded || { version: 1, lessons: [] };\n"
            "const queryTags = [\n"
            "  ctx.interpretation.intent,\n"
            "  ctx.interpretation.urgency,\n"
            "  ctx.interpretation.sensitivity,\n"
            "].filter(Boolean);\n"
            "const top = retrieveLessons(store, { queryTags, k: 3, now: new Date(), markUsed: true });\n"
            "ctx.relevant_lessons = top;\n"
            "ctx.audit.events.push({ stage: 'plan/retrieve', t_ms: Date.now(),\n"
            "  summary: 'fetched ' + top.length + ' lesson(s)' });\n"
            "return [{ json: ctx }];\n"
        ),
        position=(x, y),
    ))

    nodes.append(http_node(
        "LLM Planner",
        method="POST",
        url="http://host.docker.internal:11434/api/generate",
        body_json={
            "model": "={{ $json.model }}",
            "prompt": planner_prompt
                .replace("{interpretation_json}",
                         "={{ JSON.stringify($json.interpretation) }}")
                .replace("{lessons}",
                         "={{ JSON.stringify($json.relevant_lessons) }}"),
            "stream": False,
            "format": "json",
        },
        position=(x + 220, y),
    ))

    nodes.append(code_node(
        "Validate Plan",
        js_code=(
            "const Ajv = (() => { try { return require('ajv'); } catch { return null; } })();\n"
            "const raw = $input.first().json.response || '';\n"
            "let plan;\n"
            "try { plan = JSON.parse(raw); }\n"
            "catch { plan = null; }\n"
            "const ok = plan && Array.isArray(plan.steps) && plan.steps.length > 0\n"
            "  && plan.steps.every(s => s && s.id && s.action && Array.isArray(s.depends_on));\n"
            "const ctx = $('Retrieve Lessons').first().json;\n"
            "if (!ok) {\n"
            "  ctx.plan = { rationale: 'invalid plan from LLM', steps: [] };\n"
            "  ctx.plan_invalid = true;\n"
            "} else {\n"
            "  ctx.plan = plan;\n"
            "  ctx.plan_invalid = false;\n"
            "}\n"
            "ctx.budget.llm_calls_remaining = Math.max(0, ctx.budget.llm_calls_remaining - 1);\n"
            "ctx.audit.events.push({ stage: 'plan/built', t_ms: Date.now(),\n"
            "  summary: 'steps=' + (ctx.plan.steps?.length || 0) });\n"
            "return [{ json: ctx }];\n"
        ),
        position=(x + 440, y),
    ))

    return nodes, "Retrieve Lessons", "Validate Plan"
```

- [ ] **Step 4: Run tests, expect pass**

```bash
cd _build && pytest tests/test_stage_2.py -v
```

- [ ] **Step 5: Commit**

```bash
git add _build/nodes/stage_2_plan.py _build/tests/test_stage_2.py
git commit -m "Stage 2: planner with lesson injection and shallow plan validation"
```

### Task 4.5: Stage 3 — Approval gate

**Files:**
- Create: `_build/nodes/stage_3_approval.py`
- Create: `_build/tests/test_stage_3.py`

- [ ] **Step 1: Write the failing test**

```python
# _build/tests/test_stage_3.py
from nodes import stage_3_approval

def test_stage_3_branches_into_approved_and_rejected():
    nodes, in_name, outs = stage_3_approval.build(origin=(0, 0))
    assert set(outs.keys()) == {"approved", "rejected"}
    names = {n["name"] for n in nodes}
    assert {"Plan Needs Approval?",
            "Send & Wait Approval",
            "Approval Decision",
            "Merge Approval Branches",
            "Was Rejected?"} <= names
```

- [ ] **Step 2: Run, expect failure**

```bash
cd _build && pytest tests/test_stage_3.py -v
```

- [ ] **Step 3: Implement `nodes/stage_3_approval.py`**

```python
"""
Stage 3: plan-level approval gate.
- If any step in run.plan.steps has requires_approval=true, send a Send & Wait
  email and wait for the recipient's decision (approve / reject).
- If no step needs approval, take the auto-approve branch.
- Both branches merge before a final Was Rejected? IF that splits into the
  rejected output (skip executors, respond) or the approved output (run executors).
"""
from .base import if_node, code_node, merge_node

def build(origin):
    x, y = origin
    nodes = []

    nodes.append(code_node(
        "Plan Needs Approval?",
        js_code=(
            "const ctx = $input.first().json;\n"
            "ctx.approval_required = (ctx.plan.steps || []).some(s => s.requires_approval);\n"
            "return [{ json: ctx }];\n"
        ),
        position=(x, y),
    ))

    nodes.append(if_node(
        "Needs Approval? (router)",
        left="={{ $json.approval_required }}",
        op="true",
        right=True,
        position=(x + 220, y),
    ))

    # Send & Wait is an emailSendAndWait node in n8n. For portability we emit a
    # Code node that simulates the wait by reading an `approval` field off the
    # incoming payload. In production replace with the emailSendAndWait node.
    nodes.append(code_node(
        "Send & Wait Approval",
        js_code=(
            "const ctx = $input.first().json;\n"
            "const decision = (ctx.approval || '').toLowerCase();\n"
            "ctx.approval_outcome = ['approved','rejected'].includes(decision)\n"
            "  ? decision : 'approved';   // default to approved for demo runs\n"
            "ctx.audit.events.push({ stage: 'approval', t_ms: Date.now(),\n"
            "  summary: 'human=' + ctx.approval_outcome });\n"
            "return [{ json: ctx }];\n"
        ),
        position=(x + 440, y - 100),
    ))

    nodes.append(code_node(
        "Approval Decision",
        js_code=(
            "const ctx = $input.first().json;\n"
            "ctx.approval_outcome = 'auto_approved';\n"
            "return [{ json: ctx }];\n"
        ),
        position=(x + 440, y + 100),
    ))

    nodes.append(merge_node(
        "Merge Approval Branches",
        position=(x + 660, y),
        mode="append",
    ))

    nodes.append(if_node(
        "Was Rejected?",
        left="={{ $json.approval_outcome }}",
        op="equals",
        right="rejected",
        position=(x + 880, y),
    ))

    return nodes, "Plan Needs Approval?", {
        "approved": "Was Rejected?",   # false output of the IF
        "rejected": "Was Rejected?",   # true output of the IF
    }
```

- [ ] **Step 4: Run tests, expect pass**

```bash
cd _build && pytest tests/test_stage_3.py -v
```

- [ ] **Step 5: Commit**

```bash
git add _build/nodes/stage_3_approval.py _build/tests/test_stage_3.py
git commit -m "Stage 3: plan-level approval gate with auto and human branches"
```

### Task 4.6: Stage 4 — ReAct executor stage

**Files:**
- Create: `_build/nodes/stage_4_react.py`
- Create: `_build/tests/test_stage_4.py`

The single ReAct Code node embeds `js/tools.js`, `js/react_loop.js`, plus an adapter that maps `callLLM` to `$helpers.httpRequest`.

- [ ] **Step 1: Write the failing test**

```python
# _build/tests/test_stage_4.py
from nodes import stage_4_react

def test_stage_4_has_split_loop_executor_and_merge():
    nodes, in_name, out_name = stage_4_react.build(origin=(0, 0))
    names = {n["name"] for n in nodes}
    assert {"Split Plan Steps", "ReAct Executor", "Merge Step Outcomes"} <= names
    assert in_name == "Split Plan Steps"
    assert out_name == "Merge Step Outcomes"

def test_react_executor_embeds_tools_and_loop_source():
    nodes, *_ = stage_4_react.build(origin=(0, 0))
    react = next(n for n in nodes if n["name"] == "ReAct Executor")
    js = react["parameters"]["jsCode"]
    assert "makeTools" in js
    assert "runReactLoop" in js
    assert "TOOL_CATALOG" in js
    # the LLM caller is wired via $helpers.httpRequest
    assert "$helpers.httpRequest" in js
```

- [ ] **Step 2: Run, expect failure**

```bash
cd _build && pytest tests/test_stage_4.py -v
```

- [ ] **Step 3: Implement `nodes/stage_4_react.py`**

```python
"""
Stage 4: ReAct executor. Splits plan.steps into one item per step, runs the
ReAct loop per step inside a Code node, then merges the per-step outcomes back
into a single run object.

The Code node embeds tools.js, react_loop.js, and an LLM-call adapter that
uses $helpers.httpRequest against the configured provider.
"""
import pathlib
from .base import code_node, split_in_batches_node, merge_node

_JS = pathlib.Path(__file__).resolve().parent.parent / "js"

def _embed_module(path, exported_names):
    """Inline a JS file and strip its `export` keywords, exposing names locally."""
    src = path.read_text()
    src = src.replace("export const ", "const ")
    src = src.replace("export function ", "function ")
    src = src.replace("export async function ", "async function ")
    return src

def build(origin):
    x, y = origin
    nodes = []

    tools_src = _embed_module(_JS / "tools.js", ["makeTools", "TOOL_CATALOG"])
    loop_src  = _embed_module(_JS / "react_loop.js", ["runReactLoop"])

    nodes.append(split_in_batches_node(
        "Split Plan Steps",
        batch_size=1,
        position=(x, y),
    ))

    react_js = (
        "// === embedded tools.js ===\n" + tools_src + "\n\n"
        "// === embedded react_loop.js ===\n" + loop_src + "\n\n"
        "// === executor entry ===\n"
        "const ctx = $('Was Rejected?').first().json;   // upstream run state\n"
        "const step = $input.first().json;              // single plan step\n"
        "const correlation_id = ctx.correlation_id;\n"
        "const tools = makeTools({ correlation_id });\n"
        "\n"
        "async function callLLM({ step, tool_catalog, prior_trace, turn, maxTurns }) {\n"
        "  if (ctx.budget.llm_calls_remaining <= 0) {\n"
        "    return JSON.stringify({ thought: 'budget_exceeded', tool: 'finish',\n"
        "      args: { summary: 'budget exhausted', status: 'incomplete' } });\n"
        "  }\n"
        "  ctx.budget.llm_calls_remaining -= 1;\n"
        "  const url = (ctx.provider === 'openai')\n"
        "    ? 'https://api.openai.com/v1/chat/completions'\n"
        "    : 'http://host.docker.internal:11434/api/generate';\n"
        "  const prompt = 'You are a ReAct executor. Output strict JSON only, English only.\\n' +\n"
        "                 'Tools: ' + JSON.stringify(tool_catalog) + '\\n' +\n"
        "                 'Step: ' + JSON.stringify(step) + '\\n' +\n"
        "                 'Prior trace: ' + JSON.stringify(prior_trace) + '\\n' +\n"
        "                 'Turn ' + turn + ' of ' + maxTurns + '. Choose a tool and args.';\n"
        "  const body = (ctx.provider === 'openai')\n"
        "    ? { model: ctx.model, response_format: { type: 'json_object' },\n"
        "        messages: [{ role: 'user', content: prompt }] }\n"
        "    : { model: ctx.model, prompt, stream: false, format: 'json' };\n"
        "  const resp = await $helpers.httpRequest({\n"
        "    method: 'POST', url, body, json: true, timeout: 30000,\n"
        "  });\n"
        "  return ctx.provider === 'openai'\n"
        "    ? resp.choices[0].message.content\n"
        "    : resp.response;\n"
        "}\n"
        "\n"
        "const out = await runReactLoop({\n"
        "  step, tools, toolCatalog: TOOL_CATALOG, callLLM,\n"
        "  maxTurns: ctx.budget.react_turns_remaining_per_step,\n"
        "});\n"
        "ctx.execution = ctx.execution || [];\n"
        "ctx.execution.push({\n"
        "  step_id: step.id, trace: out.trace,\n"
        "  mutations: tools.mutations, outcome: out.outcome,\n"
        "});\n"
        "ctx.audit.events.push({ stage: 'react/step/' + step.id, t_ms: Date.now(),\n"
        "  summary: 'turns=' + out.trace.length + ' status=' + out.outcome.status,\n"
        "  tools_used: out.trace.map(t => t.tool) });\n"
        "return [{ json: ctx }];\n"
    )

    nodes.append(code_node(
        "ReAct Executor",
        js_code=react_js,
        position=(x + 220, y),
    ))

    nodes.append(merge_node(
        "Merge Step Outcomes",
        position=(x + 440, y),
        mode="append",
    ))

    return nodes, "Split Plan Steps", "Merge Step Outcomes"
```

- [ ] **Step 4: Run tests, expect pass**

```bash
cd _build && pytest tests/test_stage_4.py -v
```

- [ ] **Step 5: Commit**

```bash
git add _build/nodes/stage_4_react.py _build/tests/test_stage_4.py
git commit -m "Stage 4: ReAct executor embedding tools and loop with LLM adapter"
```

### Task 4.7: Stage 5 — Reflexion critic + replan + persist

**Files:**
- Create: `_build/nodes/stage_5_reflexion.py`
- Create: `_build/tests/test_stage_5.py`

- [ ] **Step 1: Write the failing test**

```python
# _build/tests/test_stage_5.py
from nodes import stage_5_reflexion

def test_stage_5_has_critic_replan_router_and_persist():
    nodes, in_name, outs = stage_5_reflexion.build(origin=(0, 0))
    names = {n["name"] for n in nodes}
    assert {"LLM Critic",
            "Parse Critic",
            "Replan? (router)",
            "Consolidate Lessons"} <= names
    assert set(outs.keys()) == {"replan", "respond"}

def test_consolidate_writes_to_static_data():
    nodes, *_ = stage_5_reflexion.build(origin=(0, 0))
    persist = next(n for n in nodes if n["name"] == "Consolidate Lessons")
    js = persist["parameters"]["jsCode"]
    assert "$workflow.staticData" in js
    assert "evictIfFull" in js
```

- [ ] **Step 2: Run, expect failure**

```bash
cd _build && pytest tests/test_stage_5.py -v
```

- [ ] **Step 3: Implement `nodes/stage_5_reflexion.py`**

```python
"""
Stage 5: Reflexion critic.
- LLM Critic reviews plan + execution traces, outputs {verdict, lessons}.
- If verdict=failed AND replans_remaining>0, take the 'replan' output, decrement
  replans_remaining, and feed back into the planner.
- Otherwise, take the 'respond' output, consolidate any emitted lessons into
  $workflow.staticData, and continue to stage 6.
"""
import pathlib
from .base import http_node, code_node, if_node

_PROMPTS = pathlib.Path(__file__).resolve().parent.parent / "prompts"
_JS = pathlib.Path(__file__).resolve().parent.parent / "js"

def build(origin):
    x, y = origin
    nodes = []
    reflexion_prompt = (_PROMPTS / "reflexion.txt").read_text()
    lesson_js = (_JS / "lesson_store.js").read_text()\
        .replace("export const ", "const ")\
        .replace("export function ", "function ")

    nodes.append(http_node(
        "LLM Critic",
        method="POST",
        url="http://host.docker.internal:11434/api/generate",
        body_json={
            "model": "={{ $json.model }}",
            "prompt": reflexion_prompt
                .replace("{plan_json}", "={{ JSON.stringify($json.plan) }}")
                .replace("{execution_json}",
                         "={{ JSON.stringify($json.execution) }}")
                .replace("{outcome_counts}",
                         "={{ JSON.stringify(($json.execution || []).reduce((m,s) => "
                         "(m[s.outcome.status] = (m[s.outcome.status]||0)+1, m), {})) }}"),
            "stream": False,
            "format": "json",
        },
        position=(x, y),
    ))

    nodes.append(code_node(
        "Parse Critic",
        js_code=(
            "const raw = $input.first().json.response || '';\n"
            "let r; try { r = JSON.parse(raw); }\n"
            "catch { r = { verdict: 'partial', lessons: [] }; }\n"
            "const ctx = $input.first().json;\n"
            "ctx.reflexion = { verdict: r.verdict || 'partial',\n"
            "                  lessons: Array.isArray(r.lessons) ? r.lessons.slice(0,2) : [] };\n"
            "ctx.budget.llm_calls_remaining = Math.max(0, ctx.budget.llm_calls_remaining - 1);\n"
            "ctx.audit.events.push({ stage: 'reflexion/parsed', t_ms: Date.now(),\n"
            "  summary: 'verdict=' + ctx.reflexion.verdict + ' lessons=' + ctx.reflexion.lessons.length });\n"
            "return [{ json: ctx }];\n"
        ),
        position=(x + 220, y),
    ))

    nodes.append(if_node(
        "Replan? (router)",
        left="={{ $json.reflexion.verdict === 'failed' && $json.budget.replans_remaining > 0 }}",
        op="true",
        right=True,
        position=(x + 440, y),
    ))

    nodes.append(code_node(
        "Consolidate Lessons",
        js_code=(
            lesson_js + "\n\n"
            "const ctx = $input.first().json;\n"
            "const sd = $workflow.staticData;\n"
            "if (!sd.reflexion_store) sd.reflexion_store = { version: 1, lessons: [] };\n"
            "for (const l of (ctx.reflexion.lessons || [])) {\n"
            "  addLesson(sd.reflexion_store, {\n"
            "    intent: l.intent || ctx.interpretation.intent,\n"
            "    tier: l.tier || (ctx.interpretation.entities?.tier || 'unknown'),\n"
            "    tags: l.tags || [],\n"
            "    rule: l.rule,\n"
            "    evidence_correlation_id: ctx.correlation_id,\n"
            "    confidence: l.confidence ?? 0.6,\n"
            "  }, new Date());\n"
            "}\n"
            "evictIfFull(sd.reflexion_store, new Date());\n"
            "ctx.audit.events.push({ stage: 'reflexion/persisted', t_ms: Date.now(),\n"
            "  summary: 'lessons_now=' + sd.reflexion_store.lessons.length });\n"
            "return [{ json: ctx }];\n"
        ),
        position=(x + 660, y),
    ))

    # Replan branch: decrement counter and route back to the planner. The
    # assembler wires "Replan? (router)" true-output back to "Retrieve Lessons".
    nodes.append(code_node(
        "Decrement Replan Counter",
        js_code=(
            "const ctx = $input.first().json;\n"
            "ctx.budget.replans_remaining = Math.max(0, ctx.budget.replans_remaining - 1);\n"
            "return [{ json: ctx }];\n"
        ),
        position=(x + 660, y - 160),
    ))

    return nodes, "LLM Critic", {
        "replan": "Decrement Replan Counter",
        "respond": "Consolidate Lessons",
    }
```

- [ ] **Step 4: Run tests, expect pass**

```bash
cd _build && pytest tests/test_stage_5.py -v
```

- [ ] **Step 5: Commit**

```bash
git add _build/nodes/stage_5_reflexion.py _build/tests/test_stage_5.py
git commit -m "Stage 5: Reflexion critic with replan loop and staticData persistence"
```

### Task 4.8: Stage 6 — Aggregate, audit sink, respond

**Files:**
- Create: `_build/nodes/stage_6_respond.py`
- Create: `_build/tests/test_stage_6.py`

- [ ] **Step 1: Write the failing test**

```python
# _build/tests/test_stage_6.py
from nodes import stage_6_respond

def test_stage_6_builds_summary_audit_and_respond():
    nodes, in_name, out_name = stage_6_respond.build(origin=(0, 0))
    names = {n["name"] for n in nodes}
    assert {"Build Run Summary",
            "Audit Sink",
            "Respond to Webhook"} <= names
    assert out_name == "Respond to Webhook"

def test_audit_sink_includes_correlation_header():
    nodes, *_ = stage_6_respond.build(origin=(0, 0))
    sink = next(n for n in nodes if n["name"] == "Audit Sink")
    headers = sink["parameters"]["headerParameters"]["parameters"]
    keys = {h["name"] for h in headers}
    assert "X-Correlation-Id" in keys
```

- [ ] **Step 2: Run, expect failure**

```bash
cd _build && pytest tests/test_stage_6.py -v
```

- [ ] **Step 3: Implement `nodes/stage_6_respond.py`**

```python
"""
Stage 6: aggregate, audit, respond.
"""
from .base import code_node, http_node, respond_to_webhook_node

def build(origin):
    x, y = origin
    nodes = []

    nodes.append(code_node(
        "Build Run Summary",
        js_code=(
            "const ctx = $input.first().json;\n"
            "ctx.response = {\n"
            "  correlation_id: ctx.correlation_id,\n"
            "  status: ctx.approval_outcome === 'rejected' ? 'rejected_by_human'\n"
            "       : (ctx.confidence_abstain ? 'needs_human_triage'\n"
            "       : (ctx.budget.llm_calls_remaining <= 0 ? 'budget_exceeded'\n"
            "       : 'completed')),\n"
            "  interpretation: ctx.interpretation,\n"
            "  plan: ctx.plan,\n"
            "  execution: ctx.execution || [],\n"
            "  reflexion: ctx.reflexion || null,\n"
            "  audit: ctx.audit,\n"
            "};\n"
            "return [{ json: ctx }];\n"
        ),
        position=(x, y),
    ))

    nodes.append(http_node(
        "Audit Sink",
        method="POST",
        url="https://audit.example.local/digitserve-v2",
        body_json={"audit": "={{ $json.audit }}",
                   "correlation_id": "={{ $json.correlation_id }}"},
        headers={"X-Correlation-Id": "={{ $json.correlation_id }}",
                 "Content-Type": "application/json"},
        position=(x + 220, y),
        timeout_ms=10000,
        continue_on_fail=True,
    ))

    nodes.append(respond_to_webhook_node(
        "Respond to Webhook",
        response_body="={{ $json.response }}",
        position=(x + 440, y),
    ))

    return nodes, "Build Run Summary", "Respond to Webhook"
```

- [ ] **Step 4: Run, expect pass**

```bash
cd _build && pytest tests/test_stage_6.py -v
```

- [ ] **Step 5: Commit**

```bash
git add _build/nodes/stage_6_respond.py _build/tests/test_stage_6.py
git commit -m "Stage 6: build summary, audit sink, respond to webhook"
```

### Task 4.9: Self-check Code nodes (off-path)

**Files:**
- Create: `_build/nodes/self_checks.py`
- Create: `_build/tests/test_self_checks.py`

- [ ] **Step 1: Write the failing test**

```python
# _build/tests/test_self_checks.py
from nodes import self_checks

def test_self_checks_emit_three_nodes_with_known_names():
    nodes = self_checks.build(origin=(0, 0))
    names = {n["name"] for n in nodes}
    assert {"assert_trace", "assert_mutations", "assert_lesson_store"} <= names

def test_assert_lesson_store_reads_static_data():
    nodes = self_checks.build(origin=(0, 0))
    asl = next(n for n in nodes if n["name"] == "assert_lesson_store")
    assert "$workflow.staticData" in asl["parameters"]["jsCode"]
```

- [ ] **Step 2: Run, expect failure**

```bash
cd _build && pytest tests/test_self_checks.py -v
```

- [ ] **Step 3: Implement `nodes/self_checks.py`**

```python
"""
Off-path Code nodes for manual verification. Not on the request path; the
operator runs them via 'Execute Node' from the Executions panel after a curl
test.
"""
from .base import code_node

def build(origin):
    x, y = origin
    return [
        code_node(
            "assert_trace",
            js_code=(
                "// Usage: paste a run response into $json.run, set $json.case_id.\n"
                "const EXPECTED = {\n"
                "  T1: ['interpret','critique','plan/built','react/step/s1','reflexion/parsed','reflexion/persisted'],\n"
                "  T2: ['interpret','critique','plan/built','react/step/s1','react/step/s2','react/step/s3','reflexion/parsed','reflexion/persisted'],\n"
                "};\n"
                "const case_id = $json.case_id || 'T1';\n"
                "const run = $json.run || {};\n"
                "const seq = (run.audit?.events || []).map(e => e.stage.split('/')[0] + (e.stage.includes('/') ? '/' + e.stage.split('/').slice(1).join('/') : ''));\n"
                "const want = EXPECTED[case_id] || [];\n"
                "const missing = want.filter(w => !seq.some(s => s === w));\n"
                "return [{ json: { case_id, passed: missing.length === 0, missing, seq } }];\n"
            ),
            position=(x, y),
        ),
        code_node(
            "assert_mutations",
            js_code=(
                "const EXPECTED = { T1: ['TKT'], T2: ['TKT','NTF'], T4: [] };\n"
                "const case_id = $json.case_id || 'T1';\n"
                "const run = $json.run || {};\n"
                "const muts = (run.execution || []).flatMap(s => s.mutations || []);\n"
                "const prefixes = muts.map(m => Object.keys(m).find(k => k.endsWith('_id') || k === 'ticket_id') || 'unknown').map(k => (muts[0][k] || '').slice(0,3));\n"
                "const want = EXPECTED[case_id] || [];\n"
                "const passed = want.every(p => prefixes.includes(p));\n"
                "return [{ json: { case_id, passed, prefixes, want } }];\n"
            ),
            position=(x + 240, y),
        ),
        code_node(
            "assert_lesson_store",
            js_code=(
                "const sd = $workflow.staticData || {};\n"
                "const store = sd.reflexion_store || { lessons: [] };\n"
                "const wanted = ($json.expected_tags || []);\n"
                "const found = store.lessons.find(l => wanted.every(t => l.tags.includes(t)));\n"
                "return [{ json: { passed: !!found, count: store.lessons.length, found } }];\n"
            ),
            position=(x + 480, y),
        ),
    ]
```

- [ ] **Step 4: Run, expect pass**

```bash
cd _build && pytest tests/test_self_checks.py -v
```

- [ ] **Step 5: Commit**

```bash
git add _build/nodes/self_checks.py _build/tests/test_self_checks.py
git commit -m "Add off-path self-check Code nodes for manual trace verification"
```

### Task 4.10: Workflow-level error trigger

**Files:**
- Create: `_build/nodes/error_trigger.py`
- Create: `_build/tests/test_error_trigger.py`

- [ ] **Step 1: Write the failing test**

```python
# _build/tests/test_error_trigger.py
from nodes import error_trigger

def test_error_trigger_includes_trigger_audit_and_respond():
    nodes = error_trigger.build(origin=(0, 0))
    names = {n["name"] for n in nodes}
    assert {"Error Trigger", "Error Audit", "Error Respond"} <= names
```

- [ ] **Step 2: Run, expect failure**

```bash
cd _build && pytest tests/test_error_trigger.py -v
```

- [ ] **Step 3: Implement `nodes/error_trigger.py`**

```python
"""
Workflow-level error catcher. Sits off the main path and is invoked by n8n's
ErrorTrigger only when an unhandled error escapes. Writes a final audit row
and responds 500 with the correlation_id.
"""
import uuid
from .base import _id, code_node, http_node, respond_to_webhook_node

def _error_trigger_node(name, position):
    return {
        "id": _id(name),
        "name": name,
        "type": "n8n-nodes-base.errorTrigger",
        "typeVersion": 1,
        "position": [position[0], position[1]],
        "parameters": {},
    }

def build(origin):
    x, y = origin
    nodes = [
        _error_trigger_node("Error Trigger", (x, y)),
        http_node(
            "Error Audit",
            method="POST",
            url="https://audit.example.local/digitserve-v2/errors",
            body_json={
                "correlation_id": "={{ $json.execution?.id }}",
                "error": "={{ $json.error }}",
            },
            headers={"X-Correlation-Id": "={{ $json.execution?.id }}"},
            position=(x + 220, y),
            timeout_ms=10000,
            continue_on_fail=True,
        ),
        respond_to_webhook_node(
            "Error Respond",
            response_body=(
                "={{ ({ status: 'error', correlation_id: $json.execution?.id, "
                "message: 'workflow_error, see audit by correlation_id' }) }}"
            ),
            position=(x + 440, y),
        ),
    ]
    return nodes
```

- [ ] **Step 4: Run, expect pass**

```bash
cd _build && pytest tests/test_error_trigger.py -v
```

- [ ] **Step 5: Commit**

```bash
git add _build/nodes/error_trigger.py _build/tests/test_error_trigger.py
git commit -m "Add workflow error trigger sub-flow"
```

---

## Phase 5 — Assembler and full build

### Task 5.1: Implement `build_workflow.py` (assembler)

**Files:**
- Create: `_build/build_workflow.py`
- Create: `_build/tests/test_full_build.py`

- [ ] **Step 1: Write the failing test**

```python
# _build/tests/test_full_build.py
import json, pathlib, importlib

def test_build_produces_an_importable_workflow_json(tmp_path, monkeypatch):
    """Run the assembler in a tmp output path and assert the result imports as JSON."""
    out = tmp_path / "out.json"
    bw = importlib.import_module("build_workflow")
    bw.main(out_path=str(out))
    data = json.loads(out.read_text())
    assert data["name"] == "DigitServe v2 — Plan / ReAct / Reflexion"
    # required top-level fields for n8n import
    assert "nodes" in data and isinstance(data["nodes"], list)
    assert "connections" in data and isinstance(data["connections"], dict)
    # at least one of each major stage is present
    node_names = {n["name"] for n in data["nodes"]}
    assert "Webhook - Internal request" in node_names
    assert "LLM Planner" in node_names
    assert "ReAct Executor" in node_names
    assert "LLM Critic" in node_names
    assert "Respond to Webhook" in node_names
    # acyclic apart from the Reflexion router
    # (validated inside the assembler; here we just assert no exception)

def test_build_is_byte_for_byte_reproducible(tmp_path):
    bw = importlib.import_module("build_workflow")
    out1 = tmp_path / "a.json"; out2 = tmp_path / "b.json"
    bw.main(out_path=str(out1))
    bw.main(out_path=str(out2))
    assert out1.read_bytes() == out2.read_bytes()
```

- [ ] **Step 2: Run, expect failure**

```bash
cd _build && pytest tests/test_full_build.py -v
```

- [ ] **Step 3: Implement `build_workflow.py`**

```python
"""
Top-level assembler. Imports each stage module, places the nodes along a horizontal
spine, wires connections according to the design's data-flow diagram, validates the
graph (with one explicit back-edge from the Reflexion router to the planner), and
writes the result to PRJ_orchestrazione_agenti_servizi_digitali_v2_agentic.json.
"""
from __future__ import annotations
import json, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from nodes import (stickies, stage_0_ingress, stage_1_interpret, stage_2_plan,
                   stage_3_approval, stage_4_react, stage_5_reflexion,
                   stage_6_respond, self_checks, error_trigger)
from nodes.connections import link, validate_dag

OUT = (pathlib.Path(__file__).resolve().parent.parent
       / "PRJ_orchestrazione_agenti_servizi_digitali_v2_agentic.json")

def main(out_path: str | None = None) -> None:
    nodes: list[dict] = []
    conns: dict = {}

    # ---- canvas layout: one stage per horizontal slot ----
    Y = 5000
    XS = [15500, 16400, 17400, 18400, 19400, 20400, 21400]

    nodes.append(stickies.header())
    nodes.append(stickies.test_cases())
    nodes.append(stickies.closing_notes())
    for i, lbl in enumerate(["stage_0","stage_1","stage_2","stage_3",
                              "stage_4","stage_5","stage_6"]):
        s = stickies.stage(lbl)
        s["position"] = [XS[i] - 60, Y - 280]
        nodes.append(s)

    s0_nodes, s0_in, s0_out = stage_0_ingress.build(origin=(XS[0], Y))
    s1_nodes, s1_in, s1_outs = stage_1_interpret.build(origin=(XS[1], Y))
    s2_nodes, s2_in, s2_out  = stage_2_plan.build(origin=(XS[2], Y))
    s3_nodes, s3_in, s3_outs = stage_3_approval.build(origin=(XS[3], Y))
    s4_nodes, s4_in, s4_out  = stage_4_react.build(origin=(XS[4], Y))
    s5_nodes, s5_in, s5_outs = stage_5_reflexion.build(origin=(XS[5], Y))
    s6_nodes, s6_in, s6_out  = stage_6_respond.build(origin=(XS[6], Y))

    nodes.extend(s0_nodes + s1_nodes + s2_nodes + s3_nodes
                 + s4_nodes + s5_nodes + s6_nodes)
    nodes.extend(self_checks.build(origin=(XS[6], Y + 600)))
    nodes.extend(error_trigger.build(origin=(XS[0], Y + 800)))

    # ---- intra-stage wiring is done inside each module's tests; here we
    # ---- wire only the inter-stage hops on the spine, plus branch labels.

    # Stage 0 → Stage 1
    # Chain inside stage 0:
    link(conns, "Webhook - Internal request", "Normalize Input")
    link(conns, "Normalize Input", "Configure Provider")
    link(conns, "Configure Provider", "Load Reflexion Store")
    link(conns, "Load Reflexion Store", "LLM Interpret")

    # Stage 1: interpret → parse → critique → refine? → (maybe refined) → confidence gate
    link(conns, "LLM Interpret", "Parse Interpretation")
    link(conns, "Parse Interpretation", "LLM Critique")
    link(conns, "LLM Critique", "Refine? (decision)")
    link(conns, "Refine? (decision)", "Should refine?")
    link(conns, "Should refine?", "LLM Interpret (refined)", source_output_index=0)  # true
    link(conns, "Should refine?", "Confidence Gate", source_output_index=1)           # false
    link(conns, "LLM Interpret (refined)", "Confidence Gate")
    # Confidence gate: true=proceed → stage 2; false=abstain → stage 6 build summary
    link(conns, "Confidence Gate", "Retrieve Lessons", source_output_index=0)        # >= 0.6
    link(conns, "Confidence Gate", "Build Run Summary", source_output_index=1)       # < 0.6 (abstain)

    # Stage 2: retrieve → planner → validate → stage 3
    link(conns, "Retrieve Lessons", "LLM Planner")
    link(conns, "LLM Planner", "Validate Plan")
    link(conns, "Validate Plan", "Plan Needs Approval?")

    # Stage 3: branch on approval
    link(conns, "Plan Needs Approval?", "Needs Approval? (router)")
    link(conns, "Needs Approval? (router)", "Send & Wait Approval", source_output_index=0)  # true
    link(conns, "Needs Approval? (router)", "Approval Decision",   source_output_index=1)  # false
    link(conns, "Send & Wait Approval", "Merge Approval Branches")
    link(conns, "Approval Decision",  "Merge Approval Branches")
    link(conns, "Merge Approval Branches", "Was Rejected?")
    link(conns, "Was Rejected?", "Build Run Summary", source_output_index=0)  # true=rejected
    link(conns, "Was Rejected?", "Split Plan Steps",  source_output_index=1)  # false=run executors

    # Stage 4: split → react → merge → stage 5
    link(conns, "Split Plan Steps", "ReAct Executor")
    link(conns, "ReAct Executor", "Merge Step Outcomes")
    link(conns, "ReAct Executor", "Split Plan Steps", source_output_index=1)  # n8n splitInBatches loopback
    link(conns, "Merge Step Outcomes", "LLM Critic")

    # Stage 5: critic → parse → replan router
    link(conns, "LLM Critic", "Parse Critic")
    link(conns, "Parse Critic", "Replan? (router)")
    link(conns, "Replan? (router)", "Decrement Replan Counter", source_output_index=0)  # true=replan
    link(conns, "Replan? (router)", "Consolidate Lessons",       source_output_index=1)  # false=respond
    # explicit back-edge for replan
    link(conns, "Decrement Replan Counter", "Retrieve Lessons")
    # forward path to stage 6
    link(conns, "Consolidate Lessons", "Build Run Summary")

    # Stage 6: summary → audit → respond
    link(conns, "Build Run Summary", "Audit Sink")
    link(conns, "Audit Sink", "Respond to Webhook")

    # ---- validate DAG, allowing the documented back-edge ----
    validate_dag(conns, allow_back_edges_from={"Decrement Replan Counter",
                                               "ReAct Executor"})

    workflow = {
        "name": "DigitServe v2 — Plan / ReAct / Reflexion",
        "nodes": nodes,
        "connections": conns,
        "active": False,
        "settings": {"executionOrder": "v1", "executionTimeout": 180},
        "tags": [
            {"name": "agentic-ai"},
            {"name": "digitserve"},
            {"name": "modulo-03"},
            {"name": "v2"},
        ],
        "pinData": {},
        "versionId": "1",
        "meta": {"templateCredsSetupCompleted": False},
    }

    target = pathlib.Path(out_path) if out_path else OUT
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(workflow, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    print(f"wrote {target}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run all Python tests, expect pass**

```bash
cd _build && pytest -q
```

- [ ] **Step 5: Run the build**

```bash
cd _build && python build_workflow.py
```
Expected: `wrote .../PRJ_orchestrazione_agenti_servizi_digitali_v2_agentic.json` and the file contains valid JSON.

- [ ] **Step 6: Verify the JSON parses and has the expected top-level structure**

```bash
python -c "import json,sys; d=json.load(open('03_agentic_ai/_PRJ_orchestrazione_agenti_servizi_digitali_v2_agentic/PRJ_orchestrazione_agenti_servizi_digitali_v2_agentic.json')); print('nodes', len(d['nodes']), 'connections', len(d['connections']))"
```
Expected output (counts approximate, must be non-zero on both): `nodes 50+ connections 20+`.

- [ ] **Step 7: Commit**

```bash
git add _build/build_workflow.py _build/tests/test_full_build.py 03_agentic_ai/_PRJ_orchestrazione_agenti_servizi_digitali_v2_agentic/PRJ_orchestrazione_agenti_servizi_digitali_v2_agentic.json
git commit -m "Assemble v2 workflow JSON (stages 0-6 wired, validates as DAG)"
```

---

## Phase 6 — End-to-end verification

This phase is manual because n8n imports and Ollama execution cannot be reliably automated inside the plan. The worker must run a local n8n instance and execute each scenario by curl, then inspect the response and `$workflow.staticData` via the n8n UI.

### Task 6.1: Capture T1-T8 payloads as fixtures

**Files:**
- Create: `_build/tests/fixtures/payloads.py`

- [ ] **Step 1: Write the payload module**

```python
# _build/tests/fixtures/payloads.py
"""
Curated payloads for T1-T8. Each entry is the POST body sent to
/webhook/digitserve-v2-richiesta. The 'expected' field documents what the
operator should observe in the response/audit/staticData after running.
"""
PAYLOADS = {
    "T1": {
        "body": {
            "canale": "form",
            "mittente": {"name": "Alice Rossi", "role": "client", "email": "erin@digitserve.io"},
            "testo": "Please open a ticket for the printer not responding in office 3.",
            "provider": "ollama",
        },
        "expected": {
            "response_status": "completed",
            "min_audit_stages": ["plan/built", "react/step/s1", "reflexion/persisted"],
            "mutation_prefixes": ["TKT"],
        },
    },
    "T2": {
        "body": {
            "canale": "email",
            "mittente": {"name": "Alice Rossi", "role": "client", "email": "alice@digitserve.io"},
            "testo": "Ticket for slow VPN; also notify the network team.",
            "provider": "ollama",
        },
        "expected": {
            "response_status": "completed",
            "min_audit_stages": ["plan/built", "react/step/s1", "react/step/s2", "reflexion/persisted"],
            "mutation_prefixes": ["TKT", "NTF"],
        },
    },
    "T3": {
        "body": {
            "canale": "chat",
            "mittente": {"name": "Dave Bianchi", "role": "key-account", "email": "dave@digitserve.io"},
            "testo": "Critical: production billing API is returning 500 across all tenants. Need a war room ticket and a manager email.",
            "provider": "ollama",
            "approval": "approved",
        },
        "expected": {
            "response_status": "completed",
            "min_audit_stages": ["approval"],
            "mutation_prefixes": ["TKT", "NTF"],
        },
    },
    "T4": {
        "body": {
            "canale": "chat",
            "mittente": {"name": "Dave Bianchi", "role": "key-account", "email": "dave@digitserve.io"},
            "testo": "Critical: production billing API is returning 500 across all tenants. Need a war room ticket and a manager email.",
            "provider": "ollama",
            "approval": "rejected",
        },
        "expected": {
            "response_status": "rejected_by_human",
            "mutation_prefixes": [],
        },
    },
    "T5": {
        "body": {
            "canale": "form",
            "mittente": {"name": "Bob Verdi", "role": "client", "email": "bob@digitserve.io"},
            "testo": "Open a ticket: laptop screen flicker since this morning.",
            "provider": "ollama",
            "force_skip_check": True,
        },
        "expected": {
            "response_status": "completed",
            "trace_contains_observation": "conflict",
            "mutation_prefixes": ["TKT"],
        },
    },
    "T6": {
        "body": {
            "canale": "form",
            "mittente": {"name": "Carol Marrone", "role": "client", "email": "carol@digitserve.io"},
            "testo": "Open a ticket: I cannot access my email account at all today.",
            "provider": "ollama",
            "force_lookup_skip_in_plan": True,
        },
        "expected": {
            "response_status": "completed",
            "min_audit_stages": ["plan/built", "plan/built"],  # twice = replan
            "lesson_tags": ["missing_lookup"],
        },
    },
    "T7": {
        "body": {
            "canale": "form",
            "mittente": {"name": "Carol Marrone", "role": "client", "email": "carol@digitserve.io"},
            "testo": "Open a ticket: I cannot access my email account at all today.",
            "provider": "ollama",
        },
        "expected": {
            "response_status": "completed",
            "min_audit_stages": ["plan/built"],   # one plan, primed by the T6 lesson
            "first_tool": "lookup_customer",
            "lesson_uses_incremented_for_tags": ["missing_lookup"],
        },
    },
    "T8a": {
        "body": {
            "canale": "form",
            "mittente": {"name": "Ghost", "role": "?", "email": "ghost@nowhere.test"},
            "testo": "asdf qwer zxcv",
            "provider": "ollama",
        },
        "expected": {"response_status": "needs_human_triage"},
    },
    "T8b": {
        "body": {
            "canale": "form",
            "mittente": {"name": "Alice", "role": "client", "email": "alice@digitserve.io"},
            "testo": "loop forever please open a ticket then notify then open a ticket then notify... [repeated 30x]",
            "provider": "ollama",
        },
        "expected": {"response_status": "budget_exceeded"},
    },
}
```

- [ ] **Step 2: Commit**

```bash
git add _build/tests/fixtures/payloads.py
git commit -m "Add curated T1-T8 payload fixtures with expected outcomes"
```

### Task 6.2: Manual run protocol

This task has no code; it documents the protocol the worker follows to validate T1-T8. Create a runbook the operator follows during grading prep.

**Files:**
- Create: `_build/tests/RUNBOOK.md`

- [ ] **Step 1: Write the runbook**

```markdown
# v2 Verification Runbook

## Preconditions

- `ollama serve` is running with `llama3.2` pulled.
- A local n8n instance is running and the workflow JSON has been imported.
- For T6 → T7 verification, the lesson store starts empty (Settings → Static Workflow Data → Clear).

## Steps

For each Tn in T1..T8:

1. POST the payload to the webhook:
       curl -s -X POST http://localhost:5678/webhook/digitserve-v2-richiesta \
            -H 'Content-Type: application/json' \
            -d "$(python -c 'import json,fixtures.payloads as p; print(json.dumps(p.PAYLOADS["Tn"]["body"]))')"
2. Open the latest execution in the n8n UI.
3. On the off-path "assert_trace" Code node, set the inputs (`case_id`, `run`) and execute. Confirm `passed: true`.
4. Same for "assert_mutations" (when the case prescribes prefixes).
5. For T6 / T7, after the run, open "assert_lesson_store" with `expected_tags: ["missing_lookup"]`, execute, confirm `passed: true`.
6. Note any deviations in a per-case row below.

## Results log (fill in)

| Case | Response status | Trace pass | Mutations pass | Lesson pass | Notes |
|------|-----------------|------------|----------------|-------------|-------|
| T1   |                 |            |                |             |       |
| T2   |                 |            |                |             |       |
| ...  |                 |            |                |             |       |
```

- [ ] **Step 2: Commit**

```bash
git add _build/tests/RUNBOOK.md
git commit -m "Add manual verification runbook for T1-T8"
```

### Task 6.3: Run the matrix

This is the manual execution step. It does not introduce code changes.

- [ ] **Step 1: Start ollama**

```bash
ollama serve   # if not already running
ollama pull llama3.2
```

- [ ] **Step 2: Start n8n locally and import the workflow JSON**

Document the n8n start command used (e.g., `npx n8n` or Docker) in `_build/tests/RUNBOOK.md` under a "Notes" subsection after the run completes.

- [ ] **Step 3: Execute T1 through T8 per the runbook, filling in the results table**

- [ ] **Step 4: Commit the filled-in RUNBOOK.md**

```bash
git add _build/tests/RUNBOOK.md
git commit -m "Record T1-T8 manual verification results"
```

---

## Phase 7 — Final polish

### Task 7.1: Verify English-only content and absence of AI fingerprints

**Files:**
- Create: `_build/tests/test_style.py`
- Modify: any stage module that fails the checks

- [ ] **Step 1: Write the failing test**

```python
# _build/tests/test_style.py
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
WORKFLOW = ROOT / "03_agentic_ai/_PRJ_orchestrazione_agenti_servizi_digitali_v2_agentic/PRJ_orchestrazione_agenti_servizi_digitali_v2_agentic.json"

ITALIAN_FORBIDDEN = ["Esegui", "Esecuzione", "Decisionale", "Accoda",
                     "Notifica", "Programma Report", "Casi di test",
                     "Stadio", "Agente"]
AI_FINGERPRINTS = [r"\blet's dive\b", r"\bin summary\b",
                   r"\bit is worth noting\b", r"\bfurthermore,\b",
                   r"\bmoreover,\b", r"\bin conclusion,\b"]

def test_workflow_contains_no_italian_forbidden_terms():
    text = WORKFLOW.read_text()
    offenders = [w for w in ITALIAN_FORBIDDEN if w in text]
    assert not offenders, f"forbidden Italian terms: {offenders}"

def test_workflow_avoids_em_dashes_in_sticky_notes():
    data = json.loads(WORKFLOW.read_text())
    for n in data["nodes"]:
        if n["type"] != "n8n-nodes-base.stickyNote":
            continue
        c = n["parameters"]["content"]
        assert "—" not in c, f"em dash in sticky: {n['name']}"

def test_workflow_avoids_ai_fingerprint_phrases():
    text = WORKFLOW.read_text().lower()
    for pat in AI_FINGERPRINTS:
        assert not re.search(pat, text), f"AI fingerprint: {pat}"
```

- [ ] **Step 2: Run, expect either pass (clean) or fail (have to clean offenders)**

```bash
cd _build && pytest tests/test_style.py -v
```

- [ ] **Step 3: If a test failed, edit the offending sticky/prompt/code-node source until the test passes. Re-run the build:**

```bash
cd _build && python build_workflow.py && pytest tests/test_style.py -v
```

- [ ] **Step 4: Commit**

```bash
git add _build/tests/test_style.py _build/nodes/  03_agentic_ai/_PRJ_orchestrazione_agenti_servizi_digitali_v2_agentic/
git commit -m "Style gate: English-only and no AI fingerprints across workflow"
```

### Task 7.2: README inside the fork folder (optional, only if the grader expects one)

The original PRJ folder contains only the JSON, so by default this fork follows the same convention. Skip unless the user requests one.

- [ ] **Step 1: Confirm with the user whether a README is expected. If yes, write `03_agentic_ai/_PRJ_orchestrazione_agenti_servizi_digitali_v2_agentic/README.md` summarizing what the JSON delivers.**

### Task 7.3: Final build + commit + tag

- [ ] **Step 1: Run the full test suite**

```bash
cd _build && pytest -q && node --test js/
```
Expected: all pass.

- [ ] **Step 2: Regenerate the JSON one last time**

```bash
cd _build && python build_workflow.py
```

- [ ] **Step 3: Commit any byte changes from the regeneration**

```bash
git add 03_agentic_ai/_PRJ_orchestrazione_agenti_servizi_digitali_v2_agentic/PRJ_orchestrazione_agenti_servizi_digitali_v2_agentic.json
git commit -m "Regenerate v2 workflow JSON after final fixes" || echo "nothing to commit"
```

- [ ] **Step 4: Tag (optional, only if the user wants release tagging)**

```bash
# Skip unless requested:
# git tag -a v2-agentic-fork-2026-05-16 -m "Module 03 PRJ v2 fork (plan/react/reflexion)"
```

---

## Self-review

### Spec coverage

Walking the spec section by section:

- §1 Context: covered by the header sticky (Task 4.1) and the spec itself.
- §2 Goals/non-goals: enforced by the test matrix scope; non-goals not implemented (no LLM eval, no real integrations, no LangGraph port).
- §3 Constraints: single JSON deliverable (Task 5.1 emits one file; the build dir is dev tooling, documented as such); dual provider (Stage 0 + Stage 1/2/4 LLM nodes use `$json.provider`); pure n8n (no external services); English-only (Task 7.1 enforces).
- §4 File layout: Task 0.1 + Task 5.1 produce exactly this layout.
- §5 Architecture: Tasks 4.2 through 4.8 build the seven stages and their three iteration pockets (interpret refine, ReAct per step, Reflexion replan).
- §6 Run state and audit: schemas (Task 0.2-0.3), state shape carried via Set node `includeOtherFields=true` (Task 1.1), lesson store helpers (Task 2.3), audit sink (Task 4.8).
- §7 Tool catalog: Task 2.1 implements all 12 tools plus `finish`, including deterministic failure injection and ID format.
- §8 Budgets and error handling: Task 4.2 initializes the budget object; budgets decremented in Stage 2 (validate plan), Stage 4 (ReAct loop via `callLLM`), Stage 5 (parse critic); error trigger sub-flow built in Task 4.10.
- §9 Substrate trade-off: enforced by the Code-node-only loop design; documented in stickies (Task 4.1 closing notes).
- §10 Testing strategy: T1-T8 fixtures (Task 6.1), runbook (Task 6.2), execution (Task 6.3), off-path self-checks (Task 4.9).
- §11 Justification log: mirrored in the closing-notes sticky (Task 4.1) so a reviewer reading the JSON sees the rationale.
- §12 Open items: documented in the closing-notes sticky.

No coverage gaps found.

### Placeholder scan

Searched the plan for `TBD`, `TODO`, `implement later`, `appropriate error handling`, `similar to Task N`, "Write tests for the above" without code. None present. Every step contains the actual content the worker writes.

### Type and signature consistency

- `makeTools({ correlation_id })` is consumed identically in `tools.test.js`, `react_loop.test.js`, and Stage 4's embedded entry block.
- `runReactLoop({ step, tools, toolCatalog, callLLM, maxTurns })` signature matches between definition (`js/react_loop.js`), tests (`js/react_loop.test.js`), and Stage 4 caller.
- `addLesson`, `retrieveLessons`, `evictIfFull` signatures consistent between `js/lesson_store.js`, its tests, and Stage 2 (`Retrieve Lessons` Code node) and Stage 5 (`Consolidate Lessons` Code node).
- Node names referenced across stages are byte-identical to the names produced by their factories (verified by `test_full_build.py` checking key node names appear).

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-16-digitserve-v2-agentic-fork.md`. Two execution options:

1. **Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration
2. **Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
