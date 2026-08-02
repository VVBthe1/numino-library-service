"""soft delete books (deleted_at)

Revision ID: 0006_books_soft_delete
Revises: 0005_add_loans_due_at
Create Date: 2026-08-02 16:15:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006_books_soft_delete"
down_revision: Union[str, None] = "0005_add_loans_due_at"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "books",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f("ix_books_deleted_at"), "books", ["deleted_at"], unique=False)

    op.drop_index(op.f("ix_books_isbn"), table_name="books")
    op.create_index(op.f("ix_books_isbn"), "books", ["isbn"], unique=False)
    op.create_index(
        "ux_books_isbn_active",
        "books",
        ["isbn"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("ux_books_isbn_active", table_name="books")
    op.drop_index(op.f("ix_books_isbn"), table_name="books")
    op.create_index(op.f("ix_books_isbn"), "books", ["isbn"], unique=True)
    op.drop_index(op.f("ix_books_deleted_at"), table_name="books")
    op.drop_column("books", "deleted_at")
