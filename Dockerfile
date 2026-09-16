# syntax=docker/dockerfile:1

# ============================================================================
# Common Dockerfile for the whole MyAIBuddy project (backend + frontend).
#
# Multi-stage, so a single file builds both apps:
#   docker build --target=backend  .   -> FastAPI + AI backend
#   docker build --target=frontend .   -> static SPA served by nginx
#
# Recommended usage (runs db + backend + frontend together):
#   docker compose up --build
# ============================================================================

# ---------------------------------------------------------------------------
# Stage 1: Build the frontend (pnpm workspace).
# Builds shared-types, ui, then the Vite SPA in topological order.
# ---------------------------------------------------------------------------
FROM node:20-alpine AS frontend-build

RUN corepack enable

WORKDIR /repo

COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./
COPY packages ./packages
COPY apps/frontend ./apps/frontend

RUN pnpm install --frozen-lockfile
RUN pnpm -r build

# ---------------------------------------------------------------------------
# Stage 2: Frontend runtime — nginx serving the static SPA and proxying
# /api to the backend container (keeps the exact same /api/v1 endpoints).
# ---------------------------------------------------------------------------
FROM nginx:alpine AS frontend

COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=frontend-build /repo/apps/frontend/dist /usr/share/nginx/html

EXPOSE 80

# ---------------------------------------------------------------------------
# Stage 3: Backend runtime — FastAPI + AI services.
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS backend

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /app/apps/backend
COPY apps/backend ./

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]