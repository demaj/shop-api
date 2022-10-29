import databases
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings

database = databases.Database(settings.SQLALCHEMY_DATABASE_URI, ssl=False)

engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    # connect_args={"check_some_thread": False},  # Add it if you use SQLite
    echo=True,
    future=True,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

Base = declarative_base()
