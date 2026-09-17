# syntax=docker/dockerfile:1

# =============================================================================
# MyAIBuddy - Multi-stage Dockerfile
# =============================================================================
# Build targets:
#   docker build --target frontend .   -> Standalone frontend (Nginx)
#   docker build --target backend .    -> Standalone backend (FastAPI)
#   docker build .                     -> Combined (backend + frontend static)
# =============================================================================

# =============================================================================
# Stage 1: Build React frontend
# =============================================================================
FROM node:20-alpine AS frontend-build

# For standalone frontend deployments (e.g. separate BE host):
#   docker build --target frontend --build-arg VITE_API_BASE_URL=https://api.example.com .
ARG VITE_API_BASE_URL=
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

WORKDIR /repo

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

RUN npm install -g pnpm@12.4.2

COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./
COPY packages ./packages
COPY apps/frontend ./apps/frontend

RUN pnpm install --frozen-lockfile
RUN pnpm -r build

# =============================================================================
# Stage 2: Standalone Frontend (Nginx)
# =============================================================================
FROM nginx:1.27-alpine AS frontend

# When deploying the frontend standalone (separate BE host), pass the backend
# URL as a build arg. VITE_API_BASE_URL gets baked into the JS bundle and Nginx
# serves static files only (no proxy needed):
#   docker build --target frontend --build-arg VITE_API_BASE_URL=https://api.example.com .
ARG VITE_API_BASE_URL=

COPY --from=frontend-build /repo/apps/frontend/dist /usr/share/nginx/html
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY nginx/standalone.conf /etc/nginx/conf.d/standalone.conf

# With a baked API URL the SPA talks directly to the backend, so use the
# static-only Nginx config. Otherwise use the full proxy config.
RUN if [ -n "$VITE_API_BASE_URL" ]; then \
      cp /etc/nginx/conf.d/standalone.conf /etc/nginx/conf.d/default.conf; \
    fi

EXPOSE 80

# =============================================================================
# Stage 3: Backend (Python + FastAPI)
# =============================================================================
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

COPY apps/backend ./apps/backend
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /app/apps/backend

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

# =============================================================================
# Stage 4: Combined (default) - Backend + Frontend static files
# =============================================================================
FROM backend AS combined

# WORKDIR from the backend stage is /app/apps/backend, so use an absolute path
# to place the SPA where app.main mounts it (STATIC_DIR => apps/backend/static).
COPY --from=frontend-build /repo/apps/frontend/dist /app/apps/backend/static

EXPOSE 8000
