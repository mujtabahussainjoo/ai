"""Versioned v1 router (mounted under /api/v1)."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.routes import admin, auth, chat, documents, health, integrations, providers

router = APIRouter()
router.include_router(health.router, tags=["health"])
router.include_router(auth.router)
router.include_router(providers.router)
router.include_router(integrations.router)
router.include_router(chat.router)
router.include_router(documents.router)
router.include_router(admin.router)
