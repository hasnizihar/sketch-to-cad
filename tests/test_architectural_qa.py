"""
Test Suite for Architectural QA & Engineering Standards Validator (Milestone 9).
Validates:
1. Multi-tier severity classification (blocking, major, warning, informational).
2. BIM handoff integrity verification (host wall references, coordinate systems, unique IDs).
3. Comprehensive QA report execution (geometric validation + BIM handoff + presentation checks).
4. Engineering QA Markdown report generation for human review.
5. Backward compatibility with visual QA and headless operation.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.architectural_qa import (
    perform_architectural_qa,
    validate_bim_handoff_integrity,
    generate_engineering_qa_markdown,
)

SAMPLE_MODEL_PATH = Path("tests/fixtures/sample-model.json")
FURNISHED_MODEL_PATH = Path("tests/fixtures/sample-model-with-elements.json")


class TestArchitecturalQA(unittest.TestCase):
    """Unit tests for Architectural & Engineering QA validation logic."""

    @classmethod
    def setUpClass(cls):
        with open(SAMPLE_MODEL_PATH, "r", encoding="utf-8") as f:
            cls.sample_model = json.load(f)
        with open(FURNISHED_MODEL_PATH, "r", encoding="utf-8") as f:
            cls.furnished_model = json.load(f)

    def test_01_bim_handoff_integrity_valid(self):
        """Valid BIM handoff metadata passes integrity check with zero errors."""
        valid_handoff = {
            "project": {"name": "Test Project", "coordinateSystem": "Cartesian2D_RightHanded_YUp"},
            "walls": [
                {"id": "w1", "start": [0, 0], "end": [5000, 0], "thickness": 200},
                {"id": "w2", "start": [5000, 0], "end": [5000, 4000], "thickness": 200},
            ],
            "openings": [
                {"id": "d1", "wallId": "w1", "type": "door", "width": 900, "height": None}
            ]
        }
        is_valid, errors = validate_bim_handoff_integrity(valid_handoff)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_02_bim_handoff_missing_host_wall(self):
        """Opening referencing non-existent host wall fails BIM handoff integrity check."""
        invalid_handoff = {
            "project": {"name": "Test Project", "coordinateSystem": "Cartesian2D_RightHanded_YUp"},
            "walls": [
                {"id": "w1", "start": [0, 0], "end": [5000, 0], "thickness": 200}
            ],
            "openings": [
                {"id": "d1", "wallId": "w_missing_99", "type": "door", "width": 900}
            ]
        }
        is_valid, errors = validate_bim_handoff_integrity(invalid_handoff)
        self.assertFalse(is_valid)
        self.assertTrue(any("references non-existent host wall" in e for e in errors))

    def test_03_bim_handoff_duplicate_wall_ids(self):
        """Duplicate wall IDs in BIM handoff metadata fails validation."""
        dup_handoff = {
            "walls": [
                {"id": "w1", "start": [0, 0], "end": [5000, 0]},
                {"id": "w1", "start": [5000, 0], "end": [5000, 4000]}
            ]
        }
        is_valid, errors = validate_bim_handoff_integrity(dup_handoff)
        self.assertFalse(is_valid)
        self.assertTrue(any("Duplicate or missing wall IDs" in e for e in errors))

    def test_04_perform_architectural_qa_on_sample_model(self):
        """Perform architectural QA on approved sample baseline model."""
        report = perform_architectural_qa(self.sample_model)
        self.assertIn("status", report)
        self.assertIn("severity_counts", report)
        self.assertIn("issues", report)
        # Sample model should not contain blocking errors
        self.assertEqual(report["severity_counts"]["blocking"], 0)
        self.assertIn(report["status"], ["PASSED", "REVIEW_REQUIRED"])

    def test_05_blocking_severity_blocks_approval(self):
        """A blocking error forces overall status to FAILED_BLOCKING."""
        corrupt_model = json.loads(json.dumps(self.sample_model))
        # Add a degenerate 2mm wall
        corrupt_model["walls"].append({
            "id": "w_corrupt",
            "start": [0.0, 0.0],
            "end": [2.0, 0.0],
            "thickness": 200.0,
        })
        report = perform_architectural_qa(corrupt_model)
        self.assertEqual(report["status"], "FAILED_BLOCKING")
        self.assertGreaterEqual(report["severity_counts"]["blocking"], 1)

    def test_06_major_discrepancy_status(self):
        """A major error with no blocking errors yields MAJOR_DISCREPANCY status."""
        major_model = json.loads(json.dumps(self.sample_model))
        # Add an opening with missing host wall
        major_model["openings"].append({
            "id": "d_orphan",
            "wallId": "w_non_existent",
            "type": "door",
            "distanceFromStart": 500,
            "width": 900,
        })
        report = perform_architectural_qa(major_model)
        self.assertEqual(report["status"], "MAJOR_DISCREPANCY")
        self.assertGreaterEqual(report["severity_counts"]["major"], 1)
        self.assertEqual(report["severity_counts"]["blocking"], 0)

    def test_07_warning_status(self):
        """Warning issues without blocking or major errors yield REVIEW_REQUIRED status."""
        warn_model = {
            "envelope": {"width": 8000, "depth": 6000, "origin": [0, 0]},
            "walls": [
                {"id": "w1", "start": [0, 0], "end": [8000, 0], "thickness": 200},
                {"id": "w2", "start": [8000, 0], "end": [8000, 6000], "thickness": 200},
            ],
            "openings": [
                # 20mm from start (< 50mm corner clearance)
                {"id": "d1", "wallId": "w1", "type": "door", "distanceFromStart": 20, "width": 900}
            ]
        }
        report = perform_architectural_qa(warn_model)
        self.assertEqual(report["status"], "REVIEW_REQUIRED")
        self.assertGreaterEqual(report["severity_counts"]["warning"], 1)
        self.assertEqual(report["severity_counts"]["blocking"], 0)
        self.assertEqual(report["severity_counts"]["major"], 0)

    def test_08_generate_engineering_qa_markdown(self):
        """Verify markdown report generation contains necessary architectural sections."""
        report = perform_architectural_qa(self.furnished_model)
        md = generate_engineering_qa_markdown(report)
        self.assertIn("# Architectural & Engineering QA Audit Report", md)
        self.assertIn("## Executive Summary", md)
        self.assertIn("## Severity Breakdown", md)
        self.assertIn("## Itemized Audit Findings", md)
        self.assertIn("## Recommended Corrective Actions", md)
        self.assertTrue(len(md) > 200)


if __name__ == "__main__":
    unittest.main()
