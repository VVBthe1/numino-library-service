from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.book import Book, Genre
from app.models.loan import Loan


class BookRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, book_id: int) -> Book | None:
        return self._db.query(Book).filter(Book.id == book_id).first()

    def get_by_isbn(self, isbn: str) -> Book | None:
        return self._db.query(Book).filter(Book.isbn == isbn).first()

    def list(
        self,
        *,
        title_query: str | None = None,
        author_query: str | None = None,
        genre: Genre | None = None,
        publisher: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Book]:
        query = self._db.query(Book)
        if title_query:
            query = query.filter(Book.title.ilike(f"%{title_query}%"))
        if author_query:
            query = query.filter(Book.author.ilike(f"%{author_query}%"))
        if genre:
            query = query.filter(Book.genre == genre)
        if publisher:
            query = query.filter(Book.publisher == publisher)
        return query.offset(offset).limit(limit).all()

    def add(self, book: Book) -> Book:
        self._db.add(book)
        self._db.commit()
        return book

    def delete(self, book: Book) -> None:
        self._db.delete(book)
        self._db.commit()

    def list_overdue(
        self,
        *,
        publisher: str | None = None,
        genre: Genre | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Book]:
        query = self._db.query(Book)
        if publisher:
            query = query.filter(Book.publisher == publisher)
        if genre:
            query = query.filter(Book.genre == genre)
        return (
            query.join(Loan)
                .filter(Loan.due_at < datetime.now(timezone.utc))
                .group_by(Book.id)
                .having(func.count(Loan.id) < Book.total_quantity)
                .offset(offset)
                .limit(limit)
                .all()
        )

    def list_out_of_stock(
        self,
        *,
        publisher: str | None = None,
        genre: Genre | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Book]:
        query = self._db.query(Book)
        if publisher:
            query = query.filter(Book.publisher == publisher)
        if genre:
            query = query.filter(Book.genre == genre)
        active_loan = (Loan.book_id == Book.id) & (Loan.returned_at.is_(None))
        return (
            query.outerjoin(Loan, active_loan)
            .group_by(Book.id)
            .having(func.count(Loan.id) >= Book.total_quantity)
            .offset(offset)
            .limit(limit)
            .all()
        )
