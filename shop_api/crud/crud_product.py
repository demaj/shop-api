from .base import CRUDBase
from schemas import Product, ProductBase, ProductCreate


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductBase]):
    pass


product = CRUDProduct(Product)
