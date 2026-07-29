"""add due_at to loans

Revision ID: 0005_add_loans_due_at
Revises: 0004_alter_books_quantity
Create Date: 2026-07-29 17:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005_add_loans_due_at"
down_revision: Union[str, None] = "0004_alter_books_quantity"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "loans",
        sa.Column(
            "due_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(now() + interval '7 days')"),
            nullable=False,
        ),
    )
    op.create_index(op.f("ix_loans_due_at"), "loans", ["due_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_loans_due_at"), table_name="loans")
    op.drop_column("loans", "due_at")
