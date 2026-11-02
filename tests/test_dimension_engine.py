"""
Test Suite for Architectural Dimensioning & Annotation Engine (Milestone 11).
Validates:
1. DimensionStyle properties and precision standards.
2. Clean integer millimeter formatting without floating-point artifacts.
3. Outermost overall footprint dimensions generation (South width, West depth).
4. Middle-tier chained exterior dimensions around openings and wall segments.
5. Internal room clear span dimension callouts (width x depth in meters and mm).
6. Collision detection for text overlap, room label crossing, and door swing interference.
7. Automated collision resolution via placement offset staggering.
"""

from __future__ import annotations

import unittest

from scripts.dimension_engine import (
    DimensionCollision,
    DimensionEngine,
    DimensionEntity,
    DimensionStyle,
)


class TestDimensionEngine(unittest.TestCase):
    """Unit tests for the architectural dimensioning and annotation engine."""

    def setUp(self):
        self.style = DimensionStyle()
        self.engine = DimensionEngine(self.style)

    def test_01_dimension_style_defaults(self):
        """DimensionStyle provides standard architectural metric parameters."""
        self.assertEqual(self.style.name, "Arch_Metric")
        self.assertEqual(self.style.text_height, 180.0)
        self.assertEqual(self.style.arrow_size, 140.0)
        self.assertEqual(self.style.ext_extend, 120.0)
        self.assertEqual(self.style.ext_offset, 60.0)
        self.assertEqual(self.style.units, "mm")

    def test_02_format_dimension_value_integer_mm(self):
        """Dimensions are formatted as clean integer millimeters without trailing decimals."""
        self.assertEqual(self.engine.format_dimension_value(6000.0), "6000")
        self.assertEqual(self.engine.format_dimension_value(1200.4), "1200")
        self.assertEqual(self.engine.format_dimension_value(899.9), "900")

    def test_03_generate_overall_dimensions(self):
        """Generates South width and West depth overall dimensions at specified offset."""
        envelope = {"width": 8000.0, "depth": 6000.0, "origin": [0.0, 0.0]}
        dims = self.engine.generate_overall_dimensions(envelope, offset_mm=1800.0)

        self.assertEqual(len(dims), 2)
        south_dim = next(d for d in dims if d.side == "south")
        self.assertEqual(south_dim.value_mm, 8000.0)
        self.assertEqual(south_dim.formatted_text, "8000")
        self.assertEqual(south_dim.p1, [0.0, 0.0])
        self.assertEqual(south_dim.p2, [8000.0, 0.0])
        self.assertEqual(south_dim.at, [4000.0, -1800.0])
        self.assertEqual(south_dim.rotation, 0.0)

        west_dim = next(d for d in dims if d.side == "west")
        self.assertEqual(west_dim.value_mm, 6000.0)
        self.assertEqual(west_dim.formatted_text, "6000")
        self.assertEqual(west_dim.at, [-1800.0, 3000.0])
        self.assertEqual(west_dim.rotation, 90.0)

    def test_04_generate_chained_exterior_dimensions(self):
        """Generates chained dimension string along exterior face with openings."""
        model = {
            "envelope": {"width": 6000.0, "depth": 5000.0, "origin": [0.0, 0.0]},
            "openings": [
                {"id": "win_01", "type": "window", "center": [2000.0, 0.0], "width": 1200.0},
            ],
            "walls": [],
        }
        chained = self.engine.generate_chained_exterior_dimensions(model, offset_mm=900.0)
        self.assertEqual(len(chained), 3)

        # Segment 1: from x=0 to x=1400 (jamb left = 2000 - 600 = 1400)
        self.assertEqual(chained[0].value_mm, 1400.0)
        # Segment 2: opening width = 1200
        self.assertEqual(chained[1].value_mm, 1200.0)
        # Segment 3: from x=2600 to x=6000 (length = 3400)
        self.assertEqual(chained[2].value_mm, 3400.0)
        # Total sum must equal building width
        total = sum(d.value_mm for d in chained)
        self.assertEqual(total, 6000.0)

    def test_05_calculate_internal_room_callouts(self):
        """Calculates internal room clear span dimensions in meters and mm."""
        model = {
            "rooms": [
                {
                    "id": "room_living",
                    "name": "LIVING ROOM",
                    "boundaryCorners": [[0, 0], [4000, 0], [4000, 5000], [0, 5000]],
                    "labelPosition": [2000, 2500],
                }
            ]
        }
        callouts = self.engine.calculate_internal_room_callouts(model)
        self.assertEqual(len(callouts), 1)
        c = callouts[0]
        self.assertEqual(c["roomName"], "LIVING ROOM")
        self.assertEqual(c["width_mm"], 4000)
        self.assertEqual(c["depth_mm"], 5000)
        self.assertEqual(c["formatted_m"], "4.00 x 5.00 m")
        self.assertEqual(c["formatted_mm"], "4000 x 5000 mm")

    def test_06_detect_and_resolve_dimension_collisions(self):
        """Detects dimension line collisions with room labels and resolves them via offset."""
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

        collisions = self.engine.detect_dimension_collisions([dim], room_labels=labels)
        self.assertEqual(len(collisions), 1)
        self.assertEqual(collisions[0].collision_type, "label_crossing")

        # Resolve collisions
        resolved = self.engine.resolve_collisions([dim], room_labels=labels)
        self.assertEqual(len(resolved), 1)
        # Point 'at' y-coordinate should have been moved away
        self.assertLess(resolved[0].at[1], 2300.0)


if __name__ == "__main__":
    unittest.main()
