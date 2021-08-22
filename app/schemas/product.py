from typing import Optional
from pydantic import BaseModel


# Shared properties
class ProductBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    available: Optional[bool] = None
    created: Optional[str] = None
    updated: Optional[str] = None


# Properties too receive on product creation
class ProductCreate(ProductBase):
    name: str
    price: int


# Properties to receive on product update
class ProductUpdate(ProductBase):
    pass


# Properties shared by models stored in DB
class ProductInDBBase(ProductBase):
    id: int
    name: str
    description: str
    price: int

    class Config:
        orm_mode = True


# Properties to return to client
class Product(ProductInDBBase):
    pass


# Properties stored in DB
class ProductInDB(ProductInDBBase):
    pass
