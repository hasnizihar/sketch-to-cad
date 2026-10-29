"""
End-to-End Sketch-to-CAD Test Suite for Milestone 7.

Validates all 24 required capabilities:
1. JPG/PNG input handling
2. PDF input handling
3. Unsupported or corrupted inputs
4. Source metadata preservation
5. Structured observation validation
6. Dimension provenance
7. Missing dimension handling
8. Contradictory dimension detection
9. Wall connectivity
10. Room boundary reconstruction
11. Door and window host-wall association
12. Unknown symbol handling
13. Floor identification
14. Multi-floor source separation
15. Approval package generation
16. Rejected approval handling
17. Revision-aware approval enforcement
18. Draft model schema validation
19. Approved model generation
20. Real CADCraft DXF generation
21. BIM handoff consistency
22. Architectural report consistency
23. Source-to-CAD visual QA
24. End-to-end approved fixture execution
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.sketch_interpreter import (
    load_sketch_input,
    validate_observations,
    reconstruct_geometry,
    compile_draft_model,
    get_observations_schema,
    get_model_schema,
)
from scripts.approval_package import (
    create_approval_package,
    apply_review_decision,
    calculate_geometry_hash,
    generate_proposal_markdown,
    get_approval_package_schema,
)
from scripts.visual_qa import (
    perform_visual_qa,
    generate_visual_qa_markdown,
    compare_footprint_aspect_ratio,
    compare_rooms,
    compare_openings,
    compare_dimensions,
)
from scripts.sketch_to_cad_pipeline import SketchToCADPipeline
from scripts.drawing_generator import DrawingGenerator, compile_bim_handoff


FIXTURES_DIR = Path("tests/fixtures/sketches")
REAL_SKETCH_PATH = Path("docs/assets/sketch-before.jpg")


class TestSketchToCADE2E(unittest.TestCase):
    """24 Automated test cases for the Milestone 7 Sketch-to-CAD Pipeline."""

    @classmethod
    def setUpClass(cls):
        cls.fixture_a_img = FIXTURES_DIR / "fixture-a-clean-single-floor.png"
        cls.fixture_a_obs = FIXTURES_DIR / "fixture-a-observations.json"
        cls.fixture_b_img = FIXTURES_DIR / "fixture-b-incomplete.png"
        cls.fixture_b_obs = FIXTURES_DIR / "fixture-b-observations.json"
        cls.fixture_c_img = FIXTURES_DIR / "fixture-c-contradictory.png"
        cls.fixture_c_obs = FIXTURES_DIR / "fixture-c-observations.json"
        cls.fixture_d_pdf = FIXTURES_DIR / "fixture-d-two-storey.pdf"
        cls.fixture_d_obs = FIXTURES_DIR / "fixture-d-observations.json"
        cls.fixture_e_img = FIXTURES_DIR / "fixture-e-nonrectangular.png"
        cls.fixture_e_obs = FIXTURES_DIR / "fixture-e-observations.json"

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="agy_sketch_test_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # 1. JPG/PNG input handling
    def test_01_jpg_png_input_handling(self):
        # PNG Fixture
        meta_png = load_sketch_input(str(self.fixture_a_img))
        self.assertEqual(meta_png["file_type"], "png")
        self.assertEqual(meta_png["dimensions_pixels"]["width"], 1200)
        self.assertEqual(meta_png["dimensions_pixels"]["height"], 900)

        # Real JPG sketch
        if REAL_SKETCH_PATH.is_file():
            meta_jpg = load_sketch_input(str(REAL_SKETCH_PATH))
            self.assertIn(meta_jpg["file_type"], ("jpg", "jpeg"))
            self.assertGreater(meta_jpg["dimensions_pixels"]["width"], 500)

    # 2. PDF input handling
    def test_02_pdf_input_handling(self):
        meta_pdf = load_sketch_input(str(self.fixture_d_pdf), page_number=1)
        self.assertEqual(meta_pdf["file_type"], "pdf")
        self.assertEqual(meta_pdf["total_pages"], 2)
        self.assertEqual(meta_pdf["page_number"], 1)
        self.assertGreater(meta_pdf["dimensions_pixels"]["width"], 1000)

    # 3. Unsupported or corrupted inputs
    def test_03_unsupported_or_corrupted_inputs(self):
        # Missing file
        with self.assertRaises(FileNotFoundError):
            load_sketch_input(os.path.join(self.temp_dir, "nonexistent.png"))

        # Unsupported format (.docx)
        bad_format = Path(self.temp_dir) / "test.docx"
        bad_format.write_text("dummy")
        with self.assertRaises(ValueError) as ctx:
            load_sketch_input(str(bad_format))
        self.assertIn("Unsupported file format", str(ctx.exception))

        # 0-byte file
        empty_file = Path(self.temp_dir) / "empty.png"
        empty_file.write_bytes(b"")
        with self.assertRaises(ValueError) as ctx:
            load_sketch_input(str(empty_file))
        self.assertIn("0 bytes", str(ctx.exception))

    # 4. Source metadata preservation
    def test_04_source_metadata_preservation(self):
        initial_mtime = self.fixture_a_img.stat().st_mtime
        initial_size = self.fixture_a_img.stat().st_size

        meta = load_sketch_input(str(self.fixture_a_img))
        self.assertEqual(meta["source_file"], self.fixture_a_img.name)

        # Ensure original file was NOT modified
        self.assertEqual(self.fixture_a_img.stat().st_mtime, initial_mtime)
        self.assertEqual(self.fixture_a_img.stat().st_size, initial_size)

    # 5. Structured observation validation
    def test_05_structured_observation_validation(self):
        with open(self.fixture_a_obs, "r", encoding="utf-8") as f:
            obs = json.load(f)
        valid, errors = validate_observations(obs)
        self.assertTrue(valid, f"Observation validation failed: {errors}")

        # Invalidate required field
        bad_obs = dict(obs)
        del bad_obs["walls"]
        valid_bad, errors_bad = validate_observations(bad_obs)
        self.assertFalse(valid_bad)
        self.assertGreater(len(errors_bad), 0)

    # 6. Dimension provenance
    def test_06_dimension_provenance(self):
        with open(self.fixture_a_obs, "r", encoding="utf-8") as f:
            obs = json.load(f)
        geom = reconstruct_geometry(obs)
        draft = compile_draft_model(obs, geom)

        # Check dimension sources
        for d in draft["dimensions"]:
            self.assertIn(d["source"], ("explicit", "estimated", "inferred"))

    # 7. Missing dimension handling
    def test_07_missing_dimension_handling(self):
        with open(self.fixture_b_obs, "r", encoding="utf-8") as f:
            obs = json.load(f)
        geom = reconstruct_geometry(obs)

        # Missing depth must generate a blocker uncertainty
        blockers = [u for u in geom["uncertainties"] if u.get("severity") == "blocker"]
        self.assertTrue(any("depth" in u.get("field", "") for u in blockers))
        self.assertTrue(geom["has_blockers"])

    # 8. Contradictory dimension detection
    def test_08_contradictory_dimension_detection(self):
        with open(self.fixture_c_obs, "r", encoding="utf-8") as f:
            obs = json.load(f)
        geom = reconstruct_geometry(obs)

        # Room sum 9100 > overall 8000 must be caught as arithmetic mismatch
        conflicts = geom["detected_conflicts"]
        mismatch = [c for c in conflicts if c.get("conflict_type") == "arithmetic_mismatch"]
        self.assertGreater(len(mismatch), 0)
        self.assertTrue(geom["has_blockers"])

    # 9. Wall connectivity
    def test_09_wall_connectivity(self):
        with open(self.fixture_a_obs, "r", encoding="utf-8") as f:
            obs = json.load(f)
        geom = reconstruct_geometry(obs)
        walls = geom["walls"]
        self.assertEqual(len(walls), 6)
        # All exterior walls must be present
        ext_walls = [w for w in walls if w["type"] == "exterior"]
        self.assertEqual(len(ext_walls), 4)

    # 10. Room boundary reconstruction
    def test_10_room_boundary_reconstruction(self):
        with open(self.fixture_a_obs, "r", encoding="utf-8") as f:
            obs = json.load(f)
        geom = reconstruct_geometry(obs)
        rooms = geom["rooms"]
        self.assertEqual(len(rooms), 3)
        room_names = {r["name"] for r in rooms}
        self.assertIn("LIVING / DINING ROOM", room_names)
        self.assertIn("BEDROOM 1", room_names)
        self.assertIn("BATHROOM", room_names)

    # 11. Door and window host-wall association
    def test_11_door_and_window_host_wall_association(self):
        with open(self.fixture_a_obs, "r", encoding="utf-8") as f:
            obs = json.load(f)
        geom = reconstruct_geometry(obs)
        openings = geom["openings"]
        for op in openings:
            self.assertIsNotNone(op.get("wallId"))
            self.assertGreater(op.get("width", 0), 0)

    # 12. Unknown symbol handling
    def test_12_unknown_symbol_handling(self):
        with open(self.fixture_a_obs, "r", encoding="utf-8") as f:
            obs = json.load(f)
        obs["symbols"] = [
            {
                "id": "SYM-UNKNOWN-01",
                "symbol_type": "triangle_marker",
                "description": "Unrecognized triangular symbol near entrance",
                "is_recognized": False,
                "confidence": 0.50,
                "source_bbox": [0.2, 0.4, 0.25, 0.45],
            }
        ]
        geom = reconstruct_geometry(obs)
        # Reconstruction succeeds without crash
        self.assertIsNotNone(geom["envelope"])

    # 13. Floor identification
    def test_13_floor_identification(self):
        meta_single = load_sketch_input(str(self.fixture_a_img))
        self.assertEqual(meta_single["total_pages"], 1)

        meta_multi = load_sketch_input(str(self.fixture_d_pdf))
        self.assertEqual(meta_multi["total_pages"], 2)

    # 14. Multi-floor source separation
    def test_14_multi_floor_source_separation(self):
        meta_p1 = load_sketch_input(str(self.fixture_d_pdf), page_number=1)
        meta_p2 = load_sketch_input(str(self.fixture_d_pdf), page_number=2)
        self.assertEqual(meta_p1["page_number"], 1)
        self.assertEqual(meta_p2["page_number"], 2)

    # 15. Approval package generation
    def test_15_approval_package_generation(self):
        with open(self.fixture_a_obs, "r", encoding="utf-8") as f:
            obs = json.load(f)
        geom = reconstruct_geometry(obs)
        draft = compile_draft_model(obs, geom)
        pkg = create_approval_package(draft, obs)

        self.assertEqual(pkg["status"], "awaiting_approval")
        self.assertEqual(len(pkg["revision_hash"]), 64)
        self.assertGreater(len(pkg["approval_actions_required"]), 0)

        # Markdown proposal
        md = generate_proposal_markdown(pkg)
        self.assertIn("Architectural Floor Plan Proposal", md)
        self.assertIn(pkg["revision_hash"][:12], md)

    # 16. Rejected approval handling
    def test_16_rejected_approval_handling(self):
        with open(self.fixture_a_obs, "r", encoding="utf-8") as f:
            obs = json.load(f)
        geom = reconstruct_geometry(obs)
        draft = compile_draft_model(obs, geom)
        pkg = create_approval_package(draft, obs)

        rejection_decision = {
            "reviewer_name": "John Doe, Principal Architect",
            "action": "reject",
            "details": {"reason": "Living room boundary layout is unacceptable."},
        }
        pkg_rej, model_rej = apply_review_decision(pkg, draft, rejection_decision)
        self.assertEqual(pkg_rej["status"], "rejected")
        self.assertEqual(model_rej["status"], "rejected")

    # 17. Revision-aware approval enforcement
    def test_17_revision_aware_approval_enforcement(self):
        with open(self.fixture_a_obs, "r", encoding="utf-8") as f:
            obs = json.load(f)
        geom = reconstruct_geometry(obs)
        draft = compile_draft_model(obs, geom)
        pkg = create_approval_package(draft, obs)

        # Disallow self-approval by AI agent
        with self.assertRaises(PermissionError) as ctx:
            apply_review_decision(
                pkg, draft,
                {"reviewer_name": "AI Assistant (antigravity)", "action": "approve"}
            )
        self.assertIn("Self-approval rejected", str(ctx.exception))

        # Modifying model geometry invalidates the package hash
        tampered_draft = dict(draft)
        tampered_draft["envelope"] = {"width": 9999.0, "depth": 9999.0}
        with self.assertRaises(ValueError) as ctx:
            apply_review_decision(
                pkg, tampered_draft,
                {"reviewer_name": "Valid Human Architect", "action": "approve"}
            )
        self.assertIn("Approval invalidated: Model geometry has been altered", str(ctx.exception))

    # 18. Draft model schema validation
    def test_18_draft_model_schema_validation(self):
        with open(self.fixture_a_obs, "r", encoding="utf-8") as f:
            obs = json.load(f)
        geom = reconstruct_geometry(obs)
        draft = compile_draft_model(obs, geom)
        self.assertEqual(draft["status"], "awaiting_approval")
        self.assertIn("envelope", draft)
        self.assertIn("walls", draft)
        self.assertIn("openings", draft)
        self.assertIn("rooms", draft)

    # 19. Approved model generation
    def test_19_approved_model_generation(self):
        with open(self.fixture_a_obs, "r", encoding="utf-8") as f:
            obs = json.load(f)
        geom = reconstruct_geometry(obs)
        draft = compile_draft_model(obs, geom)
        pkg = create_approval_package(draft, obs)

        decision = {
            "reviewer_name": "Jane Smith, Architect",
            "action": "approve",
            "details": {"notes": "Approved for CAD drafting."},
        }
        pkg_app, model_app = apply_review_decision(pkg, draft, decision)
        self.assertEqual(pkg_app["status"], "approved")
        self.assertEqual(model_app["status"], "approved")
        self.assertEqual(pkg_app["approval_metadata"]["approved_by"], "Jane Smith, Architect")

    # 20. Real CADCraft DXF generation
    def test_20_real_cadcraft_dxf_generation(self):
        with open(self.fixture_a_obs, "r", encoding="utf-8") as f:
            obs = json.load(f)
        geom = reconstruct_geometry(obs)
        draft = compile_draft_model(obs, geom)
        pkg = create_approval_package(draft, obs)

        # Human approve
        _, approved_model = apply_review_decision(
            pkg, draft,
            {"reviewer_name": "Human Architect", "action": "approve"}
        )

        dxf_path = os.path.join(self.temp_dir, "test_fixture_a.dxf")
        generator = DrawingGenerator()
        res = generator.build_drawing(approved_model, output_dxf_path=dxf_path)

        self.assertTrue(os.path.isfile(dxf_path))
        self.assertGreater(os.path.getsize(dxf_path), 500)
        with open(dxf_path, "r", encoding="latin1") as f:
            content = f.read()
            self.assertIn("SECTION", content)
            self.assertIn("ENTITIES", content)
            self.assertIn("EOF", content)

    # 21. BIM handoff consistency
    def test_21_bim_handoff_consistency(self):
        with open(self.fixture_a_obs, "r", encoding="utf-8") as f:
            obs = json.load(f)
        geom = reconstruct_geometry(obs)
        draft = compile_draft_model(obs, geom)
        pkg = create_approval_package(draft, obs)
        _, approved_model = apply_review_decision(
            pkg, draft,
            {"reviewer_name": "Human Architect", "action": "approve"}
        )

        handoff = compile_bim_handoff(approved_model, "test.dxf")
        self.assertEqual(handoff["schemaVersion"], "1.0.0")
        self.assertEqual(handoff["project"]["units"], "mm")
        self.assertGreater(len(handoff["walls"]), 0)

    # 22. Architectural report consistency
    def test_22_architectural_report_consistency(self):
        with open(self.fixture_a_obs, "r", encoding="utf-8") as f:
            obs = json.load(f)
        geom = reconstruct_geometry(obs)
        draft = compile_draft_model(obs, geom)
        pkg = create_approval_package(draft, obs)
        _, approved_model = apply_review_decision(
            pkg, draft,
            {"reviewer_name": "Human Architect", "action": "approve"}
        )

        dxf_path = os.path.join(self.temp_dir, "rep_test.dxf")
        rep_base = os.path.join(self.temp_dir, "rep_test")
        generator = DrawingGenerator()
        generator.build_drawing(
            approved_model,
            output_dxf_path=dxf_path,
            generate_report=True,
            output_report_base=rep_base,
        )

        self.assertTrue(os.path.isfile(f"{rep_base}.report.json"))
        self.assertTrue(os.path.isfile(f"{rep_base}.report.md"))

    # 23. Source-to-CAD visual QA
    def test_23_source_to_cad_visual_qa(self):
        with open(self.fixture_a_obs, "r", encoding="utf-8") as f:
            obs = json.load(f)
        geom = reconstruct_geometry(obs)
        draft = compile_draft_model(obs, geom)
        pkg = create_approval_package(draft, obs)
        _, approved_model = apply_review_decision(
            pkg, draft,
            {"reviewer_name": "Human Architect", "action": "approve"}
        )

        dxf_path = os.path.join(self.temp_dir, "qa_test.dxf")
        generator = DrawingGenerator()
        generator.build_drawing(approved_model, output_dxf_path=dxf_path)

        qa = perform_visual_qa(str(self.fixture_a_img), dxf_path, approved_model, obs)
        self.assertIn("overall_status", qa)
        self.assertIn("checks", qa)
        self.assertGreater(qa["checks_passed"], 0)

        qa_md = generate_visual_qa_markdown(qa)
        self.assertIn("Visual QA Report", qa_md)

    # 24. End-to-end approved fixture execution
    def test_24_end_to_end_approved_fixture_execution(self):
        with open(self.fixture_a_obs, "r", encoding="utf-8") as f:
            obs = json.load(f)

        pipeline = SketchToCADPipeline()

        # Step A: Run without approval -> must halt
        unapproved_res = pipeline.run_pipeline(
            source_sketch_path=str(self.fixture_a_img),
            output_dir=self.temp_dir,
            approval_decision=None,
            observations_override=obs,
            project_name="Fixture A Residence",
        )
        self.assertEqual(unapproved_res["status"], "awaiting_approval")
        self.assertTrue(os.path.isfile(unapproved_res["proposal_path"]))
        self.assertTrue(os.path.isfile(unapproved_res["package_path"]))

        # Step B: Run with human approval -> completes full workflow
        approved_res = pipeline.run_pipeline(
            source_sketch_path=str(self.fixture_a_img),
            output_dir=self.temp_dir,
            approval_decision={
                "reviewer_name": "Jane Smith, Registered Architect",
                "action": "approve",
                "details": {"notes": "Approved for full CAD drafting and reporting."},
            },
            observations_override=obs,
            project_name="Fixture A Residence",
        )
        self.assertEqual(approved_res["status"], "completed")
        self.assertTrue(os.path.isfile(approved_res["dxf_path"]))
        self.assertTrue(os.path.isfile(approved_res["visual_qa_json_path"]))
        self.assertTrue(os.path.isfile(approved_res["visual_qa_md_path"]))


if __name__ == "__main__":
    unittest.main()
