from crud.base import CRUDBase
from schemas import Product, ProductCreate, ProductBase


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductBase]):
    pass


product = CRUDProduct(Product)
