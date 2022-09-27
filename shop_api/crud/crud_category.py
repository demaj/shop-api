from crud.base import CRUDBase
from schemas import Category, CategoryBase, CategoryCreate


class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryBase]):
    pass


category = CRUDCategory(Category)
