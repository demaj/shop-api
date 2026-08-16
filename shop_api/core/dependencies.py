from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from .database import AsyncSessionLocal
from schemas import User


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    # Transaction per request: the routers issue raw INSERT/UPDATE statements
    # without committing, relying on this commit-on-success / rollback-on-error.
    async with AsyncSessionLocal() as session:
        async with session.begin():
            yield session


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(),
) -> User:
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
