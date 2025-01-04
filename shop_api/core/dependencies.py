from typing import AsyncGenerator

from fastapi import Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from .database import AsyncSessionLocal, async_engine
from schemas import User


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async_session = AsyncSessionLocal()
    try:
        async with async_session.begin():
            yield async_session
        await async_session.commit()
    except SQLAlchemyError as exc:
        await async_session.rollback()
        raise exc
    finally:
        await async_session.close()
        await async_engine.dispose()


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(),
) -> User:
    query = "SELECT "
    user = db.get(User)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user
