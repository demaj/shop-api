"""baseline

Revision ID: b9cf01d7dfcd
Revises:
Create Date: 2022-10-10 22:55:54.591044

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "b9cf01d7dfcd"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("idx_categories_id"), "categories", ["id"], unique=True)
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("available", sa.Boolean(), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("created", sa.DateTime(), server_default=sa.func.current_timestamp()),
        sa.Column("updated", sa.DateTime(), default=sa.func.now()),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("idx_products_id"), "products", ["id"], unique=True)
    op.create_index(op.f("idx_products_price"), "products", ["price"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("idx_categories_id"), table_name="categories")
    op.drop_table("categories")
    op.drop_index(op.f("idx_products_id"), table_name="products")
    op.drop_index(op.f("idx_products_price"), table_name="products")
    op.drop_table("products")
