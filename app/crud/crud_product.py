from crud.base import CRUDBase
from schemas import Product, ProductCreate, ProductUpdate


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    pass


product = CRUDProduct(Product)
