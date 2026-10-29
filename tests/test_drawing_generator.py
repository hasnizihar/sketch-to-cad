"""
Automated Test Suite for Sketch-to-CAD Drawing Generator (Milestone 3)
Verifies full pipeline integration: floor-plan model interpretation, approval gate,
block registration, element insertion, floor finishes, and real CADCraft DXF export.
"""

import os
import sys
import json
import unittest
import tempfile
import subprocess

# Add repository root and scripts to python path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.join(REPO_ROOT, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from drawing_generator import (
    DrawingGenerator,
    ApprovalGateError,
    CADCraftClient,
    CADCRAFT_CLI_DEFAULT
)

BASELINE_FIXTURE = os.path.join(REPO_ROOT, "tests", "fixtures", "sample-model.json")
ELEMENTS_FIXTURE = os.path.join(REPO_ROOT, "tests", "fixtures", "sample-model-with-elements.json")


class TestDrawingGeneratorIntegration(unittest.TestCase):
    """End-to-end integration tests for CAD generation with elements."""

    @classmethod
    def setUpClass(cls):
        cls.cli_available = os.path.exists(CADCRAFT_CLI_DEFAULT)
        cls.temp_dir = tempfile.mkdtemp(prefix="sketch_to_cad_test_")

    def test_unapproved_model_rejected_by_approval_gate(self):
        """Approval Gate: Drafting must halt if model status is not 'approved'."""
        with open(BASELINE_FIXTURE, "r", encoding="utf-8") as f:
            model = json.load(f)
        model["status"] = "awaiting_approval"

        gen = DrawingGenerator()
        with self.assertRaises(ApprovalGateError) as ctx:
            gen.validate_preflight(model)
        self.assertIn("Approval Gate Violation", str(ctx.exception))

    def test_unapproved_proposed_element_rejected(self):
        """Approval Gate: Proposed element without 'approved' status halts generation."""
        with open(ELEMENTS_FIXTURE, "r", encoding="utf-8") as f:
            model = json.load(f)
        # Change one proposed element status to 'unresolved'
        for elem in model["elements"]:
            if elem.get("source") == "proposed":
                elem["status"] = "unresolved"
                break

        gen = DrawingGenerator()
        with self.assertRaises(ApprovalGateError) as ctx:
            gen.validate_preflight(model)
        self.assertIn("requires explicit human approval", str(ctx.exception))

    def test_duplicate_element_id_rejected(self):
        """Duplicate element identifiers are rejected during preflight."""
        with open(ELEMENTS_FIXTURE, "r", encoding="utf-8") as f:
            model = json.load(f)
        # Duplicate an ID
        model["elements"].append(dict(model["elements"][0]))

        gen = DrawingGenerator()
        with self.assertRaises(ValueError) as ctx:
            gen.validate_preflight(model)
        self.assertIn("Duplicate element ID", str(ctx.exception))

    def test_unknown_block_id_rejected(self):
        """Elements referencing missing library blocks are rejected."""
        with open(ELEMENTS_FIXTURE, "r", encoding="utf-8") as f:
            model = json.load(f)
        model["elements"].append({
            "id": "E-NON-EXISTENT",
            "blockId": "FURN_MAGIC_TABLE",
            "category": "furniture",
            "position": [1000, 1000],
            "source": "explicit",
            "status": "confirmed"
        })

        gen = DrawingGenerator()
        with self.assertRaises(ValueError) as ctx:
            gen.validate_preflight(model)
        self.assertIn("Unknown blockId", str(ctx.exception))

    def test_element_outside_envelope_logs_warning(self):
        """Elements positioned outside the building envelope log a warning without crashing."""
        with open(ELEMENTS_FIXTURE, "r", encoding="utf-8") as f:
            model = json.load(f)
        # Position element outside 6000x5000 envelope
        model["elements"].append({
            "id": "E-OUTSIDE",
            "blockId": "FURN_BEDSIDE_TABLE",
            "category": "furniture",
            "position": [8500, 9200],
            "source": "explicit",
            "status": "confirmed"
        })

        gen = DrawingGenerator()
        gen.validate_preflight(model)
        self.assertTrue(any("falls outside exterior envelope" in w for w in gen.warnings))

    def test_real_cadcraft_furnished_floor_plan_generation(self):
        """GENUINE CADCraft integration: Generates a full furnished floor plan DXF + PNG and verifies entities."""
        if not self.cli_available:
            self.skipTest("CADCraft CLI binary not installed at default location.")

        with open(ELEMENTS_FIXTURE, "r", encoding="utf-8") as f:
            model = json.load(f)

        out_dxf = os.path.join(self.temp_dir, "test_furnished_plan.dxf")
        out_png = os.path.join(self.temp_dir, "test_furnished_plan.png")

        client = CADCraftClient(cli_path=CADCRAFT_CLI_DEFAULT)
        try:
            gen = DrawingGenerator(client=client)
            result = gen.build_drawing(model, out_dxf, out_png)
        finally:
            client.close()

        # 1. Check returned execution result
        self.assertEqual(result["status"], "PASSED")
        self.assertTrue(os.path.exists(out_dxf))
        self.assertTrue(os.path.exists(out_png))
        self.assertGreater(os.path.getsize(out_dxf), 10000)
        self.assertGreater(os.path.getsize(out_png), 10000)

        # 2. Check entity counts
        counts = result["counts"]
        self.assertEqual(counts.get("Block Reference"), 8, "Expected 8 block reference instances")
        self.assertEqual(counts.get("Hatch"), 1, "Expected 1 floor tile hatch entity")
        self.assertEqual(counts.get("Arc"), 2, "Expected 2 door swing arcs")
        self.assertGreaterEqual(counts.get("Line", 0), 30, "Expected at least 30 wall/opening lines")

        # 3. Check registered blocks in DXF
        blocks = result["blocks"]
        expected_blocks = [
            "FURN_BED_DOUBLE", "FURN_SOFA_2SEAT", "FIXT_TOILET",
            "FIXT_WASHBASIN", "FIXT_SHOWER", "FIXT_KITCHEN_SINK",
            "FIXT_REFRIGERATOR", "STRUC_COL_SQUARE"
        ]
        for b in expected_blocks:
            self.assertIn(b, blocks, f"Block '{b}' was not registered in CAD session")

        # 4. Check layer assignments
        layers = result["layers"]
        for lay in ["A-WALL-EXTR", "A-WALL-INTR", "A-DOOR", "A-GLAZ", "A-FURN", "A-FIXT", "A-COLS", "A-FLOR-FIN"]:
            self.assertIn(lay, layers, f"Layer '{lay}' missing from CAD drawing")

        # 5. Re-open and verify DXF file with cadcraft-cli info
        info_res = subprocess.run([CADCRAFT_CLI_DEFAULT, "info", out_dxf], capture_output=True, text=True)
        self.assertEqual(info_res.returncode, 0)
        info_data = json.loads(info_res.stdout)
        self.assertEqual(info_data["counts"]["Block Reference"], 8)
        self.assertEqual(info_data["counts"]["Hatch"], 1)

    def test_real_cadcraft_baseline_fixture_no_regression(self):
        """GENUINE CADCraft integration: Verifies unfurnished baseline model generates without regression."""
        if not self.cli_available:
            self.skipTest("CADCraft CLI binary not installed at default location.")

        with open(BASELINE_FIXTURE, "r", encoding="utf-8") as f:
            model = json.load(f)

        out_dxf = os.path.join(self.temp_dir, "test_baseline_plan.dxf")
        out_png = os.path.join(self.temp_dir, "test_baseline_plan.png")

        client = CADCraftClient(cli_path=CADCRAFT_CLI_DEFAULT)
        try:
            gen = DrawingGenerator(client=client)
            result = gen.build_drawing(model, out_dxf, out_png)
        finally:
            client.close()

        self.assertEqual(result["status"], "PASSED")
        self.assertTrue(os.path.exists(out_dxf))
        self.assertEqual(result["counts"].get("Block Reference", 0), 0)
        self.assertEqual(result["counts"].get("Hatch", 0), 0)
        self.assertGreater(result["counts"]["Line"], 25)


if __name__ == "__main__":
    unittest.main()
