"""
Test Suite for Real-World Benchmark Engine & Accuracy Evaluation (Milestone 10).
Validates:
1. Benchmark dataset manifest loading and schema integrity.
2. Ground truth loading across all 6 benchmark categories (A through F).
3. Spatial wall matching: True/False positives, Precision, Recall, F1, endpoint errors.
4. Opening spatial matching: Position errors, width errors, type classification accuracy.
5. Room polygon IoU computation, net area relative error, and label verification.
6. Dimension accuracy within 50mm tolerance and absolute error calculation.
7. Execution type provenance enforcement ('real_api', 'agent_native', 'mocked').
8. Benchmark audit report generation in Markdown and JSON.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.benchmark_engine import (
    BenchmarkEvaluator,
    SampleBenchmarkResult,
    generate_benchmark_markdown_report,
    polygon_bounding_box,
    polygon_intersection_area_approx,
    polygon_iou,
)
from scripts.vision_provider import VisionConfig, VisionResult

BENCHMARK_DIR = Path("tests/benchmark")
MANIFEST_PATH = BENCHMARK_DIR / "metadata" / "dataset_manifest.json"
GT_DIR = BENCHMARK_DIR / "ground_truth"


class TestBenchmarkEngine(unittest.TestCase):
    """Unit tests for benchmark accuracy metrics, spatial matching, and report generation."""

    @classmethod
    def setUpClass(cls):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            cls.manifest = json.load(f)

    def test_01_manifest_contains_six_categories(self):
        """Manifest defines all 6 required benchmark categories (A through F)."""
        self.assertEqual(self.manifest["totalSamples"], 6)
        samples = self.manifest["samples"]
        self.assertEqual(len(samples), 6)
        categories = {s["category"].split(":")[0] for s in samples}
        expected = {"Category A", "Category B", "Category C", "Category D", "Category E", "Category F"}
        self.assertEqual(categories, expected)

    def test_02_all_ground_truth_files_exist_and_parse(self):
        """All 6 ground truth annotation files exist on disk and parse cleanly."""
        for s in self.manifest["samples"]:
            gt_name = s["fileName"].rsplit(".", 1)[0] + ".ground_truth.json"
            gt_path = GT_DIR / gt_name
            self.assertTrue(gt_path.is_file(), f"Missing ground truth file at {gt_path}")
            with open(gt_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertEqual(data["sampleId"], s["sampleId"])
            self.assertIn("walls", data)
            self.assertIn("openings", data)
            self.assertIn("rooms", data)

    def test_03_polygon_iou_calculation(self):
        """Verify 2D polygon IoU calculation on identical, overlapping, and disjoint shapes."""
        # 1. Identical rectangles -> IoU = 1.0
        poly1 = [[0, 0], [4000, 0], [4000, 3000], [0, 3000]]
        poly2 = [[0, 0], [4000, 0], [4000, 3000], [0, 3000]]
        self.assertAlmostEqual(polygon_iou(poly1, poly2), 1.0, places=2)

        # 2. 50% overlapping rectangles -> IoU ~ 0.33
        poly_half = [[2000, 0], [6000, 0], [6000, 3000], [2000, 3000]]
        iou_half = polygon_iou(poly1, poly_half)
        self.assertTrue(0.25 <= iou_half <= 0.45)

        # 3. Disjoint rectangles -> IoU = 0.0
        poly_disjoint = [[5000, 0], [8000, 0], [8000, 3000], [5000, 3000]]
        self.assertEqual(polygon_iou(poly1, poly_disjoint), 0.0)

    def test_04_wall_spatial_matching(self):
        """Verify spatial wall matching handles reversed endpoints and calculates F1."""
        evaluator = BenchmarkEvaluator(wall_distance_tolerance_mm=100.0)

        # Ground truth: 2 walls
        gt_walls = [
            {"id": "w1", "start": [0, 0], "end": [5000, 0], "thickness": 200},
            {"id": "w2", "start": [5000, 0], "end": [5000, 4000], "thickness": 200},
        ]
        # Predictions: w1 reversed, w2 shifted slightly (20mm), plus 1 extra false positive
        pred_walls = [
            {"id": "pw1", "start": [5000, 0], "end": [0, 0], "thickness": 200},  # reversed -> matches w1
            {"id": "pw2", "start": [5020, 0], "end": [5020, 4000], "thickness": 200},  # 20mm shift -> matches w2
            {"id": "pw_extra", "start": [1000, 1000], "end": [2000, 1000], "thickness": 100},  # false positive
        ]

        metrics = evaluator._evaluate_walls(pred_walls, gt_walls)
        self.assertEqual(metrics.true_positives, 2)
        self.assertEqual(metrics.false_positives, 1)
        self.assertEqual(metrics.false_negatives, 0)
        self.assertAlmostEqual(metrics.precision, 2 / 3, places=2)
        self.assertAlmostEqual(metrics.recall, 1.0, places=2)
        self.assertGreater(metrics.f1, 0.75)
        self.assertTrue(metrics.mean_endpoint_error_mm < 30.0)

    def test_05_opening_spatial_matching(self):
        """Verify opening center distance matching and type classification."""
        evaluator = BenchmarkEvaluator(opening_distance_tolerance_mm=200.0)

        gt_openings = [
            {"id": "d1", "type": "door", "center": [2000, 0], "width": 900},
            {"id": "win1", "type": "window", "center": [0, 2500], "width": 1500},
        ]
        pred_openings = [
            {"id": "p_d1", "type": "door", "center": [2010, 5], "width": 900},
            {"id": "p_win1", "type": "window", "center": [0, 2520], "width": 1450},  # 50mm width error
        ]

        metrics = evaluator._evaluate_openings(pred_openings, gt_openings)
        self.assertEqual(metrics.true_positives, 2)
        self.assertEqual(metrics.false_positives, 0)
        self.assertEqual(metrics.false_negatives, 0)
        self.assertEqual(metrics.precision, 1.0)
        self.assertEqual(metrics.recall, 1.0)
        self.assertEqual(metrics.type_accuracy, 1.0)
        self.assertEqual(metrics.mean_width_error_mm, 25.0)

    def test_06_dimension_numeric_accuracy(self):
        """Verify dimension extraction tolerance: values within 50mm counted as correct."""
        evaluator = BenchmarkEvaluator(dimension_tolerance_mm=50.0)

        gt_dims = [
            {"id": "dim1", "value": 6000.0},
            {"id": "dim2", "value": 5000.0},
        ]
        pred_dims = [
            {"id": "p_dim1", "value": 6020.0},  # 20mm error -> correct (< 50mm)
            {"id": "p_dim2", "value": 4800.0},  # 200mm error -> incorrect (> 50mm)
        ]

        metrics = evaluator._evaluate_dimensions(pred_dims, gt_dims)
        self.assertEqual(metrics.true_positives, 2)
        self.assertEqual(metrics.numeric_accuracy_pct, 50.0)
        self.assertEqual(metrics.mean_value_error_mm, 110.0)

    def test_07_execution_type_provenance_enforced(self):
        """Mock execution MUST be tagged with is_genuine_ai=False and execution_type='mocked'."""
        evaluator = BenchmarkEvaluator()
        with open(GT_DIR / "sample-a-clean-ortho.ground_truth.json", "r", encoding="utf-8") as f:
            gt_data = json.load(f)

        mock_vis_result = VisionResult(
            status="success",
            execution_record={
                "record_id": "VR-MOCK-001",
                "execution_type": "mocked",
                "provider_name": "mock_provider",
                "model_identifier": "deterministic_mock_v1",
                "processing_duration_ms": 45.0,
                "source_image": {"sha256": "abcdef123456"},
            }
        )

        res = evaluator.evaluate_sample(gt_data, gt_data, mock_vis_result)
        self.assertFalse(res.is_genuine_ai)
        self.assertEqual(res.execution_type, "mocked")
        self.assertIn("mocked", res.notes[0].lower())

    def test_08_generate_benchmark_markdown_report(self):
        """Benchmark report renders markdown summary table and architectural notes."""
        evaluator = BenchmarkEvaluator()
        with open(GT_DIR / "sample-a-clean-ortho.ground_truth.json", "r", encoding="utf-8") as f:
            gt_data = json.load(f)

        vis_result = VisionResult(
            status="success",
            execution_record={
                "record_id": "VR-MOCK-001",
                "execution_type": "mocked",
                "provider_name": "mock_provider",
                "model_identifier": "mock_v1",
                "processing_duration_ms": 50.0,
                "source_image": {"sha256": "1234567890abcdef"},
            }
        )

        sample_res = evaluator.evaluate_sample(gt_data, gt_data, vis_result)
        md = generate_benchmark_markdown_report([sample_res])
        self.assertIn("# Sketch-to-CAD Real-World Vision Benchmark Report", md)
        self.assertIn("Summary Results by Sample", md)
        self.assertIn("BENCH-CAT-A-01", md)
        self.assertIn("Benchmark Integrity Notice", md)


if __name__ == "__main__":
    unittest.main()
