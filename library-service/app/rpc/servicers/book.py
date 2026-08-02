import grpc
from google.protobuf import empty_pb2
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import NoResultFound

from app.database import session_scope
from app.pb import book_pb2, book_pb2_grpc
from app.repositories.book import BookRepository
from app.repositories.loan import LoanRepository
from app.rpc.mappers.book import (
    book_minimal_to_proto,
    book_to_proto,
    genre_from_proto,
    loan_to_proto,
    member_minimal_to_proto,
)
from app.services.book import BookService


def _book_service(db) -> BookService:
    return BookService(BookRepository(db), LoanRepository(db))


class BookServicer(book_pb2_grpc.BookServiceServicer):
    def CreateBook(self, request, context):
        try:
            with session_scope() as db:
                service = _book_service(db)
                book = service.create(
                    title=request.title,
                    author=request.author,
                    isbn=request.isbn,
                    genre=genre_from_proto(request.genre),
                    total_quantity=request.total_quantity,
                    publication_year=request.publication_year
                    if request.HasField("publication_year")
                    else None,
                    publisher=request.publisher if request.HasField("publisher") else None,
                    description=request.description
                    if request.HasField("description")
                    else None,
                )
                return book_pb2.CreateBookResponse(
                    book=book_to_proto(
                        book, available_quantity=service.available_quantity(book)
                    )
                )
        except ValueError as exc:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(exc))
            return book_pb2.CreateBookResponse()

    def GetBook(self, request, context):
        try:
            with session_scope() as db:
                service = _book_service(db)
                book = service.get(request.id)
                return book_pb2.GetBookResponse(
                    book=book_to_proto(
                        book, available_quantity=service.available_quantity(book)
                    )
                )
        except ValueError as exc:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(exc))
            return book_pb2.GetBookResponse()
        except NoResultFound:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"book {request.id} not found")
            return book_pb2.GetBookResponse()

    def ListBooks(self, request, context):
        try:
            with session_scope() as db:
                service = _book_service(db)
                genre = (
                    genre_from_proto(request.genre)
                    if request.HasField("genre")
                    else None
                )
                available_only = (
                    request.available_only
                    if request.HasField("available_only")
                    else None
                )
                books = service.list(
                    title_query=request.title_query
                    if request.HasField("title_query")
                    else None,
                    author_query=request.author_query
                    if request.HasField("author_query")
                    else None,
                    genre=genre,
                    publisher=request.publisher
                    if request.HasField("publisher")
                    else None,
                    available_only=available_only,
                    limit=request.page_size or 50,
                )
                return book_pb2.ListBooksResponse(
                    books=[
                        book_to_proto(
                            book, available_quantity=service.available_quantity(book)
                        )
                        for book in books
                    ],
                )
        except ValueError as exc:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(exc))
            return book_pb2.ListBooksResponse()

    def UpdateBook(self, request, context):
        try:
            with session_scope() as db:
                service = _book_service(db)
                book = service.update(
                    request.id,
                    title=request.title,
                    author=request.author,
                    isbn=request.isbn,
                    genre=genre_from_proto(request.genre),
                    total_quantity=request.total_quantity,
                    publication_year=request.publication_year
                    if request.HasField("publication_year")
                    else None,
                    publisher=request.publisher if request.HasField("publisher") else None,
                    description=request.description
                    if request.HasField("description")
                    else None,
                )
                return book_pb2.UpdateBookResponse(
                    book=book_to_proto(
                        book, available_quantity=service.available_quantity(book)
                    )
                )
        except ValueError as exc:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(exc))
            return book_pb2.UpdateBookResponse()
        except NoResultFound:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"book {request.id} not found")
            return book_pb2.UpdateBookResponse()

    def DeleteBook(self, request, context):
        try:
            with session_scope() as db:
                service = _book_service(db)
                service.delete(request.id)
                return empty_pb2.Empty()
        except ValueError as exc:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(exc))
            return empty_pb2.Empty()
        except NoResultFound:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"book {request.id} not found")
            return empty_pb2.Empty()
        except IntegrityError:
            context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            context.set_details("cannot delete book referenced by loans")
            return empty_pb2.Empty()

    def GetOverdueBooks(self, request, context):
        try:
            with session_scope() as db:
                service = _book_service(db)
                genre = (
                    genre_from_proto(request.genre)
                    if request.HasField("genre")
                    else None
                )
                loans = service.list_overdue(
                    publisher=request.publisher
                    if request.HasField("publisher")
                    else None,
                    genre=genre,
                    limit=request.page_size or 50,
                )
                return book_pb2.OverdueBooksResponse(
                    books=[
                        book_pb2.OverdueBook(
                            book=book_minimal_to_proto(loan.book),
                            loan=loan_to_proto(loan),
                            member=member_minimal_to_proto(loan.member),
                        )
                        for loan in loans
                    ],
                )
        except ValueError as exc:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(exc))
            return book_pb2.OverdueBooksResponse()

    def GetOutOfStockBooks(self, request, context):
        try:
            with session_scope() as db:
                service = _book_service(db)
                genre = (
                    genre_from_proto(request.genre)
                    if request.HasField("genre")
                    else None
                )
                books = service.list_out_of_stock(
                    publisher=request.publisher
                    if request.HasField("publisher")
                    else None,
                    genre=genre,
                    limit=request.page_size or 50,
                )
                return book_pb2.OutOfStockBooksResponse(
                    books=[
                        book_to_proto(book, available_quantity=0) for book in books
                    ],
                )
        except ValueError as exc:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(exc))
            return book_pb2.OutOfStockBooksResponse()
