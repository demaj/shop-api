from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

import crud
from core import security
from core.dependencies import SessionDep
from helpers.tags import Tags
from schemas import Token

router = APIRouter(prefix="/auth", tags=[Tags.auth])


@router.post("/token", response_model=Token, summary="OAuth2 password login")
async def login_access_token(
    db: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """
    OAuth2-compatible token login: the `username` form field carries the user's email.
    """

    user = await crud.user.authenticate(db, email=form_data.username, password=form_data.password)
    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Inactive user")
    return Token(access_token=security.create_access_token(user.id), token_type="bearer")
