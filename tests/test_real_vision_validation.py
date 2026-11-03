"""
Test Suite for Real AI Vision Accuracy, Provider Validation & Benchmark Decoupling (Milestone 13).

Validates:
1. Strict provider credential enforcement (refusal to silently fall back to mock).
2. Architectural vision prompt structure (8 extraction domains + strict anti-extrapolation rule).
3. Observation schema extension (source_evidence, review_status, revision_history).
4. apply_human_correction audit trail (hash preservation, revision log, schema validation).
5. Vision execution record schema compliance for 'replayed' execution type.
6. Ground truth isolation in vision pilot runner (zero leakage).
7. Dry-run preflight inspection for Gemini and OpenAI providers.
8. Decoupled benchmark runner evaluation of predictions.
9. Provenance integrity enforcement (genuine AI vs mock baselines).
10. Verification of PILOT-02 CAD deliverables and DXFInspector compliance.
"""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.vision_config import (
    VisionConfig,
    resolve_vision_config,
    validate_vision_config,
)
from scripts.vision_provider import (
    AntigravityAgentVisionProvider,
    GeminiVisionProvider,
    OpenAIVisionProvider,
    MockVisionProvider,
    create_vision_provider,
    build_architectural_vision_prompt,
    save_vision_execution_record,
    get_execution_record_schema,
)
from scripts.sketch_interpreter import (
    validate_observations,
    apply_human_correction,
    get_observations_schema,
)
from scripts.run_vision_pilot import (
    find_sample_image,
    run_inference_for_sample,
)
from scripts.pilot_benchmark_runner import run_pilot_benchmark
from scripts.dxf_inspector import DXFInspector

REPO_ROOT = Path(__file__).resolve().parent.parent
PILOT_DIR = REPO_ROOT / "tests" / "benchmark" / "pilot_dataset"


class TestRealVisionValidation(unittest.TestCase):
    """Unit and integration tests for Milestone 13 real vision accuracy and decoupled benchmarking."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="milestone13_test_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_strict_provider_credential_enforcement(self):
        """Requesting live providers without valid API keys MUST raise ValueError, never silently fallback to mock."""
        cfg_gemini = VisionConfig(provider_name="google_gemini", api_key=None, allow_mock_fallback=True)
        with self.assertRaises(ValueError) as ctx:
            create_vision_provider(cfg_gemini)
        self.assertIn("Missing API key", str(ctx.exception))

        cfg_openai = VisionConfig(provider_name="openai", api_key=None, allow_mock_fallback=True)
        with self.assertRaises(ValueError) as ctx:
            create_vision_provider(cfg_openai)
        self.assertIn("Missing API key", str(ctx.exception))

        # Gemini alias normalization
        cfg_alias = resolve_vision_config(provider_name="gemini")
        self.assertEqual(cfg_alias.provider_name, "google_gemini")

    def test_02_architectural_vision_prompt_sections(self):
        """Vision prompt must contain all 8 architectural extraction domains and anti-extrapolation rule."""
        prompt = build_architectural_vision_prompt()
        self.assertIn("A. Building Envelope", prompt)
        self.assertIn("B. Interior Partitions", prompt)
        self.assertIn("C. Door Schedule", prompt)
        self.assertIn("D. Window Schedule", prompt)
        self.assertIn("E. Room Identifiers", prompt)
        self.assertIn("F. Handwritten & Printed Dimensions", prompt)
        self.assertIn("G. Vertical Circulation", prompt)
        self.assertIn("H. Discrepancies, Ambiguities", prompt)
        self.assertIn("STRICT PROHIBITION AGAINST EXTRAPOLATION", prompt)

    def test_03_observations_schema_extensions(self):
        """Observation schema must accept source_evidence, review_status, and revision_history."""
        obs = {
            "source_metadata": {
                "source_file": "sample.jpg",
                "file_type": "jpg",
                "dimensions_pixels": {"width": 1000, "height": 800},
            },
            "status": "extracted",
            "confidence_summary": {"overall_confidence": 0.9, "dimension_reliability": "high"},
            "walls": [
                {
                    "id": "W-1",
                    "wall_type": "exterior",
                    "source_bbox": [0.1, 0.1, 0.2, 0.9],
                }
            ],
            "openings": [],
            "rooms": [
                {
                    "id": "R-1",
                    "raw_label": "LIVING",
                    "source_bbox": [0.2, 0.2, 0.8, 0.8],
                }
            ],
            "dimensions": [
                {
                    "id": "D-1",
                    "source_text": "5000",
                    "value_mm": 5000.0,
                    "category": "explicit",
                    "source_bbox": [0.05, 0.1, 0.08, 0.9],
                }
            ],
            "uncertainties": [],
            "source_evidence": {
                "source_sha256": "a" * 64,
                "provider_name": "google_gemini",
                "model_identifier": "gemini-2.5-flash",
                "execution_type": "real_api",
                "extraction_timestamp": "2026-11-03T12:00:00Z",
            },
            "review_status": "in_review",
            "revision_history": [
                {
                    "timestamp": "2026-11-03T12:05:00Z",
                    "reviewer": "Architect",
                    "action": "verified",
                    "reason": "Initial inspection",
                }
            ],
        }
        is_valid, errors = validate_observations(obs)
        self.assertTrue(is_valid, f"Schema validation failed: {errors}")

    def test_04_apply_human_correction_audit_trail(self):
        """apply_human_correction updates elements, sets status to 'modified', and logs revision history."""
        obs = {
            "source_metadata": {
                "source_file": "sample.jpg",
                "file_type": "jpg",
                "dimensions_pixels": {"width": 1000, "height": 800},
            },
            "status": "extracted",
            "confidence_summary": {"overall_confidence": 0.9, "dimension_reliability": "high"},
            "walls": [
                {
                    "id": "W-1",
                    "wall_type": "exterior",
                    "thickness_mm": 200.0,
                    "thickness_category": "explicit",
                    "source_bbox": [0.1, 0.1, 0.2, 0.9],
                }
            ],
            "openings": [],
            "rooms": [],
            "dimensions": [],
            "uncertainties": [],
        }

        updated = apply_human_correction(
            observations=obs,
            element_type="walls",
            element_id="W-1",
            corrections={"thickness_mm": 250.0},
            reviewer="Senior Architect",
            reason="Corrected thickness based on structural notes",
        )

        self.assertEqual(updated["walls"][0]["thickness_mm"], 250.0)
        self.assertEqual(updated["review_status"], "modified")
        self.assertEqual(len(updated["revision_history"]), 1)
        entry = updated["revision_history"][0]
        self.assertEqual(entry["reviewer"], "Senior Architect")
        self.assertEqual(entry["element_id"], "W-1")
        self.assertEqual(entry["previous_value"]["thickness_mm"], 200.0)
        self.assertIn("original_hash", entry)
        self.assertIn("revised_hash", entry)
        self.assertNotEqual(entry["original_hash"], entry["revised_hash"])

    def test_05_vision_execution_record_schema_replayed(self):
        """Vision execution record schema accepts 'replayed' execution type."""
        record = {
            "record_id": "VR-REPLAY-1001",
            "execution_type": "replayed",
            "provider_name": "antigravity_agent",
            "model_identifier": "antigravity-native-vision-v1",
            "source_image": {
                "file_name": "sample.jpg",
                "page_number": 1,
                "total_pages": 1,
                "sha256": "1" * 64,
                "dimensions_pixels": {"width": 1200, "height": 900},
            },
            "timestamp": "2026-11-03T12:00:00Z",
            "prompt_version": "arch-interpret-v1.0",
            "status": "success",
            "validation_result": {"is_valid": True, "error_count": 0, "errors": []},
            "processing_duration_ms": 15.0,
        }
        rec_path = Path(self.temp_dir) / "replayed_exec.json"
        save_vision_execution_record(record, str(rec_path))
        self.assertTrue(rec_path.is_file())

    def test_06_ground_truth_isolation(self):
        """find_sample_image locates image in sources/ or fixtures and NEVER touches ground_truth/."""
        img_path, meta = find_sample_image("PILOT-02")
        self.assertTrue(img_path.is_file())
        self.assertNotIn("ground_truth", str(img_path))
        self.assertIn("sources", str(img_path))

    def test_07_dry_run_preflight_inspection(self):
        """Dry-run returns dry_run_ready status without making external network calls."""
        res_gemini = run_inference_for_sample(
            sample_id="PILOT-02",
            provider_name="google_gemini",
            output_dir=Path(self.temp_dir),
            dry_run=True,
        )
        self.assertEqual(res_gemini["status"], "dry_run_ready")
        self.assertEqual(res_gemini["execution_record"]["provider_name"], "google_gemini")

        res_openai = run_inference_for_sample(
            sample_id="PILOT-02",
            provider_name="openai",
            output_dir=Path(self.temp_dir),
            dry_run=True,
        )
        self.assertEqual(res_openai["status"], "dry_run_ready")
        self.assertEqual(res_openai["execution_record"]["provider_name"], "openai")

    def test_08_decoupled_benchmark_evaluator(self):
        """Benchmark runner evaluates predictions decoupled from ground truth."""
        pred_dir = PILOT_DIR / "predictions" / "antigravity_agent"
        if not (pred_dir / "PILOT-02.predictions.json").is_file():
            self.skipTest("PILOT-02 predictions not yet generated.")

        out_results = Path(self.temp_dir) / "results"
        results, cat_summary, jpath, mpath = run_pilot_benchmark(
            output_dir=out_results,
            predictions_dir=pred_dir,
            mode="auto",
        )
        self.assertEqual(len(results), 22)
        pilot_02_res = next(r for r in results if r.sample_id == "PILOT-02")
        self.assertTrue(pilot_02_res.is_genuine_ai)
        self.assertEqual(pilot_02_res.execution_type, "agent_native")
        self.assertAlmostEqual(pilot_02_res.walls.f1, 0.80, places=2)
        self.assertAlmostEqual(pilot_02_res.dimensions.numeric_accuracy_pct, 100.0, places=1)

    def test_09_provenance_integrity_check(self):
        """Verify provenance distinction: mock is never flagged as genuine AI."""
        prov_mock = create_vision_provider(VisionConfig(provider_name="mock"))
        res_mock = prov_mock.interpret_sketch(str(PILOT_DIR / "sources" / "PILOT-01-clean-ortho-studio.png"))
        self.assertEqual(res_mock.execution_record["execution_type"], "mocked")
        self.assertNotEqual(res_mock.execution_record["execution_type"], "real_api")

    def test_10_end_to_end_pilot_02_deliverables_integrity(self):
        """PILOT-02 DXF deliverable exists and satisfies DXFInspector standards."""
        dxf_path = PILOT_DIR / "deliverables" / "PILOT-02" / "pilot-02-authentic-residential-villa.dxf"
        if not dxf_path.is_file():
            self.skipTest("PILOT-02 deliverable not yet built.")

        inspector = DXFInspector()
        audit = inspector.inspect(str(dxf_path))
        self.assertEqual(audit.overall_status, "PASSED")
        self.assertTrue(audit.layer_zero_clean)
        self.assertEqual(audit.degenerate_geometry_count, 0)
        self.assertEqual(audit.duplicate_entities_count, 0)
        self.assertEqual(len(audit.errors), 0)


if __name__ == "__main__":
    unittest.main()
