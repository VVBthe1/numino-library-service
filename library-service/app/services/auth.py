from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt

from app.config import Settings, get_settings


@dataclass(frozen=True)
class TokenClaims:
    subject: str
    expires_at: datetime


class AuthService:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def login(self, username: str, password: str) -> tuple[str, int]:
        username = username.strip()
        if not username or not password:
            raise ValueError("username and password are required")
        if (
            username != self._settings.auth_username
            or password != self._settings.auth_password
        ):
            raise ValueError("invalid username or password")

        expires_in = self._settings.jwt_expire_minutes * 60
        now = datetime.now(timezone.utc)
        payload = {
            "sub": username,
            "iat": now,
            "exp": now + timedelta(seconds=expires_in),
            "jti": str(uuid4()),
        }
        token = jwt.encode(
            payload,
            self._settings.jwt_secret,
            algorithm=self._settings.jwt_algorithm,
        )
        return token, expires_in

    def verify_token(self, token: str) -> TokenClaims:
        try:
            payload = jwt.decode(
                token,
                self._settings.jwt_secret,
                algorithms=[self._settings.jwt_algorithm],
            )
        except jwt.PyJWTError as exc:
            raise ValueError("invalid or expired token") from exc

        subject = payload.get("sub")
        exp = payload.get("exp")
        if not subject or exp is None:
            raise ValueError("invalid or expired token")

        return TokenClaims(
            subject=str(subject),
            expires_at=datetime.fromtimestamp(exp, tz=timezone.utc),
        )
