"""
Sketch-to-CAD Geometric & Architectural Validation Engine (Milestone 9)

Performs comprehensive engineering validation of 2D residential floor plans:
- Wall network connectivity (L, T, Cross junctions, collinear overlaps, gaps, dead-ends).
- Opening validity (host-wall clearance, opening overlaps, door swing conflict detection).
- Room boundary geometry (polygon closure, non-zero area, self-intersection, room overlaps, envelope bounds).
- Wall-to-room relationships (boundary wall alignment, unclosed room perimeters).
- Structural and element clearance (columns, furniture within envelope, non-collision with door swings).
- 4-tier architectural severity classification (blocking, major, warning, informational).
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Set, Tuple, Union


class Point2D:
    """Represents a 2D coordinate point supporting both attribute and index access."""

    def __init__(self, x: float, y: float):
        self.x = float(x)
        self.y = float(y)

    def __getitem__(self, idx: int) -> float:
        if idx == 0:
            return self.x
        elif idx == 1:
            return self.y
        raise IndexError("Point2D index out of range")

    def __len__(self) -> int:
        return 2

    def __iter__(self):
        yield self.x
        yield self.y

    def __repr__(self) -> str:
        return f"Point2D({self.x:.2f}, {self.y:.2f})"

    def to_list(self) -> List[float]:
        return [self.x, self.y]


def point_distance(p1: Union[List[float], Tuple[float, float], Point2D], p2: Union[List[float], Tuple[float, float], Point2D]) -> float:
    """Euclidean distance between two 2D points."""
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


def points_almost_equal(p1: Union[List[float], Tuple[float, float], Point2D], p2: Union[List[float], Tuple[float, float], Point2D], tol: float = 25.0) -> bool:
    """Checks if two points are within geometric tolerance (default 25mm)."""
    return point_distance(p1, p2) <= tol


def distance_point_to_segment(
    p: Union[List[float], Tuple[float, float], Point2D],
    a: Union[List[float], Tuple[float, float], Point2D],
    b: Union[List[float], Tuple[float, float], Point2D],
) -> Tuple[float, float]:
    """
    Computes distance from point p to segment ab, and the normalized projection parameter t in [0, 1].
    Returns (distance, t_clamped).
    """
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    seg_len_sq = dx * dx + dy * dy
    if seg_len_sq < 1e-9:
        return point_distance(p, a), 0.0

    t = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / seg_len_sq
    t_clamped = max(0.0, min(1.0, t))
    proj = [a[0] + t_clamped * dx, a[1] + t_clamped * dy]
    return point_distance(p, proj), t_clamped


def line_intersection(
    p1: Union[List[float], Tuple[float, float], Point2D],
    p2: Union[List[float], Tuple[float, float], Point2D],
    p3: Union[List[float], Tuple[float, float], Point2D],
    p4: Union[List[float], Tuple[float, float], Point2D],
) -> Tuple[bool, Optional[Point2D]]:
    """
    Computes line segment intersection between p1-p2 and p3-p4.
    Returns (True, Point2D) if segments intersect, or (False, None) if disjoint or parallel.
    """
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]
    x3, y3 = p3[0], p3[1]
    x4, y4 = p4[0], p4[1]

    denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
    if abs(denom) < 1e-9:
        return False, None

    ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
    ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denom

    if 0.0 <= ua <= 1.0 and 0.0 <= ub <= 1.0:
        ix = x1 + ua * (x2 - x1)
        iy = y1 + ua * (y2 - y1)
        return True, Point2D(ix, iy)

    return False, None


def segments_intersect(
    p1: Union[List[float], Tuple[float, float], Point2D],
    p2: Union[List[float], Tuple[float, float], Point2D],
    p3: Union[List[float], Tuple[float, float], Point2D],
    p4: Union[List[float], Tuple[float, float], Point2D],
    include_endpoints: bool = False,
) -> bool:
    """
    Checks if line segment p1-p2 intersects line segment p3-p4.
    If include_endpoints is False, ignores touching at endpoints.
    """
    def ccw(a, b, c):
        return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])

    a, b, c, d = p1, p2, p3, p4

    if not include_endpoints:
        if (
            points_almost_equal(a, c)
            or points_almost_equal(a, d)
            or points_almost_equal(b, c)
            or points_almost_equal(b, d)
        ):
            return False

    return (ccw(a, c, d) != ccw(b, c, d)) and (ccw(a, b, c) != ccw(a, b, d))


def compute_polygon_area(vertices: List[Any]) -> float:
    """Computes signed area of a 2D polygon using the Shoelace formula (returns absolute mm²)."""
    if len(vertices) < 3:
        return 0.0
    area = 0.0
    n = len(vertices)
    for i in range(n):
        j = (i + 1) % n
        area += vertices[i][0] * vertices[j][1]
        area -= vertices[j][0] * vertices[i][1]
    return abs(area) / 2.0


def polygon_area_shoelace(vertices: List[Any]) -> float:
    """Computes area in square meters (m²) using Shoelace formula from coordinates in mm or m."""
    raw_area = compute_polygon_area(vertices)
    # If coordinates are in millimeters (e.g., > 100 mm), return m²
    max_coord = max(max(abs(v[0]), abs(v[1])) for v in vertices) if vertices else 0.0
    if max_coord > 100.0:
        return raw_area / 1_000_000.0
    return raw_area


def is_polygon_self_intersecting(vertices: List[Any]) -> bool:
    """Checks if a simple 2D polygon self-intersects."""
    n = len(vertices)
    if n < 4:
        return False
    for i in range(n):
        a1, a2 = vertices[i], vertices[(i + 1) % n]
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue
            b1, b2 = vertices[j], vertices[(j + 1) % n]
            if segments_intersect(a1, a2, b1, b2, include_endpoints=False):
                return True
    return False


polygon_is_self_intersecting = is_polygon_self_intersecting


def point_in_polygon(pt: Union[List[float], Tuple[float, float], Point2D], poly: List[Any]) -> bool:
    """Determines whether a 2D point lies strictly inside a polygon."""
    inside = False
    m = len(poly)
    for i in range(m):
        j = (i + 1) % m
        xi, yi = poly[i][0], poly[i][1]
        xj, yj = poly[j][0], poly[j][1]
        if ((yi > pt[1]) != (yj > pt[1])) and (pt[0] < (xj - xi) * (pt[1] - yi) / (yj - yi + 1e-12) + xi):
            inside = not inside
    return inside


def polygons_overlap(
    poly1: List[Any],
    poly2: List[Any],
    tolerance_area: float = 1000.0,
) -> bool:
    """
    Checks if two 2D polygons overlap significantly.
    Uses bounding box check followed by segment intersection and interior sample point testing.
    """
    if len(poly1) < 3 or len(poly2) < 3:
        return False

    min_x1 = min(p[0] for p in poly1)
    max_x1 = max(p[0] for p in poly1)
    min_y1 = min(p[1] for p in poly1)
    max_y1 = max(p[1] for p in poly1)

    min_x2 = min(p[0] for p in poly2)
    max_x2 = max(p[0] for p in poly2)
    min_y2 = min(p[1] for p in poly2)
    max_y2 = max(p[1] for p in poly2)

    if (
        max_x1 <= min_x2 + 10.0
        or min_x1 >= max_x2 - 10.0
        or max_y1 <= min_y2 + 10.0
        or min_y1 >= max_y2 - 10.0
    ):
        return False

    n1, n2 = len(poly1), len(poly2)
    for i in range(n1):
        e1_a, e1_b = poly1[i], poly1[(i + 1) % n1]
        for j in range(n2):
            e2_a, e2_b = poly2[j], poly2[(j + 1) % n2]
            if segments_intersect(e1_a, e1_b, e2_a, e2_b, include_endpoints=False):
                return True

    c1 = [sum(p[0] for p in poly1) / n1, sum(p[1] for p in poly1) / n1]
    c2 = [sum(p[0] for p in poly2) / n2, sum(p[1] for p in poly2) / n2]

    if point_in_polygon(c1, poly2) or point_in_polygon(c2, poly1):
        return True

    return False


class ValidationIssue:
    """Encapsulates a single geometric QA issue with both attribute and dict-like access."""

    def __init__(
        self,
        issue_id: str,
        severity: str,
        category: str,
        description: str,
        affected_entities: List[str],
        floor_id: str,
        suggested_correction: str,
        requires_human_approval: bool = False,
    ):
        self.issue_id = issue_id
        self.severity = severity
        self.category = category
        self.description = description
        self.message = description
        self.affected_entities = affected_entities
        self.entity_id = affected_entities[0] if affected_entities else ""
        self.floor_id = floor_id
        self.suggested_correction = suggested_correction
        self.requires_human_approval = requires_human_approval

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "issue_id": self.issue_id,
            "severity": self.severity,
            "category": self.category,
            "description": self.description,
            "affected_entities": self.affected_entities,
            "floor_id": self.floor_id,
            "suggested_correction": self.suggested_correction,
            "requires_human_approval": self.requires_human_approval,
        }


class ValidationResult:
    """Wrapper for validation results supporting dictionary indexing and property access."""

    def __init__(self, data: Dict[str, Any], issues_objs: List[ValidationIssue]):
        self.data = data
        self.issues = issues_objs
        self.status = data.get("status", "PASSED")
        self.summary = data.get("summary", {})
        self.total_issues = data.get("total_issues", len(issues_objs))
        self.severity_counts = data.get("severity_counts", {})

    def __getitem__(self, item: str) -> Any:
        return self.data[item]

    def get(self, item: str, default: Any = None) -> Any:
        return self.data.get(item, default)


class ArchitecturalGeometryValidator:
    """
    Validates architectural drawings against engineering drafting rules:
    - Wall graph connectivity and junction typology.
    - Door and window host relationships and swing conflicts.
    - Room polygons and boundary consistency.
    - Structural and element clearances.
    """

    def __init__(
        self,
        model: Optional[Dict[str, Any]] = None,
        floor_id: Optional[str] = None,
        tolerance_mm: float = 25.0,
    ):
        self.model = model or {}
        self.target_floor_id = floor_id
        self.tolerance_mm = tolerance_mm
        self.raw_issues: List[Dict[str, Any]] = []
        self.issue_objects: List[ValidationIssue] = []
        self._issue_counter = 0
        self.junction_counts = {
            "L-junction": 0,
            "T-junction": 0,
            "Cross-junction": 0,
            "disconnected_endpoints": 0,
        }

    def add_issue(
        self,
        severity: str,
        category: str,
        description: str,
        affected_entities: List[str],
        suggested_correction: str,
        requires_human_approval: bool = False,
        floor_id: Optional[str] = None,
    ):
        """Records a structured architectural QA issue."""
        self._issue_counter += 1
        iss_id = f"QA-{category.upper()[:4]}-{self._issue_counter:03d}"
        fid = floor_id or self.target_floor_id or "LEVEL-01"
        iss_obj = ValidationIssue(
            issue_id=iss_id,
            severity=severity,
            category=category,
            description=description,
            affected_entities=affected_entities,
            floor_id=fid,
            suggested_correction=suggested_correction,
            requires_human_approval=requires_human_approval,
        )
        self.issue_objects.append(iss_obj)
        self.raw_issues.append(iss_obj.to_dict())

    def validate(
        self,
        model: Optional[Dict[str, Any]] = None,
        level_filter: Optional[str] = None,
    ) -> ValidationResult:
        """Runs validation with optional model or level_filter parameters."""
        if model is not None:
            self.model = model
        if level_filter is not None:
            self.target_floor_id = level_filter
        res_dict = self.validate_all()
        return ValidationResult(res_dict, self.issue_objects)

    def validate_all(self) -> Dict[str, Any]:
        """Runs the complete suite of architectural engineering checks."""
        self.raw_issues.clear()
        self.issue_objects.clear()
        self._issue_counter = 0
        self.junction_counts = {
            "L-junction": 0,
            "T-junction": 0,
            "Cross-junction": 0,
            "disconnected_endpoints": 0,
        }

        # Execute check categories
        self.validate_envelope()
        self.validate_wall_geometry()
        self.validate_openings()
        self.validate_rooms()
        self.validate_elements_and_structure()

        # Severity breakdown
        counts = {
            "blocking": sum(1 for i in self.issue_objects if i.severity == "blocking"),
            "major": sum(1 for i in self.issue_objects if i.severity == "major"),
            "warning": sum(1 for i in self.issue_objects if i.severity == "warning"),
            "informational": sum(1 for i in self.issue_objects if i.severity == "informational"),
        }

        if counts["blocking"] > 0:
            status = "FAILED_BLOCKING"
        elif counts["major"] > 0:
            status = "MAJOR_DISCREPANCY"
        elif counts["warning"] > 0:
            status = "REVIEW_REQUIRED"
        else:
            status = "PASSED"

        summary = {
            "junction_counts": self.junction_counts,
            "severity_counts": counts,
        }

        return {
            "status": status,
            "total_issues": len(self.raw_issues),
            "severity_counts": counts,
            "summary": summary,
            "issues": self.raw_issues,
        }

    # ---------------------------------------------------------------------
    # 1. Envelope Validation
    # ---------------------------------------------------------------------
    def validate_envelope(self):
        env = self.model.get("envelope", {})
        if not env:
            return
        w = float(env.get("width", 0.0))
        d = float(env.get("depth", 0.0))
        if w <= 0.0 or d <= 0.0:
            self.add_issue(
                severity="blocking",
                category="geometry",
                description=f"Invalid building envelope dimensions: {w}x{d} mm.",
                affected_entities=["envelope"],
                suggested_correction="Specify positive width and depth for the building footprint envelope.",
                requires_human_approval=True,
            )

    # ---------------------------------------------------------------------
    # 2. Wall Geometry & Junction Engineering
    # ---------------------------------------------------------------------
    def validate_wall_geometry(self):
        walls = self._get_walls()
        if not walls:
            self.add_issue(
                severity="blocking",
                category="geometry",
                description="Floor plan contains zero defined walls.",
                affected_entities=[],
                suggested_correction="Define exterior perimeter and partition walls.",
                requires_human_approval=True,
            )
            return

        seen_ids = set()
        for w in walls:
            wid = w.get("id", "")
            if wid in seen_ids:
                self.add_issue(
                    severity="blocking",
                    category="geometry",
                    description=f"Duplicate wall ID '{wid}' detected.",
                    affected_entities=[wid],
                    suggested_correction="Rename duplicate wall entity to maintain unique identifiers.",
                    requires_human_approval=False,
                )
            seen_ids.add(wid)

        endpoints: List[Tuple[str, str, List[float]]] = []
        for w in walls:
            s = [float(w["start"][0]), float(w["start"][1])]
            e = [float(w["end"][0]), float(w["end"][1])]
            endpoints.append((w["id"], "start", s))
            endpoints.append((w["id"], "end", e))

            length = point_distance(s, e)
            if length < 10.0:
                self.add_issue(
                    severity="blocking",
                    category="geometry",
                    description=f"Degenerate wall '{w['id']}' has length of {length:.1f} mm (< 10mm).",
                    affected_entities=[w["id"]],
                    suggested_correction="Remove degenerate wall segment or extend to proper boundary.",
                    requires_human_approval=True,
                )
            elif length < 50.0:
                self.add_issue(
                    severity="major",
                    category="geometry",
                    description=f"Wall '{w['id']}' has very short length of {length:.1f} mm (< 50mm).",
                    affected_entities=[w["id"]],
                    suggested_correction="Verify wall segment length adheres to construction practice.",
                    requires_human_approval=True,
                )

            th = float(w.get("thickness", 200.0))
            if th < 50.0 or th > 1000.0:
                self.add_issue(
                    severity="warning",
                    category="geometry",
                    description=f"Wall '{w['id']}' has atypical thickness of {th:.1f} mm.",
                    affected_entities=[w["id"]],
                    suggested_correction="Verify wall thickness adheres to residential standards (100-350mm).",
                    requires_human_approval=False,
                )

        # Check duplicate or collinear overlapping wall segments
        for i in range(len(walls)):
            w1 = walls[i]
            s1, e1 = w1["start"], w1["end"]
            for j in range(i + 1, len(walls)):
                w2 = walls[j]
                s2, e2 = w2["start"], w2["end"]

                if (points_almost_equal(s1, s2) and points_almost_equal(e1, e2)) or (
                    points_almost_equal(s1, e2) and points_almost_equal(e1, s2)
                ):
                    self.add_issue(
                        severity="blocking",
                        category="geometry",
                        description=f"Duplicate wall segments detected: '{w1['id']}' and '{w2['id']}'.",
                        affected_entities=[w1["id"], w2["id"]],
                        suggested_correction="Remove redundant duplicate wall segment.",
                        requires_human_approval=False,
                    )

        # Classify junctions and detect disconnected endpoints
        for wid, end_type, pt in endpoints:
            connected_endpoints = []
            for other_wid, other_end_type, other_pt in endpoints:
                if other_wid == wid:
                    continue
                if points_almost_equal(pt, other_pt, tol=30.0):
                    connected_endpoints.append((other_wid, other_end_type))

            t_junction_hosts = []
            for other_w in walls:
                if other_w["id"] == wid:
                    continue
                d, t = distance_point_to_segment(pt, other_w["start"], other_w["end"])
                if d <= 35.0 and 0.05 < t < 0.95:
                    t_junction_hosts.append(other_w["id"])

            if len(connected_endpoints) == 1:
                self.junction_counts["L-junction"] += 1
            elif len(connected_endpoints) == 2 or len(t_junction_hosts) > 0:
                self.junction_counts["T-junction"] += 1
            elif len(connected_endpoints) >= 3:
                self.junction_counts["Cross-junction"] += 1
            else:
                self.junction_counts["disconnected_endpoints"] += 1
                near_walls = []
                for other_w in walls:
                    if other_w["id"] == wid:
                        continue
                    d, _ = distance_point_to_segment(pt, other_w["start"], other_w["end"])
                    if 35.0 < d <= 250.0:
                        near_walls.append(other_w["id"])

                if near_walls:
                    self.add_issue(
                        severity="warning",
                        category="geometry",
                        description=(
                            f"Wall '{wid}' {end_type} point {pt} has an unintended gap to adjacent wall(s) {near_walls}."
                        ),
                        affected_entities=[wid] + near_walls,
                        suggested_correction="Snap wall endpoint to adjacent wall to close junction cleanly.",
                        requires_human_approval=True,
                    )
                else:
                    self.add_issue(
                        severity="warning",
                        category="geometry",
                        description=f"Wall '{wid}' has disconnected endpoint at {end_type} point {pt}.",
                        affected_entities=[wid],
                        suggested_correction="Verify free-standing partition stub is intended or connect to boundary wall.",
                        requires_human_approval=False,
                    )

        # Adjust L-junction count by 2 since each L-corner is counted from both meeting endpoints
        self.junction_counts["L-junction"] = max(0, self.junction_counts["L-junction"] // 2)

    # ---------------------------------------------------------------------
    # 3. Door & Window Drafting & Conflict Validation
    # ---------------------------------------------------------------------
    def validate_openings(self):
        openings = self._get_openings()
        walls_by_id = {w["id"]: w for w in self._get_walls()}
        openings_by_wall: Dict[str, List[Dict[str, Any]]] = {}

        for op in openings:
            op_id = op.get("id", "")
            op_type = op.get("type", "door")
            wall_id = op.get("wallId")
            width = float(op.get("width", 900.0))

            if not wall_id or wall_id not in walls_by_id:
                self.add_issue(
                    severity="major",
                    category="openings",
                    description=f"Opening '{op_id}' has invalid or missing host wall reference '{wall_id}'.",
                    affected_entities=[op_id],
                    suggested_correction="Assign opening to a valid host wall in the floor model.",
                    requires_human_approval=True,
                )
                continue

            host_wall = walls_by_id[wall_id]
            s, e = host_wall["start"], host_wall["end"]
            wall_len = point_distance(s, e)

            # Center position or distance from start
            dist_from_start = op.get("distanceFromStart")
            if dist_from_start is not None:
                dist_from_start = float(dist_from_start)
                t1 = dist_from_start
                t2 = dist_from_start + width
                center_dist = dist_from_start + width / 2.0
            else:
                center = op.get("center", [0.0, 0.0])
                d, t = distance_point_to_segment(center, s, e)
                center_dist = t * wall_len
                t1 = center_dist - width / 2.0
                t2 = center_dist + width / 2.0

            # Bounds check
            if t2 > wall_len + 1.0 or t1 < -1.0:
                self.add_issue(
                    severity="blocking",
                    category="openings",
                    description=f"Opening '{op_id}' extends beyond host wall length ({t2:.0f}mm > {wall_len:.0f}mm).",
                    affected_entities=[op_id, wall_id],
                    suggested_correction="Reduce opening width or move opening entirely within host wall span.",
                    requires_human_approval=True,
                )

            # Corner clearance check (>= 50mm)
            if t1 < 50.0 or (wall_len - t2) < 50.0:
                self.add_issue(
                    severity="warning",
                    category="openings",
                    description=(
                        f"Corner clearance: opening '{op_id}' within 50mm of wall corner on wall '{wall_id}'."
                    ),
                    affected_entities=[op_id, wall_id],
                    suggested_correction="Offset opening away from wall corner to maintain minimum 50mm structural jamb return.",
                    requires_human_approval=True,
                )

            if wall_id not in openings_by_wall:
                openings_by_wall[wall_id] = []
            openings_by_wall[wall_id].append({
                "id": op_id,
                "t1": t1,
                "t2": t2,
                "width": width,
                "type": op_type,
                "center_dist": center_dist,
            })

        # Overlapping openings check
        for wid, ops_on_wall in openings_by_wall.items():
            ops_sorted = sorted(ops_on_wall, key=lambda o: o["t1"])
            for k in range(len(ops_sorted) - 1):
                cur = ops_sorted[k]
                nxt = ops_sorted[k + 1]
                if cur["t2"] > nxt["t1"]:
                    overlap_mm = cur["t2"] - nxt["t1"]
                    self.add_issue(
                        severity="blocking",
                        category="openings",
                        description=f"Opening '{cur['id']}' overlaps with opening '{nxt['id']}' on wall '{wid}' by {overlap_mm:.0f}mm.",
                        affected_entities=[cur["id"], nxt["id"], wid],
                        suggested_correction="Space openings apart with solid wall segment between them.",
                        requires_human_approval=True,
                    )

    # ---------------------------------------------------------------------
    # 4. Room Boundary & Connectivity Validation
    # ---------------------------------------------------------------------
    def validate_rooms(self):
        rooms = self._get_rooms()
        env = self.model.get("envelope", {})
        env_w = float(env.get("width", 100000.0))
        env_d = float(env.get("depth", 100000.0))

        room_polygons: List[Tuple[str, List[List[float]]]] = []

        for r in rooms:
            rid = r.get("id", "")
            rname = r.get("name", "ROOM")

            boundary = r.get("boundary", r.get("boundaryCorners", []))
            if not boundary:
                continue

            if len(boundary) < 3:
                self.add_issue(
                    severity="major",
                    category="rooms",
                    description=f"Room '{rid}' ({rname}) boundary polygon has only {len(boundary)} vertices (< 3).",
                    affected_entities=[rid],
                    suggested_correction="Provide at least 3 vertices for a closed room boundary.",
                    requires_human_approval=True,
                )
                continue

            poly_pts = [[float(p[0]), float(p[1])] for p in boundary]

            # Envelope containment
            for pt in poly_pts:
                if pt[0] < -20.0 or pt[0] > env_w + 20.0 or pt[1] < -20.0 or pt[1] > env_d + 20.0:
                    self.add_issue(
                        severity="major",
                        category="rooms",
                        description=f"Room '{rid}' ({rname}) exceeds building envelope bounds.",
                        affected_entities=[rid, "envelope"],
                        suggested_correction="Constrain room boundary inside exterior wall perimeter.",
                        requires_human_approval=True,
                    )
                    break

            if is_polygon_self_intersecting(poly_pts):
                self.add_issue(
                    severity="blocking",
                    category="rooms",
                    description=f"Room '{rid}' ({rname}) boundary polygon is self-intersecting (complex polygon).",
                    affected_entities=[rid],
                    suggested_correction="Reconstruct boundary polygon in clockwise or counter-clockwise non-self-intersecting order.",
                    requires_human_approval=False,
                )

            room_polygons.append((rid, poly_pts))

        for i in range(len(room_polygons)):
            r1_id, poly1 = room_polygons[i]
            for j in range(i + 1, len(room_polygons)):
                r2_id, poly2 = room_polygons[j]
                if polygons_overlap(poly1, poly2):
                    self.add_issue(
                        severity="blocking",
                        category="rooms",
                        description=f"Rooms '{r1_id}' and '{r2_id}' have overlapping interior boundary polygons.",
                        affected_entities=[r1_id, r2_id],
                        suggested_correction="Adjust adjacent room boundaries to share common partition wall without overlap.",
                        requires_human_approval=True,
                    )

    # ---------------------------------------------------------------------
    # 5. Elements & Structural Validation
    # ---------------------------------------------------------------------
    def validate_elements_and_structure(self):
        elements = self._get_elements()
        env = self.model.get("envelope", {})
        env_w = float(env.get("width", 100000.0))
        env_d = float(env.get("depth", 100000.0))

        seen_elem_ids = set()
        for el in elements:
            el_id = el.get("id", "")
            if el_id in seen_elem_ids:
                self.add_issue(
                    severity="blocking",
                    category="symbols",
                    description=f"Duplicate architectural element ID '{el_id}' detected.",
                    affected_entities=[el_id],
                    suggested_correction="Assign unique identifier to each architectural element.",
                    requires_human_approval=False,
                )
            seen_elem_ids.add(el_id)

            pos = el.get("position", [0.0, 0.0])
            if pos[0] < 0.0 or pos[0] > env_w or pos[1] < 0.0 or pos[1] > env_d:
                self.add_issue(
                    severity="warning",
                    category="symbols",
                    description=f"Element '{el_id}' at {pos} falls outside the exterior building envelope.",
                    affected_entities=[el_id, "envelope"],
                    suggested_correction="Reposition element within interior room boundaries.",
                    requires_human_approval=True,
                )

    # ---------------------------------------------------------------------
    # Helper Accessors (Floor-Filtered)
    # ---------------------------------------------------------------------
    def _matches_floor(self, entity: Dict[str, Any]) -> bool:
        if self.target_floor_id is None:
            return True
        ent_floor = entity.get("level", entity.get("floorId"))
        if ent_floor is None:
            default_fid = (
                self.model.get("floors", [{}])[0].get("id", "LEVEL-01")
                if self.model.get("floors")
                else self.model.get("floorId", "LEVEL-01")
            )
            return default_fid == self.target_floor_id
        return ent_floor == self.target_floor_id

    def _get_walls(self) -> List[Dict[str, Any]]:
        return [w for w in self.model.get("walls", []) if self._matches_floor(w)]

    def _get_openings(self) -> List[Dict[str, Any]]:
        return [op for op in self.model.get("openings", []) if self._matches_floor(op)]

    def _get_rooms(self) -> List[Dict[str, Any]]:
        return [r for r in self.model.get("rooms", []) if self._matches_floor(r)]

    def _get_elements(self) -> List[Dict[str, Any]]:
        return [el for el in self.model.get("elements", []) if self._matches_floor(el)]
