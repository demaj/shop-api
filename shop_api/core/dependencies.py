from typing import Generator

from core.database import SessionLocal


# Dependency
def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
