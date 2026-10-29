"""
Comprehensive Test Suite for Sketch-to-CAD Architectural Element Library
Validates block definitions, metadata, schema conformance, placement rules, and CADCraft integration.
"""

import os
import sys
import json
import unittest
import jsonschema

# Add repository root and scripts to python path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.join(REPO_ROOT, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from element_library import (
    ELEMENT_CATALOG,
    ELEMENT_LAYERS,
    get_element_definition,
    list_catalog_elements,
    validate_element_instance,
    register_cad_block,
    insert_cad_element,
    create_floor_finish_hatch,
)

SCHEMA_PATH = os.path.join(REPO_ROOT, "skills", "sketch-to-cad", "schemas", "floor-plan-model.json")
BASELINE_FIXTURE = os.path.join(REPO_ROOT, "tests", "fixtures", "sample-model.json")
ELEMENTS_FIXTURE = os.path.join(REPO_ROOT, "tests", "fixtures", "sample-model-with-elements.json")


class TestArchitecturalElementCatalog(unittest.TestCase):
    """Test element catalog integrity, metadata, layers, and geometry definitions."""

    def test_catalog_minimum_element_count(self):
        """Verify the catalog contains all required core residential element types."""
        self.assertGreaterEqual(len(ELEMENT_CATALOG), 18)

    def test_all_elements_have_valid_metadata(self):
        """Verify every element definition has required fields, positive dimensions, and base point [0, 0]."""
        required_keys = ["id", "name", "category", "layer", "default_width", "default_depth", "base_point", "primitives"]
        valid_categories = {"furniture", "sanitary", "kitchen", "circulation", "structural"}
        valid_layers = {"A-FURN", "A-FIXT", "A-STAIR", "A-COLS", "A-FLOR-FIN"}

        for elem_id, elem in ELEMENT_CATALOG.items():
            for key in required_keys:
                self.assertIn(key, elem, f"Element '{elem_id}' missing required key '{key}'")

            self.assertIn(elem["category"], valid_categories, f"Element '{elem_id}' has invalid category '{elem['category']}'")
            self.assertIn(elem["layer"], valid_layers, f"Element '{elem_id}' has invalid layer '{elem['layer']}'")
            self.assertGreater(elem["default_width"], 0, f"Element '{elem_id}' default_width must be positive")
            self.assertGreater(elem["default_depth"], 0, f"Element '{elem_id}' default_depth must be positive")
            self.assertEqual(elem["base_point"], [0.0, 0.0], f"Element '{elem_id}' base_point must be [0.0, 0.0]")
            self.assertIsInstance(elem["primitives"], list)
            self.assertGreater(len(elem["primitives"]), 0, f"Element '{elem_id}' must define at least one primitive")

    def test_element_category_filtering(self):
        """Verify catalog filtering by category returns the correct subsets."""
        furniture = list_catalog_elements("furniture")
        sanitary = list_catalog_elements("sanitary")
        kitchen = list_catalog_elements("kitchen")
        circulation = list_catalog_elements("circulation")
        structural = list_catalog_elements("structural")

        self.assertGreaterEqual(len(furniture), 8)
        self.assertGreaterEqual(len(sanitary), 4)
        self.assertGreaterEqual(len(kitchen), 4)
        self.assertGreaterEqual(len(circulation), 2)
        self.assertGreaterEqual(len(structural), 2)

        for f in furniture:
            self.assertEqual(f["category"], "furniture")
            self.assertEqual(f["layer"], "A-FURN")

        for s in sanitary:
            self.assertEqual(s["category"], "sanitary")
            self.assertEqual(s["layer"], "A-FIXT")

        for k in kitchen:
            self.assertEqual(k["category"], "kitchen")
            self.assertEqual(k["layer"], "A-FIXT")


class TestElementInstanceValidation(unittest.TestCase):
    """Test validation logic for element placement requests."""

    def test_valid_instance(self):
        """Valid element passes validation with zero errors."""
        inst = {
            "id": "E-BED-1",
            "blockId": "FURN_BED_DOUBLE",
            "category": "furniture",
            "position": [2000, 3000],
            "rotation": 90.0,
            "scale": 1.0,
            "source": "explicit",
            "status": "confirmed"
        }
        valid, errors = validate_element_instance(inst)
        self.assertTrue(valid)
        self.assertEqual(errors, [])

    def test_unknown_block_id_rejected(self):
        """Unknown blockId is caught and reported."""
        inst = {
            "id": "E-INVALID-1",
            "blockId": "FURN_NON_EXISTENT",
            "category": "furniture",
            "position": [1000, 1000],
            "source": "explicit"
        }
        valid, errors = validate_element_instance(inst)
        self.assertFalse(valid)
        self.assertTrue(any("Unknown blockId" in err for err in errors))

    def test_category_mismatch_rejected(self):
        """Declaring sanitary fixture under furniture category is rejected."""
        inst = {
            "id": "E-MISMATCH",
            "blockId": "FIXT_TOILET",
            "category": "furniture",  # Mismatch: FIXT_TOILET is sanitary
            "position": [1000, 1000],
            "source": "explicit"
        }
        valid, errors = validate_element_instance(inst)
        self.assertFalse(valid)
        self.assertTrue(any("Category mismatch" in err for err in errors))

    def test_invalid_position_coordinates(self):
        """Non-numeric or malformed positions are rejected."""
        inst = {
            "id": "E-BAD-POS",
            "blockId": "FURN_SOFA_2SEAT",
            "category": "furniture",
            "position": ["1000", 2000],  # string instead of number
            "source": "explicit"
        }
        valid, errors = validate_element_instance(inst)
        self.assertFalse(valid)

    def test_negative_scale_rejected(self):
        """Negative or zero scale is rejected."""
        inst = {
            "id": "E-BAD-SCALE",
            "blockId": "FURN_SOFA_2SEAT",
            "category": "furniture",
            "position": [1000, 2000],
            "scale": -1.0,
            "source": "explicit"
        }
        valid, errors = validate_element_instance(inst)
        self.assertFalse(valid)
        self.assertTrue(any("Scale must be strictly positive" in err for err in errors))

    def test_unapproved_proposed_element_rejected(self):
        """Proposed element without explicit approval is halted at approval gate."""
        inst = {
            "id": "E-PROP-1",
            "blockId": "FURN_TV_UNIT",
            "category": "furniture",
            "position": [1500, 2500],
            "source": "proposed",
            "status": "unresolved"  # Must be 'approved' to draft
        }
        valid, errors = validate_element_instance(inst)
        self.assertFalse(valid)
        self.assertTrue(any("requires explicit human approval" in err for err in errors))


class TestFloorPlanModelSchemaCompatibility(unittest.TestCase):
    """Test that schema updates maintain 100% backward compatibility while supporting elements."""

    @classmethod
    def setUpClass(cls):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            cls.schema = json.load(f)

    def test_baseline_fixture_validates(self):
        """Regression protection: original sample-model.json must validate cleanly."""
        with open(BASELINE_FIXTURE, "r", encoding="utf-8") as f:
            model = json.load(f)
        # Should not raise ValidationError
        jsonschema.validate(instance=model, schema=self.schema)

    def test_elements_fixture_validates(self):
        """Verify sample-model-with-elements.json validates against schema."""
        with open(ELEMENTS_FIXTURE, "r", encoding="utf-8") as f:
            model = json.load(f)
        jsonschema.validate(instance=model, schema=self.schema)
        self.assertIn("elements", model)
        self.assertIn("finishes", model)
        self.assertEqual(len(model["elements"]), 8)
        self.assertEqual(len(model["finishes"]), 1)


class TestMockedCADCraftBlockWorkflow(unittest.TestCase):
    """Unit test CAD block registration and insertion using mocked MCP execution calls."""

    def test_block_registration_and_insertion(self):
        commands_called = []
        handle_counter = 100

        def mock_execute(command, params):
            nonlocal handle_counter
            commands_called.append({"command": command, "params": params})
            if command in ("line", "rectang", "circle"):
                handle_counter += 1
                return {"handle": hex(handle_counter)}
            if command == "block":
                return {"block": params["name"]}
            if command == "insert":
                handle_counter += 1
                return {"handle": hex(handle_counter)}
            return None

        # 1. Register block
        res_reg = register_cad_block(mock_execute, "FURN_BED_DOUBLE")
        self.assertEqual(res_reg["status"], "created")
        self.assertEqual(res_reg["block"], "FURN_BED_DOUBLE")

        # 2. Re-register should skip when existing_blocks is provided
        res_skip = register_cad_block(mock_execute, "FURN_BED_DOUBLE", existing_blocks=["FURN_BED_DOUBLE"])
        self.assertEqual(res_skip["status"], "already_registered")

        # 3. Insert element instance
        res_ins = insert_cad_element(
            mock_execute,
            "FURN_BED_DOUBLE",
            at=[2000.0, 3000.0],
            rotation=90.0,
            scale=1.0,
            existing_blocks=["FURN_BED_DOUBLE"]
        )
        self.assertIn("handle", res_ins)

        # Verify command sequence
        cmds = [c["command"] for c in commands_called]
        self.assertIn("layer.current", cmds)
        self.assertIn("block", cmds)
        self.assertIn("insert", cmds)


class TestRealCADCraftCLIIntegration(unittest.TestCase):
    """Real integration test against CADCraft CLI engine (if installed)."""

    def setUp(self):
        self.cli_path = r"C:\Program Files\CADCraft\cadcraft-cli.exe"
        if not os.path.exists(self.cli_path):
            self.skipTest(f"CADCraft CLI binary not found at {self.cli_path}")

    def test_real_cadcraft_block_generation_and_export(self):
        import tempfile
        import subprocess

        temp_dir = tempfile.gettempdir()
        dxf_path = os.path.join(temp_dir, "test_cadcraft_element_integration.dxf")

        commands = [
            "layer.new " + json.dumps({"name": "A-FURN", "color": "green"}),
            "layer.new " + json.dumps({"name": "A-FIXT", "color": "8"}),
            "layer.new " + json.dumps({"name": "A-COLS", "color": "cyan"}),
            "line " + json.dumps({"points": [[0, 0], [1800, 0], [1800, 2000], [0, 2000]], "closed": True}),
            "block " + json.dumps({"name": "FURN_BED_DOUBLE", "base": [0, 0], "handles": ["100", "101", "102", "103"], "keep": "delete"}),
            "insert " + json.dumps({"name": "FURN_BED_DOUBLE", "at": [1000, 1000], "rotation": 90.0}),
        ]

        cmd_args = [self.cli_path, "run", "--metric"]
        for c in commands:
            cmd_args.extend(["--cmd", c])
        cmd_args.extend(["--save", dxf_path])

        res = subprocess.run(cmd_args, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"CADCraft CLI execution failed:\nStdout: {res.stdout}\nStderr: {res.stderr}")
        self.assertTrue(os.path.exists(dxf_path))
        self.assertGreater(os.path.getsize(dxf_path), 0)

        # Inspect exported DXF with cadcraft-cli info
        info_res = subprocess.run([self.cli_path, "info", dxf_path], capture_output=True, text=True)
        self.assertEqual(info_res.returncode, 0)
        info_data = json.loads(info_res.stdout)
        self.assertIn("FURN_BED_DOUBLE", info_data.get("blocks", []))
        self.assertEqual(info_data.get("counts", {}).get("Block Reference"), 1)

        if os.path.exists(dxf_path):
            os.remove(dxf_path)


if __name__ == "__main__":
    unittest.main()
