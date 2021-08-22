from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud
from app.core import dependencies

router = APIRouter(prefix="/products")


@router.get("/", response_model=List[schemas.Product])
def read_products(
        db: Session = Depends(dependencies.get_db),
        skip: int = 0,
        limit: int = 100,
) -> Any:
    """ Retrieve products. """
    products = crud.product.get_list(db=db, skip=skip, limit=limit)
    return products


@router.post("/", response_model=schemas.Product)
def create_product(
        *,
        db: Session = Depends(dependencies.get_db),
        product_in: schemas.ProductCreate,
) -> Any:
    """ Create new product. """
    product = crud.product.create(db=db, obj_in=product_in)
    return product


@router.put("/{id}", response_model=schemas.Product)
def update_product(
        *,
        db: Session = Depends(dependencies.get_db),
        id: int,
        product_in: schemas.ProductUpdate,
) -> Any:
    """ Update a product. """
    product = crud.product.get(db=db, id=id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product = crud.product.update(db=db, db_obj=product, obj_in=product_in)
    return product


@router.get("/{id}", response_model=schemas.Product)
def read_product(
        *,
        db: Session = Depends(dependencies.get_db),
        id: int,
) -> Any:
    """ Get product by ID. """
    product = crud.product.get(db=db, id=id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.delete("/{id}", response_model=schemas.Product)
def delete_product(
        *,
        db: Session = Depends(dependencies.get_db),
        id: int,
) -> Any:
    """ Delete a product. """
    product = crud.product.get(db=db, id=id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product = crud.product.remove(db=db, id=id)
    return product
