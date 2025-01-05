from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    name: str | None = None


class CategoryCreate(CategoryBase):
    name: str = Field(
        title="The name of the `category`",
        min_length=3,
        max_length=50,
    )


class Category(CategoryCreate):
    id: UUID = Field(title="Category ID", default_factory=uuid4)
    model_config = ConfigDict(from_attributes=True)
