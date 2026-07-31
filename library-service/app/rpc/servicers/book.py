import grpc
from google.protobuf import empty_pb2

from app.database import session_scope
from app.pb import book_pb2, book_pb2_grpc
from app.repositories.book import BookRepository
from app.repositories.loan import LoanRepository
from app.rpc.mappers.book import book_to_proto, genre_from_proto
from app.services.book import BookService


class BookServicer(book_pb2_grpc.BookServiceServicer):
    def CreateBook(self, request, context):
        try:
            with session_scope() as db:
                service = BookService(BookRepository(db), LoanRepository(db))
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
                    book=book_to_proto(book, available_quantity=book.total_quantity)
                )
        except ValueError as exc:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(exc))
            return book_pb2.CreateBookResponse()

    def GetBook(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("GetBook not implemented")
        return book_pb2.GetBookResponse()

    def ListBooks(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("ListBooks not implemented")
        return book_pb2.ListBooksResponse()

    def UpdateBook(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("UpdateBook not implemented")
        return book_pb2.UpdateBookResponse()

    def DeleteBook(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("DeleteBook not implemented")
        return empty_pb2.Empty()

    def GetOverdueBooks(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("GetOverdueBooks not implemented")
        return book_pb2.OverdueBooksResponse()

    def GetOutOfStockBooks(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("GetOutOfStockBooks not implemented")
        return book_pb2.OutOfStockBooksResponse()
