from __future__ import annotations

import json

from fastapi import FastAPI, HTTPException

from src.client import SecureAPIClient
from src.config import Settings
from src.exceptions import APIIntegrationError
from src.logging_utils import get_logger
from src.schemas import (
    ConfigSummaryResponse,
    ErrorResponse,
    FetchRequest,
    FetchResponse,
    HealthResponse,
)


logger = get_logger(__name__)


app = FastAPI(
    title="Secure Python API Integration",
    description="Portfolio-ready backend service for secure authenticated API access.",
    version="0.1.0",
)


def build_client() -> tuple[Settings, SecureAPIClient]:
    settings = Settings()
    return settings, SecureAPIClient(settings=settings)


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    logger.info("Health check requested")
    return HealthResponse()


@app.get("/config-summary", response_model=ConfigSummaryResponse)
def config_summary() -> ConfigSummaryResponse:
    logger.info("Configuration summary requested")
    settings = Settings()
    return ConfigSummaryResponse(**settings.summary())


@app.post(
    "/fetch",
    response_model=FetchResponse,
    responses={400: {"model": ErrorResponse}, 502: {"model": ErrorResponse}},
)
def fetch_data(request: FetchRequest) -> FetchResponse:
    settings, client = build_client()
    path = request.path or settings.api_data_path
    logger.info("Fetch endpoint called for path %s", path)

    try:
        response = client.get(path=path, params=request.params)
    except APIIntegrationError as exc:
        logger.error("Fetch endpoint failed: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    logger.info("Fetch endpoint completed successfully")
    return FetchResponse(path=path, data=response)


def main() -> None:
    settings, client = build_client()
    logger.info("Running demo integration script")

    try:
        response = client.get()
    except APIIntegrationError as exc:
        logger.error("Demo integration failed: %s", exc)
        print(f"Integration failed: {exc}")
        return

    print(json.dumps(response, indent=2))


if __name__ == "__main__":
    main()
