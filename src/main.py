from __future__ import annotations

import json

from src.client import SecureAPIClient
from src.config import Settings
from src.exceptions import APIIntegrationError


def main() -> None:
    settings = Settings()
    client = SecureAPIClient(settings=settings)

    try:
        response = client.get()
    except APIIntegrationError as exc:
        print(f"Integration failed: {exc}")
        return

    print(json.dumps(response, indent=2))


if __name__ == "__main__":
    main()
