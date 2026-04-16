from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(slots=True)
class Settings:
    api_base_url: str = os.getenv("API_BASE_URL", "")
    api_auth_url: str = os.getenv("API_AUTH_URL", "")
    api_data_path: str = os.getenv("API_DATA_PATH", "/v1/data")
    api_username: str = os.getenv("API_USERNAME", "")
    api_password: str = os.getenv("API_PASSWORD", "")
    api_client_id: str = os.getenv("API_CLIENT_ID", "")
    api_client_secret: str = os.getenv("API_CLIENT_SECRET", "")
    proxy_url: str = os.getenv("PROXY_URL", "")
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "30"))

    @property
    def proxies(self) -> dict[str, str]:
        if not self.proxy_url:
            return {}
        return {"http": self.proxy_url, "https": self.proxy_url}

    @property
    def auth_payload(self) -> dict[str, str]:
        return {
            "username": self.api_username,
            "password": self.api_password,
            "client_id": self.api_client_id,
            "client_secret": self.api_client_secret,
        }

    def summary(self) -> dict[str, str | bool | int]:
        return {
            "api_base_url": self.api_base_url,
            "api_auth_url": self.api_auth_url,
            "api_data_path": self.api_data_path,
            "proxy_enabled": bool(self.proxy_url),
            "request_timeout": self.request_timeout,
        }
