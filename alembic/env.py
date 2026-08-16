import asyncio
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# shop_api/ is the application's import root (models.py does `from core.base import Base`).
# Done here rather than via prepend_sys_path: alembic.ini is baked into the docker image
# (not volume-mounted), and ini paths resolve against the process cwd anyway.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shop_api"))

from core.base import Base  # noqa: E402
import models  # noqa: E402,F401  (imported for its side effect: registers tables on Base.metadata)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# The database URL comes from the environment, same as the application's
# settings; the value in alembic.ini is only a fallback.
if database_uri := os.getenv("DATABASE_URI"):
    config.set_main_option("sqlalchemy.url", database_uri.replace("%", "%%"))

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# compare_type defaults to True since alembic 1.12 — no need to pass it.
# compare_server_default stays off: on Postgres it yields permanent false
# positives (now() vs CURRENT_TIMESTAMP, 'available' vs 'available'::product_status).
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
