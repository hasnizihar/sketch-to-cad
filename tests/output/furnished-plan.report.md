# Architectural Documentation & Schedules Report

> **Project:** Studio-Apartment-Furnished-Fixture | **Drawing ID:** `floor-plan`  
> **Approval State:** **STATUS: APPROVED**  
> **Date:** 2026-10-30T01:15:00Z | **Units:** mm (`Cartesian2D_RightHanded_YUp`)  

---

## 1. Executive Architectural Summary

| Parameter | Metric / Value | Calculation & Scope Notes |
| :--- | :--- | :--- |
| **Floors Represented** | 1 Storey | Single-storey ground level (`LEVEL-01`) |
| **Verified Net Area** | **25.16 m²** | Sum of internal clear room polygons (Shoelace formula) |
| **Gross Footprint Area** | 30.00 m² | Exterior bounding box footprint (exterior_envelope_bounding_box) |
| **Room Enclosures** | 3 Rooms | Verified room boundaries with centroids |
| **Door Openings** | 2 Doors | Capped jambs with swing arcs |
| **Window Openings** | 2 Windows | Centerline glazing and jamb cuts |
| **Architectural Blocks** | 8 Instances | Furniture, sanitary fixtures, structure & circulation |
| **Floor Finishes** | 1 Finish Zones | Surface boundaries and graphical tile hatching |
| **Uncertainty Audit** | 2 Items (1 unresolved) | Documented assumptions & unverified 2D heights |
| **Validation Status** | **PASSED** | Architectural rule compliance & integrity |

---

## 2. Room Area & Dimension Schedule

| Room ID | Room Name | Floor | Length (m) | Width (m) | Net Area (m²) | Perimeter (m) | Finish Pattern | Calculation Method | Notes |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- | :--- | :--- |
| `R1` | **STUDIO / LIVING** | LEVEL-01 | 4.60 | 4.10 | **18.86** | 17.40 | Standard / Unspecified | `shoelace_boundary_polygon` | Orthogonal rectangular boundary; internal clear dimensions. |
| `R2` | **BATHROOM** | LEVEL-01 | 2.10 | 1.40 | **2.94** | 7.00 | tile_grid | `shoelace_boundary_polygon` | Orthogonal rectangular boundary; internal clear dimensions. |
| `R3` | **KITCHEN / ENTRY** | LEVEL-01 | 2.40 | 1.40 | **3.36** | 7.60 | Standard / Unspecified | `shoelace_boundary_polygon` | Orthogonal rectangular boundary; internal clear dimensions. |

> **Calculation Conventions**: Net room areas are calculated strictly from internal wall-face boundary vertices using the Shoelace formula. Non-rectangular rooms report `N/A` for length and width to prevent misleading orthogonal simplifications.

---

## 3. Opening Schedules

### 3.1 Door Schedule

| Door ID | Floor | Host Wall | Associated Space(s) | Width (mm) | Height (mm) | Sill (mm) | Swing Geometry | Provenance | Verification |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| `D-ENTR` | LEVEL-01 | `W-EXT-S` | `R3` | 900 | *Unannotated (Null)* | 0 (Flush) | inward-left | `inferred` | `verified` |
| `D-BATH` | LEVEL-01 | `W-INT-H` | `R2`, `R3` | 750 | *Unannotated (Null)* | 0 (Flush) | inward-right | `inferred` | `verified` |

### 3.2 Window Schedule

| Window ID | Floor | Host Wall | Associated Space | Width (mm) | Height (mm) | Sill Height (mm) | Provenance | Verification |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `WIN-1` | LEVEL-01 | `W-EXT-S` | `R1` | 1800 | *Unannotated (Null)* | 900 | `estimated` | `verified` |
| `WIN-2` | LEVEL-01 | `W-EXT-N` | `R2` | 800 | *Unannotated (Null)* | 1400 | `estimated` | `verified` |

> **Notice**: 2D floor plans do not define vertical clearances. Door head heights and window sill heights are stored as `null` and must be confirmed during downstream BIM vertical parameter approval.

---

## 4. Architectural Element Inventory

### 4.1 Summary by Category & Block Definition

| Category | Block Definition ID | Nominal Dimensions (W x D mm) | Instance Count |
| :--- | :--- | :--- | :---: |
| **Furniture** | `FURN_BED_DOUBLE` | Parametric | **1** |
| **Furniture** | `FURN_SOFA_2SEAT` | Parametric | **1** |
| **Kitchen** | `FIXT_KITCHEN_SINK` | Parametric | **1** |
| **Kitchen** | `FIXT_REFRIGERATOR` | Parametric | **1** |
| **Sanitary** | `FIXT_SHOWER` | Parametric | **1** |
| **Sanitary** | `FIXT_TOILET` | Parametric | **1** |
| **Sanitary** | `FIXT_WASHBASIN` | Parametric | **1** |
| **Structural** | `STRUC_COL_SQUARE` | Parametric | **1** |

### 4.2 Itemized Element Instances

| Element ID | Block Definition | Category | Floor | Room | Insertion (X, Y mm) | Rotation | Status |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| `E-BED-1` | `FURN_BED_DOUBLE` | furniture | LEVEL-01 | `R1` | [400, 2600] | 0.0° | `confirmed` |
| `E-SOFA-1` | `FURN_SOFA_2SEAT` | furniture | LEVEL-01 | `R1` | [400, 500] | 0.0° | `approved` |
| `E-WC-1` | `FIXT_TOILET` | sanitary | LEVEL-01 | `R2` | [4500, 4000] | 0.0° | `confirmed` |
| `E-BASIN-1` | `FIXT_WASHBASIN` | sanitary | LEVEL-01 | `R2` | [5100, 4200] | 0.0° | `confirmed` |
| `E-SHOWER-1` | `FIXT_SHOWER` | sanitary | LEVEL-01 | `R2` | [4500, 2800] | 0.0° | `confirmed` |
| `E-SINK-1` | `FIXT_KITCHEN_SINK` | kitchen | LEVEL-01 | `R3` | [4500, 300] | 0.0° | `confirmed` |
| `E-FRIDGE-1` | `FIXT_REFRIGERATOR` | kitchen | LEVEL-01 | `R3` | [5050, 1800] | 0.0° | `confirmed` |
| `E-COL-1` | `STRUC_COL_SQUARE` | structural | LEVEL-01 | `R1` | [4200, 2500] | 0.0° | `confirmed` |

---

## 5. Floor Finish Schedule

| Finish ID | Room Name (ID) | Floor | Pattern | Tile Grid Size (mm) | Physical Material | Covered Area (m²) | Status |
| :--- | :--- | :--- | :--- | :---: | :--- | :---: | :--- |
| `FIN-BATH-1` | BATHROOM (`R2`) | LEVEL-01 | `tile_grid` | 300 | *Unspecified (Hatch Pattern Only)* | **2.94** | `material_unspecified (graphical hatch pattern only)` |

> **Material Disclaimer**: A CAD hatch pattern (`ANSI37`, `NET`, `ANSI31`) is a drafting convention and does not certify physical material specifications without manufacturer submittals.

---

## 6. Uncertainty, Provenance & Verification Audit

| Issue ID | Scope | Target | Status | Confidence | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `U1` | sketch_interpretation | `Bathroom Fixture Clearances` | `confirmed` | `high` | Standard 700mm clearance verified between WC and shower tray. |
| `UNC-VERT-01` | vertical_geometry | `openings.height` | `unresolved (requires downstream approval)` | `low` | 4 door/window vertical heights unannotated in 2D floor plan. |

### 6.1 Integrity Audit Results
- **Host-Wall Validation**: ✅ PASSED (All openings hosted on valid walls)
- **Room Polygon Overlaps**: ✅ PASSED (Zero overlapping room enclosures)
- **Envelope Clearance**: ✅ PASSED (All blocks reside inside exterior footprint)
- **Approval Gate Status**: ✅ APPROVED FOR DRAFTING & HANDOFF

---

## 7. Regulatory & Compliance Notice
This architectural schedule and report has been synthesized automatically from verified 2D CAD vector geometry. Structural load-bearing capacity, shear wall provisions, fire-resistance ratings, egress width calculations, and municipal zoning setbacks remain **UNVERIFIED** and must be reviewed and stamped by a licensed architect or professional engineer prior to construction.