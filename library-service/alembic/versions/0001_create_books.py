"""create books table

Revision ID: 0001_create_books
Revises:
Create Date: 2026-07-28 18:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_create_books"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

genre_enum = postgresql.ENUM(
    "fiction",
    "non_fiction",
    "mystery",
    "science_fiction",
    "fantasy",
    "biography",
    "history",
    "romance",
    "thriller",
    "children",
    "other",
    name="genre",
    create_type=False,
)


def upgrade() -> None:
    genre_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "books",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("author", sa.String(length=255), nullable=False),
        sa.Column("isbn", sa.String(length=20), nullable=False),
        sa.Column("publication_year", sa.Integer(), nullable=True),
        sa.Column("publisher", sa.String(length=255), nullable=True),
        sa.Column("genre", genre_enum, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "is_available",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_books_isbn"), "books", ["isbn"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_books_isbn"), table_name="books")
    op.drop_table("books")
    genre_enum.drop(op.get_bind(), checkfirst=True)
