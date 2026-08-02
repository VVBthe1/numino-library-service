from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.config import Settings
from app.services.auth import AuthService


@pytest.fixture
def settings() -> Settings:
    return Settings(
        jwt_secret="test-secret-key-at-least-32-bytes!",
        jwt_expire_minutes=60,
        auth_username="admin",
        auth_password="admin",
    )


@pytest.fixture
def auth(settings: Settings) -> AuthService:
    return AuthService(settings)


class TestLoginFailures:
    @pytest.mark.parametrize(
        "username,password,match",
        [
            ("", "admin", "username and password are required"),
            ("admin", "", "username and password are required"),
            ("admin", "wrong", "invalid username or password"),
            ("nope", "admin", "invalid username or password"),
        ],
    )
    def test_rejects_bad_credentials(self, auth, username, password, match):
        with pytest.raises(ValueError, match=match):
            auth.login(username, password)


def test_login_returns_verifiable_token(auth, settings):
    token, expires_in = auth.login("admin", "admin")

    assert expires_in == 3600
    assert token
    claims = auth.verify_token(token)
    assert claims.subject == "admin"


def test_verify_rejects_bad_token(auth):
    with pytest.raises(ValueError, match="invalid or expired token"):
        auth.verify_token("not-a-jwt")


def test_verify_rejects_expired_token(auth, settings):
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {
            "sub": "admin",
            "iat": now - timedelta(hours=2),
            "exp": now - timedelta(hours=1),
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    with pytest.raises(ValueError, match="invalid or expired token"):
        auth.verify_token(token)
