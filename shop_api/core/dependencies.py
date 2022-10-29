from typing import Generator

from .database import AsyncSessionLocal


# Dependency
async def get_db() -> Generator:
    try:
        db = AsyncSessionLocal()
        yield db
    finally:
        db.close()
