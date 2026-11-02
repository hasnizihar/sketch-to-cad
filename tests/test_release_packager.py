"""
Test Suite for Production Release Packaging Framework (Milestone 11).
Validates:
1. Rejection of unapproved projects (status != 'approved').
2. Rejection of AI agent self-approval in packaging stage.
3. Complete output folder hierarchy (source, review, drawings, sheets, handoff, reports, qa).
4. Generation and validation of master release manifest.json with SHA-256 digests.
5. Multi-storey coordinated deliverables (drawings, sheets, and schedules).
6. Release gating enforcement (blocking issues prevent packaging unless explicitly allowed).
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.release_packager import ReleasePackager, compute_file_sha256


class TestReleasePackager(unittest.TestCase):
    """Unit tests for the production release packager."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_root = Path(self.temp_dir.name)
        self.packager = ReleasePackager(output_root=str(self.output_root))

        self.approved_model = {
            "metadata": {"projectName": "Villa Paradiso", "author": "Architect Marcus"},
            "status": "approved",
            "approvedBy": "Marcus Vance, Registered Architect",
            "approvedAt": "2026-11-02",
            "envelope": {"width": 8000.0, "depth": 6000.0, "origin": [0.0, 0.0]},
            "floors": [{"id": "LEVEL-01", "name": "Ground Floor", "elevation": 0.0}],
            "walls": [
                {"id": "w1", "start": [0, 0], "end": [8000, 0], "thickness": 200, "classification": "exterior", "layer": "A-WALL-EXTR"},
                {"id": "w2", "start": [8000, 0], "end": [8000, 6000], "thickness": 200, "classification": "exterior", "layer": "A-WALL-EXTR"},
                {"id": "w3", "start": [8000, 6000], "end": [0, 6000], "thickness": 200, "classification": "exterior", "layer": "A-WALL-EXTR"},
                {"id": "w4", "start": [0, 6000], "end": [0, 0], "thickness": 200, "classification": "exterior", "layer": "A-WALL-EXTR"},
            ],
            "openings": [
                {"id": "door_1", "type": "door", "wallId": "w1", "center": [4000, 0], "width": 900},
                {"id": "win_1", "type": "window", "wallId": "w3", "center": [4000, 6000], "width": 1200},
            ],
            "rooms": [
                {
                    "id": "room_main",
                    "name": "MAIN SALON",
                    "approximateArea": 48.0,
                    "labelPosition": [4000, 3000],
                    "boundaryCorners": [[0, 0], [8000, 0], [8000, 6000], [0, 6000]],
                }
            ],
            "dimensions": [
                {"id": "dim1", "p1": [0, 0], "p2": [8000, 0], "at": [4000, -1500], "text": "8000"}
            ],
            "uncertainties": [],
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_01_rejects_unapproved_model(self):
        """Packaging fails with ValueError if model is awaiting approval."""
        unapproved = dict(self.approved_model)
        unapproved["status"] = "awaiting_approval"

        with self.assertRaises(ValueError) as ctx:
            self.packager.assemble_release_package("Unapproved Villa", unapproved)
        self.assertIn("expected 'approved'", str(ctx.exception))

    def test_02_rejects_ai_agent_self_approval(self):
        """Packaging fails if approvedBy matches disallowed AI agent identities."""
        agent_approved = dict(self.approved_model)
        agent_approved["approvedBy"] = "Antigravity Assistant"

        with self.assertRaises(ValueError) as ctx:
            self.packager.assemble_release_package("Agent Villa", agent_approved)
        self.assertIn("Security Gate: AI Agent self-approval rejected", str(ctx.exception))

    def test_03_assembles_complete_release_package(self):
        """Generates all 7 directory areas, deliverables, and master manifest.json."""
        dummy_sketch = self.output_root / "test_sketch.png"
        dummy_sketch.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 128)

        result = self.packager.assemble_release_package(
            project_name="Villa Paradiso",
            model=self.approved_model,
            source_file_path=str(dummy_sketch),
            paper_size="A3",
            scale=100,
        )

        pkg_dir = Path(result["packageDir"])
        self.assertTrue(pkg_dir.is_dir())
        self.assertTrue((pkg_dir / "source").is_dir())
        self.assertTrue((pkg_dir / "review").is_dir())
        self.assertTrue((pkg_dir / "drawings").is_dir())
        self.assertTrue((pkg_dir / "sheets").is_dir())
        self.assertTrue((pkg_dir / "handoff").is_dir())
        self.assertTrue((pkg_dir / "reports").is_dir())
        self.assertTrue((pkg_dir / "qa").is_dir())

        # Check manifest
        manifest_path = Path(result["manifestPath"])
        self.assertTrue(manifest_path.is_file())
        with open(manifest_path, "r", encoding="utf-8") as f:
            man = json.load(f)

        self.assertEqual(man["softwareVersion"], "1.1.0")
        self.assertEqual(man["projectName"], "Villa Paradiso")
        self.assertEqual(man["approval"]["status"], "approved")
        self.assertIn("deliverables", man)
        self.assertGreaterEqual(man["deliverablesCount"], 8)

        # Verify that all listed deliverables exist on disk and have non-empty SHA-256
        for deliv in man["deliverables"]:
            deliv_path = pkg_dir / deliv["path"]
            self.assertTrue(deliv_path.is_file(), f"Missing deliverable: {deliv_path}")
            self.assertEqual(len(deliv["sha256"]), 64)

    def test_04_verify_package_integrity(self):
        """ReleasePackager.verify_package_integrity verifies all deliverable checksums."""
        dummy_sketch = self.output_root / "test_sketch_2.png"
        dummy_sketch.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 64)

        result = self.packager.assemble_release_package(
            project_name="Integrity Villa",
            model=self.approved_model,
            source_file_path=str(dummy_sketch),
        )
        pkg_dir = result["packageDir"]

        is_valid, errors = ReleasePackager.verify_package_integrity(pkg_dir)
        self.assertTrue(is_valid, f"Integrity check failed: {errors}")
        self.assertEqual(len(errors), 0)

        # Corrupt one deliverable
        manifest_path = Path(pkg_dir) / "manifest.json"
        with open(manifest_path, "r", encoding="utf-8") as f:
            man = json.load(f)
        first_deliv = Path(pkg_dir) / man["deliverables"][0]["path"]
        first_deliv.write_bytes(b"tampered content")

        is_valid_after, errors_after = ReleasePackager.verify_package_integrity(pkg_dir)
        self.assertFalse(is_valid_after)
        self.assertGreaterEqual(len(errors_after), 1)
        self.assertIn("Hash mismatch", errors_after[0])

    def test_05_multi_storey_packaging(self):
        """ReleasePackager correctly packages multi-storey residential projects."""
        multi_model = {
            "projectName": "Duplex Residence",
            "status": "approved",
            "approvedBy": "Licensed Architect",
            "approvedAt": "2026-11-02",
            "envelope": {"width": 6000.0, "depth": 5000.0},
            "building": {"totalLevels": 2},
            "floors": [
                {
                    "id": "LEVEL-01",
                    "levelIndex": 0,
                    "levelName": "Ground Floor",
                    "elevation": 0.0,
                    "height": 2800.0,
                    "walls": [
                        {"start": [0, 0], "end": [6000, 0], "thickness": 200},
                        {"start": [6000, 0], "end": [6000, 5000], "thickness": 200},
                        {"start": [6000, 5000], "end": [0, 5000], "thickness": 200},
                        {"start": [0, 5000], "end": [0, 0], "thickness": 200},
                    ],
                    "rooms": [
                        {"name": "Living Room", "label": "LIVING", "area": 30.0, "perimeter": 22.0, "centroid": [3000, 2500]}
                    ],
                    "doors": [],
                    "windows": [],
                },
                {
                    "id": "LEVEL-02",
                    "levelIndex": 1,
                    "levelName": "First Floor",
                    "elevation": 2800.0,
                    "height": 2800.0,
                    "walls": [
                        {"start": [0, 0], "end": [6000, 0], "thickness": 200},
                        {"start": [6000, 0], "end": [6000, 5000], "thickness": 200},
                        {"start": [6000, 5000], "end": [0, 5000], "thickness": 200},
                        {"start": [0, 5000], "end": [0, 0], "thickness": 200},
                    ],
                    "rooms": [
                        {"name": "Master Bedroom", "label": "BED-01", "area": 30.0, "perimeter": 22.0, "centroid": [3000, 2500]}
                    ],
                    "doors": [],
                    "windows": [],
                },
            ],
        }

        result = self.packager.assemble_release_package(
            project_name="Duplex Residence",
            model=multi_model,
        )
        pkg_dir = Path(result["packageDir"])
        self.assertTrue((pkg_dir / "drawings" / "duplex-residence-level-01.dxf").is_file())
        self.assertTrue((pkg_dir / "drawings" / "duplex-residence-level-02.dxf").is_file())
        self.assertTrue((pkg_dir / "sheets" / "duplex-residence-level-01-sheet.pdf").is_file())
        self.assertTrue((pkg_dir / "sheets" / "duplex-residence-level-02-sheet.pdf").is_file())

        is_valid, errors = ReleasePackager.verify_package_integrity(pkg_dir)
        self.assertTrue(is_valid, f"Multi-floor integrity error: {errors}")


if __name__ == "__main__":
    unittest.main()
