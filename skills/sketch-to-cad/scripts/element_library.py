"""
Sketch-to-CAD Reusable Architectural Element Library
Standardized 2D residential CAD blocks, geometric primitives, and placement helpers.
"""

from typing import Dict, List, Optional, Tuple, Union, Any

# -------------------------------------------------------------------------
# AIA Standard Layer Definitions for Elements
# -------------------------------------------------------------------------
ELEMENT_LAYERS = {
    "furniture": {"name": "A-FURN", "color": "green", "description": "Movable furniture"},
    "sanitary": {"name": "A-FIXT", "color": "8", "description": "Plumbing and sanitary fixtures"},
    "kitchen": {"name": "A-FIXT", "color": "8", "description": "Kitchen counters, sinks, and appliances"},
    "circulation": {"name": "A-STAIR", "color": "yellow", "description": "Stairs, steps, and landings"},
    "structural": {"name": "A-COLS", "color": "cyan", "description": "Structural columns and load-bearing piers"},
    "finish": {"name": "A-FLOR-FIN", "color": "8", "description": "Floor finishes, tile boundaries, and hatches"},
}

# -------------------------------------------------------------------------
# Element Catalog Definitions
# -------------------------------------------------------------------------
ELEMENT_CATALOG: Dict[str, Dict[str, Any]] = {
    # ------------------ FURNITURE ------------------
    "FURN_BED_SINGLE": {
        "id": "FURN_BED_SINGLE",
        "name": "Single Bed",
        "category": "furniture",
        "layer": "A-FURN",
        "default_width": 1000.0,
        "default_depth": 2000.0,
        "base_point": [0.0, 0.0],
        "description": "Single bed 1000x2000mm with pillow and duvet fold",
        "primitives": [
            {"type": "rectang", "params": {"p1": [0.0, 0.0], "p2": [1000.0, 2000.0]}},
            {"type": "rectang", "params": {"p1": [200.0, 1550.0], "p2": [800.0, 1900.0]}},
            {"type": "line", "params": {"points": [[0.0, 1350.0], [1000.0, 1350.0]]}},
        ],
    },
    "FURN_BED_DOUBLE": {
        "id": "FURN_BED_DOUBLE",
        "name": "Double Bed",
        "category": "furniture",
        "layer": "A-FURN",
        "default_width": 1800.0,
        "default_depth": 2000.0,
        "base_point": [0.0, 0.0],
        "description": "Double bed 1800x2000mm with dual pillows and duvet fold",
        "primitives": [
            {"type": "rectang", "params": {"p1": [0.0, 0.0], "p2": [1800.0, 2000.0]}},
            {"type": "rectang", "params": {"p1": [150.0, 1550.0], "p2": [850.0, 1900.0]}},
            {"type": "rectang", "params": {"p1": [950.0, 1550.0], "p2": [1650.0, 1900.0]}},
            {"type": "line", "params": {"points": [[0.0, 1350.0], [1800.0, 1350.0]]}},
        ],
    },
    "FURN_BEDSIDE_TABLE": {
        "id": "FURN_BEDSIDE_TABLE",
        "name": "Bedside Table",
        "category": "furniture",
        "layer": "A-FURN",
        "default_width": 500.0,
        "default_depth": 450.0,
        "base_point": [0.0, 0.0],
        "description": "Nightstand 500x450mm with drawer front detail",
        "primitives": [
            {"type": "rectang", "params": {"p1": [0.0, 0.0], "p2": [500.0, 450.0]}},
            {"type": "line", "params": {"points": [[50.0, 100.0], [450.0, 100.0]]}},
            {"type": "line", "params": {"points": [[200.0, 50.0], [300.0, 50.0]]}},
        ],
    },
    "FURN_WARDROBE": {
        "id": "FURN_WARDROBE",
        "name": "Wardrobe",
        "category": "furniture",
        "layer": "A-FURN",
        "default_width": 1800.0,
        "default_depth": 600.0,
        "base_point": [0.0, 0.0],
        "description": "Wardrobe 1800x600mm with 3 compartments and swing diagonals",
        "primitives": [
            {"type": "rectang", "params": {"p1": [0.0, 0.0], "p2": [1800.0, 600.0]}},
            {"type": "line", "params": {"points": [[600.0, 0.0], [600.0, 600.0]]}},
            {"type": "line", "params": {"points": [[1200.0, 0.0], [1200.0, 600.0]]}},
            {"type": "line", "params": {"points": [[0.0, 0.0], [600.0, 600.0]]}},
            {"type": "line", "params": {"points": [[600.0, 0.0], [1200.0, 600.0]]}},
            {"type": "line", "params": {"points": [[1200.0, 0.0], [1800.0, 600.0]]}},
        ],
    },
    "FURN_SOFA_2SEAT": {
        "id": "FURN_SOFA_2SEAT",
        "name": "Two-Seater Sofa",
        "category": "furniture",
        "layer": "A-FURN",
        "default_width": 1500.0,
        "default_depth": 850.0,
        "base_point": [0.0, 0.0],
        "description": "Two-seater sofa 1500x850mm with backrest and dual cushions",
        "primitives": [
            {"type": "rectang", "params": {"p1": [0.0, 0.0], "p2": [1500.0, 850.0]}},
            {"type": "line", "params": {"points": [[0.0, 700.0], [1500.0, 700.0]]}},
            {"type": "line", "params": {"points": [[150.0, 0.0], [150.0, 700.0]]}},
            {"type": "line", "params": {"points": [[1350.0, 0.0], [1350.0, 700.0]]}},
            {"type": "line", "params": {"points": [[750.0, 0.0], [750.0, 700.0]]}},
        ],
    },
    "FURN_SOFA_3SEAT": {
        "id": "FURN_SOFA_3SEAT",
        "name": "Three-Seater Sofa",
        "category": "furniture",
        "layer": "A-FURN",
        "default_width": 2100.0,
        "default_depth": 850.0,
        "base_point": [0.0, 0.0],
        "description": "Three-seater sofa 2100x850mm with backrest and three cushions",
        "primitives": [
            {"type": "rectang", "params": {"p1": [0.0, 0.0], "p2": [2100.0, 850.0]}},
            {"type": "line", "params": {"points": [[0.0, 700.0], [2100.0, 700.0]]}},
            {"type": "line", "params": {"points": [[150.0, 0.0], [150.0, 700.0]]}},
            {"type": "line", "params": {"points": [[1950.0, 0.0], [1950.0, 700.0]]}},
            {"type": "line", "params": {"points": [[750.0, 0.0], [750.0, 700.0]]}},
            {"type": "line", "params": {"points": [[1350.0, 0.0], [1350.0, 700.0]]}},
        ],
    },
    "FURN_DINING_TABLE": {
        "id": "FURN_DINING_TABLE",
        "name": "Dining Table with Chairs",
        "category": "furniture",
        "layer": "A-FURN",
        "default_width": 1500.0,
        "default_depth": 900.0,
        "base_point": [0.0, 0.0],
        "description": "Dining table 1500x900mm with 4 chair footprints",
        "primitives": [
            {"type": "rectang", "params": {"p1": [0.0, 0.0], "p2": [1500.0, 900.0]}},
            # Chairs Top
            {"type": "rectang", "params": {"p1": [250.0, 900.0], "p2": [650.0, 1150.0]}},
            {"type": "rectang", "params": {"p1": [850.0, 900.0], "p2": [1250.0, 1150.0]}},
            # Chairs Bottom
            {"type": "rectang", "params": {"p1": [250.0, -250.0], "p2": [650.0, 0.0]}},
            {"type": "rectang", "params": {"p1": [850.0, -250.0], "p2": [1250.0, 0.0]}},
        ],
    },
    "FURN_DESK": {
        "id": "FURN_DESK",
        "name": "Study Desk",
        "category": "furniture",
        "layer": "A-FURN",
        "default_width": 1200.0,
        "default_depth": 600.0,
        "base_point": [0.0, 0.0],
        "description": "Desk 1200x600mm with chair footprint",
        "primitives": [
            {"type": "rectang", "params": {"p1": [0.0, 0.0], "p2": [1200.0, 600.0]}},
            {"type": "rectang", "params": {"p1": [350.0, -350.0], "p2": [850.0, 0.0]}},
            {"type": "line", "params": {"points": [[200.0, 480.0], [1000.0, 480.0]]}},
        ],
    },
    "FURN_TV_UNIT": {
        "id": "FURN_TV_UNIT",
        "name": "TV Media Console",
        "category": "furniture",
        "layer": "A-FURN",
        "default_width": 1600.0,
        "default_depth": 400.0,
        "base_point": [0.0, 0.0],
        "description": "TV media bench 1600x400mm with screen rectangle",
        "primitives": [
            {"type": "rectang", "params": {"p1": [0.0, 0.0], "p2": [1600.0, 400.0]}},
            {"type": "rectang", "params": {"p1": [200.0, 160.0], "p2": [1400.0, 240.0]}},
        ],
    },

    # ------------------ SANITARY FIXTURES ------------------
    "FIXT_TOILET": {
        "id": "FIXT_TOILET",
        "name": "Water Closet / Toilet",
        "category": "sanitary",
        "layer": "A-FIXT",
        "default_width": 450.0,
        "default_depth": 700.0,
        "base_point": [0.0, 0.0],
        "description": "Toilet with cistern tank and rounded bowl",
        "primitives": [
            {"type": "rectang", "params": {"p1": [0.0, 500.0], "p2": [450.0, 700.0]}},
            {"type": "line", "params": {"points": [[50.0, 500.0], [50.0, 200.0]]}},
            {"type": "line", "params": {"points": [[400.0, 500.0], [400.0, 200.0]]}},
            {"type": "line", "params": {"points": [[50.0, 200.0], [150.0, 50.0]]}},
            {"type": "line", "params": {"points": [[150.0, 50.0], [300.0, 50.0]]}},
            {"type": "line", "params": {"points": [[300.0, 50.0], [400.0, 200.0]]}},
        ],
    },
    "FIXT_WASHBASIN": {
        "id": "FIXT_WASHBASIN",
        "name": "Washbasin / Vanity",
        "category": "sanitary",
        "layer": "A-FIXT",
        "default_width": 600.0,
        "default_depth": 450.0,
        "base_point": [0.0, 0.0],
        "description": "Vanity counter 600x450mm with inner basin rim and faucet",
        "primitives": [
            {"type": "rectang", "params": {"p1": [0.0, 0.0], "p2": [600.0, 450.0]}},
            {"type": "rectang", "params": {"p1": [75.0, 75.0], "p2": [525.0, 375.0]}},
            {"type": "circle", "params": {"center": [300.0, 400.0], "radius": 20.0}},
        ],
    },
    "FIXT_SHOWER": {
        "id": "FIXT_SHOWER",
        "name": "Shower Tray",
        "category": "sanitary",
        "layer": "A-FIXT",
        "default_width": 900.0,
        "default_depth": 900.0,
        "base_point": [0.0, 0.0],
        "description": "Shower tray 900x900mm with drain and slope diagonals",
        "primitives": [
            {"type": "rectang", "params": {"p1": [0.0, 0.0], "p2": [900.0, 900.0]}},
            {"type": "rectang", "params": {"p1": [50.0, 50.0], "p2": [850.0, 850.0]}},
            {"type": "line", "params": {"points": [[50.0, 50.0], [850.0, 850.0]]}},
            {"type": "line", "params": {"points": [[50.0, 850.0], [850.0, 50.0]]}},
            {"type": "circle", "params": {"center": [450.0, 450.0], "radius": 40.0}},
        ],
    },
    "FIXT_BATHTUB": {
        "id": "FIXT_BATHTUB",
        "name": "Bathtub",
        "category": "sanitary",
        "layer": "A-FIXT",
        "default_width": 1700.0,
        "default_depth": 750.0,
        "base_point": [0.0, 0.0],
        "description": "Bathtub 1700x750mm with inner apron rim and drain",
        "primitives": [
            {"type": "rectang", "params": {"p1": [0.0, 0.0], "p2": [1700.0, 750.0]}},
            {"type": "rectang", "params": {"p1": [100.0, 80.0], "p2": [1600.0, 670.0]}},
            {"type": "circle", "params": {"center": [250.0, 375.0], "radius": 30.0}},
        ],
    },

    # ------------------ KITCHEN FIXTURES ------------------
    "FIXT_KITCHEN_COUNTER": {
        "id": "FIXT_KITCHEN_COUNTER",
        "name": "Kitchen Base Counter",
        "category": "kitchen",
        "layer": "A-FIXT",
        "default_width": 1200.0,
        "default_depth": 600.0,
        "base_point": [0.0, 0.0],
        "description": "Modular kitchen counter 1200x600mm with front overhang edge",
        "primitives": [
            {"type": "rectang", "params": {"p1": [0.0, 0.0], "p2": [1200.0, 600.0]}},
            {"type": "line", "params": {"points": [[0.0, 50.0], [1200.0, 50.0]]}},
        ],
    },
    "FIXT_KITCHEN_SINK": {
        "id": "FIXT_KITCHEN_SINK",
        "name": "Kitchen Double Sink",
        "category": "kitchen",
        "layer": "A-FIXT",
        "default_width": 800.0,
        "default_depth": 500.0,
        "base_point": [0.0, 0.0],
        "description": "Double-basin kitchen sink 800x500mm with mixer faucet",
        "primitives": [
            {"type": "rectang", "params": {"p1": [0.0, 0.0], "p2": [800.0, 500.0]}},
            {"type": "rectang", "params": {"p1": [50.0, 50.0], "p2": [380.0, 450.0]}},
            {"type": "rectang", "params": {"p1": [420.0, 50.0], "p2": [750.0, 450.0]}},
            {"type": "circle", "params": {"center": [400.0, 470.0], "radius": 20.0}},
        ],
    },
    "FIXT_COOKING_HOB": {
        "id": "FIXT_COOKING_HOB",
        "name": "Cooking Hob / Stove",
        "category": "kitchen",
        "layer": "A-FIXT",
        "default_width": 600.0,
        "default_depth": 500.0,
        "base_point": [0.0, 0.0],
        "description": "4-burner cooking range / hob 600x500mm",
        "primitives": [
            {"type": "rectang", "params": {"p1": [0.0, 0.0], "p2": [600.0, 500.0]}},
            {"type": "circle", "params": {"center": [160.0, 150.0], "radius": 60.0}},
            {"type": "circle", "params": {"center": [440.0, 150.0], "radius": 70.0}},
            {"type": "circle", "params": {"center": [160.0, 360.0], "radius": 50.0}},
            {"type": "circle", "params": {"center": [440.0, 360.0], "radius": 55.0}},
        ],
    },
    "FIXT_REFRIGERATOR": {
        "id": "FIXT_REFRIGERATOR",
        "name": "Refrigerator",
        "category": "kitchen",
        "layer": "A-FIXT",
        "default_width": 700.0,
        "default_depth": 700.0,
        "base_point": [0.0, 0.0],
        "description": "Refrigerator 700x700mm with door split line and handle",
        "primitives": [
            {"type": "rectang", "params": {"p1": [0.0, 0.0], "p2": [700.0, 700.0]}},
            {"type": "line", "params": {"points": [[0.0, 100.0], [700.0, 100.0]]}},
            {"type": "line", "params": {"points": [[150.0, 80.0], [550.0, 80.0]]}},
        ],
    },

    # ------------------ STRUCTURAL & CIRCULATION ------------------
    "STRUC_COL_SQUARE": {
        "id": "STRUC_COL_SQUARE",
        "name": "Square Column",
        "category": "structural",
        "layer": "A-COLS",
        "default_width": 200.0,
        "default_depth": 200.0,
        "base_point": [0.0, 0.0],
        "description": "Square reinforced concrete column 200x200mm",
        "primitives": [
            {"type": "rectang", "params": {"p1": [0.0, 0.0], "p2": [200.0, 200.0]}},
            {"type": "line", "params": {"points": [[0.0, 0.0], [200.0, 200.0]]}},
            {"type": "line", "params": {"points": [[0.0, 200.0], [200.0, 0.0]]}},
        ],
    },
    "STRUC_COL_RECT": {
        "id": "STRUC_COL_RECT",
        "name": "Rectangular Column",
        "category": "structural",
        "layer": "A-COLS",
        "default_width": 200.0,
        "default_depth": 400.0,
        "base_point": [0.0, 0.0],
        "description": "Rectangular structural column 200x400mm",
        "primitives": [
            {"type": "rectang", "params": {"p1": [0.0, 0.0], "p2": [200.0, 400.0]}},
            {"type": "line", "params": {"points": [[0.0, 0.0], [200.0, 400.0]]}},
            {"type": "line", "params": {"points": [[0.0, 400.0], [200.0, 0.0]]}},
        ],
    },
    "CIRC_STAIR_STRAIGHT": {
        "id": "CIRC_STAIR_STRAIGHT",
        "name": "Straight Stair Flight",
        "category": "circulation",
        "layer": "A-STAIR",
        "default_width": 1000.0,
        "default_depth": 2700.0,
        "base_point": [0.0, 0.0],
        "description": "Straight flight with 10 treads (270mm run) and walking line",
        "primitives": [
            {"type": "rectang", "params": {"p1": [0.0, 0.0], "p2": [1000.0, 2700.0]}},
            # 9 intermediate riser lines
            {"type": "line", "params": {"points": [[0.0, 270.0], [1000.0, 270.0]]}},
            {"type": "line", "params": {"points": [[0.0, 540.0], [1000.0, 540.0]]}},
            {"type": "line", "params": {"points": [[0.0, 810.0], [1000.0, 810.0]]}},
            {"type": "line", "params": {"points": [[0.0, 1080.0], [1000.0, 1080.0]]}},
            {"type": "line", "params": {"points": [[0.0, 1350.0], [1000.0, 1350.0]]}},
            {"type": "line", "params": {"points": [[0.0, 1620.0], [1000.0, 1620.0]]}},
            {"type": "line", "params": {"points": [[0.0, 1890.0], [1000.0, 1890.0]]}},
            {"type": "line", "params": {"points": [[0.0, 2160.0], [1000.0, 2160.0]]}},
            {"type": "line", "params": {"points": [[0.0, 2430.0], [1000.0, 2430.0]]}},
            # Center walking line with UP arrow
            {"type": "line", "params": {"points": [[500.0, 150.0], [500.0, 2550.0]]}},
            {"type": "line", "params": {"points": [[420.0, 2450.0], [500.0, 2550.0]]}},
            {"type": "line", "params": {"points": [[580.0, 2450.0], [500.0, 2550.0]]}},
        ],
    },
    "CIRC_STAIR_LSHAPE": {
        "id": "CIRC_STAIR_LSHAPE",
        "name": "L-Shaped Staircase",
        "category": "circulation",
        "layer": "A-STAIR",
        "default_width": 2000.0,
        "default_depth": 2000.0,
        "base_point": [0.0, 0.0],
        "description": "L-shaped flight with 1000x1000mm landing and turning treads",
        "primitives": [
            # Flight 1 (0..1000 X, 0..1000 Y)
            {"type": "rectang", "params": {"p1": [0.0, 0.0], "p2": [1000.0, 1000.0]}},
            {"type": "line", "params": {"points": [[0.0, 250.0], [1000.0, 250.0]]}},
            {"type": "line", "params": {"points": [[0.0, 500.0], [1000.0, 500.0]]}},
            {"type": "line", "params": {"points": [[0.0, 750.0], [1000.0, 750.0]]}},
            # Quarter Landing (0..1000 X, 1000..2000 Y)
            {"type": "rectang", "params": {"p1": [0.0, 1000.0], "p2": [1000.0, 2000.0]}},
            # Flight 2 (1000..2000 X, 1000..2000 Y)
            {"type": "rectang", "params": {"p1": [1000.0, 1000.0], "p2": [2000.0, 2000.0]}},
            {"type": "line", "params": {"points": [[1250.0, 1000.0], [1250.0, 2000.0]]}},
            {"type": "line", "params": {"points": [[1500.0, 1000.0], [1500.0, 2000.0]]}},
            {"type": "line", "params": {"points": [[1750.0, 1000.0], [1750.0, 2000.0]]}},
        ],
    },
}

# -------------------------------------------------------------------------
# Access & Validation Helper Functions
# -------------------------------------------------------------------------

def get_element_definition(block_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve block definition metadata by unique ID."""
    return ELEMENT_CATALOG.get(block_id)


def list_catalog_elements(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """List all supported element definitions, optionally filtered by category."""
    if not category:
        return list(ELEMENT_CATALOG.values())
    return [elem for elem in ELEMENT_CATALOG.values() if elem.get("category") == category]


def validate_element_instance(instance: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates an element placement request against library definitions and geometry rules.
    Returns (is_valid, list_of_errors).
    """
    errors: List[str] = []

    # Required fields
    required_fields = ["id", "blockId", "category", "position", "source"]
    for req in required_fields:
        if req not in instance or instance[req] is None:
            errors.append(f"Missing required property: '{req}'")

    if errors:
        return False, errors

    block_id = instance["blockId"]
    if block_id not in ELEMENT_CATALOG:
        errors.append(f"Unknown blockId '{block_id}'. Element not found in library catalog.")
        return False, errors

    elem_def = ELEMENT_CATALOG[block_id]

    # Category match
    if instance.get("category") != elem_def["category"]:
        errors.append(f"Category mismatch: instance declares '{instance.get('category')}', but '{block_id}' is defined under '{elem_def['category']}'.")

    # Position validation
    pos = instance.get("position")
    if not isinstance(pos, (list, tuple)) or len(pos) != 2:
        errors.append(f"Invalid position '{pos}': must be a 2-element [x, y] coordinate array.")
    else:
        if not all(isinstance(v, (int, float)) for v in pos):
            errors.append(f"Position coordinates must be numerical values: '{pos}'.")

    # Rotation validation
    rot = instance.get("rotation", 0.0)
    if not isinstance(rot, (int, float)):
        errors.append(f"Rotation must be numeric: '{rot}'.")

    # Scale validation
    scale = instance.get("scale", 1.0)
    if isinstance(scale, (int, float)):
        if scale <= 0:
            errors.append(f"Scale must be strictly positive: {scale}.")
    elif isinstance(scale, (list, tuple)):
        if len(scale) != 2 or any(not isinstance(s, (int, float)) or s <= 0 for s in scale):
            errors.append(f"Non-uniform scale must contain positive numbers: '{scale}'.")
    else:
        errors.append(f"Invalid scale format: '{scale}'.")

    # Source provenance validation
    valid_sources = ["explicit", "estimated", "inferred", "proposed"]
    src = instance.get("source")
    if src not in valid_sources:
        errors.append(f"Invalid source classification '{src}'. Must be one of {valid_sources}.")

    # Status validation
    valid_statuses = ["unresolved", "approved", "confirmed", "rejected"]
    status = instance.get("status", "confirmed")
    if status not in valid_statuses:
        errors.append(f"Invalid status '{status}'. Must be one of {valid_statuses}.")

    # Mandatory approval check: proposed elements must have status 'approved'
    if src == "proposed" and status != "approved":
        errors.append(f"Proposed element '{instance.get('id')}' requires explicit human approval before drafting.")

    return len(errors) == 0, errors


# -------------------------------------------------------------------------
# CADCraft MCP Integration Operations
# -------------------------------------------------------------------------

def ensure_element_layers(execute_fn) -> None:
    """Creates all designated element layers if they do not exist."""
    for category_info in ELEMENT_LAYERS.values():
        execute_fn(
            command="layer.new",
            params={
                "name": category_info["name"],
                "color": category_info["color"],
            }
        )


def register_cad_block(
    execute_fn,
    block_id: str,
    existing_blocks: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Registers an element as a reusable CAD block in the active drawing session.
    If the block already exists, re-registration is skipped.
    """
    if existing_blocks and block_id in existing_blocks:
        return {"block": block_id, "status": "already_registered"}

    elem_def = get_element_definition(block_id)
    if not elem_def:
        raise ValueError(f"Block '{block_id}' is not defined in the element library.")

    # 1. Switch to the target element layer
    target_layer = elem_def["layer"]
    execute_fn(command="layer.current", params={"name": target_layer})

    # 2. Draft primitives at origin [0, 0]
    drawn_handles: List[str] = []
    for prim in elem_def["primitives"]:
        cmd = prim["type"]
        params = prim["params"]
        res = execute_fn(command=cmd, params=params)
        if res and isinstance(res, dict):
            if "handles" in res and res["handles"]:
                drawn_handles.extend(res["handles"])
            elif "handle" in res and res["handle"]:
                drawn_handles.append(res["handle"])

    if not drawn_handles:
        raise RuntimeError(f"Failed to draft primitives for block '{block_id}'. Zero handles returned.")

    # 3. Create the block and delete temporary drafting entities from model space
    block_res = execute_fn(
        command="block",
        params={
            "name": block_id,
            "base": elem_def.get("base_point", [0.0, 0.0]),
            "handles": drawn_handles,
            "keep": "delete",
            "description": elem_def.get("description", ""),
        }
    )
    return {"block": block_id, "status": "created", "details": block_res}


def insert_cad_element(
    execute_fn,
    block_id: str,
    at: List[float],
    rotation: float = 0.0,
    scale: Union[float, List[float]] = 1.0,
    existing_blocks: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Ensures block is registered and inserts an instance at the specified coordinates.
    """
    elem_def = get_element_definition(block_id)
    if not elem_def:
        raise ValueError(f"Unknown block ID '{block_id}'.")

    # Ensure block is registered in session
    register_cad_block(execute_fn, block_id, existing_blocks=existing_blocks)

    # Ensure layer is active
    execute_fn(command="layer.current", params={"name": elem_def["layer"]})

    # Execute insert
    insert_params = {
        "name": block_id,
        "at": at,
        "rotation": float(rotation),
    }
    if isinstance(scale, (int, float)):
        insert_params["scale"] = float(scale)
    elif isinstance(scale, (list, tuple)):
        insert_params["scale"] = [float(scale[0]), float(scale[1])]

    res = execute_fn(command="insert", params=insert_params)
    return res


def create_floor_finish_hatch(
    execute_fn,
    boundary_pts: List[List[float]],
    pattern: str = "ANSI37",
    scale: float = 20.0
) -> Dict[str, Any]:
    """
    Creates a floor finish tile hatch boundary and applies hatching on A-FLOR-FIN.
    """
    execute_fn(command="layer.current", params={"name": "A-FLOR-FIN"})
    
    # Draw closed boundary rectangle or polygon
    if len(boundary_pts) == 2:
        # p1, p2 rectangle
        poly_res = execute_fn(command="rectang", params={"p1": boundary_pts[0], "p2": boundary_pts[1]})
    else:
        # Closed polyline
        poly_res = execute_fn(command="pline", params={"vertices": boundary_pts, "closed": True})

    boundary_handle = None
    if poly_res and isinstance(poly_res, dict):
        boundary_handle = poly_res.get("handle") or (poly_res.get("handles", [None])[0])

    if not boundary_handle:
        raise RuntimeError("Failed to generate boundary geometry for floor finish hatch.")

    hatch_res = execute_fn(
        command="hatch",
        params={
            "handles": [boundary_handle],
            "pattern": pattern,
            "scale": float(scale),
        }
    )
    return {"boundary": boundary_handle, "hatch": hatch_res}
