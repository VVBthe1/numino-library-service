"""create loans table

Revision ID: 0003_create_loans
Revises: 0002_create_members
Create Date: 2026-07-28 18:31:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003_create_loans"
down_revision: Union[str, None] = "0002_create_members"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "loans",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.Integer(), nullable=False),
        sa.Column(
            "borrowed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("returned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["book_id"],
            ["books.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["member_id"],
            ["members.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_loans_book_id"), "loans", ["book_id"], unique=False)
    op.create_index(op.f("ix_loans_member_id"), "loans", ["member_id"], unique=False)
    op.create_index(
        "ix_loans_book_id_active",
        "loans",
        ["book_id"],
        unique=False,
        postgresql_where=sa.text("returned_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("ix_loans_book_id_active", table_name="loans")
    op.drop_index(op.f("ix_loans_member_id"), table_name="loans")
    op.drop_index(op.f("ix_loans_book_id"), table_name="loans")
    op.drop_table("loans")
