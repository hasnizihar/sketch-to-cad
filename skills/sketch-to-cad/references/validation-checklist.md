# Residential CAD Validation Checklist

This checklist must be executed during Phase 7 (Validation) before delivering any generated drawing.

## 1. Setup & Layer Pre-Flight
- [ ] Drawing units verified (`metric: true` for mm/m, or imperial).
- [ ] Standard AIA layers exist with assigned colors (`A-WALL-EXTR`, `A-WALL-INTR`, `A-DOOR`, `A-GLAZ`, `A-ANNO-TEXT`, `A-ANNO-DIMS`).
- [ ] No entities placed indiscriminately on default layer `0`.

---

## 2. Wall Geometry & Envelope
- [ ] **Enclosure**: Exterior envelope is completely closed with no accidental gaps or disjoint segments.
- [ ] **Wall Thickness**:
  - Exterior walls have consistent specified thickness (e.g., 200mm).
  - Interior partitions have consistent specified thickness (e.g., 100mm).
- [ ] **Junction Cleanliness**: T-junctions and corner L-junctions have interior collision lines removed (walls merge seamlessly).
- [ ] **No Duplicate Entities**: No duplicate overlapping lines or zero-length line artifacts.

---

## 3. Openings (Doors & Windows)
- [ ] **Wall Cuts**: Every door and window has a matching physical opening cut through the host wall.
- [ ] **Door Clearances**:
  - Door swing arcs do not collide with adjacent walls, fixtures, or opposing door swings.
  - Door swings open inwards against an adjoining wall where practical.
- [ ] **Window Alignment**: Windows sit flush inside the wall openings with jamb endpoints matching wall vertices.

---

## 4. Room Layout & Circulation
- [ ] **Room Boundaries**: Every specified room has clear enclosing boundaries.
- [ ] **Accessibility / Circulation**: Every habitable room is accessible via a hallway, door, or open doorway of minimum clearance (≥ 800mm).
- [ ] **Bath / WC Privacy**: Bathrooms open into private hallways or lobbies, not directly into main kitchens or dining areas where local building codes prohibit it.

---

## 5. Annotations & Dimensions
- [ ] **Room Labels**: Centered within the physical room boundaries, legible, and placed on `A-ANNO-TEXT`.
- [ ] **Dimension Accuracy**: Numerical text on dimensions matches the true coordinate distance between witness points.
- [ ] **Dimension Placement**: Exterior dimensions placed outside the building footprint with proper offset so they do not overlap walls.

---

---

## 6. Mandatory Visual QA & Source Comparison
- [ ] **Dimension Readability**: Numeric text values are visible, legible, and unclipped at standard viewing scale (`textHeight >= 150mm`).
- [ ] **Source Sketch Reconciliation**: Opening locations (e.g. entrance on East vs North) and swing directions match the original sketch.
- [ ] **Jamb Closures**: Wall thickness cutouts at doors and windows have physical transverse jamb end-caps sealing the wall cavity.
- [ ] **Annotation Clearances**: Room names and labels do not collide with walls, door swings, or cross circulation corridors.

---

## 7. Export & File Integrity Checks
- [ ] **DXF Export**: File created on disk, non-zero file size, verified by `inspect_drawing` or CLI `info`.
- [ ] **Visual Preview (PNG)**: Rendered successfully, non-zero file size, extents fit the bounding box cleanly.
- [ ] **Extents Sanity**: Drawing extents `[[min_x, min_y], [max_x, max_y]]` match the anticipated building footprint (no stray entities miles away from the origin).
