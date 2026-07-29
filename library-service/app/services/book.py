from app.models.book import Book
from app.repositories.book import BookRepository
from app.repositories.loan import LoanRepository


class BookService:
    def __init__(self, books: BookRepository, loans: LoanRepository) -> None:
        self._books = books
        self._loans = loans

    def create(self, **fields) -> Book:
        return self._books.add(Book(**fields))

    def get(self, book_id: int) -> Book:
        return self._books.get_by_id(book_id)

    def list(self, **filters) -> list[Book]:
        return self._books.list(**filters)

    def update(self, book_id: int, **fields) -> Book:
        return self._books.update(book_id, **fields)

    def delete(self, book_id: int) -> None:
        return self._books.delete(book_id)

    def list_overdue(self, **filters) -> list[tuple]:
        return self._books.list_overdue(**filters)

    def list_out_of_stock(self, **filters) -> list[Book]:
        return self._books.list_out_of_stock(**filters)
