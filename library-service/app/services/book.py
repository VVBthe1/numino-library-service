from __future__ import annotations

import re

from app.models.book import Book, Genre
from app.models.loan import Loan
from app.repositories.book import BookRepository
from app.repositories.loan import LoanRepository

_ISBN_RE = re.compile(r"^[0-9]{9}[0-9Xx]$|^[0-9]{13}$")


def normalize_isbn(isbn: str) -> str:
    """Strip separators; keep digits and a trailing ISBN-10 check digit X."""
    cleaned = re.sub(r"[\s-]", "", isbn.strip())
    return cleaned.upper()


def validate_isbn(isbn: str) -> str:
    """Require ISBN-10 or ISBN-13 after normalization."""
    normalized = normalize_isbn(isbn)
    if not normalized:
        raise ValueError("isbn is required")
    if not _ISBN_RE.fullmatch(normalized):
        raise ValueError("isbn must be 10 or 13 characters (ISBN-10 or ISBN-13)")
    return normalized


class BookService:
    def __init__(self, books: BookRepository, loans: LoanRepository) -> None:
        self._books = books
        self._loans = loans

    def available_quantity(self, book: Book) -> int:
        active = self._loans.count_active_for_book(book.id)
        return max(book.total_quantity - active, 0)

    def create(
        self,
        *,
        title: str,
        author: str,
        isbn: str,
        genre: Genre,
        total_quantity: int,
        publication_year: int | None = None,
        publisher: str | None = None,
        description: str | None = None,
    ) -> Book:
        title = title.strip()
        author = author.strip()
        isbn = validate_isbn(isbn)

        if not title:
            raise ValueError("title is required")
        if not author:
            raise ValueError("author is required")
        if total_quantity < 0:
            raise ValueError("total_quantity must be >= 0")
        if self._books.get_by_isbn(isbn) is not None:
            raise ValueError("isbn already exists")

        book = Book(
            title=title,
            author=author,
            isbn=isbn,
            genre=genre,
            total_quantity=total_quantity,
            publication_year=publication_year,
            publisher=publisher,
            description=description,
        )
        return self._books.add(book)

    def get(self, book_id: int) -> Book:
        if book_id <= 0:
            raise ValueError("id must be a positive integer")
        return self._books.get_by_id(book_id)

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
        if limit <= 0:
            raise ValueError("page_size must be a positive integer")
        if offset < 0:
            raise ValueError("offset must be >= 0")
        return self._books.list(
            title_query=title_query.strip() if title_query else None,
            author_query=author_query.strip() if author_query else None,
            genre=genre,
            publisher=publisher.strip() if publisher else None,
            available_only=available_only,
            limit=limit,
            offset=offset,
        )

    def update(
        self,
        book_id: int,
        *,
        title: str,
        author: str,
        isbn: str,
        genre: Genre,
        total_quantity: int,
        publication_year: int | None = None,
        publisher: str | None = None,
        description: str | None = None,
    ) -> Book:
        if book_id <= 0:
            raise ValueError("id must be a positive integer")

        title = title.strip()
        author = author.strip()
        isbn = validate_isbn(isbn)

        if not title:
            raise ValueError("title is required")
        if not author:
            raise ValueError("author is required")
        if total_quantity < 0:
            raise ValueError("total_quantity must be >= 0")

        book = self._books.get_by_id(book_id)
        existing = self._books.get_by_isbn(isbn)
        if existing is not None and existing.id != book.id:
            raise ValueError("isbn already exists")

        active = self._loans.count_active_for_book(book.id)
        if total_quantity < active:
            raise ValueError(
                f"total_quantity cannot be less than active loans ({active})"
            )

        book.title = title
        book.author = author
        book.isbn = isbn
        book.genre = genre
        book.total_quantity = total_quantity
        book.publication_year = publication_year
        book.publisher = publisher
        book.description = description
        return book

    def delete(self, book_id: int) -> None:
        if book_id <= 0:
            raise ValueError("id must be a positive integer")
        book = self._books.get_by_id(book_id)
        active = self._loans.count_active_for_book(book.id)
        if active > 0:
            raise ValueError("cannot delete book with active loans")
        self._books.delete(book)

    def list_overdue(
        self,
        *,
        publisher: str | None = None,
        genre: Genre | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Loan]:
        if limit <= 0:
            raise ValueError("page_size must be a positive integer")
        return self._loans.list_overdue(
            publisher=publisher.strip() if publisher else None,
            genre=genre,
            limit=limit,
            offset=offset,
        )

    def list_out_of_stock(
        self,
        *,
        publisher: str | None = None,
        genre: Genre | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Book]:
        if limit <= 0:
            raise ValueError("page_size must be a positive integer")
        return self._books.list_out_of_stock(
            publisher=publisher.strip() if publisher else None,
            genre=genre,
            limit=limit,
            offset=offset,
        )
