"""FastAPI application entrypoint.

Run with: uvicorn app.main:app --reload --port 8010
"""

from __future__ import annotations

import os
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.limits import limiter
from app.core.logging import logger, request_id_var, setup_logging
from app.db.session import dispose_engine

SCHEMA_NAME = "BearerAuth"


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
        request_id_var.set(request_id)
        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        return response


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    setup_logging(settings.LOG_LEVEL)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    logger.info(
        "backend_starting",
        extra={
            "extra_fields": {"app": settings.APP_NAME, "env": settings.APP_ENV, "version": settings.VERSION}
        },
    )
    yield
    await dispose_engine()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        description="Conversational AI, RAG, web research, and all-rounder agent API.",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
        default_response_class=ORJSONResponse,
    )

    _original_openapi = app.openapi

    def _openapi_with_auth() -> dict[str, Any]:
        schema = _original_openapi()
        schema.setdefault("components", {}).setdefault("securitySchemes", {})[SCHEMA_NAME] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Click **Authorize**, paste your access token, then hit any protected endpoint.",
        }
        for path_methods in schema.get("paths", {}).values():
            for method, operation in path_methods.items():
                if method in ("get", "post", "put", "patch", "delete"):
                    op_sec = operation.get("security")
                    if op_sec is None:
                        operation["security"] = [{SCHEMA_NAME: []}]
        return schema

    app.openapi = _openapi_with_auth  # type: ignore[method-assign]

    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    register_exception_handlers(app)

    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(api_router, prefix=settings.API_PREFIX)
    return app


app = create_app()
