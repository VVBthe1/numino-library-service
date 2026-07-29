from sqlalchemy.orm import Session

from app.models.loan import Loan


class LoanRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, loan_id: int) -> Loan | None:
        raise NotImplementedError

    def list(
        self,
        *,
        book_id: int | None = None,
        member_id: int | None = None,
        active_only: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Loan]:
        raise NotImplementedError

    def count_active_for_book(self, book_id: int) -> int:
        raise NotImplementedError

    def add(self, loan: Loan) -> Loan:
        raise NotImplementedError
