from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

import crud
import models
import schemas
from core.dependencies import CurrentActiveUser, SessionDep, get_current_active_superuser
from helpers.tags import Tags

router = APIRouter(prefix="/users", tags=[Tags.users])


@router.get("/me", response_model=schemas.UserRead)
async def read_user_me(current_user: CurrentActiveUser) -> models.User:
    """
    Get the currently authenticated user.
    """

    return current_user


@router.post(
    "",
    response_model=schemas.UserRead,
    status_code=HTTPStatus.CREATED,
    dependencies=[Depends(get_current_active_superuser)],
)
async def create_user(db: SessionDep, user_in: schemas.UserCreate) -> models.User:
    """
    Create a new user. Superusers only.
    """

    if await crud.user.get_by_email(db, email=user_in.email) is not None:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="A user with this email already exists",
        )
    return await crud.user.create(db, obj_in=user_in)
