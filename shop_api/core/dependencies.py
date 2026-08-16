from collections.abc import AsyncGenerator
from http import HTTPStatus
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

import models
from .database import AsyncSessionLocal
from core import security
from core.config import get_settings


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    # Transaction per request: crud methods flush; this commits on success,
    # rolls back when an exception propagates out of the handler.
    async with AsyncSessionLocal() as session:
        async with session.begin():
            yield session


SessionDep = Annotated[AsyncSession, Depends(get_db)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{get_settings().API_V1_STR}/auth/token")

TokenDep = Annotated[str, Depends(oauth2_scheme)]


async def get_current_user(db: SessionDep, token: TokenDep) -> models.User:
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_data = security.decode_access_token(token)
        user_id = UUID(token_data.sub)
    except (jwt.PyJWTError, ValidationError, ValueError):
        raise credentials_exception from None
    user = await db.get(models.User, user_id)
    if user is None:
        # A token for a deleted user must be indistinguishable from a bad token.
        raise credentials_exception
    return user


CurrentUser = Annotated[models.User, Depends(get_current_user)]


async def get_current_active_user(current_user: CurrentUser) -> models.User:
    if not current_user.is_active:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Inactive user")
    return current_user


CurrentActiveUser = Annotated[models.User, Depends(get_current_active_user)]


async def get_current_active_superuser(current_user: CurrentActiveUser) -> models.User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user


CurrentActiveSuperuser = Annotated[models.User, Depends(get_current_active_superuser)]
