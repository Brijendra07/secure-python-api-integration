from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def test_health_endpoint_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "secure-python-api-integration",
    }


def test_config_summary_masks_to_boolean_proxy_state():
    response = client.get("/config-summary")

    assert response.status_code == 200
    body = response.json()
    assert "proxy_enabled" in body
    assert isinstance(body["proxy_enabled"], bool)


def test_fetch_endpoint_returns_client_response(monkeypatch):
    class DummyIntegrationClient:
        def get(self, path=None, params=None):
            assert path == "/v1/demo"
            assert params == {"limit": 5}
            return {"items": [{"id": 1}]}

    def fake_build_client():
        from src.config import Settings

        return Settings(api_data_path="/v1/data"), DummyIntegrationClient()

    monkeypatch.setattr("src.main.build_client", fake_build_client)

    response = client.post("/fetch", json={"path": "/v1/demo", "params": {"limit": 5}})

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "path": "/v1/demo",
        "data": {"items": [{"id": 1}]},
    }


def test_fetch_endpoint_returns_502_for_integration_errors(monkeypatch):
    from src.exceptions import RequestExecutionError

    class DummyIntegrationClient:
        def get(self, path=None, params=None):
            raise RequestExecutionError("upstream API failed")

    def fake_build_client():
        from src.config import Settings

        return Settings(api_data_path="/v1/data"), DummyIntegrationClient()

    monkeypatch.setattr("src.main.build_client", fake_build_client)

    response = client.post("/fetch", json={})

    assert response.status_code == 502
    assert response.json() == {"detail": "upstream API failed"}
