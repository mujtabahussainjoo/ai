"""Create (or promote) an admin account.

Idempotent: if the account already exists it is granted the requested roles
and its password is left untouched. Runs against whatever DATABASE_URL the
backend container already uses, so no URL/credential duplication is needed.

Usage:
    docker compose exec -T backend python scripts/create_admin.py \
        --email admin@myaibuddy.dev \
        --password 'Admin@1234' \
        --roles admin user

Default credentials:
    email:    admin@myaibuddy.dev
    password: Admin@1234
    roles:    admin

Password rules (same as the API): min 8 chars, at least one uppercase
letter and one digit.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.security import hash_password  # noqa: E402
from app.db.repositories.user import RoleRepository, UserRepository  # noqa: E402
from app.db.seeds import run_seeds  # noqa: E402
from app.db.session import async_session_factory, dispose_engine  # noqa: E402

DEFAULT_EMAIL = "admin@myaibuddy.dev"
DEFAULT_PASSWORD = "Admin@1234"
DEFAULT_ROLES = ["admin"]


def _validate_password(password: str) -> None:
    if len(password) < 8:
        raise SystemExit("Error: password must be at least 8 characters")
    if not any(c.isupper() for c in password):
        raise SystemExit("Error: password must contain an uppercase letter")
    if not any(c.isdigit() for c in password):
        raise SystemExit("Error: password must contain a digit")


async def _main(args: argparse.Namespace) -> None:
    _validate_password(args.password)

    async with async_session_factory() as session:
        await run_seeds(session)

        role_repo = RoleRepository(session)
        roles = await role_repo.get_by_names(args.roles)
        known = {r.name for r in roles}
        missing = set(args.roles) - known
        if missing:
            raise SystemExit(f"Error: required roles not seeded: {sorted(missing)}")

        user_repo = UserRepository(session)
        user = await user_repo.get_by_email(args.email)
        if user is None:
            user = await user_repo.create(
                email=args.email,
                password_hash=hash_password(args.password),
                display_name=args.display_name,
                roles=roles,
            )
            await session.commit()
            granted = ", ".join(role.name for role in user.roles)
            print(f"Created account {user.email} with roles: [{granted}]")
        else:
            existing = {role.name for role in user.roles}
            to_add = [role for role in roles if role.name not in existing]
            changed = False
            if to_add:
                user.roles = list(user.roles) + to_add
                changed = True
            if args.reset_password:
                user.password_hash = hash_password(args.password)
                changed = True
            await session.commit()
            granted = ", ".join(sorted({role.name for role in user.roles}))
            if changed:
                note = " (password reset)" if args.reset_password else ""
                print(f"Updated {user.email} — roles now: [{granted}]{note}")
            else:
                print(f"{user.email} already has roles: [{granted}]")
            if not args.reset_password:
                print("Note: this script never changes a password unless --reset-password is passed.")

    await dispose_engine()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create or promote an admin account")
    parser.add_argument("--email", default=DEFAULT_EMAIL)
    parser.add_argument("--password", default=DEFAULT_PASSWORD)
    parser.add_argument("--display-name", default="Admin")
    parser.add_argument(
        "--roles",
        nargs="*",
        default=DEFAULT_ROLES,
        help="Role names to grant, e.g. --roles admin user",
    )
    parser.add_argument(
        "--reset-password",
        action="store_true",
        help="Force-set the password even when the account already exists",
    )
    asyncio.run(_main(parser.parse_args()))