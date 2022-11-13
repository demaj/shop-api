from typing import AsyncGenerator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from .database import AsyncSessionLocal


# Dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    try:
        db = AsyncSessionLocal()
        yield db
        # await db.commit()
    except SQLAlchemyError as exc:
        await db.rollback()
        raise exc
    except Exception as exc:
        raise exc
    finally:
        await db.close()
