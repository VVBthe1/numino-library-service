"""soft delete members (deleted_at)

Revision ID: 0007_members_soft_delete
Revises: 0006_books_soft_delete
Create Date: 2026-08-02 16:25:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007_members_soft_delete"
down_revision: Union[str, None] = "0006_books_soft_delete"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "members",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        op.f("ix_members_deleted_at"), "members", ["deleted_at"], unique=False
    )

    op.drop_index(op.f("ix_members_email"), table_name="members")
    op.create_index(op.f("ix_members_email"), "members", ["email"], unique=False)
    op.create_index(
        "ux_members_email_active",
        "members",
        ["email"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("ux_members_email_active", table_name="members")
    op.drop_index(op.f("ix_members_email"), table_name="members")
    op.create_index(op.f("ix_members_email"), "members", ["email"], unique=True)
    op.drop_index(op.f("ix_members_deleted_at"), table_name="members")
    op.drop_column("members", "deleted_at")
