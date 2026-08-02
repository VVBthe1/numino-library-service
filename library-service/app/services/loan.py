from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone

from app.models.loan import Loan
from app.repositories.book import BookRepository
from app.repositories.loan import LoanRepository
from app.repositories.member import MemberRepository

DEFAULT_LOAN_DAYS = 7


class LoanService:
    def __init__(
        self,
        loans: LoanRepository,
        books: BookRepository,
        members: MemberRepository,
    ) -> None:
        self._loans = loans
        self._books = books
        self._members = members

    def borrow(
        self,
        book_id: int,
        member_id: int,
        due_date: str | None = None,
    ) -> Loan:
        if book_id <= 0:
            raise ValueError("book_id must be a positive integer")
        if member_id <= 0:
            raise ValueError("member_id must be a positive integer")

        book = self._books.get_by_id(book_id)
        member = self._members.get_by_id(member_id)

        today = date.today()
        if member.membership_end_date is not None and member.membership_end_date < today:
            raise ValueError("member membership has expired")

        active = self._loans.count_active_for_book(book.id)
        if active >= book.total_quantity:
            raise ValueError("book is out of stock")

        now = datetime.now(timezone.utc)
        if due_date:
            raw = due_date.strip()
            if not raw:
                raise ValueError("due_date is required")
            try:
                due_day = date.fromisoformat(raw)
            except ValueError as exc:
                raise ValueError("due_date must be YYYY-MM-DD") from exc
            if due_day < today:
                raise ValueError("due_date must be today or later")
            # start of due day so "today" can already be overdue
            due_at = datetime.combine(due_day, time(0, 0, 0), tzinfo=timezone.utc)
        else:
            due_at = now + timedelta(days=DEFAULT_LOAN_DAYS)

        loan = Loan(
            book_id=book.id,
            member_id=member.id,
            borrowed_at=now,
            due_at=due_at,
        )
        return self._loans.add(loan)

    def return_book(self, loan_id: int) -> Loan:
        if loan_id <= 0:
            raise ValueError("loan_id must be a positive integer")
        loan = self._loans.get_by_id(loan_id)
        if loan.returned_at is not None:
            raise ValueError("loan is already returned")
        loan.returned_at = datetime.now(timezone.utc)
        return loan

    def get(self, loan_id: int) -> Loan:
        if loan_id <= 0:
            raise ValueError("id must be a positive integer")
        return self._loans.get_by_id(loan_id)

    def list(
        self,
        *,
        book_id: int | None = None,
        member_id: int | None = None,
        active_only: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Loan]:
        if limit <= 0:
            raise ValueError("page_size must be a positive integer")
        if book_id is not None and book_id <= 0:
            raise ValueError("book_id must be a positive integer")
        if member_id is not None and member_id <= 0:
            raise ValueError("member_id must be a positive integer")
        return self._loans.list(
            book_id=book_id,
            member_id=member_id,
            active_only=active_only,
            limit=limit,
            offset=offset,
        )
