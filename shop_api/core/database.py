from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from .base import Base  # re-exported so `from core.database import Base` keeps working
from .config import get_settings

async_engine: AsyncEngine = create_async_engine(
    get_settings().DATABASE_URI,
    # connect_args={"check_same_thread": False},  # Add it if you use SQLite
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    autoflush=False,
    expire_on_commit=False,
)
