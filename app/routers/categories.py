from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import crud
import schemas
from core import dependencies

router = APIRouter(prefix="/categories")


@router.get("/", response_model=List[schemas.Category])
def read_categories(
        db: Session = Depends(dependencies.get_db),
        skip: int = 0,
        limit: int = 100,
) -> Any:
    """ Retrieve categories. """
    categories = crud.category.get_list(db, skip=skip, limit=limit)
    return categories


@router.post("/", response_model=schemas.Category)
def create_category(
        *,
        db: Session = Depends(dependencies.get_db),
        category_in: schemas.CategoryCreate,
) -> Any:
    """ Create new category. """
    category = crud.category.create(db=db, obj_in=category_in)
    return category


@router.put("/{id}", response_model=schemas.Category)
def update_category(
        *,
        db: Session = Depends(dependencies.get_db),
        id: int,
        category_in: schemas.CategoryUpdate,
) -> Any:
    """ Update a category. """
    category = crud.category.get(db=db, id=id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    category = crud.category.update(db=db, db_obj=category, obj_in=category_in)
    return category


@router.get("/{id}", response_model=schemas.Category)
def read_category(
        *,
        db: Session = Depends(dependencies.get_db),
        id: int,
) -> Any:
    """ Get category by ID. """
    category = crud.category.get(db=db, id=id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.delete("/{id}", response_model=schemas.Category)
def delete_category(
        *,
        db: Session = Depends(dependencies.get_db),
        id: int,
) -> Any:
    """ Delete a category. """
    category = crud.category.get(db=db, id=id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    category = crud.category.remove(db=db, id=id)
    return category
