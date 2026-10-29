"""
Automated Test Suite for BIM Handoff Contract (Milestone 4)
Verifies:
- bim-handoff.schema.json Draft-07 compliance.
- Complete companion JSON compilation from floor-plan models.
- Required and optional fields handling (including null vertical parameters).
- Block, layer, and category consistency between DXF metadata and JSON.
- Backward compatibility with legacy minimal sample-model.json.
- Real CADCraft DXF generation and companion JSON consistency.
"""

import os
import sys
import json
import unittest
import tempfile
import jsonschema

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.join(REPO_ROOT, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from drawing_generator import (
    DrawingGenerator,
    CADCraftClient,
    compile_bim_handoff,
    get_handoff_schema_path,
    _map_layer_category,
    _map_block_category,
    CADCRAFT_CLI_DEFAULT
)
from element_library import ELEMENT_CATALOG

SCHEMA_PATH = os.path.join(REPO_ROOT, "skills", "sketch-to-cad", "schemas", "bim-handoff.schema.json")
FIXTURE_MINIMAL = os.path.join(REPO_ROOT, "tests", "fixtures", "sample-model.json")
FIXTURE_FURNISHED = os.path.join(REPO_ROOT, "tests", "fixtures", "sample-model-with-elements.json")


class TestBIMHandoffSchema(unittest.TestCase):
    """Verifies schema validity and structure."""

    def setUp(self):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            self.schema = json.load(f)

    def test_schema_is_valid_draft07(self):
        """Verifies bim-handoff.schema.json is a valid Draft-07 JSON Schema."""
        jsonschema.Draft7Validator.check_schema(self.schema)
        self.assertEqual(self.schema.get("title"), "BIMHandoffContract")

    def test_schema_required_root_properties(self):
        """Ensures all 11 required root contract sections are defined."""
        expected_sections = [
            "schemaVersion", "project", "dxf", "floors", "walls",
            "openings", "rooms", "elements", "finishes", "uncertainties", "validation"
        ]
        for section in expected_sections:
            self.assertIn(section, self.schema.get("required", []))


class TestBIMHandoffCompilerUnit(unittest.TestCase):
    """Unit tests for compile_bim_handoff without live CADCraft subprocess."""

    def setUp(self):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            self.schema = json.load(f)
        with open(FIXTURE_FURNISHED, "r", encoding="utf-8") as f:
            self.model_furnished = json.load(f)
        with open(FIXTURE_MINIMAL, "r", encoding="utf-8") as f:
            self.model_minimal = json.load(f)

    def test_layer_category_mapping(self):
        """Verifies CAD layer to BIM category mapping."""
        self.assertEqual(_map_layer_category("A-WALL-EXTR"), "walls")
        self.assertEqual(_map_layer_category("A-WALL-INTR"), "walls")
        self.assertEqual(_map_layer_category("A-DOOR"), "doors")
        self.assertEqual(_map_layer_category("A-GLAZ"), "glazing")
        self.assertEqual(_map_layer_category("A-FURN"), "furniture")
        self.assertEqual(_map_layer_category("A-FIXT"), "fixtures")
        self.assertEqual(_map_layer_category("A-STAIR"), "circulation")
        self.assertEqual(_map_layer_category("A-COLS"), "structure")
        self.assertEqual(_map_layer_category("A-FLOR-FIN"), "finishes")
        self.assertEqual(_map_layer_category("A-ANNO-TEXT"), "annotations")
        self.assertEqual(_map_layer_category("A-ANNO-DIMS"), "annotations")
        self.assertEqual(_map_layer_category("0"), "system")

    def test_block_category_mapping(self):
        """Verifies block ID to element category mapping."""
        self.assertEqual(_map_block_category("BED-DOUBLE"), "furniture")
        self.assertEqual(_map_block_category("TOILET-STD"), "sanitary")
        self.assertEqual(_map_block_category("KITCHEN-SINK"), "kitchen")
        self.assertEqual(_map_block_category("STAIR-STRAIGHT"), "circulation")
        self.assertEqual(_map_block_category("COL-SQUARE-300"), "structural")

    def test_compile_furnished_model(self):
        """Verifies handoff compilation of furnished model against schema."""
        mock_inspection = {
            "entityCount": 62,
            "counts": {"LINE": 46, "ARC": 4, "INSERT": 8, "HATCH": 1, "TEXT": 3},
            "blocks": ["BED-DOUBLE", "NIGHTSTAND", "WARDROBE-STD", "SOFA-2SEAT", "DINING-4SEAT", "TOILET-STD", "BASIN-STD", "KITCHEN-SINK"],
            "layers": [
                {"name": "A-WALL-EXTR", "color": "cyan", "count": 16},
                {"name": "A-WALL-INTR", "color": "green", "count": 8}
            ],
            "extents": [[-500.0, -500.0], [6500.0, 5500.0]],
            "layer0Empty": True
        }
        handoff = compile_bim_handoff(
            model=self.model_furnished,
            dxf_path="sample.dxf",
            inspection=mock_inspection
        )
        jsonschema.validate(instance=handoff, schema=self.schema)

        # Check core attributes
        self.assertEqual(handoff["schemaVersion"], "1.0.0")
        self.assertEqual(handoff["project"]["units"], "mm")
        self.assertEqual(handoff["project"]["coordinateSystem"], "Cartesian2D_RightHanded_YUp")
        self.assertEqual(len(handoff["floors"]), 1)
        self.assertEqual(handoff["floors"][0]["id"], "LEVEL-01")
        # Elevation and height must be null (unverified in 2D)
        self.assertIsNone(handoff["floors"][0]["elevation"])
        self.assertIsNone(handoff["floors"][0]["height"])
        self.assertEqual(len(handoff["elements"]), 8)
        self.assertEqual(len(handoff["finishes"]), 1)
        self.assertEqual(handoff["validation"]["status"], "PASSED")
        self.assertTrue(handoff["validation"]["isApproved"])

    def test_backward_compatibility_minimal_model(self):
        """Verifies backward compatibility with minimal un-furnished sample-model.json."""
        handoff = compile_bim_handoff(
            model=self.model_minimal,
            dxf_path="minimal.dxf"
        )
        jsonschema.validate(instance=handoff, schema=self.schema)
        self.assertEqual(len(handoff["walls"]), 6)
        self.assertEqual(len(handoff["openings"]), 4)
        self.assertEqual(len(handoff["elements"]), 0)
        self.assertEqual(len(handoff["finishes"]), 0)
        self.assertEqual(len(handoff["uncertainties"]), 2)

    def test_unverified_vertical_parameters_are_null(self):
        """Enforces that storey elevations and wall/opening heights default to null in 2D handoff."""
        handoff = compile_bim_handoff(
            model=self.model_furnished,
            dxf_path="test.dxf"
        )
        # Storey elevation and height
        self.assertIsNone(handoff["floors"][0]["elevation"])
        self.assertIsNone(handoff["floors"][0]["height"])
        # Opening heights (unless explicitly in model)
        for op in handoff["openings"]:
            self.assertIn("height", op)
            # Default in 2D model is None
            if "height" not in self.model_furnished["openings"][0]:
                self.assertIsNone(op["height"])

    def test_opening_wall_hosting_relationships(self):
        """Verifies opening host-wall association integrity."""
        handoff = compile_bim_handoff(
            model=self.model_furnished,
            dxf_path="test.dxf"
        )
        wall_ids = {w["id"] for w in handoff["walls"]}
        for op in handoff["openings"]:
            self.assertIn("wallId", op)
            self.assertIn(op["wallId"], wall_ids, f"Opening {op['id']} hosted on nonexistent wall {op['wallId']}")


class TestBIMHandoffCADCraftIntegration(unittest.TestCase):
    """Integration test using genuine CADCraft CLI to generate both DXF and companion handoff JSON."""

    @classmethod
    def setUpClass(cls):
        cls.cli_available = os.path.exists(CADCRAFT_CLI_DEFAULT)
        if not cls.cli_available:
            print(f"[SKIP] CADCraft CLI not found at '{CADCRAFT_CLI_DEFAULT}'.")

    def setUp(self):
        if not self.cli_available:
            self.skipTest(f"CADCraft CLI not installed at {CADCRAFT_CLI_DEFAULT}")
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            self.schema = json.load(f)
        with open(FIXTURE_FURNISHED, "r", encoding="utf-8") as f:
            self.model = json.load(f)

    def test_genuine_cadcraft_dxf_and_handoff_consistency(self):
        """Builds a real drawing via CADCraft and verifies consistency between DXF and handoff JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dxf_path = os.path.join(tmpdir, "furnished-plan.dxf")
            handoff_path = os.path.join(tmpdir, "furnished-plan.handoff.json")

            client = CADCraftClient(cli_path=CADCRAFT_CLI_DEFAULT)
            try:
                gen = DrawingGenerator(client=client)
                res = gen.build_drawing(
                    model=self.model,
                    output_dxf_path=dxf_path,
                    output_handoff_path=handoff_path
                )
            finally:
                client.close()

            # 1. Verify files exist on disk
            self.assertTrue(os.path.exists(dxf_path), "DXF was not generated.")
            self.assertTrue(os.path.exists(handoff_path), "Handoff JSON was not generated.")
            self.assertGreater(os.path.getsize(dxf_path), 5000, "DXF file too small.")

            # 2. Validate companion JSON against schema
            with open(handoff_path, "r", encoding="utf-8") as f:
                handoff_data = json.load(f)
            jsonschema.validate(instance=handoff_data, schema=self.schema)

            # 3. Verify cross-consistency between DXF inspection and JSON
            self.assertEqual(handoff_data["dxf"]["filename"], "furnished-plan.dxf")
            self.assertEqual(handoff_data["dxf"]["entityCount"], res["entityCount"])
            self.assertGreater(res["entityCount"], 40)

            # Block instances check
            self.assertEqual(len(handoff_data["elements"]), len(self.model["elements"]))
            dxf_block_count = sum(b.get("instanceCount", 0) for b in handoff_data["dxf"]["blocks"])
            self.assertEqual(dxf_block_count, len(self.model["elements"]))

            # Finishes check
            self.assertEqual(len(handoff_data["finishes"]), len(self.model["finishes"]))

            # Layer names match
            dxf_layers = {l["name"] for l in handoff_data["dxf"]["layers"]}
            self.assertIn("A-WALL-EXTR", dxf_layers)
            self.assertIn("A-FURN", dxf_layers)
            self.assertIn("A-FIXT", dxf_layers)
            self.assertIn("A-FLOR-FIN", dxf_layers)

            # Validation block status
            self.assertEqual(handoff_data["validation"]["status"], "PASSED")
            self.assertTrue(handoff_data["validation"]["entityIntegrity"]["layer0Empty"])


if __name__ == "__main__":
    unittest.main()
