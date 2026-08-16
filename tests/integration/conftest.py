from collections.abc import AsyncIterator
from typing import Annotated

import pytest
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

import crud
import models
from core.config import get_settings
from core.dependencies import get_db
from routers.auth import login_candidate


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

    async def _login_candidate(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    ) -> models.User | None:
        # login opens its own session in production; here it must read the
        # rolled-back test transaction, not a fresh pooled connection.
        async with AsyncSession(
            bind=db_connection, join_transaction_mode="create_savepoint", expire_on_commit=False
        ) as session:
            return await crud.user.get_by_email(session, email=form_data.username)

    app.dependency_overrides[get_db] = _get_db
    app.dependency_overrides[login_candidate] = _login_candidate
    yield
    app.dependency_overrides.clear()
