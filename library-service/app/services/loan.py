from app.models.loan import Loan
from app.repositories.book import BookRepository
from app.repositories.loan import LoanRepository
from app.repositories.member import MemberRepository


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

    def borrow(self, book_id: int, member_id: int) -> Loan:
        raise NotImplementedError

    def return_book(self, loan_id: int) -> Loan:
        raise NotImplementedError

    def get(self, loan_id: int) -> Loan:
        raise NotImplementedError

    def list(self, **filters) -> list[Loan]:
        raise NotImplementedError
