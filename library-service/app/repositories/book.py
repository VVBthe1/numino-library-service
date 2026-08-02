from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from app.models.book import Book, Genre
from app.models.loan import Loan


class BookRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def _alive(self):
        return self._db.query(Book).filter(Book.deleted_at.is_(None))

    def get_by_id(self, book_id: int, *, with_trashed: bool = False) -> Book:
        if with_trashed:
            book = self._db.get(Book, book_id)
        else:
            book = self._alive().filter(Book.id == book_id).first()
        if book is None:
            raise NoResultFound()
        return book

    def get_by_isbn(self, isbn: str) -> Book | None:
        return self._alive().filter(Book.isbn == isbn).first()

    def list(
        self,
        *,
        title_query: str | None = None,
        author_query: str | None = None,
        genre: Genre | None = None,
        publisher: str | None = None,
        available_only: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Book]:
        query = self._alive()
        if title_query:
            query = query.filter(Book.title.ilike(f"%{title_query}%"))
        if author_query:
            query = query.filter(Book.author.ilike(f"%{author_query}%"))
        if genre:
            query = query.filter(Book.genre == genre)
        if publisher:
            query = query.filter(Book.publisher.ilike(f"%{publisher}%"))
        if available_only:
            active_loan = (Loan.book_id == Book.id) & (Loan.returned_at.is_(None))
            query = (
                query.outerjoin(Loan, active_loan)
                .group_by(Book.id)
                .having(func.count(Loan.id) < Book.total_quantity)
            )
        return query.order_by(Book.id).offset(offset).limit(limit).all()

    def add(self, book: Book) -> Book:
        self._db.add(book)
        self._db.flush()
        self._db.refresh(book)
        return book

    def delete(self, book: Book) -> None:
        book.soft_delete()
        self._db.flush()

    def list_out_of_stock(
        self,
        *,
        publisher: str | None = None,
        genre: Genre | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Book]:
        query = self._alive()
        if publisher:
            query = query.filter(Book.publisher.ilike(f"%{publisher}%"))
        if genre:
            query = query.filter(Book.genre == genre)
        active_loan = (Loan.book_id == Book.id) & (Loan.returned_at.is_(None))
        return (
            query.outerjoin(Loan, active_loan)
            .group_by(Book.id)
            .having(func.count(Loan.id) >= Book.total_quantity)
            .order_by(Book.id)
            .offset(offset)
            .limit(limit)
            .all()
        )
