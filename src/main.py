from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

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
    PaginatedFetchRequest,
    PaginatedFetchResponse,
)


logger = get_logger(__name__)


app = FastAPI(
    title="Secure Python API Integration",
    description="Portfolio-ready backend service for secure authenticated API access.",
    version="0.1.0",
)

EXPORT_DIR = Path("exports")


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


@app.post(
    "/fetch-paginated",
    response_model=PaginatedFetchResponse,
    responses={400: {"model": ErrorResponse}, 502: {"model": ErrorResponse}},
)
def fetch_paginated_data(request: PaginatedFetchRequest) -> PaginatedFetchResponse:
    settings, client = build_client()
    path = request.path or settings.api_data_path
    logger.info(
        "Paginated fetch requested for path %s from page %s to %s",
        path,
        request.start_page,
        request.end_page,
    )

    if request.end_page < request.start_page:
        raise HTTPException(status_code=400, detail="end_page must be >= start_page")

    try:
        paginated_data = client.fetch_paginated(
            path=path,
            base_params=request.params,
            start_page=request.start_page,
            end_page=request.end_page,
            page_param=request.page_param,
        )
    except APIIntegrationError as exc:
        logger.error("Paginated fetch failed: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return PaginatedFetchResponse(
        path=path,
        page_param=request.page_param,
        pages_fetched=list(range(request.start_page, request.end_page + 1)),
        data=paginated_data,
    )


@app.post("/export/json")
def export_json_file(request: PaginatedFetchRequest) -> FileResponse:
    settings, client = build_client()
    path = request.path or settings.api_data_path

    if request.end_page < request.start_page:
        raise HTTPException(status_code=400, detail="end_page must be >= start_page")

    try:
        data = client.fetch_paginated(
            path=path,
            base_params=request.params,
            start_page=request.start_page,
            end_page=request.end_page,
            page_param=request.page_param,
        )
        export_path = client.export_json(data, EXPORT_DIR / "integration_export.json")
    except APIIntegrationError as exc:
        logger.error("JSON export failed: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return FileResponse(
        path=export_path,
        media_type="application/json",
        filename="integration_export.json",
    )


@app.post("/export/csv")
def export_csv_file(request: PaginatedFetchRequest) -> FileResponse:
    settings, client = build_client()
    path = request.path or settings.api_data_path

    if request.end_page < request.start_page:
        raise HTTPException(status_code=400, detail="end_page must be >= start_page")

    try:
        data = client.fetch_paginated(
            path=path,
            base_params=request.params,
            start_page=request.start_page,
            end_page=request.end_page,
            page_param=request.page_param,
        )
        flattened_rows = [
            {
                "page": item["page"],
                "payload": json.dumps(item["payload"]),
            }
            for item in data
        ]
        export_path = client.export_csv(flattened_rows, EXPORT_DIR / "integration_export.csv")
    except APIIntegrationError as exc:
        logger.error("CSV export failed: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return FileResponse(
        path=export_path,
        media_type="text/csv",
        filename="integration_export.csv",
    )


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
