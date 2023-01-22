from typing import AsyncGenerator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from .database import AsyncSessionLocal, async_engine

# async def get_db() -> AsyncGenerator[AsyncSession, None]:
#     async with AsyncSessionLocal.begin() as db:
#         yield db
#     await async_engine.dispose()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async_session = AsyncSessionLocal()
    try:
        yield async_session
        await async_session.commit()
    except SQLAlchemyError as exc:
        await async_session.rollback()
        raise exc
    finally:
        await async_session.close()
        await async_engine.dispose()
