# MyAIBuddy

A production-shaped AI workspace running fully on localhost (no Docker for the app itself).

It includes a conversational assistant, a RAG assistant grounded in your documents,
a web research agent with citations, and an all-rounder agent that can read code,
inspect repositories, run approved tests, and call allowlisted tools.

## URLs

| Service | URL | Notes |
|---|---|---|
| Frontend (web dashboard) | http://127.0.0.1:3000 | React + Vite SPA served on port 3000 |
| Backend API | http://127.0.0.1:8000 | FastAPI on port 8000 |
| Swagger UI (interactive API explorer) | http://127.0.0.1:8000/docs | Register/login, then Authorize with the access token |
| ReDoc | http://127.0.0.1:8000/redoc | Read-only API reference |
| OpenAPI JSON | http://127.0.0.1:8000/openapi.json | Machine-readable spec |
| Health check | http://127.0.0.1:8000/api/v1/health | Returns 200 when the API is up |
| Readiness | http://127.0.0.1:8000/api/v1/ready | Returns 200 when DB + app are ready |

> Note: the default Vite port is 5173, but on this machine port 5173 has a stale
> socket with no owning process, so the frontend runs on **port 3000** instead.

## API endpoints (`/api/v1`)

### Auth (`/auth`)
| Method | Path | Description |
|---|---|---|
| POST | `/auth/register` | Create a user. In dev, an optional `roles: ["admin"]` field grants the admin role. |
| POST | `/auth/login` | Login, returns `access_token` + `refresh_token` |
| POST | `/auth/refresh` | Exchange a refresh token for a new access token |
| GET | `/auth/me` | Current user profile |
| POST | `/auth/change-password` | Change the current user's password |

### Providers (`/providers`)
| Method | Path | Description |
|---|---|---|
| GET | `/providers` | List all providers with status, capabilities, default/order |
| PUT | `/providers/{provider}` | Configure/enable/disable/set default (admin only) |
| POST | `/providers/{provider}/test` | Ping a provider with a key (admin only) |

### 3rd-party APIs (`/integrations`)
| Method | Path | Description |
|---|---|---|
| GET | `/integrations` | List configured 3rd-party API integrations |
| POST | `/integrations` | Add a new API (endpoint, auth type, key, headers) — admin only |
| PUT | `/integrations/{id}` | Update an API integration (admin only) |
| DELETE | `/integrations/{id}` | Delete an API integration (admin only) |

### Conversations (`/conversations`)
| Method | Path | Description |
|---|---|---|
| GET | `/conversations` | List conversations (paginated) |
| POST | `/conversations` | Create a conversation |
| GET | `/conversations/{id}` | Conversation detail |
| DELETE | `/conversations/{id}` | Soft-delete a conversation |
| GET | `/conversations/{id}/messages` | List messages |
| POST | `/conversations/{id}/messages` | Send a message (JSON response) |
| POST | `/conversations/{id}/messages/stream` | Send a message (SSE stream) |

### Admin (`/admin`)
| Method | Path | Description |
|---|---|---|
| GET | `/admin/logs?min_level=WARNING&limit=100` | Recent in-memory backend logs (admin only) |

### Health
| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness probe |
| GET | `/ready` | Readiness (checks DB) |

## Quick start

```bash
# One-time environment setup (installs dependencies, backend venv, initializes DB)
./scripts/setup-local.sh

# Run migrations
./scripts/run-migrations.sh

# Backend (API + AI service)
(cd apps/backend && pnpm dev)   # or: uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend (web dashboard)
(cd apps/frontend && pnpm dev)  # served on http://127.0.0.1:3000
```

## Using Swagger (http://127.0.0.1:8000/docs)

1. **Register** an admin: `POST /api/v1/auth/register` with body
   ```json
   {"email":"dev@test.com","password":"TestPass123","display_name":"Dev","roles":["admin"]}
   ```
   (`roles` is honored only in development/test; it is ignored in production.)
2. **Login**: `POST /api/v1/auth/login` → copy `data.access_token`.
3. Click **Authorize** (top-right), paste the token, hit **Authorize**.
4. All protected endpoints (providers, conversations, auth/me, admin/logs) now work.
5. A pre-seeded admin `admin@myaibuddy.dev` also exists if you know its password.

## Provider priority (which model chat uses when you enable several)

Priority = **`fallback_order` ascending** — order `0` is the default (used first):

1. **Explicit request** — if a chat request names a provider, that one wins.
2. **Enabled providers in DB** — sorted by `fallback_order` asc (nulls last); the first
   one that is actually usable (has a key / base URL and supports chat) is picked.
   `mock` is always deferred to last resort.
3. **Env-configured providers** — `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`
   from `.env`, tried in that fixed order.
4. **Ollama** — if reachable (`OLLAMA_BASE_URL` + running server).
5. **mock** — absolute fallback, only if nothing above can answer.

How `fallback_order` is assigned in Settings:

- **Set default** → that provider gets `0`, every other ordered provider is bumped `+1`.
- **Enable** a provider that has no order yet → appended at the end (`max+1`).
- **Auto-promote** → enabling a chat-capable provider that can actually work makes it the
  default automatically when the current default is only `mock`.

Example — everything enabled:

| Provider | fallback_order | Used when |
|---|---|---|
| OpenAI | 0 (default) | always first if a key is set |
| Anthropic | 1 | if OpenAI unusable/unreachable |
| Ollama | 2 | next fallback |
| Google | 3 | next fallback |
| HuggingFace | any | **never for chat** (embedding-only, no chat support) |
| mock | any | last resort, only if all others unusable |

Unusable providers are skipped and logged (`provider_skipped`) with the reason — see
Settings → **System logs** (admin only) or `GET /api/v1/admin/logs`.

## Settings walkthrough

- **Manage AI providers** — enable/disable providers, set the default, configure keys and
  base URLs, and pick model names per capability (chat/reasoning/embedding/image).
  Each provider shows what it needs (e.g. "Requires OPENAI_API_KEY", "Local Ollama server"),
  which capabilities it supports, and suggested models for each field.
- **System logs** (admin only) — recent backend log records captured in-memory, filtered by
  level (DEBUG/INFO/WARNING/ERROR) with expandable tracebacks. Useful for diagnosing why a
  chat request fell back to `mock` or which provider failed.

## Documentation

- `docs/architecture.md` — components, data flow, module boundaries
- `docs/api-contracts.md` — endpoints, auth, request/response examples
- `docs/setup.md` — local setup
- `docs/deployment.md` — deploy without Docker
- `docs/security.md` — secrets, roles, data handling, approvals
- `docs/ai-design.md` — providers, model router, RAG, agents, tools, MCP, safety, evaluation

## Stack

- Frontend: React + TypeScript + Vite + Tailwind CSS + Zod + TanStack Query
- Backend: Python 3.12 + FastAPI + Pydantic v2 + SQLAlchemy 2 (async) + Alembic
- Database: PostgreSQL 16 + pgvector
- AI: LangChain providers + LangGraph agents (the all-rounder)

## Credentials & secrets

- API keys stored in `apps/backend/.env` are encrypted at rest (Fernet) and never returned
  to the browser (only a key fingerprint is exposed).
- Access tokens expire after 30 min; refresh tokens after 7 days.
- Admin-only endpoints are protected via a `Bearer` token with an `admin` role.