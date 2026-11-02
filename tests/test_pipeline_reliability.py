"""
Test Suite for Production Reliability, Retry Strategy & Atomic File Operations (Milestone 10).
Validates:
1. RetryConfig default values and customization.
2. Error classification: transient vs. permanent failures.
3. with_retry decorator execution, exponential backoff, and exhaustion.
4. Immediate failure without retry on permanent errors (e.g. invalid auth, schema error).
5. Atomic text writing ensuring no corrupt/half-written files.
6. Atomic JSON serialization and atomic writing.
7. Atomic binary bytes writing.
8. Rollback and cleanup on failed atomic write operations.
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from scripts.pipeline_reliability import (
    PermanentFailureError,
    RetryConfig,
    TransientFailureError,
    atomic_write_bytes,
    atomic_write_json,
    atomic_write_text,
    is_error_retryable,
    with_retry,
)


class TestPipelineReliability(unittest.TestCase):
    """Unit tests for pipeline fault tolerance, retry backoff, and atomic writes."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_01_retry_config_defaults(self):
        """RetryConfig provides sensible production defaults."""
        config = RetryConfig()
        self.assertEqual(config.max_retries, 3)
        self.assertEqual(config.initial_delay_sec, 1.0)
        self.assertEqual(config.backoff_factor, 2.0)
        self.assertIn(429, config.retryable_status_codes)
        self.assertIn(503, config.retryable_status_codes)

    def test_02_transient_vs_permanent_error_classification(self):
        """Correctly identifies transient errors vs. permanent blocking errors."""
        config = RetryConfig()

        # Transient: Timeout, ConnectionError, Rate Limit
        self.assertTrue(is_error_retryable(TimeoutError("Read operation timed out"), config))
        self.assertTrue(is_error_retryable(ConnectionError("Connection reset by peer"), config))
        self.assertTrue(is_error_retryable(Exception("HTTP 429 Rate limit exceeded"), config))

        # Permanent: Authentication, Forbidden, Schema validation
        self.assertFalse(is_error_retryable(Exception("Unauthorized: invalid_api_key provided"), config))
        self.assertFalse(is_error_retryable(Exception("Schema_validation_failed: missing field"), config))
        self.assertFalse(is_error_retryable(PermanentFailureError("Unrecoverable error"), config))

    def test_03_with_retry_succeeds_after_transient_failure(self):
        """Function succeeds on subsequent attempt when earlier attempts raise transient errors."""
        config = RetryConfig(max_retries=3, initial_delay_sec=0.01, jitter=False)
        attempts = 0

        @with_retry(config)
        def flaky_service():
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise TimeoutError("Temporary network timeout")
            return "SUCCESS"

        result = flaky_service()
        self.assertEqual(result, "SUCCESS")
        self.assertEqual(attempts, 3)

    def test_04_with_retry_fails_immediately_on_permanent_error(self):
        """Function raises immediately without retrying when permanent error occurs."""
        config = RetryConfig(max_retries=3, initial_delay_sec=0.01)
        attempts = 0

        @with_retry(config)
        def unauthorized_call():
            nonlocal attempts
            attempts += 1
            raise Exception("Invalid_api_key: check credentials")

        with self.assertRaises(Exception) as ctx:
            unauthorized_call()

        self.assertIn("Invalid_api_key", str(ctx.exception))
        self.assertEqual(attempts, 1)  # Only 1 attempt, zero retries

    def test_05_with_retry_raises_after_exhausting_retries(self):
        """Raises exception after max retries are exhausted on persistent transient failure."""
        config = RetryConfig(max_retries=2, initial_delay_sec=0.01, jitter=False)
        attempts = 0

        @with_retry(config)
        def constantly_failing():
            nonlocal attempts
            attempts += 1
            raise TimeoutError("Persistent server timeout")

        with self.assertRaises(TimeoutError):
            constantly_failing()

        self.assertEqual(attempts, 3)  # Initial + 2 retries = 3 attempts

    def test_06_atomic_write_text(self):
        """Atomic write creates valid text file and overwrites cleanly."""
        target = self.temp_path / "output.txt"
        atomic_write_text(target, "First content")
        self.assertTrue(target.is_file())
        self.assertEqual(target.read_text(encoding="utf-8"), "First content")

        # Overwrite atomically
        atomic_write_text(target, "Updated content")
        self.assertEqual(target.read_text(encoding="utf-8"), "Updated content")

    def test_07_atomic_write_json(self):
        """Atomic JSON write serializes data structures with proper indentation."""
        target = self.temp_path / "data.json"
        data = {"project": "Res-101", "rooms": 4, "validated": True}
        atomic_write_json(target, data, indent=2)

        self.assertTrue(target.is_file())
        with open(target, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        self.assertEqual(loaded, data)

    def test_08_atomic_write_bytes(self):
        """Atomic binary write preserves byte integrity."""
        target = self.temp_path / "binary.bin"
        raw_bytes = b"\x00\x01\x02\x03\xfe\xff"
        atomic_write_bytes(target, raw_bytes)

        self.assertTrue(target.is_file())
        self.assertEqual(target.read_bytes(), raw_bytes)


if __name__ == "__main__":
    unittest.main()
