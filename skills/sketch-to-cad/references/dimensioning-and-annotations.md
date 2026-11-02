# Architectural Dimensioning & Annotation Standards

This document specifies the dimensioning hierarchy, room annotation layout, sheet header composition, and North Arrow rules enforced by **Sketch-to-CAD**.

---

## 1. Tiered Exterior Dimension Chains

Exterior dimensions are placed in coordinated, non-colliding parallel chains offset outwards from the building envelope:

```
+-------------------------------------------------------------------+  Tier 1: Overall Envelope
       +-----------------------------+ +----------------------------+  Tier 2: Structural Bays
       +------+ +-------------+ +----+ +-----+ +-------------+ +----+  Tier 3: Openings & Piers
=====================================================================  Exterior Wall Face
```

### 1.1 Dimension Hierarchy
- **Tier 1 (Outer Chain)**: Total building length and depth from outside corner to outside corner. Standoff: $1800\text{ mm}$ from wall face.
- **Tier 2 (Middle Chain)**: Structural grid lines, major wall intersections, and room compartment widths. Standoff: $1200\text{ mm}$ from wall face.
- **Tier 3 (Inner Chain)**: Pier widths, door and window opening sizes, and corner returns. Standoff: $600\text{ mm}$ from wall face.

### 1.2 Drafting Rules
- Placed on layer `A-ANNO-DIMS`.
- Dimension lines feature standard architectural oblique tick marks (45° slashes) or filled arrows.
- Text placed above and centered on the dimension line, oriented to read from bottom or right of sheet (standard architectural readability convention).

---

## 2. Room Annotation Standards

Room labels are drafted on layer `A-ANNO-TEXT` and comprise:
1. **Room Name**: Uppercase bold architectural lettering (e.g., `LIVING ROOM`, `MASTER BEDROOM`, `KITCHEN`). Text height: $180\text{ mm}$ (1:50) or $250\text{ mm}$ (1:100).
2. **Room Area Callout**: Net floor area in square meters to two decimal places (e.g., `24.50 m²` or `24.5 m²`). Text height: $130\text{ mm}$ to $180\text{ mm}$.
3. **Room Identifier (Optional)**: Short reference tag (e.g., `[R-01]`).

### 2.1 Centroid Placement & Containment
- Label insertion points must lie inside the room's boundary polygon.
- Point-in-polygon verification ensures text never overlaps boundary partition walls or sits outside the room perimeter.

---

## 3. Sheet Title Block & Project Header

Every exported DXF drawing features a standardized sheet header placed below the floor plan outside dimension clearances:

- **Primary Title**: Project Name in uppercase (e.g., `VILLA SUNSET RESIDENCE`), text height $180\text{ mm}$ on layer `A-ANNO-TEXT`.
- **Secondary Subtitle**: `LEVEL: <FLOOR_NAME> | SCALE: <SCALE> | UNITS: <UNITS>` (e.g., `LEVEL: GROUND FLOOR | SCALE: 1:50 | UNITS: mm`), text height $130\text{ mm}$.
- Positioned deterministically at $X = 0$, $Y = -750\text{ mm}$ relative to the building footprint origin.

---

## 4. Strict Conditional North Arrow Policy

> [!IMPORTANT]
> **Deterministic Orientation Rule**:
> The North Arrow is drawn **if and only if** explicit orientation data is provided in the project metadata (`northAngle` or `orientation`).
> If orientation is absent or unknown, the North Arrow is **strictly omitted**.
> **NEVER** assume or fabricate a default North orientation on an architectural plan, as doing so introduces unverified navigational assumptions into site planning and solar analysis.

### 4.1 North Arrow Geometry (When Present)
- Placed on layer `A-ANNO-TEXT` at the upper right corner outside the plan envelope ($X = W_{\text{env}} + 600\text{ mm}$, $Y = D_{\text{env}} + 400\text{ mm}$).
- Consists of:
  - Enclosing circle (radius $200\text{ mm}$).
  - Directional pointer arrow oriented at angle $\theta_{\text{north}}$.
  - Uppercase `"N"` text marker at the arrow apex ($140\text{ mm}$ height, center-justified).
