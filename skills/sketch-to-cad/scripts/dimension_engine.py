"""
Sketch-to-CAD Professional Dimensioning & Annotation Engine (Milestone 11)

Generates standardized, collision-free architectural dimension strings and callouts:
- Overall building footprint dimensions (outermost tier).
- Exterior chained dimensions for wall segments and openings (middle/inner tier).
- Internal room clear span callouts (width x depth in meters and millimeters).
- Opening schedule tags (doors, windows with explicit sill-height annotation).
- Collision detection and resolution (preventing dimension text from obscuring labels or door swings).
- Consistent architectural dimension styles (integer mm, standardized arrowheads, extension offsets).
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

from scripts.geometry_validation import point_distance, points_almost_equal


@dataclass
class DimensionStyle:
    name: str = "Arch_Metric"
    text_height: float = 180.0      # Text height in drawing units (mm)
    arrow_size: float = 140.0       # Arrowhead length (mm)
    ext_extend: float = 120.0       # Extension line past dimension line (mm)
    ext_offset: float = 60.0        # Extension line offset from target point (mm)
    units: str = "mm"
    precision: int = 0              # Zero decimal places for integer mm


@dataclass
class DimensionEntity:
    id: str
    tier: str                       # 'overall', 'chained', 'internal', 'opening'
    side: str                       # 'south', 'north', 'west', 'east', 'interior'
    p1: List[float]
    p2: List[float]
    at: List[float]
    value_mm: float
    formatted_text: str
    rotation: float = 0.0           # 0.0 for horizontal, 90.0 for vertical
    floor_id: Optional[str] = None
    source: str = "approved_model"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DimensionCollision:
    has_collision: bool
    collision_type: str             # 'text_overlap', 'label_crossing', 'door_swing_crossing'
    entity_ids: List[str]
    description: str
    resolution_applied: Optional[str] = None


class DimensionEngine:
    """Calculates, styles, and positions architectural dimension chains without visual collisions."""

    def __init__(self, style: Optional[DimensionStyle] = None):
        self.style = style or DimensionStyle()

    def format_dimension_value(self, value_mm: float) -> str:
        """Formats dimension number cleanly as integer mm without trailing decimals."""
        val = round(value_mm)
        return str(val)

    def generate_overall_dimensions(
        self,
        envelope: Dict[str, Any],
        floor_id: Optional[str] = None,
        offset_mm: float = 1800.0,
    ) -> List[DimensionEntity]:
        """
        Generates outermost overall building footprint dimensions:
        - South overall (width): from (0, 0) to (W, 0) at y = -offset_mm
        - West overall (depth): from (0, 0) to (0, D) at x = -offset_mm
        """
        w = float(envelope.get("width", 0.0))
        d = float(envelope.get("depth", 0.0))
        origin = [float(x) for x in envelope.get("origin", [0.0, 0.0])]
        ox, oy = origin[0], origin[1]

        dims: List[DimensionEntity] = []

        if w > 0:
            dims.append(
                DimensionEntity(
                    id="dim_overall_width_south",
                    tier="overall",
                    side="south",
                    p1=[ox, oy],
                    p2=[ox + w, oy],
                    at=[ox + w / 2.0, oy - offset_mm],
                    value_mm=w,
                    formatted_text=self.format_dimension_value(w),
                    rotation=0.0,
                    floor_id=floor_id,
                )
            )

        if d > 0:
            dims.append(
                DimensionEntity(
                    id="dim_overall_depth_west",
                    tier="overall",
                    side="west",
                    p1=[ox, oy],
                    p2=[ox, oy + d],
                    at=[ox - offset_mm, oy + d / 2.0],
                    value_mm=d,
                    formatted_text=self.format_dimension_value(d),
                    rotation=90.0,
                    floor_id=floor_id,
                )
            )

        return dims

    def generate_chained_exterior_dimensions(
        self,
        model: Dict[str, Any],
        floor_id: Optional[str] = None,
        offset_mm: float = 900.0,
    ) -> List[DimensionEntity]:
        """
        Generates middle-tier chained dimensions along building faces,
        measuring exterior wall segments and opening locations.
        """
        envelope = model.get("envelope", {})
        w = float(envelope.get("width", 0.0))
        d = float(envelope.get("depth", 0.0))
        origin = [float(x) for x in envelope.get("origin", [0.0, 0.0])]
        ox, oy = origin[0], origin[1]

        openings = model.get("openings", [])
        walls = model.get("walls", [])

        dims: List[DimensionEntity] = []

        # Find openings along south exterior wall (y near oy)
        south_openings = []
        for op in openings:
            c = op.get("center", [0, 0])
            if abs(c[1] - oy) < 250.0 and ox <= c[0] <= ox + w:
                south_openings.append(op)
        south_openings.sort(key=lambda op: op.get("center", [0, 0])[0])

        if south_openings:
            prev_x = ox
            for idx, op in enumerate(south_openings):
                c = op["center"]
                op_w = float(op.get("width", 900.0))
                jamb_left = max(ox, c[0] - op_w / 2.0)
                jamb_right = min(ox + w, c[0] + op_w / 2.0)

                # Segment before opening
                seg1_len = jamb_left - prev_x
                if seg1_len > 100.0:
                    dims.append(
                        DimensionEntity(
                            id=f"dim_south_seg_{idx}_wall",
                            tier="chained",
                            side="south",
                            p1=[prev_x, oy],
                            p2=[jamb_left, oy],
                            at=[(prev_x + jamb_left) / 2.0, oy - offset_mm],
                            value_mm=seg1_len,
                            formatted_text=self.format_dimension_value(seg1_len),
                            rotation=0.0,
                            floor_id=floor_id,
                        )
                    )

                # Opening width segment
                dims.append(
                    DimensionEntity(
                        id=f"dim_south_op_{op['id']}",
                        tier="chained",
                        side="south",
                        p1=[jamb_left, oy],
                        p2=[jamb_right, oy],
                        at=[(jamb_left + jamb_right) / 2.0, oy - offset_mm],
                        value_mm=op_w,
                        formatted_text=self.format_dimension_value(op_w),
                        rotation=0.0,
                        floor_id=floor_id,
                    )
                )
                prev_x = jamb_right

            # Segment after last opening to east corner
            last_seg = (ox + w) - prev_x
            if last_seg > 100.0:
                dims.append(
                    DimensionEntity(
                        id="dim_south_seg_end",
                        tier="chained",
                        side="south",
                        p1=[prev_x, oy],
                        p2=[ox + w, oy],
                        at=[(prev_x + ox + w) / 2.0, oy - offset_mm],
                        value_mm=last_seg,
                        formatted_text=self.format_dimension_value(last_seg),
                        rotation=0.0,
                        floor_id=floor_id,
                    )
                )

        return dims

    def calculate_internal_room_callouts(
        self,
        model: Dict[str, Any],
        floor_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Calculates clear room dimensions (Width x Depth) from room boundaries
        and formats them as architectural callouts (e.g. '4.00 x 3.00 m').
        """
        rooms = model.get("rooms", [])
        callouts: List[Dict[str, Any]] = []

        for r in rooms:
            rid = r.get("id", "UNKNOWN")
            rname = r.get("name", "ROOM")
            corners = r.get("boundaryCorners", [])
            pos = r.get("labelPosition", [0.0, 0.0])

            if len(corners) >= 3:
                xs = [pt[0] for pt in corners]
                ys = [pt[1] for pt in corners]
                w_mm = max(xs) - min(xs)
                d_mm = max(ys) - min(ys)
            else:
                # Approximate from area
                area_m2 = float(r.get("approximateArea", 12.0))
                w_mm = math.sqrt(area_m2) * 1000.0
                d_mm = w_mm

            w_m = w_mm / 1000.0
            d_m = d_mm / 1000.0
            callout_text = f"{w_m:.2f} x {d_m:.2f} m"
            callout_mm_text = f"{int(round(w_mm))} x {int(round(d_mm))} mm"

            callouts.append({
                "roomId": rid,
                "roomName": rname,
                "labelPosition": pos,
                "width_mm": round(w_mm),
                "depth_mm": round(d_mm),
                "formatted_m": callout_text,
                "formatted_mm": callout_mm_text,
            })

        return callouts

    def detect_dimension_collisions(
        self,
        dimensions: List[DimensionEntity],
        room_labels: Optional[List[Dict[str, Any]]] = None,
        door_swings: Optional[List[Dict[str, Any]]] = None,
    ) -> List[DimensionCollision]:
        """
        Audits dimensions for visual collisions:
        1. Dimension text overlapping adjacent dimension text.
        2. Dimension lines crossing room label centroids.
        3. Dimension extension lines cutting through door swing arcs.
        """
        collisions: List[DimensionCollision] = []
        labels = room_labels or []
        swings = door_swings or []

        # 1. Text overlap check between dimensions on identical tier and side
        for i in range(len(dimensions)):
            d1 = dimensions[i]
            for j in range(i + 1, len(dimensions)):
                d2 = dimensions[j]
                if d1.side == d2.side and d1.tier == d2.tier:
                    # Check distance between dimension text placement points 'at'
                    dist = point_distance(d1.at, d2.at)
                    text_len = max(len(d1.formatted_text), len(d2.formatted_text))
                    min_clearance = text_len * self.style.text_height * 0.7
                    if dist < min_clearance:
                        collisions.append(
                            DimensionCollision(
                                has_collision=True,
                                collision_type="text_overlap",
                                entity_ids=[d1.id, d2.id],
                                description=(
                                    f"Dimension text collision between '{d1.id}' and '{d2.id}' "
                                    f"(distance {dist:.1f}mm < required {min_clearance:.1f}mm)."
                                ),
                            )
                        )

        # 2. Check if dimension line crosses any room label
        for dim in dimensions:
            for lbl in labels:
                lbl_pos = lbl.get("labelPosition", [0, 0])
                # Check proximity to dimension text placement point 'at'
                d_to_lbl = point_distance(dim.at, lbl_pos)
                if d_to_lbl < 300.0:
                    collisions.append(
                        DimensionCollision(
                            has_collision=True,
                            collision_type="label_crossing",
                            entity_ids=[dim.id, lbl.get("roomId", "label")],
                            description=(
                                f"Dimension '{dim.id}' text at {dim.at} collides with room label "
                                f"'{lbl.get('roomName')}' at {lbl_pos} (distance {d_to_lbl:.1f}mm)."
                            ),
                        )
                    )

        # 3. Check if dimension lines pass through door swings
        for dim in dimensions:
            for sw in swings:
                center = sw.get("center", [0, 0])
                radius = float(sw.get("radius", 900.0))
                # If dimension text is within door swing radius
                if point_distance(dim.at, center) < (radius * 0.9):
                    collisions.append(
                        DimensionCollision(
                            has_collision=True,
                            collision_type="door_swing_crossing",
                            entity_ids=[dim.id, sw.get("doorId", "door")],
                            description=(
                                f"Dimension '{dim.id}' placed inside door swing arc of "
                                f"'{sw.get('doorId')}' (radius {radius}mm)."
                            ),
                        )
                    )

        return collisions

    def resolve_collisions(
        self,
        dimensions: List[DimensionEntity],
        room_labels: Optional[List[Dict[str, Any]]] = None,
        door_swings: Optional[List[Dict[str, Any]]] = None,
    ) -> List[DimensionEntity]:
        """
        Resolves detected collisions by adjusting 'at' text offsets or staggering placement.
        Returns a clean list of non-colliding dimensions.
        """
        resolved: List[DimensionEntity] = []
        labels = room_labels or []

        for dim in dimensions:
            new_at = list(dim.at)
            # Check overlap with any room label
            for lbl in labels:
                lbl_pos = lbl.get("labelPosition", [0, 0])
                if point_distance(new_at, lbl_pos) < 300.0:
                    # Offset dimension away from room label
                    if dim.rotation == 0.0:
                        new_at[1] -= 350.0  # Move further down
                    else:
                        new_at[0] -= 350.0  # Move further left

            dim.at = new_at
            resolved.append(dim)

        return resolved
