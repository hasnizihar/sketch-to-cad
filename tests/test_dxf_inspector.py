"""
Test Suite for Independent DXF Inspector (Milestone 10).
Validates:
1. File existence validation and SHA-256 computation.
2. DXF Header inspection ($INSUNITS, DXF version, bounding box extents).
3. Layer architecture audit (AIA standard compliance, layer 0 cleanliness).
4. Entity inventory counting (LINE, ARC, INSERT, HATCH, TEXT, DIMENSION).
5. Duplicate geometric entity detection.
6. Degenerate geometry detection (lines < 10mm).
7. Cross-consistency audit between approved model, DXF, and companion BIM handoff.
8. Markdown audit report generation.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

try:
    import ezdxf
except ImportError:
    ezdxf = None

from scripts.dxf_inspector import (
    DXFConsistencyAudit,
    DXFHeaderAudit,
    DXFInspectionReport,
    DXFInspector,
    DXFLayerAudit,
    generate_dxf_inspection_markdown,
)


class TestDXFInspector(unittest.TestCase):
    """Unit tests for the independent architectural and structural DXF inspector."""

    def setUp(self):
        self.inspector = DXFInspector()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_01_nonexistent_file_raises_error(self):
        """Inspector raises FileNotFoundError when given a non-existent path."""
        with self.assertRaises(FileNotFoundError):
            self.inspector.inspect("nonexistent_drawing.dxf")

    @unittest.skipIf(ezdxf is None, "ezdxf library is required for DXF inspection tests")
    def test_02_clean_drawing_passes_inspection(self):
        """Valid DXF drawing with millimeters and AIA layers passes inspection."""
        dxf_file = self.temp_path / "clean_plan.dxf"
        doc = ezdxf.new("R2018")
        doc.header["$INSUNITS"] = 4  # Millimeters
        msp = doc.modelspace()

        # Add valid AIA layers
        doc.layers.add("A-WALL-EXTR", color=1)
        doc.layers.add("A-DOOR", color=2)

        # Add geometry on proper layers (not on layer 0)
        msp.add_line((0, 0), (5000, 0), dxfattribs={"layer": "A-WALL-EXTR"})
        msp.add_line((5000, 0), (5000, 4000), dxfattribs={"layer": "A-WALL-EXTR"})
        msp.add_arc(center=(1000, 0), radius=900, start_angle=0, end_angle=90, dxfattribs={"layer": "A-DOOR"})

        doc.saveas(str(dxf_file))

        report = self.inspector.inspect(dxf_file)
        self.assertEqual(report.overall_status, "PASSED")
        self.assertEqual(report.header.insunits, 4)
        self.assertEqual(report.header.units_name, "Millimeters")
        self.assertTrue(report.layer_zero_clean)
        self.assertEqual(report.duplicate_entities_count, 0)
        self.assertEqual(report.degenerate_geometry_count, 0)
        self.assertEqual(report.entity_counts.get("LINE", 0), 2)
        self.assertEqual(report.entity_counts.get("ARC", 0), 1)

    @unittest.skipIf(ezdxf is None, "ezdxf library is required")
    def test_03_detects_layer_zero_pollution(self):
        """Detects geometry placed on default layer '0' and raises warning."""
        dxf_file = self.temp_path / "polluted_layer0.dxf"
        doc = ezdxf.new("R2018")
        doc.header["$INSUNITS"] = 4
        msp = doc.modelspace()

        # Place entity on layer 0
        msp.add_line((0, 0), (3000, 0), dxfattribs={"layer": "0"})
        doc.saveas(str(dxf_file))

        report = self.inspector.inspect(dxf_file)
        self.assertFalse(report.layer_zero_clean)
        self.assertIn("WARNING", report.overall_status)
        self.assertTrue(any("layer '0'" in w.lower() for w in report.warnings))

    @unittest.skipIf(ezdxf is None, "ezdxf library is required")
    def test_04_detects_duplicate_entities(self):
        """Detects duplicate lines with identical endpoints on the same layer."""
        dxf_file = self.temp_path / "duplicates.dxf"
        doc = ezdxf.new("R2018")
        doc.header["$INSUNITS"] = 4
        msp = doc.modelspace()
        doc.layers.add("A-WALL", color=1)

        # Add duplicate line
        msp.add_line((0, 0), (4000, 0), dxfattribs={"layer": "A-WALL"})
        msp.add_line((0, 0), (4000, 0), dxfattribs={"layer": "A-WALL"})
        doc.saveas(str(dxf_file))

        report = self.inspector.inspect(dxf_file)
        self.assertEqual(report.duplicate_entities_count, 1)
        self.assertTrue(any("duplicate" in w.lower() for w in report.warnings))

    @unittest.skipIf(ezdxf is None, "ezdxf library is required")
    def test_05_detects_degenerate_geometry(self):
        """Detects degenerate line segments shorter than 10mm as errors."""
        dxf_file = self.temp_path / "degenerate.dxf"
        doc = ezdxf.new("R2018")
        doc.header["$INSUNITS"] = 4
        msp = doc.modelspace()
        doc.layers.add("A-WALL", color=1)

        # 3mm line (degenerate)
        msp.add_line((0, 0), (3, 0), dxfattribs={"layer": "A-WALL"})
        doc.saveas(str(dxf_file))

        report = self.inspector.inspect(dxf_file)
        self.assertEqual(report.degenerate_geometry_count, 1)
        self.assertEqual(report.overall_status, "FAILED")
        self.assertTrue(any("degenerate" in e.lower() for e in report.errors))

    @unittest.skipIf(ezdxf is None, "ezdxf library is required")
    def test_06_model_to_dxf_cross_consistency(self):
        """Audits consistency between model entity counts and generated DXF entities."""
        dxf_file = self.temp_path / "model_audit.dxf"
        doc = ezdxf.new("R2018")
        doc.header["$INSUNITS"] = 4
        msp = doc.modelspace()
        doc.layers.add("A-WALL-EXTR", color=1)
        doc.layers.add("A-DOOR", color=2)

        # 2 wall lines
        msp.add_line((0, 0), (4000, 0), dxfattribs={"layer": "A-WALL-EXTR"})
        msp.add_line((4000, 0), (4000, 3000), dxfattribs={"layer": "A-WALL-EXTR"})

        doc.saveas(str(dxf_file))

        approved_model = {
            "walls": [
                {"id": "w1", "start": [0, 0], "end": [4000, 0]},
                {"id": "w2", "start": [4000, 0], "end": [4000, 3000]},
            ],
            "openings": [],
            "elements": [],
        }
        handoff = {
            "walls": approved_model["walls"],
            "openings": [],
        }

        report = self.inspector.inspect(dxf_file, model=approved_model, handoff=handoff)
        self.assertIsNotNone(report.consistency)
        self.assertEqual(report.consistency.model_walls_count, 2)
        self.assertEqual(report.consistency.dxf_wall_lines_count, 2)
        self.assertTrue(report.consistency.handoff_walls_match)

    def test_07_markdown_report_formatting(self):
        """Renders comprehensive Markdown report containing executive summary and entity tables."""
        header = DXFHeaderAudit(
            dxf_version="R2018",
            insunits=4,
            units_name="Millimeters",
            extents_min=[0.0, 0.0],
            extents_max=[8000.0, 6000.0],
            dimensions_span=[8000.0, 6000.0],
        )
        layers = [
            DXFLayerAudit(name="A-WALL", entity_count=12, is_standard_aia=True, is_empty=False),
            DXFLayerAudit(name="0", entity_count=0, is_standard_aia=False, is_empty=True),
        ]
        report = DXFInspectionReport(
            file_path="/mock/path/test.dxf",
            file_name="test.dxf",
            file_size_bytes=1048576,
            sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            overall_status="PASSED",
            header=header,
            layers=layers,
            entity_counts={"LINE": 12, "ARC": 4, "TEXT": 5},
            blocks_defined=["DOOR_900"],
            duplicate_entities_count=0,
            degenerate_geometry_count=0,
            layer_zero_clean=True,
            consistency=DXFConsistencyAudit(model_walls_count=6, dxf_wall_lines_count=12),
        )

        md = generate_dxf_inspection_markdown(report)
        self.assertIn("# Independent Architectural DXF Inspection Report: test.dxf", md)
        self.assertIn("Millimeters", md)
        self.assertIn("A-WALL", md)
        self.assertIn("Clean (0 entities)", md)
        self.assertIn("Model-to-DXF-to-BIM Consistency Cross-Audit", md)


if __name__ == "__main__":
    unittest.main()
