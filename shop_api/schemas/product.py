from datetime import datetime

from pydantic import BaseModel


class ProductBase(BaseModel):
    name: str | None = None
    description: str | None = None
    price: str | None = None
    available: bool | None = None
    created: datetime | None = None
    updated: datetime | None = None


class ProductCreate(ProductBase):
    name: str
    price: int


class Product(ProductCreate):
    id: int
    description: str

    class Config:
        orm_mode = True
