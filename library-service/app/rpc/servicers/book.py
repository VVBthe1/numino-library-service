import grpc
from google.protobuf import empty_pb2

from app.pb import book_pb2, book_pb2_grpc


class BookServicer(book_pb2_grpc.BookServiceServicer):
    def CreateBook(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("CreateBook not implemented")
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
