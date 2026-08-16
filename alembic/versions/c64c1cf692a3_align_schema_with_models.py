"""align schema with models

Reconciles the physical schema (created by the baseline) with the ORM models:
- users table (was never migrated)
- price: float dollars -> integer cents
- available (nullable boolean) -> status (product_status enum, NOT NULL)
- naive timestamps -> timestamptz (values interpreted as UTC)
- constraint/index names moved to the metadata naming convention, redundant
  unique indexes on primary keys dropped, FK named with explicit RESTRICT

Pre-flight on a real database: SELECT max(length(description)) FROM products;
must be <= 300 or the description ALTER below will (deliberately) fail.

Revision ID: c64c1cf692a3
Revises: b9cf01d7dfcd
Create Date: 2026-08-16 00:15:54.444652

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c64c1cf692a3'
down_revision = 'b9cf01d7dfcd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. enum type (alembic only auto-creates PG enums inside create_table)
    op.execute("CREATE TYPE product_status AS ENUM ('available', 'pending', 'sold')")

    # 2. categories: drop redundant PK index; RENAME is metadata-only, no rebuild
    op.drop_index('idx_categories_id', table_name='categories')
    op.execute("ALTER TABLE categories RENAME CONSTRAINT categories_pkey TO pk_categories")
    op.execute("ALTER TABLE categories RENAME CONSTRAINT categories_name_key TO uq_categories_name")

    # 3. products index hygiene
    op.drop_index('idx_products_id', table_name='products')
    op.execute("ALTER TABLE products RENAME CONSTRAINT products_pkey TO pk_products")
    op.execute("ALTER INDEX idx_products_price RENAME TO ix_products_price")
    op.create_index(op.f('ix_products_name'), 'products', ['name'], unique=False)

    # 4. price: float dollars -> cents; without USING, PG silently rounds 19.99 -> 20 dollars
    op.execute(
        "ALTER TABLE products ALTER COLUMN price TYPE integer "
        "USING round(price::numeric * 100)::integer"
    )

    # 5. description: unbounded varchar -> varchar(300); fails loudly on longer rows
    op.alter_column('products', 'description',
               existing_type=sa.String(),
               type_=sa.String(length=300),
               existing_nullable=True)

    # 6. available -> status enum; discrete statements (alter_column emits DEFAULT before TYPE), IS TRUE/IS FALSE (CASE sends NULL to ELSE)
    op.alter_column('products', 'available', new_column_name='status')
    op.execute(
        "ALTER TABLE products ALTER COLUMN status TYPE product_status USING "
        "CASE WHEN status IS TRUE THEN 'available' "
        "     WHEN status IS FALSE THEN 'sold' "
        "     ELSE 'available' END::product_status"
    )
    op.execute("ALTER TABLE products ALTER COLUMN status SET DEFAULT 'available'")
    op.execute("ALTER TABLE products ALTER COLUMN status SET NOT NULL")

    # 7. timestamps -> timestamptz; explicit UTC so session TimeZone can't reinterpret history
    op.execute("UPDATE products SET created = now() WHERE created IS NULL")
    op.execute(
        "ALTER TABLE products ALTER COLUMN created TYPE timestamptz "
        "USING created AT TIME ZONE 'UTC'"
    )
    op.execute("ALTER TABLE products ALTER COLUMN created SET DEFAULT now()")
    op.execute("ALTER TABLE products ALTER COLUMN created SET NOT NULL")
    op.execute(
        "ALTER TABLE products ALTER COLUMN updated TYPE timestamptz "
        "USING updated AT TIME ZONE 'UTC'"
    )

    # 8. FK: named per convention, explicit RESTRICT
    op.drop_constraint('products_category_id_fkey', 'products', type_='foreignkey')
    op.create_foreign_key(op.f('fk_products_category_id_categories'), 'products', 'categories', ['category_id'], ['id'], ondelete='RESTRICT')

    # 9. users
    op.create_table('users',
    sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users'))
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')

    op.drop_constraint(op.f('fk_products_category_id_categories'), 'products', type_='foreignkey')
    op.create_foreign_key('products_category_id_fkey', 'products', 'categories', ['category_id'], ['id'])

    op.execute(
        "ALTER TABLE products ALTER COLUMN updated TYPE timestamp "
        "USING updated AT TIME ZONE 'UTC'"
    )
    op.execute("ALTER TABLE products ALTER COLUMN created DROP NOT NULL")
    op.execute("ALTER TABLE products ALTER COLUMN created DROP DEFAULT")
    op.execute(
        "ALTER TABLE products ALTER COLUMN created TYPE timestamp "
        "USING created AT TIME ZONE 'UTC'"
    )
    op.execute("ALTER TABLE products ALTER COLUMN created SET DEFAULT CURRENT_TIMESTAMP")

    # status -> available is lossy: pending/sold both become false
    op.execute("ALTER TABLE products ALTER COLUMN status DROP DEFAULT")
    op.execute("ALTER TABLE products ALTER COLUMN status DROP NOT NULL")
    op.execute(
        "ALTER TABLE products ALTER COLUMN status TYPE boolean "
        "USING (status = 'available')"
    )
    op.alter_column('products', 'status', new_column_name='available')
    op.execute("DROP TYPE product_status")

    op.alter_column('products', 'description',
               existing_type=sa.String(length=300),
               type_=sa.String(),
               existing_nullable=True)

    op.execute("ALTER TABLE products ALTER COLUMN price TYPE double precision USING price / 100.0")

    op.drop_index(op.f('ix_products_name'), table_name='products')
    op.execute("ALTER INDEX ix_products_price RENAME TO idx_products_price")
    op.execute("ALTER TABLE products RENAME CONSTRAINT pk_products TO products_pkey")
    op.create_index('idx_products_id', 'products', ['id'], unique=True)

    op.execute("ALTER TABLE categories RENAME CONSTRAINT uq_categories_name TO categories_name_key")
    op.execute("ALTER TABLE categories RENAME CONSTRAINT pk_categories TO categories_pkey")
    op.create_index('idx_categories_id', 'categories', ['id'], unique=True)
