from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    name: str = Field(
        title="The name of the `category`",
        min_length=3,
        max_length=50,
    )


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=50)


class CategoryRead(BaseModel):
    # Deliberately free of the Create constraints so legacy rows stay readable.
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(title="Category ID")
    name: str


Category = CategoryRead
