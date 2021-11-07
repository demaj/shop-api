from crud.base import CRUDBase
from schemas import Category, CategoryCreate, CategoryBase


class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryBase]):
    pass


category = CRUDCategory(Category)
