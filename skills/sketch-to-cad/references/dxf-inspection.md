# Independent Architectural & Structural DXF Inspection Reference

This document describes the architectural inspection rules, geometric integrity checks, and validation standards enforced by the **Independent DXF Inspector** (`scripts/dxf_inspector.py`).

---

## 1. Inspection Purpose & Role in Quality Assurance

Generated CAD drawings must be structurally valid, geometrically clean, and compliant with architectural drafting standards before being delivered to clients or passed to downstream BIM modeling skills.

The `DXFInspector` performs automated post-generation quality auditing directly on `.dxf` drawing files on disk, operating independently from the generator logic.

---

## 2. Header & Dimensional Units Inspection

| Header Variable | Required Value | Architectural Rationale |
| :--- | :--- | :--- |
| **`$INSUNITS`** | `4` (Millimeters) | Ensures seamless 1:1 metric scale import in downstream CAD/BIM tools. |
| **`$ACADVER`** | `AC1027` (AutoCAD 2013) or `AC1032` (AutoCAD 2018) | Standard modern DXF release compatible with Autodesk, BIMCraft, FreeCAD, and Rhino. |
| **Drawing Extents** | Finite, non-empty bounding box | Catches coordinate inversion, degenerate plans, or off-sheet stray entities. |

---

## 3. Layer Architecture Compliance

CAD drawings must adhere to the **AIA CAD Layer Guidelines** (American Institute of Architects):

- **Permitted Layers**:
  - `A-WALL-EXTR`, `A-WALL-INTR`, `A-WALL`: Exterior and interior wall boundaries.
  - `A-DOOR`: Door openings and swing arcs.
  - `A-GLAZ`: Window frames and glazing centerlines.
  - `A-FURN`: Furniture block references.
  - `A-FIXT`: Plumbing and sanitary fixtures.
  - `A-STAIR`: Staircase treads and walkline annotations.
  - `A-COLS`: Structural columns.
  - `A-FLOR-FIN`: Floor finish hatches and tiling.
  - `A-FLOR-LEVL`: Finished floor level markers and room stamps.
  - `A-ANNO-TEXT`, `A-ANNO-DIMS`: Room text labels and dimension strings.
- **Default Layer `0` Rule**: Layer `0` must contain **0** geometric entities. Geometry on layer `0` generates an audit warning.

---

## 4. Geometric Integrity & Topological Audits

### 4.1 Duplicate Entity Detection
Identifies redundant lines or arcs sharing the same coordinates and layer:
- Tolerance: Endpoints within $1.0\text{ mm}$ on identical layers.
- Severity: `WARNING`.

### 4.2 Degenerate Geometry Detection
Identifies line segments with length $< 10.0\text{ mm}$:
- Length: $\sqrt{\Delta x^2 + \Delta y^2} < 10.0\text{ mm}$.
- Severity: `FAILED` (Blocking). Such entities cause self-intersections or numerical failures in downstream BIM wall extrusion.

---

## 5. Model-to-DXF-to-BIM Cross-Audit

When an approved model and BIM handoff are supplied, the inspector performs cross-deliverable consistency checking:
- **Wall Count**: Verifies that the number of wall entities in the DXF matches the approved model wall count.
- **Opening Count**: Verifies door/window counts between model, DXF swing arcs, and companion BIM handoff.
- **Block Reference Count**: Verifies furniture and fixture blocks match approved model elements.
- **Handoff Coordination**: Flags discrepancies where geometry exists in CAD but is missing from BIM metadata.

---

## 6. Inspection Deliverables & CLI Usage

Run inspection via CLI:
```bash
python scripts/dxf_inspector.py path/to/drawing.dxf --model path/to/model.json --handoff path/to/handoff.json
```

Outputs:
- JSON Report: `drawing.dxf.inspection.json`
- Markdown Audit: `drawing.dxf.inspection.md`
