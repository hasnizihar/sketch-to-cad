# Architectural Drafting Standards

This document establishes the official architectural drafting standards, layer conventions, geometric representations, and detailing rules enforced by the **Sketch-to-CAD** engine.

---

## 1. Coordinate System & Measurement Units

- **Coordinate System**: 2D Cartesian Right-Handed ($+X$ East, $+Y$ North, Origin $(0, 0)$ at South-West footprint corner).
- **Primary Units**: Millimeters ($\text{mm}$) for architectural CAD generation and downstream BIM handoff.
- **Precision**: Coordinates and dimensions are drafted with millimeter precision without floating-point drift.
- **Scale Standards**: 1:50 (detailed residential), 1:100 (general layout), 1:200 (site/schematic).

---

## 2. AIA/ISO Layer Architecture

All entities produced by the CADCraft generation pipeline are strictly allocated to standardized AIA CAD layers:

| Layer Name | CAD Color | Lineweight | Linetype | Architectural Content |
| :--- | :--- | :--- | :--- | :--- |
| `A-WALL-EXTR` | Cyan (4) | 0.50 mm | Continuous | Exterior building perimeter walls and structural envelope |
| `A-WALL-INTR` | Green (3) | 0.35 mm | Continuous | Interior non-load-bearing partitions and dividing walls |
| `A-DOOR` | Yellow (2) | 0.18 mm | Continuous | Door leaves, jambs, sliding tracks, and 90° swing arcs |
| `A-GLAZ` | Blue (5) | 0.25 mm | Continuous | Window frames, sills, and glazing panel centerlines |
| `A-COLS` | Cyan (4) | 0.50 mm | Continuous | Reinforced concrete or steel columns and load-bearing piers |
| `A-STAIR` | Yellow (2) | 0.25 mm | Continuous | Stair treads, risers, handrails, and walk-line direction arrows |
| `A-FURN` | Green (3) | 0.18 mm | Continuous | Movable residential furniture (beds, sofas, tables, desks) |
| `A-FIXT` | Dark Gray (8) | 0.18 mm | Continuous | Fixed plumbing fixtures (toilets, basins, showers) and kitchen units |
| `A-FLOR-FIN` | Dark Gray (8) | 0.13 mm | Continuous | Floor finish patterns (wet-area tiles, timber planks) |
| `A-FLOR-LEVL` | Magenta (6) | 0.18 mm | Continuous | Floor datum markers and level elevation callouts |
| `A-ANNO-TEXT` | Red (1) | 0.25 mm | Continuous | Room names, area callouts ($m^2$), sheet titles, and North arrow |
| `A-ANNO-DIMS` | Magenta (6) | 0.18 mm | Continuous | Exterior and interior dimension lines, extension lines, tick marks |

---

## 3. Wall Geometry & Junction Engineering

### 3.1 Double-Line Cavity Representation
- Walls are represented as continuous parallel double lines spaced by the wall thickness ($T$):
  - Standard Exterior: $200\text{ mm}$ to $250\text{ mm}$ (insulated blockwork or brick veneer).
  - Standard Interior: $100\text{ mm}$ to $150\text{ mm}$ (drywall stud or masonry partition).
- Cavity trimming must ensure zero double-line penetration into host wall cores:
  - **L-Junctions**: Exterior corners meet cleanly at 90° or specified angle with intersecting outer and inner faces.
  - **T-Junctions**: When an interior partition meets an exterior or host partition wall, incoming partition double lines are trimmed back by $T_{\text{host}} / 2$, cleanly terminating at the inner face of the host cavity.
  - **Cross-Junctions (X)**: Intersecting partitions are trimmed to preserve open core continuity without internal divider lines.

### 3.2 Opening Cuts & Transverse Jamb End-Caps
- Wall lines must break cleanly across door and window openings.
- Openings are sealed on both sides by transverse jamb end-caps perpendicular to the wall axis, bridging the outer and inner wall faces on layer `A-WALL-EXTR` or `A-WALL-INTR`.

---

## 4. Door & Window Drafting Conventions

### 4.1 Single-Leaf Hinged Doors
- **Components**:
  1. Clear opening cut through host wall.
  2. Door leaf panel drawn at 90° open position with length equal to clear opening width.
  3. Circular swing arc spanning 90° with center at hinge point on layer `A-DOOR`.
- **Swing Directions**:
  - `inward-right` / `inward-left`: Panel swings into the interior room space.
  - `outward-right` / `outward-left`: Panel swings outward (mandated for exit doors and small bathrooms).

### 4.2 Double-Leaf Doors (`swing: "double"`)
- Dual opposing leaves each with width $W/2$ hinged from opposite jambs.
- Dual 90° swing arcs meeting symmetrically at the center of the opening.

### 4.3 Sliding & Pocket Doors (`swing: "sliding"`)
- Parallel offset overlapping panel lines indicating sliding tracks on layer `A-DOOR`.
- Zero swing arcs (enforces ADA and clearance rules without swing arc conflicts).

### 4.4 Windows
- **Casement / Fixed Windows**:
  - Outer frame jamb caps on host wall.
  - Double sill lines and central glazing centerline on layer `A-GLAZ`.
- **Sliding Windows (`swing: "sliding"`)**:
  - Dual offset overlapping sash lines representing bypass glass panels.

---

## 5. Architectural Symbols & Fixtures

- Architectural elements are inserted from the standardized `element_library.py` block catalog.
- Standard insertion origins: Centroid or back-wall anchor point.
- Zero duplication: Pre-existing blocks are instantiated as block references (`INSERT`) rather than redrawn.
- Boundary containment: All furniture and fixtures must reside entirely inside room boundaries.
