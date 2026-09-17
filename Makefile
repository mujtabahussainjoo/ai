# =============================================================================
# MyAIBuddy Makefile
# =============================================================================
# Usage: make <target>
# All configuration is in .env (copy from .env.example)
# =============================================================================
SHELL := /bin/bash
COMPOSE := docker compose
ENV_FILE := .env

# Load .env for shell commands
ifneq (,$(wildcard $(ENV_FILE)))
  include $(ENV_FILE)
  export
endif

FRONTEND_PORT ?= 8080
BACKEND_PORT  ?= 8000
DB_PORT       ?= 5433

# =============================================================================
# Help
# =============================================================================

.PHONY: help
help: ## Show this help
	@echo "MyAIBuddy - Available Commands:"
	@echo ""
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# =============================================================================
# Quick Start
# =============================================================================

.PHONY: setup
setup: ## First-time setup: create .env and start everything
	@test -f .env || (cp .env.example .env && echo "Created .env from .env.example")
	$(COMPOSE) up -d --build
	@echo ""
	@echo "Waiting for services..."
	@sleep 10
	@echo ""
	@echo "============================================="
	@echo " MyAIBuddy is running!"
	@echo "============================================="
	@echo ""
	@printf " Frontend:     http://localhost:$(FRONTEND_PORT)\n"
	@printf " Backend API:  http://localhost:$(BACKEND_PORT)\n"
	@printf " Swagger:      http://localhost:$(BACKEND_PORT)/docs\n"
	@printf " ReDoc:        http://localhost:$(BACKEND_PORT)/redoc\n"
	@printf " OpenAPI:      http://localhost:$(BACKEND_PORT)/openapi.json\n"
	@printf " Database:     postgresql://localhost:$(DB_PORT)\n"
	@echo "============================================="

.PHONY: up
up: ## Start all services
	$(COMPOSE) up -d

.PHONY: up-build
up-build: ## Rebuild and start all services
	$(COMPOSE) up -d --build

.PHONY: down
down: ## Stop all services
	$(COMPOSE) down

.PHONY: restart
restart: ## Restart all services
	$(COMPOSE) restart

.PHONY: stop
stop: ## Stop and remove all containers
	$(COMPOSE) down -v --remove-orphans

# =============================================================================
# Logs & Status
# =============================================================================

.PHONY: logs
logs: ## Tail logs from all services
	$(COMPOSE) logs -f

.PHONY: status
status: ## Show service status
	$(COMPOSE) ps
	@echo ""
	@echo "Listening ports:"
	@ss -tlnp | grep -E ':(8080|8000|5433) ' 2>/dev/null || true

.PHONY: backend-logs
backend-logs: ## Tail backend logs
	$(COMPOSE) logs -f backend

.PHONY: frontend-logs
frontend-logs: ## Tail frontend logs
	$(COMPOSE) logs -f frontend

.PHONY: db-logs
db-logs: ## Tail database logs
	$(COMPOSE) logs -f db

# =============================================================================
# Database
# =============================================================================

.PHONY: db-shell
db-shell: ## Open PostgreSQL shell
	$(COMPOSE) exec db psql -U $${POSTGRES_USER:-myaibuddy} -d $${POSTGRES_DB:-myaibuddy}

.PHONY: db-migrate
db-migrate: ## Run database migrations
	$(COMPOSE) exec backend alembic upgrade head

.PHONY: db-reset
db-reset: ## Reset database (DELETES ALL DATA)
	@echo "WARNING: This will destroy all data!"
	@read -p "Type 'yes' to confirm: " confirm && [ "$$confirm" = "yes" ] || (echo "Aborted." && exit 1)
	$(COMPOSE) down -v
	$(COMPOSE) up -d db
	@echo "Waiting for DB..."
	@sleep 5
	$(COMPOSE) up -d backend
	@echo "Database reset complete. Backend will run migrations on startup."

# =============================================================================
# Build (Standalone)
# =============================================================================

.PHONY: build-frontend
build-frontend: ## Build frontend Docker image (standalone)
	docker build --target frontend -t myaibuddy-frontend .

.PHONY: build-backend
build-backend: ## Build backend Docker image (standalone)
	docker build --target backend -t myaibuddy-backend .

.PHONY: build
build: ## Build all Docker images
	$(COMPOSE) build

# =============================================================================
# Local Development (without Docker)
# =============================================================================

.PHONY: dev-frontend
dev-frontend: ## Start frontend dev server (local, no Docker)
	cd apps/frontend && pnpm install && pnpm dev

.PHONY: dev-backend
dev-backend: ## Start backend dev server (local, needs DB running)
	cd apps/backend && source .env && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

.PHONY: dev
dev: ## Start both FE and BE dev servers (needs DB running)
	@echo "Starting frontend and backend in parallel..."
	@make -j2 dev-frontend dev-backend

# =============================================================================
# Cleanup
# =============================================================================

.PHONY: clean
clean: ## Remove build artifacts and Docker resources
	$(COMPOSE) down -v --remove-orphans
	docker image prune -f
	cd apps/frontend && rm -rf dist node_modules/.vite
	cd apps/backend && rm -rf __pycache__ .pytest_cache

# =============================================================================
# Utilities
# =============================================================================

.PHONY: urls
urls: ## Print all service URLs
	@echo ""
	@echo "============================================="
	@echo " MyAIBuddy Service URLs"
	@echo "============================================="
	@echo ""
	@printf " Frontend:     http://localhost:$(FRONTEND_PORT)\n"
	@printf " Backend API:  http://localhost:$(BACKEND_PORT)\n"
	@printf " Swagger:      http://localhost:$(BACKEND_PORT)/docs\n"
	@printf " ReDoc:        http://localhost:$(BACKEND_PORT)/redoc\n"
	@printf " OpenAPI:      http://localhost:$(BACKEND_PORT)/openapi.json\n"
	@printf " Database:     postgresql://localhost:$(DB_PORT)\n"
	@echo ""
	@echo "============================================="
