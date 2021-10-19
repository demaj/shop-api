from crud.base import CRUDBase
from schemas import Category, CategoryCreate, CategoryUpdate


class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    pass


category = CRUDCategory(Category)
