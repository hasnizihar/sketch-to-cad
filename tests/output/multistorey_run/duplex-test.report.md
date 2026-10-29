# Architectural Documentation & Schedules Report

> **Project:** Duplex-Residence-Two-Storey | **Drawing ID:** `duplex-test-level-01`  
> **Approval State:** **STATUS: APPROVED**  
> **Date:** 2026-10-30T00:00:00Z | **Units:** mm (`Cartesian2D_RightHanded_YUp`)  

---

## 1. Executive Architectural Summary

| Parameter | Metric / Value | Calculation & Scope Notes |
| :--- | :--- | :--- |
| **Floors Represented** | 2 Storey | Single-storey ground level (`LEVEL-01`) |
| **Verified Net Area** | **119.36 m²** | Sum of internal clear room polygons (Shoelace formula) |
| **Gross Footprint Area** | 69.60 m² | Exterior bounding box footprint (exterior_envelope_bounding_box) |
| **Room Enclosures** | 6 Rooms | Verified room boundaries with centroids |
| **Door Openings** | 4 Doors | Capped jambs with swing arcs |
| **Window Openings** | 4 Windows | Centerline glazing and jamb cuts |
| **Architectural Blocks** | 9 Instances | Furniture, sanitary fixtures, structure & circulation |
| **Floor Finishes** | 2 Finish Zones | Surface boundaries and graphical tile hatching |
| **Uncertainty Audit** | 2 Items (1 unresolved) | Documented assumptions & unverified 2D heights |
| **Validation Status** | **WARNING** | Architectural rule compliance & integrity |

---

## 2. Room Area & Dimension Schedule

| Room ID | Room Name | Floor | Length (m) | Width (m) | Net Area (m²) | Perimeter (m) | Finish Pattern | Calculation Method | Notes |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- | :--- | :--- |
| `RM-GF-LIV` | **LIVING & DINING** | LEVEL-01 | 7.60 | 4.65 | **35.34** | 24.50 | Standard / Unspecified | `shoelace_boundary_polygon` | Orthogonal rectangular boundary; internal clear dimensions. |
| `RM-GF-KIT` | **KITCHEN** | LEVEL-01 | 3.65 | 3.35 | **12.23** | 14.00 | tile_grid | `shoelace_boundary_polygon` | Orthogonal rectangular boundary; internal clear dimensions. |
| `RM-GF-CIRC` | **STAIR & ENTRY** | LEVEL-01 | 3.65 | 3.35 | **12.23** | 14.00 | Standard / Unspecified | `shoelace_boundary_polygon` | Orthogonal rectangular boundary; internal clear dimensions. |
| `RM-FF-BED1` | **MASTER BEDROOM** | LEVEL-02 | 4.15 | 3.65 | **15.15** | 15.60 | Standard / Unspecified | `shoelace_boundary_polygon` | Orthogonal rectangular boundary; internal clear dimensions. |
| `RM-FF-BED2` | **BEDROOM 2** | LEVEL-02 | 4.15 | 3.65 | **15.15** | 15.60 | Standard / Unspecified | `shoelace_boundary_polygon` | Orthogonal rectangular boundary; internal clear dimensions. |
| `RM-FF-LAND` | **UPPER LANDING** | LEVEL-02 | 7.60 | 3.85 | **29.26** | 22.90 | wood_strip | `shoelace_boundary_polygon` | Orthogonal rectangular boundary; internal clear dimensions. |

> **Calculation Conventions**: Net room areas are calculated strictly from internal wall-face boundary vertices using the Shoelace formula. Non-rectangular rooms report `N/A` for length and width to prevent misleading orthogonal simplifications.

---

## 3. Opening Schedules

### 3.1 Door Schedule

| Door ID | Floor | Host Wall | Associated Space(s) | Width (mm) | Height (mm) | Sill (mm) | Swing Geometry | Provenance | Verification |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| `D-GF-ENT` | LEVEL-01 | `W-GF-EXT-S` | `RM-GF-LIV` | 900 | *Unannotated (Null)* | 0 (Flush) | inward-right | `explicit` | `verified` |
| `D-GF-KIT` | LEVEL-01 | `W-GF-INT-1` | `RM-GF-KIT`, `RM-FF-LAND`, `RM-GF-LIV` | 800 | *Unannotated (Null)* | 0 (Flush) | inward-left | `explicit` | `verified` |
| `D-FF-BED1` | LEVEL-02 | `W-FF-INT-1` | `RM-GF-LIV`, `RM-FF-LAND`, `RM-FF-BED1` | 800 | *Unannotated (Null)* | 0 (Flush) | inward-left | `explicit` | `verified` |
| `D-FF-BED2` | LEVEL-02 | `W-FF-INT-1` | `RM-GF-LIV`, `RM-FF-LAND`, `RM-FF-BED2` | 800 | *Unannotated (Null)* | 0 (Flush) | inward-right | `explicit` | `verified` |

### 3.2 Window Schedule

| Window ID | Floor | Host Wall | Associated Space | Width (mm) | Height (mm) | Sill Height (mm) | Provenance | Verification |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `WIN-GF-LIV` | LEVEL-01 | `W-GF-EXT-S` | `RM-GF-LIV`, `RM-FF-BED1` | 1500 | *Unannotated (Null)* | *Unannotated (Null)* | `explicit` | `verified` |
| `WIN-GF-KIT` | LEVEL-01 | `W-GF-EXT-W` | `RM-GF-KIT`, `RM-FF-LAND` | 1200 | *Unannotated (Null)* | *Unannotated (Null)* | `explicit` | `verified` |
| `WIN-FF-BED1` | LEVEL-02 | `W-FF-EXT-S` | `RM-GF-LIV`, `RM-FF-BED1` | 1500 | *Unannotated (Null)* | *Unannotated (Null)* | `explicit` | `verified` |
| `WIN-FF-BED2` | LEVEL-02 | `W-FF-EXT-S` | `RM-GF-LIV`, `RM-FF-BED2` | 1500 | *Unannotated (Null)* | *Unannotated (Null)* | `explicit` | `verified` |

> **Notice**: 2D floor plans do not define vertical clearances. Door head heights and window sill heights are stored as `null` and must be confirmed during downstream BIM vertical parameter approval.

---

## 4. Architectural Element Inventory

### 4.1 Summary by Category & Block Definition

| Category | Block Definition ID | Nominal Dimensions (W x D mm) | Instance Count |
| :--- | :--- | :--- | :---: |
| **Circulation** | `CIRC_STAIR_STRAIGHT` | Parametric | **2** |
| **Furniture** | `FURN_BED_DOUBLE` | Parametric | **1** |
| **Furniture** | `FURN_BED_SINGLE` | Parametric | **1** |
| **Furniture** | `FURN_DINING_TABLE` | Parametric | **1** |
| **Furniture** | `FURN_SOFA_3SEAT` | Parametric | **1** |
| **Kitchen** | `FIXT_KITCHEN_SINK` | Parametric | **1** |
| **Structural** | `STRUC_COL_SQUARE` | Parametric | **2** |

### 4.2 Itemized Element Instances

| Element ID | Block Definition | Category | Floor | Room | Insertion (X, Y mm) | Rotation | Status |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| `E-GF-SOFA` | `FURN_SOFA_3SEAT` | furniture | LEVEL-01 | `RM-GF-LIV` | [2500, 1200] | 0.0° | `approved` |
| `E-GF-DINING` | `FURN_DINING_TABLE` | furniture | LEVEL-01 | `RM-GF-LIV` | [5500, 2500] | 0.0° | `approved` |
| `E-GF-SINK` | `FIXT_KITCHEN_SINK` | kitchen | LEVEL-01 | `RM-GF-KIT` | [1200, 8200] | 0.0° | `approved` |
| `E-GF-COL` | `STRUC_COL_SQUARE` | structural | LEVEL-01 | `RM-FF-LAND` | [4000, 5000] | 0.0° | `approved` |
| `E-GF-STAIR` | `CIRC_STAIR_STRAIGHT` | circulation | LEVEL-01 | `RM-GF-CIRC` | [5000, 6000] | 0.0° | `approved` |
| `E-FF-BED1` | `FURN_BED_DOUBLE` | furniture | LEVEL-02 | `RM-GF-LIV` | [2000, 1800] | 0.0° | `approved` |
| `E-FF-BED2` | `FURN_BED_SINGLE` | furniture | LEVEL-02 | `RM-GF-LIV` | [6000, 1800] | 0.0° | `approved` |
| `E-FF-COL` | `STRUC_COL_SQUARE` | structural | LEVEL-02 | `RM-FF-LAND` | [4000, 5000] | 0.0° | `approved` |
| `E-FF-STAIR` | `CIRC_STAIR_STRAIGHT` | circulation | LEVEL-02 | `RM-GF-CIRC` | [5000, 6000] | 0.0° | `approved` |

---

## 5. Floor Finish Schedule

| Finish ID | Room Name (ID) | Floor | Pattern | Tile Grid Size (mm) | Physical Material | Covered Area (m²) | Status |
| :--- | :--- | :--- | :--- | :---: | :--- | :---: | :--- |
| `FIN-GF-KIT` | KITCHEN (`RM-GF-KIT`) | LEVEL-01 | `tile_grid` | 600 | *Unspecified (Hatch Pattern Only)* | **12.23** | `material_unspecified (graphical hatch pattern only)` |
| `FIN-FF-LAND` | UPPER LANDING (`RM-FF-LAND`) | LEVEL-02 | `wood_strip` | 150 | *Unspecified (Hatch Pattern Only)* | **29.26** | `material_unspecified (graphical hatch pattern only)` |

> **Material Disclaimer**: A CAD hatch pattern (`ANSI37`, `NET`, `ANSI31`) is a drafting convention and does not certify physical material specifications without manufacturer submittals.

---

## 6. Uncertainty, Provenance & Verification Audit

| Issue ID | Scope | Target | Status | Confidence | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `U-ELEV-1` | sketch_interpretation | `Storey Elevations` | `confirmed` | `high` | Vertical floor datum and clear storey heights are omitted from 2D floor plans. |
| `UNC-VERT-01` | vertical_geometry | `openings.height` | `unresolved (requires downstream approval)` | `low` | 8 door/window vertical heights unannotated in 2D floor plan. |

### 6.1 Integrity Audit Results
- **Host-Wall Validation**: ✅ PASSED (All openings hosted on valid walls)
- **Room Polygon Overlaps**: ❌ WARNING (Overlapping room enclosures detected)
- **Envelope Clearance**: ✅ PASSED (All blocks reside inside exterior footprint)
- **Approval Gate Status**: ⚠️ DRAFT / NOT APPROVED

---

## 7. Regulatory & Compliance Notice
This architectural schedule and report has been synthesized automatically from verified 2D CAD vector geometry. Structural load-bearing capacity, shear wall provisions, fire-resistance ratings, egress width calculations, and municipal zoning setbacks remain **UNVERIFIED** and must be reviewed and stamped by a licensed architect or professional engineer prior to construction.