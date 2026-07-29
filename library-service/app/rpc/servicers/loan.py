import grpc

from app.pb import loan_pb2, loan_pb2_grpc


class LoanServicer(loan_pb2_grpc.LoanServiceServicer):
    def BorrowBook(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("BorrowBook not implemented")
        return loan_pb2.BorrowBookResponse()

    def ReturnBook(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("ReturnBook not implemented")
        return loan_pb2.ReturnBookResponse()

    def GetLoan(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("GetLoan not implemented")
        return loan_pb2.GetLoanResponse()

    def ListLoans(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("ListLoans not implemented")
        return loan_pb2.ListLoansResponse()
