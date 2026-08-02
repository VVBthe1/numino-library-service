import grpc
from sqlalchemy.exc import NoResultFound

from app.database import session_scope
from app.pb import loan_pb2, loan_pb2_grpc
from app.repositories.book import BookRepository
from app.repositories.loan import LoanRepository
from app.repositories.member import MemberRepository
from app.rpc.mappers.book import (
    book_minimal_to_proto,
    loan_to_proto,
    member_minimal_to_proto,
)
from app.services.loan import LoanService


def _loan_service(db) -> LoanService:
    return LoanService(
        LoanRepository(db),
        BookRepository(db),
        MemberRepository(db),
    )


class LoanServicer(loan_pb2_grpc.LoanServiceServicer):
    def BorrowBook(self, request, context):
        try:
            with session_scope() as db:
                service = _loan_service(db)
                loan = service.borrow(
                    request.book_id,
                    request.member_id,
                    due_date=request.due_date if request.HasField("due_date") else None,
                )
                return loan_pb2.BorrowBookResponse(loan=loan_to_proto(loan))
        except ValueError as exc:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(exc))
            return loan_pb2.BorrowBookResponse()
        except NoResultFound:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("book or member not found")
            return loan_pb2.BorrowBookResponse()

    def ReturnBook(self, request, context):
        try:
            with session_scope() as db:
                service = _loan_service(db)
                loan = service.return_book(request.loan_id)
                return loan_pb2.ReturnBookResponse(loan=loan_to_proto(loan))
        except ValueError as exc:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(exc))
            return loan_pb2.ReturnBookResponse()
        except NoResultFound:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"loan {request.loan_id} not found")
            return loan_pb2.ReturnBookResponse()

    def GetLoan(self, request, context):
        try:
            with session_scope() as db:
                service = _loan_service(db)
                loan = service.get(request.id)
                return loan_pb2.GetLoanResponse(
                    loan=loan_to_proto(loan),
                    book=book_minimal_to_proto(loan.book),
                    member=member_minimal_to_proto(loan.member),
                )
        except ValueError as exc:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(exc))
            return loan_pb2.GetLoanResponse()
        except NoResultFound:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"loan {request.id} not found")
            return loan_pb2.GetLoanResponse()

    def ListLoans(self, request, context):
        try:
            with session_scope() as db:
                service = _loan_service(db)
                loans = service.list(
                    book_id=request.book_id if request.HasField("book_id") else None,
                    member_id=request.member_id
                    if request.HasField("member_id")
                    else None,
                    active_only=request.active_only
                    if request.HasField("active_only")
                    else None,
                    limit=request.page_size or 50,
                )
                return loan_pb2.ListLoansResponse(
                    loans=[
                        loan_pb2.LoanWithBookAndMember(
                            loan=loan_to_proto(loan),
                            book=book_minimal_to_proto(loan.book),
                            member=member_minimal_to_proto(loan.member),
                        )
                        for loan in loans
                    ],
                )
        except ValueError as exc:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(exc))
            return loan_pb2.ListLoansResponse()
