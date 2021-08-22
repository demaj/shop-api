from app.crud.base import CRUDBase
from app.schemas import Category, CategoryCreate, CategoryUpdate


class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    pass


category = CRUDCategory(Category)
