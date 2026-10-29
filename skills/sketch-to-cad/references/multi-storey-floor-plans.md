# Multi-Storey Residential Floor Plans Reference Guide

## 1. Architectural Purpose & Boundaries

`sketch-to-cad` is a specialized 2D architectural drafting skill. When processing multi-storey residences (duplexes, two-storey houses, villas), the skill generates **independent, editable 2D floor plans** for each storey.

> [!IMPORTANT]
> **2D Floor Plans Only**: This skill intentionally generates 2D drawings only. It does NOT generate 3D geometry, building elevations, cross-sections, or BIM models. The separate downstream `dxf-to-3d-bim` skill consumes these coordinated 2D deliverables and is solely responsible for generating 3D models.

---

## 2. Independent DXF Drawing Separation

In professional architectural practice, storeys are **never** drafted overlapping in the same model space. Each storey requires its own dedicated CAD file:

1. **Ground Floor**: `<project>-level-01.dxf` (+ visual preview `<project>-level-01.png`)
2. **First Floor**: `<project>-level-02.dxf` (+ visual preview `<project>-level-02.png`)
3. **N-th Floor**: `<project>-<level-id>.dxf` (+ visual preview `<project>-<level-id>.png`)

Each drawing is constructed in a distinct, isolated CADCraft session (`new_drawing(metric=True)`), guaranteeing:
- Zero entity leakage between floors.
- Exact entity counts per floor.
- Separate architectural presentation sheets and permit sets.

---

## 3. Shared Project Coordinate Reference

To enable downstream 3D BIM assembly without manual spatial alignment:
- All storeys share an identical Cartesian 2D right-handed Y-up coordinate origin `[0.0, 0.0]`.
- Vertical building elements (structural columns, stairwells, plumbing stacks, external envelopes) are placed at matching $(X, Y)$ coordinates across all levels.
- Offsets between floors can be verified directly without coordinate transformations.

---

## 4. Vertical Coordination & Alignment Checks

The system performs automated vertical coordination checks via `validate_vertical_coordination(model)`:

### A. Staircase Vertical Circulation
- **Floor Connectivity**: Validates that `sourceFloorId` and `destinationFloorId` exist in the model's `floors` declaration.
- **Footprint / Centroid Alignment**: Compares stair position $(X_{\text{src}}, Y_{\text{src}})$ and $(X_{\text{dest}}, Y_{\text{dest}})$ across storeys.
  $$\Delta X = |X_{\text{dest}} - X_{\text{src}}| \le \text{tolerance}$$
  $$\Delta Y = |Y_{\text{dest}} - Y_{\text{src}}| \le \text{tolerance}$$
  The default tolerance is $50.0\text{ mm}$. Any offset exceeding this threshold is flagged as a `VERTICAL COORDINATION ERROR` and halts construction approval.
- **Upper Floor Void / Opening**: Validates that upper levels contain an arrival landing, stair void, or corresponding circulation element.

### B. Structural Column Continuity
- Compares structural column positions (`category: structural`, `STRUC_COL_SQUARE` / `STRUC_COL_RECT`) between vertically adjacent floors.
- Columns on the same vertical grid line must align within $50.0\text{ mm}$ tolerance. Offsets are flagged as `VERTICAL COORDINATION WARNING`.

---

## 5. Multi-Storey Approval Gate

The Mandatory Human Approval Gate is enforced at two tiers:
1. **Model Level**: `model.status == "approved"`.
2. **Floor Level**: Every storey in `floors` and `approval.floorApprovals` must be marked `"approved"`.
If any individual storey has status `"awaiting_approval"` or `"draft"`, CAD drafting is halted with an `ApprovalGateError`.

---

## 6. Multi-Storey Deliverables Ecosystem

A multi-storey residential project produces four synchronized deliverables:

| Deliverable | Format | Purpose |
| :--- | :--- | :--- |
| **Per-Floor DXF Drawings** | `.dxf` (Release 2018) | Layered, editable 2D CAD floor plans for each storey |
| **Per-Floor Visual Previews** | `.png` | Visual verification of walls, doors, windows, and elements |
| **Companion BIM Manifest** | `.handoff.json` | Coordinated metadata mapping all floor DXF paths (`dxf.floorDrawings`) and `stairs` schema |
| **Consolidated Report** | `.report.json`, `.report.md`, `.report.pdf` | Floor-by-floor room area schedules, door/window schedules, finish quantities, and vertical coordination audit |
