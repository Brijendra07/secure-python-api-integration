# Secure Python API Integration

A practical Python backend project that demonstrates secure API integration patterns for real-world business systems.

This project focuses on the kind of backend work clients often need in production:

- token-based authentication
- OAuth client credentials support
- refresh token support
- proxy-aware requests
- reliable API communication
- structured error handling
- reusable Python client design
- API service exposure through FastAPI
- structured logging
- retry support with backoff
- paginated data retrieval
- JSON and CSV export workflows

It is designed as a portfolio-ready reference project for secure data access and external API integration workflows.

## Why This Project

Many backend integrations fail not because of business logic, but because of operational details such as:

- authentication flow handling
- expired access tokens
- proxy/network environments
- request formatting issues
- poor error visibility

This project demonstrates how to build a clean Python integration layer that handles those concerns in a reusable and production-oriented way.

It now supports both:

- username/password style token acquisition
- OAuth client credentials style token acquisition

## Core Use Case

The project implements a Python client and a lightweight FastAPI service that:

1. authenticates with an external API
2. stores or reuses an access token
3. refreshes credentials when needed
4. sends authenticated requests to protected endpoints
5. optionally supports proxy configuration
6. exposes integration behavior through API endpoints
7. returns structured results with safe error handling

## Features

- Python-based API client for external service integration
- token authentication workflow
- OAuth-style client credentials authentication workflow
- refresh token handling
- configurable request headers and payloads
- proxy support for restricted enterprise environments
- clean request/response handling
- structured exceptions for integration failures
- reusable module layout for future API clients
- FastAPI endpoints for health checks, config summary, fetch, paginated fetch, and export operations
- example script for running the integration flow
- test coverage for auth, client, and API service behavior
- README-driven setup and usage documentation

## Tech Stack

- Python 3.12
- `requests`
- `FastAPI`
- `Pydantic`
- `pandas`
- `pytest`
- environment-based configuration using `.env`

## Project Structure

```text
secure-python-api-integration/
  README.md
  .env.example
  requirements.txt
  pytest.ini
  src/
    auth.py
    client.py
    config.py
    exceptions.py
    logging_utils.py
    main.py
    retry.py
    schemas.py
  examples/
    run_demo.py
  tests/
    test_api.py
    test_auth.py
    test_client.py
```

## What This Project Demonstrates To Clients

This project is meant to show practical backend value, not just code complexity.

It demonstrates:

- secure API integration using Python
- understanding of authentication and token lifecycle handling
- ability to build backend utilities that work in real environments
- ability to expose secure integration logic through a backend API
- clean code structure for maintainability
- implementation focused on reliability instead of demo-only output
- observability through structured logging
- resilience through retry/backoff handling
- paginated retrieval and export support for downstream workflows
- tested service behavior for easier evolution and debugging

This makes it relevant for jobs involving:

- API integrations
- secure backend workflows
- automation scripts
- enterprise/proxy environments
- Python service development

## Example Functional Flow

An example integration flow works like this:

1. Read API credentials and settings from environment variables
2. Authenticate against a token endpoint
3. Save the access token in memory for the current session
4. Send a request to a target endpoint with the bearer token
5. If the token is expired, refresh it and retry
6. If a proxy is configured, route requests through the proxy
7. Return parsed JSON data or a clear integration error

The FastAPI layer currently exposes:

- `GET /health` for service health checks
- `GET /config-summary` for safe config inspection
- `POST /fetch` for authenticated request execution
- `POST /fetch-paginated` for multi-page retrieval
- `POST /export/json` for JSON export
- `POST /export/csv` for CSV export

## Environment Variables

Example configuration:

```env
API_BASE_URL=https://api.example.com
API_AUTH_URL=https://api.example.com/auth/token
API_DATA_PATH=/v1/data
AUTH_MODE=basic
API_USERNAME=your_username
API_PASSWORD=your_password
API_CLIENT_ID=your_client_id
API_CLIENT_SECRET=your_client_secret
OAUTH_SCOPE=
PROXY_URL=
REQUEST_TIMEOUT=30
MAX_RETRIES=2
RETRY_BACKOFF_SECONDS=0.5
```

## Example Commands

Create the project environment:

```bash
uv venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt
```

Run a demo script:

```bash
python examples/run_demo.py
```

Run the FastAPI service:

```bash
uvicorn src.main:app --reload
```

Run the test suite:

```bash
pytest
```

## Reliability Considerations

This project is designed around backend concerns that matter in real integrations:

- timeout handling
- retry-safe request logic
- authentication failure visibility
- safe config loading
- explicit exception handling
- clear separation between auth logic and request logic
- API contract validation through typed request/response models
- structured logging across auth, request, and API layers
- controlled retries for transient transport and upstream failures

## Security Considerations

- store credentials in environment variables, not source code
- do not commit real API keys or passwords
- redact sensitive values in logs
- keep proxy credentials private
- validate and sanitize external inputs before sending requests

## Portfolio Positioning

Suggested portfolio title:

`Secure Python API Integration for Authenticated Data Access`

Suggested short description:

`Built a secure Python-based API integration workflow with token and OAuth client-credentials authentication, refresh-token handling, proxy support, FastAPI endpoints, retry/backoff handling, structured logging, and JSON/CSV export for reliable backend data access.`

Suggested client-facing value statement:

`This project demonstrates how I build practical Python backend integrations that work reliably in real environments, including token and OAuth-based APIs, enterprise proxy constraints, reusable request flows, service-ready API endpoints, and export-friendly data pipelines.`

## Current Status

Implemented today:

- secure token-based auth client
- OAuth client credentials auth support
- refresh-token support
- proxy-aware request configuration
- FastAPI API layer
- structured logging
- retries with exponential backoff
- paginated fetch support
- JSON export support
- CSV export support
- automated tests for auth, client, and API endpoints

## Future Enhancements

- add a lightweight demo dashboard UI
