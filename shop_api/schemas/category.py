from uuid import UUID, uuid4

from pydantic import BaseModel, Field, Required


class CategoryBase(BaseModel):
    name: str | None = None


class CategoryCreate(CategoryBase):
    name: str = Field(
        default=Required,
        title="The name of the `category`",
        min_length=3,
        max_length=50,
    )


class Category(CategoryCreate):
    id: UUID = Field(title="Category ID", default_factory=uuid4)

    class Config:
        orm_mode = True
