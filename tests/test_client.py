import pytest

from src.auth import TokenBundle
from src.client import SecureAPIClient
from src.config import Settings
from src.exceptions import RequestExecutionError


class DummyResponse:
    def __init__(self, ok=True, status_code=200, payload=None, text=""):
        self.ok = ok
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self):
        return self._payload


class SequencedSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, url, headers, params, timeout, proxies):
        self.calls.append(
            {
                "url": url,
                "headers": headers,
                "params": params,
                "timeout": timeout,
                "proxies": proxies,
            }
        )
        return self.responses.pop(0)


def make_settings() -> Settings:
    return Settings(
        api_base_url="https://api.example.com",
        api_data_path="/v1/data",
        request_timeout=10,
    )


def test_get_returns_json_payload():
    session = SequencedSession([DummyResponse(payload={"result": "ok"})])
    client = SecureAPIClient(settings=make_settings(), session=session)
    client.tokens = TokenBundle(access_token="access-123")

    result = client.get(params={"page": 1})

    assert result == {"result": "ok"}
    assert session.calls[0]["headers"]["Authorization"] == "Bearer access-123"


def test_get_refreshes_token_after_401():
    session = SequencedSession(
        [
            DummyResponse(ok=False, status_code=401, text="expired"),
            DummyResponse(payload={"result": "ok"}),
        ]
    )
    client = SecureAPIClient(settings=make_settings(), session=session)
    client.tokens = TokenBundle(access_token="expired-token", refresh_token="refresh-123")
    refresh_called = {"value": False}

    def fake_refresh(refresh_token: str) -> TokenBundle:
        refresh_called["value"] = True
        assert refresh_token == "refresh-123"
        return TokenBundle(access_token="new-token", refresh_token="refresh-123")

    client.authenticator.refresh = fake_refresh

    result = client.get()

    assert result == {"result": "ok"}
    assert refresh_called["value"] is True
    assert session.calls[1]["headers"]["Authorization"] == "Bearer new-token"


def test_get_raises_for_non_json_response():
    class NonJsonResponse(DummyResponse):
        def json(self):
            raise ValueError("not json")

    session = SequencedSession([NonJsonResponse()])
    client = SecureAPIClient(settings=make_settings(), session=session)
    client.tokens = TokenBundle(access_token="access-123")

    with pytest.raises(RequestExecutionError, match="valid JSON"):
        client.get()


def test_build_url_requires_api_base_url():
    client = SecureAPIClient(settings=Settings())

    with pytest.raises(RequestExecutionError, match="API_BASE_URL"):
        client._build_url("/v1/data")


def test_get_retries_on_retryable_server_error():
    session = SequencedSession(
        [
            DummyResponse(ok=False, status_code=503, text="service unavailable"),
            DummyResponse(payload={"result": "ok"}),
        ]
    )
    client = SecureAPIClient(settings=make_settings(), session=session)
    client.tokens = TokenBundle(access_token="access-123")
    client.sleep_func = lambda _: None

    result = client.get()

    assert result == {"result": "ok"}
    assert len(session.calls) == 2
