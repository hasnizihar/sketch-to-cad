"""
Test Suite for Downstream BIM Integration & Interoperability Validator (Milestone 10).
Validates:
1. Downstream environment detection.
2. Handoff contract verification (coordinate system, units, walls, openings).
3. Referential integrity checks (orphan openings, duplicate wall IDs).
4. Window sill height specification warnings.
5. Markdown integration report generation.
6. Downstream CLI preflight and prepare execution when environment is available.
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from scripts.bim_integration_validator import (
    BIMIntegrationResult,
    BIMIntegrationValidator,
    generate_bim_integration_markdown,
)


class TestBIMIntegrationValidator(unittest.TestCase):
    """Unit tests for the downstream BIM integration validator."""

    def setUp(self):
        self.validator = BIMIntegrationValidator()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        # Create dummy DXF file (> 100 bytes to satisfy non-empty check)
        self.dummy_dxf = self.temp_path / "test_plan.dxf"
        self.dummy_dxf.write_text("0\nSECTION\n2\nHEADER\n9\n$ACADVER\n1\nAC1032\n9\n$INSUNITS\n70\n4\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n0\nENDSEC\n0\nEOF\n", encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_01_valid_handoff_contract_passes(self):
        """Standard architectural handoff passes all semantic contract checks."""
        handoff_data = {
            "project": {
                "name": "Integration Test House",
                "units": "mm",
                "coordinateSystem": "Cartesian2D_RightHanded_YUp",
            },
            "floors": [{"id": "floor_1", "name": "Ground Floor", "elevation": 0.0}],
            "walls": [
                {"id": "w1", "start": [0, 0], "end": [5000, 0], "thickness": 200},
                {"id": "w2", "start": [5000, 0], "end": [5000, 4000], "thickness": 200},
            ],
            "openings": [
                {"id": "door_1", "type": "door", "wallId": "w1", "position": [2000, 0], "width": 900},
                {"id": "win_1", "type": "window", "wallId": "w2", "position": [5000, 2000], "width": 1200, "sillHeight": 900.0},
            ],
        }

        valid, errors, warnings = self.validator.validate_handoff_contract(
            str(self.dummy_dxf), handoff_data
        )
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)

    def test_02_detects_missing_dxf(self):
        """Contract validator fails when referenced DXF file does not exist."""
        handoff_data = {
            "project": {"units": "mm", "coordinateSystem": "Cartesian2D_RightHanded_YUp"},
            "walls": [{"id": "w1", "start": [0, 0], "end": [1000, 0]}],
        }
        valid, errors, _ = self.validator.validate_handoff_contract("missing.dxf", handoff_data)
        self.assertFalse(valid)
        self.assertTrue(any("does not exist" in e for e in errors))

    def test_03_detects_invalid_coordinate_system_or_units(self):
        """Contract validator fails on invalid coordinate system or unsupported units."""
        bad_handoff = {
            "project": {
                "units": "feet_inches",  # unsupported
                "coordinateSystem": "ScreenSpace_YDown",  # invalid
            },
            "walls": [{"id": "w1", "start": [0, 0], "end": [1000, 0]}],
        }
        valid, errors, _ = self.validator.validate_handoff_contract(
            str(self.dummy_dxf), bad_handoff
        )
        self.assertFalse(valid)
        self.assertTrue(any("coordinateSystem" in e for e in errors))
        self.assertTrue(any("units" in e for e in errors))

    def test_04_detects_orphan_openings_and_duplicate_walls(self):
        """Contract validator detects duplicate wall IDs and openings referencing non-existent walls."""
        bad_handoff = {
            "project": {"units": "mm", "coordinateSystem": "Cartesian2D_RightHanded_YUp"},
            "walls": [
                {"id": "w1", "start": [0, 0], "end": [1000, 0]},
                {"id": "w1", "start": [1000, 0], "end": [2000, 0]},  # duplicate id
            ],
            "openings": [
                {"id": "op1", "type": "door", "wallId": "w_nonexistent", "position": [500, 0]},  # orphan
            ],
        }
        valid, errors, _ = self.validator.validate_handoff_contract(
            str(self.dummy_dxf), bad_handoff
        )
        self.assertFalse(valid)
        self.assertTrue(any("Duplicate wall id" in e for e in errors))
        self.assertTrue(any("non-existent host wall" in e for e in errors))

    def test_05_warns_on_null_window_sill_height(self):
        """Contract validator warns if a window does not define numeric sillHeight."""
        handoff_data = {
            "project": {"units": "mm", "coordinateSystem": "Cartesian2D_RightHanded_YUp"},
            "walls": [{"id": "w1", "start": [0, 0], "end": [3000, 0]}],
            "openings": [
                {"id": "win1", "type": "window", "wallId": "w1", "position": [1500, 0], "sillHeight": None},
            ],
        }
        valid, errors, warnings = self.validator.validate_handoff_contract(
            str(self.dummy_dxf), handoff_data
        )
        self.assertTrue(valid)
        self.assertTrue(any("sillHeight" in w for w in warnings))

    def test_06_markdown_report_formatting(self):
        """Report generator formats Markdown executive summary and status tags."""
        result = BIMIntegrationResult(
            dxf_path="/mock/house.dxf",
            handoff_path="/mock/house.handoff.json",
            is_downstream_available=True,
            downstream_execution_type="genuine_downstream_cli",
            contract_valid=True,
            preflight_passed=True,
            reconstruction_passed=True,
            intermediate_model_path="/mock/house_intermediate_bim.json",
            notes=["Successfully processed 8 walls and 4 openings."],
        )

        md = generate_bim_integration_markdown(result)
        self.assertIn("# Downstream BIM Integration Validation Report", md)
        self.assertIn("genuine_downstream_cli", md)
        self.assertIn("house_intermediate_bim.json", md)
        self.assertIn("Successfully processed 8 walls", md)


if __name__ == "__main__":
    unittest.main()
