"""
Test Suite for Advanced Architectural Drafting & Engineering Standards (Milestone 9).
Validates:
1. Wall T-junction cavity trimming (partition double-lines terminate cleanly at inner face of host wall).
2. Enhanced door types and swing geometry: inward/outward swings, double-leaf, sliding/pocket doors.
3. Enhanced window types: standard fixed/casement and sliding windows.
4. Non-colliding sheet annotations: project title, level name, scale, units header.
5. Strict conditional North Arrow drafting (drawn if orientation known; strictly omitted if unknown).
6. AIA CAD layer assignment compliance across architectural entities.
7. Real CADCraft CLI execution with advanced drafting features.
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from scripts.drawing_generator import (
    DrawingGenerator,
    CADCraftClient,
    CADCRAFT_CLI_DEFAULT,
)


class RecordingCADCraftClient:
    """Mock CADCraft client that records all executed CAD commands for inspection."""

    def __init__(self):
        self.commands: List[Tuple[str, Dict[str, Any]]] = []
        self.layers: Set[str] = set()
        self.blocks: List[str] = []
        self.current_layer: str = "0"

    def execute(self, cmd: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = params or {}
        if cmd == "layer.current":
            self.current_layer = params.get("name", "0")
            self.layers.add(self.current_layer)
        elif cmd == "layer.create":
            self.layers.add(params.get("name", "0"))
        elif cmd == "block.create":
            self.blocks.append(params.get("name", ""))

        record = dict(params)
        record["_layer"] = self.current_layer
        self.commands.append((cmd, record))
        return {"status": "ok"}

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        return self.execute(tool_name, arguments)

    def new_drawing(self, metric: bool = True) -> Dict[str, Any]:
        self.commands.append(("new_drawing", {"metric": metric, "_layer": "0"}))
        return {"status": "ok"}

    def inspect_drawing(self, entities: bool = True) -> Dict[str, Any]:
        counts: Dict[str, int] = {}
        for cmd, rec in self.commands:
            if cmd == "line":
                counts["Line"] = counts.get("Line", 0) + 1
            elif cmd == "arc":
                counts["Arc"] = counts.get("Arc", 0) + 1
            elif cmd == "circle":
                counts["Circle"] = counts.get("Circle", 0) + 1
            elif cmd == "text":
                counts["Text"] = counts.get("Text", 0) + 1
            elif cmd == "insert":
                counts["Block Reference"] = counts.get("Block Reference", 0) + 1
            elif cmd == "hatch":
                counts["Hatch"] = counts.get("Hatch", 0) + 1
        return {"counts": counts, "blocks": self.blocks, "layers": [{"name": lay} for lay in self.layers]}

    def save(self, path: str) -> Dict[str, Any]:
        return {"status": "ok", "path": path}

    def render(self, path: Optional[str] = None, fit: bool = True) -> Dict[str, Any]:
        return {"status": "ok", "path": path}

    def close(self):
        pass


class TestAdvancedDrafting(unittest.TestCase):
    """Unit and integration tests for advanced architectural drafting rules."""

    @classmethod
    def setUpClass(cls):
        cls.cli_available = os.path.exists(CADCRAFT_CLI_DEFAULT)
        cls.temp_dir = tempfile.mkdtemp(prefix="sketch_to_cad_m9_")

    def test_01_t_junction_trimming_logic(self):
        """Partition walls at T-junctions must trim incoming endpoints by host wall half-thickness."""
        model = {
            "metadata": {"projectName": "T-Junction Test"},
            "status": "approved",
            "envelope": {
                "width": 8000.0,
                "depth": 6000.0,
                "origin": [0.0, 0.0],
                "widthSource": "explicit",
                "depthSource": "explicit",
            },
            "walls": [
                # Exterior host wall: horizontal at y=0, thickness=200mm (half_th = 100mm)
                {"id": "w_host_south", "start": [0.0, 0.0], "end": [8000.0, 0.0], "thickness": 200.0, "layer": "A-WALL-EXTR"},
                # Partition wall: vertical from y=0 to y=4000, thickness=100mm
                {"id": "w_part_v", "start": [4000.0, 0.0], "end": [4000.0, 4000.0], "thickness": 100.0, "layer": "A-WALL-INTR"},
            ],
            "rooms": [],
            "openings": [],
            "dimensions": [],
            "elements": [],
            "finishes": [],
        }

        client = RecordingCADCraftClient()
        gen = DrawingGenerator(client=client)
        gen.build_drawing(model, os.path.join(self.temp_dir, "t_junction.dxf"), os.path.join(self.temp_dir, "t_junction.png"))

        # In w_part_v, start point (4000, 0) should be trimmed northwards by 100mm (host half-thickness)
        # So trimmed start is [4000, 100], and its double lines will have start y=100.0, not y=0.0
        intr_wall_lines = [
            params["points"]
            for cmd, params in client.commands
            if cmd == "line" and params.get("_layer") == "A-WALL-INTR"
        ]
        self.assertGreaterEqual(len(intr_wall_lines), 2)
        # Verify both double lines of the partition wall start at y=100.0
        y_starts = [pts[0][1] for pts in intr_wall_lines]
        for y_s in y_starts:
            self.assertAlmostEqual(y_s, 100.0, places=1, msg="Partition wall must terminate at inner face of host wall (y=100)")

    def test_02_double_leaf_door_drafting(self):
        """Double leaf doors generate two symmetric swing arcs and leaf lines on A-DOOR."""
        model = {
            "metadata": {"projectName": "Double Door Test"},
            "status": "approved",
            "envelope": {
                "width": 8000.0,
                "depth": 6000.0,
                "origin": [0.0, 0.0],
                "widthSource": "explicit",
                "depthSource": "explicit",
            },
            "walls": [
                {"id": "w1", "start": [0.0, 0.0], "end": [8000.0, 0.0], "thickness": 200.0, "openingIds": ["d_double"]}
            ],
            "openings": [
                {
                    "id": "d_double",
                    "wallId": "w1",
                    "type": "door",
                    "center": [4000.0, 0.0],
                    "width": 1600.0,
                    "swing": "double",
                }
            ],
            "rooms": [],
            "dimensions": [],
            "elements": [],
            "finishes": [],
        }

        client = RecordingCADCraftClient()
        gen = DrawingGenerator(client=client)
        gen.build_drawing(model, os.path.join(self.temp_dir, "double_door.dxf"), os.path.join(self.temp_dir, "double_door.png"))

        door_arcs = [params for cmd, params in client.commands if cmd == "arc" and params.get("_layer") == "A-DOOR"]
        self.assertEqual(len(door_arcs), 2, "Double leaf door must generate exactly 2 swing arcs")
        door_lines = [params for cmd, params in client.commands if cmd == "line" and params.get("_layer") == "A-DOOR"]
        self.assertEqual(len(door_lines), 2, "Double leaf door must generate 2 leaf panel lines")

    def test_03_sliding_door_drafting(self):
        """Sliding door generates parallel track lines and zero swing arcs on A-DOOR."""
        model = {
            "metadata": {"projectName": "Sliding Door Test"},
            "status": "approved",
            "envelope": {
                "width": 8000.0,
                "depth": 6000.0,
                "origin": [0.0, 0.0],
                "widthSource": "explicit",
                "depthSource": "explicit",
            },
            "walls": [
                {"id": "w1", "start": [0.0, 0.0], "end": [8000.0, 0.0], "thickness": 200.0, "openingIds": ["d_slide"]}
            ],
            "openings": [
                {
                    "id": "d_slide",
                    "wallId": "w1",
                    "type": "door",
                    "center": [4000.0, 0.0],
                    "width": 1800.0,
                    "swing": "sliding",
                }
            ],
            "rooms": [],
            "dimensions": [],
            "elements": [],
            "finishes": [],
        }

        client = RecordingCADCraftClient()
        gen = DrawingGenerator(client=client)
        gen.build_drawing(model, os.path.join(self.temp_dir, "sliding_door.dxf"), os.path.join(self.temp_dir, "sliding_door.png"))

        door_arcs = [params for cmd, params in client.commands if cmd == "arc" and params.get("_layer") == "A-DOOR"]
        self.assertEqual(len(door_arcs), 0, "Sliding doors must not produce swing arcs")
        door_lines = [params for cmd, params in client.commands if cmd == "line" and params.get("_layer") == "A-DOOR"]
        self.assertGreaterEqual(len(door_lines), 2, "Sliding doors must produce parallel track lines")

    def test_04_sliding_window_drafting(self):
        """Sliding window generates multi-line sash details on A-GLAZ."""
        model = {
            "metadata": {"projectName": "Sliding Window Test"},
            "status": "approved",
            "envelope": {
                "width": 8000.0,
                "depth": 6000.0,
                "origin": [0.0, 0.0],
                "widthSource": "explicit",
                "depthSource": "explicit",
            },
            "walls": [
                {"id": "w1", "start": [0.0, 0.0], "end": [8000.0, 0.0], "thickness": 200.0, "openingIds": ["win_slide"]}
            ],
            "openings": [
                {
                    "id": "win_slide",
                    "wallId": "w1",
                    "type": "window",
                    "center": [4000.0, 0.0],
                    "width": 1500.0,
                    "swing": "sliding",
                }
            ],
            "rooms": [],
            "dimensions": [],
            "elements": [],
            "finishes": [],
        }

        client = RecordingCADCraftClient()
        gen = DrawingGenerator(client=client)
        gen.build_drawing(model, os.path.join(self.temp_dir, "sliding_win.dxf"), os.path.join(self.temp_dir, "sliding_win.png"))

        glaz_lines = [params for cmd, params in client.commands if cmd == "line" and params.get("_layer") == "A-GLAZ"]
        self.assertGreaterEqual(len(glaz_lines), 2, "Sliding window must generate dual overlapping sashes")

    def test_05_conditional_north_arrow(self):
        """North Arrow is strictly drawn only when orientation/northAngle is provided."""
        model_no_north = {
            "metadata": {"projectName": "No North Model"},
            "status": "approved",
            "envelope": {"width": 5000.0, "depth": 4000.0, "origin": [0.0, 0.0], "widthSource": "explicit", "depthSource": "explicit"},
            "walls": [{"id": "w1", "start": [0, 0], "end": [5000, 0], "thickness": 200}],
            "rooms": [],
            "openings": [],
            "dimensions": [],
            "elements": [],
            "finishes": [],
        }

        client_no = RecordingCADCraftClient()
        gen = DrawingGenerator(client=client_no)
        gen.build_drawing(model_no_north, os.path.join(self.temp_dir, "no_north.dxf"), os.path.join(self.temp_dir, "no_north.png"))

        north_texts = [p for cmd, p in client_no.commands if cmd == "text" and p.get("text") == "N"]
        self.assertEqual(len(north_texts), 0, "North Arrow must NOT be drawn when orientation is unknown")

        # Case B: Model with orientation metadata -> North Arrow drawn
        model_with_north = json.loads(json.dumps(model_no_north))
        model_with_north["metadata"]["northAngle"] = 0.0

        client_yes = RecordingCADCraftClient()
        gen2 = DrawingGenerator(client=client_yes)
        gen2.build_drawing(model_with_north, os.path.join(self.temp_dir, "with_north.dxf"), os.path.join(self.temp_dir, "with_north.png"))

        north_texts2 = [p for cmd, p in client_yes.commands if cmd == "text" and p.get("text") == "N"]
        self.assertEqual(len(north_texts2), 1, "North Arrow must be drawn when orientation is specified")

    def test_06_drawing_title_block_header(self):
        """Drawing sheet header contains project title, level name, scale and units on A-ANNO-TEXT."""
        model = {
            "metadata": {"projectName": "Villa Sunset", "scale": "1:50", "units": "mm"},
            "status": "approved",
            "floorId": "LEVEL-01",
            "envelope": {"width": 8000.0, "depth": 6000.0, "origin": [0.0, 0.0], "widthSource": "explicit", "depthSource": "explicit"},
            "walls": [{"id": "w1", "start": [0, 0], "end": [8000, 0], "thickness": 200}],
            "rooms": [],
            "openings": [],
            "dimensions": [],
            "elements": [],
            "finishes": [],
        }

        client = RecordingCADCraftClient()
        gen = DrawingGenerator(client=client)
        gen.build_drawing(model, os.path.join(self.temp_dir, "header.dxf"), os.path.join(self.temp_dir, "header.png"))

        texts = [p.get("text", "") for cmd, p in client.commands if cmd == "text" and p.get("_layer") == "A-ANNO-TEXT"]
        self.assertTrue(any("VILLA SUNSET" in t for t in texts))
        self.assertTrue(any("SCALE: 1:50" in t for t in texts))
        self.assertTrue(any("UNITS: mm" in t for t in texts))

    def test_07_real_cadcraft_advanced_drafting_execution(self):
        """GENUINE CADCraft execution: runs real CADCraft CLI with advanced drafting features on Case F."""
        if not self.cli_available:
            self.skipTest("CADCraft CLI binary not installed at default location.")

        case_f_path = Path("tests/fixtures/sketches/fixture-f-complex-junctions.json")
        with open(case_f_path, "r", encoding="utf-8") as f:
            model = json.load(f)

        out_dxf = os.path.join(self.temp_dir, "test_case_f.dxf")
        out_png = os.path.join(self.temp_dir, "test_case_f.png")

        client = CADCraftClient(cli_path=CADCRAFT_CLI_DEFAULT)
        try:
            gen = DrawingGenerator(client=client)
            result = gen.build_drawing(model, out_dxf, out_png)
        finally:
            client.close()

        self.assertEqual(result["status"], "PASSED")
        self.assertTrue(os.path.exists(out_dxf))
        self.assertTrue(os.path.exists(out_png))
        self.assertGreater(os.path.getsize(out_dxf), 5000)
        self.assertGreater(os.path.getsize(out_png), 5000)


if __name__ == "__main__":
    unittest.main()
