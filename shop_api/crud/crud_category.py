from schemas import Category, CategoryBase, CategoryCreate

from .base import CRUDBase


class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryBase]):
    pass


category = CRUDCategory(Category)
