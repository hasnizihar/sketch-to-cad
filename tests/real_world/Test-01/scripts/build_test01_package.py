"""
Build extracted observations, canonical coordinate model, approval package,
and uncertainty register for Real-World Test 01 (Hand-Drawn Residential Floor Plan).
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import json
from jsonschema import validate

from scripts.approval_package import create_approval_package, generate_proposal_markdown
from scripts.sketch_interpreter import validate_observations, get_observations_schema
TEST_DIR = REPO_ROOT / "tests" / "real_world" / "Test-01"
TEST_DIR.mkdir(parents=True, exist_ok=True)

# 1. Source Metadata
source_meta = {
    "source_file": "source_sketch.jpg",
    "source_path": str((TEST_DIR / "source_sketch.jpg").resolve()),
    "file_type": "jpg",
    "page_number": 1,
    "total_pages": 1,
    "dimensions_pixels": {"width": 845, "height": 1024},
    "dpi": 72.0,
    "orientation_degrees": 0,
    "source_floor_hint": "Ground Floor",
    "sha256": "12ca802a25cd855467a62473c7c35f423ca01ed53ab3818b61b7b75cf9259957",
    "preprocessing_applied": ["Deterministic RGB Normalization"]
}

# 2. Extracted Observations adhering to sketch-observations.schema.json
observations = {
    "source_metadata": source_meta,
    "status": "extracted",
    "confidence_summary": {
        "overall_confidence": 0.90,
        "dimension_reliability": "high",
        "notes": "Nordic/Estonian single-storey residential villa with sauna wing and wrap-around terrace. Explicit dimensions: 5000, 10000, 16000, 5000, 14200, 3000 mm. Contradiction detected on West depth chain (19200 mm vs 19000 mm on East)."
    },
    "walls": [
        # Exterior Walls
        {"id": "W-EXT-NORTH-1", "wall_type": "exterior", "start_point_pixel": [90, 105], "end_point_pixel": [310, 105], "thickness_mm": 200.0, "thickness_category": "inferred", "confidence": 0.95, "provenance": "source_sketch", "source_bbox": [0.09, 0.10, 0.12, 0.37]},
        {"id": "W-EXT-NORTH-2", "wall_type": "exterior", "start_point_pixel": [310, 105], "end_point_pixel": [755, 105], "thickness_mm": 200.0, "thickness_category": "inferred", "confidence": 0.95, "provenance": "source_sketch", "source_bbox": [0.09, 0.36, 0.12, 0.90]},
        {"id": "W-EXT-EAST", "wall_type": "exterior", "start_point_pixel": [755, 105], "end_point_pixel": [765, 830], "thickness_mm": 200.0, "thickness_category": "inferred", "confidence": 0.95, "provenance": "source_sketch", "source_bbox": [0.10, 0.88, 0.82, 0.92]},
        {"id": "W-EXT-SOUTH-MAIN", "wall_type": "exterior", "start_point_pixel": [765, 830], "end_point_pixel": [315, 830], "thickness_mm": 200.0, "thickness_category": "inferred", "confidence": 0.95, "provenance": "source_sketch", "source_bbox": [0.80, 0.36, 0.83, 0.91]},
        {"id": "W-EXT-WEST-MAIN", "wall_type": "exterior", "start_point_pixel": [315, 830], "end_point_pixel": [310, 325], "thickness_mm": 200.0, "thickness_category": "inferred", "confidence": 0.95, "provenance": "source_sketch", "source_bbox": [0.31, 0.35, 0.82, 0.38]},
        {"id": "W-EXT-SOUTH-SAUNA", "wall_type": "exterior", "start_point_pixel": [310, 325], "end_point_pixel": [90, 325], "thickness_mm": 200.0, "thickness_category": "inferred", "confidence": 0.95, "provenance": "source_sketch", "source_bbox": [0.31, 0.10, 0.33, 0.37]},
        {"id": "W-EXT-WEST-SAUNA", "wall_type": "exterior", "start_point_pixel": [90, 325], "end_point_pixel": [90, 105], "thickness_mm": 200.0, "thickness_category": "inferred", "confidence": 0.95, "provenance": "source_sketch", "source_bbox": [0.10, 0.09, 0.33, 0.12]},

        # Interior Partitions (Sauna Wing)
        {"id": "W-INT-SAUNA-VERT", "wall_type": "interior", "start_point_pixel": [180, 105], "end_point_pixel": [180, 325], "thickness_mm": 100.0, "thickness_category": "inferred", "confidence": 0.90, "provenance": "source_sketch", "source_bbox": [0.10, 0.20, 0.32, 0.23]},
        {"id": "W-INT-SAUNA-HORIZ", "wall_type": "interior", "start_point_pixel": [90, 240], "end_point_pixel": [180, 240], "thickness_mm": 100.0, "thickness_category": "inferred", "confidence": 0.90, "provenance": "source_sketch", "source_bbox": [0.22, 0.10, 0.25, 0.22]},
        {"id": "W-INT-SAUNA-EAST", "wall_type": "interior", "start_point_pixel": [310, 105], "end_point_pixel": [310, 325], "thickness_mm": 150.0, "thickness_category": "inferred", "confidence": 0.90, "provenance": "source_sketch", "source_bbox": [0.10, 0.35, 0.32, 0.38]},

        # Interior Partitions (Main Body - North Utility Zone)
        {"id": "W-INT-CORR-NORTH", "wall_type": "interior", "start_point_pixel": [310, 215], "end_point_pixel": [580, 215], "thickness_mm": 100.0, "thickness_category": "inferred", "confidence": 0.90, "provenance": "source_sketch", "source_bbox": [0.20, 0.36, 0.23, 0.69]},
        {"id": "W-INT-UTIL-1", "wall_type": "interior", "start_point_pixel": [415, 105], "end_point_pixel": [415, 215], "thickness_mm": 100.0, "thickness_category": "inferred", "confidence": 0.90, "provenance": "source_sketch", "source_bbox": [0.10, 0.48, 0.22, 0.51]},
        {"id": "W-INT-UTIL-2", "wall_type": "interior", "start_point_pixel": [505, 105], "end_point_pixel": [505, 215], "thickness_mm": 100.0, "thickness_category": "inferred", "confidence": 0.90, "provenance": "source_sketch", "source_bbox": [0.10, 0.58, 0.22, 0.61]},

        # Interior Partitions (East Wing Bedrooms & Esik)
        {"id": "W-INT-SPINE-EAST", "wall_type": "interior", "start_point_pixel": [580, 105], "end_point_pixel": [580, 500], "thickness_mm": 100.0, "thickness_category": "inferred", "confidence": 0.90, "provenance": "source_sketch", "source_bbox": [0.10, 0.67, 0.50, 0.70]},
        {"id": "W-INT-BED-1-2", "wall_type": "interior", "start_point_pixel": [580, 230], "end_point_pixel": [755, 230], "thickness_mm": 100.0, "thickness_category": "inferred", "confidence": 0.90, "provenance": "source_sketch", "source_bbox": [0.21, 0.68, 0.24, 0.90]},
        {"id": "W-INT-BED-2-ESIK", "wall_type": "interior", "start_point_pixel": [580, 360], "end_point_pixel": [755, 360], "thickness_mm": 100.0, "thickness_category": "inferred", "confidence": 0.90, "provenance": "source_sketch", "source_bbox": [0.34, 0.68, 0.37, 0.90]},
        {"id": "W-INT-ESIK-SOUTH", "wall_type": "interior", "start_point_pixel": [580, 500], "end_point_pixel": [765, 500], "thickness_mm": 100.0, "thickness_category": "inferred", "confidence": 0.90, "provenance": "source_sketch", "source_bbox": [0.48, 0.68, 0.51, 0.91]},

        # Interior Partitions (Master Bedroom & Bathroom)
        {"id": "W-INT-CORR-WEST", "wall_type": "interior", "start_point_pixel": [505, 275], "end_point_pixel": [505, 550], "thickness_mm": 100.0, "thickness_category": "inferred", "confidence": 0.90, "provenance": "source_sketch", "source_bbox": [0.26, 0.58, 0.55, 0.61]},
        {"id": "W-INT-MASTER-BATH", "wall_type": "interior", "start_point_pixel": [315, 450], "end_point_pixel": [505, 450], "thickness_mm": 100.0, "thickness_category": "inferred", "confidence": 0.90, "provenance": "source_sketch", "source_bbox": [0.43, 0.36, 0.46, 0.60]},
        {"id": "W-INT-BATH-LIVING", "wall_type": "interior", "start_point_pixel": [315, 550], "end_point_pixel": [505, 550], "thickness_mm": 100.0, "thickness_category": "inferred", "confidence": 0.90, "provenance": "source_sketch", "source_bbox": [0.53, 0.36, 0.56, 0.60]}
    ],
    "openings": [
        # Exterior Doors
        {"id": "D-ENTRY", "type": "door", "sub_type": "single_swing", "swing_direction": "outward_right", "width_mm": 900.0, "width_category": "inferred", "host_wall_ref": "W-EXT-EAST", "associated_room": "R-ESIK", "confidence": 0.95, "provenance": "source_sketch", "source_bbox": [0.38, 0.88, 0.44, 0.92]},
        {"id": "D-SAUNA-TERRACE", "type": "door", "sub_type": "sliding", "swing_direction": "sliding", "width_mm": 1500.0, "width_category": "inferred", "host_wall_ref": "W-EXT-SOUTH-SAUNA", "associated_room": "R-SAUNA-PUHKE", "confidence": 0.90, "provenance": "source_sketch", "source_bbox": [0.31, 0.19, 0.33, 0.30]},
        {"id": "D-LIVING-TERRACE", "type": "door", "sub_type": "sliding", "swing_direction": "sliding", "width_mm": 2400.0, "width_category": "inferred", "host_wall_ref": "W-EXT-SOUTH-MAIN", "associated_room": "R-LIVING-KITCHEN", "confidence": 0.95, "provenance": "source_sketch", "source_bbox": [0.81, 0.62, 0.83, 0.78]},

        # Interior Doors
        {"id": "D-ESIK-LIVING", "type": "opening", "sub_type": "cased_opening", "swing_direction": None, "width_mm": 1200.0, "width_category": "inferred", "host_wall_ref": "W-INT-SPINE-EAST", "associated_room": "R-ESIK", "confidence": 0.90, "provenance": "source_sketch", "source_bbox": [0.42, 0.68, 0.46, 0.70]},
        {"id": "D-BED-1", "type": "door", "sub_type": "single_swing", "swing_direction": "inward_right", "width_mm": 800.0, "width_category": "inferred", "host_wall_ref": "W-INT-SPINE-EAST", "associated_room": "R-BED-1", "confidence": 0.90, "provenance": "source_sketch", "source_bbox": [0.18, 0.68, 0.22, 0.70]},
        {"id": "D-BED-2", "type": "door", "sub_type": "single_swing", "swing_direction": "inward_right", "width_mm": 800.0, "width_category": "inferred", "host_wall_ref": "W-INT-SPINE-EAST", "associated_room": "R-BED-2", "confidence": 0.90, "provenance": "source_sketch", "source_bbox": [0.28, 0.68, 0.32, 0.70]},
        {"id": "D-WC", "type": "door", "sub_type": "single_swing", "swing_direction": "inward_left", "width_mm": 700.0, "width_category": "inferred", "host_wall_ref": "W-INT-CORR-NORTH", "associated_room": "R-WC", "confidence": 0.85, "provenance": "source_sketch", "source_bbox": [0.17, 0.61, 0.21, 0.66]},
        {"id": "D-TEH", "type": "door", "sub_type": "single_swing", "swing_direction": "outward_left", "width_mm": 800.0, "width_category": "inferred", "host_wall_ref": "W-INT-CORR-NORTH", "associated_room": "R-TEH", "confidence": 0.90, "provenance": "source_sketch", "source_bbox": [0.20, 0.52, 0.23, 0.58]},
        {"id": "D-MAJAPIDAMIS", "type": "door", "sub_type": "single_swing", "swing_direction": "outward_left", "width_mm": 800.0, "width_category": "inferred", "host_wall_ref": "W-INT-CORR-NORTH", "associated_room": "R-MAJAPIDAMIS", "confidence": 0.90, "provenance": "source_sketch", "source_bbox": [0.20, 0.40, 0.23, 0.46]},
        {"id": "D-SAUNA-HALL", "type": "door", "sub_type": "single_swing", "swing_direction": "inward_left", "width_mm": 800.0, "width_category": "inferred", "host_wall_ref": "W-INT-SAUNA-EAST", "associated_room": "R-SAUNA-PUHKE", "confidence": 0.85, "provenance": "source_sketch", "source_bbox": [0.22, 0.35, 0.27, 0.38]},
        {"id": "D-MASTER-BED", "type": "door", "sub_type": "single_swing", "swing_direction": "inward_left", "width_mm": 800.0, "width_category": "inferred", "host_wall_ref": "W-INT-CORR-WEST", "associated_room": "R-MASTER-BED", "confidence": 0.90, "provenance": "source_sketch", "source_bbox": [0.35, 0.58, 0.40, 0.61]},
        {"id": "D-BATHROOM", "type": "door", "sub_type": "single_swing", "swing_direction": "inward_left", "width_mm": 800.0, "width_category": "inferred", "host_wall_ref": "W-INT-CORR-WEST", "associated_room": "R-BATHROOM", "confidence": 0.90, "provenance": "source_sketch", "source_bbox": [0.45, 0.58, 0.49, 0.61]},
        {"id": "D-DUSS", "type": "door", "sub_type": "single_swing", "swing_direction": "inward_left", "width_mm": 700.0, "width_category": "inferred", "host_wall_ref": "W-INT-SAUNA-VERT", "associated_room": "R-DUSS", "confidence": 0.85, "provenance": "source_sketch", "source_bbox": [0.17, 0.20, 0.21, 0.23]},
        {"id": "D-SAUN", "type": "door", "sub_type": "single_swing", "swing_direction": "outward_right", "width_mm": 700.0, "width_category": "inferred", "host_wall_ref": "W-INT-SAUNA-HORIZ", "associated_room": "R-SAUN", "confidence": 0.85, "provenance": "source_sketch", "source_bbox": [0.22, 0.14, 0.25, 0.18]},

        # Windows
        {"id": "W-DUSS", "type": "window", "sub_type": "casement", "swing_direction": None, "width_mm": 900.0, "width_category": "estimated", "host_wall_ref": "W-EXT-NORTH-1", "associated_room": "R-DUSS", "confidence": 0.90, "provenance": "source_sketch", "source_bbox": [0.09, 0.14, 0.11, 0.18]},
        {"id": "W-SAUNA-PUHKE", "type": "window", "sub_type": "casement", "swing_direction": None, "width_mm": 1200.0, "width_category": "estimated", "host_wall_ref": "W-EXT-NORTH-1", "associated_room": "R-SAUNA-PUHKE", "confidence": 0.90, "provenance": "source_sketch", "source_bbox": [0.09, 0.24, 0.11, 0.29]},
        {"id": "W-MAJAPIDAMIS", "type": "window", "sub_type": "casement", "swing_direction": None, "width_mm": 1000.0, "width_category": "estimated", "host_wall_ref": "W-EXT-NORTH-2", "associated_room": "R-MAJAPIDAMIS", "confidence": 0.90, "provenance": "source_sketch", "source_bbox": [0.09, 0.40, 0.11, 0.47]},
        {"id": "W-WC", "type": "window", "sub_type": "casement", "swing_direction": None, "width_mm": 600.0, "width_category": "estimated", "host_wall_ref": "W-EXT-NORTH-2", "associated_room": "R-WC", "confidence": 0.85, "provenance": "source_sketch", "source_bbox": [0.09, 0.62, 0.11, 0.65]},
        {"id": "W-BED-1", "type": "window", "sub_type": "casement", "swing_direction": None, "width_mm": 1200.0, "width_category": "estimated", "host_wall_ref": "W-EXT-NORTH-2", "associated_room": "R-BED-1", "confidence": 0.90, "provenance": "source_sketch", "source_bbox": [0.09, 0.77, 0.11, 0.84]},
        {"id": "W-BED-2", "type": "window", "sub_type": "casement", "swing_direction": None, "width_mm": 1200.0, "width_category": "estimated", "host_wall_ref": "W-EXT-EAST", "associated_room": "R-BED-2", "confidence": 0.90, "provenance": "source_sketch", "source_bbox": [0.24, 0.89, 0.30, 0.92]},
        {"id": "W-MASTER-BED", "type": "window", "sub_type": "casement", "swing_direction": None, "width_mm": 1200.0, "width_category": "estimated", "host_wall_ref": "W-EXT-WEST-MAIN", "associated_room": "R-MASTER-BED", "confidence": 0.90, "provenance": "source_sketch", "source_bbox": [0.38, 0.35, 0.44, 0.38]},
        {"id": "W-BATHROOM", "type": "window", "sub_type": "casement", "swing_direction": None, "width_mm": 900.0, "width_category": "estimated", "host_wall_ref": "W-EXT-WEST-MAIN", "associated_room": "R-BATHROOM", "confidence": 0.90, "provenance": "source_sketch", "source_bbox": [0.47, 0.35, 0.51, 0.38]},
        {"id": "W-LIVING-WEST", "type": "window", "sub_type": "casement", "swing_direction": None, "width_mm": 1500.0, "width_category": "estimated", "host_wall_ref": "W-EXT-WEST-MAIN", "associated_room": "R-LIVING-KITCHEN", "confidence": 0.90, "provenance": "source_sketch", "source_bbox": [0.70, 0.35, 0.76, 0.38]},
        {"id": "W-LIVING-EAST", "type": "window", "sub_type": "casement", "swing_direction": None, "width_mm": 1500.0, "width_category": "estimated", "host_wall_ref": "W-EXT-EAST", "associated_room": "R-LIVING-KITCHEN", "confidence": 0.90, "provenance": "source_sketch", "source_bbox": [0.55, 0.88, 0.68, 0.92]},
        {"id": "W-LIVING-SOUTH", "type": "window", "sub_type": "casement", "swing_direction": None, "width_mm": 1800.0, "width_category": "estimated", "host_wall_ref": "W-EXT-SOUTH-MAIN", "associated_room": "R-LIVING-KITCHEN", "confidence": 0.90, "provenance": "source_sketch", "source_bbox": [0.81, 0.44, 0.83, 0.56]}
    ],
    "rooms": [
        {"id": "R-DUSS", "raw_label": "Dušš 6 m²", "standardized_type": "bathroom", "floor_level": "Level 1", "annotated_dimensions_text": "6 m²", "approx_width_mm": 1800.0, "approx_depth_mm": 2500.0, "dimension_provenance": "explicit", "confidence": 0.95, "source_bbox": [0.12, 0.12, 0.22, 0.20]},
        {"id": "R-SAUN", "raw_label": "Saun 4 m²", "standardized_type": "sauna", "floor_level": "Level 1", "annotated_dimensions_text": "4 m²", "approx_width_mm": 1800.0, "approx_depth_mm": 2000.0, "dimension_provenance": "explicit", "confidence": 0.95, "source_bbox": [0.24, 0.12, 0.31, 0.20]},
        {"id": "R-SAUNA-PUHKE", "raw_label": "Sauna Puhkeruum 15 m²", "standardized_type": "living", "floor_level": "Level 1", "annotated_dimensions_text": "15 m²", "approx_width_mm": 3200.0, "approx_depth_mm": 4800.0, "dimension_provenance": "explicit", "confidence": 0.95, "source_bbox": [0.16, 0.22, 0.30, 0.34]},
        {"id": "R-MAJAPIDAMIS", "raw_label": "MAJAPIDAMIS 6 m²", "standardized_type": "utility", "floor_level": "Level 1", "annotated_dimensions_text": "6 m²", "approx_width_mm": 2400.0, "approx_depth_mm": 2300.0, "dimension_provenance": "explicit", "confidence": 0.95, "source_bbox": [0.12, 0.38, 0.20, 0.48]},
        {"id": "R-TEH", "raw_label": "TEH 5 m²", "standardized_type": "mechanical", "floor_level": "Level 1", "annotated_dimensions_text": "5 m²", "approx_width_mm": 2000.0, "approx_depth_mm": 2300.0, "dimension_provenance": "explicit", "confidence": 0.95, "source_bbox": [0.12, 0.49, 0.20, 0.58]},
        {"id": "R-WC", "raw_label": "WC 2.4 m²", "standardized_type": "toilet", "floor_level": "Level 1", "annotated_dimensions_text": "2.4 m²", "approx_width_mm": 1300.0, "approx_depth_mm": 1800.0, "dimension_provenance": "explicit", "confidence": 0.95, "source_bbox": [0.12, 0.60, 0.18, 0.67]},
        {"id": "R-BED-1", "raw_label": "12 m²", "standardized_type": "bedroom", "floor_level": "Level 1", "annotated_dimensions_text": "12 m²", "approx_width_mm": 4200.0, "approx_depth_mm": 3000.0, "dimension_provenance": "explicit", "confidence": 0.95, "source_bbox": [0.12, 0.70, 0.23, 0.88]},
        {"id": "R-BED-2", "raw_label": "12 m²", "standardized_type": "bedroom", "floor_level": "Level 1", "annotated_dimensions_text": "12 m²", "approx_width_mm": 4200.0, "approx_depth_mm": 3000.0, "dimension_provenance": "explicit", "confidence": 0.95, "source_bbox": [0.24, 0.70, 0.35, 0.88]},
        {"id": "R-ESIK", "raw_label": "esik 12.8 m²", "standardized_type": "entry", "floor_level": "Level 1", "annotated_dimensions_text": "12.8 m²", "approx_width_mm": 4200.0, "approx_depth_mm": 3100.0, "dimension_provenance": "explicit", "confidence": 0.95, "source_bbox": [0.38, 0.70, 0.48, 0.88]},
        {"id": "R-MASTER-BED", "raw_label": "17.6 m²", "standardized_type": "bedroom", "floor_level": "Level 1", "annotated_dimensions_text": "17.6 m²", "approx_width_mm": 3800.0, "approx_depth_mm": 4200.0, "dimension_provenance": "explicit", "confidence": 0.95, "source_bbox": [0.27, 0.37, 0.42, 0.58]},
        {"id": "R-BATHROOM", "raw_label": "vannituba 6.5 m²", "standardized_type": "bathroom", "floor_level": "Level 1", "annotated_dimensions_text": "6.5 m²", "approx_width_mm": 3800.0, "approx_depth_mm": 2500.0, "dimension_provenance": "explicit", "confidence": 0.95, "source_bbox": [0.44, 0.37, 0.53, 0.58]},
        {"id": "R-LIVING-KITCHEN", "raw_label": "Elutuba köök 65 m²", "standardized_type": "living", "floor_level": "Level 1", "annotated_dimensions_text": "65 m²", "approx_width_mm": 9600.0, "approx_depth_mm": 6500.0, "dimension_provenance": "explicit", "confidence": 0.95, "source_bbox": [0.55, 0.36, 0.82, 0.90]},
        {"id": "R-CORRIDOR", "raw_label": "Koridor", "standardized_type": "hallway", "floor_level": "Level 1", "annotated_dimensions_text": None, "approx_width_mm": 1500.0, "approx_depth_mm": 7000.0, "dimension_provenance": "inferred", "confidence": 0.85, "source_bbox": [0.22, 0.58, 0.52, 0.68]},
        {"id": "R-TERRACE-SOUTH", "raw_label": "Terrass", "standardized_type": "terrace", "floor_level": "Level 1", "annotated_dimensions_text": "3000", "approx_width_mm": 10000.0, "approx_depth_mm": 3000.0, "dimension_provenance": "explicit", "confidence": 0.90, "source_bbox": [0.83, 0.36, 0.96, 0.90]},
        {"id": "R-TERRACE-WEST", "raw_label": "Terrass", "standardized_type": "terrace", "floor_level": "Level 1", "annotated_dimensions_text": "14200", "approx_width_mm": 5000.0, "approx_depth_mm": 11000.0, "dimension_provenance": "explicit", "confidence": 0.85, "source_bbox": [0.35, 0.10, 0.83, 0.35]}
    ],
    "dimensions": [
        {"id": "DIM-TOP-1", "source_text": "5000", "value_mm": 5000.0, "unit_source": "mm", "category": "explicit", "target_entity_type": "overall_width", "target_entity_id": "W-EXT-NORTH-1", "confidence": 0.98, "source_bbox": [0.03, 0.17, 0.07, 0.28]},
        {"id": "DIM-TOP-2", "source_text": "10000", "value_mm": 10000.0, "unit_source": "mm", "category": "explicit", "target_entity_type": "overall_width", "target_entity_id": "W-EXT-NORTH-2", "confidence": 0.98, "source_bbox": [0.02, 0.55, 0.06, 0.68]},
        {"id": "DIM-RIGHT-1", "source_text": "16000", "value_mm": 16000.0, "unit_source": "mm", "category": "explicit", "target_entity_type": "overall_depth", "target_entity_id": "W-EXT-EAST", "confidence": 0.98, "source_bbox": [0.39, 0.94, 0.53, 0.99]},
        {"id": "DIM-RIGHT-2", "source_text": "3000", "value_mm": 3000.0, "unit_source": "mm", "category": "explicit", "target_entity_type": "overall_depth", "target_entity_id": "R-TERRACE-SOUTH", "confidence": 0.95, "source_bbox": [0.84, 0.94, 0.92, 0.99]},
        {"id": "DIM-LEFT-1", "source_text": "5000", "value_mm": 5000.0, "unit_source": "mm", "category": "explicit", "target_entity_type": "overall_depth", "target_entity_id": "W-EXT-WEST-SAUNA", "confidence": 0.98, "source_bbox": [0.17, 0.03, 0.28, 0.08]},
        {"id": "DIM-LEFT-2", "source_text": "14200", "value_mm": 14200.0, "unit_source": "mm", "category": "explicit", "target_entity_type": "overall_depth", "target_entity_id": "R-TERRACE-WEST", "confidence": 0.92, "source_bbox": [0.53, 0.03, 0.65, 0.08]}
    ],
    "columns": [
        {"id": "COL-TERRACE-01", "shape": "rectangular", "width_mm_hint": 200.0, "depth_mm_hint": 200.0, "confidence": 0.90, "source_bbox": [0.93, 0.37, 0.96, 0.40]},
        {"id": "COL-TERRACE-02", "shape": "rectangular", "width_mm_hint": 200.0, "depth_mm_hint": 200.0, "confidence": 0.90, "source_bbox": [0.93, 0.63, 0.96, 0.66]},
        {"id": "COL-TERRACE-03", "shape": "rectangular", "width_mm_hint": 200.0, "depth_mm_hint": 200.0, "confidence": 0.90, "source_bbox": [0.93, 0.89, 0.96, 0.92]}
    ],
    "symbols": [
        {"id": "SYM-FIREPLACE", "symbol_type": "fireplace", "description": "Fireplace and flue hearth marked 'kamin ahi'", "is_recognized": True, "confidence": 0.95, "source_bbox": [0.50, 0.68, 0.54, 0.77]},
        {"id": "SYM-KITCHEN-ISLAND", "symbol_type": "counter", "description": "Kitchen island with breakfast bar seating labeled 'Lett'", "is_recognized": True, "confidence": 0.95, "source_bbox": [0.62, 0.47, 0.71, 0.58]},
        {"id": "SYM-COOKTOP", "symbol_type": "cooktop", "description": "4-burner cooking range [88] on L-counter", "is_recognized": True, "confidence": 0.95, "source_bbox": [0.54, 0.48, 0.58, 0.53]},
        {"id": "SYM-SAUNA-HEATER", "symbol_type": "stove", "description": "Sauna heater unit [O] in corner of Saun", "is_recognized": True, "confidence": 0.95, "source_bbox": [0.26, 0.17, 0.29, 0.20]},
        {"id": "SYM-TV-UNIT", "symbol_type": "furniture", "description": "Wall-mounted TV / media unit along East wall", "is_recognized": True, "confidence": 0.90, "source_bbox": [0.55, 0.86, 0.67, 0.89]}
    ],
    "uncertainties": [
        {
            "id": "UNC-01",
            "field": "dimensions.depth_chain_arithmetic",
            "severity": "blocker",
            "description": "Arithmetic discrepancy between West and East depth chains: West side indicates 5000 mm + 14200 mm = 19200 mm total depth to bottom of terrace, while East side indicates 16000 mm (main body) + 3000 mm (terrace) = 19000 mm total depth. Difference is 200 mm (equivalent to one exterior wall thickness).",
            "suggested_action": "Lock main house building depth to 16000 mm and terrace depth to 3000 mm (total 19000 mm). Reconcile West lower terrace dimension to 14000 mm (11000 mm main body + 3000 mm terrace), treating 14200 mm as an exterior-to-exterior face measurement that counted wall thickness.",
            "conflicting_values": ["19200 mm (West side: 5000 + 14200)", "19000 mm (East side: 16000 + 3000)"]
        },
        {
            "id": "UNC-02",
            "field": "walls.interior_thickness",
            "severity": "warning",
            "description": "Interior partition wall thicknesses are not explicitly annotated with numeric millimeter dimensions.",
            "suggested_action": "Apply standard architectural residential defaults: 100 mm for interior non-bearing partitions, 150 mm for plumbing/utility core walls, and 200 mm for exterior perimeter walls.",
            "conflicting_values": ["Not annotated on sketch"]
        },
        {
            "id": "UNC-03",
            "field": "openings.window_widths",
            "severity": "warning",
            "description": "Window symbols are clearly indicated on exterior walls with double lines and sill cutouts, but lack individual numeric width callouts.",
            "suggested_action": "Assign standard modular residential window widths: 600 mm for WC, 900 mm for shower/bath, 1000 mm for laundry, 1200 mm for bedrooms/sauna, 1500 mm for dining/living, and 1800 mm for south living glazing.",
            "conflicting_values": ["Not annotated on sketch"]
        },
        {
            "id": "UNC-04",
            "field": "openings.window_sill_heights",
            "severity": "info",
            "description": "2D floor plan sketch does not indicate vertical window sill heights.",
            "suggested_action": "Assign standard 900 mm sill height fallback; tag as assumed_default_unverified in BIM handoff metadata for downstream 3D review.",
            "conflicting_values": ["Not annotated on sketch"]
        },
        {
            "id": "UNC-05",
            "field": "openings.door_clear_widths",
            "severity": "info",
            "description": "Door swing arcs clearly show opening orientations, but clear door leaf widths are unannotated.",
            "suggested_action": "Assign standard 900 mm for main exterior entrance door, 800 mm for habitable room interior doors, 700 mm for secondary wet/WC/sauna doors, and 1500/2400 mm for terrace patio sliders.",
            "conflicting_values": ["Not annotated on sketch"]
        },
        {
            "id": "UNC-06",
            "field": "geometry.footprint_shape",
            "severity": "warning",
            "description": "Building footprint is stepped L-shaped with an upper-left 5000x5000 mm sauna wing projection rather than a simple rectangle.",
            "suggested_action": "Model exterior perimeter as an orthogonal 6-segment polygon bounding a gross enclosed footprint of 185.0 m2 (25.0 m2 sauna wing + 160.0 m2 main house body).",
            "conflicting_values": ["Rectangular bounding box 15000x16000 mm vs actual stepped footprint"]
        },
        {
            "id": "UNC-07",
            "field": "rooms.terrace_enclosure",
            "severity": "info",
            "description": "South and West terraces are labeled 'Terrass' with open column posts.",
            "suggested_action": "Treat terraces as outdoor covered/semi-covered structures on dedicated architectural layer A-FLOR-OTLN / A-COLS, excluding them from gross internal conditioned floor area.",
            "conflicting_values": ["Outdoor covered terrace vs internal room"]
        }
    ]
}

# Validate observations against Draft-07 schema
is_valid, obs_errors = validate_observations(observations)
if not is_valid:
    raise ValueError(f"Observations schema validation failed: {obs_errors}")
print("Extracted observations validated successfully with 0 errors!")

with open(TEST_DIR / "extracted_observations.json", "w", encoding="utf-8") as f:
    json.dump(observations, f, indent=2)

# 3. Canonical Coordinate Model adhering to floor-plan-model.json
draft_model = {
    "metadata": {
        "projectName": "Real-World Test 01 - Nordic Residential Villa",
        "author": "Antigravity Sketch-to-CAD Agent",
        "version": "1.0.0",
        "createdAt": "2026-11-03T19:00:00Z"
    },
    "status": "awaiting_approval",
    "units": "mm",
    "envelope": {
        "width": 15000.0,
        "depth": 16000.0,
        "origin": [0.0, 0.0],
        "widthSource": "explicit",
        "depthSource": "explicit"
    },
    "walls": [
        # Exterior Walls (200 mm thickness, layer A-WALL-EXTR)
        {"id": "W-EXT-NORTH-1", "type": "exterior", "start": [0.0, 16000.0], "end": [5000.0, 16000.0], "thickness": 200.0, "layer": "A-WALL-EXTR", "source": "explicit"},
        {"id": "W-EXT-NORTH-2", "type": "exterior", "start": [5000.0, 16000.0], "end": [15000.0, 16000.0], "thickness": 200.0, "layer": "A-WALL-EXTR", "source": "explicit"},
        {"id": "W-EXT-EAST", "type": "exterior", "start": [15000.0, 16000.0], "end": [15000.0, 0.0], "thickness": 200.0, "layer": "A-WALL-EXTR", "source": "explicit"},
        {"id": "W-EXT-SOUTH-MAIN", "type": "exterior", "start": [15000.0, 0.0], "end": [5000.0, 0.0], "thickness": 200.0, "layer": "A-WALL-EXTR", "source": "explicit"},
        {"id": "W-EXT-WEST-MAIN", "type": "exterior", "start": [5000.0, 0.0], "end": [5000.0, 11000.0], "thickness": 200.0, "layer": "A-WALL-EXTR", "source": "explicit"},
        {"id": "W-EXT-SOUTH-SAUNA", "type": "exterior", "start": [5000.0, 11000.0], "end": [0.0, 11000.0], "thickness": 200.0, "layer": "A-WALL-EXTR", "source": "explicit"},
        {"id": "W-EXT-WEST-SAUNA", "type": "exterior", "start": [0.0, 11000.0], "end": [0.0, 16000.0], "thickness": 200.0, "layer": "A-WALL-EXTR", "source": "explicit"},

        # Interior Partitions (100 mm thickness, layer A-WALL-INTR)
        {"id": "W-INT-SAUNA-VERT", "type": "interior", "start": [1800.0, 11000.0], "end": [1800.0, 16000.0], "thickness": 100.0, "layer": "A-WALL-INTR", "source": "inferred"},
        {"id": "W-INT-SAUNA-HORIZ", "type": "interior", "start": [0.0, 13500.0], "end": [1800.0, 13500.0], "thickness": 100.0, "layer": "A-WALL-INTR", "source": "inferred"},
        {"id": "W-INT-SAUNA-EAST", "type": "interior", "start": [5000.0, 11000.0], "end": [5000.0, 16000.0], "thickness": 150.0, "layer": "A-WALL-INTR", "source": "inferred"},

        {"id": "W-INT-CORR-NORTH", "type": "interior", "start": [5000.0, 13600.0], "end": [10500.0, 13600.0], "thickness": 100.0, "layer": "A-WALL-INTR", "source": "inferred"},
        {"id": "W-INT-UTIL-1", "type": "interior", "start": [7600.0, 13600.0], "end": [7600.0, 16000.0], "thickness": 100.0, "layer": "A-WALL-INTR", "source": "inferred"},
        {"id": "W-INT-UTIL-2", "type": "interior", "start": [9600.0, 13600.0], "end": [9600.0, 16000.0], "thickness": 100.0, "layer": "A-WALL-INTR", "source": "inferred"},

        {"id": "W-INT-SPINE-EAST", "type": "interior", "start": [10500.0, 6500.0], "end": [10500.0, 16000.0], "thickness": 100.0, "layer": "A-WALL-INTR", "source": "inferred"},
        {"id": "W-INT-BED-1-2", "type": "interior", "start": [10500.0, 13000.0], "end": [15000.0, 13000.0], "thickness": 100.0, "layer": "A-WALL-INTR", "source": "inferred"},
        {"id": "W-INT-BED-2-ESIK", "type": "interior", "start": [10500.0, 9800.0], "end": [15000.0, 9800.0], "thickness": 100.0, "layer": "A-WALL-INTR", "source": "inferred"},
        {"id": "W-INT-ESIK-SOUTH", "type": "interior", "start": [10500.0, 6500.0], "end": [15000.0, 6500.0], "thickness": 100.0, "layer": "A-WALL-INTR", "source": "inferred"},

        {"id": "W-INT-CORR-WEST", "type": "interior", "start": [9000.0, 6500.0], "end": [9000.0, 13600.0], "thickness": 100.0, "layer": "A-WALL-INTR", "source": "inferred"},
        {"id": "W-INT-MASTER-BATH", "type": "interior", "start": [5000.0, 9200.0], "end": [9000.0, 9200.0], "thickness": 100.0, "layer": "A-WALL-INTR", "source": "inferred"},
        {"id": "W-INT-BATH-LIVING", "type": "interior", "start": [5000.0, 6500.0], "end": [9000.0, 6500.0], "thickness": 100.0, "layer": "A-WALL-INTR", "source": "inferred"}
    ],
    "openings": [
        # Exterior Doors
        {"id": "D-ENTRY", "type": "door", "wallId": "W-EXT-EAST", "center": [15000.0, 8200.0], "width": 900.0, "swing": "outward-right", "layer": "A-DOOR", "source": "explicit"},
        {"id": "D-SAUNA-TERRACE", "type": "door", "wallId": "W-EXT-SOUTH-SAUNA", "center": [3500.0, 11000.0], "width": 1500.0, "swing": "sliding", "layer": "A-DOOR", "source": "explicit"},
        {"id": "D-LIVING-TERRACE", "type": "door", "wallId": "W-EXT-SOUTH-MAIN", "center": [11500.0, 0.0], "width": 2400.0, "swing": "sliding", "layer": "A-DOOR", "source": "explicit"},

        # Interior Doors
        {"id": "D-ESIK-LIVING", "type": "door", "wallId": "W-INT-ESIK-SOUTH", "center": [11500.0, 6500.0], "width": 1200.0, "swing": "none", "layer": "A-DOOR", "source": "inferred"},
        {"id": "D-BED-1", "type": "door", "wallId": "W-INT-SPINE-EAST", "center": [10500.0, 13800.0], "width": 800.0, "swing": "inward-right", "layer": "A-DOOR", "source": "inferred"},
        {"id": "D-BED-2", "type": "door", "wallId": "W-INT-SPINE-EAST", "center": [10500.0, 10500.0], "width": 800.0, "swing": "inward-right", "layer": "A-DOOR", "source": "inferred"},
        {"id": "D-WC", "type": "door", "wallId": "W-INT-CORR-NORTH", "center": [10000.0, 13600.0], "width": 700.0, "swing": "inward-left", "layer": "A-DOOR", "source": "inferred"},
        {"id": "D-TEH", "type": "door", "wallId": "W-INT-CORR-NORTH", "center": [8600.0, 13600.0], "width": 800.0, "swing": "outward-left", "layer": "A-DOOR", "source": "inferred"},
        {"id": "D-MAJAPIDAMIS", "type": "door", "wallId": "W-INT-CORR-NORTH", "center": [6300.0, 13600.0], "width": 800.0, "swing": "outward-left", "layer": "A-DOOR", "source": "inferred"},
        {"id": "D-SAUNA-HALL", "type": "door", "wallId": "W-INT-SAUNA-EAST", "center": [5000.0, 13800.0], "width": 800.0, "swing": "inward-left", "layer": "A-DOOR", "source": "inferred"},
        {"id": "D-MASTER-BED", "type": "door", "wallId": "W-INT-CORR-WEST", "center": [9000.0, 10000.0], "width": 800.0, "swing": "inward-left", "layer": "A-DOOR", "source": "inferred"},
        {"id": "D-BATHROOM", "type": "door", "wallId": "W-INT-CORR-WEST", "center": [9000.0, 8500.0], "width": 800.0, "swing": "inward-left", "layer": "A-DOOR", "source": "inferred"},
        {"id": "D-DUSS", "type": "door", "wallId": "W-INT-SAUNA-VERT", "center": [1800.0, 14500.0], "width": 700.0, "swing": "inward-left", "layer": "A-DOOR", "source": "inferred"},
        {"id": "D-SAUN", "type": "door", "wallId": "W-INT-SAUNA-HORIZ", "center": [900.0, 13500.0], "width": 700.0, "swing": "outward-right", "layer": "A-DOOR", "source": "inferred"},

        # Windows (layer A-GLAZ)
        {"id": "W-DUSS", "type": "window", "wallId": "W-EXT-NORTH-1", "center": [900.0, 16000.0], "width": 900.0, "layer": "A-GLAZ", "source": "estimated"},
        {"id": "W-SAUNA-PUHKE", "type": "window", "wallId": "W-EXT-NORTH-1", "center": [3400.0, 16000.0], "width": 1200.0, "layer": "A-GLAZ", "source": "estimated"},
        {"id": "W-MAJAPIDAMIS", "type": "window", "wallId": "W-EXT-NORTH-2", "center": [6300.0, 16000.0], "width": 1000.0, "layer": "A-GLAZ", "source": "estimated"},
        {"id": "W-WC", "type": "window", "wallId": "W-EXT-NORTH-2", "center": [10000.0, 16000.0], "width": 600.0, "layer": "A-GLAZ", "source": "estimated"},
        {"id": "W-BED-1", "type": "window", "wallId": "W-EXT-NORTH-2", "center": [12800.0, 16000.0], "width": 1200.0, "layer": "A-GLAZ", "source": "estimated"},
        {"id": "W-BED-2", "type": "window", "wallId": "W-EXT-EAST", "center": [15000.0, 11400.0], "width": 1200.0, "layer": "A-GLAZ", "source": "estimated"},
        {"id": "W-MASTER-BED", "type": "window", "wallId": "W-EXT-WEST-MAIN", "center": [5000.0, 11400.0], "width": 1200.0, "layer": "A-GLAZ", "source": "estimated"},
        {"id": "W-BATHROOM", "type": "window", "wallId": "W-EXT-WEST-MAIN", "center": [5000.0, 7800.0], "width": 900.0, "layer": "A-GLAZ", "source": "estimated"},
        {"id": "W-LIVING-WEST", "type": "window", "wallId": "W-EXT-WEST-MAIN", "center": [5000.0, 3200.0], "width": 1500.0, "layer": "A-GLAZ", "source": "estimated"},
        {"id": "W-LIVING-EAST", "type": "window", "wallId": "W-EXT-EAST", "center": [15000.0, 3200.0], "width": 1500.0, "layer": "A-GLAZ", "source": "estimated"},
        {"id": "W-LIVING-SOUTH", "type": "window", "wallId": "W-EXT-SOUTH-MAIN", "center": [8000.0, 0.0], "width": 1800.0, "layer": "A-GLAZ", "source": "estimated"}
    ],
    "rooms": [
        {"id": "R-DUSS", "name": "Shower", "label": "Dušš", "labelPosition": [900.0, 14750.0], "approximateArea": 4.5},
        {"id": "R-SAUN", "name": "Sauna", "label": "Saun", "labelPosition": [900.0, 12250.0], "approximateArea": 4.0},
        {"id": "R-SAUNA-PUHKE", "name": "Sauna Lounge", "label": "Sauna Puhkeruum", "labelPosition": [3400.0, 13500.0], "approximateArea": 15.0},
        {"id": "R-MAJAPIDAMIS", "name": "Utility Room", "label": "MAJAPIDAMIS", "labelPosition": [6300.0, 14800.0], "approximateArea": 5.5},
        {"id": "R-TEH", "name": "Technical Room", "label": "TEH", "labelPosition": [8600.0, 14800.0], "approximateArea": 4.8},
        {"id": "R-WC", "name": "Guest Toilet", "label": "WC", "labelPosition": [10050.0, 14800.0], "approximateArea": 2.2},
        {"id": "R-BED-1", "name": "Bedroom 1", "label": "Magamistuba 1", "labelPosition": [12750.0, 14500.0], "approximateArea": 12.0},
        {"id": "R-BED-2", "name": "Bedroom 2", "label": "Magamistuba 2", "labelPosition": [12750.0, 11400.0], "approximateArea": 12.0},
        {"id": "R-ESIK", "name": "Entry Vestibule", "label": "Esik", "labelPosition": [12750.0, 8150.0], "approximateArea": 12.8},
        {"id": "R-MASTER-BED", "name": "Master Bedroom", "label": "Magamistuba (Suur)", "labelPosition": [7000.0, 11400.0], "approximateArea": 17.6},
        {"id": "R-BATHROOM", "name": "Main Bathroom", "label": "Vannituba", "labelPosition": [7000.0, 7850.0], "approximateArea": 6.5},
        {"id": "R-LIVING-KITCHEN", "name": "Living Room & Kitchen", "label": "Elutuba köök", "labelPosition": [10000.0, 3250.0], "approximateArea": 65.0},
        {"id": "R-CORRIDOR", "name": "Circulation Corridor", "label": "Koridor", "labelPosition": [9750.0, 10000.0], "approximateArea": 10.5}
    ],
    "elements": [
        # Architectural Furniture & Blocks (category: furniture / sanitary / structural)
        {"id": "E-BED-01", "blockId": "bed_double", "category": "furniture", "position": [12750.0, 14800.0], "source": "explicit"},
        {"id": "E-BED-02", "blockId": "bed_double", "category": "furniture", "position": [12750.0, 11700.0], "source": "explicit"},
        {"id": "E-BED-MASTER", "blockId": "bed_double", "category": "furniture", "position": [7000.0, 12000.0], "source": "explicit"},
        {"id": "E-DINING-TABLE", "blockId": "table_dining_6p", "category": "furniture", "position": [7000.0, 1500.0], "source": "explicit"},
        {"id": "E-LIVING-SOFA", "blockId": "sofa_sectional_l", "category": "furniture", "position": [11500.0, 2500.0], "source": "explicit"},
        {"id": "E-FIREPLACE", "blockId": "fireplace_corner", "category": "furniture", "position": [11000.0, 5800.0], "source": "explicit"},
        {"id": "E-WC-FIXTURE", "blockId": "wc_standard", "category": "sanitary", "position": [10050.0, 15400.0], "source": "explicit"},
        {"id": "E-BATH-FIXTURE", "blockId": "bathtub_standard", "category": "sanitary", "position": [6200.0, 8500.0], "source": "explicit"},
        {"id": "E-COL-TERRACE-1", "blockId": "column_concrete_square", "category": "structural", "position": [5100.0, -2900.0], "source": "explicit"},
        {"id": "E-COL-TERRACE-2", "blockId": "column_concrete_square", "category": "structural", "position": [10000.0, -2900.0], "source": "explicit"},
        {"id": "E-COL-TERRACE-3", "blockId": "column_concrete_square", "category": "structural", "position": [14900.0, -2900.0], "source": "explicit"}
    ],
    "dimensions": [
        {"id": "DIM-EXT-TOP-1", "p1": [0.0, 16000.0], "p2": [5000.0, 16000.0], "at": [2500.0, 17000.0], "source": "explicit"},
        {"id": "DIM-EXT-TOP-2", "p1": [5000.0, 16000.0], "p2": [15000.0, 16000.0], "at": [10000.0, 17000.0], "source": "explicit"},
        {"id": "DIM-EXT-EAST", "p1": [15000.0, 16000.0], "p2": [15000.0, 0.0], "at": [16000.0, 8000.0], "source": "explicit"},
        {"id": "DIM-EXT-TERRACE-S", "p1": [15000.0, 0.0], "p2": [15000.0, -3000.0], "at": [16000.0, -1500.0], "source": "explicit"},
        {"id": "DIM-EXT-SAUNA-W", "p1": [0.0, 16000.0], "p2": [0.0, 11000.0], "at": [-1000.0, 13500.0], "source": "explicit"},
        {"id": "DIM-EXT-MAIN-S", "p1": [5000.0, 0.0], "p2": [15000.0, 0.0], "at": [10000.0, -1000.0], "source": "explicit"}
    ],
    "uncertainties": [
        {
            "id": "UNC-01",
            "target": "dimensions.depth_chain",
            "description": "Arithmetic conflict between West dimension chain (5000 + 14200 = 19200 mm) and East dimension chain (16000 + 3000 = 19000 mm). Reconciled building depth to 16000 mm with 3000 mm terrace.",
            "assumedValue": "16000 mm building depth + 3000 mm terrace depth",
            "confidence": "high",
            "status": "unresolved"
        },
        {
            "id": "UNC-02",
            "target": "walls.interior_thickness",
            "description": "Interior partition thicknesses unannotated; assumed standard 100 mm partitions.",
            "assumedValue": "100 mm",
            "confidence": "medium",
            "status": "unresolved"
        },
        {
            "id": "UNC-03",
            "target": "openings.window_widths",
            "description": "Window widths estimated based on standard modular dimensions.",
            "assumedValue": "600-1800 mm",
            "confidence": "medium",
            "status": "unresolved"
        },
        {
            "id": "UNC-04",
            "target": "openings.sill_heights",
            "description": "Window sill heights unannotated; assumed standard 900 mm fallback.",
            "assumedValue": "900 mm",
            "confidence": "low",
            "status": "unresolved"
        },
        {
            "id": "UNC-05",
            "target": "openings.door_clearances",
            "description": "Door clear opening widths inferred from standard residential practice.",
            "assumedValue": "700-900 mm",
            "confidence": "medium",
            "status": "unresolved"
        }
    ]
}

# Validate draft model against floor-plan-model.json schema
with open(REPO_ROOT / "skills" / "sketch-to-cad" / "schemas" / "floor-plan-model.json", "r", encoding="utf-8") as f:
    model_schema = json.load(f)
validate(instance=draft_model, schema=model_schema)
print("Draft coordinate model validated successfully against floor-plan-model.json!")

with open(TEST_DIR / "draft_model.json", "w", encoding="utf-8") as f:
    json.dump(draft_model, f, indent=2)

# 4. Create Structured Approval Package
approval_package = create_approval_package(
    draft_model=draft_model,
    observations=observations,
    project_name="Real-World Test 01 - Nordic Residential Villa"
)

# Validate approval package against approval-package.schema.json
with open(REPO_ROOT / "skills" / "sketch-to-cad" / "schemas" / "approval-package.schema.json", "r", encoding="utf-8") as f:
    app_schema = json.load(f)
validate(instance=approval_package, schema=app_schema)
print("Approval package validated successfully against approval-package.schema.json!")

with open(TEST_DIR / "approval_package.json", "w", encoding="utf-8") as f:
    json.dump(approval_package, f, indent=2)

# 5. Generate Markdown Proposal with Uncertainty Register
proposal_md = generate_proposal_markdown(approval_package)
with open(TEST_DIR / "proposal.md", "w", encoding="utf-8") as f:
    f.write(proposal_md)

# 6. Standalone Uncertainty Register
uncertainty_reg = {
    "project": "Real-World Test 01 - Nordic Residential Villa",
    "source_file": "source_sketch.jpg",
    "source_sha256": "12ca802a25cd855467a62473c7c35f423ca01ed53ab3818b61b7b75cf9259957",
    "total_uncertainties": len(observations["uncertainties"]),
    "blocking_count": sum(1 for u in observations["uncertainties"] if u["severity"] == "blocker"),
    "warning_count": sum(1 for u in observations["uncertainties"] if u["severity"] == "warning"),
    "info_count": sum(1 for u in observations["uncertainties"] if u["severity"] == "info"),
    "uncertainties": observations["uncertainties"]
}

with open(TEST_DIR / "uncertainty_register.json", "w", encoding="utf-8") as f:
    json.dump(uncertainty_reg, f, indent=2)

# 7. Execution and Provenance Log
exec_log = {
    "test_id": "TEST-01",
    "timestamp": "2026-11-03T19:05:00Z",
    "status": "AWAITING_HUMAN_APPROVAL",
    "source_image": {
        "file_name": "source_sketch.jpg",
        "sha256": "12ca802a25cd855467a62473c7c35f423ca01ed53ab3818b61b7b75cf9259957",
        "dimensions": "845x1024 px",
        "provenance": "user_uploaded_media_1793712592081_320ca563.jpg"
    },
    "interpretation": {
        "provider": "agent_native_multimodal",
        "model": "antigravity-native-vision-v1",
        "schema_validation": "PASSED (0 errors)",
        "walls_extracted": len(observations["walls"]),
        "openings_extracted": len(observations["openings"]),
        "rooms_extracted": len(observations["rooms"]),
        "dimensions_extracted": len(observations["dimensions"]),
        "uncertainties_logged": len(observations["uncertainties"]),
        "columns_extracted": len(observations["columns"]),
        "symbols_extracted": len(observations["symbols"])
    },
    "governance": {
        "approval_gate": "ENFORCED",
        "revision_hash": approval_package["revision_hash"],
        "approval_status": "awaiting_approval",
        "cad_generation_blocked": True,
        "message": "Interpretation completed and structured approval package compiled. Stopped before CAD drafting in accordance with mandatory Human Approval Gate."
    }
}

with open(TEST_DIR / "execution_log.json", "w", encoding="utf-8") as f:
    json.dump(exec_log, f, indent=2)

print("All intermediate deliverables for Test-01 generated successfully in tests/real_world/Test-01/!")
