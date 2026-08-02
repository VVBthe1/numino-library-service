from unittest.mock import MagicMock

import pytest

from app.models.book import Book, Genre
from app.services.book import BookService


@pytest.fixture
def books():
    return MagicMock()


@pytest.fixture
def loans():
    return MagicMock()


@pytest.fixture
def service(books, loans):
    return BookService(books, loans)


def _book(**kwargs) -> Book:
    book = Book(
        title=kwargs.get("title", "Dune"),
        author=kwargs.get("author", "Frank Herbert"),
        isbn=kwargs.get("isbn", "9780441172719"),
        genre=kwargs.get("genre", Genre.SCIENCE_FICTION),
        total_quantity=kwargs.get("total_quantity", 3),
    )
    book.id = kwargs.get("id", 1)
    return book


class TestCreateFailures:
    @pytest.mark.parametrize(
        "overrides,match",
        [
            ({"title": "  "}, "title is required"),
            ({"author": ""}, "author is required"),
            ({"isbn": "  "}, "isbn is required"),
            ({"isbn": "123"}, "isbn must be 10 or 13"),
            ({"isbn": "978044117271"}, "isbn must be 10 or 13"),
            ({"total_quantity": -1}, "total_quantity must be >= 0"),
        ],
    )
    def test_validation(self, service, books, overrides, match):
        books.get_by_isbn.return_value = None
        args = {
            "title": "Title",
            "author": "Author",
            "isbn": "9780441172719",
            "genre": Genre.FICTION,
            "total_quantity": 1,
            **overrides,
        }
        with pytest.raises(ValueError, match=match):
            service.create(**args)
        books.add.assert_not_called()

    def test_duplicate_isbn(self, service, books):
        books.get_by_isbn.return_value = _book()
        with pytest.raises(ValueError, match="isbn already exists"):
            service.create(
                title="Title",
                author="Author",
                isbn="9780441172719",
                genre=Genre.FICTION,
                total_quantity=1,
            )
        books.add.assert_not_called()


class TestGetFailures:
    def test_non_positive_id(self, service, books):
        with pytest.raises(ValueError, match="positive integer"):
            service.get(0)
        books.get_by_id.assert_not_called()


class TestUpdateFailures:
    def test_non_positive_id(self, service, books):
        with pytest.raises(ValueError, match="positive integer"):
            service.update(
                0,
                title="T",
                author="A",
                isbn="9780441172719",
                genre=Genre.FICTION,
                total_quantity=1,
            )

    def test_duplicate_isbn(self, service, books, loans):
        book = _book(id=1, isbn="9780441172719")
        books.get_by_id.return_value = book
        books.get_by_isbn.return_value = _book(id=2, isbn="9780141439510")
        with pytest.raises(ValueError, match="isbn already exists"):
            service.update(
                1,
                title="T",
                author="A",
                isbn="9780141439510",
                genre=Genre.FICTION,
                total_quantity=1,
            )

    def test_quantity_below_active_loans(self, service, books, loans):
        book = _book()
        books.get_by_id.return_value = book
        books.get_by_isbn.return_value = book
        loans.count_active_for_book.return_value = 2
        with pytest.raises(ValueError, match="active loans"):
            service.update(
                1,
                title="Dune",
                author="Frank Herbert",
                isbn="9780441172719",
                genre=Genre.SCIENCE_FICTION,
                total_quantity=1,
            )


class TestDeleteFailures:
    def test_non_positive_id(self, service, books):
        with pytest.raises(ValueError, match="positive integer"):
            service.delete(-1)
        books.get_by_id.assert_not_called()

    def test_active_loans(self, service, books, loans):
        book = _book()
        books.get_by_id.return_value = book
        loans.count_active_for_book.return_value = 1
        with pytest.raises(ValueError, match="active loans"):
            service.delete(1)
        books.delete.assert_not_called()

    def test_soft_deletes_when_no_active_loans(self, service, books, loans):
        book = _book()
        books.get_by_id.return_value = book
        loans.count_active_for_book.return_value = 0
        service.delete(1)
        books.delete.assert_called_once_with(book)

def test_list_methods_forward_filters(service, books, loans):
    books.list.return_value = []
    loans.list_overdue.return_value = []
    books.list_out_of_stock.return_value = []

    service.list(
        title_query="  dune  ",
        author_query="  herbert  ",
        genre=Genre.SCIENCE_FICTION,
        publisher="  Chilton  ",
        available_only=True,
        limit=10,
        offset=5,
    )
    service.list_overdue(
        publisher="  Chilton  ",
        genre=Genre.SCIENCE_FICTION,
        limit=20,
        offset=2,
    )
    service.list_out_of_stock(
        publisher="  Chilton  ",
        genre=Genre.SCIENCE_FICTION,
        limit=15,
        offset=3,
    )

    books.list.assert_called_once_with(
        title_query="dune",
        author_query="herbert",
        genre=Genre.SCIENCE_FICTION,
        publisher="Chilton",
        available_only=True,
        limit=10,
        offset=5,
    )
    loans.list_overdue.assert_called_once_with(
        publisher="Chilton",
        genre=Genre.SCIENCE_FICTION,
        limit=20,
        offset=2,
    )
    books.list_out_of_stock.assert_called_once_with(
        publisher="Chilton",
        genre=Genre.SCIENCE_FICTION,
        limit=15,
        offset=3,
    )
