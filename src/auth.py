from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

from src.config import Settings
from src.exceptions import AuthenticationError


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

    def authenticate(self) -> TokenBundle:
        response = self._post_token_request(self.settings.auth_payload)
        return self._parse_token_response(response)

    def refresh(self, refresh_token: str) -> TokenBundle:
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.settings.api_client_id,
            "client_secret": self.settings.api_client_secret,
        }
        response = self._post_token_request(payload)
        return self._parse_token_response(response)

    def _post_token_request(self, payload: dict[str, Any]) -> requests.Response:
        if not self.settings.api_auth_url:
            raise AuthenticationError("API_AUTH_URL is not configured.")

        try:
            response = self.session.post(
                self.settings.api_auth_url,
                json=payload,
                timeout=self.settings.request_timeout,
                proxies=self.settings.proxies,
            )
        except requests.RequestException as exc:
            raise AuthenticationError(f"Authentication request failed: {exc}") from exc

        if not response.ok:
            raise AuthenticationError(
                f"Authentication failed with status {response.status_code}: {response.text}"
            )
        return response

    @staticmethod
    def _parse_token_response(response: requests.Response) -> TokenBundle:
        try:
            payload = response.json()
        except ValueError as exc:
            raise AuthenticationError("Authentication response was not valid JSON.") from exc

        access_token = payload.get("access_token")
        if not access_token:
            raise AuthenticationError("Authentication response did not include access_token.")

        return TokenBundle(
            access_token=access_token,
            refresh_token=payload.get("refresh_token"),
            token_type=payload.get("token_type", "Bearer"),
        )
