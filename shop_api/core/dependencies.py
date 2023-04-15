from typing import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from .database import AsyncSessionLocal, async_engine


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
