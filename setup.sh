#!/usr/bin/env bash
# =============================================================================
# MyAIBuddy - Setup & Start Script
# =============================================================================
# This script:
#   1. Checks prerequisites (Docker, Node.js, pnpm)
#   2. Creates .env from .env.example if it doesn't exist
#   3. Starts all services via Docker Compose
#   4. Waits for services to be healthy
#   5. Prints all URLs (FE, BE, Swagger, DB)
# =============================================================================
set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# =============================================================================
# Helpers
# =============================================================================
info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()   { echo -e "${RED}[ERROR]${NC} $*" >&2; }

separator() {
  echo -e "${CYAN}────────────────────────────────────────────────────────────────${NC}"
}

# =============================================================================
# 1. Check Prerequisites
# =============================================================================
info "Checking prerequisites..."

check_cmd() {
  if command -v "$1" &>/dev/null; then
    ok "$1 found: $(command -v "$1")"
    return 0
  else
    err "$1 is NOT installed. Please install it first."
    return 1
  fi
}

MISSING=0
check_cmd docker || MISSING=1
check_cmd docker compose || check_cmd "docker-compose" || MISSING=1

if [ "$MISSING" -eq 1 ]; then
  err "Missing required tools. Install Docker and Docker Compose, then retry."
  exit 1
fi

# Use docker compose v2 if available, fall back to docker-compose
if docker compose version &>/dev/null 2>&1; then
  COMPOSE="docker compose"
else
  COMPOSE="docker-compose"
fi

info "Using: $COMPOSE"

# =============================================================================
# 2. Create .env if missing
# =============================================================================
if [ ! -f .env ]; then
  warn ".env file not found. Creating from .env.example..."
  cp .env.example .env
  ok ".env created. Edit it to add your API keys and customize settings."
  echo ""
fi

# =============================================================================
# 3. Load .env values for URL display
# =============================================================================
# Parse .env safely (skip comments and empty lines)
while IFS='=' read -r key value; do
  key=$(echo "$key" | xargs)
  value=$(echo "$value" | xargs | sed 's/^["'"'"']\(.*\)["'"'"']$/\1/')
  if [[ ! "$key" =~ ^# ]] && [[ -n "$key" ]]; then
    export "$key"="$value" 2>/dev/null || true
  fi
done < .env

FRONTEND_PORT="${FRONTEND_PORT:-8080}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
DB_PORT="${DB_PORT:-5433}"

# =============================================================================
# 4. Start Services
# =============================================================================
separator
info "Starting MyAIBuddy services..."
separator

$COMPOSE up -d --build

# =============================================================================
# 5. Wait for Services
# =============================================================================
info "Waiting for services to become healthy..."
separator

MAX_WAIT=120
ELAPSED=0
INTERVAL=5

while [ $ELAPSED -lt $MAX_WAIT ]; do
  BACKEND_HEALTHY=$(docker inspect --format='{{.State.Health.Status}}' myaibuddy-backend 2>/dev/null || echo "starting")
  DB_HEALTHY=$(docker inspect --format='{{.State.Health.Status}}' myaibuddy-db 2>/dev/null || echo "starting")
  FRONTEND_RUNNING=$(docker inspect --format='{{.State.Status}}' myaibuddy-frontend 2>/dev/null || echo "starting")

  BACKEND_OK=false
  DB_OK=false
  FRONTEND_OK=false

  [ "$DB_HEALTHY" = "healthy" ] && DB_OK=true
  [ "$BACKEND_HEALTHY" = "healthy" ] && BACKEND_OK=true
  [ "$FRONTEND_RUNNING" = "running" ] && FRONTEND_OK=true

  ALL_OK=true
  $DB_OK   || ALL_OK=false
  $BACKEND_OK || ALL_OK=false
  $FRONTEND_OK || ALL_OK=false

  if $ALL_OK; then
    ok "All services are healthy!"
    break
  fi

  printf "\r  Waiting... DB=%-10s Backend=%-10s Frontend=%-10s (%ds)" \
    "$DB_HEALTHY" "$BACKEND_HEALTHY" "$FRONTEND_RUNNING" "$ELAPSED"
  sleep $INTERVAL
  ELAPSED=$((ELAPSED + INTERVAL))
done

echo ""

if [ $ELAPSED -ge $MAX_WAIT ]; then
  warn "Some services may not be fully healthy yet. Check with: $COMPOSE logs"
fi

# =============================================================================
# 6. Print All URLs
# =============================================================================
separator
echo ""
echo -e "${BOLD}${GREEN}  MyAIBuddy is running!${NC}"
echo ""
separator
echo ""
echo -e "${BOLD}  URLs:${NC}"
echo ""
echo -e "  ${CYAN}Frontend:${NC}     http://localhost:${FRONTEND_PORT}"
echo -e "  ${CYAN}Backend API:${NC}  http://localhost:${BACKEND_PORT}"
echo -e "  ${CYAN}Swagger Docs:${NC} http://localhost:${BACKEND_PORT}/docs"
echo -e "  ${CYAN}ReDoc:${NC}        http://localhost:${BACKEND_PORT}/redoc"
echo -e "  ${CYAN}OpenAPI JSON:${NC} http://localhost:${BACKEND_PORT}/openapi.json"
echo -e "  ${CYAN}Health Check:${NC} http://localhost:${BACKEND_PORT}${API_PREFIX:-/api/v1}/health"
echo -e "  ${CYAN}Database:${NC}     postgresql://localhost:${DB_PORT}"
echo ""
separator
echo ""
echo -e "  ${BOLD}Commands:${NC}"
echo ""
echo -e "  ${YELLOW}make logs${NC}          - Tail all service logs"
echo -e "  ${YELLOW}make stop${NC}          - Stop all services"
echo -e "  ${YELLOW}make restart${NC}       - Restart all services"
echo -e "  ${YELLOW}make status${NC}        - Show service status"
echo -e "  ${YELLOW}make db-shell${NC}      - Open PostgreSQL shell"
echo -e "  ${YELLOW}make db-migrate${NC}    - Run database migrations"
echo -e "  ${YELLOW}make db-reset${NC}      - Reset database (DESTRUCTIVE)"
echo -e "  ${YELLOW}make backend-logs${NC}  - Tail backend logs"
echo -e "  ${YELLOW}make frontend-logs${NC} - Tail frontend logs"
echo ""
separator
echo ""
