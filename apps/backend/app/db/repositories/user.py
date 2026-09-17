"""User, role, and session repositories."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from hashlib import sha256

from sqlalchemy import select, update

from app.db.models import Permission, Role, Session, User

from .base import BaseRepository


def hash_refresh_token(token: str) -> str:
    return sha256(token.encode()).hexdigest()


class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email.lower())
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_all(self) -> list[User]:
        stmt = select(User).order_by(User.created_at.desc())
        return list((await self.session.execute(stmt)).scalars().all())

    async def create(
        self,
        *,
        email: str,
        password_hash: str,
        display_name: str | None = None,
        roles: list[Role] | None = None,
    ) -> User:
        user = User(
            email=email.lower(),
            password_hash=password_hash,
            display_name=display_name,
            is_active=True,
            is_verified=True,
            roles=roles or [],
        )
        self.session.add(user)
        return user


class RoleRepository(BaseRepository[Role]):
    model = Role

    async def get_by_names(self, names: list[str]) -> list[Role]:
        stmt = select(Role).where(Role.name.in_(names))
        return list((await self.session.execute(stmt)).scalars().all())

    async def all_permission_codes(self) -> set[str]:
        stmt = select(Permission.code)
        return set((await self.session.execute(stmt)).scalars().all())


class SessionRepository(BaseRepository[Session]):
    model = Session

    async def create(
        self,
        *,
        user_id: uuid.UUID,
        refresh_token_hash: str,
        expires_at: datetime,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> Session:
        session = Session(
            user_id=user_id,
            refresh_token_hash=refresh_token_hash,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.session.add(session)
        return session

    async def get_by_hash(self, refresh_token_hash: str) -> Session | None:
        stmt = select(Session).where(Session.refresh_token_hash == refresh_token_hash)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def revoke(self, session: Session) -> None:
        session.revoked_at = datetime.now(UTC)
        await self.session.flush()

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        await self.session.execute(
            update(Session)
            .where(Session.user_id == user_id, Session.revoked_at.is_(None))
            .values(revoked_at=datetime.now(UTC))
        )
