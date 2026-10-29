# Residential CAD Drawing Standards

## 1. Units & Scale Conventions
- **Metric Default**: Millimeters (mm) for high-precision architectural drafting, or meters (m) if explicitly requested.
  - Typical wall thickness: Exterior 200mm (or 230mm brick), Interior partitions 100mm (or 115mm).
  - Door openings: Main Entry = 900mm–1000mm, Bedroom = 800mm–850mm, Bath/WC = 700mm–750mm.
  - Window openings: Living = 1500mm–2400mm, Bedroom = 1200mm–1800mm, Bathroom = 600mm–900mm.
- **Imperial (Alternative)**: Fractional inches / architectural units.
  - Exterior walls: 8" (2x6 frame + siding/drywall) or 10" (brick veneer).
  - Interior walls: 4.5" (2x4 frame + drywall).
  - Door openings: 3'-0" entry, 2'-8" interior, 2'-4" bathroom.

---

## 2. Standard Layer Architecture (AIA Standard)
All generated floor plans should strictly adhere to structured layers:

| Layer Name | Color | Linetype | Description | Lineweight / Priority |
| :--- | :--- | :--- | :--- | :--- |
| `0` | White | Continuous | AutoCAD default (avoid placing drawing elements here) | Normal |
| `A-WALL-EXTR` | Cyan (4) | Continuous | Exterior load-bearing walls and building envelope | Heavy (0.50mm) |
| `A-WALL-INTR` | Green (3) | Continuous | Interior non-load-bearing partition walls | Medium (0.35mm) |
| `A-DOOR` | Yellow (2) | Continuous | Door frames, leaves, and 90° swing arcs | Light (0.18mm) |
| `A-GLAZ` | Blue (5) | Continuous | Window openings, frames, and glass centerlines | Medium-Light (0.25mm) |
| `A-FURN` | Green (3) | Continuous | Movable residential furniture (beds, sofas, tables) | Light (0.18mm) |
| `A-FIXT` | 8 (Dark Gray) | Continuous | Fixed plumbing fixtures and built-in kitchen cabinetry | Light (0.18mm) |
| `A-STAIR` | Yellow (2) | Continuous | Staircases, treads, landings, and walking direction arrows | Medium-Light (0.25mm) |
| `A-COLS` | Cyan (4) | Continuous | Structural columns and load-bearing piers | Heavy (0.50mm) |
| `A-FLOR-FIN` | 8 (Dark Gray) | Continuous | Room finish boundaries, tile grid hatches, floor transitions | Thin (0.13mm) |
| `A-ANNO-TEXT` | Red (1) | Continuous | Room names, area callouts (m² / sq ft), annotations | Text (0.25mm) |
| `A-ANNO-DIMS` | Magenta (6) | Continuous | Dimension lines, extension lines, tick marks, text | Light (0.18mm) |

---

## 3. Geometry Representation Rules

### 3.1 Walls
- Walls must be drawn with double lines representing the actual wall thickness.
- Wall junctions (L-junctions, T-junctions, and X-intersections) must be properly trimmed and continuous without interior closing lines separating adjoining wall bodies.
- Openings (doors and windows) must cut through both wall faces cleanly.

### 3.2 Doors
- Door assemblies consist of:
  1. The opening cut in the wall.
  2. The door leaf (rectangle or line indicating the open panel at 90°).
  3. The swing arc (quarter-circle arc with center at the hinge point, radius equal to the leaf width).

### 3.3 Windows
- Window openings cut through the wall lines.
- Represented by:
  - 2 jamb lines capping the wall cut.
  - 2 outer sill lines.
  - 1 or 2 centerlines representing the glass sash/pane.

### 3.4 Room Labels & Areas
- Text centered in each room space.
- Format:
  ```
  BEDROOM 1
  3.60 x 4.20 m
  15.1 m²
  ```
- Text height: 150mm–200mm in metric drawings (or 6"–8" in imperial).

### 3.5 Dimensions
- Dimension strings organized in hierarchical tiers:
  - **Tier 1 (Innermost)**: Openings and wall segments (wall to window, window width, window to door, etc.).
  - **Tier 2 (Middle)**: Room centerlines or major room boundary dimensions.
  - **Tier 3 (Outermost)**: Overall building length and width.
