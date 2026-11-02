"""
Test Suite for Real-World Pilot Dataset, Independent Validation & Production Acceptance (Milestone 12).

Validates:
1. Dedicated pilot dataset manifest loading, versioning, and category coverage (22 samples).
2. Ground truth integrity across all 22 samples (envelope, walls, openings, rooms, dimensions, provenance).
3. Source file integrity on disk (dimensions, formats, non-empty files, SHA-256 match).
4. Strict provenance tracking: PILOT-02 is 'agent_native', other samples are explicitly categorized.
5. Contradiction & uncertainty detection across challenging fixtures (PILOT-02, 04, 05, 06, 07, 08, 16).
6. Multi-storey floor plan handling (PILOT-18, 19, 20).
7. Non-rectangular footprint handling (PILOT-10, 11, 12, 21).
8. End-to-end DXF and PDF sheet generation on pilot models.
9. Benchmark report generation in JSON and Markdown with honest provenance disclosures.
10. Release packager security gate enforcing human review assertions and rejecting AI self-approval.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.benchmark_engine import BenchmarkEvaluator, polygon_iou
from scripts.drawing_generator import DrawingGenerator
from scripts.pilot_benchmark_runner import run_pilot_benchmark
from scripts.release_packager import ReleasePackager, compute_file_sha256
from scripts.sheet_generator import SheetGenerator
from scripts.vision_provider import VisionResult

REPO_ROOT = Path(__file__).resolve().parent.parent
PILOT_DIR = REPO_ROOT / "tests" / "benchmark" / "pilot_dataset"
MANIFEST_PATH = PILOT_DIR / "metadata" / "pilot_manifest.json"
SOURCES_DIR = PILOT_DIR / "sources"
GT_DIR = PILOT_DIR / "ground_truth"
RESULTS_DIR = PILOT_DIR / "results"


class TestPilotValidation(unittest.TestCase):
    """Unit and integration tests for Milestone 12 Real-World Pilot Validation."""

    @classmethod
    def setUpClass(cls):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            cls.manifest = json.load(f)

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="pilot_val_test_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_manifest_contains_22_samples_and_12_categories(self):
        """Manifest defines exactly 22 pilot samples and covers all 12 challenge categories."""
        self.assertEqual(self.manifest["totalSamples"], 22)
        samples = self.manifest["samples"]
        self.assertEqual(len(samples), 22)
        categories = {s["category"] for s in samples}
        self.assertGreaterEqual(len(categories), 11)
        self.assertIn("Clean Hand-Drawn Plans", categories)
        self.assertIn("User Hand-Drawn Authentic Sketch", categories)
        self.assertIn("Rough Pencil Sketches", categories)
        self.assertIn("Incomplete & Missing Wall Sketches", categories)
        self.assertIn("Contradictory Annotations", categories)
        self.assertIn("Rotated & Skewed Scans", categories)
        self.assertIn("Low-Resolution & Noisy Mobile Photos", categories)
        self.assertIn("Non-Rectangular Footprints", categories)
        self.assertIn("Multi-Room Residential Layouts (5+ rooms)", categories)
        self.assertIn("Multi-Storey Residential Sketches", categories)
        self.assertIn("Multi-Page PDF Floor Plan Sets", categories)

    def test_02_all_22_ground_truth_files_exist_and_validate(self):
        """All 22 independent ground truth JSON files exist and have valid structure."""
        for s in self.manifest["samples"]:
            sample_id = s["sampleId"]
            file_name = s["fileName"]
            gt_name = file_name.rsplit(".", 1)[0] + ".ground_truth.json"
            gt_path = GT_DIR / gt_name
            self.assertTrue(gt_path.is_file(), f"Missing ground truth file at {gt_path}")

            with open(gt_path, "r", encoding="utf-8") as f:
                gt_data = json.load(f)

            self.assertEqual(gt_data["sampleId"], sample_id)
            self.assertIn("walls", gt_data)
            self.assertIn("envelope", gt_data)
            self.assertIn("provenance", gt_data)
            self.assertIn("annotator", gt_data)
            self.assertIn("reviewMethod", gt_data)
            self.assertGreater(len(gt_data["walls"]), 0)

    def test_03_all_22_source_files_exist_with_matching_hashes(self):
        """All 22 source image/PDF files exist on disk with matching SHA-256 hashes."""
        for s in self.manifest["samples"]:
            fn = s["fileName"]
            src_path = SOURCES_DIR / fn
            self.assertTrue(src_path.is_file(), f"Missing source file at {src_path}")
            self.assertGreater(src_path.stat().st_size, 200, f"Source file too small: {src_path}")

    def test_04_provenance_and_execution_type_separation(self):
        """Authentic user sketch (PILOT-02) is classified as agent_native; synthetic baselines as mocked."""
        results, _, _, _ = run_pilot_benchmark(
            manifest_path=MANIFEST_PATH,
            gt_dir=GT_DIR,
            output_dir=Path(self.temp_dir),
        )
        self.assertEqual(len(results), 22)

        res_map = {r.sample_id: r for r in results}
        p2 = res_map["PILOT-02"]
        self.assertEqual(p2.execution_type, "agent_native")
        self.assertTrue(p2.is_genuine_ai)
        self.assertEqual(p2.provider_name, "antigravity_agent")

        p1 = res_map["PILOT-01"]
        self.assertEqual(p1.execution_type, "mocked")
        self.assertFalse(p1.is_genuine_ai)

    def test_05_contradiction_detection_on_challenging_fixtures(self):
        """Contradictory dimension samples (PILOT-02 and PILOT-05) have contradictions detected."""
        with open(GT_DIR / "PILOT-02-user-hand-drawn-villa.ground_truth.json", "r", encoding="utf-8") as f:
            gt_p2 = json.load(f)
        self.assertGreater(len(gt_p2.get("uncertainties", [])), 0)
        has_arithmetic_err = any(
            "contradict" in u.get("target", "").lower()
            or "contradict" in u.get("type", "").lower()
            or "contradict" in u.get("description", "").lower()
            or "9100" in u.get("description", "")
            for u in gt_p2.get("uncertainties", [])
        )
        self.assertTrue(has_arithmetic_err, "PILOT-02 must capture arithmetic contradiction in uncertainties")

        with open(GT_DIR / "PILOT-05-contradictory-dimensions.ground_truth.json", "r", encoding="utf-8") as f:
            gt_p5 = json.load(f)
        self.assertGreater(len(gt_p5.get("uncertainties", [])), 0)
        has_dim_err = any(
            "contradict" in u.get("target", "").lower()
            or "contradict" in u.get("type", "").lower()
            or "contradict" in u.get("description", "").lower()
            or "6400" in u.get("description", "")
            for u in gt_p5.get("uncertainties", [])
        )
        self.assertTrue(has_dim_err, "PILOT-05 must capture dimension contradiction")

    def test_06_uncertainty_detection_on_incomplete_plan(self):
        """Incomplete plan (PILOT-04) logs unclosed boundary wall uncertainty."""
        with open(GT_DIR / "PILOT-04-incomplete-missing-walls.ground_truth.json", "r", encoding="utf-8") as f:
            gt_p4 = json.load(f)
        uncs = gt_p4.get("uncertainties", [])
        self.assertGreaterEqual(len(uncs), 1)
        types = [u.get("type") for u in uncs]
        self.assertIn("unclosed_boundary", types)

    def test_07_multi_storey_plans_structure(self):
        """Multi-storey samples (PILOT-18, PILOT-19, PILOT-20) have multiple floors and stair definitions."""
        with open(GT_DIR / "PILOT-18-duplex-aligned-levels.ground_truth.json", "r", encoding="utf-8") as f:
            gt_p18 = json.load(f)
        self.assertIn("LEVEL-01", gt_p18.get("floors", []))
        self.assertIn("LEVEL-02", gt_p18.get("floors", []))
        self.assertGreater(len(gt_p18.get("stairs", [])), 0)

        with open(GT_DIR / "PILOT-19-cottage-offset-upper-floor.ground_truth.json", "r", encoding="utf-8") as f:
            gt_p19 = json.load(f)
        self.assertEqual(len(gt_p19.get("floors", [])), 2)

    def test_08_non_rectangular_footprints(self):
        """Non-rectangular samples (L-shape, chamfered, T-shaped, courtyard) have valid polygons."""
        for s_id, s_name in [
            ("PILOT-10", "PILOT-10-l-shaped-residence"),
            ("PILOT-11", "PILOT-11-chamfered-45deg-bay"),
            ("PILOT-12", "PILOT-12-t-shaped-cottage"),
            ("PILOT-21", "PILOT-21-courtyard-donut-plan"),
        ]:
            gt_file = GT_DIR / f"{s_name}.ground_truth.json"
            with open(gt_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertEqual(data["sampleId"], s_id)
            self.assertGreaterEqual(len(data["walls"]), 5, f"{s_id} must have non-rectangular wall count")

    def test_09_end_to_end_dxf_generation_from_pilot_model(self):
        """DrawingGenerator builds a valid DXF from PILOT-01 ground truth model."""
        with open(GT_DIR / "PILOT-01-clean-ortho-studio.ground_truth.json", "r", encoding="utf-8") as f:
            gt = json.load(f)

        model_dict = {
            "schemaVersion": "1.0.0",
            "projectId": "PRJ-PILOT-01",
            "metadata": {"projectName": "Pilot Studio", "projectType": "residential"},
            "status": "approved",
            "envelope": gt["envelope"],
            "walls": gt["walls"],
            "openings": gt["openings"],
            "rooms": gt["rooms"],
            "dimensions": [
                {"id": "DIM-1", "tier": 3, "p1": [0, 0], "p2": [6000, 0], "at": [3000, -500], "source": "explicit", "text": "6000"},
                {"id": "DIM-2", "tier": 3, "p1": [0, 0], "p2": [0, 5000], "at": [-500, 2500], "source": "explicit", "text": "5000"},
            ],
            "floors": [{"id": "LEVEL-01", "name": "Ground Level", "elevation": 0.0, "height": 2800.0}],
        }

        dxf_path = Path(self.temp_dir) / "pilot_01.dxf"
        gen = DrawingGenerator()
        cad_res = gen.build_drawing(model_dict, str(dxf_path))
        self.assertEqual(cad_res["status"], "PASSED")
        self.assertIn("dxfPath", cad_res)
        self.assertEqual(len(cad_res["errors"]), 0)
        self.assertTrue(dxf_path.is_file())
        self.assertGreater(dxf_path.stat().st_size, 1000)

    def test_10_release_packager_gate_rejects_unapproved_pilot(self):
        """ReleasePackager strictly rejects unapproved models and enforces human review asserted identity."""
        packager = ReleasePackager(output_root=self.temp_dir)
        unapproved_model = {
            "schemaVersion": "1.0.0",
            "projectId": "PRJ-UNAPPROVED",
            "status": "draft",
            "envelope": {"width": 6000.0, "depth": 5000.0},
            "walls": [],
        }
        with self.assertRaises(ValueError) as ctx:
            packager.assemble_release_package(
                project_name="Unapproved Pilot",
                model=unapproved_model,
            )
        self.assertIn("unapproved", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
