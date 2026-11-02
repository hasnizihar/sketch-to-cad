"""
Test Suite for Multimodal Vision Benchmark & Evaluation Metrics (Milestone 8).

Validates:
1. Normalized bounding-box IoU calculation.
2. Entity detection precision and recall.
3. Dimension extraction accuracy within 50mm tolerance.
4. Room label extraction accuracy.
5. Contradiction detection rate.
6. Benchmark execution across all 5 benchmark cases.
7. Benchmark result JSON schema validation.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.evaluate_vision import (
    calculate_box_iou,
    evaluate_entity_precision_recall,
    evaluate_dimension_accuracy,
    evaluate_label_accuracy,
    evaluate_benchmark,
    get_benchmark_result_schema,
)
from scripts.vision_config import resolve_vision_config
from scripts.vision_provider import create_vision_provider


class TestVisionBenchmark(unittest.TestCase):
    """Unit and integration tests for the vision benchmark evaluation suite."""

    def test_01_box_iou_calculation(self):
        # Identical boxes -> IoU = 1.0
        box1 = [0.1, 0.1, 0.5, 0.5]
        box2 = [0.1, 0.1, 0.5, 0.5]
        self.assertAlmostEqual(calculate_box_iou(box1, box2), 1.0, places=3)

        # Completely disjoint boxes -> IoU = 0.0
        box_disjoint = [0.6, 0.6, 0.9, 0.9]
        self.assertEqual(calculate_box_iou(box1, box_disjoint), 0.0)

        # Partial overlap
        box_half = [0.1, 0.3, 0.5, 0.7]  # width 0.4, height 0.4, overlap width 0.2
        iou = calculate_box_iou(box1, box_half)
        self.assertGreater(iou, 0.2)
        self.assertLess(iou, 0.8)

        # None or invalid boxes -> 0.0
        self.assertEqual(calculate_box_iou(None, box1), 0.0)
        self.assertEqual(calculate_box_iou([0, 0], box1), 0.0)

    def test_02_entity_precision_recall(self):
        ref_walls = [
            {"id": "W1", "wall_type": "exterior", "source_bbox": [0.1, 0.1, 0.2, 0.9]},
            {"id": "W2", "wall_type": "interior", "source_bbox": [0.5, 0.1, 0.52, 0.9]},
        ]
        # Exact match
        p, r, iou = evaluate_entity_precision_recall(ref_walls, ref_walls, "wall_type")
        self.assertEqual(p, 1.0)
        self.assertEqual(r, 1.0)
        self.assertEqual(iou, 1.0)

        # Missing one entity (FN)
        p_miss, r_miss, _ = evaluate_entity_precision_recall(ref_walls, [ref_walls[0]], "wall_type")
        self.assertEqual(p_miss, 1.0)
        self.assertEqual(r_miss, 0.5)

        # Extra false positive entity (FP)
        extra = {"id": "W3", "wall_type": "exterior", "source_bbox": [0.8, 0.1, 0.9, 0.9]}
        p_fp, r_fp, _ = evaluate_entity_precision_recall(ref_walls, ref_walls + [extra], "wall_type")
        self.assertAlmostEqual(p_fp, 0.667, places=2)
        self.assertEqual(r_fp, 1.0)

    def test_03_dimension_accuracy_evaluation(self):
        ref_dims = [
            {"id": "D1", "value_mm": 6000.0, "category": "explicit"},
            {"id": "D2", "value_mm": 5000.0, "category": "explicit"},
        ]
        # Predicted with 20mm tolerance drift -> must pass
        pred_dims = [
            {"id": "P1", "value_mm": 6020.0},
            {"id": "P2", "value_mm": 4990.0},
        ]
        acc = evaluate_dimension_accuracy(ref_dims, pred_dims, tolerance_mm=50.0)
        self.assertEqual(acc, 1.0)

        # Predicted with 100mm error on D2 -> 50% accuracy
        pred_bad = [
            {"id": "P1", "value_mm": 6020.0},
            {"id": "P2", "value_mm": 4850.0},
        ]
        acc_bad = evaluate_dimension_accuracy(ref_dims, pred_bad, tolerance_mm=50.0)
        self.assertEqual(acc_bad, 0.5)

    def test_04_room_label_accuracy(self):
        ref_rooms = [
            {"raw_label": "LIVING / DINING"},
            {"raw_label": "BEDROOM 1"},
            {"raw_label": "BATHROOM"},
        ]
        pred_rooms = [
            {"raw_label": "LIVING / DINING"},
            {"raw_label": "BEDROOM 1"},
            {"raw_label": "KITCHEN"},  # Mismatch
        ]
        lbl_acc = evaluate_label_accuracy(ref_rooms, pred_rooms)
        self.assertAlmostEqual(lbl_acc, 0.667, places=2)

    def test_05_benchmark_execution_and_schema_validation(self):
        cfg = resolve_vision_config(provider_name="mock")
        prov = create_vision_provider(cfg)
        benchmark_results = evaluate_benchmark(prov)

        self.assertIn("benchmark_id", benchmark_results)
        self.assertEqual(benchmark_results["test_cases_count"], 5)
        self.assertIn("metrics_summary", benchmark_results)
        self.assertEqual(len(benchmark_results["case_results"]), 5)

        # High metrics expected for reference-backed mock
        m = benchmark_results["metrics_summary"]
        self.assertEqual(m["wall_detection_precision"], 1.0)
        self.assertEqual(m["wall_detection_recall"], 1.0)
        self.assertEqual(m["contradiction_detection_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
