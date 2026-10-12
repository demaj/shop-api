from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

import crud
import models
from core import security
from core.database import AsyncSessionLocal
from core.errors import ApiError, ErrorCode
from helpers.tags import Tags
from schemas import Token
from schemas.user import PASSWORD_MAX_LENGTH

router = APIRouter(prefix="/auth", tags=[Tags.auth])


async def login_candidate(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> models.User | None:
    # Own short-lived session so the DB connection is released before the ~100ms
    # argon2 verify in the handler. A dependency seam so tests can override it.
    async with AsyncSessionLocal() as session:
        return await crud.user.get_by_email(session, email=form_data.username)


@router.post("/token", response_model=Token, summary="OAuth2 password login")
async def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user: Annotated[models.User | None, Depends(login_candidate)],
) -> Token:
    """
    OAuth2-compatible token login: the `username` form field carries the user's email.
    """

    unauthorized = ApiError(
        ErrorCode.invalid_credentials,
        "Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if len(form_data.password) > PASSWORD_MAX_LENGTH:
        raise unauthorized
    if user is None:
        # Same wall-clock cost as a real verification (anti user-enumeration).
        await security.verify_dummy_password(form_data.password)
        raise unauthorized
    if not await security.verify_password(form_data.password, user.hashed_password):
        raise unauthorized
    if not user.is_active:
        raise unauthorized
    return Token(access_token=security.create_access_token(user.id), token_type="bearer")
