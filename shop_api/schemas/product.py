from typing import Optional

from pydantic import BaseModel


class ProductBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    available: Optional[bool] = None
    created: Optional[str] = None
    updated: Optional[str] = None


class ProductCreate(ProductBase):
    name: str
    price: int


class Product(ProductCreate):
    id: int
    description: str

    class Config:
        orm_mode = True
