from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "secure-python-api-integration"


class ConfigSummaryResponse(BaseModel):
    api_base_url: str = ""
    api_auth_url: str = ""
    api_data_path: str = ""
    proxy_enabled: bool = False
    request_timeout: int = 30


class FetchRequest(BaseModel):
    path: str | None = Field(default=None, description="Optional API path override")
    params: dict[str, Any] | None = Field(
        default=None, description="Optional query parameters"
    )


class FetchResponse(BaseModel):
    success: bool = True
    path: str
    data: Any


class PaginatedFetchRequest(FetchRequest):
    start_page: int = Field(default=1, ge=1)
    end_page: int = Field(default=1, ge=1)
    page_param: str = Field(default="page")


class PaginatedFetchResponse(BaseModel):
    success: bool = True
    path: str
    page_param: str
    pages_fetched: list[int]
    data: list[dict[str, Any]]


class ErrorResponse(BaseModel):
    detail: str
