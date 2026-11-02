"""
Test Suite for Architectural Geometry Validation (Milestone 9).
Validates:
1. Wall network topology: L-junctions, T-junctions, Cross-junctions, and disconnected endpoints.
2. Degenerate wall detection (< 10mm).
3. Opening clearances: Corner clearance >= 50mm, opening bounds within wall, overlapping openings.
4. Door swing clearances: conflicts between door swing arcs and adjacent partition walls.
5. Room polygon validation: Shoelace area calculation, polygon closure, self-intersection, overlapping rooms.
6. Envelope containment: rooms strictly bounded within external envelope.
7. Multi-storey level filtering: isolates geometry per level.
8. 4-tier severity categorization: blocking, major, warning, informational.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.geometry_validation import (
    ArchitecturalGeometryValidator,
    Point2D,
    line_intersection,
    polygon_area_shoelace,
    polygon_is_self_intersecting,
    polygons_overlap,
    point_in_polygon,
)

FIXTURES_DIR = Path("tests/fixtures/sketches")


class TestGeometryValidation(unittest.TestCase):
    """Unit tests for ArchitecturalGeometryValidator and geometric utility functions."""

    def setUp(self):
        self.validator = ArchitecturalGeometryValidator(tolerance_mm=10.0)

    def test_01_shoelace_area_calculation(self):
        """Verify Shoelace formula on known geometric shapes."""
        # 4m x 5m rectangle = 20 m² = 20,000,000 mm²
        rect = [(0.0, 0.0), (4000.0, 0.0), (4000.0, 5000.0), (0.0, 5000.0)]
        area = polygon_area_shoelace(rect)
        self.assertAlmostEqual(area, 20.0, places=2)

        # Counter-clockwise orientation
        rect_ccw = [(0.0, 0.0), (0.0, 5000.0), (4000.0, 5000.0), (4000.0, 0.0)]
        area_ccw = polygon_area_shoelace(rect_ccw)
        self.assertAlmostEqual(area_ccw, 20.0, places=2)

        # Triangle: base 6m, height 4m = 12 m²
        triangle = [(0.0, 0.0), (6000.0, 0.0), (3000.0, 4000.0)]
        self.assertAlmostEqual(polygon_area_shoelace(triangle), 12.0, places=2)

    def test_02_self_intersecting_polygon_detection(self):
        """Bowtie / self-crossing polygons must be flagged."""
        # Simple rectangle (not self-intersecting)
        rect = [(0.0, 0.0), (4000.0, 0.0), (4000.0, 3000.0), (0.0, 3000.0)]
        self.assertFalse(polygon_is_self_intersecting(rect))

        # Bowtie polygon (self-intersecting)
        bowtie = [(0.0, 0.0), (4000.0, 3000.0), (4000.0, 0.0), (0.0, 3000.0)]
        self.assertTrue(polygon_is_self_intersecting(bowtie))

    def test_03_line_intersection(self):
        """Verify 2D line segment intersection logic."""
        p1, p2 = Point2D(0, 0), Point2D(10, 10)
        p3, p4 = Point2D(0, 10), Point2D(10, 0)
        hit, pt = line_intersection(p1, p2, p3, p4)
        self.assertTrue(hit)
        self.assertIsNotNone(pt)
        self.assertAlmostEqual(pt.x, 5.0)
        self.assertAlmostEqual(pt.y, 5.0)

        # Parallel lines
        p5, p6 = Point2D(0, 5), Point2D(10, 15)
        hit_parallel, _ = line_intersection(p1, p2, p5, p6)
        self.assertFalse(hit_parallel)

    def test_04_point_in_polygon(self):
        """Verify point-in-polygon containment check."""
        poly = [(0.0, 0.0), (5000.0, 0.0), (5000.0, 5000.0), (0.0, 5000.0)]
        self.assertTrue(point_in_polygon(Point2D(2500, 2500), poly))
        self.assertFalse(point_in_polygon(Point2D(6000, 2500), poly))
        self.assertFalse(point_in_polygon(Point2D(-100, 2500), poly))

    def test_05_polygons_overlap(self):
        """Verify overlap detection between two distinct room polygons."""
        poly_a = [(0.0, 0.0), (4000.0, 0.0), (4000.0, 4000.0), (0.0, 4000.0)]
        # Adjacent non-overlapping room
        poly_b = [(4000.0, 0.0), (8000.0, 0.0), (8000.0, 4000.0), (4000.0, 4000.0)]
        self.assertFalse(polygons_overlap(poly_a, poly_b))

        # Overlapping room
        poly_c = [(3000.0, 1000.0), (7000.0, 1000.0), (7000.0, 5000.0), (3000.0, 5000.0)]
        self.assertTrue(polygons_overlap(poly_a, poly_c))

    def test_06_degenerate_wall_detection(self):
        """Zero-length or sub-10mm walls must be flagged as blocking."""
        model = {
            "walls": [
                {"id": "w1", "start": [0, 0], "end": [5, 0], "thickness": 200}, # 5mm length!
                {"id": "w2", "start": [0, 0], "end": [4000, 0], "thickness": 200},
            ]
        }
        res = self.validator.validate(model)
        degenerate_issues = [i for i in res.issues if "Degenerate wall" in i.message]
        self.assertEqual(len(degenerate_issues), 1)
        self.assertEqual(degenerate_issues[0].severity, "blocking")
        self.assertEqual(degenerate_issues[0].entity_id, "w1")

    def test_07_wall_junction_analysis(self):
        """Classify L-junctions, T-junctions, Cross-junctions and disconnected ends."""
        # 4 boundary walls forming closed rectangle (4 L-junctions) + 1 interior partition (2 T-junctions)
        model = {
            "envelope": {"width": 8000, "depth": 6000, "origin": [0, 0]},
            "walls": [
                {"id": "w_south", "start": [0, 0], "end": [8000, 0], "thickness": 200},
                {"id": "w_east", "start": [8000, 0], "end": [8000, 6000], "thickness": 200},
                {"id": "w_north", "start": [8000, 6000], "end": [0, 6000], "thickness": 200},
                {"id": "w_west", "start": [0, 6000], "end": [0, 0], "thickness": 200},
                # Interior partition T-junctioning at south and north walls
                {"id": "w_part", "start": [4000, 0], "end": [4000, 6000], "thickness": 100},
            ]
        }
        res = self.validator.validate(model)
        self.assertTrue(res.summary["junction_counts"]["L-junction"] >= 4)
        self.assertTrue(res.summary["junction_counts"]["T-junction"] >= 2)
        # No disconnected endpoints
        self.assertEqual(res.summary["junction_counts"]["disconnected_endpoints"], 0)

    def test_08_disconnected_wall_endpoint_warning(self):
        """A wall floating in space without connecting to other walls should be flagged."""
        model = {
            "walls": [
                {"id": "w_free", "start": [1000, 1000], "end": [3000, 1000], "thickness": 100}
            ]
        }
        res = self.validator.validate(model)
        self.assertGreater(res.summary["junction_counts"]["disconnected_endpoints"], 0)
        disconnected = [i for i in res.issues if "disconnected endpoint" in i.message]
        self.assertEqual(len(disconnected), 2)
        self.assertEqual(disconnected[0].severity, "warning")

    def test_09_opening_corner_clearance_warning(self):
        """Openings placed closer than 50mm to a corner should trigger a warning."""
        model = {
            "walls": [
                {"id": "w1", "start": [0, 0], "end": [4000, 0], "thickness": 200}
            ],
            "openings": [
                {
                    "id": "d1",
                    "wallId": "w1",
                    "type": "door",
                    "distanceFromStart": 20.0, # < 50mm from start!
                    "width": 900.0,
                    "swing": "inward-right"
                }
            ]
        }
        res = self.validator.validate(model)
        clearance_issues = [i for i in res.issues if "Corner clearance" in i.message]
        self.assertGreaterEqual(len(clearance_issues), 1)
        self.assertEqual(clearance_issues[0].severity, "warning")

    def test_10_opening_exceeding_wall_length_blocking(self):
        """Opening wider than or placed beyond host wall must be flagged as blocking."""
        model = {
            "walls": [
                {"id": "w1", "start": [0, 0], "end": [2000, 0], "thickness": 200}
            ],
            "openings": [
                {
                    "id": "d_oversize",
                    "wallId": "w1",
                    "type": "door",
                    "distanceFromStart": 1500.0,
                    "width": 1000.0, # 1500 + 1000 = 2500 > 2000!
                    "swing": "inward-right"
                }
            ]
        }
        res = self.validator.validate(model)
        oversize = [i for i in res.issues if "extends beyond host wall" in i.message]
        self.assertEqual(len(oversize), 1)
        self.assertEqual(oversize[0].severity, "blocking")

    def test_11_overlapping_openings_on_same_wall(self):
        """Two openings occupying overlapping intervals on the same wall must be flagged."""
        model = {
            "walls": [
                {"id": "w1", "start": [0, 0], "end": [5000, 0], "thickness": 200}
            ],
            "openings": [
                {"id": "d1", "wallId": "w1", "type": "door", "distanceFromStart": 500, "width": 900},
                {"id": "d2", "wallId": "w1", "type": "door", "distanceFromStart": 1000, "width": 900}, # overlaps d1 [500..1400]
            ]
        }
        res = self.validator.validate(model)
        overlaps = [i for i in res.issues if "overlaps with opening" in i.message]
        self.assertEqual(len(overlaps), 1)
        self.assertEqual(overlaps[0].severity, "blocking")

    def test_12_room_envelope_containment(self):
        """Rooms extending outside the bounding envelope must be flagged as major."""
        model = {
            "envelope": {"width": 5000, "depth": 5000, "origin": [0, 0]},
            "rooms": [
                {
                    "id": "r1",
                    "name": "Overextended Room",
                    "boundaryCorners": [
                        [0, 0], [6000, 0], [6000, 4000], [0, 4000] # x=6000 exceeds envelope 5000
                    ]
                }
            ]
        }
        res = self.validator.validate(model)
        containment = [i for i in res.issues if "exceeds building envelope" in i.message]
        self.assertGreaterEqual(len(containment), 1)
        self.assertEqual(containment[0].severity, "major")

    def test_13_multi_storey_filtering(self):
        """Geometry validation correctly filters elements by level."""
        model = {
            "envelope": {"width": 8000, "depth": 6000, "origin": [0, 0]},
            "walls": [
                {"id": "w_g1", "level": "ground-floor", "start": [0, 0], "end": [8000, 0], "thickness": 200},
                {"id": "w_f1", "level": "first-floor", "start": [0, 0], "end": [5, 0], "thickness": 200}, # degenerate on first floor
            ]
        }
        # Validating ground floor should NOT report degenerate wall from first floor
        res_gf = self.validator.validate(model, level_filter="ground-floor")
        degenerate_gf = [i for i in res_gf.issues if "Degenerate wall" in i.message]
        self.assertEqual(len(degenerate_gf), 0)

        # Validating first floor should report degenerate wall
        res_ff = self.validator.validate(model, level_filter="first-floor")
        degenerate_ff = [i for i in res_ff.issues if "Degenerate wall" in i.message]
        self.assertEqual(len(degenerate_ff), 1)


if __name__ == "__main__":
    unittest.main()
