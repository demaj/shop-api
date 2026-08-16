from datetime import datetime, timedelta, timezone
from typing import Final
from uuid import UUID

import anyio.to_thread
import jwt
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError

from core.config import get_settings
from schemas.token import TokenData

_password_hash: Final = PasswordHash.recommended()

# Verified against this so unknown-email and wrong-password cost the same time.
_DUMMY_HASH: Final = _password_hash.hash("dummy-password-for-timing")


def hash_password_sync(password: str) -> str:
    return _password_hash.hash(password)


def verify_password_sync(password: str, hashed_password: str) -> bool:
    try:
        return _password_hash.verify(password, hashed_password)
    except (UnknownHashError, TypeError):
        # A corrupt/empty stored hash must read as "wrong password", not a 500.
        return False


async def hash_password(password: str) -> str:
    # Argon2 costs ~100ms CPU and 64MiB per call — never run it on the event loop.
    return await anyio.to_thread.run_sync(hash_password_sync, password)


async def verify_password(password: str, hashed_password: str) -> bool:
    return await anyio.to_thread.run_sync(verify_password_sync, password, hashed_password)


async def verify_dummy_password(password: str) -> None:
    await anyio.to_thread.run_sync(verify_password_sync, password, _DUMMY_HASH)


def create_access_token(subject: str | UUID, expires_delta: timedelta | None = None) -> str:
    settings = get_settings()
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    now = datetime.now(timezone.utc)
    payload = {"sub": str(subject), "iat": now, "exp": now + expires_delta}
    return jwt.encode(payload, settings.SECRET_KEY.get_secret_value(), algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> TokenData:
    settings = get_settings()
    payload = jwt.decode(
        token,
        settings.SECRET_KEY.get_secret_value(),
        algorithms=[settings.ALGORITHM],
        options={"require": ["exp", "iat", "sub"]},
    )
    return TokenData.model_validate(payload)
