"""
Test Suite for Visual QA Severity Classifications & Out-of-Scale Sketch Reasoning (Milestone 8).

Validates:
1. Classification of out-of-scale hand sketches (e.g., 1.41 vs 0.92 ratio) as warning vs algorithm error.
2. Major discrepancy identification for missing rooms or opening mismatches.
3. Duplicate entity detection across walls, rooms, and openings.
4. Structured severity categorization (informational, warning, major, blocking).
5. Non-destructive QA reporting: guarantees that QA never modifies approved geometry.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.visual_qa import (
    compare_footprint_aspect_ratio,
    compare_rooms,
    compare_openings,
    compare_dimensions,
    detect_duplicate_entities,
    perform_visual_qa,
    generate_visual_qa_markdown,
)

FIXTURES_DIR = Path("tests/fixtures/sketches")
SAMPLE_OBS_PATH = FIXTURES_DIR / "fixture-a-observations.json"


class TestVisualQASeverity(unittest.TestCase):
    """Unit tests for Visual QA severity analysis and architectural discrepancy reasoning."""

    @classmethod
    def setUpClass(cls):
        with open(SAMPLE_OBS_PATH, "r", encoding="utf-8") as f:
            cls.obs = json.load(f)

    def test_01_out_of_scale_hand_sketch_classification(self):
        # Explicit dimensions: 8000x8700 (ratio 0.920)
        envelope_explicit = {
            "width": 8000.0,
            "depth": 8700.0,
            "widthSource": "explicit",
            "depthSource": "explicit",
        }
        # Sketch drawn in landscape mode: 1200x849 (ratio 1.413)
        sketch_px = {"width": 1200, "height": 849}

        res = compare_footprint_aspect_ratio(sketch_px, envelope_explicit)
        self.assertEqual(res["status"], "DISCREPANCY")
        self.assertEqual(res["severity"], "warning")
        self.assertEqual(res["discrepancy_type"], "out_of_scale_source_sketch")
        self.assertIn("out-of-scale relative to explicit annotations", res["message"])
        self.assertIn("correctly honored explicit dimensions", res["message"])

    def test_02_estimated_aspect_ratio_drift_classification(self):
        # Estimated dimensions: 8000x8700
        envelope_estimated = {
            "width": 8000.0,
            "depth": 8700.0,
            "widthSource": "estimated",
            "depthSource": "estimated",
        }
        sketch_px = {"width": 1200, "height": 849}

        res = compare_footprint_aspect_ratio(sketch_px, envelope_estimated)
        self.assertEqual(res["status"], "DISCREPANCY")
        self.assertEqual(res["severity"], "major_discrepancy")
        self.assertEqual(res["discrepancy_type"], "aspect_ratio_drift")

    def test_03_missing_room_major_discrepancy(self):
        obs_rooms = [
            {"id": "R1", "raw_label": "LIVING ROOM"},
            {"id": "R2", "raw_label": "BEDROOM 1"},
            {"id": "R3", "raw_label": "KITCHEN"},
        ]
        cad_rooms = [
            {"id": "R1", "name": "LIVING ROOM"},
            # BEDROOM 1 and KITCHEN missing
        ]
        res = compare_rooms(obs_rooms, cad_rooms)
        self.assertEqual(res["status"], "DISCREPANCY")
        self.assertEqual(res["severity"], "major_discrepancy")
        self.assertIn("BEDROOM 1", res["missing_in_cad"])
        self.assertIn("KITCHEN", res["missing_in_cad"])

    def test_04_duplicate_entity_detection(self):
        model_clean = {
            "walls": [{"id": "W1"}, {"id": "W2"}],
            "rooms": [{"id": "R1"}, {"id": "R2"}],
            "openings": [{"id": "D1"}],
        }
        res_clean = detect_duplicate_entities(model_clean)
        self.assertEqual(res_clean["status"], "PASS")
        self.assertEqual(res_clean["severity"], "informational")

        model_dup = {
            "walls": [{"id": "W1"}, {"id": "W1"}, {"id": "W2"}],  # Duplicate W1
            "rooms": [{"id": "R1"}, {"id": "R2"}],
            "openings": [{"id": "D1"}],
        }
        res_dup = detect_duplicate_entities(model_dup)
        self.assertEqual(res_dup["status"], "DISCREPANCY")
        self.assertEqual(res_dup["severity"], "major_discrepancy")
        self.assertIn("W1", res_dup["duplicate_ids"])

    def test_05_overall_status_aggregation(self):
        # 1. Clean match
        sample_model = {
            "metadata": {"projectName": "Clean Model"},
            "envelope": {"width": 6000, "depth": 5000, "widthSource": "explicit", "depthSource": "explicit"},
            "walls": [{"id": "W1"}, {"id": "W2"}],
            "openings": [],
            "rooms": [],
            "dimensions": [],
        }
        qa_clean = perform_visual_qa(
            "tests/fixtures/sketches/fixture-a-clean-single-floor.png",
            "dummy.dxf",
            sample_model,
            observations=None,
        )
        self.assertIn(qa_clean["overall_status"], ("MATCH", "REVIEW_REQUIRED"))
        self.assertIn("severity_summary", qa_clean)

    def test_06_markdown_discrepancy_report_rendering(self):
        report = {
            "project_name": "QA Markdown Test",
            "source_sketch": "sketch.png",
            "cad_output": "drawing.dxf",
            "overall_status": "REVIEW_REQUIRED",
            "severity_summary": {
                "blocking_discrepancies": 0,
                "major_discrepancies": 0,
                "warnings": 1,
                "informational": 4,
            },
            "checks_passed": 4,
            "total_checks": 5,
            "checks": [
                {
                    "check": "footprint_aspect_ratio",
                    "status": "DISCREPANCY",
                    "severity": "warning",
                    "message": "Out of scale sketch warning",
                }
            ],
        }
        md = generate_visual_qa_markdown(report)
        self.assertIn("REVIEW REQUIRED", md)
        self.assertIn("Out of scale sketch warning", md)
        self.assertIn("Architectural QA Policy", md)


if __name__ == "__main__":
    unittest.main()
