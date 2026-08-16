from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProductStatus(str, Enum):
    available = "available"
    pending = "pending"
    sold = "sold"


class ProductBase(BaseModel):
    name: str = Field(title="The name of the `product`", min_length=1, max_length=50)
    description: str | None = Field(default=None, title="The description of the `product`", max_length=300)
    price: int = Field(gt=0, le=2_147_483_647, description="The price of the `product`, in cents")
    status: ProductStatus = Field(default=ProductStatus.available, title="Product status")
    category_id: UUID = Field(title="Category ID")


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=300)
    price: int | None = Field(
        default=None,
        gt=0,
        le=2_147_483_647,
        description="The price of the `product`, in cents",
    )
    status: ProductStatus | None = None
    category_id: UUID | None = None


class ProductRead(BaseModel):
    # Deliberately free of the Create constraints so legacy rows stay readable.
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(title="Product ID")
    name: str
    description: str | None = None
    price: int = Field(description="The price of the `product`, in cents")
    status: ProductStatus
    category_id: UUID
    created: datetime
    updated: datetime | None = None


Product = ProductRead
