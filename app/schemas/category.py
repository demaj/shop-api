from typing import Optional

from pydantic import BaseModel


class CategoryBase(BaseModel):
    name: Optional[str] = None


class CategoryCreate(CategoryBase):
    name: str


class Category(CategoryCreate):
    id: int

    class Config:
        orm_mode = True
