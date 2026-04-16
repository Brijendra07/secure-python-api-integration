from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

from src.config import Settings
from src.exceptions import AuthenticationError
from src.logging_utils import get_logger
from src.retry import run_with_retry


logger = get_logger(__name__)


@dataclass(slots=True)
class TokenBundle:
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class Authenticator:
    """Handles token acquisition and refresh operations."""

    def __init__(self, settings: Settings, session: requests.Session | None = None):
        self.settings = settings
        self.session = session or requests.Session()
        self.sleep_func = __import__("time").sleep

    def authenticate(self) -> TokenBundle:
        logger.info("Starting authentication flow with mode %s", self.settings.auth_mode)
        response = self._post_token_request(self._build_auth_payload())
        return self._parse_token_response(response)

    def refresh(self, refresh_token: str) -> TokenBundle:
        logger.info("Refreshing access token")
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.settings.api_client_id,
            "client_secret": self.settings.api_client_secret,
        }
        response = self._post_token_request(payload)
        return self._parse_token_response(response)

    def _build_auth_payload(self) -> dict[str, Any]:
        if self.settings.auth_mode == "oauth_client_credentials":
            logger.info("Using OAuth client credentials flow")
            return self.settings.oauth_client_credentials_payload

        logger.info("Using username/password authentication flow")
        return self.settings.auth_payload

    def _post_token_request(self, payload: dict[str, Any]) -> requests.Response:
        if not self.settings.api_auth_url:
            logger.error("Authentication failed because API_AUTH_URL is missing")
            raise AuthenticationError("API_AUTH_URL is not configured.")

        def operation() -> requests.Response:
            logger.info("Sending authentication request to token endpoint")
            return self.session.post(
                self.settings.api_auth_url,
                json=payload,
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
            response = run_with_retry(
                operation,
                max_retries=self.settings.max_retries,
                backoff_seconds=self.settings.retry_backoff_seconds,
                should_retry=should_retry,
                operation_name="Authentication request",
                sleep_func=self.sleep_func,
            )
        except requests.RequestException as exc:
            logger.exception("Authentication request raised a transport error")
            raise AuthenticationError(f"Authentication request failed: {exc}") from exc

        if not response.ok:
            logger.error(
                "Authentication endpoint returned status %s", response.status_code
            )
            raise AuthenticationError(
                f"Authentication failed with status {response.status_code}: {response.text}"
            )
        return response

    @staticmethod
    def _parse_token_response(response: requests.Response) -> TokenBundle:
        try:
            payload = response.json()
        except ValueError as exc:
            logger.exception("Authentication response could not be parsed as JSON")
            raise AuthenticationError("Authentication response was not valid JSON.") from exc

        access_token = payload.get("access_token")
        if not access_token:
            logger.error("Authentication response did not include an access token")
            raise AuthenticationError("Authentication response did not include access_token.")

        logger.info("Authentication flow completed successfully")
        return TokenBundle(
            access_token=access_token,
            refresh_token=payload.get("refresh_token"),
            token_type=payload.get("token_type", "Bearer"),
        )
