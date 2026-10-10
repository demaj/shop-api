from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from .base import Base  # re-exported so `from core.database import Base` keeps working
from .config import get_settings

settings = get_settings()

async_engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URI,
    echo=settings.SQL_ECHO,
    pool_pre_ping=True,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    hide_parameters=True,
    connect_args={
        "timeout": settings.DATABASE_CONNECT_TIMEOUT,
        "command_timeout": settings.DATABASE_COMMAND_TIMEOUT,
    },
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    autoflush=False,
    expire_on_commit=False,
)
