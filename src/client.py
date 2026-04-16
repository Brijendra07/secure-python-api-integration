from __future__ import annotations

from typing import Any

import requests

from src.auth import Authenticator, TokenBundle
from src.config import Settings
from src.exceptions import RequestExecutionError
from src.logging_utils import get_logger
from src.retry import run_with_retry


logger = get_logger(__name__)


class SecureAPIClient:
    """Authenticated API client with optional refresh-token retry."""

    def __init__(self, settings: Settings, session: requests.Session | None = None):
        self.settings = settings
        self.session = session or requests.Session()
        self.authenticator = Authenticator(settings=self.settings, session=self.session)
        self.tokens: TokenBundle | None = None
        self.sleep_func = __import__("time").sleep

    def ensure_authenticated(self) -> TokenBundle:
        if self.tokens is None:
            logger.info("No cached token found, authenticating client")
            self.tokens = self.authenticator.authenticate()
        return self.tokens

    def get(self, path: str | None = None, params: dict[str, Any] | None = None) -> Any:
        endpoint = self._build_url(path or self.settings.api_data_path)
        logger.info("Executing GET request against %s", endpoint)
        response = self._send_get(endpoint, params=params)

        if response.status_code == 401 and self.tokens and self.tokens.refresh_token:
            logger.warning("Received 401 response, attempting token refresh")
            self.tokens = self.authenticator.refresh(self.tokens.refresh_token)
            response = self._send_get(endpoint, params=params)

        if not response.ok:
            logger.error("GET request failed with status %s", response.status_code)
            raise RequestExecutionError(
                f"API request failed with status {response.status_code}: {response.text}"
            )

        try:
            payload = response.json()
        except ValueError as exc:
            logger.exception("GET response could not be parsed as JSON")
            raise RequestExecutionError("API response was not valid JSON.") from exc

        logger.info("GET request completed successfully")
        return payload

    def _send_get(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> requests.Response:
        tokens = self.ensure_authenticated()
        headers = {"Authorization": f"{tokens.token_type} {tokens.access_token}"}

        def operation() -> requests.Response:
            return self.session.get(
                endpoint,
                headers=headers,
                params=params,
                timeout=self.settings.request_timeout,
                proxies=self.settings.proxies,
            )

        def should_retry(
            response: requests.Response | None, error: Exception | None
        ) -> bool:
            if error is not None:
                return isinstance(error, requests.RequestException)
            return response is not None and response.status_code >= 500

        try:
            return run_with_retry(
                operation,
                max_retries=self.settings.max_retries,
                backoff_seconds=self.settings.retry_backoff_seconds,
                should_retry=should_retry,
                operation_name="GET request",
                sleep_func=self.sleep_func,
            )
        except requests.RequestException as exc:
            logger.exception("GET request raised a transport error")
            raise RequestExecutionError(f"API request failed: {exc}") from exc

    def _build_url(self, path: str) -> str:
        if not self.settings.api_base_url:
            logger.error("Cannot build request URL because API_BASE_URL is missing")
            raise RequestExecutionError("API_BASE_URL is not configured.")
        return f"{self.settings.api_base_url.rstrip('/')}/{path.lstrip('/')}"
