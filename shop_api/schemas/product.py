from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl, Required


class ProductImage(BaseModel):
    url: HttpUrl
    name: str


class ProductBase(BaseModel):
    name: str | None = None
    description: str | None = Field(default=None, title="The description of the `product`", max_length=300)
    price: float | None = None
    available: bool | None = None
    tags: set[str] = set()
    created: datetime | None = None
    updated: datetime | None = None


class ProductCreate(ProductBase):
    name: str = Field(default=Required, title="The name of the `product`", max_length=50)
    price: float = Field(default=Required, gt=0, description="The price of the `product`")


class Product(ProductCreate):
    id: int
    description: str

    class Config:
        orm_mode = True
