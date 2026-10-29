"""
Automated Test Suite for Architectural Reports and Schedules (Milestone 5)
Verifies:
1. Rectangular room area calculations
2. Non-rectangular polygon area calculations (L-shaped room)
3. Perimeter calculations
4. Missing or incomplete room boundaries handling
5. Overlapping room detection
6. Door and window schedule compilation
7. Missing opening dimensions and null vertical parameter preservation
8. Invalid host-wall reference detection
9. Furniture and fixture quantities (aggregated and itemized)
10. Floor finish quantities and area coverage
11. Unknown material mappings (graphical hatch vs physical material)
12. Provenance and uncertainty preservation
13. Approval-gate enforcement
14. Legacy model compatibility (sample-model.json)
15. Report JSON schema validation (architectural-report.schema.json)
16. DXF / handoff / report cross-consistency
17. Multiple floor IDs handling
18. Genuine CADCraft integration test
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

from architectural_reports import (
    calculate_polygon_area,
    calculate_polygon_perimeter,
    detect_axis_aligned_rectangle,
    point_in_polygon,
    detect_polygons_overlap,
    compile_room_schedule,
    compile_opening_schedules,
    compile_element_inventory,
    compile_finish_schedule,
    compile_uncertainty_and_audit,
    compile_architectural_report,
    render_markdown_report,
    render_pdf_report,
    get_report_schema_path
)
from drawing_generator import DrawingGenerator, CADCraftClient, CADCRAFT_CLI_DEFAULT

SCHEMA_PATH = os.path.join(REPO_ROOT, "skills", "sketch-to-cad", "schemas", "architectural-report.schema.json")
FIXTURE_MINIMAL = os.path.join(REPO_ROOT, "tests", "fixtures", "sample-model.json")
FIXTURE_FURNISHED = os.path.join(REPO_ROOT, "tests", "fixtures", "sample-model-with-elements.json")


class TestArchitecturalCalculations(unittest.TestCase):
    """Unit tests for geometric and quantity calculation functions."""

    def test_01_rectangular_room_area(self):
        """Verifies Shoelace area calculation for rectangular room (4100mm x 4600mm = 18.86 m2)."""
        rect = [[200, 200], [4300, 200], [4300, 4800], [200, 4800]]
        area_mm2 = calculate_polygon_area(rect)
        area_m2 = round(area_mm2 / 1e6, 2)
        self.assertEqual(area_m2, 18.86)

    def test_02_nonrectangular_polygon_area(self):
        """Verifies Shoelace area calculation for an L-shaped room (12.00 m2)."""
        # L-shape: 4m x 2m bottom + 2m x 2m top = 8 + 4 = 12 m2
        l_shape = [[0, 0], [4000, 0], [4000, 2000], [2000, 2000], [2000, 4000], [0, 4000]]
        area_mm2 = calculate_polygon_area(l_shape)
        area_m2 = round(area_mm2 / 1e6, 2)
        self.assertEqual(area_m2, 12.00)

    def test_03_perimeter_calculation(self):
        """Verifies closed polygon perimeter calculations for rectangular and irregular shapes."""
        rect = [[200, 200], [4300, 200], [4300, 4800], [200, 4800]]
        perim_rect = calculate_polygon_perimeter(rect)
        self.assertEqual(perim_rect, 17400.0)

        l_shape = [[0, 0], [4000, 0], [4000, 2000], [2000, 2000], [2000, 4000], [0, 4000]]
        perim_l = calculate_polygon_perimeter(l_shape)
        self.assertEqual(perim_l, 16000.0)

    def test_04_missing_or_incomplete_room_boundaries(self):
        """Verifies fallback when room boundaryCorners is missing or incomplete."""
        model = {
            "rooms": [
                {"id": "R_NO_BOUND", "name": "OFFICE", "approximateArea": 14.5, "labelPosition": [1000, 1000]}
            ]
        }
        rooms_out = compile_room_schedule(model, finishes=[])
        self.assertEqual(len(rooms_out), 1)
        r = rooms_out[0]
        self.assertEqual(r["netAreaM2"], 14.5)
        self.assertEqual(r["calculationMethod"], "model_annotated")
        self.assertIsNone(r["lengthMm"])
        self.assertIsNone(r["widthMm"])
        self.assertIsNone(r["perimeterM"])

    def test_05_overlapping_rooms_detection(self):
        """Verifies detection of overlapping room polygons."""
        # Non-overlapping adjacent rooms
        r1 = [[200, 200], [4300, 200], [4300, 4800], [200, 4800]]
        r2 = [[4400, 2700], [5800, 2700], [5800, 4800], [4400, 4800]]
        self.assertFalse(detect_polygons_overlap(r1, r2))

        # Overlapping rooms
        r_overlap = [[3000, 1000], [5000, 1000], [5000, 3000], [3000, 3000]]
        self.assertTrue(detect_polygons_overlap(r1, r_overlap))

    def test_06_axis_aligned_rectangle_detection(self):
        """Ensures length x width is not manufactured for irregular polygons."""
        rect = [[200, 200], [4300, 200], [4300, 4800], [200, 4800]]
        dims = detect_axis_aligned_rectangle(rect)
        self.assertIsNotNone(dims)
        self.assertEqual(dims, (4600.0, 4100.0))

        # Non-rectangular L-shape must return None
        l_shape = [[0, 0], [4000, 0], [4000, 2000], [2000, 2000], [2000, 4000], [0, 4000]]
        self.assertIsNone(detect_axis_aligned_rectangle(l_shape))


class TestSchedulesAndReporting(unittest.TestCase):
    """Unit tests for schedule compilation, provenance, and audit logic."""

    def setUp(self):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            self.schema = json.load(f)
        with open(FIXTURE_FURNISHED, "r", encoding="utf-8") as f:
            self.model_furnished = json.load(f)
        with open(FIXTURE_MINIMAL, "r", encoding="utf-8") as f:
            self.model_minimal = json.load(f)

    def test_07_door_and_window_schedules(self):
        """Verifies compilation of separate door and window schedules."""
        doors, windows, warnings = compile_opening_schedules(self.model_furnished)
        self.assertEqual(len(doors), 2)
        self.assertEqual(len(windows), 2)
        # Door checks
        door_ids = {d["id"] for d in doors}
        self.assertIn("D-ENTR", door_ids)
        self.assertIn("D-BATH", door_ids)
        # Window checks
        win_ids = {w["id"] for w in windows}
        self.assertIn("WIN-1", win_ids)
        self.assertIn("WIN-2", win_ids)

    def test_08_missing_opening_dimensions_null_preservation(self):
        """Enforces that vertical heights remain null when unannotated in 2D."""
        doors, windows, _ = compile_opening_schedules(self.model_furnished)
        for d in doors:
            self.assertIsNone(d["heightMm"])
            self.assertGreater(d["widthMm"], 0.0)
        for w in windows:
            self.assertIsNone(w["heightMm"])
            self.assertGreater(w["widthMm"], 0.0)

    def test_09_invalid_host_wall_reference_detection(self):
        """Detects and flags openings referencing nonexistent host walls."""
        bad_model = dict(self.model_furnished)
        bad_model["openings"] = [
            {"id": "D-ORPHAN", "type": "door", "wallId": "WALL-NONEXISTENT", "center": [1000, 1000], "width": 900}
        ]
        doors, windows, warnings = compile_opening_schedules(bad_model)
        self.assertEqual(doors[0]["verificationStatus"], "invalid_host_wall")
        self.assertTrue(any("WALL-NONEXISTENT" in w for w in warnings))

    def test_10_furniture_and_fixture_quantities(self):
        """Verifies itemized instance reporting and aggregated block/category counts."""
        elem_data = compile_element_inventory(self.model_furnished)
        self.assertEqual(len(elem_data["instances"]), 8)
        # Check summary by category
        cats = {c["category"]: c["instanceCount"] for c in elem_data["summaryByCategory"]}
        self.assertEqual(cats.get("furniture"), 2)
        self.assertEqual(cats.get("sanitary"), 3)
        self.assertEqual(cats.get("kitchen"), 2)
        self.assertEqual(cats.get("structural"), 1)

    def test_11_floor_finish_quantities_and_material_mapping(self):
        """Verifies finish area calculation and warns about unspecified physical materials."""
        rooms = compile_room_schedule(self.model_furnished, self.model_furnished.get("finishes", []))
        finishes = compile_finish_schedule(self.model_furnished, rooms)
        self.assertEqual(len(finishes), 1)
        fin = finishes[0]
        self.assertEqual(fin["roomId"], "R2")
        self.assertEqual(fin["pattern"], "tile_grid")
        self.assertEqual(fin["areaCoveredM2"], 2.94)
        # Material was unspecified in fixture -> flagged
        self.assertIn("material_unspecified", fin["verificationStatus"])

    def test_12_provenance_and_uncertainty_preservation(self):
        """Verifies that all model uncertainties and provenance tags are preserved."""
        report = compile_architectural_report(self.model_furnished)
        uncs = report["uncertainties"]
        self.assertGreaterEqual(len(uncs), 2)
        # Should include vertical parameter uncertainty
        vert_unc = [u for u in uncs if u["id"] == "UNC-VERT-01"]
        self.assertEqual(len(vert_unc), 1)
        self.assertEqual(vert_unc[0]["category"], "vertical_geometry")

    def test_13_approval_gate_enforcement(self):
        """Verifies that unapproved models are flagged as DRAFT / NOT APPROVED."""
        unapproved_model = dict(self.model_furnished)
        unapproved_model["status"] = "awaiting_approval"
        report = compile_architectural_report(unapproved_model)
        self.assertEqual(report["summary"]["validationStatus"], "DRAFT")
        self.assertFalse(report["audit"]["isApprovedForConstruction"])
        self.assertTrue(any("NOT APPROVED" in f.upper() for f in report["audit"]["flags"]))

    def test_14_legacy_minimal_model_compatibility(self):
        """Verifies report compilation on minimal un-furnished sample-model.json."""
        report = compile_architectural_report(self.model_minimal)
        jsonschema.validate(instance=report, schema=self.schema)
        self.assertEqual(report["summary"]["roomCount"], 3)
        self.assertEqual(report["summary"]["doorCount"], 2)
        self.assertEqual(report["summary"]["windowCount"], 2)
        self.assertEqual(report["summary"]["elementCount"], 0)
        self.assertEqual(report["summary"]["finishCount"], 0)

    def test_15_report_json_schema_validation(self):
        """Validates that compiled report conforms 100% to architectural-report.schema.json."""
        report = compile_architectural_report(self.model_furnished)
        jsonschema.validate(instance=report, schema=self.schema)
        self.assertEqual(report["schemaVersion"], "1.0.0")
        self.assertEqual(report["project"]["drawingId"], "floor-plan")

    def test_16_multiple_floor_ids_handling(self):
        """Verifies that room and opening floor associations preserve multi-floor level IDs."""
        multi_model = dict(self.model_furnished)
        multi_model["rooms"] = [
            {"id": "R-GF-1", "name": "LIVING", "floorId": "LEVEL-01", "approximateArea": 20.0, "labelPosition": [0, 0]},
            {"id": "R-1F-1", "name": "BEDROOM", "floorId": "LEVEL-02", "approximateArea": 15.0, "labelPosition": [0, 0]}
        ]
        rooms = compile_room_schedule(multi_model, finishes=[])
        self.assertEqual(rooms[0]["floorId"], "LEVEL-01")
        self.assertEqual(rooms[1]["floorId"], "LEVEL-02")

    def test_17_markdown_and_pdf_rendering(self):
        """Verifies that markdown and PDF reports render without errors."""
        report = compile_architectural_report(self.model_furnished)
        md = render_markdown_report(report)
        self.assertIn("# Architectural Documentation & Schedules Report", md)
        self.assertIn("## 1. Executive Architectural Summary", md)
        self.assertIn("## 2. Room Area & Dimension Schedule", md)

        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = os.path.join(tmpdir, "test-report.pdf")
            render_pdf_report(report, pdf_path)
            self.assertTrue(os.path.exists(pdf_path))
            self.assertGreater(os.path.getsize(pdf_path), 5000)


class TestCADCraftIntegrationReports(unittest.TestCase):
    """Integration test running live CADCraft drawing generator with full report output."""

    @classmethod
    def setUpClass(cls):
        cls.cli_available = os.path.exists(CADCRAFT_CLI_DEFAULT)

    def setUp(self):
        if not self.cli_available:
            self.skipTest(f"CADCraft CLI not installed at {CADCRAFT_CLI_DEFAULT}")
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            self.schema = json.load(f)
        with open(FIXTURE_FURNISHED, "r", encoding="utf-8") as f:
            self.model = json.load(f)

    def test_18_genuine_cadcraft_drawing_and_report_pipeline(self):
        """Generates DXF, Handoff JSON, Report JSON, Report MD, and Report PDF in a unified run."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dxf_path = os.path.join(tmpdir, "furnished-plan.dxf")
            client = CADCraftClient(cli_path=CADCRAFT_CLI_DEFAULT)
            try:
                gen = DrawingGenerator(client=client)
                res = gen.build_drawing(
                    model=self.model,
                    output_dxf_path=dxf_path,
                    generate_report=True
                )
            finally:
                client.close()

            # Verify all deliverables exist
            self.assertTrue(os.path.exists(res["dxfPath"]))
            self.assertTrue(os.path.exists(res["handoffPath"]))
            self.assertTrue(os.path.exists(res["reportJsonPath"]))
            self.assertTrue(os.path.exists(res["reportMdPath"]))
            self.assertTrue(os.path.exists(res["reportPdfPath"]))

            # Validate report JSON
            with open(res["reportJsonPath"], "r", encoding="utf-8") as rf:
                rep_data = json.load(rf)
            jsonschema.validate(instance=rep_data, schema=self.schema)

            # Cross-consistency checks between DXF, Handoff, and Report
            with open(res["handoffPath"], "r", encoding="utf-8") as hf:
                handoff_data = json.load(hf)

            # Room count consistency
            self.assertEqual(rep_data["summary"]["roomCount"], len(handoff_data["rooms"]))
            # Element count consistency
            self.assertEqual(rep_data["summary"]["elementCount"], len(handoff_data["elements"]))
            # Door & window count consistency
            door_count = len(rep_data["openings"]["doors"])
            win_count = len(rep_data["openings"]["windows"])
            self.assertEqual(door_count + win_count, len(handoff_data["openings"]))


if __name__ == "__main__":
    unittest.main()
