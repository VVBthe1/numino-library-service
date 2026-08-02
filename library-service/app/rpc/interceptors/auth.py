from __future__ import annotations

import grpc

from app.services.auth import AuthService

_LOGIN_METHOD = "/neighborhood.library.v1.AuthService/Login"
_AUTH_HEADER = "authorization"


def _extract_bearer_token(metadata: tuple) -> str | None:
    for key, value in metadata:
        if key.lower() != _AUTH_HEADER:
            continue
        parts = value.split(" ", 1)
        if len(parts) == 2 and parts[0].lower() == "bearer" and parts[1].strip():
            return parts[1].strip()
    return None


class AuthInterceptor(grpc.ServerInterceptor):
    def __init__(self, auth: AuthService | None = None) -> None:
        self._auth = auth or AuthService()

    def intercept_service(self, continuation, handler_call_details):
        method = handler_call_details.method
        if method == _LOGIN_METHOD:
            return continuation(handler_call_details)

        handler = continuation(handler_call_details)
        if handler is None:
            return None

        token = _extract_bearer_token(handler_call_details.invocation_metadata or ())
        if not token:
            return self._unauthenticated_handler(handler, "missing authorization token")

        try:
            self._auth.verify_token(token)
        except ValueError as exc:
            return self._unauthenticated_handler(handler, str(exc))

        return handler

    def _unauthenticated_handler(self, handler, details: str):
        def abort(request, context):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, details)

        if handler.unary_unary:
            return grpc.unary_unary_rpc_method_handler(
                abort,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        if handler.unary_stream:
            return grpc.unary_stream_rpc_method_handler(
                abort,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        if handler.stream_unary:
            return grpc.stream_unary_rpc_method_handler(
                abort,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        if handler.stream_stream:
            return grpc.stream_stream_rpc_method_handler(
                abort,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        return handler
