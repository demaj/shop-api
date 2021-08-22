from app.crud.base import CRUDBase
from app.schemas import Product, ProductCreate, ProductUpdate


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    pass


product = CRUDProduct(Product)
