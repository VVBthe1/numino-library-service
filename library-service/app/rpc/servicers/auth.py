import grpc

from app.pb import auth_pb2, auth_pb2_grpc
from app.services.auth import AuthService


class AuthServicer(auth_pb2_grpc.AuthServiceServicer):
    def Login(self, request, context):
        try:
            token, expires_in = AuthService().login(request.username, request.password)
            return auth_pb2.LoginResponse(
                access_token=token,
                token_type="bearer",
                expires_in=expires_in,
            )
        except ValueError as exc:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details(str(exc))
            return auth_pb2.LoginResponse()
