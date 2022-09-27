from typing import Optional

from pydantic import BaseModel


class BaseFilter(BaseModel):
    class Config:
        use_enum_values = True


class CategoryFilter(BaseFilter):
    name: Optional[str]


class ProductFilter(BaseFilter):
    name: Optional[str] = None
    price: Optional[int] = None
    available: Optional[bool] = None
