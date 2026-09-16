# MyAIBuddy Backend

FastAPI + SQLAlchemy(async) + Alembic + PostgreSQL + LangChain/LangGraph AI service.

## URLs

- API base: http://127.0.0.1:8000/api/v1
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health: http://127.0.0.1:8000/api/v1/health

## Quick start

```bash
python3 -m venv .venv
./.venv/bin/pip install -e ".[dev]"
cp .env.example .env            # fill in values
../../scripts/run-migrations.sh
./.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Docs: `../../docs/setup.md`, API explorer at `http://127.0.0.1:8000/docs`.

## Chat provider priority

Chat picks a provider by `fallback_order` ascending (0 = default): explicit request →
enabled DB providers (mock last) → env keys (`OPENAI`/`ANTHROPIC`/`GOOGLE`) → Ollama if
reachable → mock. Unusable providers (missing key, no chat support, dead Ollama) are
skipped and logged (`provider_skipped`), visible in `GET /api/v1/admin/logs`.