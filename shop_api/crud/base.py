from collections.abc import Sequence
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Async CRUD running under the request transaction owned by `get_db`:
    methods flush (so constraint violations surface in the handler) and never commit.
    """

    def __init__(self, model: type[ModelType], *, order_by: Sequence[Any]) -> None:
        self.model = model
        # Mandatory deterministic ordering — LIMIT/OFFSET without it skips/duplicates rows.
        self.order_by = tuple(order_by)

    async def get(self, db: AsyncSession, id: UUID) -> ModelType | None:
        return await db.get(self.model, id)

    async def get_list(
        self,
        db: AsyncSession,
        *,
        where: Sequence[Any] = (),
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[ModelType]:
        statement = select(self.model).where(*where).order_by(*self.order_by).offset(offset).limit(limit)
        result = await db.execute(statement)
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, *, db_obj: ModelType, changes: dict[str, Any]) -> ModelType:
        for field, value in changes.items():
            setattr(db_obj, field, value)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, db_obj: ModelType) -> None:
        await db.delete(db_obj)
        await db.flush()
