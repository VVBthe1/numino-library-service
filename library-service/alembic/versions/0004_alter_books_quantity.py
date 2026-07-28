"""replace books.is_available with total_quantity

Revision ID: 0004_alter_books_quantity
Revises: 0003_create_loans
Create Date: 2026-07-28 19:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004_alter_books_quantity"
down_revision: Union[str, None] = "0003_create_loans"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "books",
        sa.Column(
            "total_quantity",
            sa.Integer(),
            server_default=sa.text("1"),
            nullable=False,
        ),
    )
    op.create_check_constraint(
        "ck_books_total_quantity_non_negative",
        "books",
        "total_quantity >= 0",
    )
    op.drop_column("books", "is_available")


def downgrade() -> None:
    op.add_column(
        "books",
        sa.Column(
            "is_available",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
    )
    op.drop_constraint(
        "ck_books_total_quantity_non_negative",
        "books",
        type_="check",
    )
    op.drop_column("books", "total_quantity")
