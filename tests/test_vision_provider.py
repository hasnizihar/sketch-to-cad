"""
Test Suite for Multimodal Vision Provider and Execution Records (Milestone 8).

Validates provider configuration, credential handling, secret masking,
source image hashing, mock failure simulation (timeout, rate limits, malformed JSON),
and Draft-07 execution record schema compliance.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.vision_config import (
    VisionConfig,
    resolve_vision_config,
    validate_vision_config,
    mask_secret,
)
from scripts.vision_provider import (
    BaseVisionProvider,
    GeminiVisionProvider,
    OpenAIVisionProvider,
    MockVisionProvider,
    AntigravityAgentVisionProvider,
    create_vision_provider,
    compute_source_sha256,
    encode_image_for_api,
    build_architectural_vision_prompt,
    save_vision_execution_record,
    get_execution_record_schema,
)

FIXTURES_DIR = Path("tests/fixtures/sketches")
SAMPLE_IMG = FIXTURES_DIR / "fixture-a-clean-single-floor.png"
SAMPLE_PDF = FIXTURES_DIR / "fixture-d-two-storey.pdf"


class TestVisionProvider(unittest.TestCase):
    """Unit and mock integration tests for Vision Provider."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="agy_vision_test_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_config_resolution_and_defaults(self):
        cfg = resolve_vision_config(provider_name="mock")
        self.assertEqual(cfg.provider_name, "mock")
        self.assertEqual(cfg.model_identifier, "mock-architectural-v1")
        self.assertTrue(cfg.allow_mock_fallback)

    def test_02_secret_masking(self):
        self.assertEqual(mask_secret(None), "[NOT SET]")
        self.assertEqual(mask_secret(""), "[NOT SET]")
        self.assertEqual(mask_secret("short"), "***")
        masked = mask_secret("AIzaSyD-1234567890abcdef")
        self.assertTrue(masked.startswith("AIz...cdef"))
        self.assertNotIn("1234567890", masked)

        cfg = VisionConfig(provider_name="google_gemini", api_key="secret-api-key-12345")
        rep = repr(cfg)
        self.assertNotIn("secret-api-key", rep)
        self.assertIn("***", rep)

    def test_03_config_validation_missing_credentials(self):
        # Gemini missing API key
        cfg_gemini_no_key = VisionConfig(provider_name="google_gemini", api_key=None)
        valid, errors = validate_vision_config(cfg_gemini_no_key)
        self.assertFalse(valid)
        self.assertTrue(any("Missing API key" in e for e in errors))

        # OpenAI missing API key
        cfg_openai_no_key = VisionConfig(provider_name="openai", api_key=None)
        valid, errors = validate_vision_config(cfg_openai_no_key)
        self.assertFalse(valid)
        self.assertTrue(any("Missing API key" in e for e in errors))

        # Unsupported provider
        cfg_bad = VisionConfig(provider_name="unsupported_engine")
        valid, errors = validate_vision_config(cfg_bad)
        self.assertFalse(valid)
        self.assertTrue(any("Unsupported provider" in e for e in errors))

    def test_04_source_image_sha256_computation(self):
        sha_img = compute_source_sha256(str(SAMPLE_IMG))
        self.assertEqual(len(sha_img), 64)
        # Re-computing on same file must match exactly
        self.assertEqual(sha_img, compute_source_sha256(str(SAMPLE_IMG)))

        # Test PDF page hashing
        sha_p1 = compute_source_sha256(str(SAMPLE_PDF), page_number=1)
        sha_p2 = compute_source_sha256(str(SAMPLE_PDF), page_number=2)
        self.assertEqual(len(sha_p1), 64)
        self.assertEqual(len(sha_p2), 64)
        self.assertNotEqual(sha_p1, sha_p2)

    def test_05_image_base64_encoding(self):
        b64_data, mime = encode_image_for_api(str(SAMPLE_IMG))
        self.assertEqual(mime, "image/png")
        self.assertGreater(len(b64_data), 100)

        # PDF page encoding
        b64_pdf, mime_pdf = encode_image_for_api(str(SAMPLE_PDF), page_number=1)
        self.assertEqual(mime_pdf, "image/png")
        self.assertGreater(len(b64_pdf), 100)

    def test_06_architectural_vision_prompt(self):
        prompt = build_architectural_vision_prompt()
        self.assertIn("SketchObservations", prompt)
        self.assertIn("explicit", prompt)
        self.assertIn("estimated", prompt)
        self.assertIn("inferred", prompt)
        self.assertIn("NEVER fabricate dimensions", prompt)

    def test_07_mock_provider_success_flow(self):
        cfg = resolve_vision_config(provider_name="mock")
        prov = create_vision_provider(cfg)
        res = prov.interpret_sketch(str(SAMPLE_IMG))

        self.assertEqual(res.status, "success")
        self.assertIsNotNone(res.observations)
        self.assertIsNotNone(res.execution_record)
        self.assertEqual(res.execution_record["execution_type"], "mocked")
        self.assertEqual(res.execution_record["provider_name"], "mock_provider")
        self.assertTrue(res.execution_record["validation_result"]["is_valid"])

    def test_08_mock_provider_timeout_simulation(self):
        cfg = resolve_vision_config(provider_name="mock")
        prov = MockVisionProvider(cfg, simulated_behavior="timeout")
        res = prov.interpret_sketch(str(SAMPLE_IMG))

        self.assertEqual(res.status, "timeout")
        self.assertIsNone(res.observations)
        self.assertEqual(res.execution_record["status"], "timeout")
        self.assertEqual(res.execution_record["error_details"]["error_code"], "SIMULATED_TIMEOUT")

    def test_09_mock_provider_rate_limit_simulation(self):
        cfg = resolve_vision_config(provider_name="mock")
        prov = MockVisionProvider(cfg, simulated_behavior="rate_limited")
        res = prov.interpret_sketch(str(SAMPLE_IMG))

        self.assertEqual(res.status, "rate_limited")
        self.assertEqual(res.execution_record["error_details"]["http_status"], 429)

    def test_10_mock_provider_malformed_json_simulation(self):
        cfg = resolve_vision_config(provider_name="mock")
        prov = MockVisionProvider(cfg, simulated_behavior="malformed_json")
        res = prov.interpret_sketch(str(SAMPLE_IMG))

        self.assertEqual(res.status, "invalid_response")
        self.assertIn("JSONDecodeError", res.error_message)

    def test_11_save_vision_execution_record_schema_validation(self):
        cfg = resolve_vision_config(provider_name="mock")
        prov = create_vision_provider(cfg)
        res = prov.interpret_sketch(str(SAMPLE_IMG))

        rec_path = Path(self.temp_dir) / "test_exec.json"
        save_vision_execution_record(res.execution_record, str(rec_path))
        self.assertTrue(rec_path.is_file())

        # Tamper record and verify schema rejection
        bad_rec = dict(res.execution_record)
        del bad_rec["execution_type"]
        with self.assertRaises(ValueError):
            save_vision_execution_record(bad_rec, str(Path(self.temp_dir) / "bad.json"))

    def test_12_antigravity_agent_native_provider(self):
        cfg = resolve_vision_config(provider_name="antigravity_agent")
        prov = create_vision_provider(cfg)
        res = prov.interpret_sketch(str(SAMPLE_IMG))

        self.assertEqual(res.status, "success")
        self.assertEqual(res.execution_record["execution_type"], "agent_native")
        self.assertEqual(res.execution_record["provider_name"], "antigravity_agent")


if __name__ == "__main__":
    unittest.main()
