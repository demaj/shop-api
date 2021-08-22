from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# database = databases.Database(settings.DATABASE_URL)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_some_thread": False},
    echo=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
