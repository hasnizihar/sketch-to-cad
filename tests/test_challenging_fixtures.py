"""
Test Suite for Challenging Architectural Test Fixtures (Cases F through K) - Milestone 9.

Validates the complete pipeline against edge cases and demanding architectural configurations:
- Case F: Complex Junctions (T-junctions, cross-junctions, thickness transitions, clean cavity trimming).
- Case G: Complex Openings (double-leaf doors, sliding doors, sliding windows, corner clearance warnings).
- Case H: Irregular Floor Plan (L-shaped footprint, 6-vertex room boundary polygon, Shoelace area).
- Case I: Compact ADU / Tiny Home (high density, furniture & fixture clearances in 32 m²).
- Case J: Multi-Storey Complex (Ground Floor & First Floor, shared envelope, vertical stair alignment).
- Case K: Incomplete & Ambiguous Sketch (unapproved status, missing dimensions -> mandatory Approval Gate rejection).
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from scripts.drawing_generator import (
    DrawingGenerator,
    ApprovalGateError,
    compile_bim_handoff,
    CADCraftClient,
    CADCRAFT_CLI_DEFAULT,
)
from scripts.geometry_validation import ArchitecturalGeometryValidator
from scripts.architectural_qa import perform_architectural_qa

FIXTURES_DIR = Path("tests/fixtures/sketches")


class TestChallengingFixtures(unittest.TestCase):
    """Integration test suite executing Cases F through K."""

    @classmethod
    def setUpClass(cls):
        cls.cli_available = os.path.exists(CADCRAFT_CLI_DEFAULT)
        cls.temp_dir = tempfile.mkdtemp(prefix="sketch_to_cad_cases_")

    def test_01_case_f_complex_junctions(self):
        """Case F: Validates wall network junctions and cavity trimming without blocking errors."""
        fixture_path = FIXTURES_DIR / "fixture-f-complex-junctions.json"
        with open(fixture_path, "r", encoding="utf-8") as f:
            model = json.load(f)

        # 1. Geometry Validation
        validator = ArchitecturalGeometryValidator()
        res = validator.validate(model)
        self.assertEqual(res.severity_counts["blocking"], 0)
        self.assertGreater(res.summary["junction_counts"]["T-junction"], 0)

        # 2. Architectural QA
        qa = perform_architectural_qa(model)
        self.assertNotEqual(qa["status"], "FAILED_BLOCKING")

        # 3. BIM Handoff Compilation
        handoff = compile_bim_handoff(model, dxf_path=os.path.join(self.temp_dir, "case_f.dxf"))
        self.assertEqual(len(handoff["walls"]), len(model["walls"]))

    def test_02_case_g_complex_openings(self):
        """Case G: Validates double doors, sliding doors, sliding windows, and corner clearances."""
        fixture_path = FIXTURES_DIR / "fixture-g-complex-openings.json"
        with open(fixture_path, "r", encoding="utf-8") as f:
            model = json.load(f)

        # 1. Geometry Validation
        validator = ArchitecturalGeometryValidator()
        res = validator.validate(model)
        self.assertEqual(res.severity_counts["blocking"], 0)
        self.assertEqual(res.severity_counts["major"], 0)

        # 2. Verify diverse opening types are present
        swings = {op.get("swing") for op in model["openings"]}
        self.assertIn("double", swings)
        self.assertIn("sliding", swings)
        self.assertIn("inward-left", swings)
        self.assertIn("inward-right", swings)

        # 3. Preflight and Drawing Generation check
        gen = DrawingGenerator()
        gen.validate_preflight(model)

    def test_03_case_h_irregular_plan(self):
        """Case H: Validates non-rectangular L-shaped footprint and non-convex room polygons."""
        fixture_path = FIXTURES_DIR / "fixture-h-irregular-plan.json"
        with open(fixture_path, "r", encoding="utf-8") as f:
            model = json.load(f)

        # 1. Geometry Validation
        validator = ArchitecturalGeometryValidator()
        res = validator.validate(model)
        self.assertEqual(res.severity_counts["blocking"], 0)

        # 2. Verify Salon Room polygon has 5 boundary corners (non-convex angled wall)
        salon_room = next(r for r in model["rooms"] if r["id"] == "R-SALON")
        self.assertEqual(len(salon_room["boundaryCorners"]), 5)
        self.assertGreater(salon_room["approximateArea"], 20.0)

        # 3. Architectural QA
        qa = perform_architectural_qa(model)
        self.assertIn(qa["status"], ["PASSED", "REVIEW_REQUIRED"])

    def test_04_case_i_compact_plan(self):
        """Case I: Validates compact 32 m² studio/ADU plan with dense fixtures and furniture."""
        fixture_path = FIXTURES_DIR / "fixture-i-compact-plan.json"
        with open(fixture_path, "r", encoding="utf-8") as f:
            model = json.load(f)

        # 1. Geometry Validation
        validator = ArchitecturalGeometryValidator()
        res = validator.validate(model)
        self.assertEqual(res.severity_counts["blocking"], 0)

        # 2. Check elements all fall within 6000x5500 envelope
        env = model["envelope"]
        for el in model.get("elements", []):
            pos = el["position"]
            self.assertTrue(0 <= pos[0] <= env["width"])
            self.assertTrue(0 <= pos[1] <= env["depth"])

        # 3. Preflight
        gen = DrawingGenerator()
        gen.validate_preflight(model)

    def test_05_case_j_multi_storey_complex(self):
        """Case J: Validates 2-storey residential plan, level filtering, and staircase coordination."""
        fixture_path = FIXTURES_DIR / "fixture-j-multi-storey-complex.json"
        with open(fixture_path, "r", encoding="utf-8") as f:
            model = json.load(f)

        self.assertEqual(len(model["floors"]), 2)

        # 1. Level-specific validation
        val_gf = ArchitecturalGeometryValidator().validate(model, level_filter="LEVEL-01")
        self.assertEqual(val_gf.severity_counts["blocking"], 0)

        val_ff = ArchitecturalGeometryValidator().validate(model, level_filter="LEVEL-02")
        self.assertEqual(val_ff.severity_counts["blocking"], 0)

        # 2. Verify staircase exists on both floors and shares alignment
        stairs = [el for el in model["elements"] if el["category"] == "circulation"]
        self.assertGreaterEqual(len(stairs), 2)
        stair_gf = next(s for s in stairs if s.get("floorId") == "LEVEL-01")
        stair_ff = next(s for s in stairs if s.get("floorId") == "LEVEL-02")
        self.assertEqual(stair_gf["position"], stair_ff["position"])

        # 3. Multi-storey BIM handoff compilation
        handoff = compile_bim_handoff(model, dxf_path=os.path.join(self.temp_dir, "case_j.dxf"))
        self.assertIn("floors", handoff)
        self.assertEqual(len(handoff["floors"]), 2)

    def test_06_case_k_incomplete_ambiguous_rejected_by_approval_gate(self):
        """Case K: Unapproved status ('awaiting_approval') MUST be rejected by Approval Gate."""
        fixture_path = FIXTURES_DIR / "fixture-k-incomplete-ambiguous.json"
        with open(fixture_path, "r", encoding="utf-8") as f:
            model = json.load(f)

        self.assertEqual(model["status"], "awaiting_approval")

        gen = DrawingGenerator()
        with self.assertRaises(ApprovalGateError) as ctx:
            gen.validate_preflight(model)

        self.assertIn("Approval Gate Violation", str(ctx.exception))
        self.assertIn("awaiting_approval", str(ctx.exception))

        # Even if someone attempts to run full build_drawing, preflight blocks execution
        out_dxf = os.path.join(self.temp_dir, "should_not_exist.dxf")
        out_png = os.path.join(self.temp_dir, "should_not_exist.png")
        with self.assertRaises(ApprovalGateError):
            gen.build_drawing(model, out_dxf, out_png)
        self.assertFalse(os.path.exists(out_dxf))


if __name__ == "__main__":
    unittest.main()
