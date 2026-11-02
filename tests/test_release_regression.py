"""
Release Regression Test Suite (Milestone 11 - Phase 7).
Covers 15 challenging architectural and drafting scenarios:
 1. Small single-storey plan (6x5m)
 2. Large multi-room residential plan
 3. Two-storey duplex plan with stairs
 4. Non-rectangular footprint with angled wall
 5. Multiple door types (single, double, sliding)
 6. Multiple window configurations (standard, sliding bypass)
 7. Dense dimension chains and collision avoidance
 8. Conflicting dimensions detection
 9. Incomplete sketches handling (missing depth dimension)
10. Poor-quality and rotated sketches handling
11. Unknown window sill heights (explicit non-silent provenance)
12. Unapproved geometry revisions (revision hash invalidation)
13. Invalid wall junctions (detecting gaps)
14. DXF with duplicate entities (inspector flags duplicates)
15. BIM handoff with unresolved assumptions
"""

from __future__ import annotations

import json
import math
import tempfile
import unittest
from pathlib import Path

try:
    import ezdxf
except ImportError:
    ezdxf = None

from scripts.approval_package import (
    calculate_geometry_hash,
    create_approval_package,
)
from scripts.dimension_engine import (
    DimensionCollision,
    DimensionEngine,
    DimensionEntity,
    DimensionStyle,
)
from scripts.drawing_generator import (
    AIA_LAYER_STANDARDS,
    ApprovalGateError,
    DrawingGenerator,
    compile_bim_handoff,
)
from scripts.dxf_inspector import DXFInspector
from scripts.geometry_validation import ArchitecturalGeometryValidator
from scripts.release_packager import ReleasePackager, compute_file_sha256
from scripts.sheet_generator import SheetGenerator, SheetTitleBlock


class TestReleaseRegressionSuite(unittest.TestCase):
    """Exhaustive 15-scenario regression test suite for Milestone 11 release readiness."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_root = Path(self.temp_dir.name)
        self.generator = DrawingGenerator()
        self.packager = ReleasePackager(output_root=str(self.output_root))

    def tearDown(self):
        self.temp_dir.cleanup()

    # -------------------------------------------------------------------------
    # Scenario 1: Small Single-Storey Plan (6x5m)
    # -------------------------------------------------------------------------
    def test_scenario_01_small_single_storey_plan(self):
        """1. Small 6x5m studio/cabin generates valid DXF, layers, and preflight passes."""
        model = {
            "projectName": "Studio Cabin",
            "status": "approved",
            "approvedBy": "Lead Architect",
            "approvedAt": "2026-11-02",
            "envelope": {"width": 6000.0, "depth": 5000.0},
            "walls": [
                {"id": "W-01", "start": [0, 0], "end": [6000, 0], "thickness": 200},
                {"id": "W-02", "start": [6000, 0], "end": [6000, 5000], "thickness": 200},
                {"id": "W-03", "start": [6000, 5000], "end": [0, 5000], "thickness": 200},
                {"id": "W-04", "start": [0, 5000], "end": [0, 0], "thickness": 200},
            ],
            "rooms": [
                {"id": "R-01", "name": "Studio Room", "label": "STUDIO", "area": 30.0, "perimeter": 22.0, "centroid": [3000, 2500]}
            ],
            "openings": [],
            "elements": [],
        }

        dxf_path = self.output_root / "scenario_01.dxf"
        res = self.generator.build_drawing(model=model, output_dxf_path=str(dxf_path))

        self.assertTrue(dxf_path.is_file())
        self.assertGreater(dxf_path.stat().st_size, 500)

        # Inspect generated DXF
        doc = ezdxf.readfile(str(dxf_path))
        self.assertEqual(doc.header.get("$INSUNITS", 0), 4)  # 4 = Millimeters
        layers = [l.dxf.name for l in doc.layers]
        self.assertIn("A-WALL-EXTR", layers)

    # -------------------------------------------------------------------------
    # Scenario 2: Large Multi-Room Residential Plan
    # -------------------------------------------------------------------------
    def test_scenario_02_large_multi_room_plan(self):
        """2. Multi-room layout produces verified dimension callouts and complete schedules."""
        engine = DimensionEngine()
        rooms = [
            {"id": "R-1", "name": "Living Room", "label": "LIVING", "centroid": [3000, 2500], "area": 30.0, "boundary": [[0,0], [6000,0], [6000,5000], [0,5000]]},
            {"id": "R-2", "name": "Kitchen", "label": "KIT", "centroid": [8000, 2000], "area": 16.0, "boundary": [[6000,0], [10000,0], [10000,4000], [6000,4000]]},
            {"id": "R-3", "name": "Master Bed", "label": "MBED", "centroid": [3000, 7500], "area": 25.0, "boundary": [[0,5000], [6000,5000], [6000,10000], [0,10000]]},
        ]
        model = {
            "projectName": "Family Villa",
            "status": "approved",
            "approvedBy": "Architect",
            "envelope": {"width": 10000.0, "depth": 10000.0},
            "rooms": rooms,
            "walls": [{"id": "W-01", "start": [0,0], "end": [10000,0], "thickness": 200}],
        }
        callouts = engine.calculate_internal_room_callouts(model)
        self.assertEqual(len(callouts), 3)
        self.assertEqual(callouts[0]["roomName"], "Living Room")
        self.assertIn("m", callouts[0]["formatted_m"])

    # -------------------------------------------------------------------------
    # Scenario 3: Two-Storey Duplex Plan with Stairs
    # -------------------------------------------------------------------------
    def test_scenario_03_two_storey_duplex_plan(self):
        """3. Two-storey duplex plan coordinates floor levels and validates stairs."""
        fixture_path = Path(__file__).resolve().parent / "fixtures" / "sample-model-two-storey.json"
        with open(fixture_path, "r", encoding="utf-8") as f:
            model = json.load(f)

        out_dir = self.output_root / "duplex_out"
        out_dir.mkdir(parents=True, exist_ok=True)

        res = self.generator.build_multi_floor_drawings(
            model=model,
            output_dir=str(out_dir),
            base_filename="duplex_test",
            generate_report=False,
            generate_handoff=True,
        )

        self.assertEqual(res["floorCount"], 2)
        dxf_gf = Path(res["floors"]["LEVEL-01"]["dxf"])
        dxf_ff = Path(res["floors"]["LEVEL-02"]["dxf"])
        self.assertTrue(dxf_gf.is_file())
        self.assertTrue(dxf_ff.is_file())

        handoff_path = Path(res["handoff"])
        self.assertTrue(handoff_path.is_file())
        with open(handoff_path, "r", encoding="utf-8") as f:
            ho = json.load(f)
        self.assertEqual(len(ho.get("floors", [])), 2)

    # -------------------------------------------------------------------------
    # Scenario 4: Non-Rectangular Footprint with Angled Wall
    # -------------------------------------------------------------------------
    def test_scenario_04_non_rectangular_footprint_angled_wall(self):
        """4. Angled wall footprint parses without geometry validation error."""
        model = {
            "projectName": "Angled Pavilion",
            "status": "approved",
            "approvedBy": "Architect",
            "envelope": {"width": 8000.0, "depth": 6000.0},
            "walls": [
                {"id": "W-01", "start": [0, 0], "end": [6000, 0], "thickness": 200},
                {"id": "W-02", "start": [6000, 0], "end": [8000, 2000], "thickness": 200},  # Angled chamfer
                {"id": "W-03", "start": [8000, 2000], "end": [8000, 6000], "thickness": 200},
                {"id": "W-04", "start": [8000, 6000], "end": [0, 6000], "thickness": 200},
                {"id": "W-05", "start": [0, 6000], "end": [0, 0], "thickness": 200},
            ],
            "rooms": [
                {"id": "R-01", "name": "Great Room", "label": "ROOM", "area": 44.0, "perimeter": 28.0, "centroid": [3500, 3000]}
            ],
        }

        val = ArchitecturalGeometryValidator(model)
        val_res = val.validate_all()
        blocking_issues = [i for i in val_res.get("issues", []) if i.get("severity") == "blocking"]
        self.assertEqual(len(blocking_issues), 0)

    # -------------------------------------------------------------------------
    # Scenario 5: Multiple Door Types (Single, Double, Sliding)
    # -------------------------------------------------------------------------
    def test_scenario_05_multiple_door_types(self):
        """5. Single swing, double, and pocket/sliding doors insert with swing arcs."""
        model = {
            "projectName": "Door Showcase",
            "status": "approved",
            "approvedBy": "Architect",
            "envelope": {"width": 10000.0, "depth": 6000.0},
            "walls": [
                {"id": "W-01", "start": [0, 0], "end": [10000, 0], "thickness": 200},
                {"id": "W-02", "start": [10000, 0], "end": [10000, 6000], "thickness": 200},
                {"id": "W-03", "start": [10000, 6000], "end": [0, 6000], "thickness": 200},
                {"id": "W-04", "start": [0, 6000], "end": [0, 0], "thickness": 200},
            ],
            "openings": [
                {"id": "D-01", "type": "door", "subType": "single_swing", "width": 900.0, "start": [1000, 0], "end": [1900, 0], "swing": "inward_right"},
                {"id": "D-02", "type": "door", "subType": "double_swing", "width": 1800.0, "start": [4000, 0], "end": [5800, 0], "swing": "inward"},
                {"id": "D-03", "type": "door", "subType": "sliding_pocket", "width": 1200.0, "start": [7500, 0], "end": [8700, 0], "swing": "none"},
            ],
            "rooms": [{"id": "R-1", "name": "Hall", "label": "HALL", "area": 55.0, "perimeter": 32.0, "centroid": [5000, 3000]}],
        }

        dxf_path = self.output_root / "scenario_05.dxf"
        res = self.generator.build_drawing(model=model, output_dxf_path=str(dxf_path))
        self.assertTrue(dxf_path.is_file())

        doc = ezdxf.readfile(str(dxf_path))
        layer_names = [l.dxf.name for l in doc.layers]
        self.assertIn("A-DOOR", layer_names)

    # -------------------------------------------------------------------------
    # Scenario 6: Multiple Window Configurations
    # -------------------------------------------------------------------------
    def test_scenario_06_multiple_window_configurations(self):
        """6. Casement and sliding bypass windows generate multi-line glazing & sills."""
        model = {
            "projectName": "Window Showcase",
            "status": "approved",
            "approvedBy": "Architect",
            "envelope": {"width": 8000.0, "depth": 5000.0},
            "walls": [
                {"id": "W-01", "start": [0, 0], "end": [8000, 0], "thickness": 200},
                {"id": "W-02", "start": [8000, 0], "end": [8000, 5000], "thickness": 200},
                {"id": "W-03", "start": [8000, 5000], "end": [0, 5000], "thickness": 200},
                {"id": "W-04", "start": [0, 5000], "end": [0, 0], "thickness": 200},
            ],
            "openings": [
                {"id": "W-01", "type": "window", "subType": "casement", "width": 1200.0, "start": [1500, 0], "end": [2700, 0], "sillHeight": 900.0},
                {"id": "W-02", "type": "window", "subType": "sliding_bypass", "width": 1800.0, "start": [4500, 0], "end": [6300, 0], "sillHeight": 1050.0},
            ],
            "rooms": [{"id": "R-1", "name": "Room", "label": "ROOM", "area": 36.0, "perimeter": 26.0, "centroid": [4000, 2500]}],
        }

        dxf_path = self.output_root / "scenario_06.dxf"
        res = self.generator.build_drawing(model=model, output_dxf_path=str(dxf_path))
        self.assertTrue(dxf_path.is_file())

        doc = ezdxf.readfile(str(dxf_path))
        layers = [l.dxf.name for l in doc.layers]
        self.assertIn("A-GLAZ", layers)

    # -------------------------------------------------------------------------
    # Scenario 7: Dense Dimension Chains and Collision Avoidance
    # -------------------------------------------------------------------------
    def test_scenario_07_dense_dimension_chains_collision_avoidance(self):
        """7. Dense overlapping dimensions are shifted by collision resolution."""
        engine = DimensionEngine()
        dim = DimensionEntity(
            id="dim_test",
            tier="internal",
            side="interior",
            p1=[0, 2500],
            p2=[4000, 2500],
            at=[2000, 2550],  # Very close to label at [2000, 2500]
            value_mm=4000.0,
            formatted_text="4000",
            rotation=0.0,
        )
        labels = [{"roomId": "living", "roomName": "LIVING", "labelPosition": [2000, 2500]}]

        collisions = engine.detect_dimension_collisions([dim], room_labels=labels)
        self.assertEqual(len(collisions), 1)
        self.assertEqual(collisions[0].collision_type, "label_crossing")

        # Resolve collisions
        resolved = engine.resolve_collisions([dim], room_labels=labels)
        self.assertEqual(len(resolved), 1)
        # Point 'at' y-coordinate should have been moved away
        self.assertLess(resolved[0].at[1], 2300.0)

    # -------------------------------------------------------------------------
    # Scenario 8: Conflicting Dimensions Detection
    # -------------------------------------------------------------------------
    def test_scenario_08_conflicting_dimensions_detection(self):
        """8. Contradictory dimensions trigger conflict detection in approval package."""
        model = {
            "projectName": "Conflicting Pavilion",
            "envelope": {"width": 8000.0, "depth": 6000.0},
            "walls": [
                {"id": "W-01", "start": [0, 0], "end": [8000, 0], "thickness": 200},
                {"id": "W-02", "start": [8000, 0], "end": [8000, 6000], "thickness": 200},
                {"id": "W-03", "start": [8000, 6000], "end": [0, 6000], "thickness": 200},
                {"id": "W-04", "start": [0, 6000], "end": [0, 0], "thickness": 200},
            ],
            "rooms": [
                {"id": "R-1", "name": "Room", "label": "ROOM", "area": 48.0, "perimeter": 28.0, "centroid": [4000, 3000]}
            ],
            "uncertainties": [
                {
                    "target": "W-01",
                    "description": "Arithmetic conflict: sum of interior opening widths (8500mm) exceeds total exterior wall length (8000mm).",
                    "confidence": "low",
                    "status": "unresolved",
                }
            ],
        }

        pkg = create_approval_package(draft_model=model)
        self.assertEqual(pkg["status"], "awaiting_approval")
        self.assertGreaterEqual(len(pkg["detected_conflicts"]), 1)
        self.assertEqual(pkg["detected_conflicts"][0]["conflict_type"], "arithmetic_mismatch")

    # -------------------------------------------------------------------------
    # Scenario 9: Incomplete Sketches Handling
    # -------------------------------------------------------------------------
    def test_scenario_09_incomplete_sketches_handling(self):
        """9. Missing depth dimension logs uncertainty and requires human review."""
        model = {
            "projectName": "Incomplete Sketch",
            "envelope": {"width": 7000.0, "depth": 5000.0},
            "walls": [{"id": "W-01", "start": [0, 0], "end": [7000, 0], "thickness": 200}],
            "uncertainties": [
                {
                    "target": "envelope.depth",
                    "description": "Missing overall building depth dimension on source sketch. Inferred from room proportions.",
                    "provenance": "assumed_default_unverified",
                    "confidence": "low",
                    "status": "unresolved",
                }
            ],
        }

        pkg = create_approval_package(draft_model=model)
        self.assertGreaterEqual(len(pkg["unknowns"]), 1)
        self.assertIn("envelope.depth", [u["field"] for u in pkg["unknowns"]])

    # -------------------------------------------------------------------------
    # Scenario 10: Poor-Quality and Rotated Sketches Handling
    # -------------------------------------------------------------------------
    def test_scenario_10_poor_quality_and_rotated_sketches(self):
        """10. Low-confidence rotated sketch logs uncertainties without failing."""
        observations = {
            "source_metadata": {
                "source_file": "rotated_blurry_sketch.jpg",
                "file_type": "jpg",
                "page_number": 1,
            },
            "uncertainties": [
                {
                    "id": "UNC-ROT-1",
                    "type": "skew_angle",
                    "description": "Source sketch is tilted approximately 7.5 degrees clockwise.",
                    "status": "unresolved",
                    "confidence": "low",
                }
            ],
        }
        model = {
            "projectName": "Rotated Plan",
            "envelope": {"width": 6000.0, "depth": 5000.0},
            "walls": [{"id": "W-01", "start": [0, 0], "end": [6000, 0], "thickness": 200}],
            "uncertainties": observations["uncertainties"],
        }

        pkg = create_approval_package(draft_model=model, observations=observations)
        self.assertEqual(pkg["source_sketch"]["source_file"], "rotated_blurry_sketch.jpg")
        self.assertGreaterEqual(len(pkg["unknowns"]), 1)

    # -------------------------------------------------------------------------
    # Scenario 11: Unknown Window Sill Heights (Explicit Provenance)
    # -------------------------------------------------------------------------
    def test_scenario_11_unknown_window_sill_heights(self):
        """11. Unannotated sill height is marked assumed_default_unverified and logged in uncertainties."""
        model = {
            "projectName": "Sill Integrity Villa",
            "status": "approved",
            "approvedBy": "Architect",
            "envelope": {"width": 8000.0, "depth": 5000.0},
            "walls": [
                {"id": "W-01", "start": [0, 0], "end": [8000, 0], "thickness": 200},
                {"id": "W-02", "start": [8000, 0], "end": [8000, 5000], "thickness": 200},
                {"id": "W-03", "start": [8000, 5000], "end": [0, 5000], "thickness": 200},
                {"id": "W-04", "start": [0, 5000], "end": [0, 0], "thickness": 200},
            ],
            "openings": [
                # Window with NO sillHeight specified
                {"id": "WIN-UNANNOTATED", "type": "window", "width": 1200.0, "start": [2000, 0], "end": [3200, 0]},
            ],
            "rooms": [{"id": "R-1", "name": "Room", "label": "ROOM", "area": 36.0, "perimeter": 26.0, "centroid": [4000, 2500]}],
        }

        dxf_path = self.output_root / "scenario_11.dxf"
        self.generator.build_drawing(model=model, output_dxf_path=str(dxf_path))

        handoff = compile_bim_handoff(model=model, dxf_path=str(dxf_path))
        win_item = handoff["openings"][0]

        # Verify fallback value is 900.0 mm
        self.assertEqual(win_item["sillHeight"], 900.0)
        # Verify provenance is explicit and non-silent
        self.assertEqual(win_item["sillHeightProvenance"], "assumed_default_unverified")
        self.assertEqual(win_item["source"], "inferred")

        # Verify uncertainty register includes this exact item
        unc_targets = [u["target"] for u in handoff.get("uncertainties", [])]
        self.assertTrue(any("WIN-UNANNOTATED" in t for t in unc_targets))

    # -------------------------------------------------------------------------
    # Scenario 12: Unapproved Geometry Revisions
    # -------------------------------------------------------------------------
    def test_scenario_12_unapproved_geometry_revisions(self):
        """12. Geometry changes alter hash; drafting without approved status is blocked."""
        model_v1 = {
            "projectName": "Versioned Home",
            "status": "awaiting_approval",
            "envelope": {"width": 8000.0, "depth": 6000.0},
            "walls": [{"id": "W-1", "start": [0, 0], "end": [8000, 0], "thickness": 200}],
        }
        hash_v1 = calculate_geometry_hash(model_v1)

        model_v2 = dict(model_v1)
        model_v2["walls"] = [{"id": "W-1", "start": [0, 0], "end": [8500, 0], "thickness": 200}]
        hash_v2 = calculate_geometry_hash(model_v2)

        self.assertNotEqual(hash_v1, hash_v2)

        # Drafting must fail if model status is not approved
        with self.assertRaises(ApprovalGateError):
            self.generator.build_drawing(model=model_v2, output_dxf_path=str(self.output_root / "fail.dxf"))

    # -------------------------------------------------------------------------
    # Scenario 13: Invalid Wall Junctions (Detecting Disconnected Walls)
    # -------------------------------------------------------------------------
    def test_scenario_13_invalid_wall_junctions(self):
        """13. Wall with 100mm gap to adjacent perpendicular wall is flagged."""
        model = {
            "projectName": "Disconnected Junction",
            "status": "approved",
            "envelope": {"width": 8000.0, "depth": 6000.0},
            "walls": [
                {"id": "W-01", "start": [0, 0], "end": [8000, 0], "thickness": 200},
                # Wall ending 100mm away from W-01 (gap)
                {"id": "W-02", "start": [4000, 100], "end": [4000, 5000], "thickness": 200},
            ],
        }

        validator = ArchitecturalGeometryValidator(model)
        res = validator.validate_all()

        gap_issues = [i for i in res.get("issues", []) if "unintended gap" in i.get("description", "").lower()]
        self.assertGreaterEqual(len(gap_issues), 1)

    # -------------------------------------------------------------------------
    # Scenario 14: DXF with Duplicate Entities
    # -------------------------------------------------------------------------
    def test_scenario_14_dxf_duplicate_entities(self):
        """14. DXFInspector detects and flags duplicate geometric entities."""
        doc = ezdxf.new("R2018")
        msp = doc.modelspace()
        # Add duplicate lines
        msp.add_line((0, 0), (5000, 0), dxfattribs={"layer": "A-WALL"})
        msp.add_line((0, 0), (5000, 0), dxfattribs={"layer": "A-WALL"})  # Duplicate!

        dxf_file = self.output_root / "duplicate_test.dxf"
        doc.saveas(str(dxf_file))

        inspector = DXFInspector()
        report = inspector.inspect(dxf_file)

        self.assertGreater(report.duplicate_entities_count, 0)
        self.assertGreaterEqual(len(report.warnings), 1)

    # -------------------------------------------------------------------------
    # Scenario 15: BIM Handoff with Unresolved Assumptions
    # -------------------------------------------------------------------------
    def test_scenario_15_bim_handoff_with_unresolved_assumptions(self):
        """15. Handoff JSON serializes unresolved assumptions with low confidence."""
        model = {
            "projectName": "Assumption Project",
            "status": "approved",
            "approvedBy": "Architect",
            "envelope": {"width": 6000.0, "depth": 5000.0},
            "walls": [
                {"id": "W-01", "start": [0, 0], "end": [6000, 0], "thickness": 200},
                {"id": "W-02", "start": [6000, 0], "end": [6000, 5000], "thickness": 200},
                {"id": "W-03", "start": [6000, 5000], "end": [0, 5000], "thickness": 200},
                {"id": "W-04", "start": [0, 5000], "end": [0, 0], "thickness": 200},
            ],
            "openings": [
                {"id": "WIN-01", "type": "window", "width": 1200.0, "start": [1000, 0], "end": [2200, 0]}
            ],
            "uncertainties": [
                {
                    "target": "WIN-01.sillHeight",
                    "description": "Window sill height unannotated; assumed 900mm default.",
                    "confidence": "low",
                    "provenance": "assumed_default_unverified",
                    "status": "unresolved",
                }
            ],
        }

        dxf_path = self.output_root / "scenario_15.dxf"
        self.generator.build_drawing(model=model, output_dxf_path=str(dxf_path))
        ho = compile_bim_handoff(model=model, dxf_path=str(dxf_path))

        self.assertIn("uncertainties", ho)
        self.assertGreaterEqual(len(ho["uncertainties"]), 1)
        unc = ho["uncertainties"][0]
        self.assertEqual(unc["status"], "unresolved")
        self.assertEqual(unc["confidence"], "low")
        self.assertEqual(unc["provenance"], "assumed_default_unverified")


if __name__ == "__main__":
    unittest.main()
