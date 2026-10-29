"""
Sketch-to-CAD Deterministic Drawing Generator
Translates an approved floor-plan model into a verified, layered CAD drawing (DXF + PNG)
via CADCraft MCP, with integrated reusable architectural element blocks and floor finishes.
"""

import os
import sys
import json
import math
import subprocess
from typing import Dict, List, Optional, Tuple, Any, Union

from element_library import (
    ELEMENT_CATALOG,
    ELEMENT_LAYERS,
    get_element_definition,
    validate_element_instance,
    register_cad_block,
    insert_cad_element,
    create_floor_finish_hatch,
)

CADCRAFT_CLI_DEFAULT = r"C:\Program Files\CADCraft\cadcraft-cli.exe"


class ApprovalGateError(Exception):
    """Raised when attempting to draft an unapproved model or proposed element."""
    pass


class CADCraftClient:
    """Headless stdio JSON-RPC MCP client for CADCraft CLI engine."""

    def __init__(self, cli_path: str = CADCRAFT_CLI_DEFAULT):
        if not os.path.exists(cli_path):
            raise FileNotFoundError(f"CADCraft CLI executable not found at '{cli_path}'")
        self.cli_path = cli_path
        self.proc = subprocess.Popen(
            [cli_path, "mcp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8"
        )
        self.msg_id = 0
        self._initialize()

    def _initialize(self):
        init_req = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "sketch-to-cad-engine", "version": "1.1.0"}
            }
        }
        resp = self._send(init_req)
        # Send initialized notification
        self._notify("notifications/initialized", {})

    def _next_id(self) -> int:
        self.msg_id += 1
        return self.msg_id

    def _send(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        body = json.dumps(payload)
        self.proc.stdin.write(body + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            err = self.proc.stderr.read()
            raise RuntimeError(f"CADCraft MCP engine closed pipe unexpectedly: {err}")
        return json.loads(line)

    def _notify(self, method: str, params: Dict[str, Any]):
        body = json.dumps({"jsonrpc": "2.0", "method": method, "params": params})
        self.proc.stdin.write(body + "\n")
        self.proc.stdin.flush()

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        req = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        resp = self._send(req)
        if "error" in resp:
            raise RuntimeError(f"CADCraft MCP error in tool '{tool_name}': {resp['error']}")
        result = resp.get("result", {})
        content = result.get("content", [])
        if content and isinstance(content, list) and "text" in content[0]:
            try:
                return json.loads(content[0]["text"])
            except json.JSONDecodeError:
                return content[0]["text"]
        return result

    def new_drawing(self, metric: bool = True) -> Dict[str, Any]:
        return self.call_tool("new_drawing", {"metric": metric})

    def execute(self, command: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self.call_tool("execute", {"command": command, "params": params or {}})

    def inspect_drawing(self, entities: bool = True) -> Dict[str, Any]:
        return self.call_tool("inspect_drawing", {"entities": entities})

    def save(self, path: str) -> Dict[str, Any]:
        return self.call_tool("save", {"path": path})

    def render(self, path: Optional[str] = None, fit: bool = True) -> Any:
        args: Dict[str, Any] = {"fit": fit}
        if path:
            args["path"] = path
        return self.call_tool("render", args)

    def close(self):
        try:
            self.proc.terminate()
            self.proc.wait(timeout=2)
        except Exception:
            pass


class DrawingGenerator:
    """Compiles and executes an approved floor-plan model into CADCraft vector drafting."""

    def __init__(self, client: Optional[CADCraftClient] = None):
        self.client = client
        self.warnings: List[str] = []
        self.errors: List[str] = []

    def validate_preflight(self, model: Dict[str, Any]):
        """Enforces the Approval Gate, envelope bounds, and element validation."""
        self.warnings.clear()
        self.errors.clear()

        # 1. Approval Gate
        if model.get("status") != "approved":
            raise ApprovalGateError(
                f"Approval Gate Violation: Model status is '{model.get('status')}'. "
                f"CAD drafting must not proceed without explicit human approval."
            )

        envelope = model.get("envelope", {})
        env_w = envelope.get("width", 0.0)
        env_d = envelope.get("depth", 0.0)
        if env_w <= 0 or env_d <= 0:
            raise ValueError(f"Invalid envelope bounds: width={env_w}, depth={env_d}")

        # 2. Elements validation
        elements = model.get("elements", [])
        seen_element_ids = set()
        for elem in elements:
            elem_id = elem.get("id")
            if elem_id in seen_element_ids:
                self.errors.append(f"Duplicate element ID: '{elem_id}'")
            seen_element_ids.add(elem_id)

            # Validate instance against library rules
            is_valid, validation_errors = validate_element_instance(elem)
            if not is_valid:
                for v_err in validation_errors:
                    if "requires explicit human approval" in v_err:
                        raise ApprovalGateError(v_err)
                    self.errors.append(f"Element '{elem_id}': {v_err}")

            # Envelope boundary check
            pos = elem.get("position", [0, 0])
            if isinstance(pos, (list, tuple)) and len(pos) == 2:
                x, y = pos[0], pos[1]
                if x < 0 or x > env_w or y < 0 or y > env_d:
                    self.warnings.append(
                        f"Element '{elem_id}' at position [{x}, {y}] falls outside exterior envelope [0..{env_w}, 0..{env_d}]."
                    )

        # 3. Finishes validation
        finishes = model.get("finishes", [])
        for fin in finishes:
            fin_id = fin.get("id")
            bound = fin.get("boundary", [])
            if len(bound) < 2:
                self.errors.append(f"Finish '{fin_id}': boundary must contain at least 2 points.")

        if self.errors:
            raise ValueError(f"Pre-flight validation failed with {len(self.errors)} errors: {'; '.join(self.errors)}")

    def build_drawing(
        self,
        model: Dict[str, Any],
        output_dxf_path: str,
        output_png_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Executes full drawing construction in CADCraft."""
        self.validate_preflight(model)

        owns_client = False
        if self.client is None:
            self.client = CADCraftClient()
            owns_client = True

        try:
            c = self.client

            # Stage 1: New Drawing Session
            c.new_drawing(metric=True)

            # Stage 2: Create Standard AIA Layers
            all_layers = [
                ("A-WALL-EXTR", "cyan"),
                ("A-WALL-INTR", "green"),
                ("A-DOOR", "yellow"),
                ("A-GLAZ", "blue"),
                ("A-FURN", "green"),
                ("A-FIXT", "8"),
                ("A-STAIR", "yellow"),
                ("A-COLS", "cyan"),
                ("A-FLOR-FIN", "8"),
                ("A-ANNO-TEXT", "red"),
                ("A-ANNO-DIMS", "magenta"),
            ]
            for lay_name, lay_col in all_layers:
                c.execute("layer.new", {"name": lay_name, "color": lay_col})

            # Configure dimension style
            c.execute("dimstyle.new", {
                "name": "Arch",
                "textHeight": 180.0,
                "arrowSize": 140.0,
                "extExtend": 120.0,
                "extOffset": 60.0,
                "current": True
            })

            # Stage 3: Draw Walls & Jambs
            self._draw_walls_and_openings(c, model)

            # Stage 4: Draw Doors & Windows
            self._draw_doors_and_windows(c, model)

            # Stage 5: Register and Insert Architectural Elements
            self._insert_elements(c, model)

            # Stage 6: Apply Floor Finishes & Hatches
            self._apply_finishes(c, model)

            # Stage 7: Draw Room Text Labels
            self._draw_room_labels(c, model)

            # Stage 8: Draw Dimension Chains
            self._draw_dimensions(c, model)

            # Stage 9: Frame View Extents
            c.execute("zoom", {"mode": "extents"})

            # Stage 10: Save Deliverables
            os.makedirs(os.path.dirname(os.path.abspath(output_dxf_path)), exist_ok=True)
            c.save(output_dxf_path)

            if output_png_path:
                os.makedirs(os.path.dirname(os.path.abspath(output_png_path)), exist_ok=True)
                c.save(output_png_path)

            # Inspect and return validation result
            inspection = c.inspect_drawing(entities=True)
            result = {
                "status": "PASSED",
                "dxfPath": output_dxf_path,
                "pngPath": output_png_path,
                "entityCount": inspection.get("entityCount", 0),
                "counts": inspection.get("counts", {}),
                "blocks": inspection.get("blocks", []),
                "layers": [lay["name"] for lay in inspection.get("layers", [])],
                "extents": inspection.get("extents"),
                "warnings": list(self.warnings),
                "errors": list(self.errors)
            }
            return result

        finally:
            if owns_client:
                c.close()
                self.client = None

    def _draw_walls_and_openings(self, c: CADCraftClient, model: Dict[str, Any]):
        """Generates double-line walls with clean opening cuts and transverse jamb end-caps."""
        openings_by_id = {op["id"]: op for op in model.get("openings", [])}

        for wall in model.get("walls", []):
            layer = wall.get("layer", "A-WALL-EXTR")
            c.execute("layer.current", {"name": layer})

            start = wall["start"]
            end = wall["end"]
            thickness = float(wall.get("thickness", 200.0))
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            length = math.hypot(dx, dy)
            if length == 0:
                continue

            ux = dx / length
            uy = dy / length
            # Normal perpendicular vector (left-hand normal)
            nx = -uy * (thickness / 2.0)
            ny = ux * (thickness / 2.0)

            wall_openings = []
            for op_id in wall.get("openingIds", []):
                if op_id in openings_by_id:
                    op = openings_by_id[op_id]
                    op_center = op["center"]
                    # Project center onto wall axis
                    op_t = (op_center[0] - start[0]) * ux + (op_center[1] - start[1]) * uy
                    op_w = float(op.get("width", 900.0))
                    wall_openings.append({
                        "id": op_id,
                        "t1": max(0.0, op_t - op_w / 2.0),
                        "t2": min(length, op_t + op_w / 2.0),
                        "type": op.get("type", "door")
                    })

            wall_openings.sort(key=lambda o: o["t1"])

            # Segments of solid wall
            current_t = 0.0
            for op in wall_openings:
                if op["t1"] > current_t:
                    self._draw_wall_segment(c, start, ux, uy, nx, ny, current_t, op["t1"])
                # Transverse jamb end-caps sealing the wall cavity at opening
                p1_out = [start[0] + op["t1"] * ux + nx, start[1] + op["t1"] * uy + ny]
                p1_in = [start[0] + op["t1"] * ux - nx, start[1] + op["t1"] * uy - ny]
                p2_out = [start[0] + op["t2"] * ux + nx, start[1] + op["t2"] * uy + ny]
                p2_in = [start[0] + op["t2"] * ux - nx, start[1] + op["t2"] * uy - ny]
                c.execute("line", {"points": [p1_out, p1_in]})
                c.execute("line", {"points": [p2_out, p2_in]})
                current_t = op["t2"]

            if current_t < length:
                self._draw_wall_segment(c, start, ux, uy, nx, ny, current_t, length)

    def _draw_wall_segment(self, c: CADCraftClient, start, ux, uy, nx, ny, t1, t2):
        p1_out = [start[0] + t1 * ux + nx, start[1] + t1 * uy + ny]
        p2_out = [start[0] + t2 * ux + nx, start[1] + t2 * uy + ny]
        p1_in = [start[0] + t1 * ux - nx, start[1] + t1 * uy - ny]
        p2_in = [start[0] + t2 * ux - nx, start[1] + t2 * uy - ny]
        c.execute("line", {"points": [p1_out, p2_out]})
        c.execute("line", {"points": [p1_in, p2_in]})

    def _draw_doors_and_windows(self, c: CADCraftClient, model: Dict[str, Any]):
        """Generates doors with 90 deg swing arcs on A-DOOR and windows on A-GLAZ."""
        walls_by_id = {w["id"]: w for w in model.get("walls", [])}

        for op in model.get("openings", []):
            op_type = op.get("type", "door")
            center = op["center"]
            width = float(op.get("width", 900.0))
            wall = walls_by_id.get(op.get("wallId"))

            # Determine wall orientation
            if wall:
                dx = wall["end"][0] - wall["start"][0]
                dy = wall["end"][1] - wall["start"][1]
                wall_len = math.hypot(dx, dy)
                ux = dx / wall_len if wall_len > 0 else 1.0
                uy = dy / wall_len if wall_len > 0 else 0.0
            else:
                ux, uy = 1.0, 0.0

            if op_type == "door":
                c.execute("layer.current", {"name": "A-DOOR"})
                # Door hinge at center - width/2 along wall
                hx = center[0] - (width / 2.0) * ux
                hy = center[1] - (width / 2.0) * uy
                # Perpendicular direction for swing
                nx, ny = -uy, ux
                leaf_end = [hx + width * nx, hy + width * ny]
                c.execute("line", {"points": [[hx, hy], leaf_end]})
                
                # Compute swing arc angles in degrees
                base_angle = math.degrees(math.atan2(uy, ux))
                swing_start = base_angle
                swing_end = base_angle + 90.0
                c.execute("arc", {
                    "center": [hx, hy],
                    "radius": width,
                    "start": swing_start,
                    "end": swing_end
                })

            elif op_type == "window":
                c.execute("layer.current", {"name": "A-GLAZ"})
                half_w = width / 2.0
                p_left = [center[0] - half_w * ux, center[1] - half_w * uy]
                p_right = [center[0] + half_w * ux, center[1] + half_w * uy]
                # Centerline glass pane
                c.execute("line", {"points": [p_left, p_right]})

    def _insert_elements(self, c: CADCraftClient, model: Dict[str, Any]):
        """Registers required CAD blocks and inserts instances."""
        elements = model.get("elements", [])
        if not elements:
            return

        # Query existing blocks in active drawing
        drawing_info = c.inspect_drawing(entities=False)
        existing_blocks = drawing_info.get("blocks", [])

        # Unique block IDs needed
        needed_block_ids = {elem["blockId"] for elem in elements if elem.get("blockId")}

        # Register missing blocks
        for b_id in needed_block_ids:
            if b_id in ELEMENT_CATALOG:
                register_cad_block(c.execute, b_id, existing_blocks=existing_blocks)
                existing_blocks.append(b_id)
            else:
                self.warnings.append(f"Block ID '{b_id}' not found in catalog; skipping registration.")

        # Insert instances
        for elem in elements:
            b_id = elem["blockId"]
            if b_id not in ELEMENT_CATALOG:
                continue
            pos = elem.get("position", [0.0, 0.0])
            rot = float(elem.get("rotation", 0.0))
            scale = elem.get("scale", 1.0)
            insert_cad_element(c.execute, b_id, at=pos, rotation=rot, scale=scale, existing_blocks=existing_blocks)

    def _apply_finishes(self, c: CADCraftClient, model: Dict[str, Any]):
        """Applies floor finishes and tile grid hatches on A-FLOR-FIN."""
        finishes = model.get("finishes", [])
        if not finishes:
            return

        for fin in finishes:
            boundary = fin.get("boundary", [])
            pattern = "ANSI37" if fin.get("pattern") in ("tile_grid", None) else "NET"
            scale = float(fin.get("tileSize", 300.0)) / 15.0  # Scale factor for CAD hatch pattern
            create_floor_finish_hatch(c.execute, boundary, pattern=pattern, scale=scale)

    def _draw_room_labels(self, c: CADCraftClient, model: Dict[str, Any]):
        """Places centered room labels on A-ANNO-TEXT."""
        c.execute("layer.current", {"name": "A-ANNO-TEXT"})
        for room in model.get("rooms", []):
            name = room.get("name", "ROOM")
            pos = room.get("labelPosition", [0.0, 0.0])
            area = room.get("approximateArea")
            c.execute("text", {
                "at": pos,
                "text": name,
                "height": 180.0,
                "justify": "MC"
            })
            if area is not None:
                c.execute("text", {
                    "at": [pos[0], pos[1] - 250.0],
                    "text": f"{area:.1f} m2",
                    "height": 130.0,
                    "justify": "MC"
                })

    def _draw_dimensions(self, c: CADCraftClient, model: Dict[str, Any]):
        """Draws dimension chains on A-ANNO-DIMS."""
        c.execute("layer.current", {"name": "A-ANNO-DIMS"})
        for dim in model.get("dimensions", []):
            p1 = dim["p1"]
            p2 = dim["p2"]
            at = dim["at"]
            text = str(dim.get("text", ""))
            
            # Determine horizontal vs vertical
            dx = abs(p2[0] - p1[0])
            dy = abs(p2[1] - p1[1])
            is_vertical = dy > dx

            params = {
                "p1": p1,
                "p2": p2,
                "at": at,
                "text": text
            }
            if is_vertical:
                params["rotation"] = 90.0

            c.execute("dimlinear", params)


def main():
    """CLI Entry point for generating CAD drawings from model JSON."""
    import argparse
    parser = argparse.ArgumentParser(description="Sketch-to-CAD Drawing Generator")
    parser.add_argument("--model", required=True, help="Path to input floor-plan-model.json")
    parser.add_argument("--output-dxf", required=True, help="Destination DXF path")
    parser.add_argument("--output-png", help="Destination PNG preview path")
    parser.add_argument("--cli", default=CADCRAFT_CLI_DEFAULT, help="Path to cadcraft-cli executable")
    args = parser.parse_args()

    with open(args.model, "r", encoding="utf-8") as f:
        model = json.load(f)

    client = CADCraftClient(cli_path=args.cli)
    gen = DrawingGenerator(client=client)
    res = gen.build_drawing(model, args.output_dxf, args.output_png)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
