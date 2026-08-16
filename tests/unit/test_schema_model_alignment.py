"""Drift guard: models and pydantic schemas must describe the same database.

Runs without a database — `alembic check` covers the models<->migrations side.
"""
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from annotated_types import Le, MaxLen
from pydantic import EmailStr, ValidationError
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Integer, String
from sqlalchemy.orm import configure_mappers

import models
from schemas import CategoryCreate, CategoryRead, ProductCreate, ProductRead, ProductStatus, UserCreate, UserRead


def test_mappers_configure() -> None:
    configure_mappers()


def test_relationship_round_trip() -> None:
    category = models.Category(name="Tea")
    product = models.Product(name="Earl Grey", price=1999)
    category.products.append(product)
    assert product.category is category


def test_read_models_cover_exact_column_sets() -> None:
    assert set(ProductRead.model_fields) == {c.key for c in models.Product.__table__.columns}
    assert set(CategoryRead.model_fields) == {c.key for c in models.Category.__table__.columns}
    user_columns = {c.key for c in models.User.__table__.columns}
    assert set(UserRead.model_fields) <= user_columns
    assert "hashed_password" not in UserRead.model_fields


@pytest.mark.parametrize(
    ("create_model", "table"),
    [
        (ProductCreate, models.Product.__table__),
        (CategoryCreate, models.Category.__table__),
        (UserCreate, models.User.__table__),
    ],
)
def test_create_max_lengths_match_column_lengths(create_model, table) -> None:
    for field_name, field in create_model.model_fields.items():
        if field_name not in table.columns:
            continue
        column_type = table.columns[field_name].type
        # sa.Enum subclasses String; EmailStr is capped at 254 chars by email_validator
        if isinstance(column_type, SAEnum) or field.annotation is EmailStr:
            continue
        if not isinstance(column_type, String) or column_type.length is None:
            continue
        max_lens = [m.max_length for m in field.metadata if isinstance(m, MaxLen)]
        assert max_lens, f"{create_model.__name__}.{field_name} has no max_length but column is String({column_type.length})"
        assert max_lens[0] == column_type.length, f"{create_model.__name__}.{field_name}"


def test_integer_columns_have_int32_bounded_create_fields() -> None:
    # PG integer is int32; an unbounded pydantic int would 500 in asyncpg instead of 422ing.
    int32_max = 2_147_483_647
    for create_model, table in [(ProductCreate, models.Product.__table__)]:
        for field_name, field in create_model.model_fields.items():
            if field_name not in table.columns:
                continue
            if type(table.columns[field_name].type) is not Integer:
                continue
            upper_bounds = [m.le for m in field.metadata if isinstance(m, Le)]
            assert upper_bounds and upper_bounds[0] <= int32_max, f"{create_model.__name__}.{field_name}"


def test_product_read_validates_orm_instance() -> None:
    orm_product = models.Product(
        id=uuid4(),
        name="Earl Grey",
        description=None,
        price=1999,
        status=ProductStatus.available,
        category_id=uuid4(),
        created=datetime.now(timezone.utc),
        updated=None,
    )
    read = ProductRead.model_validate(orm_product)
    assert read.price == 1999
    assert read.status is ProductStatus.available
    assert read.created.tzinfo is not None
    assert read.updated is None


def test_read_models_require_id() -> None:
    with pytest.raises(ValidationError):
        CategoryRead.model_validate({"name": "Tea"})
    with pytest.raises(ValidationError):
        ProductRead.model_validate(
            {"name": "x", "price": 1, "status": "available", "category_id": uuid4(), "created": datetime.now(timezone.utc)}
        )


def test_read_models_accept_legacy_rows() -> None:
    # Rows predating the Create constraints (price 0, over-long name) must stay readable.
    read = ProductRead.model_validate(
        {
            "id": uuid4(),
            "name": "x" * 80,
            "price": 0,
            "status": "sold",
            "category_id": uuid4(),
            "created": datetime.now(timezone.utc),
        }
    )
    assert read.price == 0


def test_status_enum_matches_column_enum() -> None:
    assert set(models.Product.__table__.c.status.type.enums) == {s.value for s in ProductStatus}


def test_price_is_integer_cents() -> None:
    assert models.Product.__table__.c.price.type.python_type is int
