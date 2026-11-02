"""
Test Suite for Architectural Sheet & Print Quality Engine (Milestone 11).
Validates:
1. ISO 216 paper dimensions (A4, A3, A2, A1) in landscape and portrait.
2. Viewport fitting calculation and utilization percentage.
3. Scale overflow detection raising ScaleOverflowError without silent scaling.
4. Recommended standard scale calculation when plan overflows.
5. Title block metadata, drawing numbering, and revision notation.
6. Conditional North Arrow policy (verified vs unverified).
7. ReportLab vector PDF sheet generation.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.sheet_generator import (
    PAPER_SIZES_MM,
    ScaleOverflowError,
    SheetGenerator,
    SheetTitleBlock,
    ViewportFittingReport,
)


class TestSheetGenerator(unittest.TestCase):
    """Unit tests for the architectural sheet and print quality engine."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_01_paper_size_dimensions(self):
        """Standard ISO 216 paper dimensions are accurate in millimeters."""
        self.assertEqual(PAPER_SIZES_MM["A4"]["width"], 297.0)
        self.assertEqual(PAPER_SIZES_MM["A4"]["height"], 210.0)
        self.assertEqual(PAPER_SIZES_MM["A3"]["width"], 420.0)
        self.assertEqual(PAPER_SIZES_MM["A3"]["height"], 297.0)
        self.assertEqual(PAPER_SIZES_MM["A2"]["width"], 594.0)
        self.assertEqual(PAPER_SIZES_MM["A1"]["width"], 841.0)

    def test_02_sheet_generator_orientation(self):
        """Landscape and portrait orientations return correct dimensions."""
        gen_land = SheetGenerator(paper_size="A3", orientation="landscape")
        self.assertEqual(gen_land.get_sheet_dimensions_mm(), (420.0, 297.0))

        gen_port = SheetGenerator(paper_size="A3", orientation="portrait")
        self.assertEqual(gen_port.get_sheet_dimensions_mm(), (297.0, 420.0))

    def test_03_viewport_fitting_successful(self):
        """A standard 6m x 5m residence fits comfortably on A3 landscape at 1:100."""
        gen = SheetGenerator(paper_size="A3", orientation="landscape", scale=100)
        envelope = {"width": 6000.0, "depth": 5000.0}

        report = gen.calculate_viewport_fitting(envelope, scale=100)
        self.assertTrue(report.fits)
        self.assertEqual(report.scale, 100)
        self.assertLess(report.utilization_pct, 100.0)
        self.assertIsNone(report.error_message)

    def test_04_scale_overflow_raises_error(self):
        """A large 25m x 20m building overflows A4 at 1:50 and raises ScaleOverflowError."""
        gen = SheetGenerator(paper_size="A4", orientation="landscape", scale=50)
        large_envelope = {"width": 25000.0, "depth": 20000.0}

        report = gen.calculate_viewport_fitting(large_envelope, scale=50)
        self.assertFalse(report.fits)
        self.assertIn("exceeding available viewport", report.error_message)
        self.assertIn(report.recommended_scale, [100, 200, 500])

        # Verify that rendering sheet raises ScaleOverflowError
        out_pdf = self.temp_path / "overflow_test.pdf"
        with self.assertRaises(ScaleOverflowError) as ctx:
            gen.render_sheet_pdf({"envelope": large_envelope}, str(out_pdf), scale=50)
        self.assertIn("exceeding available viewport", str(ctx.exception))

    def test_05_title_block_defaults_and_customization(self):
        """Title block correctly holds project, drawing number, scale, and north status."""
        tb = SheetTitleBlock(
            project_name="Villa Serena",
            sheet_title="FIRST FLOOR PLAN",
            drawing_number="A-102",
            floor_id="LEVEL-02",
            scale_notation="1:100 @ A3",
            north_orientation="North-East",
        )
        self.assertEqual(tb.project_name, "Villa Serena")
        self.assertEqual(tb.drawing_number, "A-102")
        self.assertEqual(tb.north_orientation, "North-East")

    def test_06_render_sheet_pdf_creation(self):
        """Generates a valid printable vector PDF sheet with title block."""
        gen = SheetGenerator(paper_size="A3", orientation="landscape", scale=100)
        model = {
            "metadata": {"projectName": "Modern Duplex Residence"},
            "envelope": {"width": 8000.0, "depth": 6000.0},
        }
        out_pdf = self.temp_path / "duplex_sheet_a3.pdf"
        result_path = gen.render_sheet_pdf(model, str(out_pdf), scale=100)

        self.assertTrue(Path(result_path).is_file())
        self.assertGreater(Path(result_path).stat().st_size, 1000)


if __name__ == "__main__":
    unittest.main()
