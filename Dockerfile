# syntax=docker/dockerfile:1

# ============================================================================
# Stage 1: Build the frontend
# ============================================================================

FROM node:20-alpine AS frontend-build

WORKDIR /repo

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

# Install and activate pnpm explicitly.
RUN npm install -g corepack@latest \
    && corepack enable pnpm \
    && corepack prepare pnpm@10.15.0 --activate \
    && pnpm --version

# Copy workspace metadata first.
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./

# Copy workspace package manifests.
COPY packages ./packages
COPY apps/frontend ./apps/frontend

# Install dependencies and build the workspace.
RUN pnpm install --frozen-lockfile
RUN pnpm -r build


# ============================================================================
# Stage 2: Frontend runtime
# ============================================================================

FROM nginx:alpine AS frontend

COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=frontend-build /repo/apps/frontend/dist /usr/share/nginx/html

# Render/Railway inject PORT at runtime.
CMD ["sh", "-c", "sed -i \"s/listen 80;/listen ${PORT:-8080};/\" /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]


# ============================================================================
# Stage 3: Backend runtime
# ============================================================================

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

ENTRYPOINT ["/entrypoint.sh"]

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]