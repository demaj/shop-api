from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from core.config import get_settings
from core.dependencies import get_db


@pytest.fixture(scope="session")
async def engine() -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(get_settings().DATABASE_URI, poolclass=NullPool)
    try:
        async with engine.connect():
            pass
    except (OSError, DBAPIError) as exc:
        pytest.skip(f"PostgreSQL not reachable at DATABASE_URI: {exc}")
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_connection(engine: AsyncEngine) -> AsyncIterator[AsyncConnection]:
    # One outer transaction per test, always rolled back — no cross-test bleed.
    async with engine.connect() as connection:
        transaction = await connection.begin()
        yield connection
        await transaction.rollback()


@pytest.fixture(autouse=True)
def override_db(app: FastAPI, db_connection: AsyncConnection) -> AsyncIterator[None]:
    async def _get_db() -> AsyncIterator[AsyncSession]:
        async with AsyncSession(
            bind=db_connection,
            join_transaction_mode="create_savepoint",
            expire_on_commit=False,
        ) as session:
            # Mirrors production commit-on-success; the "commit" releases a savepoint.
            async with session.begin():
                yield session

    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()
