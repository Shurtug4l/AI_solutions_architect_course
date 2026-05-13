# Deploying an Agent

## TL;DR

An agent that works in a notebook is not a service. Putting it behind an HTTP endpoint surfaces a different set of concerns from the ones that dominate exercises 01-06. Four pillars matter operationally: **stateless vs stateful**, **tool safety**, **containers**, and **secrets**. HTTP is stateless by default - every request stands alone - which is great for scaling but useless for a chatbot. The fix is a **session id** the client carries between turns, plus a structured request body (`user_id`, `session_id`, `message`) that gives every call enough context. Tools in production are **attack surfaces**: each one is a door to the outside world (DB, web, API) and needs authentication, authorisation, input validation, and the principle of least privilege. Long operations have to be split off into **async background tasks** behind a polling endpoint so the foreground `/chat` stays responsive under a hard 3-10 second timeout. **Docker** is the lockbox: a `Dockerfile` declares dependencies, the OS, and the entry point, producing an immutable **image** that runs identically anywhere. **Secrets never live in source code**: read them from environment variables, keep a `.env` file for local dev (gitignored), and use a real secret manager in production. The cost of every shortcut here shows up in production at the worst possible moment - a deployed agent fails differently from a notebook agent.

## Cheatsheet

| Concern | Mechanism | One-line |
|---|---|---|
| **State across turns** | Session id + server-side store | `session_id` in every request |
| **Structured request** | Pydantic / typed body | `user_id`, `session_id`, `message` |
| **Long operations** | Async background task + polling | Return `task_id`, client polls `/status` |
| **Foreground latency** | Hard timeout on `/chat` | 3-10s, return 504 if exceeded |
| **Tool safety** | Authn, authz, input validation, least privilege | Every tool is a door |
| **Reproducible deploy** | `Dockerfile` + pinned `requirements.txt` | Image is immutable; container is the running instance |
| **Health check** | Cheap `/health` endpoint | Always 200; no I/O |
| **Secrets** | Env vars + `.env` (gitignored) + secret manager in prod | `os.getenv("OPENAI_API_KEY")` only |

---

## From notebook to service

Module 03's exercises 01-06 produced agents that work in cells. This note (and exercise 07) is about the wrapper that turns a function into a service.

```
notebook agent                       deployed agent
────────────────                     ──────────────
                                              ┌────────────────────────┐
                                              │   HTTP request         │
                                              │ (user_id, session_id,  │
                                              │  message)              │
                                              └──────────┬─────────────┘
                                                         ▼
                                              ┌────────────────────────┐
                                              │ Validation (Pydantic)  │
                                              └──────────┬─────────────┘
                                                         ▼
                                              ┌────────────────────────┐
                                              │ Session lookup         │
                                              │ (state store)          │
                                              └──────────┬─────────────┘
                                                         ▼
   def agent(message):                        ┌────────────────────────┐
       ...                          ─────►    │ The same `agent`       │
                                              │ function as before     │
                                              └──────────┬─────────────┘
                                                         ▼
                                              ┌────────────────────────┐
                                              │ Response + session     │
                                              │ persisted              │
                                              └────────────────────────┘
```

The function in the middle does not change. Everything else is the wrapper that this note covers.

---

## Stateless vs Stateful

HTTP is stateless by design. The server receives a request, computes a response, sends it, forgets. For a chatbot this is the wrong default: the second turn needs to know what was said in the first.

| Stateless | Stateful |
|---|---|
| Each request stands alone | The server keeps the conversation across requests |
| No memory of who you are | Recognises returning users / sessions |
| Trivial to scale (any instance handles any request) | Sticky sessions or external store needed |
| Right for: weather APIs, lookups | Right for: chatbots, agents, anything with continuity |

The HTTP protocol does not pick a side; the application picks one. For an agent, **stateful** is the default, and the question becomes *where the state lives*.

### Session id

The standard mechanism. The first request creates a server-side session and returns a **session id**. The client carries the id in every subsequent request; the server uses it to look up the conversation history.

```
# Request 1: first interaction
POST /chat
{"message": "Hi, I'm Marco"}

# Response: the server creates a session_id
{"reply": "Hi Marco!",
 "session_id": "abc-123"}

# Request 2: include the session_id
POST /chat
{"message": "What is my name?",
 "session_id": "abc-123"}

# Response: the server remembers
{"reply": "Your name is Marco."}
```

The id is opaque to the client - it does not need to know what is inside the session. The server can swap the storage backend (in-memory dict, Redis, sqlite, Postgres) without changing the client.

### Structured request body

A bare `"message"` field is not enough. A production agent needs at least:

- `user_id` - who is talking; needed for rate limiting, audit, permissions.
- `session_id` - which conversation, as above.
- `message` - the actual content.
- `context` - optional, carries language, platform, locale.

```
POST /api/chat
Content-Type: application/json

{
  "user_id":    "user_42",
  "session_id": "abc-123",
  "message":    "What are my orders?",
  "context":    {"language": "it", "platform": "web"}
}
```

Validating this at the boundary (Pydantic in Python, `zod` in TypeScript, etc.) catches malformed requests before they reach the agent. The validator is doing real defensive work even when the schema looks trivial: stripping whitespace, capping length, refusing empty fields - things you do not want every handler to repeat.

### Where the session store lives

| Backend | Pros | Cons |
|---|---|---|
| **In-memory dict** | Zero config, fastest | Single instance only, lost on restart |
| **Redis** | Sub-millisecond reads, easy TTL | Adds a dependency |
| **sqlite (WAL mode)** | Single-file, persistent | Single-instance writes |
| **Postgres / managed DB** | Multi-instance, durable | More ops overhead |

For 10 concurrent users an in-memory dict with periodic snapshots is enough. For 10,000 you need Redis. Module 03 exercise 07 ships with the in-memory version on purpose; the interface is the same in either case.

---

## Tools in production

In a notebook a tool is a Python function. In production a tool is a **door**: it reads from a database, calls an external API, executes a side effect. Each door needs guarding.

### Protected vs unprotected

| Unprotected (anti-pattern) | Protected |
|---|---|
| Credentials in source code | Credentials in environment variables / secret manager |
| No input validation | Validated and sanitised input |
| Unbounded DB access | Least-privilege account (read-only, scoped) |
| No logging | Every operation logged with user id and arguments |

Module 03 exercise 07 implements this discipline on the `search_product` tool: an `os.getenv` for the database URL, a `sanitize` function that strips SQL-injection metacharacters, and an `INFO` log on every call.

### Five rules

1. **Every tool is an attack surface.** Treat it like a public API: authn, authz, validation, audit.
2. **Never hardcode credentials.** Read from env vars; rotate without touching code.
3. **Principle of least privilege.** The DB user the tool reads with should not be able to write. The API key the tool uses should be scoped to the minimum endpoints needed.
4. **Validate every input.** Sanitise SQL-injection metacharacters, cap length, reject suspicious characters. Cheap defence in depth.
5. **Log every operation.** Who, when, what arguments, what response. This is what makes a post-mortem possible.

### Timeouts: the inversion of control

A tool can take milliseconds or minutes. The user-facing `/chat` cannot wait minutes. The fix is a **timeout** + a separate path for long jobs.

```python
import asyncio
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        result = await asyncio.wait_for(
            run_agent(req.message),
            timeout=10.0,           # max 10 seconds in the foreground
        )
        return {"reply": result}
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="The agent is taking too long; please try again in a moment.",
        )
```

Three things this does right:

- The **timeout is short** (3-10 seconds). Interactive UX demands sub-10s.
- **504 Gateway Timeout** is the right status code: the upstream agent did not respond in time.
- The **detail is human-readable**, not a stack trace. The client surfaces it to the user.

| Without timeout | With timeout |
|---|---|
| Client waits indefinitely | Bounded wait |
| TCP connection drops after ~60s | Clean error after N seconds |
| Generic "Network error" surfaces | Specific 504 with retry guidance |
| Server worker pinned waiting | Worker freed for the next request |

### Async / polling pattern for long jobs

When a job genuinely takes minutes (large reports, multi-step analysis), the client cannot block on it. The split:

```
# Submit
POST /report  → returns immediately
              { "task_id": "xyz-789" }

# Poll
GET /report/status/xyz-789  → status: queued | processing | completed
                              result: { ... } when completed
```

The server accepts the work, returns a `task_id` synchronously, then runs the job in the background (an `asyncio.create_task`, or a worker queue like Celery / RQ for real production). The client polls until completion.

Alternatives to polling: **server-sent events** for streaming progress; **webhooks** for push notification when done. Polling is the simplest and works without client-side complexity.

---

## Containers

Dependencies are the silent killer of deployments. Python alone has dozens of libraries with overlapping version constraints; add `litellm`, `langchain`, `langchain-ollama`, an embedder, a vector DB, FastAPI, uvicorn, and the install starts producing "it works on my PC" outcomes.

### What a container is

Docker bundles the OS, the Python interpreter, the libraries, and the application code into a single immutable artifact - an **image** - that runs identically anywhere a Docker runtime exists.

| Without Docker | With Docker |
|---|---|
| Dependencies installed by hand | Dependencies declared in `Dockerfile` |
| "Works on my PC" | Identical behaviour everywhere |
| Version conflicts between projects | Isolated environment, zero conflicts |
| Each machine is different | One configuration, reproducible builds |
| Painful debugging | Predictable deploy |

### Image vs container

| Image | Container |
|---|---|
| Immutable file with build instructions | Live instance running from an image |
| Created with `docker build` | Created with `docker run` |
| Template / recipe, shareable | Ephemeral, dies when stopped |
| Stored on disk / in a registry | Lives in memory (runtime) |

The recipe is the **manual**, the container is the **chef following the manual**. One image creates N identical containers; the containers can be killed and recreated without losing the recipe.

### A working Dockerfile for an agent

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "agent:app", "--host", "0.0.0.0", "--port", "8000"]
```

Six lines, six decisions:

- `FROM python:3.10-slim` - a lean Python base image; smaller and faster than the full one.
- `WORKDIR /app` - all subsequent paths relative to this.
- `COPY requirements.txt .` then `RUN pip install` - copy *first*, then install. Docker caches the layer; subsequent builds skip the pip install if the requirements have not changed.
- `COPY . .` - copy the application source.
- `EXPOSE 8000` - document the port the service listens on.
- `CMD [...]` - the command Docker runs when the container starts.

### Essential commands

```bash
# Build the image from the Dockerfile in the current directory
docker build -t my-agent .

# Start a container from the image
docker run -d --name agent1 my-agent

# List running containers
docker ps

# Read the container's logs
docker logs agent1
```

### What this Dockerfile is missing for real production

Module 03 exercise 07's critical analysis lists four upgrades, each one line and a measurable improvement:

| Upgrade | Why |
|---|---|
| `USER appuser` before `CMD` | Non-root user; reduces blast radius of a container compromise |
| Multi-stage build (builder + runtime) | Smaller final image; no pip / build tools in production |
| `--workers 4` on uvicorn | Handle concurrent CPU-bound requests |
| Healthcheck with backoff | Faster detection of startup failures |

### docker-compose for local orchestration

For a multi-service stack (agent + Redis + vector DB + monitoring) the right abstraction is `docker-compose.yml`:

```yaml
version: "3.8"
services:
  agent:
    build: .
    ports: ["8000:8000"]
    env_file: [.env]
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
```

One-command local deploy: `docker compose up`. In real production this is replaced by Kubernetes, ECS, or a managed PaaS, but the same primitives apply.

### `/health` should be cheap

Healthcheck endpoints have one job: tell the orchestrator the process is alive. Two anti-patterns:

- **Doing work in `/health`** (querying the DB, calling the LLM). Under load the healthcheck times out, the orchestrator concludes the pod is dead, kills healthy pods.
- **No `/health` at all.** The orchestrator has no signal; it cannot restart a wedged container.

The right shape: always 200, fixed JSON, no I/O. The orchestrator hits it every few seconds; anything heavier than that is a recipe for false negatives.

---

## Secrets and environment variables

LLM agents talk to paid services. Every call needs an API key. Every key is a credential. Every credential needs the same hygiene as a password.

### The single rule

> API keys are secrets. They never live in source code.

A key committed to git is a public key. Bots scan GitHub continuously for `sk-...` patterns; the time from commit to compromise is measured in seconds, not days. The financial damage from a leaked key can run into thousands of dollars before the rotation happens.

### Wrong vs right

**Wrong** (this code looks innocuous and is dangerous):

```python
import openai
api_key = "<YOUR-API-KEY-HERE>"   # NEVER do this in real code
client = openai.OpenAI(api_key=api_key)
```

The key is visible in the file. The file goes on git. The key is compromised.

**Right**:

```python
import os
import openai

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set")

client = openai.OpenAI(api_key=api_key)
```

The code knows *which* key it needs, never the *value*. The value is provided at runtime by the environment.

### How to set env vars

| Where | How |
|---|---|
| Terminal | `export OPENAI_API_KEY="sk-..."` |
| Docker | `docker run -e OPENAI_API_KEY="sk-..." my-agent` |
| docker-compose | `env_file: [.env]` |
| Kubernetes | `Secret` mounted as env var |
| Cloud (AWS / GCP / Azure) | Secret manager (Vault, AWS Secrets Manager, GCP Secret Manager) |

### The `.env` pattern

For local development, a `.env` file collects all the variables in one place:

```
# .env (development only, never commit)
OPENAI_API_KEY=sk-...
DATABASE_URL=postgres://localhost/agent
LOG_LEVEL=info
```

The application reads it via `python-dotenv`:

```python
from dotenv import load_dotenv
load_dotenv()
```

Three files always work together:

| File | Purpose | Committed? |
|---|---|---|
| `.env` | Real local values | **No** |
| `.env.example` | Schema only, no real values | **Yes** |
| `.gitignore` | Excludes `.env`, re-includes `.env.example` | **Yes** |

```
# .gitignore
.env
.env.*
!.env.example
__pycache__/
*.pyc
```

The `!.env.example` line is the bang re-include: even though `.env.*` matches, the example file is explicitly allowed through.

### `.env.example` carries the schema

```
# Copy this file to .env and fill in real values.
OPENAI_API_KEY=your-key-here
DATABASE_URL=postgres://localhost/agent
LOG_LEVEL=info
```

The string `your-key-here` is deliberately NOT in the `sk-...` shape. The point of the example file is to document **which** variables exist, not to provide a working credential.

### Hardcoded vs env var: the trade-offs

| Hardcoded | Environment variable |
|---|---|
| Visible in source | Out of source entirely |
| Not portable across environments | Portable; each env has its own values |
| Rotation requires a code change + redeploy | Rotation is a `.env` edit + restart |
| Leaks on the first commit | No git exposure |

### `.env` is the floor, not the ceiling

In production the `.env` file is replaced by a **secret manager**:

- AWS Secrets Manager / Parameter Store.
- GCP Secret Manager.
- HashiCorp Vault.
- Azure Key Vault.

The container fetches the secret at startup via an IAM-authenticated call. The raw value never lives on disk. Rotation is automatic. Compromised CI does not leak production credentials. Same `os.getenv()` API on the application side; different backend behind it.

---

## Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Session in memory, multiple instances | User loses their thread when load-balanced to a different instance | Sticky sessions or external session store |
| Sessions never expire | Memory grows indefinitely | TTL on the store; eviction policy |
| No timeout on `/chat` | Worker pinned indefinitely on a slow agent | `asyncio.wait_for(..., timeout=...)` |
| Long job blocking the foreground | Whole service degrades | Move long jobs to `/report` + polling |
| `/health` doing work | False negatives under load | Make it return a constant; no I/O |
| Tool with hardcoded credentials | Leak risk + impossible rotation | `os.getenv`, secret manager |
| Tool with DB write privilege used for reads | Compromise blast radius is the whole DB | Read-only user for read-only tools |
| `.env` committed once and rotated | Old key is in git history forever | Treat any committed key as compromised; rotate immediately |
| `Dockerfile` runs as root | Container compromise = host compromise | `USER appuser` before `CMD` |
| Single-stage build with pip in the image | Bigger image, pip CVEs in production | Multi-stage build: pip in builder, copy installed packages to runtime |
| Unpinned `requirements.txt` | Next pip resolve changes versions, breaks build | Pin every dependency |
| `latest` Docker tag in compose | Subtle silent updates | Pin to a specific image tag |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Stateless lookup endpoint | No session id needed | Simpler is better when state is not required |
| Multi-turn chat | Session id + server-side store | Continuity is the product |
| Long job (analysis, report, batch) | Async submit + polling | Foreground stays responsive |
| Multiple instances + session continuity | External session store (Redis) | In-memory does not survive load balancing |
| Local dev | `.env` + python-dotenv | One file, one place |
| Production | Secret manager | Rotation, audit, IAM scoping |
| Single-service local deploy | Docker (image + container) | Reproducible, isolated |
| Multi-service stack | docker-compose | One-command orchestration |
| Production at scale | Kubernetes / ECS / managed PaaS | Compose does not scale operationally |
| Foreground latency-sensitive | Hard timeout + 504 + retry guidance | Worse to hang than to fail fast |

---

## See also

### Other notes
- [01_agents_vs_workflows.md](01_agents_vs_workflows.md) — the agent that gets wrapped here
- [02_agent_components.md](02_agent_components.md) — tools, the surface this note hardens
- [04_frameworks.md](04_frameworks.md) — LangChain / LangGraph agents are what `run_agent` typically calls
- [05_short_term_memory.md](05_short_term_memory.md) — the session store is the production version of STM
- [06_long_term_memory.md](06_long_term_memory.md) — vector DB persistence and the same secret hygiene applies to the embedder API key

### Exercises that exercise the concepts in this note
- [`07_ex_shopassist_deployment.ipynb`](../exercises/07_ex_shopassist_deployment.ipynb) — full ShopAssist deployment: Pydantic-validated requests, session manager, sanitised tool, FastAPI with `/chat` timeout and `/report` async pattern, Dockerfile + .env hygiene + docker-compose with healthcheck
