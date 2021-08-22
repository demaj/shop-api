from typing import Optional
from pydantic import BaseModel


# Shared properties
class CategoryBase(BaseModel):
    name: Optional[str] = None


# Properties too receive on Category creation
class CategoryCreate(CategoryBase):
    name: str


# Properties to receive on Category update
class CategoryUpdate(CategoryBase):
    pass


# Properties shared by models stored in DB
class CategoryInDBBase(CategoryBase):
    id: int
    name: str

    class Config:
        orm_mode = True


# Properties to return to client
class Category(CategoryInDBBase):
    pass


# Properties stored in DB
class CategoryInDB(CategoryInDBBase):
    pass
