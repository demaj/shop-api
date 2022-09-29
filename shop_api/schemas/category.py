from pydantic import BaseModel


class CategoryBase(BaseModel):
    name: str | None = None


class CategoryCreate(CategoryBase):
    name: str


class Category(CategoryCreate):
    id: int

    class Config:
        orm_mode = True
