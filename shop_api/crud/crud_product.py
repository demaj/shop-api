from collections.abc import Sequence
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

import models
from .base import CRUDBase
from helpers.params import ProductListParams
from schemas import ProductCreate, ProductUpdate


class CRUDProduct(CRUDBase[models.Product, ProductCreate, ProductUpdate]):
    def where(self, params: ProductListParams) -> list[Any]:
        clauses: list[Any] = []
        if params.name:
            clauses.append(models.Product.name == params.name)
        if params.price is not None:
            clauses.append(models.Product.price == params.price)
        if params.status is not None:
            clauses.append(models.Product.status == params.status)
        return clauses

    async def get_page(self, db: AsyncSession, *, params: ProductListParams) -> Sequence[models.Product]:
        return await self.get_list(db, where=self.where(params), offset=params.offset, limit=params.limit)


product = CRUDProduct(
    models.Product,
    order_by=(models.Product.created.desc(), models.Product.id.asc()),
)
