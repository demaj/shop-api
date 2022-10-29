from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    product = relationship("Product", back_populates="category")

    def __repr__(self) -> str:
        return f"Category(id={self.id!r}, name={self.name!r})"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Integer)
    available = Column(Boolean, default=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), onupdate=func.now())

    category = relationship("Category", back_populates="products")

    def __repr__(self) -> str:
        return f"Product(id={self.id!r}, name={self.name!r}, price={self.price}, available={self.available})"
