"""
Generate synthetic architectural sketch test fixtures for Milestone 7.
Creates Fixtures A, B, C, D (multi-page PDF), and E (angled wall), plus observation JSON files.
"""

from __future__ import annotations

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import fitz

OUT_DIR = Path("tests/fixtures/sketches")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def draw_sketch_base(w=1200, h=900):
    img = Image.new("RGB", (w, h), color=(250, 249, 246))
    draw = ImageDraw.Draw(img)
    return img, draw


# ==========================================
# Fixture A: Clean Hand-drawn Single Floor
# ==========================================
def generate_fixture_a():
    img, draw = draw_sketch_base(1200, 900)
    # Exterior boundary: x: 200..1000, y: 200..700 (aspect 800:500 = 6000:5000 approx)
    draw.rectangle([200, 200, 1000, 700], outline=(30, 40, 60), width=6)
    # Interior partition: y=450, x: 200..1000
    draw.line([200, 450, 1000, 450], fill=(50, 60, 80), width=4)
    # Interior partition: x=650, y: 450..700
    draw.line([650, 450, 650, 700], fill=(50, 60, 80), width=4)

    # Texts
    draw.text((450, 310), "LIVING / DINING ROOM", fill=(20, 20, 20))
    draw.text((320, 560), "BEDROOM 1", fill=(20, 20, 20))
    draw.text((780, 560), "BATHROOM", fill=(20, 20, 20))

    # Dimensions
    draw.text((560, 150), "6000 mm", fill=(180, 20, 80))
    draw.text((120, 430), "5000 mm", fill=(180, 20, 80))
    draw.text((400, 720), "3600", fill=(180, 20, 80))
    draw.text((800, 720), "2400", fill=(180, 20, 80))

    # Openings
    draw.line([550, 200, 650, 200], fill=(250, 249, 246), width=8)  # Door opening
    draw.arc([550, 150, 650, 250], 0, 90, fill=(100, 150, 50), width=2)
    draw.text((570, 215), "D-01 (900)", fill=(100, 150, 50))

    path = OUT_DIR / "fixture-a-clean-single-floor.png"
    img.save(path)
    print(f"Generated {path}")

    # Observations JSON
    obs = {
        "source_metadata": {
            "source_file": "fixture-a-clean-single-floor.png",
            "file_type": "png",
            "page_number": 1,
            "total_pages": 1,
            "dimensions_pixels": {"width": 1200, "height": 900},
            "dpi": 72.0,
            "orientation_degrees": 0,
            "source_floor_hint": "Ground Floor",
            "preprocessing_applied": ["Deterministic RGB normalization"],
        },
        "status": "extracted",
        "confidence_summary": {
            "overall_confidence": 0.95,
            "dimension_reliability": "high",
            "notes": "Clean orthogonal hand sketch with complete explicit dimensioning",
        },
        "walls": [
            {
                "id": "W-EXT-NORTH",
                "wall_type": "exterior",
                "start_point_pixel": [200, 200],
                "end_point_pixel": [1000, 200],
                "thickness_mm": 200.0,
                "thickness_category": "explicit",
                "confidence": 0.98,
                "provenance": "source_sketch",
                "source_bbox": [0.22, 0.16, 0.23, 0.84],
            },
            {
                "id": "W-EXT-EAST",
                "wall_type": "exterior",
                "start_point_pixel": [1000, 200],
                "end_point_pixel": [1000, 700],
                "thickness_mm": 200.0,
                "thickness_category": "explicit",
                "confidence": 0.98,
                "provenance": "source_sketch",
                "source_bbox": [0.22, 0.83, 0.78, 0.84],
            },
            {
                "id": "W-EXT-SOUTH",
                "wall_type": "exterior",
                "start_point_pixel": [1000, 700],
                "end_point_pixel": [200, 700],
                "thickness_mm": 200.0,
                "thickness_category": "explicit",
                "confidence": 0.98,
                "provenance": "source_sketch",
                "source_bbox": [0.77, 0.16, 0.78, 0.84],
            },
            {
                "id": "W-EXT-WEST",
                "wall_type": "exterior",
                "start_point_pixel": [200, 700],
                "end_point_pixel": [200, 200],
                "thickness_mm": 200.0,
                "thickness_category": "explicit",
                "confidence": 0.98,
                "provenance": "source_sketch",
                "source_bbox": [0.22, 0.16, 0.78, 0.17],
            },
            {
                "id": "W-INTR-H",
                "wall_type": "interior",
                "start_point_pixel": [200, 450],
                "end_point_pixel": [1000, 450],
                "thickness_mm": 150.0,
                "thickness_category": "explicit",
                "confidence": 0.95,
                "provenance": "source_sketch",
                "source_bbox": [0.50, 0.16, 0.51, 0.84],
            },
            {
                "id": "W-INTR-V",
                "wall_type": "interior",
                "start_point_pixel": [650, 450],
                "end_point_pixel": [650, 700],
                "thickness_mm": 150.0,
                "thickness_category": "explicit",
                "confidence": 0.95,
                "provenance": "source_sketch",
                "source_bbox": [0.50, 0.54, 0.78, 0.55],
            },
        ],
        "openings": [
            {
                "id": "D-01",
                "type": "door",
                "swing_direction": "inward_right",
                "width_mm": 900.0,
                "width_category": "explicit",
                "host_wall_ref": "W-EXT-NORTH",
                "confidence": 0.96,
                "provenance": "source_sketch",
                "source_bbox": [0.21, 0.45, 0.24, 0.55],
            },
            {
                "id": "W-01",
                "type": "window",
                "swing_direction": None,
                "width_mm": 1200.0,
                "width_category": "explicit",
                "host_wall_ref": "W-EXT-WEST",
                "confidence": 0.94,
                "provenance": "source_sketch",
                "source_bbox": [0.35, 0.15, 0.45, 0.18],
            },
        ],
        "rooms": [
            {
                "id": "R-01",
                "raw_label": "LIVING / DINING ROOM",
                "standardized_type": "LIVING",
                "floor_level": "ground",
                "approx_width_mm": 6000.0,
                "approx_depth_mm": 2800.0,
                "dimension_provenance": "explicit",
                "confidence": 0.96,
                "source_bbox": [0.25, 0.2, 0.48, 0.8],
            },
            {
                "id": "R-02",
                "raw_label": "BEDROOM 1",
                "standardized_type": "BEDROOM",
                "floor_level": "ground",
                "approx_width_mm": 3600.0,
                "approx_depth_mm": 2200.0,
                "dimension_provenance": "explicit",
                "confidence": 0.95,
                "source_bbox": [0.52, 0.2, 0.75, 0.52],
            },
            {
                "id": "R-03",
                "raw_label": "BATHROOM",
                "standardized_type": "BATHROOM",
                "floor_level": "ground",
                "approx_width_mm": 2400.0,
                "approx_depth_mm": 2200.0,
                "dimension_provenance": "explicit",
                "confidence": 0.95,
                "source_bbox": [0.52, 0.56, 0.75, 0.8],
            },
        ],
        "dimensions": [
            {
                "id": "DIM-1",
                "source_text": "6000 mm",
                "value_mm": 6000.0,
                "category": "explicit",
                "target_entity_type": "overall_width",
                "confidence": 0.98,
                "source_bbox": [0.15, 0.45, 0.18, 0.55],
            },
            {
                "id": "DIM-2",
                "source_text": "5000 mm",
                "value_mm": 5000.0,
                "category": "explicit",
                "target_entity_type": "overall_depth",
                "confidence": 0.98,
                "source_bbox": [0.45, 0.08, 0.55, 0.15],
            },
            {
                "id": "DIM-3",
                "source_text": "3600",
                "value_mm": 3600.0,
                "category": "explicit",
                "target_entity_type": "room_width",
                "confidence": 0.95,
                "source_bbox": [0.78, 0.3, 0.82, 0.45],
            },
            {
                "id": "DIM-4",
                "source_text": "2400",
                "value_mm": 2400.0,
                "category": "explicit",
                "target_entity_type": "room_width",
                "confidence": 0.95,
                "source_bbox": [0.78, 0.65, 0.82, 0.75],
            },
        ],
        "uncertainties": [],
    }
    with open(OUT_DIR / "fixture-a-observations.json", "w", encoding="utf-8") as f:
        json.dump(obs, f, indent=2)


# ==========================================
# Fixture B: Incomplete Sketch (Missing Dims)
# ==========================================
def generate_fixture_b():
    img, draw = draw_sketch_base(1000, 800)
    # Rough walls
    draw.rectangle([150, 150, 850, 650], outline=(60, 60, 60), width=5)
    draw.line([150, 400, 850, 400], fill=(60, 60, 60), width=3)
    # Only width given, depth missing! Wall thickness not annotated!
    draw.text((450, 100), "7000 mm", fill=(180, 20, 20))
    draw.text((400, 260), "STUDIO LIVING", fill=(40, 40, 40))
    draw.text((400, 500), "UTILITY / STORAGE", fill=(40, 40, 40))
    # Ambiguous opening tick
    draw.line([850, 250, 850, 320], fill=(250, 249, 246), width=6)
    draw.text((865, 275), "?", fill=(200, 0, 0))

    path = OUT_DIR / "fixture-b-incomplete.png"
    img.save(path)
    print(f"Generated {path}")

    obs = {
        "source_metadata": {
            "source_file": "fixture-b-incomplete.png",
            "file_type": "png",
            "page_number": 1,
            "total_pages": 1,
            "dimensions_pixels": {"width": 1000, "height": 800},
            "dpi": 72.0,
            "orientation_degrees": 0,
            "source_floor_hint": "Ground Floor",
            "preprocessing_applied": ["Deterministic RGB normalization"],
        },
        "status": "extracted",
        "confidence_summary": {
            "overall_confidence": 0.72,
            "dimension_reliability": "medium",
            "notes": "Incomplete sketch: overall depth missing and wall thicknesses unannotated",
        },
        "walls": [
            {
                "id": "W-EXT-NORTH",
                "wall_type": "exterior",
                "start_point_pixel": [150, 150],
                "end_point_pixel": [850, 150],
                "thickness_mm": None,
                "thickness_category": "unknown",
                "confidence": 0.85,
                "provenance": "source_sketch",
                "source_bbox": [0.18, 0.15, 0.20, 0.85],
            },
            {
                "id": "W-EXT-SOUTH",
                "wall_type": "exterior",
                "start_point_pixel": [150, 650],
                "end_point_pixel": [850, 650],
                "thickness_mm": None,
                "thickness_category": "unknown",
                "confidence": 0.85,
                "provenance": "source_sketch",
                "source_bbox": [0.80, 0.15, 0.82, 0.85],
            },
        ],
        "openings": [
            {
                "id": "OP-AMBIGUOUS-01",
                "type": "opening",
                "swing_direction": "unknown",
                "width_mm": None,
                "width_category": "unknown",
                "host_wall_ref": None,
                "confidence": 0.60,
                "provenance": "source_sketch",
                "source_bbox": [0.31, 0.84, 0.40, 0.86],
            }
        ],
        "rooms": [
            {
                "id": "R-01",
                "raw_label": "STUDIO LIVING",
                "standardized_type": "LIVING",
                "floor_level": "ground",
                "approx_width_mm": 7000.0,
                "approx_depth_mm": None,
                "dimension_provenance": "inferred",
                "confidence": 0.80,
                "source_bbox": [0.20, 0.20, 0.50, 0.80],
            }
        ],
        "dimensions": [
            {
                "id": "DIM-1",
                "source_text": "7000 mm",
                "value_mm": 7000.0,
                "category": "explicit",
                "target_entity_type": "overall_width",
                "confidence": 0.95,
                "source_bbox": [0.10, 0.40, 0.15, 0.60],
            }
        ],
        "uncertainties": [
            {
                "id": "unc-missing-depth",
                "field": "envelope.depth",
                "severity": "blocker",
                "description": "Overall building depth is not annotated on sketch.",
                "suggested_action": "Request human confirmation for building depth.",
            },
            {
                "id": "unc-wall-thickness",
                "field": "walls.thickness",
                "severity": "info",
                "description": "Wall thickness unannotated; standard 200mm exterior proposed.",
                "suggested_action": "Confirm proposed 200mm exterior wall thickness.",
            },
        ],
    }
    with open(OUT_DIR / "fixture-b-observations.json", "w", encoding="utf-8") as f:
        json.dump(obs, f, indent=2)


# ==========================================
# Fixture C: Contradictory Sketch (Arithmetic Mismatch)
# ==========================================
def generate_fixture_c():
    img, draw = draw_sketch_base(1200, 900)
    draw.rectangle([200, 200, 1000, 700], outline=(30, 30, 30), width=6)
    draw.line([600, 200, 600, 700], fill=(50, 50, 50), width=4)

    # Contradictory dimensions: Envelope 8000 vs Rooms 4500 + 4600 = 9100!
    draw.text((540, 140), "8000 mm (OVERALL)", fill=(200, 20, 20))
    draw.text((350, 720), "ROOM A: 4500 mm", fill=(200, 20, 20))
    draw.text((750, 720), "ROOM B: 4600 mm", fill=(200, 20, 20))
    draw.text((100, 440), "6000 mm", fill=(20, 20, 150))

    path = OUT_DIR / "fixture-c-contradictory.png"
    img.save(path)
    print(f"Generated {path}")

    obs = {
        "source_metadata": {
            "source_file": "fixture-c-contradictory.png",
            "file_type": "png",
            "page_number": 1,
            "total_pages": 1,
            "dimensions_pixels": {"width": 1200, "height": 900},
            "dpi": 72.0,
            "orientation_degrees": 0,
            "source_floor_hint": "Ground Floor",
            "preprocessing_applied": ["Deterministic RGB normalization"],
        },
        "status": "extracted",
        "confidence_summary": {
            "overall_confidence": 0.65,
            "dimension_reliability": "critical_conflicts",
            "notes": "Severe arithmetic contradiction: room chain (9100mm) exceeds overall footprint (8000mm)",
        },
        "walls": [
            {
                "id": "W-EXT-NORTH",
                "wall_type": "exterior",
                "start_point_pixel": [200, 200],
                "end_point_pixel": [1000, 200],
                "thickness_mm": 200.0,
                "thickness_category": "explicit",
                "confidence": 0.95,
                "provenance": "source_sketch",
                "source_bbox": [0.22, 0.16, 0.23, 0.84],
            },
            {
                "id": "W-EXT-SOUTH",
                "wall_type": "exterior",
                "start_point_pixel": [1000, 700],
                "end_point_pixel": [200, 700],
                "thickness_mm": 200.0,
                "thickness_category": "explicit",
                "confidence": 0.95,
                "provenance": "source_sketch",
                "source_bbox": [0.77, 0.16, 0.78, 0.84],
            },
        ],
        "openings": [],
        "rooms": [
            {
                "id": "R-A",
                "raw_label": "ROOM A",
                "standardized_type": "ROOM",
                "floor_level": "ground",
                "approx_width_mm": 4500.0,
                "approx_depth_mm": 6000.0,
                "dimension_provenance": "explicit",
                "confidence": 0.90,
                "source_bbox": [0.25, 0.2, 0.75, 0.5],
            },
            {
                "id": "R-B",
                "raw_label": "ROOM B",
                "standardized_type": "ROOM",
                "floor_level": "ground",
                "approx_width_mm": 4600.0,
                "approx_depth_mm": 6000.0,
                "dimension_provenance": "explicit",
                "confidence": 0.90,
                "source_bbox": [0.25, 0.5, 0.75, 0.8],
            },
        ],
        "dimensions": [
            {
                "id": "DIM-OVERALL-W",
                "source_text": "8000 mm",
                "value_mm": 8000.0,
                "category": "explicit",
                "target_entity_type": "overall_width",
                "confidence": 0.95,
                "source_bbox": [0.15, 0.45, 0.18, 0.55],
            },
            {
                "id": "DIM-OVERALL-D",
                "source_text": "6000 mm",
                "value_mm": 6000.0,
                "category": "explicit",
                "target_entity_type": "overall_depth",
                "confidence": 0.95,
                "source_bbox": [0.45, 0.08, 0.55, 0.15],
            },
            {
                "id": "DIM-ROOM-A-W",
                "source_text": "4500 mm",
                "value_mm": 4500.0,
                "category": "explicit",
                "target_entity_type": "room_width",
                "confidence": 0.95,
                "source_bbox": [0.78, 0.25, 0.82, 0.45],
            },
            {
                "id": "DIM-ROOM-B-W",
                "source_text": "4600 mm",
                "value_mm": 4600.0,
                "category": "explicit",
                "target_entity_type": "room_width",
                "confidence": 0.95,
                "source_bbox": [0.78, 0.55, 0.82, 0.75],
            },
        ],
        "uncertainties": [
            {
                "id": "unc-contradiction-width",
                "field": "envelope.width",
                "severity": "blocker",
                "description": "Contradictory width: Room chain sum (4500 + 4600 = 9100mm) exceeds overall width (8000mm).",
                "suggested_action": "User must clarify whether 8000mm envelope or 9100mm interior sum is correct.",
            }
        ],
    }
    with open(OUT_DIR / "fixture-c-observations.json", "w", encoding="utf-8") as f:
        json.dump(obs, f, indent=2)


# ==========================================
# Fixture D: Multi-Page Two-Storey PDF
# ==========================================
def generate_fixture_d():
    doc = fitz.open()

    # Page 1: Ground Floor
    p1 = doc.new_page(width=842, height=595)
    p1.draw_rect(fitz.Rect(100, 100, 700, 480), color=(0.1, 0.2, 0.4), width=3)
    p1.draw_line(fitz.Point(400, 100), fitz.Point(400, 480), color=(0.1, 0.2, 0.4), width=2)
    # Staircase Ground Floor
    p1.draw_rect(fitz.Rect(420, 120, 550, 240), color=(0.6, 0.3, 0.1), width=1.5)
    for y in range(135, 240, 15):
        p1.draw_line(fitz.Point(420, y), fitz.Point(550, y), color=(0.6, 0.3, 0.1), width=0.8)
    p1.insert_text(fitz.Point(120, 60), "GROUND FLOOR PLAN (LEVEL 01)", fontsize=14, fontname="helv", color=(0, 0, 0))
    p1.insert_text(fitz.Point(180, 280), "LIVING ROOM (6000 x 4000)", fontsize=11, fontname="helv", color=(0.2, 0.2, 0.2))
    p1.insert_text(fitz.Point(440, 180), "STAIRS UP", fontsize=10, fontname="helv", color=(0.6, 0.3, 0.1))
    p1.insert_text(fitz.Point(450, 350), "KITCHEN / DINING", fontsize=11, fontname="helv", color=(0.2, 0.2, 0.2))
    p1.insert_text(fitz.Point(360, 520), "8000 mm (WIDTH)", fontsize=10, fontname="helv", color=(0.8, 0, 0))

    # Page 2: First Floor
    p2 = doc.new_page(width=842, height=595)
    p2.draw_rect(fitz.Rect(100, 100, 700, 480), color=(0.1, 0.2, 0.4), width=3)
    p2.draw_line(fitz.Point(400, 100), fitz.Point(400, 480), color=(0.1, 0.2, 0.4), width=2)
    # Staircase First Floor (aligned)
    p2.draw_rect(fitz.Rect(420, 120, 550, 240), color=(0.6, 0.3, 0.1), width=1.5)
    for y in range(135, 240, 15):
        p2.draw_line(fitz.Point(420, y), fitz.Point(550, y), color=(0.6, 0.3, 0.1), width=0.8)
    p2.insert_text(fitz.Point(120, 60), "FIRST FLOOR PLAN (LEVEL 02)", fontsize=14, fontname="helv", color=(0, 0, 0))
    p2.insert_text(fitz.Point(180, 280), "MASTER BEDROOM", fontsize=11, fontname="helv", color=(0.2, 0.2, 0.2))
    p2.insert_text(fitz.Point(440, 180), "STAIRS DOWN", fontsize=10, fontname="helv", color=(0.6, 0.3, 0.1))
    p2.insert_text(fitz.Point(450, 350), "BEDROOM 2", fontsize=11, fontname="helv", color=(0.2, 0.2, 0.2))
    p2.insert_text(fitz.Point(360, 520), "8000 mm (WIDTH)", fontsize=10, fontname="helv", color=(0.8, 0, 0))

    pdf_path = OUT_DIR / "fixture-d-two-storey.pdf"
    doc.save(str(pdf_path))
    doc.close()
    print(f"Generated {pdf_path}")

    obs = {
        "source_metadata": {
            "source_file": "fixture-d-two-storey.pdf",
            "file_type": "pdf",
            "page_number": 1,
            "total_pages": 2,
            "dimensions_pixels": {"width": 1754, "height": 1240},
            "dpi": 150.0,
            "orientation_degrees": 0,
            "source_floor_hint": "Ground Floor & First Floor Multi-page Set",
            "preprocessing_applied": ["Rendered PDF page 1 at 150.0 DPI", "Extracted 2 floor plans"],
        },
        "status": "extracted",
        "confidence_summary": {
            "overall_confidence": 0.94,
            "dimension_reliability": "high",
            "notes": "Coordinated 2-storey residential plan with vertically aligned stair core",
        },
        "walls": [
            {
                "id": "W-L1-EXT-N",
                "wall_type": "exterior",
                "start_point_pixel": [100, 100],
                "end_point_pixel": [700, 100],
                "thickness_mm": 200.0,
                "thickness_category": "explicit",
                "confidence": 0.96,
                "provenance": "source_sketch",
                "source_bbox": [0.15, 0.12, 0.17, 0.83],
            },
            {
                "id": "W-L1-EXT-S",
                "wall_type": "exterior",
                "start_point_pixel": [100, 480],
                "end_point_pixel": [700, 480],
                "thickness_mm": 200.0,
                "thickness_category": "explicit",
                "confidence": 0.96,
                "provenance": "source_sketch",
                "source_bbox": [0.80, 0.12, 0.82, 0.83],
            },
        ],
        "openings": [],
        "rooms": [
            {
                "id": "R-GF-1",
                "raw_label": "LIVING ROOM",
                "standardized_type": "LIVING",
                "floor_level": "ground",
                "approx_width_mm": 4000.0,
                "approx_depth_mm": 5000.0,
                "dimension_provenance": "explicit",
                "confidence": 0.95,
                "source_bbox": [0.2, 0.15, 0.7, 0.45],
            },
            {
                "id": "R-1F-1",
                "raw_label": "MASTER BEDROOM",
                "standardized_type": "BEDROOM",
                "floor_level": "first_floor",
                "approx_width_mm": 4000.0,
                "approx_depth_mm": 5000.0,
                "dimension_provenance": "explicit",
                "confidence": 0.95,
                "source_bbox": [0.2, 0.15, 0.7, 0.45],
            },
        ],
        "stairs": [
            {
                "id": "STAIR-CORE-01",
                "direction": "up",
                "riser_count_hint": 16,
                "width_mm_hint": 1000.0,
                "confidence": 0.96,
                "source_bbox": [0.2, 0.5, 0.4, 0.65],
            }
        ],
        "dimensions": [
            {
                "id": "DIM-W",
                "source_text": "8000 mm",
                "value_mm": 8000.0,
                "category": "explicit",
                "target_entity_type": "overall_width",
                "confidence": 0.98,
                "source_bbox": [0.85, 0.4, 0.9, 0.6],
            },
            {
                "id": "DIM-D",
                "source_text": "6000 mm",
                "value_mm": 6000.0,
                "category": "explicit",
                "target_entity_type": "overall_depth",
                "confidence": 0.98,
                "source_bbox": [0.4, 0.05, 0.6, 0.1],
            },
        ],
        "uncertainties": [],
    }
    with open(OUT_DIR / "fixture-d-observations.json", "w", encoding="utf-8") as f:
        json.dump(obs, f, indent=2)


# ==========================================
# Fixture E: Nonrectangular Angled Plan
# ==========================================
def generate_fixture_e():
    img, draw = draw_sketch_base(1200, 900)
    # Angled boundary: North wall starts at (200, 300) and angles up to (900, 150)
    # Polygon: (200, 300) -> (900, 150) -> (900, 700) -> (200, 700) -> (200, 300)
    poly = [(200, 300), (900, 150), (900, 700), (200, 700)]
    draw.polygon(poly, outline=(40, 40, 50), width=6)
    draw.text((450, 400), "ANGLED LIVING SPACE", fill=(30, 30, 30))
    draw.text((450, 200), "ANGLED WALL (PRESERVE SLOPE)", fill=(200, 20, 20))
    draw.text((500, 730), "7000 mm", fill=(20, 20, 180))

    path = OUT_DIR / "fixture-e-nonrectangular.png"
    img.save(path)
    print(f"Generated {path}")

    obs = {
        "source_metadata": {
            "source_file": "fixture-e-nonrectangular.png",
            "file_type": "png",
            "page_number": 1,
            "total_pages": 1,
            "dimensions_pixels": {"width": 1200, "height": 900},
            "dpi": 72.0,
            "orientation_degrees": 0,
            "source_floor_hint": "Ground Floor",
            "preprocessing_applied": ["Deterministic RGB normalization"],
        },
        "status": "extracted",
        "confidence_summary": {
            "overall_confidence": 0.88,
            "dimension_reliability": "medium",
            "notes": "Nonrectangular floor plan with an intentionally angled northern boundary wall",
        },
        "walls": [
            {
                "id": "W-ANGLED-NORTH",
                "wall_type": "exterior",
                "start_point_pixel": [200, 300],
                "end_point_pixel": [900, 150],
                "thickness_mm": 200.0,
                "thickness_category": "explicit",
                "confidence": 0.92,
                "provenance": "source_sketch",
                "source_bbox": [0.16, 0.16, 0.34, 0.75],
            },
            {
                "id": "W-EXT-EAST",
                "wall_type": "exterior",
                "start_point_pixel": [900, 150],
                "end_point_pixel": [900, 700],
                "thickness_mm": 200.0,
                "thickness_category": "explicit",
                "confidence": 0.95,
                "provenance": "source_sketch",
                "source_bbox": [0.16, 0.74, 0.78, 0.76],
            },
            {
                "id": "W-EXT-SOUTH",
                "wall_type": "exterior",
                "start_point_pixel": [900, 700],
                "end_point_pixel": [200, 700],
                "thickness_mm": 200.0,
                "thickness_category": "explicit",
                "confidence": 0.95,
                "provenance": "source_sketch",
                "source_bbox": [0.77, 0.16, 0.79, 0.76],
            },
            {
                "id": "W-EXT-WEST",
                "wall_type": "exterior",
                "start_point_pixel": [200, 700],
                "end_point_pixel": [200, 300],
                "thickness_mm": 200.0,
                "thickness_category": "explicit",
                "confidence": 0.95,
                "provenance": "source_sketch",
                "source_bbox": [0.33, 0.16, 0.78, 0.17],
            },
        ],
        "openings": [],
        "rooms": [
            {
                "id": "R-ANGLED-1",
                "raw_label": "ANGLED LIVING SPACE",
                "standardized_type": "LIVING",
                "floor_level": "ground",
                "approx_width_mm": 7000.0,
                "approx_depth_mm": 5500.0,
                "dimension_provenance": "inferred",
                "confidence": 0.88,
                "source_bbox": [0.25, 0.2, 0.7, 0.7],
            }
        ],
        "dimensions": [
            {
                "id": "DIM-S",
                "source_text": "7000 mm",
                "value_mm": 7000.0,
                "category": "explicit",
                "target_entity_type": "overall_width",
                "confidence": 0.95,
                "source_bbox": [0.8, 0.4, 0.85, 0.6],
            }
        ],
        "uncertainties": [
            {
                "id": "unc-angled-wall",
                "field": "walls.W-ANGLED-NORTH",
                "severity": "warning",
                "description": "Wall W-ANGLED-NORTH is genuinely angled (slope preserved); confirm CAD drafting compatibility.",
                "suggested_action": "Confirm angled wall geometry without forcing orthogonal alignment.",
            }
        ],
    }
    with open(OUT_DIR / "fixture-e-observations.json", "w", encoding="utf-8") as f:
        json.dump(obs, f, indent=2)


if __name__ == "__main__":
    generate_fixture_a()
    generate_fixture_b()
    generate_fixture_c()
    generate_fixture_d()
    generate_fixture_e()
    print("All 5 sketch test fixtures and observation files generated successfully!")
