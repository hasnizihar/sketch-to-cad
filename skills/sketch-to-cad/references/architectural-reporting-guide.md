# Architectural Reporting & Scheduling Reference Guide

## 1. Overview

The **Architectural Reporting & Scheduling Engine** deterministically transforms an approved canonical floor-plan model (`floor-plan-model.json`) into comprehensive, auditable architectural schedules and technical documentation. It provides:
1. **Executive Architectural Summary** (footprints, net areas, counts, validation status)
2. **Room Area & Dimension Schedule** (internal clear dimensions, Shoelace net areas, perimeters)
3. **Door & Window Schedules** (host-wall relationships, widths, swing geometry, null vertical clearances)
4. **Architectural Element Inventory** (furniture, sanitary fixtures, kitchen equipment, structure, circulation)
5. **Floor Finish Schedule** (material mapping audit, covered area, pattern hatching)
6. **Uncertainty & Verification Audit** (provenance tracking, host-wall validation, overlap checks)
7. **Deliverable Exports**:
   - Machine-readable JSON: `<drawing-name>.report.json` (validated against `architectural-report.schema.json`)
   - Formatted Markdown: `<drawing-name>.report.md`
   - Executive PDF Report: `<drawing-name>.report.pdf` (paginated multi-page document via ReportLab)

---

## 2. Area & Geometry Calculation Conventions

### 2.1 Net Room Area vs. Gross Footprint Area

| Metric | Calculation Method | Internal Unit | Display Unit | Definition & Scope |
| :--- | :--- | :--- | :--- | :--- |
| **Net Room Area** | Shoelace polygon formula on `boundaryCorners` | $\text{mm}^2$ | $\text{m}^2$ (2 dec.) | Clear usable internal floor area measured to internal wall faces. Excludes wall thicknesses and partition cavities. |
| **Gross Footprint Area** | Envelope bounding box ($W \times D$) | $\text{mm}^2$ | $\text{m}^2$ (2 dec.) | Total building footprint bounding perimeter measured to exterior wall faces. Includes perimeter walls and interior partitions. |

> [!IMPORTANT]
> **Shoelace Formula**: For $n$ polygon vertices $(x_0, y_0), \dots, (x_{n-1}, y_{n-1})$:
> $$A = \frac{1}{2} \left| \sum_{i=0}^{n-1} (x_i y_{i+1} - x_{i+1} y_i) \right|$$
> Where $(x_n, y_n) = (x_0, y_0)$. Area in $\text{m}^2 = A / 10^6$.

### 2.2 Room Dimensions (Length & Width)

- **Orthogonal Rectangular Rooms**: When a room boundary consists of exactly 4 vertices forming an axis-aligned rectangle, length is reported as $\max(\Delta X, \Delta Y)$ and width as $\min(\Delta X, \Delta Y)$ in meters.
- **Irregular / Polygonal Rooms**: When a room is L-shaped, chamfered, or non-orthogonal, length and width are reported strictly as `null` / `N/A`. The engine **never manufactures** a false length $\times$ width simplification for irregular spaces.

### 2.3 Room Perimeter

Perimeter is computed as the sum of Euclidean distances between adjacent boundary vertices:
$$P = \sum_{i=0}^{n-1} \sqrt{(x_{i+1} - x_i)^2 + (y_{i+1} - y_i)^2}$$
Reported in millimeters and converted to meters ($P / 1000.0$).

---

## 3. Schedule Specifications & Columns

### 3.1 Room Schedule Columns

| Column | Internal Key | Type | Description |
| :--- | :--- | :--- | :--- |
| **Room ID** | `id` | String | Stable unique room identifier (e.g. `R1`, `ROOM-BED-01`). |
| **Room Name** | `name` | String | Approved space designation (e.g. `STUDIO / LIVING`, `BATHROOM`). |
| **Floor** | `floorId` | String | Associated storey identifier (default: `LEVEL-01`). |
| **Length (m)** | `lengthMm` | Float/Null | Clear internal length in meters. `N/A` for irregular rooms. |
| **Width (m)** | `widthMm` | Float/Null | Clear internal width in meters. `N/A` for irregular rooms. |
| **Net Area (m²)** | `netAreaM2` | Float | Calculated internal clear area (2 decimal places). |
| **Perimeter (m)** | `perimeterM` | Float/Null | Closed internal perimeter in meters. |
| **Finish Pattern**| `finishPattern` | String/Null| Associated surface finish pattern (e.g. `tile_grid`, `wood_strip`). |
| **Method** | `calculationMethod` | String | `"shoelace_boundary_polygon"`, `"model_annotated"`, or `"uncalculated"`. |
| **Notes** | `notes` | String | Boundary geometry description and orthogonal qualification notes. |

---

### 3.2 Opening Schedules (Doors & Windows)

| Column | Internal Key | Type | Description |
| :--- | :--- | :--- | :--- |
| **Opening ID** | `id` | String | Stable unique opening identifier (e.g. `D-01`, `WIN-01`). |
| **Type** | `type` | String | `"door"`, `"window"`, or `"cased_opening"`. |
| **Floor** | `floorId` | String | Associated storey identifier. |
| **Host Wall** | `wallId` | String | Validated host wall reference (e.g. `W-EXT-01`). Flagged if invalid. |
| **Associated Space**| `associatedRoomIds` | Array | Room(s) geometrically connected or bounded by this opening. |
| **Width (mm)** | `widthMm` | Float | Clear structural opening width in millimeters. |
| **Height (mm)** | `heightMm` | Float/Null | Head clearance in mm. Preserved as `null` when unannotated in 2D. |
| **Sill (mm)** | `sillHeightMm` | Float/Null | Sill height in mm. `0` for flush doors; `null` for unannotated windows. |
| **Swing** | `swing` | String/Null | Door leaf swing geometry (e.g. `inward-left`, `90_deg_single`). |
| **Status** | `verificationStatus` | String | `"verified"`, `"invalid_host_wall"`, or `"missing_width"`. |

> [!WARNING]
> **No Fabricated Clearances**: In 2D floor plans, vertical elevations are unmeasured. Height and sill clearance are stored as `null`. Downstream 3D BIM skills (`dxf-to-3d-bim`) must obtain user confirmation for vertical parameters.

---

### 3.3 Architectural Element Inventory

- **Categories**: `furniture`, `sanitary`, `kitchen`, `circulation`, `structural`.
- **Instance Count**: Aggregated strictly by inserted block references. Block definitions in the catalog without inserted instances report count `0` and are not inflated.
- **Attributes**: Itemized instances include coordinates `[X, Y]`, rotation angle, bounding dimensions (`width`, `depth`), associated room, and approval status.

---

### 3.4 Floor Finish Schedule

- **Hatch vs. Material Rule**: A graphical CAD hatch (`ANSI37`, `NET`, `ANSI31`) represents visual texture, not physical material specification.
- If physical material is not explicitly defined in the model, `material` reports `null` and `verificationStatus` reports `material_unspecified (graphical hatch pattern only)`.

---

## 4. Uncertainty & Verification Audit

The audit module automatically inspects:
1. **Unresolved Ambiguities**: Propagates all items from `model.uncertainties`.
2. **Host-Wall Validation**: Verifies that every door/window `wallId` exists in `model.walls`. Nonexistent walls are flagged as `invalid_host_wall`.
3. **Room Polygon Overlaps**: Tests all pairs of room boundaries using ray-casting and segment-intersection algorithms to guarantee non-overlapping net floor areas.
4. **Envelope Clearance**: Verifies that all elements and wall segments reside within $[0..W, 0..D]$.
5. **Approval Gate Enforcement**:
   - If `model.status != "approved"`, the report is stamped with `validationStatus = "DRAFT"` and `isApprovedForConstruction = false`.
   - Clear warning banner: `⚠️ DRAFT / NOT APPROVED FOR CONSTRUCTION`.

---

## 5. CLI Usage & Pipeline Integration

### 5.1 Standalone CLI Report Generation
```powershell
python scripts/architectural_reports.py `
  --model tests/fixtures/sample-model-with-elements.json `
  --dxf tests/output/furnished-plan.dxf `
  --handoff tests/output/furnished-plan.handoff.json `
  --output-dir tests/output `
  --output-base furnished-plan
```

### 5.2 Unified Drawing & Reporting Pipeline
```powershell
python scripts/drawing_generator.py `
  --model tests/fixtures/sample-model-with-elements.json `
  --output-dxf tests/output/furnished-plan.dxf `
  --output-png tests/output/furnished-plan.png `
  --generate-report
```
When `--generate-report` is passed, the generator outputs:
- `furnished-plan.dxf`
- `furnished-plan.png`
- `furnished-plan.handoff.json`
- `furnished-plan.report.json`
- `furnished-plan.report.md`
- `furnished-plan.report.pdf`
