from concurrent import futures

import grpc

from app.config import get_settings
from app.rpc.servicers.book import BookServicer
from app.rpc.servicers.loan import LoanServicer
from app.rpc.servicers.member import MemberServicer
from app.pb import book_pb2_grpc, loan_pb2_grpc, member_pb2_grpc


def create_server() -> grpc.Server:
    settings = get_settings()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    book_pb2_grpc.add_BookServiceServicer_to_server(BookServicer(), server)
    member_pb2_grpc.add_MemberServiceServicer_to_server(MemberServicer(), server)
    loan_pb2_grpc.add_LoanServiceServicer_to_server(LoanServicer(), server)

    listen_addr = f"{settings.grpc_host}:{settings.grpc_port}"
    server.add_insecure_port(listen_addr)
    return server


def serve() -> None:
    settings = get_settings()
    server = create_server()
    server.start()
    print(f"gRPC listening on {settings.grpc_host}:{settings.grpc_port}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
