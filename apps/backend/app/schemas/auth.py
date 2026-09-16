"""Authentication schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = Field(default=None, max_length=80)
    roles: list[str] | None = Field(
        default=None,
        description="Optional roles (e.g. [\"admin\"]). Honored only when APP_ENV=development/test; ignored in production.",
    )

    @field_validator("password")
    @classmethod
    def password_secure(cls, value: str) -> str:
        if not any(char.isupper() for char in value):
            raise ValueError("password must contain an uppercase letter")
        if not any(char.isdigit() for char in value):
            raise ValueError("password must contain a digit")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int


class UserProfile(BaseModel):
    id: uuid.UUID
    email: EmailStr
    display_name: str | None
    roles: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("roles", mode="before")
    @classmethod
    def roles_to_names(cls, value: Any) -> list[str] | Any:
        if value and not isinstance(value[0], str):
            return [role.name for role in value]
        return value


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def password_secure(cls, value: str) -> str:
        if not any(char.isupper() for char in value):
            raise ValueError("password must contain an uppercase letter")
        if not any(char.isdigit() for char in value):
            raise ValueError("password must contain a digit")
        return value
