from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

from src.logging_utils import get_logger


logger = get_logger(__name__)

T = TypeVar("T")


def run_with_retry(
    operation: Callable[[], T],
    *,
    max_retries: int,
    backoff_seconds: float,
    should_retry: Callable[[T | None, Exception | None], bool],
    operation_name: str,
    sleep_func: Callable[[float], None] = time.sleep,
) -> T:
    last_exception: Exception | None = None
    max_attempts = max_retries + 1

    for attempt in range(1, max_attempts + 1):
        try:
            result = operation()
        except Exception as exc:
            last_exception = exc
            if attempt >= max_attempts or not should_retry(None, exc):
                raise

            delay = backoff_seconds * (2 ** (attempt - 1))
            logger.warning(
                "%s failed on attempt %s/%s with %s. Retrying in %.2fs",
                operation_name,
                attempt,
                max_attempts,
                exc,
                delay,
            )
            sleep_func(delay)
            continue

        if attempt >= max_attempts or not should_retry(result, None):
            return result

        delay = backoff_seconds * (2 ** (attempt - 1))
        logger.warning(
            "%s returned a retryable response on attempt %s/%s. Retrying in %.2fs",
            operation_name,
            attempt,
            max_attempts,
            delay,
        )
        sleep_func(delay)

    if last_exception is not None:
        raise last_exception

    raise RuntimeError(f"{operation_name} exhausted retries without a result.")
