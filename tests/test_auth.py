import pytest

from src.auth import Authenticator
from src.config import Settings
from src.exceptions import AuthenticationError


class DummyResponse:
    def __init__(self, ok=True, status_code=200, payload=None, text=""):
        self.ok = ok
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self):
        return self._payload


class DummySession:
    def __init__(self, response):
        if isinstance(response, list):
            self.responses = list(response)
        else:
            self.responses = [response]
        self.calls = []

    def post(self, url, json, timeout, proxies):
        self.calls.append(
            {"url": url, "json": json, "timeout": timeout, "proxies": proxies}
        )
        current = self.responses.pop(0)
        if isinstance(current, Exception):
            raise current
        return current


def make_settings() -> Settings:
    return Settings(
        api_auth_url="https://api.example.com/auth/token",
        api_username="demo",
        api_password="secret",
        api_client_id="client-id",
        api_client_secret="client-secret",
        proxy_url="http://proxy.local:8080",
        request_timeout=15,
    )


def test_authenticate_returns_token_bundle():
    session = DummySession(
        DummyResponse(
            payload={
                "access_token": "access-123",
                "refresh_token": "refresh-123",
                "token_type": "Bearer",
            }
        )
    )
    authenticator = Authenticator(settings=make_settings(), session=session)

    tokens = authenticator.authenticate()

    assert tokens.access_token == "access-123"
    assert tokens.refresh_token == "refresh-123"
    assert session.calls[0]["json"]["username"] == "demo"


def test_refresh_uses_refresh_grant_payload():
    session = DummySession(DummyResponse(payload={"access_token": "new-access"}))
    authenticator = Authenticator(settings=make_settings(), session=session)

    authenticator.refresh("refresh-123")

    assert session.calls[0]["json"]["grant_type"] == "refresh_token"
    assert session.calls[0]["json"]["refresh_token"] == "refresh-123"


def test_authenticate_raises_when_access_token_missing():
    session = DummySession(DummyResponse(payload={"refresh_token": "refresh-123"}))
    authenticator = Authenticator(settings=make_settings(), session=session)

    with pytest.raises(AuthenticationError, match="access_token"):
        authenticator.authenticate()


def test_authenticate_raises_when_auth_url_missing():
    settings = Settings()
    authenticator = Authenticator(settings=settings, session=DummySession(DummyResponse()))

    with pytest.raises(AuthenticationError, match="API_AUTH_URL"):
        authenticator.authenticate()


def test_authenticate_retries_on_retryable_server_error():
    session = DummySession(
        [
            DummyResponse(ok=False, status_code=502, text="bad gateway"),
            DummyResponse(payload={"access_token": "access-123"}),
        ]
    )
    authenticator = Authenticator(settings=make_settings(), session=session)
    authenticator.sleep_func = lambda _: None

    tokens = authenticator.authenticate()

    assert tokens.access_token == "access-123"
    assert len(session.calls) == 2
