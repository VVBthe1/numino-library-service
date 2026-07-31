from app.models.book import Book, Genre
from app.repositories.book import BookRepository
from app.repositories.loan import LoanRepository


class BookService:
    def __init__(self, books: BookRepository, loans: LoanRepository) -> None:
        self._books = books
        self._loans = loans

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
        isbn = isbn.strip()

        if not title:
            raise ValueError("title is required")
        if not author:
            raise ValueError("author is required")
        if not isbn:
            raise ValueError("isbn is required")
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
        return self._books.get_by_id(book_id)

    def list(self, **filters) -> list[Book]:
        return self._books.list(**filters)

    def update(self, book_id: int, **fields) -> Book:
        return self._books.update(book_id, **fields)

    def delete(self, book_id: int) -> None:
        return self._books.delete(book_id)

    def list_overdue(self, **filters) -> list[Book]:
        return self._books.list_overdue(**filters)

    def list_out_of_stock(self, **filters) -> list[Book]:
        return self._books.list_out_of_stock(**filters)
