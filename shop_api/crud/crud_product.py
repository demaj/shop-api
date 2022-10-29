from schemas import Product, ProductBase, ProductCreate

from .base import CRUDBase


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductBase]):
    pass


product = CRUDProduct(Product)
