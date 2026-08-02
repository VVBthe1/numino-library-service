from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session, contains_eager, joinedload

from app.models.book import Book, Genre
from app.models.loan import Loan


class LoanRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, loan_id: int) -> Loan:
        return (
            self._db.query(Loan)
            .options(joinedload(Loan.book), joinedload(Loan.member))
            .filter(Loan.id == loan_id)
            .one()
        )

    def list(
        self,
        *,
        book_id: int | None = None,
        member_id: int | None = None,
        active_only: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Loan]:
        query = self._db.query(Loan).options(
            joinedload(Loan.book), joinedload(Loan.member)
        )
        if book_id is not None:
            query = query.filter(Loan.book_id == book_id)
        if member_id is not None:
            query = query.filter(Loan.member_id == member_id)
        if active_only:
            query = query.filter(Loan.returned_at.is_(None))
        return query.order_by(Loan.id.desc()).offset(offset).limit(limit).all()

    def count_active_for_book(self, book_id: int) -> int:
        return (
            self._db.query(Loan)
            .filter(Loan.book_id == book_id, Loan.returned_at.is_(None))
            .count()
        )

    def count_active_for_member(self, member_id: int) -> int:
        return (
            self._db.query(Loan)
            .filter(Loan.member_id == member_id, Loan.returned_at.is_(None))
            .count()
        )

    def list_overdue(
        self,
        *,
        publisher: str | None = None,
        genre: Genre | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Loan]:
        now = datetime.now(timezone.utc)
        query = (
            self._db.query(Loan)
            .join(Loan.book)
            .options(contains_eager(Loan.book), joinedload(Loan.member))
            .filter(
                Loan.returned_at.is_(None),
                Loan.due_at < now,
                Book.deleted_at.is_(None),
            )
        )
        if publisher:
            query = query.filter(Book.publisher.ilike(f"%{publisher}%"))
        if genre:
            query = query.filter(Book.genre == genre)
        return query.order_by(Loan.due_at).offset(offset).limit(limit).all()

    def add(self, loan: Loan) -> Loan:
        self._db.add(loan)
        self._db.flush()
        self._db.refresh(loan)
        return loan
