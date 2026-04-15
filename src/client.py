from __future__ import annotations

from typing import Any

import requests

from src.auth import Authenticator, TokenBundle
from src.config import Settings
from src.exceptions import RequestExecutionError


class SecureAPIClient:
    """Authenticated API client with optional refresh-token retry."""

    def __init__(self, settings: Settings, session: requests.Session | None = None):
        self.settings = settings
        self.session = session or requests.Session()
        self.authenticator = Authenticator(settings=self.settings, session=self.session)
        self.tokens: TokenBundle | None = None

    def ensure_authenticated(self) -> TokenBundle:
        if self.tokens is None:
            self.tokens = self.authenticator.authenticate()
        return self.tokens

    def get(self, path: str | None = None, params: dict[str, Any] | None = None) -> Any:
        endpoint = self._build_url(path or self.settings.api_data_path)
        response = self._send_get(endpoint, params=params)

        if response.status_code == 401 and self.tokens and self.tokens.refresh_token:
            self.tokens = self.authenticator.refresh(self.tokens.refresh_token)
            response = self._send_get(endpoint, params=params)

        if not response.ok:
            raise RequestExecutionError(
                f"API request failed with status {response.status_code}: {response.text}"
            )

        try:
            return response.json()
        except ValueError as exc:
            raise RequestExecutionError("API response was not valid JSON.") from exc

    def _send_get(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> requests.Response:
        tokens = self.ensure_authenticated()
        headers = {"Authorization": f"{tokens.token_type} {tokens.access_token}"}

        try:
            return self.session.get(
                endpoint,
                headers=headers,
                params=params,
                timeout=self.settings.request_timeout,
                proxies=self.settings.proxies,
            )
        except requests.RequestException as exc:
            raise RequestExecutionError(f"API request failed: {exc}") from exc

    def _build_url(self, path: str) -> str:
        if not self.settings.api_base_url:
            raise RequestExecutionError("API_BASE_URL is not configured.")
        return f"{self.settings.api_base_url.rstrip('/')}/{path.lstrip('/')}"
