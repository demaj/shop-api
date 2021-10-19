import databases
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings


SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

database = databases.Database(settings.DATABASE_URL)

engine = create_engine(
    settings.DATABASE_URL,
    # connect_args={"check_some_thread": False},  # Add it if you use SQLite
    echo=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
