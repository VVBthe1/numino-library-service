from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Enum as SAEnum

from app.database import Base

if TYPE_CHECKING:
    from app.models.loan import Loan


class Genre(str, enum.Enum):
    FICTION = "fiction"
    NON_FICTION = "non_fiction"
    MYSTERY = "mystery"
    SCIENCE_FICTION = "science_fiction"
    FANTASY = "fantasy"
    BIOGRAPHY = "biography"
    HISTORY = "history"
    ROMANCE = "romance"
    THRILLER = "thriller"
    CHILDREN = "children"
    OTHER = "other"


class Book(Base):
    __tablename__ = "books"
    __table_args__ = (
        CheckConstraint("total_quantity >= 0", name="ck_books_total_quantity_non_negative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    isbn: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    publication_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    publisher: Mapped[str | None] = mapped_column(String(255), nullable=True)
    genre: Mapped[Genre] = mapped_column(
        SAEnum(
            Genre,
            name="genre",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            native_enum=True,
        ),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    total_quantity: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="1"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    loans: Mapped[list[Loan]] = relationship("Loan", back_populates="book")
