"""Central constants: roles, providers, MIME allowlists, limits, error codes."""

from __future__ import annotations

from enum import StrEnum


class Role(StrEnum):
    ADMIN = "admin"
    USER = "user"


class Provider(StrEnum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"


# Scenario -> kind keys used by the model router
MODEL_TASK_CHAT = "chat"
MODEL_TASK_REASONING = "reasoning"
MODEL_TASK_CODING = "coding"
MODEL_TASK_EMBEDDING = "embedding"
MODEL_TASK_VISION = "vision"
MODEL_TASK_IMAGE_GENERATION = "image_generation"

# File upload allowlists
DOCUMENT_MIME_ALLOWED = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",  # .pptx
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
    "text/plain",
    "text/markdown",
    "text/csv",
    "text/html",
    "application/json",
}
IMAGE_MIME_ALLOWED = {"image/png", "image/jpeg", "image/webp", "image/tiff"}

# Size limits
MAX_UPLOAD_BYTES_DEFAULT = 25 * 1024 * 1024  # honor settings.MAX_UPLOAD_MB

# Agent tool policy
TOOL_CATEGORY_READ = "read"
TOOL_CATEGORY_WRITE = "write"
TOOL_CATEGORY_ACTION = "action"
WRITE_OR_ACTION_TOOLS = frozenset({TOOL_CATEGORY_WRITE, TOOL_CATEGORY_ACTION})

# Audit / approvals
MAX_APPROVAL_PENDING_SECONDS = 60 * 10

ERROR_CODES = {
    "not_found",
    "already_exists",
    "unauthorized",
    "forbidden",
    "validation_error",
    "rate_limited",
    "payload_too_large",
    "misconfigured",
    "external_service_error",
    "internal_error",
    "insufficient_evidence",
}
