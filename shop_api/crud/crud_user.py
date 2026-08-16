from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from .base import CRUDBase
from core import security
from schemas import UserCreate, UserUpdate


class CRUDUser(CRUDBase[models.User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> models.User | None:
        result = await db.execute(select(models.User).where(models.User.email == email))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> models.User:
        # Plaintext never reaches the model: hash here, for every writer.
        data = obj_in.model_dump(exclude={"password"})
        data["hashed_password"] = await security.hash_password(obj_in.password)
        db_obj = models.User(**data)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def authenticate(self, db: AsyncSession, *, email: str, password: str) -> models.User | None:
        user = await self.get_by_email(db, email=email)
        if user is None:
            # Same wall-clock cost as a real verification (anti user-enumeration).
            await security.verify_dummy_password(password)
            return None
        if not await security.verify_password(password, user.hashed_password):
            return None
        return user


user = CRUDUser(models.User, order_by=(models.User.email.asc(), models.User.id.asc()))
