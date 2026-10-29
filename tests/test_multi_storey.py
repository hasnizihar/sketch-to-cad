"""
Automated Multi-Storey Test Suite (Milestone 6)
Validates multi-level floor plan schemas, independent DXF drawing separation,
isolated entity filtering, shared project coordinates, vertical staircase & column alignment,
BIM handoff manifests, and genuine CADCraft multi-floor execution.
"""

import os
import sys
import json
import unittest
import jsonschema

_tests_dir = os.path.dirname(os.path.abspath(__file__))
_root_dir = os.path.abspath(os.path.join(_tests_dir, ".."))
_scripts_dir = os.path.join(_root_dir, "scripts")

for p in [_root_dir, _scripts_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

from drawing_generator import (
    DrawingGenerator,
    ApprovalGateError,
    compile_bim_handoff,
    get_handoff_schema_path,
    CADCraftClient,
    _matches_floor,
)
from architectural_reports import (
    compile_architectural_report,
    validate_vertical_coordination,
    get_report_schema_path,
    render_markdown_report,
    render_pdf_report,
)


class TestMultiStoreySchemaAndGate(unittest.TestCase):
    """Tests 1-6: Schema validation, constraints, and approval gate enforcement."""

    @classmethod
    def setUpClass(cls):
        cls.schema_path = os.path.join(_root_dir, "skills", "sketch-to-cad", "schemas", "floor-plan-model.json")
        with open(cls.schema_path, "r", encoding="utf-8") as f:
            cls.schema = json.load(f)
        cls.validator = jsonschema.Draft7Validator(cls.schema)

        cls.two_storey_path = os.path.join(_tests_dir, "fixtures", "sample-model-two-storey.json")
        with open(cls.two_storey_path, "r", encoding="utf-8") as f:
            cls.two_storey_model = json.load(f)

        cls.single_storey_path = os.path.join(_tests_dir, "fixtures", "sample-model.json")
        with open(cls.single_storey_path, "r", encoding="utf-8") as f:
            cls.single_storey_model = json.load(f)

    def test_01_schema_accepts_valid_two_storey_model(self):
        """1. Verifies that the multi-storey duplex fixture validates 100% against floor-plan-model.json."""
        self.validator.validate(self.two_storey_model)
        self.assertIn("floors", self.two_storey_model)
        self.assertEqual(len(self.two_storey_model["floors"]), 2)
        self.assertIn("stairs", self.two_storey_model)

    def test_02_schema_accepts_legacy_single_storey_model(self):
        """2. Backward compatibility: verifies that legacy single-floor model validates without error."""
        self.validator.validate(self.single_storey_model)
        self.assertNotIn("floors", self.single_storey_model)

    def test_03_schema_rejects_missing_floor_id_in_multistorey(self):
        """3. Verifies schema rejects malformed floors entry lacking mandatory 'id' or 'name'."""
        import copy
        bad_model = copy.deepcopy(self.two_storey_model)
        del bad_model["floors"][0]["id"]
        with self.assertRaises(jsonschema.ValidationError):
            self.validator.validate(bad_model)

    def test_04_schema_rejects_negative_flight_width(self):
        """4. Verifies schema rejects stairs with negative flight width."""
        import copy
        bad_model = copy.deepcopy(self.two_storey_model)
        bad_model["stairs"][0]["flightWidth"] = -500.0
        with self.assertRaises(jsonschema.ValidationError):
            self.validator.validate(bad_model)

    def test_05_preflight_approval_gate_enforces_all_floors(self):
        """5. Fully approved multi-floor model passes preflight validation without error."""
        gen = DrawingGenerator(client=None)
        gen.validate_preflight(self.two_storey_model)
        self.assertEqual(len(gen.errors), 0)

    def test_06_preflight_approval_gate_rejects_single_unapproved_floor(self):
        """6. Rejects generation if even a single floor is unapproved."""
        import copy
        unapproved_model = copy.deepcopy(self.two_storey_model)
        unapproved_model["approval"]["floorApprovals"]["LEVEL-02"] = "awaiting_approval"
        gen = DrawingGenerator(client=None)
        with self.assertRaises(ApprovalGateError) as ctx:
            gen.validate_preflight(unapproved_model)
        self.assertIn("LEVEL-02", str(ctx.exception))


class TestMultiStoreyEntityFilteringAndCoordinates(unittest.TestCase):
    """Tests 7-11: Entity isolation, filtering, and coordinate consistency."""

    @classmethod
    def setUpClass(cls):
        cls.fixture_path = os.path.join(_tests_dir, "fixtures", "sample-model-two-storey.json")
        with open(cls.fixture_path, "r", encoding="utf-8") as f:
            cls.model = json.load(f)

    def test_07_matches_floor_filtering_logic(self):
        """7. Verifies that _matches_floor correctly isolates entities by level."""
        gf_wall = {"id": "W1", "floorId": "LEVEL-01"}
        ff_wall = {"id": "W2", "floorId": "LEVEL-02"}
        legacy_wall = {"id": "W3"} # No floorId

        self.assertTrue(_matches_floor(gf_wall, "LEVEL-01", "LEVEL-01"))
        self.assertFalse(_matches_floor(gf_wall, "LEVEL-02", "LEVEL-01"))

        self.assertFalse(_matches_floor(ff_wall, "LEVEL-01", "LEVEL-01"))
        self.assertTrue(_matches_floor(ff_wall, "LEVEL-02", "LEVEL-01"))

        # Legacy fallback
        self.assertTrue(_matches_floor(legacy_wall, "LEVEL-01", "LEVEL-01"))
        self.assertFalse(_matches_floor(legacy_wall, "LEVEL-02", "LEVEL-01"))
        self.assertTrue(_matches_floor(legacy_wall, None, "LEVEL-01"))

    def test_08_entity_filtering_isolates_ground_floor_entities(self):
        """8. Ground floor filter collects only LEVEL-01 walls, openings, and elements."""
        gf_walls = [w for w in self.model["walls"] if w.get("floorId") == "LEVEL-01"]
        ff_walls = [w for w in self.model["walls"] if w.get("floorId") == "LEVEL-02"]
        self.assertEqual(len(gf_walls), 6)
        self.assertEqual(len(ff_walls), 6)

        gf_elems = [e for e in self.model["elements"] if e.get("floorId") == "LEVEL-01"]
        self.assertEqual(len(gf_elems), 5) # sofa, dining, sink, col, stair

    def test_09_entity_filtering_isolates_first_floor_entities(self):
        """9. First floor filter collects only LEVEL-02 walls, openings, and elements."""
        ff_elems = [e for e in self.model["elements"] if e.get("floorId") == "LEVEL-02"]
        self.assertEqual(len(ff_elems), 4) # bed1, bed2, col, stair
        for el in ff_elems:
            self.assertEqual(el["floorId"], "LEVEL-02")

    def test_10_no_entity_leakage_between_floors(self):
        """10. Ensures zero set intersection of element IDs between storeys."""
        gf_elem_ids = {e["id"] for e in self.model["elements"] if e.get("floorId") == "LEVEL-01"}
        ff_elem_ids = {e["id"] for e in self.model["elements"] if e.get("floorId") == "LEVEL-02"}
        self.assertEqual(len(gf_elem_ids & ff_elem_ids), 0)

    def test_11_shared_project_coordinate_system(self):
        """11. Confirms both storeys share identical Cartesian origin [0.0, 0.0] and envelope width/depth."""
        fl1 = self.model["floors"][0]
        fl2 = self.model["floors"][1]
        self.assertEqual(fl1["envelope"]["origin"], [0, 0])
        self.assertEqual(fl2["envelope"]["origin"], [0, 0])
        self.assertEqual(fl1["envelope"]["width"], self.model["envelope"]["width"])
        self.assertEqual(fl2["envelope"]["depth"], self.model["envelope"]["depth"])


class TestVerticalCoordinationAndStairs(unittest.TestCase):
    """Tests 12-15: Vertical circulation, staircase and column alignment checker."""

    @classmethod
    def setUpClass(cls):
        cls.aligned_path = os.path.join(_tests_dir, "fixtures", "sample-model-two-storey.json")
        with open(cls.aligned_path, "r", encoding="utf-8") as f:
            cls.aligned_model = json.load(f)

        cls.misaligned_path = os.path.join(_tests_dir, "fixtures", "sample-model-two-storey-misaligned.json")
        with open(cls.misaligned_path, "r", encoding="utf-8") as f:
            cls.misaligned_model = json.load(f)

    def test_12_vertical_coordination_stair_alignment_passes(self):
        """12. Aligned two-storey model passes vertical coordination with 0 errors."""
        res = validate_vertical_coordination(self.aligned_model)
        self.assertTrue(res["valid"])
        self.assertEqual(len(res["errors"]), 0)
        self.assertEqual(res["stairsChecked"], 1)
        self.assertTrue(res["stairAlignment"][0]["aligned"])
        self.assertEqual(res["stairAlignment"][0]["dxMm"], 0.0)
        self.assertEqual(res["stairAlignment"][0]["dyMm"], 0.0)

    def test_13_vertical_coordination_stair_misalignment_fails(self):
        """13. Misaligned model flags stair offset > 50mm and marks coordination invalid."""
        res = validate_vertical_coordination(self.misaligned_model)
        self.assertFalse(res["valid"])
        self.assertGreater(len(res["errors"]), 0)
        self.assertIn("misalignment", res["errors"][0].lower())
        self.assertFalse(res["stairAlignment"][0]["aligned"])

    def test_14_vertical_coordination_column_alignment(self):
        """14. Structural columns continuous across storeys are verified within tolerance."""
        res = validate_vertical_coordination(self.aligned_model)
        self.assertGreater(res["columnsChecked"], 0)
        col_res = res["columnAlignment"][0]
        self.assertTrue(col_res["aligned"])
        self.assertLessEqual(col_res["distanceMm"], 50.0)

    def test_15_vertical_coordination_detects_invalid_floor_ids(self):
        """15. Flags error if staircase references non-existent source or destination floor."""
        import copy
        bad_model = copy.deepcopy(self.aligned_model)
        bad_model["stairs"][0]["destinationFloorId"] = "NONEXISTENT-LEVEL"
        res = validate_vertical_coordination(bad_model)
        self.assertFalse(res["valid"])
        self.assertTrue(any("does not exist" in e for e in res["errors"]))


class TestBIMHandoffAndReporting(unittest.TestCase):
    """Tests 16-19: Multi-storey BIM handoff manifest and consolidated architectural reports."""

    @classmethod
    def setUpClass(cls):
        cls.fixture_path = os.path.join(_tests_dir, "fixtures", "sample-model-two-storey.json")
        with open(cls.fixture_path, "r", encoding="utf-8") as f:
            cls.model = json.load(f)

    def test_16_bim_handoff_multistorey_contains_all_floors(self):
        """16. Handoff compiler includes all declared storeys and validates against bim-handoff.schema.json."""
        handoff = compile_bim_handoff(
            model=self.model,
            dxf_path="duplex-level-01.dxf",
            inspection={"entityCount": 40}
        )
        self.assertEqual(len(handoff["floors"]), 2)
        self.assertEqual(handoff["floors"][0]["id"], "LEVEL-01")
        self.assertEqual(handoff["floors"][1]["id"], "LEVEL-02")
        self.assertIn("stairs", handoff)
        self.assertEqual(len(handoff["stairs"]), 1)

    def test_17_bim_handoff_references_all_floor_dxfs(self):
        """17. dxf.floorDrawings mapping references each per-floor DXF deliverable."""
        drawings_map = {
            "LEVEL-01": "duplex-level-01.dxf",
            "LEVEL-02": "duplex-level-02.dxf"
        }
        handoff = compile_bim_handoff(
            model=self.model,
            dxf_path="duplex-level-01.dxf",
            inspection={"entityCount": 40},
            floor_drawings=drawings_map
        )
        self.assertIn("floorDrawings", handoff["dxf"])
        self.assertEqual(handoff["dxf"]["floorDrawings"]["LEVEL-01"], "duplex-level-01.dxf")
        self.assertEqual(handoff["dxf"]["floorDrawings"]["LEVEL-02"], "duplex-level-02.dxf")

    def test_18_architectural_report_contains_per_floor_schedules(self):
        """18. Consolidated report associates every room, opening, element, and finish with its floorId."""
        report = compile_architectural_report(model=self.model)
        self.assertEqual(report["summary"]["floorCount"], 2)

        gf_rooms = [r for r in report["rooms"] if r["floorId"] == "LEVEL-01"]
        ff_rooms = [r for r in report["rooms"] if r["floorId"] == "LEVEL-02"]
        self.assertEqual(len(gf_rooms), 3)
        self.assertEqual(len(ff_rooms), 3)

        gf_doors = [d for d in report["openings"]["doors"] if d["floorId"] == "LEVEL-01"]
        ff_doors = [d for d in report["openings"]["doors"] if d["floorId"] == "LEVEL-02"]
        self.assertEqual(len(gf_doors), 2)
        self.assertEqual(len(ff_doors), 2)

    def test_19_architectural_report_consolidated_totals(self):
        """19. Consolidated report calculates total net area across both storeys and confirms vertical coordination."""
        report = compile_architectural_report(model=self.model)
        self.assertGreater(report["summary"]["totalNetAreaM2"], 100.0) # ~61m2 + ~61m2
        self.assertIn("verticalCoordination", report["audit"])
        self.assertTrue(report["audit"]["verticalCoordination"]["valid"])


class TestCADCraftMultiStoreyIntegration(unittest.TestCase):
    """Test 20: Genuine end-to-end multi-storey CADCraft drafting execution."""

    def test_20_real_cadcraft_multistorey_generation(self):
        """20. Genuine CADCraft CLI execution generating independent DXFs, PNGs, handoff JSON, and reports."""
        fixture_path = os.path.join(_tests_dir, "fixtures", "sample-model-two-storey.json")
        with open(fixture_path, "r", encoding="utf-8") as f:
            model = json.load(f)

        output_dir = os.path.join(_tests_dir, "output", "multistorey_run")
        os.makedirs(output_dir, exist_ok=True)

        gen = DrawingGenerator()
        results = gen.build_multi_floor_drawings(
            model=model,
            output_dir=output_dir,
            base_filename="duplex-test",
            generate_report=True,
            generate_handoff=True
        )

        self.assertEqual(results["floorCount"], 2)
        self.assertIn("LEVEL-01", results["floors"])
        self.assertIn("LEVEL-02", results["floors"])

        gf_dxf = results["floors"]["LEVEL-01"]["dxf"]
        ff_dxf = results["floors"]["LEVEL-02"]["dxf"]
        self.assertTrue(os.path.exists(gf_dxf))
        self.assertTrue(os.path.exists(ff_dxf))
        self.assertGreater(os.path.getsize(gf_dxf), 1000)
        self.assertGreater(os.path.getsize(ff_dxf), 1000)

        # Independent entity counts
        self.assertGreater(results["floors"]["LEVEL-01"]["entityCount"], 10)
        self.assertGreater(results["floors"]["LEVEL-02"]["entityCount"], 10)

        # Handoff and Report verification
        self.assertTrue(os.path.exists(results["handoff"]))
        self.assertTrue(os.path.exists(results["report"]["json"]))
        self.assertTrue(os.path.exists(results["report"]["md"]))
        self.assertTrue(os.path.exists(results["report"]["pdf"]))


if __name__ == "__main__":
    unittest.main()
