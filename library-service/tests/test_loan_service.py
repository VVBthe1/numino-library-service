from datetime import date, datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.models.book import Book, Genre
from app.models.loan import Loan
from app.models.member import Member
from app.services.loan import LoanService


@pytest.fixture
def loans():
    return MagicMock()


@pytest.fixture
def books():
    return MagicMock()


@pytest.fixture
def members():
    return MagicMock()


@pytest.fixture
def service(loans, books, members):
    return LoanService(loans, books, members)


def _book(**kwargs) -> Book:
    book = Book(
        title="Dune",
        author="Frank Herbert",
        isbn="9780441172719",
        genre=Genre.SCIENCE_FICTION,
        total_quantity=kwargs.get("total_quantity", 3),
    )
    book.id = kwargs.get("id", 1)
    return book


def _member(**kwargs) -> Member:
    member = Member(
        name="Ada Lovelace",
        email="ada@example.com",
        membership_start_date=date(2024, 1, 1),
        membership_end_date=kwargs.get("membership_end_date"),
    )
    member.id = kwargs.get("id", 1)
    return member


def _loan(**kwargs) -> Loan:
    now = datetime.now(timezone.utc)
    loan = Loan(
        book_id=kwargs.get("book_id", 1),
        member_id=kwargs.get("member_id", 1),
        borrowed_at=now,
        due_at=now,
        returned_at=kwargs.get("returned_at"),
    )
    loan.id = kwargs.get("id", 1)
    return loan


class TestBorrowFailures:
    @pytest.mark.parametrize(
        "book_id,member_id,match",
        [
            (0, 1, "book_id must be a positive integer"),
            (1, -1, "member_id must be a positive integer"),
        ],
    )
    def test_invalid_ids(self, service, loans, book_id, member_id, match):
        with pytest.raises(ValueError, match=match):
            service.borrow(book_id, member_id)
        loans.add.assert_not_called()

    def test_expired_membership(self, service, books, members, loans):
        books.get_by_id.return_value = _book()
        members.get_by_id.return_value = _member(
            membership_end_date=date(2020, 1, 1)
        )
        with pytest.raises(ValueError, match="membership has expired"):
            service.borrow(1, 1)
        loans.add.assert_not_called()

    def test_out_of_stock(self, service, books, members, loans):
        books.get_by_id.return_value = _book(total_quantity=2)
        members.get_by_id.return_value = _member()
        loans.count_active_for_book.return_value = 2
        with pytest.raises(ValueError, match="out of stock"):
            service.borrow(1, 1)
        loans.add.assert_not_called()

    def test_due_date_in_past(self, service, books, members, loans):
        books.get_by_id.return_value = _book()
        members.get_by_id.return_value = _member()
        loans.count_active_for_book.return_value = 0
        with pytest.raises(ValueError, match="today or later"):
            service.borrow(1, 1, due_date="2000-01-01")
        loans.add.assert_not_called()

    def test_due_date_bad_format(self, service, books, members, loans):
        books.get_by_id.return_value = _book()
        members.get_by_id.return_value = _member()
        loans.count_active_for_book.return_value = 0
        with pytest.raises(ValueError, match="YYYY-MM-DD"):
            service.borrow(1, 1, due_date="02-08-2026")
        loans.add.assert_not_called()


class TestReturnFailures:
    def test_non_positive_id(self, service, loans):
        with pytest.raises(ValueError, match="loan_id must be a positive integer"):
            service.return_book(0)
        loans.get_by_id.assert_not_called()

    def test_already_returned(self, service, loans):
        loans.get_by_id.return_value = _loan(
            returned_at=datetime.now(timezone.utc)
        )
        with pytest.raises(ValueError, match="already returned"):
            service.return_book(1)


class TestGetFailures:
    def test_non_positive_id(self, service, loans):
        with pytest.raises(ValueError, match="positive integer"):
            service.get(0)
        loans.get_by_id.assert_not_called()


class TestListFailures:
    @pytest.mark.parametrize(
        "overrides,match",
        [
            ({"limit": 0}, "page_size"),
            ({"book_id": -1}, "book_id must be a positive integer"),
            ({"member_id": 0}, "member_id must be a positive integer"),
        ],
    )
    def test_validation(self, service, loans, overrides, match):
        with pytest.raises(ValueError, match=match):
            service.list(**overrides)
        loans.list.assert_not_called()


def test_list_methods_forward_filters(service, loans):
    loans.list.return_value = []

    service.list(
        book_id=1,
        member_id=2,
        active_only=True,
        limit=10,
        offset=5,
    )

    loans.list.assert_called_once_with(
        book_id=1,
        member_id=2,
        active_only=True,
        limit=10,
        offset=5,
    )
