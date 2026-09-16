#!/usr/bin/env bash
# ingest_documents.sh — wrapper to run ingestion from repo root
#
# Usage:
#   ./scripts/ingest_documents.sh --all          # re-ingest every document
#   ./scripts/ingest_documents.sh --doc-id UUID  # re-ingest a single document
#
# Must be run from the repository root (/var/www/html/ai).

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}/../apps/backend"
cd "${BACKEND_DIR}"
exec ./.venv/bin/python "${SCRIPT_DIR}/ingest_documents.py" "$@"
