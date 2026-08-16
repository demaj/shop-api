import logging

from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, OperationalError, ProgrammingError

import crud
from core.config import get_settings
from core.database import AsyncSessionLocal
from schemas import UserCreate

logger = logging.getLogger(__name__)


async def ensure_first_superuser() -> None:
    """Idempotent get-or-create for the configured first superuser."""

    settings = get_settings()
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                if await crud.user.get_by_email(session, email=settings.FIRST_SUPERUSER) is not None:
                    return
                await crud.user.create(
                    session,
                    obj_in=UserCreate(
                        email=settings.FIRST_SUPERUSER,
                        password=settings.FIRST_SUPERUSER_PASSWORD.get_secret_value(),
                        name="Superuser",
                        is_active=True,
                        is_superuser=True,
                    ),
                )
        logger.info("Created first superuser %s", settings.FIRST_SUPERUSER)
    except IntegrityError:
        # Another uvicorn worker won the get-or-create race — fine.
        logger.info("First superuser already exists")
    except (ProgrammingError, OperationalError) as exc:
        # A missing users table must not crash-loop the container (you could no
        # longer exec into it to run migrations).
        logger.warning("Skipping superuser bootstrap: %s. Run `alembic upgrade head`.", exc)
    except ValidationError as exc:
        logger.error("FIRST_SUPERUSER / FIRST_SUPERUSER_PASSWORD are invalid: %s", exc)
