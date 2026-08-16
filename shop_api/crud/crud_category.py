from collections.abc import Sequence
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

import models
from .base import CRUDBase
from helpers.params import CategoryListParams
from schemas import CategoryCreate, CategoryUpdate


class CRUDCategory(CRUDBase[models.Category, CategoryCreate, CategoryUpdate]):
    def where(self, params: CategoryListParams) -> list[Any]:
        clauses: list[Any] = []
        if params.name:
            clauses.append(models.Category.name == params.name)
        return clauses

    async def get_page(self, db: AsyncSession, *, params: CategoryListParams) -> Sequence[models.Category]:
        return await self.get_list(db, where=self.where(params), offset=params.offset, limit=params.limit)


category = CRUDCategory(
    models.Category,
    order_by=(models.Category.name.asc(), models.Category.id.asc()),
)
