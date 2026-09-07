# AI-Powered Workforce and Technology Recommendation Assistant

A chat assistant that answers questions about **your company's people** and about **current open-source projects on GitHub** — and can combine both in a single answer.

Ask *"Which of our employees know Python?"* and it reads your internal database. Ask *"Find popular FastAPI repositories"* and it calls the live GitHub API. Ask *"Recommend a GitHub project for our FastAPI developers"* and it does both, then merges the results.

Everything runs on your own machine. The language model is local (Ollama), so no question or company data is sent to an external AI provider.

---

## Table of contents

- [What it can do](#what-it-can-do)
- [How it works](#how-it-works)
- [Architecture](#architecture)
- [Technology used](#technology-used)
- [Getting started](#getting-started)
- [Configuration](#configuration)
- [API reference](#api-reference)
- [The assistant's tools](#the-assistants-tools)
- [Database](#database)
- [Conversation memory](#conversation-memory)
- [Semantic cache](#semantic-cache)
- [Project structure](#project-structure)
- [Development](#development)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

---

## What it can do

| Kind of question | Where the answer comes from | Example |
|---|---|---|
| General knowledge | The local AI model only | "What is the difference between FastAPI and Flask?" |
| Internal people data | Your PostgreSQL database | "Which internal employees know Python?" |
| Live GitHub data | The GitHub REST API | "Find popular FastAPI repositories on GitHub." |
| Both combined | Database **and** GitHub together | "Recommend a GitHub project for employees with FastAPI experience." |

Every answer tells you where it came from, using one of four labels:

- `llm` — the model answered from its own knowledge
- `postgresql` — internal company data was used
- `github_mcp` — live GitHub data was used
- `multi_source` — both internal and GitHub data were used

Other things it does:

- **Remembers the conversation.** You can say "tell me more about the first one" and it understands.
- **Keeps separate chats.** Each session has its own history and its own cache.
- **Reuses similar answers.** Ask nearly the same question twice and the second answer is instant.
- **Never invents facts.** The system prompt forbids making up employee records or GitHub statistics.

---

## How it works

When you send a question, this is what happens:

```
1. Clean up the question (trim spaces, collapse line breaks)
2. Check the session exists                    → 404 if it does not
3. Load the conversation history from Redis
4. Look in the semantic cache
      ├── similar question found (≥ 0.92 match) → return the saved answer, done
      └── nothing similar found                 → continue
5. Run the AI agent
      ├── the model decides which tools it needs
      ├── internal tools  → PostgreSQL
      └── GitHub tools    → MCP server → GitHub API
6. Save the question and answer to the conversation history
7. Save the answer to the semantic cache for next time
8. If the chat is still called "New conversation", rename it after the question
9. Return the answer, the source label, and the list of tools used
```

Two details worth knowing:

- **A cache hit still gets recorded in your history**, so the conversation reads normally.
- **If saving to the cache fails, the answer is still returned.** A cache problem never costs you a good answer.

---

## Architecture

Five containers, plus Ollama running directly on your machine.

```
                    ┌───────────────────────┐
   your browser ───▶│  Frontend  (Next.js)  │  :3000
                    └───────────┬───────────┘
                                │  HTTP / JSON
                    ┌───────────▼───────────┐
                    │  Backend  (FastAPI)   │  :8000
                    └───┬───────┬───────┬───┘
                        │       │       │
        ┌───────────────┘       │       └────────────────┐
        │                       │                        │
┌───────▼────────┐   ┌──────────▼─────────┐   ┌──────────▼──────────┐
│  PostgreSQL    │   │      Redis         │   │   MCP Server        │  :8001
│  :5432         │   │      :6379         │   │   (FastMCP)         │
│                │   │                    │   └──────────┬──────────┘
│ people, skills │   │ chat history       │              │
│ departments    │   │ semantic cache     │              ▼
└────────────────┘   └────────────────────┘      GitHub REST API

                    ┌───────────────────────┐
                    │  Ollama (on the host) │  :11434
                    │  chat + embeddings    │
                    └───────────────────────┘
```

**Why is Ollama outside Docker?** So it can use your machine's GPU and so the models stay on disk between rebuilds. The backend reaches it at `host.docker.internal:11434`.

**Why a separate MCP server?** MCP (Model Context Protocol) is a standard way to expose tools to an AI model. Keeping GitHub access in its own service means the backend does not need to know anything about the GitHub API — it just discovers whatever tools the MCP server offers.

### The services

| Service | Port | What it does |
|---|---|---|
| `frontend` | 3000 | The chat interface |
| `backend` | 8000 | The API, the AI agent, memory, and caching |
| `mcp-server` | 8001 | Exposes GitHub search as AI tools |
| `postgres` | 5432 | Stores employees, departments, and skills |
| `redis` | 6379 | Stores chat history and the semantic cache |

Startup order is enforced: Postgres and Redis must report healthy, and the MCP server must be started, before the backend runs. The frontend waits until the backend is healthy.

---

## Technology used

**Frontend** — Next.js 16, React 19, TypeScript, Tailwind CSS 4, Zod (validates every API response), Vitest

**Backend** — FastAPI, LangChain, SQLAlchemy 2 (async) with asyncpg, Alembic, Pydantic v2, redis-py, pytest

**MCP server** — FastMCP, httpx, Pydantic v2

**Infrastructure** — Docker Compose, PostgreSQL 17, Redis 8, Ollama

---

## Getting started

### 1. What you need first

- **Docker Desktop** (or Docker Engine with the Compose plugin)
- **Ollama**, installed and running on your machine — <https://ollama.com>
- About **8 GB of free RAM** and **10 GB of disk space**

### 2. Download the AI models

The assistant needs two models. Pull them before the first run:

```bash
ollama pull qwen3:8b          # answers questions and picks tools
ollama pull embeddinggemma    # powers the semantic cache
```

Check they arrived:

```bash
ollama list
```

### 3. Create your environment file

```bash
cp .env.example .env
```

The defaults work as-is. See [Configuration](#configuration) if you need to change ports or add a GitHub token.

### 4. Start everything

```bash
docker compose up --build
```

The first run takes a while — it builds three images, then the backend creates the database tables and loads sample data.

### 5. Open it

| What | Where |
|---|---|
| The chat app | <http://localhost:3000> |
| API docs (interactive) | <http://localhost:8000/docs> |
| Health check | <http://localhost:8000/api/v1/health> |

A healthy system returns `"status": "ok"`. If it says `"degraded"`, one dependency is down — the response names which one.

### 6. Stopping

```bash
docker compose down            # stop, keep the data
docker compose down -v         # stop and erase the database and cache
```

---

## Configuration

Settings live in the root `.env` file (used by Docker Compose) and are passed to the backend in `compose.yaml`.

### Commonly changed

| Variable | Default | Meaning |
|---|---|---|
| `FRONTEND_PORT` | `3000` | Port for the web app |
| `BACKEND_PORT` | `8000` | Port for the API |
| `MCP_SERVER_PORT` | `8001` | Port for the MCP server |
| `POSTGRES_PORT` | `5432` | Port for the database |
| `REDIS_PORT` | `6379` | Port for Redis |
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` | Where the browser finds the API — **must match `BACKEND_PORT`** |
| `GITHUB_TOKEN` | *(empty)* | Optional. Raises the GitHub rate limit from 60 to 5,000 requests/hour |
| `OLLAMA_CHAT_MODEL` | `qwen3:8b` | The model that answers |
| `OLLAMA_EMBEDDING_MODEL` | `embeddinggemma` | The model used for cache matching |

### Backend tuning (set in `compose.yaml`)

| Variable | Default | Meaning |
|---|---|---|
| `SEED_DATABASE` | `true` | Load the sample employees on startup. Set `false` to skip |
| `AGENT_MAX_ITERATIONS` | `8` | How many tool-calling rounds the agent may take |
| `CONVERSATION_MAX_MESSAGES` | `40` | Messages kept per chat |
| `CONVERSATION_TTL_SECONDS` | `86400` | Chats expire after 24 hours |
| `SEMANTIC_CACHE_ENABLED` | `true` | Turn answer reuse on or off |
| `SEMANTIC_CACHE_SIMILARITY_THRESHOLD` | `0.92` | How alike two questions must be to reuse an answer (0–1) |
| `SEMANTIC_CACHE_TTL_SECONDS` | `3600` | Cached answers expire after 1 hour |
| `SEMANTIC_CACHE_MAX_ENTRIES_PER_SESSION` | `100` | Oldest cached answers are dropped past this |
| `OLLAMA_TEMPERATURE` | `0` | `0` keeps answers consistent and repeatable |
| `OLLAMA_NUM_CTX` | `8192` | How much text the model can consider at once |

> **Note on ports:** if you change `BACKEND_PORT`, change `NEXT_PUBLIC_API_BASE_URL` to match. The browser talks to the backend directly, so a mismatch means the app loads but every request fails.

---

## API reference

Base URL: `http://localhost:8000`. All endpoints are under `/api/v1`. Full interactive docs at `/docs`.

### Ask a question

```http
POST /api/v1/ask
```

```json
{
  "session_id": "3f2a7c18-5b9e-4d21-8a6f-1c7e9b2d4a80",
  "question": "Which internal employees know Python?",
  "context": null
}
```

Response:

```json
{
  "session_id": "3f2a7c18-5b9e-4d21-8a6f-1c7e9b2d4a80",
  "answer": "Three employees have Python skills...",
  "cache_hit": false,
  "similarity_score": null,
  "source": "postgresql",
  "tools_used": ["search_employees"],
  "model_name": "qwen3:8b"
}
```

`context` is optional — use it to add instructions such as *"answer in bullet points"*.

### Sessions

| Method | Path | What it does |
|---|---|---|
| `POST` | `/api/v1/sessions` | Start a new chat. Body: `{"title": "optional name"}` |
| `GET` | `/api/v1/sessions?limit=50` | List chats, newest first |
| `GET` | `/api/v1/sessions/{id}` | Get a chat with all its messages |
| `PATCH` | `/api/v1/sessions/{id}` | Rename a chat. Body: `{"title": "New name"}` |
| `DELETE` | `/api/v1/sessions/{id}` | Delete a chat and its cached answers |

### Health

```http
GET /api/v1/health
```

```json
{
  "status": "ok",
  "service": { "name": "...", "version": "0.6.0", "environment": "development" },
  "dependencies": {
    "postgres": { "status": "connected", "message": null },
    "redis":    { "status": "connected", "message": null },
    "ollama":   { "status": "connected", "message": null }
  }
}
```

All three dependencies are checked at the same time. `status` is `ok` only when every one is connected.

### Errors

Errors come back in a consistent shape:

```json
{ "error": { "code": "session_not_found", "message": "...", "details": {} } }
```

| Code | HTTP | Meaning |
|---|---|---|
| `session_not_found` | 404 | That chat does not exist or has expired |
| `agent_execution_failed` | 502 | The AI agent could not finish |
| `ollama_unavailable` | 503 | Ollama is not reachable |
| `embedding_generation_failed` | 502 | The embedding model failed |
| `application_error` | 500 | Something else went wrong |

---

## The assistant's tools

The AI does not query anything directly. It chooses from a fixed list of tools, and the code decides what those tools do.

### Internal tools (PostgreSQL)

| Tool | What it does |
|---|---|
| `search_employees` | Free-text search across names, emails, roles, departments, and skills |
| `get_employee_details` | Full profile for one person, by ID or email |
| `get_employee_statistics` | Employee counts, optionally per department |
| `analyze_workforce_skills` | Which skills the workforce has, and how deeply |

### External tools (GitHub, via MCP)

| Tool | What it does |
|---|---|
| `search_github_repositories` | Search public repositories, filter by language, sort by stars/forks/activity |
| `get_github_repository_details` | Live stars, forks, issues, topics, and license for one repository |

The MCP server also exposes `get_server_information` for diagnostics.

At startup the backend loads its four internal tools, discovers the GitHub tools over MCP, and **refuses to start if any expected tool is missing** — so a broken tool fails loudly instead of quietly degrading answers.

---

## Database

Four tables, created by Alembic.

```
departments ──┬──< employees >──┬── employee_skills >──── skills
              │                 │
   name       │   name          │   proficiency_level     name
   location   │   email         │   years_of_experience   category
   description│   role          │                         description
              │   years_of_experience
```

- **`departments`** — teams, with an optional location
- **`skills`** — technologies, grouped by category (Programming Language, Database, DevOps, and so on)
- **`employees`** — people, each belonging to one department
- **`employee_skills`** — links a person to a skill, with a proficiency of `beginner`, `intermediate`, `advanced`, or `expert`

Safety rules are enforced in the database itself: emails and skill names are unique, years of experience cannot be negative, deleting an employee removes their skill links, and a department cannot be deleted while people still belong to it.

### Sample data

On first startup the seed script loads:

- **4 departments** — Engineering, Data Science, Quality Assurance, Human Resources
- **10 skills** — Python, TypeScript, FastAPI, Next.js, PostgreSQL, Redis, Docker, Playwright, LangChain, Machine Learning
- **5 employees** with skills assigned

The script is safe to run more than once — it will not create duplicates. Set `SEED_DATABASE=false` to skip it.

---

## Conversation memory

Chat history lives in Redis, not PostgreSQL, because it is temporary by design.

Each chat uses three Redis keys:

| Key | Type | Holds |
|---|---|---|
| `chat:session:{id}` | hash | Title, timestamps, message count |
| `chat:history:{id}` | list | The messages themselves |
| `chat:sessions` | sorted set | All chats, ordered by last use |

Only the most recent **40** messages are kept, and everything expires after **24 hours** of inactivity. The clock resets whenever you read or write the chat, so an active conversation stays alive.

---

## Semantic cache

A normal cache only helps when two questions are *identical*. This one helps when they merely *mean the same thing*.

How it works:

1. Your question is turned into a list of numbers (an embedding) by `embeddinggemma`.
2. That embedding is stored in a **Redis vector set** (`VADD`), scoped to your chat.
3. On the next question, Redis finds the closest earlier questions (`VSIM`).
4. If the closest one scores **0.92 or higher**, its saved answer is returned immediately.

So *"Which employees know Python?"* and *"Who on the team knows Python?"* share one answer.

**When the cache is skipped.** Questions asking for fresh information bypass it entirely — if the question contains words like *current, latest, now, today, recent, live,* or *updated*, the agent always runs. Otherwise "How many stars does this repo have now?" could return yesterday's number.

**Cache boundaries.** Entries are per-chat, so one conversation never serves another's answers. Each chat keeps at most 100 entries, and entries expire after an hour. Deleting a chat deletes its cache too.

---

## Project structure

```
workforce-technology-assistant/
├── compose.yaml              # the five services
├── compose.dev.yaml          # dev overrides (hot reload)
├── .env.example              # copy this to .env
│
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app setup
│   │   ├── api/              # routes, dependencies, error handlers
│   │   ├── agent/            # the LangChain agent
│   │   ├── tools/            # the four internal tools
│   │   ├── mcp/              # client that discovers GitHub tools
│   │   ├── memory/           # Redis chat history
│   │   ├── semantic_cache/   # vector-based answer reuse
│   │   ├── services/         # business logic
│   │   ├── db/               # models and queries
│   │   ├── integrations/     # Ollama, Redis, LLM setup
│   │   ├── schemas/          # request and response shapes
│   │   └── core/             # config, exceptions, startup
│   ├── alembic/              # database migrations
│   └── scripts/              # start.sh, seed_database.py, verification scripts
│
├── mcp-server/
│   ├── app/
│   │   ├── main.py           # starts the MCP server
│   │   ├── server/           # registers the tools
│   │   ├── tools/            # the GitHub tools
│   │   ├── integrations/     # GitHub API client
│   │   └── schemas/          # tool inputs and outputs
│   └── scripts/              # verification script
│
├── frontend/
│   └── src/
│       ├── app/              # Next.js pages
│       ├── components/       # buttons, modals, layout
│       ├── features/         # chat, sessions, system status
│       └── lib/              # API client, helpers
│
└── infrastructure/
    ├── postgres/init/        # database init scripts
    └── redis/redis.conf      # Redis settings
```

The backend is organised in layers: **routes** handle HTTP, **services** hold the logic, **repositories** talk to the database, and **integrations** talk to the outside world. Each layer only knows about the one below it.

---

## Development

### Hot reload

`compose.dev.yaml` mounts your code into the containers so changes apply without rebuilding. Both files must be passed:

```bash
docker compose -f compose.yaml -f compose.dev.yaml up
```

> Plain `docker compose up` does **not** pick up `compose.dev.yaml` — Compose only merges a file named `compose.override.yaml` automatically. Without both `-f` flags you get the production setup, and code changes are ignored until you rebuild.

In dev mode the frontend sits behind a `full` profile, so only the backend, MCP server, database, and Redis start. Add `--profile full` if you want the frontend too.

### Running the backend outside Docker

Keep the supporting services in Docker and run only the API on your machine:

```bash
docker compose up -d postgres redis mcp-server

cd backend
python3 -m venv .venv
./.venv/bin/pip install -r requirements-dev.txt
```

The hostnames in `backend/.env` (`postgres`, `redis`, `mcp-server`) only resolve *inside* Docker, so override them:

```bash
export POSTGRES_HOST=localhost
export REDIS_URL=redis://localhost:6379/0
export MCP_SERVER_URL=http://localhost:8001/mcp
export OLLAMA_BASE_URL=http://localhost:11434

./.venv/bin/alembic upgrade head
./.venv/bin/python -m scripts.seed_database
./.venv/bin/uvicorn app.main:app --reload --port 8000
```

### Running the frontend outside Docker

```bash
cd frontend
npm install
npm run dev
```

### Database migrations

```bash
# after changing a model, generate a migration
docker compose exec backend alembic revision --autogenerate -m "describe the change"

# apply migrations
docker compose exec backend alembic upgrade head

# undo the last one
docker compose exec backend alembic downgrade -1
```

### Useful commands

```bash
docker compose ps                      # what is running
docker compose logs -f backend         # follow one service's logs
docker compose restart backend         # restart one service
docker compose exec postgres psql -U workforce_user -d workforce_assistant
docker compose exec redis redis-cli
```

---

## Testing

Test coverage is uneven right now, so here is the honest picture:

| Part | State |
|---|---|
| Frontend | **40 automated tests** across 6 files, run with Vitest |
| Backend | **No automated tests.** Verification is done with the manual scripts below |
| MCP server | **No automated tests.** One manual script |

### Frontend (automated)

```bash
cd frontend
npm test             # Vitest, single run
npm run test:watch   # Vitest, re-runs on save
npm run lint         # ESLint
```

These cover the API client, error handling, session filtering, the question composer, response metadata, and the main workspace screen.

### Backend (manual verification scripts)

These are not pytest tests — they are standalone scripts that exercise a
part of the system and print what happened. **The services must be running**
(Postgres, Redis, the MCP server, and Ollama), because the scripts talk to
them for real.

```bash
# easiest: run them inside the container, where everything is reachable
docker compose exec backend python -m scripts.test_workforce_tools      # the four database tools
docker compose exec backend python -m scripts.test_conversation_memory  # Redis chat history
docker compose exec backend python -m scripts.test_semantic_cache       # answer reuse
docker compose exec backend python -m scripts.test_agent                # the full agent, end to end
```

### MCP server (manual verification script)

```bash
docker compose exec mcp-server python -m scripts.test_github_tools
```

### Linting

```bash
cd backend      && ./.venv/bin/ruff check app
cd mcp-server   && ./.venv/bin/ruff check app
cd frontend     && npm run lint
```

### Adding real backend tests

`requirements-dev.txt` already installs `pytest`, `pytest-asyncio`, and
`pytest-cov` (plus `respx` for the MCP server), so the tooling is ready. Two
things are worth knowing before you start:

- There is no `pytest.ini`, `pyproject.toml`, or `conftest.py` yet. Async
  tests need `asyncio_mode = auto` set somewhere, or every async test needs
  the `@pytest.mark.asyncio` marker.
- The scripts above are a good starting point — they already contain the
  setup and assertions, they just need converting into `test_` functions.

---

## Troubleshooting

### A port is already in use

```
Error: bind: address already in use
```

Something else holds that port. Either stop it, or pick different ports in `.env`:

```
BACKEND_PORT=8010
FRONTEND_PORT=3010
POSTGRES_PORT=5433
NEXT_PUBLIC_API_BASE_URL=http://localhost:8010
```

Remember to update `NEXT_PUBLIC_API_BASE_URL` alongside `BACKEND_PORT`.

### Health says `ollama: unavailable`

Check Ollama is running on your machine:

```bash
curl http://localhost:11434/api/tags
```

If that works but the container still cannot reach it, Ollama may only be listening on `127.0.0.1`. Restart it bound to all interfaces:

```bash
OLLAMA_HOST=0.0.0.0 ollama serve
```

### Answers are slow

Normal on a first run — the model has to load into memory. It gets faster after that. A smaller model helps if it stays slow:

```
OLLAMA_CHAT_MODEL=qwen3:4b
```

### `model "qwen3:8b" not found`

The model was never pulled:

```bash
ollama pull qwen3:8b
ollama pull embeddinggemma
```

### GitHub questions fail with a rate-limit error

Without a token GitHub allows only 60 requests per hour. Create a token with no special scopes (public data is enough) and add it to `.env`:

```
GITHUB_TOKEN=ghp_your_token_here
```

Then `docker compose up -d --build mcp-server`.

### The backend keeps restarting

Read the logs — the cause is almost always in the first 30 lines:

```bash
docker compose logs backend | head -40
```

Common causes: Ollama unreachable, a migration failure, or a missing model.

### Starting completely fresh

This erases the database and all chats:

```bash
docker compose down -v
docker compose up --build
```

### Code changes are not showing up

Plain `docker compose up` bakes code into the image. Either rebuild:

```bash
docker compose up -d --build backend
```

or use dev mode with both compose files (see [Development](#development)).
