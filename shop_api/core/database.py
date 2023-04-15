from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import get_settings

async_engine: AsyncEngine = create_async_engine(
    get_settings().DATABASE_URI,
    # connect_args={"check_some_thread": False},  # Add it if you use SQLite
    echo=True,
    future=True,
)

AsyncSessionLocal: AsyncSession = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)

Base = declarative_base()
