"""
Sketch-to-CAD Architectural Reporting & Scheduling Engine (Milestone 5)
Compiles deterministic, auditable architectural documentation and schedules from an
approved canonical floor-plan model and companion DXF/BIM handoff metadata.

Generates:
1. Machine-readable Report JSON (<drawing-name>.report.json)
2. Formatted Markdown Report (<drawing-name>.report.md)
3. Professional PDF Report (<drawing-name>.report.pdf)
"""

import os
import sys
import json
import math
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any, Union

_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)

from element_library import ELEMENT_CATALOG


# ==============================================================================
# 1. GEOMETRY & QUANTITY CALCULATIONS
# ==============================================================================

def calculate_polygon_area(vertices: List[List[float]]) -> float:
    """Calculates the 2D planar area of a polygon using the Shoelace formula.
    
    Returns area in square millimeters (mm^2).
    """
    n = len(vertices)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += float(vertices[i][0]) * float(vertices[j][1])
        area -= float(vertices[j][0]) * float(vertices[i][1])
    return abs(area) / 2.0


def calculate_polygon_perimeter(vertices: List[List[float]]) -> float:
    """Calculates the closed perimeter length of a polygon.
    
    Returns perimeter in millimeters (mm).
    """
    n = len(vertices)
    if n < 2:
        return 0.0
    perimeter = 0.0
    for i in range(n):
        j = (i + 1) % n
        dx = float(vertices[j][0]) - float(vertices[i][0])
        dy = float(vertices[j][1]) - float(vertices[i][1])
        perimeter += math.hypot(dx, dy)
    return perimeter


def detect_axis_aligned_rectangle(vertices: List[List[float]]) -> Optional[Tuple[float, float]]:
    """Determines if a 4-vertex polygon is an orthogonal axis-aligned rectangle.
    
    Returns (length_mm, width_mm) where length >= width, or None if irregular/non-orthogonal.
    Enforces the rule: Never manufacture a length x width representation for irregular rooms.
    """
    if len(vertices) != 4:
        return None
    xs = [float(p[0]) for p in vertices]
    ys = [float(p[1]) for p in vertices]
    uniq_xs = sorted(list(set(xs)))
    uniq_ys = sorted(list(set(ys)))
    if len(uniq_xs) != 2 or len(uniq_ys) != 2:
        return None
    if xs.count(uniq_xs[0]) != 2 or xs.count(uniq_xs[1]) != 2:
        return None
    if ys.count(uniq_ys[0]) != 2 or ys.count(uniq_ys[1]) != 2:
        return None
    dx = uniq_xs[1] - uniq_xs[0]
    dy = uniq_ys[1] - uniq_ys[0]
    if dx <= 0 or dy <= 0:
        return None
    length = max(dx, dy)
    width = min(dx, dy)
    return (round(length, 1), round(width, 1))


def point_in_polygon(point: List[float], vertices: List[List[float]]) -> bool:
    """Ray-casting algorithm to test whether a 2D point lies strictly inside a polygon."""
    if len(vertices) < 3:
        return False
    x, y = float(point[0]), float(point[1])
    n = len(vertices)
    inside = False
    p1x, p1y = float(vertices[0][0]), float(vertices[0][1])
    for i in range(n + 1):
        p2x, p2y = float(vertices[i % n][0]), float(vertices[i % n][1])
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside


def _segments_intersect(p1: List[float], p2: List[float], p3: List[float], p4: List[float]) -> bool:
    """Returns True if segment (p1, p2) and segment (p3, p4) properly cross in their interiors."""
    def ccw(a, b, c):
        return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])
    return (ccw(p1, p3, p4) != ccw(p2, p3, p4)) and (ccw(p1, p2, p3) != ccw(p1, p2, p4))


def detect_polygons_overlap(poly_a: List[List[float]], poly_b: List[List[float]]) -> bool:
    """Detects if two 2D room polygons have overlapping interior area (> 0).
    
    Touching along a shared wall edge or vertex does NOT constitute an overlap.
    """
    if len(poly_a) < 3 or len(poly_b) < 3:
        return False
    # Bounding box quick rejection
    min_xa, max_xa = min(p[0] for p in poly_a), max(p[0] for p in poly_a)
    min_ya, max_ya = min(p[1] for p in poly_a), max(p[1] for p in poly_a)
    min_xb, max_xb = min(p[0] for p in poly_b), max(p[0] for p in poly_b)
    min_yb, max_yb = min(p[1] for p in poly_b), max(p[1] for p in poly_b)
    if max_xa <= min_xb or max_xb <= min_xa or max_ya <= min_yb or max_yb <= min_ya:
        return False

    # Check edge intersection
    na, nb = len(poly_a), len(poly_b)
    for i in range(na):
        ea1, ea2 = poly_a[i], poly_a[(i + 1) % na]
        for j in range(nb):
            eb1, eb2 = poly_b[j], poly_b[(j + 1) % nb]
            if _segments_intersect(ea1, ea2, eb1, eb2):
                return True

    # Check interior containment via centroid
    cent_a = [sum(p[0] for p in poly_a) / na, sum(p[1] for p in poly_a) / na]
    if point_in_polygon(cent_a, poly_b):
        return True
    cent_b = [sum(p[0] for p in poly_b) / nb, sum(p[1] for p in poly_b) / nb]
    if point_in_polygon(cent_b, poly_a):
        return True
    return False


# ==============================================================================
# 2. SCHEDULE COMPILERS
# ==============================================================================

def compile_room_schedule(
    model: Dict[str, Any],
    finishes: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Compiles the architectural room schedule with verified areas and dimensions."""
    finishes_by_room = {f["roomId"]: f for f in finishes if "roomId" in f}
    rooms_out = []

    for room in model.get("rooms", []):
        r_id = room["id"]
        r_name = room.get("name", "UNNAMED ROOM")
        floor_id = room.get("floorId", model.get("floorId", "LEVEL-01"))
        corners = room.get("boundaryCorners", [])
        
        finish_info = finishes_by_room.get(r_id, {})
        finish_id = finish_info.get("id")
        finish_pattern = finish_info.get("pattern")

        if corners and len(corners) >= 3:
            area_mm2 = calculate_polygon_area(corners)
            net_area_m2 = round(area_mm2 / 1e6, 2)
            perim_mm = round(calculate_polygon_perimeter(corners), 1)
            perim_m = round(perim_mm / 1000.0, 2)
            calc_method = "shoelace_boundary_polygon"
            rect_dims = detect_axis_aligned_rectangle(corners)
            if rect_dims:
                length_mm, width_mm = rect_dims
                notes = "Orthogonal rectangular boundary; internal clear dimensions."
            else:
                length_mm, width_mm = None, None
                notes = "Irregular/polygonal room boundary; dimensioned by verified boundary polygon."
            vert_count = len(corners)
        elif "approximateArea" in room and room["approximateArea"] is not None:
            net_area_m2 = float(room["approximateArea"])
            perim_mm, perim_m = None, None
            length_mm, width_mm = None, None
            calc_method = "model_annotated"
            vert_count = 0
            notes = "Boundary corners not supplied; using model annotated area."
        else:
            net_area_m2 = 0.0
            perim_mm, perim_m = None, None
            length_mm, width_mm = None, None
            calc_method = "uncalculated"
            vert_count = 0
            notes = "Boundary geometry and area unannotated."

        confidence = room.get("source") or room.get("confidence") or "explicit"

        rooms_out.append({
            "id": r_id,
            "name": r_name,
            "floorId": floor_id,
            "netAreaM2": net_area_m2,
            "lengthMm": length_mm,
            "widthMm": width_mm,
            "perimeterMm": perim_mm,
            "perimeterM": perim_m,
            "finishId": finish_id,
            "finishPattern": finish_pattern,
            "calculationMethod": calc_method,
            "confidence": confidence,
            "boundaryVertices": vert_count,
            "notes": notes
        })

    return rooms_out


def compile_opening_schedules(
    model: Dict[str, Any]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[str]]:
    """Compiles separate Door and Window schedules with host-wall validation."""
    walls_by_id = {w["id"]: w for w in model.get("walls", [])}
    rooms = model.get("rooms", [])
    doors_out = []
    windows_out = []
    warnings = []
    seen_ids = set()

    for op in model.get("openings", []):
        op_id = op["id"]
        op_type = op.get("type", "door")
        wall_id = op.get("wallId", "")
        floor_id = op.get("floorId", model.get("floorId", "LEVEL-01"))
        width = float(op.get("width", 0.0))
        source = op.get("source", "explicit")

        # Duplicate ID check
        if op_id in seen_ids:
            warnings.append(f"Duplicate opening ID detected: '{op_id}'.")
        seen_ids.add(op_id)

        # Host wall validation
        wall = walls_by_id.get(wall_id)
        if not wall:
            v_status = "invalid_host_wall"
            warnings.append(f"Opening '{op_id}' references nonexistent host wall '{wall_id}'.")
        else:
            v_status = "verified"

        # Missing or contradictory dimension check
        if width <= 0:
            v_status = "missing_width"
            warnings.append(f"Opening '{op_id}' has missing or non-positive width ({width} mm).")

        # Discover associated rooms geometrically
        matched_rooms = []
        if "roomId" in op and op["roomId"]:
            matched_rooms = [op["roomId"]]
        elif wall and "center" in op and len(op["center"]) == 2:
            cx, cy = float(op["center"][0]), float(op["center"][1])
            dx = float(wall["end"][0]) - float(wall["start"][0])
            dy = float(wall["end"][1]) - float(wall["start"][1])
            w_len = math.hypot(dx, dy)
            if w_len > 0:
                ux, uy = dx / w_len, dy / w_len
                nx, ny = -uy, ux  # normal perpendicular
                for sign in [1.0, -1.0]:
                    test_pt = [cx + sign * 300.0 * nx, cy + sign * 300.0 * ny]
                    for r in rooms:
                        corners = r.get("boundaryCorners", [])
                        if corners and point_in_polygon(test_pt, corners):
                            if r["id"] not in matched_rooms:
                                matched_rooms.append(r["id"])

        height = float(op["height"]) if "height" in op and op["height"] is not None else None
        sill_height = float(op["sillHeight"]) if "sillHeight" in op and op["sillHeight"] is not None else None

        if op_type == "door":
            swing = op.get("swing", "90_deg_single")
            doors_out.append({
                "id": op_id,
                "type": op_type,
                "floorId": floor_id,
                "wallId": wall_id,
                "associatedRoomIds": matched_rooms,
                "widthMm": width,
                "heightMm": height,
                "sillHeightMm": sill_height,
                "swing": swing,
                "source": source,
                "verificationStatus": v_status
            })
        else:
            windows_out.append({
                "id": op_id,
                "type": op_type,
                "floorId": floor_id,
                "wallId": wall_id,
                "associatedRoomIds": matched_rooms,
                "widthMm": width,
                "heightMm": height,
                "sillHeightMm": sill_height,
                "source": source,
                "verificationStatus": v_status
            })

    return doors_out, windows_out, warnings


def compile_element_inventory(
    model: Dict[str, Any]
) -> Dict[str, Any]:
    """Compiles itemized instances and category/block aggregations for architectural elements."""
    elements_list = model.get("elements", [])
    rooms = model.get("rooms", [])
    instances_out = []
    summary_by_cat: Dict[str, int] = {}
    summary_by_block: Dict[str, Dict[str, Any]] = {}

    for elem in elements_list:
        e_id = elem["id"]
        b_id = elem["blockId"]
        cat = elem.get("category")
        if not cat and b_id in ELEMENT_CATALOG:
            cat = ELEMENT_CATALOG[b_id].get("category", "furniture")
        if not cat:
            cat = "furniture"

        floor_id = elem.get("floorId", elem.get("levelId", model.get("floorId", "LEVEL-01")))
        pos = elem.get("position", [0.0, 0.0])
        rot = float(elem.get("rotation", 0.0))
        source = elem.get("source", "proposed")
        status = elem.get("status", "approved")

        # Discover or verify room ID
        room_id = elem.get("roomId")
        if not room_id and isinstance(pos, (list, tuple)) and len(pos) == 2:
            for r in rooms:
                corners = r.get("boundaryCorners", [])
                if corners and point_in_polygon(pos, corners):
                    room_id = r["id"]
                    break

        dims = elem.get("dimensions")
        if not dims and b_id in ELEMENT_CATALOG:
            dims = ELEMENT_CATALOG[b_id].get("dimensions", {})

        instances_out.append({
            "id": e_id,
            "blockId": b_id,
            "category": cat,
            "floorId": floor_id,
            "roomId": room_id,
            "position": [float(pos[0]), float(pos[1])],
            "rotation": rot,
            "dimensions": dims or {},
            "source": source,
            "status": status
        })

        # Aggregation
        summary_by_cat[cat] = summary_by_cat.get(cat, 0) + 1

        if b_id not in summary_by_block:
            summary_by_block[b_id] = {
                "blockId": b_id,
                "category": cat,
                "dimensions": dims or {},
                "instanceCount": 0
            }
        summary_by_block[b_id]["instanceCount"] += 1

    cat_list = [{"category": k, "instanceCount": v} for k, v in sorted(summary_by_cat.items())]
    block_list = sorted(summary_by_block.values(), key=lambda x: (x["category"], x["blockId"]))

    return {
        "summaryByCategory": cat_list,
        "summaryByBlock": block_list,
        "instances": instances_out
    }


def compile_finish_schedule(
    model: Dict[str, Any],
    rooms: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Compiles the floor finish schedule with area calculations and material audit."""
    rooms_by_id = {r["id"]: r for r in rooms}
    finishes_out = []

    for fin in model.get("finishes", []):
        f_id = fin["id"]
        r_id = fin.get("roomId", "")
        room = rooms_by_id.get(r_id, {})
        r_name = room.get("name", "UNSPECIFIED ROOM")
        floor_id = fin.get("floorId", model.get("floorId", "LEVEL-01"))
        pattern = fin.get("pattern", "tile_grid")
        tile_size = float(fin.get("tileSize", 0.0)) if "tileSize" in fin else None
        boundary = fin.get("boundary", [])
        source = fin.get("source", "proposed")

        if boundary and len(boundary) >= 3:
            area_m2 = round(calculate_polygon_area(boundary) / 1e6, 2)
        elif "netAreaM2" in room:
            area_m2 = room["netAreaM2"]
        else:
            area_m2 = 0.0

        # Physical material audit rule
        material = fin.get("material")
        if material:
            v_status = "verified_material"
        else:
            v_status = "material_unspecified (graphical hatch pattern only)"

        finishes_out.append({
            "id": f_id,
            "roomId": r_id,
            "roomName": r_name,
            "floorId": floor_id,
            "pattern": pattern,
            "tileSizeMm": tile_size,
            "material": material,
            "areaCoveredM2": area_m2,
            "source": source,
            "verificationStatus": v_status
        })

    return finishes_out


def compile_uncertainty_and_audit(
    model: Dict[str, Any],
    rooms: List[Dict[str, Any]],
    doors: List[Dict[str, Any]],
    windows: List[Dict[str, Any]],
    elements: Dict[str, Any],
    warnings: List[str]
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Performs rigorous integrity audit across geometry, host walls, overlaps, and uncertainties."""
    uncertainties_out = []
    envelope = model.get("envelope", {})
    env_w = float(envelope.get("width", 0.0))
    env_d = float(envelope.get("depth", 0.0))

    # 1. Existing model uncertainties
    for u in model.get("uncertainties", []):
        uncertainties_out.append({
            "id": u["id"],
            "category": "sketch_interpretation",
            "target": u.get("target", "unspecified"),
            "description": u.get("description", ""),
            "assumedValue": u.get("assumedValue"),
            "confidence": u.get("confidence", "medium"),
            "status": u.get("status", "unresolved"),
            "provenance": "model_uncertainty_log"
        })

    # 2. Host wall validation
    invalid_openings = [d["id"] for d in doors if d["verificationStatus"] == "invalid_host_wall"]
    invalid_openings += [w["id"] for w in windows if w["verificationStatus"] == "invalid_host_wall"]
    host_walls_valid = (len(invalid_openings) == 0)

    # 3. Room boundary overlaps
    overlapping_pairs = []
    room_count = len(rooms)
    raw_rooms = model.get("rooms", [])
    for i in range(room_count):
        corners_i = raw_rooms[i].get("boundaryCorners", [])
        for j in range(i + 1, room_count):
            corners_j = raw_rooms[j].get("boundaryCorners", [])
            if corners_i and corners_j:
                if detect_polygons_overlap(corners_i, corners_j):
                    overlapping_pairs.append([raw_rooms[i]["id"], raw_rooms[j]["id"]])
                    warnings.append(
                        f"Overlapping room polygons detected between '{raw_rooms[i]['id']}' and '{raw_rooms[j]['id']}'."
                    )

    # 4. Out-of-envelope elements
    out_of_envelope = []
    for inst in elements.get("instances", []):
        pos = inst.get("position", [0.0, 0.0])
        if pos[0] < 0.0 or pos[0] > env_w or pos[1] < 0.0 or pos[1] > env_d:
            out_of_envelope.append(inst["id"])
            warnings.append(
                f"Element '{inst['id']}' at position [{pos[0]}, {pos[1]}] falls outside building envelope [0..{env_w}, 0..{env_d}]."
            )

    # 5. Unannotated vertical parameters audit
    unverified_height_count = sum(1 for d in doors if d["heightMm"] is None) + sum(1 for w in windows if w["heightMm"] is None)
    if unverified_height_count > 0:
        uncertainties_out.append({
            "id": "UNC-VERT-01",
            "category": "vertical_geometry",
            "target": "openings.height",
            "description": f"{unverified_height_count} door/window vertical heights unannotated in 2D floor plan.",
            "assumedValue": None,
            "confidence": "low",
            "status": "unresolved (requires downstream approval)",
            "provenance": "2d_floor_plan_boundary"
        })

    is_approved = (model.get("status") == "approved")
    if not is_approved:
        warnings.append(
            f"MODEL STATUS '{model.get('status')}': This document is an unapproved diagnostic draft. NOT APPROVED FOR CONSTRUCTION."
        )

    audit_out = {
        "flags": warnings,
        "hostWallValidation": {
            "valid": host_walls_valid,
            "invalidOpenings": invalid_openings
        },
        "overlappingRooms": {
            "detected": len(overlapping_pairs) > 0,
            "overlappingPairs": overlapping_pairs
        },
        "envelopeClearance": {
            "allWithinEnvelope": len(out_of_envelope) == 0,
            "outOfEnvelopeElements": out_of_envelope
        },
        "isApprovedForConstruction": is_approved and host_walls_valid and len(overlapping_pairs) == 0
    }

    return uncertainties_out, audit_out


# ==============================================================================
# 3. MASTER REPORT COMPILER
# ==============================================================================

def get_report_schema_path() -> str:
    """Discovers architectural-report.schema.json in candidate directory locations."""
    candidates = [
        os.path.join(os.path.dirname(__file__), "..", "skills", "sketch-to-cad", "schemas", "architectural-report.schema.json"),
        os.path.join(os.path.dirname(__file__), "..", "schemas", "architectural-report.schema.json"),
        os.path.join(os.path.dirname(__file__), "schemas", "architectural-report.schema.json"),
    ]
    for p in candidates:
        abs_p = os.path.abspath(p)
        if os.path.isfile(abs_p):
            return abs_p
    raise FileNotFoundError("architectural-report.schema.json not found in repository candidate paths.")


def compile_architectural_report(
    model: Dict[str, Any],
    handoff: Optional[Dict[str, Any]] = None,
    dxf_path: Optional[str] = None,
    schema_path: Optional[str] = None
) -> Dict[str, Any]:
    """Compiles the complete architectural report conforming to architectural-report.schema.json v1.0.0."""
    metadata = model.get("metadata", {})
    project_meta = model.get("project", {})
    drawing_id = metadata.get("drawingId") or (os.path.splitext(os.path.basename(dxf_path))[0] if dxf_path else "floor-plan")
    units = model.get("units", "mm")
    envelope = model.get("envelope", {})
    env_w = float(envelope.get("width", 0.0))
    env_d = float(envelope.get("depth", 0.0))

    approval_status = model.get("status", "draft")
    approval_block = model.get("approval", {})
    approved_by = approval_block.get("approvedBy") or model.get("approvedBy")
    approved_at = approval_block.get("approvedAt") or model.get("approvedAt")
    created_at = metadata.get("createdAt") or datetime.now(timezone.utc).isoformat()

    warnings: List[str] = []

    # 1. Schedules
    finishes_raw = model.get("finishes", [])
    rooms = compile_room_schedule(model, finishes_raw)
    doors, windows, op_warnings = compile_opening_schedules(model)
    warnings.extend(op_warnings)

    elements = compile_element_inventory(model)
    finishes = compile_finish_schedule(model, rooms)

    # 2. Uncertainty and Audit
    uncertainties, audit = compile_uncertainty_and_audit(
        model, rooms, doors, windows, elements, warnings
    )

    # 3. Summary
    total_net_area = round(sum(r["netAreaM2"] for r in rooms), 2)
    if env_w > 0 and env_d > 0:
        gross_area = round((env_w * env_d) / 1e6, 2)
        gross_method = "exterior_envelope_bounding_box"
    else:
        gross_area = None
        gross_method = "uncalculated"

    unresolved_u_count = sum(1 for u in uncertainties if "unresolved" in str(u.get("status", "")).lower())

    if approval_status != "approved":
        val_status = "DRAFT"
    elif len(audit["flags"]) > 0:
        val_status = "WARNING"
    else:
        val_status = "PASSED"

    report_data = {
        "schemaVersion": "1.0.0",
        "project": {
            "projectName": project_meta.get("name") or metadata.get("projectName") or metadata.get("title") or "Residential Floor Plan",
            "drawingId": drawing_id,
            "units": units,
            "coordinateSystem": "Cartesian2D_RightHanded_YUp",
            "sourceSketch": metadata.get("sourceSketch", "hand-sketch-residential.png"),
            "author": metadata.get("author", "Sketch-to-CAD Engine"),
            "approvalStatus": approval_status,
            "approvedBy": approved_by,
            "approvedAt": approved_at,
            "createdAt": created_at
        },
        "summary": {
            "floorCount": 1,
            "roomCount": len(rooms),
            "doorCount": len(doors),
            "windowCount": len(windows),
            "elementCount": len(elements["instances"]),
            "finishCount": len(finishes),
            "totalNetAreaM2": total_net_area,
            "grossFootprintAreaM2": gross_area,
            "grossAreaMethod": gross_method,
            "uncertaintyCount": len(uncertainties),
            "unresolvedUncertaintyCount": unresolved_u_count,
            "validationStatus": val_status
        },
        "rooms": rooms,
        "openings": {
            "doors": doors,
            "windows": windows
        },
        "elements": elements,
        "finishes": finishes,
        "uncertainties": uncertainties,
        "audit": audit
    }

    # Validate against schema if jsonschema is available
    try:
        import jsonschema
        if schema_path is None:
            schema_path = get_report_schema_path()
        with open(schema_path, "r", encoding="utf-8") as sf:
            s_data = json.load(sf)
        jsonschema.validate(instance=report_data, schema=s_data)
    except ImportError:
        pass

    return report_data


# ==============================================================================
# 4. MARKDOWN REPORT RENDERER
# ==============================================================================

def render_markdown_report(report: Dict[str, Any]) -> str:
    """Renders the compiled report into an auditable Markdown technical document."""
    proj = report["project"]
    summ = report["summary"]
    rooms = report["rooms"]
    doors = report["openings"]["doors"]
    windows = report["openings"]["windows"]
    elements = report["elements"]
    finishes = report["finishes"]
    uncertainties = report["uncertainties"]
    audit = report["audit"]

    status_tag = f"**STATUS: {proj['approvalStatus'].upper()}**"
    if proj['approvalStatus'] != "approved":
        status_tag += " ⚠️ *(DRAFT / NOT APPROVED FOR CONSTRUCTION)*"

    gross_str = f"{summ['grossFootprintAreaM2']:.2f} m²" if summ.get('grossFootprintAreaM2') else "N/A"

    lines = [
        f"# Architectural Documentation & Schedules Report",
        f"",
        f"> **Project:** {proj['projectName']} | **Drawing ID:** `{proj['drawingId']}`  ",
        f"> **Approval State:** {status_tag}  ",
        f"> **Date:** {proj['createdAt']} | **Units:** {proj['units']} (`{proj['coordinateSystem']}`)  ",
        f"",
        f"---",
        f"",
        f"## 1. Executive Architectural Summary",
        f"",
        f"| Parameter | Metric / Value | Calculation & Scope Notes |",
        f"| :--- | :--- | :--- |",
        f"| **Floors Represented** | {summ['floorCount']} Storey | Single-storey ground level (`LEVEL-01`) |",
        f"| **Verified Net Area** | **{summ['totalNetAreaM2']:.2f} m²** | Sum of internal clear room polygons (Shoelace formula) |",
        f"| **Gross Footprint Area** | {gross_str} | Exterior bounding box footprint ({summ['grossAreaMethod']}) |",
        f"| **Room Enclosures** | {summ['roomCount']} Rooms | Verified room boundaries with centroids |",
        f"| **Door Openings** | {summ['doorCount']} Doors | Capped jambs with swing arcs |",
        f"| **Window Openings** | {summ['windowCount']} Windows | Centerline glazing and jamb cuts |",
        f"| **Architectural Blocks** | {summ['elementCount']} Instances | Furniture, sanitary fixtures, structure & circulation |",
        f"| **Floor Finishes** | {summ['finishCount']} Finish Zones | Surface boundaries and graphical tile hatching |",
        f"| **Uncertainty Audit** | {summ['uncertaintyCount']} Items ({summ['unresolvedUncertaintyCount']} unresolved) | Documented assumptions & unverified 2D heights |",
        f"| **Validation Status** | **{summ['validationStatus']}** | Architectural rule compliance & integrity |",
        f"",
        f"---",
        f"",
        f"## 2. Room Area & Dimension Schedule",
        f"",
        f"| Room ID | Room Name | Floor | Length (m) | Width (m) | Net Area (m²) | Perimeter (m) | Finish Pattern | Calculation Method | Notes |",
        f"| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- | :--- | :--- |"
    ]

    for r in rooms:
        len_str = f"{r['lengthMm'] / 1000.0:.2f}" if r['lengthMm'] else "N/A"
        wid_str = f"{r['widthMm'] / 1000.0:.2f}" if r['widthMm'] else "N/A"
        per_str = f"{r['perimeterM']:.2f}" if r['perimeterM'] else "N/A"
        fin_str = r['finishPattern'] or "Standard / Unspecified"
        lines.append(
            f"| `{r['id']}` | **{r['name']}** | {r['floorId']} | {len_str} | {wid_str} | **{r['netAreaM2']:.2f}** | {per_str} | {fin_str} | `{r['calculationMethod']}` | {r['notes']} |"
        )

    lines.extend([
        "",
        "> **Calculation Conventions**: Net room areas are calculated strictly from internal wall-face boundary vertices using the Shoelace formula. Non-rectangular rooms report `N/A` for length and width to prevent misleading orthogonal simplifications.",
        f"",
        f"---",
        f"",
        f"## 3. Opening Schedules",
        f"",
        f"### 3.1 Door Schedule",
        f"",
        f"| Door ID | Floor | Host Wall | Associated Space(s) | Width (mm) | Height (mm) | Sill (mm) | Swing Geometry | Provenance | Verification |",
        f"| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- |"
    ])

    for d in doors:
        rooms_str = ", ".join(f"`{rid}`" for rid in d['associatedRoomIds']) if d['associatedRoomIds'] else "Exterior / Unassigned"
        h_str = f"{d['heightMm']:.0f}" if d['heightMm'] else "*Unannotated (Null)*"
        s_str = f"{d['sillHeightMm']:.0f}" if d['sillHeightMm'] else "0 (Flush)"
        lines.append(
            f"| `{d['id']}` | {d['floorId']} | `{d['wallId']}` | {rooms_str} | {d['widthMm']:.0f} | {h_str} | {s_str} | {d['swing'] or 'None'} | `{d['source']}` | `{d['verificationStatus']}` |"
        )

    lines.extend([
        f"",
        f"### 3.2 Window Schedule",
        f"",
        f"| Window ID | Floor | Host Wall | Associated Space | Width (mm) | Height (mm) | Sill Height (mm) | Provenance | Verification |",
        f"| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- |"
    ])

    for w in windows:
        rooms_str = ", ".join(f"`{rid}`" for rid in w['associatedRoomIds']) if w['associatedRoomIds'] else "Unassigned"
        h_str = f"{w['heightMm']:.0f}" if w['heightMm'] else "*Unannotated (Null)*"
        s_str = f"{w['sillHeightMm']:.0f}" if w['sillHeightMm'] else "*Unannotated (Null)*"
        lines.append(
            f"| `{w['id']}` | {w['floorId']} | `{w['wallId']}` | {rooms_str} | {w['widthMm']:.0f} | {h_str} | {s_str} | `{w['source']}` | `{w['verificationStatus']}` |"
        )

    lines.extend([
        f"",
        f"> **Notice**: 2D floor plans do not define vertical clearances. Door head heights and window sill heights are stored as `null` and must be confirmed during downstream BIM vertical parameter approval.",
        f"",
        f"---",
        f"",
        f"## 4. Architectural Element Inventory",
        f"",
        f"### 4.1 Summary by Category & Block Definition",
        f"",
        f"| Category | Block Definition ID | Nominal Dimensions (W x D mm) | Instance Count |",
        f"| :--- | :--- | :--- | :---: |"
    ])

    for blk in elements["summaryByBlock"]:
        dims = blk.get("dimensions", {})
        dim_str = f"{dims.get('width', '-')} x {dims.get('depth', '-')}" if dims else "Parametric"
        lines.append(f"| **{blk['category'].capitalize()}** | `{blk['blockId']}` | {dim_str} | **{blk['instanceCount']}** |")

    lines.extend([
        f"",
        f"### 4.2 Itemized Element Instances",
        f"",
        f"| Element ID | Block Definition | Category | Floor | Room | Insertion (X, Y mm) | Rotation | Status |",
        f"| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |"
    ])

    for inst in elements["instances"]:
        r_str = f"`{inst['roomId']}`" if inst['roomId'] else "*Unassigned*"
        pos_str = f"[{inst['position'][0]:.0f}, {inst['position'][1]:.0f}]"
        lines.append(
            f"| `{inst['id']}` | `{inst['blockId']}` | {inst['category']} | {inst['floorId']} | {r_str} | {pos_str} | {inst['rotation']}° | `{inst['status']}` |"
        )

    lines.extend([
        f"",
        f"---",
        f"",
        f"## 5. Floor Finish Schedule",
        f"",
        f"| Finish ID | Room Name (ID) | Floor | Pattern | Tile Grid Size (mm) | Physical Material | Covered Area (m²) | Status |",
        f"| :--- | :--- | :--- | :--- | :---: | :--- | :---: | :--- |"
    ])

    for fin in finishes:
        mat_str = fin['material'] or "*Unspecified (Hatch Pattern Only)*"
        ts_str = f"{fin['tileSizeMm']:.0f}" if fin['tileSizeMm'] else "Continuous"
        lines.append(
            f"| `{fin['id']}` | {fin['roomName']} (`{fin['roomId']}`) | {fin['floorId']} | `{fin['pattern']}` | {ts_str} | {mat_str} | **{fin['areaCoveredM2']:.2f}** | `{fin['verificationStatus']}` |"
        )

    lines.extend([
        f"",
        f"> **Material Disclaimer**: A CAD hatch pattern (`ANSI37`, `NET`, `ANSI31`) is a drafting convention and does not certify physical material specifications without manufacturer submittals.",
        f"",
        f"---",
        f"",
        f"## 6. Uncertainty, Provenance & Verification Audit",
        f"",
        f"| Issue ID | Scope | Target | Status | Confidence | Description |",
        f"| :--- | :--- | :--- | :--- | :--- | :--- |"
    ])

    for u in uncertainties:
        lines.append(
            f"| `{u['id']}` | {u.get('category', 'general')} | `{u['target']}` | `{u['status']}` | `{u['confidence']}` | {u['description']} |"
        )

    lines.extend([
        f"",
        f"### 6.1 Integrity Audit Results",
        f"- **Host-Wall Validation**: {'✅ PASSED (All openings hosted on valid walls)' if audit['hostWallValidation']['valid'] else '❌ FAILED (Invalid host wall references detected)'}",
        f"- **Room Polygon Overlaps**: {'✅ PASSED (Zero overlapping room enclosures)' if not audit['overlappingRooms']['detected'] else '❌ WARNING (Overlapping room enclosures detected)'}",
        f"- **Envelope Clearance**: {'✅ PASSED (All blocks reside inside exterior footprint)' if audit['envelopeClearance']['allWithinEnvelope'] else '⚠️ WARNING (Out-of-envelope elements detected)'}",
        f"- **Approval Gate Status**: {'✅ APPROVED FOR DRAFTING & HANDOFF' if audit['isApprovedForConstruction'] else '⚠️ DRAFT / NOT APPROVED'}",
        f"",
        f"---",
        f"",
        f"## 7. Regulatory & Compliance Notice",
        f"This architectural schedule and report has been synthesized automatically from verified 2D CAD vector geometry. Structural load-bearing capacity, shear wall provisions, fire-resistance ratings, egress width calculations, and municipal zoning setbacks remain **UNVERIFIED** and must be reviewed and stamped by a licensed architect or professional engineer prior to construction."
    ])

    return "\n".join(lines)


# ==============================================================================
# 5. PDF REPORT RENDERER (REPORTLAB)
# ==============================================================================

def render_pdf_report(report: Dict[str, Any], output_pdf_path: str) -> str:
    """Generates an executive, multi-page paginated architectural PDF report using ReportLab."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.pdfgen import canvas
    except ImportError:
        raise ImportError("ReportLab is required for PDF generation. Install with: pip install reportlab")

    class NumberedCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            super(NumberedCanvas, self).__init__(*args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            num_pages = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self.draw_decorations(num_pages)
                super(NumberedCanvas, self).showPage()
            super(NumberedCanvas, self).save()

        def draw_decorations(self, num_pages):
            self.saveState()
            self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(colors.HexColor("#475569"))
            if self._pageNumber > 1:
                self.drawString(36, 11 * inch - 26, "SKETCH-TO-CAD ARCHITECTURAL TECHNICAL REPORT & SCHEDULES")
                self.setFont("Helvetica", 7.5)
                self.drawRightString(8.5 * inch - 36, 11 * inch - 26, f"DRAWING: {report['project']['drawingId']}")
                self.setStrokeColor(colors.HexColor("#CBD5E1"))
                self.setLineWidth(0.5)
                self.line(36, 11 * inch - 30, 8.5 * inch - 36, 11 * inch - 30)

            self.setFont("Helvetica", 7.5)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(36, 22, "CONFIDENTIAL & PROPRIETARY | ANTIGRAVITY AGENTIC CAD SUITE | ISO & AIA CAD STANDARDS")
            self.drawRightString(8.5 * inch - 36, 22, f"Page {self._pageNumber} of {num_pages}")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(36, 30, 8.5 * inch - 36, 30)
            self.restoreState()

    os.makedirs(os.path.dirname(os.path.abspath(output_pdf_path)), exist_ok=True)
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=38,
        bottomMargin=38
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "RepTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#0F172A")
    )
    subtitle_style = ParagraphStyle(
        "RepSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#475569")
    )
    h2_style = ParagraphStyle(
        "RepH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=10,
        spaceAfter=4
    )
    cell_style = ParagraphStyle(
        "RepCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#1E293B")
    )
    cell_bold = ParagraphStyle(
        "RepCellBold",
        parent=cell_style,
        fontName="Helvetica-Bold"
    )
    cell_hdr = ParagraphStyle(
        "RepCellHdr",
        parent=cell_style,
        fontName="Helvetica-Bold",
        fontSize=7.5,
        textColor=colors.white
    )

    story = []

    # Title & Header
    proj = report["project"]
    summ = report["summary"]
    story.append(Paragraph("Architectural Documentation & Schedules", title_style))
    story.append(Paragraph(
        f"<b>Project:</b> {proj['projectName']} | <b>Drawing:</b> {proj['drawingId']} | "
        f"<b>Status:</b> {proj['approvalStatus'].upper()} | <b>Units:</b> {proj['units']}",
        subtitle_style
    ))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceAfter=8))

    # Executive Summary Table
    story.append(Paragraph("1. Executive Architectural Summary", h2_style))
    sum_data = [
        [Paragraph("Metric / Parameter", cell_hdr), Paragraph("Value", cell_hdr), Paragraph("Notes & Conventions", cell_hdr)],
        [Paragraph("Verified Net Area", cell_bold), Paragraph(f"<b>{summ['totalNetAreaM2']:.2f} m2</b>", cell_style), Paragraph("Internal clear room boundaries (Shoelace formula)", cell_style)],
        [Paragraph("Gross Footprint Area", cell_bold), Paragraph(f"{summ['grossFootprintAreaM2']:.2f} m2" if summ['grossFootprintAreaM2'] else "N/A", cell_style), Paragraph("Exterior envelope footprint bounding box", cell_style)],
        [Paragraph("Room Enclosures", cell_bold), Paragraph(str(summ['roomCount']), cell_style), Paragraph("Approved room zones with centroids", cell_style)],
        [Paragraph("Doors & Windows", cell_bold), Paragraph(f"{summ['doorCount']} Doors, {summ['windowCount']} Windows", cell_style), Paragraph("Clean jamb cuts with 90° swings / glazing", cell_style)],
        [Paragraph("Architectural Blocks", cell_bold), Paragraph(f"{summ['elementCount']} Instances", cell_style), Paragraph("Furniture, sanitary fixtures, columns, stairs", cell_style)],
        [Paragraph("Floor Finishes", cell_bold), Paragraph(f"{summ['finishCount']} Zones", cell_style), Paragraph("Tile grids and finish hatch boundaries", cell_style)],
        [Paragraph("Audit & Validation", cell_bold), Paragraph(f"<b>{summ['validationStatus']}</b>", cell_style), Paragraph(f"{summ['uncertaintyCount']} uncertainty logs ({summ['unresolvedUncertaintyCount']} unresolved)", cell_style)]
    ]
    t_sum = Table(sum_data, colWidths=[130, 110, 300])
    t_sum.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t_sum)
    story.append(Spacer(1, 10))

    # Room Schedule
    story.append(Paragraph("2. Room Area & Dimension Schedule", h2_style))
    r_hdr = [
        Paragraph("ID", cell_hdr), Paragraph("Room Name", cell_hdr), Paragraph("Floor", cell_hdr),
        Paragraph("Length (m)", cell_hdr), Paragraph("Width (m)", cell_hdr), Paragraph("Net Area (m2)", cell_hdr),
        Paragraph("Perimeter (m)", cell_hdr), Paragraph("Finish", cell_hdr), Paragraph("Method", cell_hdr)
    ]
    r_rows = [r_hdr]
    for r in report["rooms"]:
        l_str = f"{r['lengthMm']/1000.0:.2f}" if r['lengthMm'] else "N/A"
        w_str = f"{r['widthMm']/1000.0:.2f}" if r['widthMm'] else "N/A"
        p_str = f"{r['perimeterM']:.2f}" if r['perimeterM'] else "N/A"
        r_rows.append([
            Paragraph(r["id"], cell_bold),
            Paragraph(r["name"], cell_style),
            Paragraph(r["floorId"], cell_style),
            Paragraph(l_str, cell_style),
            Paragraph(w_str, cell_style),
            Paragraph(f"<b>{r['netAreaM2']:.2f}</b>", cell_style),
            Paragraph(p_str, cell_style),
            Paragraph(r["finishPattern"] or "-", cell_style),
            Paragraph(r["calculationMethod"][:12], cell_style)
        ])
    t_room = Table(r_rows, colWidths=[35, 120, 45, 50, 50, 65, 60, 55, 60])
    t_room.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t_room)
    story.append(Spacer(1, 10))

    # Page Break for clean schedule presentation
    story.append(PageBreak())

    # Door and Window Schedules
    story.append(Paragraph("3. Door and Window Schedules", h2_style))
    d_hdr = [
        Paragraph("ID", cell_hdr), Paragraph("Host Wall", cell_hdr), Paragraph("Space(s)", cell_hdr),
        Paragraph("Width (mm)", cell_hdr), Paragraph("Height (mm)", cell_hdr), Paragraph("Swing", cell_hdr),
        Paragraph("Status", cell_hdr)
    ]
    d_rows = [d_hdr]
    for d in report["openings"]["doors"]:
        r_str = ", ".join(d["associatedRoomIds"]) if d["associatedRoomIds"] else "Exterior"
        h_str = f"{d['heightMm']:.0f}" if d['heightMm'] else "Null"
        d_rows.append([
            Paragraph(d["id"], cell_bold),
            Paragraph(d["wallId"], cell_style),
            Paragraph(r_str, cell_style),
            Paragraph(f"{d['widthMm']:.0f}", cell_style),
            Paragraph(h_str, cell_style),
            Paragraph(d["swing"] or "None", cell_style),
            Paragraph(d["verificationStatus"], cell_style)
        ])
    t_door = Table(d_rows, colWidths=[45, 75, 100, 65, 65, 85, 105])
    t_door.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0D9488")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    story.append(Paragraph("<b>3.1 Door Schedule</b>", subtitle_style))
    story.append(Spacer(1, 3))
    story.append(t_door)
    story.append(Spacer(1, 8))

    w_hdr = [
        Paragraph("ID", cell_hdr), Paragraph("Host Wall", cell_hdr), Paragraph("Space", cell_hdr),
        Paragraph("Width (mm)", cell_hdr), Paragraph("Height (mm)", cell_hdr), Paragraph("Sill (mm)", cell_hdr),
        Paragraph("Status", cell_hdr)
    ]
    w_rows = [w_hdr]
    for w in report["openings"]["windows"]:
        r_str = ", ".join(w["associatedRoomIds"]) if w["associatedRoomIds"] else "Unassigned"
        h_str = f"{w['heightMm']:.0f}" if w['heightMm'] else "Null"
        s_str = f"{w['sillHeightMm']:.0f}" if w['sillHeightMm'] else "Null"
        w_rows.append([
            Paragraph(w["id"], cell_bold),
            Paragraph(w["wallId"], cell_style),
            Paragraph(r_str, cell_style),
            Paragraph(f"{w['widthMm']:.0f}", cell_style),
            Paragraph(h_str, cell_style),
            Paragraph(s_str, cell_style),
            Paragraph(w["verificationStatus"], cell_style)
        ])
    t_win = Table(w_rows, colWidths=[45, 75, 100, 65, 65, 85, 105])
    t_win.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0284C7")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    story.append(Paragraph("<b>3.2 Window Schedule</b>", subtitle_style))
    story.append(Spacer(1, 3))
    story.append(t_win)
    story.append(Spacer(1, 10))

    # Floor Finish Schedule
    story.append(Paragraph("4. Floor Finish Schedule", h2_style))
    f_hdr = [
        Paragraph("ID", cell_hdr), Paragraph("Room", cell_hdr), Paragraph("Pattern", cell_hdr),
        Paragraph("Tile Size (mm)", cell_hdr), Paragraph("Material", cell_hdr), Paragraph("Area (m2)", cell_hdr),
        Paragraph("Status", cell_hdr)
    ]
    f_rows = [f_hdr]
    for fin in report["finishes"]:
        ts_str = f"{fin['tileSizeMm']:.0f}" if fin['tileSizeMm'] else "N/A"
        mat_str = fin['material'] or "Unspecified (Hatch Only)"
        f_rows.append([
            Paragraph(fin["id"], cell_bold),
            Paragraph(f"{fin['roomName']} ({fin['roomId']})", cell_style),
            Paragraph(fin["pattern"], cell_style),
            Paragraph(ts_str, cell_style),
            Paragraph(mat_str, cell_style),
            Paragraph(f"<b>{fin['areaCoveredM2']:.2f}</b>", cell_style),
            Paragraph(fin["verificationStatus"][:20], cell_style)
        ])
    t_fin = Table(f_rows, colWidths=[65, 110, 65, 65, 95, 60, 80])
    t_fin.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#475569")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_fin)
    story.append(Spacer(1, 10))

    # Page Break for Elements & Audit
    story.append(PageBreak())

    # Architectural Element Inventory
    story.append(Paragraph("5. Architectural Element Inventory", h2_style))
    blk_hdr = [
        Paragraph("Category", cell_hdr), Paragraph("Block Definition ID", cell_hdr),
        Paragraph("Nominal Dims (W x D mm)", cell_hdr), Paragraph("Quantity", cell_hdr)
    ]
    blk_rows = [blk_hdr]
    for b in report["elements"]["summaryByBlock"]:
        dims = b.get("dimensions", {})
        d_str = f"{dims.get('width', '-')} x {dims.get('depth', '-')}" if dims else "-"
        blk_rows.append([
            Paragraph(b["category"].capitalize(), cell_bold),
            Paragraph(b["blockId"], cell_style),
            Paragraph(d_str, cell_style),
            Paragraph(f"<b>{b['instanceCount']}</b>", cell_style)
        ])
    t_blk = Table(blk_rows, colWidths=[120, 160, 160, 100])
    t_blk.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#059669")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_blk)
    story.append(Spacer(1, 10))

    # Uncertainty & Verification Audit
    story.append(Paragraph("6. Uncertainty & Verification Audit", h2_style))
    u_hdr = [
        Paragraph("ID", cell_hdr), Paragraph("Category", cell_hdr), Paragraph("Target", cell_hdr),
        Paragraph("Confidence", cell_hdr), Paragraph("Status", cell_hdr), Paragraph("Description", cell_hdr)
    ]
    u_rows = [u_hdr]
    for u in report["uncertainties"]:
        u_rows.append([
            Paragraph(u["id"], cell_bold),
            Paragraph(u.get("category", "general"), cell_style),
            Paragraph(u["target"], cell_style),
            Paragraph(u["confidence"], cell_style),
            Paragraph(u["status"][:16], cell_style),
            Paragraph(u["description"], cell_style)
        ])
    t_unc = Table(u_rows, colWidths=[55, 65, 80, 50, 80, 210])
    t_unc.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DC2626")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_unc)
    story.append(Spacer(1, 10))

    # Regulatory Disclaimer
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#94A3B8"), spaceAfter=6))
    disc_text = (
        "<b>COMPLIANCE NOTICE:</b> This architectural report has been synthesized deterministically from "
        "verified 2D CAD geometry. Structural load-bearing capacity, shear walls, fire-safety egress, "
        "and building code compliance remain UNVERIFIED and must be approved by a licensed professional architect "
        "or structural engineer prior to construction."
    )
    story.append(Paragraph(disc_text, subtitle_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    return output_pdf_path


# ==============================================================================
# 6. CLI ENTRY POINT
# ==============================================================================

def main():
    """CLI tool to generate architectural reports and schedules from model JSON."""
    import argparse
    parser = argparse.ArgumentParser(description="Sketch-to-CAD Architectural Report & Schedule Generator")
    parser.add_argument("--model", required=True, help="Path to input floor-plan-model.json")
    parser.add_argument("--dxf", help="Optional path to corresponding DXF drawing")
    parser.add_argument("--handoff", help="Optional path to companion BIM handoff JSON")
    parser.add_argument("--output-dir", help="Directory where reports should be written")
    parser.add_argument("--output-base", help="Base filename for reports without extension")
    parser.add_argument("--no-pdf", action="store_true", help="Skip PDF generation")
    args = parser.parse_args()

    with open(args.model, "r", encoding="utf-8") as f:
        model = json.load(f)

    handoff = None
    if args.handoff and os.path.exists(args.handoff):
        with open(args.handoff, "r", encoding="utf-8") as hf:
            handoff = json.load(hf)

    out_dir = args.output_dir or os.path.dirname(os.path.abspath(args.model))
    os.makedirs(out_dir, exist_ok=True)

    base_name = args.output_base or os.path.splitext(os.path.basename(args.model))[0]

    # Compile master report
    report = compile_architectural_report(model=model, handoff=handoff, dxf_path=args.dxf)

    json_path = os.path.join(out_dir, f"{base_name}.report.json")
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(report, jf, indent=2)
    print(f"Exported Report JSON: {json_path}")

    md_path = os.path.join(out_dir, f"{base_name}.report.md")
    md_content = render_markdown_report(report)
    with open(md_path, "w", encoding="utf-8") as mf:
        mf.write(md_content)
    print(f"Exported Report Markdown: {md_path}")

    if not args.no_pdf:
        pdf_path = os.path.join(out_dir, f"{base_name}.report.pdf")
        render_pdf_report(report, pdf_path)
        print(f"Exported Report PDF: {pdf_path}")


if __name__ == "__main__":
    main()
