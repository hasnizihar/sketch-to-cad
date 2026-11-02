"""
Sketch-to-CAD Production Reliability, Retry Strategy & Atomic Execution Engine (Milestone 10)

Provides enterprise-grade fault tolerance across vision inference and CAD pipeline execution:
- Transient vs. permanent failure classification.
- Exponential backoff with jitter and configurable retry limits.
- Atomic file write operations preventing incomplete or corrupted deliverables.
- Structured execution logging with automated secret masking.
"""

from __future__ import annotations

import functools
import json
import logging
import os
import random
import shutil
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union

from scripts.vision_config import mask_secret

logger = logging.getLogger("sketch_to_cad.reliability")


@dataclass
class RetryConfig:
    max_retries: int = 3
    initial_delay_sec: float = 1.0
    backoff_factor: float = 2.0
    max_delay_sec: float = 30.0
    jitter: bool = True
    retryable_status_codes: Set[int] = field(default_factory=lambda: {429, 500, 502, 503, 504})
    retryable_exceptions: Tuple[Type[Exception], ...] = field(
        default_factory=lambda: (TimeoutError, ConnectionError, OSError)
    )


class PermanentFailureError(Exception):
    """Raised for non-retryable errors such as authentication failure or invalid input."""
    pass


class TransientFailureError(Exception):
    """Raised for retryable temporary conditions such as timeouts or rate limits."""
    pass


def is_error_retryable(error: Exception, retry_config: Optional[RetryConfig] = None) -> bool:
    """Determines whether an exception warrants automated retry."""
    config = retry_config or RetryConfig()

    # Permanent failures should never be retried
    err_str = str(error).lower()
    if any(k in err_str for k in ["unauthorized", "invalid_api_key", "forbidden", "schema_validation_failed"]):
        return False

    if isinstance(error, config.retryable_exceptions):
        return True

    # Check HTTP response status codes if present
    if hasattr(error, "response") and error.response is not None:
        status_code = getattr(error.response, "status_code", None)
        if status_code in config.retryable_status_codes:
            return True

    if "rate limit" in err_str or "timeout" in err_str or "connection reset" in err_str:
        return True

    return False


def with_retry(retry_config: Optional[RetryConfig] = None):
    """Decorator applying exponential backoff retry logic to a callable."""
    config = retry_config or RetryConfig()

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = config.initial_delay_sec
            last_err = None

            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_err = e
                    if attempt == config.max_retries or not is_error_retryable(e, config):
                        logger.error(
                            f"[FAIL] Execution failed on attempt {attempt+1}/{config.max_retries+1}: {mask_secret(str(e))}"
                        )
                        raise

                    actual_delay = delay
                    if config.jitter:
                        actual_delay = delay * (0.8 + random.random() * 0.4)

                    logger.warning(
                        f"[RETRY] Attempt {attempt+1} failed with transient error: {mask_secret(str(e))}. "
                        f"Retrying in {actual_delay:.2f}s..."
                    )
                    time.sleep(actual_delay)
                    delay = min(delay * config.backoff_factor, config.max_delay_sec)

            raise last_err
        return wrapper
    return decorator


def atomic_write_text(file_path: Union[str, Path], content: str, encoding: str = "utf-8"):
    """
    Atomically writes text to file using a temporary staging file.
    Ensures that an interrupted write never corrupts the target deliverable.
    """
    p = Path(file_path).resolve()
    p.parent.mkdir(parents=True, exist_ok=True)

    temp_fd, temp_path = tempfile.mkstemp(dir=p.parent, prefix=f"{p.name}_tmp_")
    try:
        with os.fdopen(temp_fd, "w", encoding=encoding) as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())

        # Atomic replacement
        shutil.move(temp_path, str(p))
    except Exception:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        raise


def atomic_write_json(file_path: Union[str, Path], data: Any, indent: int = 2):
    """Atomically serializes and writes JSON data."""
    text = json.dumps(data, indent=indent)
    atomic_write_text(file_path, text)


def atomic_write_bytes(file_path: Union[str, Path], data: bytes):
    """Atomically writes binary data to file."""
    p = Path(file_path).resolve()
    p.parent.mkdir(parents=True, exist_ok=True)

    temp_fd, temp_path = tempfile.mkstemp(dir=p.parent, prefix=f"{p.name}_tmp_")
    try:
        with os.fdopen(temp_fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())

        shutil.move(temp_path, str(p))
    except Exception:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        raise
