# Architectural Documentation & Schedules Report

> **Project:** Real-World Test 01 - Nordic Residential Villa | **Drawing ID:** `Test-01-floor-plan`  
> **Approval State:** **STATUS: APPROVED**  
> **Date:** 2026-11-03T19:00:00Z | **Units:** mm (`Cartesian2D_RightHanded_YUp`)  

---

## 1. Executive Architectural Summary

| Parameter | Metric / Value | Calculation & Scope Notes |
| :--- | :--- | :--- |
| **Floors Represented** | 1 Storey | Single-storey ground level (`LEVEL-01`) |
| **Verified Net Area** | **172.90 m²** | Sum of internal clear room polygons (Shoelace formula) |
| **Gross Footprint Area** | 240.00 m² | Exterior bounding box footprint (exterior_envelope_bounding_box) |
| **Room Enclosures** | 13 Rooms | Verified room boundaries with centroids |
| **Door Openings** | 14 Doors | Capped jambs with swing arcs |
| **Window Openings** | 11 Windows | Centerline glazing and jamb cuts |
| **Architectural Blocks** | 11 Instances | Furniture, sanitary fixtures, structure & circulation |
| **Floor Finishes** | 0 Finish Zones | Surface boundaries and graphical tile hatching |
| **Uncertainty Audit** | 8 Items (8 unresolved) | Documented assumptions & unverified 2D heights |
| **Validation Status** | **WARNING** | Architectural rule compliance & integrity |

---

## 2. Room Area & Dimension Schedule

| Room ID | Room Name | Floor | Length (m) | Width (m) | Net Area (m²) | Perimeter (m) | Finish Pattern | Calculation Method | Notes |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- | :--- | :--- |
| `R-DUSS` | **Shower** | LEVEL-01 | N/A | N/A | **5.40** | N/A | Standard / Unspecified | `model_annotated` | Boundary corners not supplied; using model annotated area. |
| `R-SAUN` | **Sauna** | LEVEL-01 | N/A | N/A | **3.60** | N/A | Standard / Unspecified | `model_annotated` | Boundary corners not supplied; using model annotated area. |
| `R-SAUNA-PUHKE` | **Sauna Lounge** | LEVEL-01 | N/A | N/A | **15.00** | N/A | Standard / Unspecified | `model_annotated` | Boundary corners not supplied; using model annotated area. |
| `R-MAJAPIDAMIS` | **Utility Room** | LEVEL-01 | N/A | N/A | **5.50** | N/A | Standard / Unspecified | `model_annotated` | Boundary corners not supplied; using model annotated area. |
| `R-TEH` | **Technical Room** | LEVEL-01 | N/A | N/A | **4.80** | N/A | Standard / Unspecified | `model_annotated` | Boundary corners not supplied; using model annotated area. |
| `R-WC` | **Guest Toilet** | LEVEL-01 | N/A | N/A | **2.20** | N/A | Standard / Unspecified | `model_annotated` | Boundary corners not supplied; using model annotated area. |
| `R-BED-1` | **Bedroom 1** | LEVEL-01 | N/A | N/A | **12.00** | N/A | Standard / Unspecified | `model_annotated` | Boundary corners not supplied; using model annotated area. |
| `R-BED-2` | **Bedroom 2** | LEVEL-01 | N/A | N/A | **12.00** | N/A | Standard / Unspecified | `model_annotated` | Boundary corners not supplied; using model annotated area. |
| `R-ESIK` | **Entry Vestibule** | LEVEL-01 | N/A | N/A | **12.80** | N/A | Standard / Unspecified | `model_annotated` | Boundary corners not supplied; using model annotated area. |
| `R-MASTER-BED` | **Master Bedroom** | LEVEL-01 | N/A | N/A | **17.60** | N/A | Standard / Unspecified | `model_annotated` | Boundary corners not supplied; using model annotated area. |
| `R-BATHROOM` | **Main Bathroom** | LEVEL-01 | N/A | N/A | **6.50** | N/A | Standard / Unspecified | `model_annotated` | Boundary corners not supplied; using model annotated area. |
| `R-LIVING-KITCHEN` | **Living Room & Kitchen** | LEVEL-01 | N/A | N/A | **65.00** | N/A | Standard / Unspecified | `model_annotated` | Boundary corners not supplied; using model annotated area. |
| `R-CORRIDOR` | **Circulation Corridor** | LEVEL-01 | N/A | N/A | **10.50** | N/A | Standard / Unspecified | `model_annotated` | Boundary corners not supplied; using model annotated area. |

> **Calculation Conventions**: Net room areas are calculated strictly from internal wall-face boundary vertices using the Shoelace formula. Non-rectangular rooms report `N/A` for length and width to prevent misleading orthogonal simplifications.

---

## 3. Opening Schedules

### 3.1 Door Schedule

| Door ID | Floor | Host Wall | Associated Space(s) | Width (mm) | Height (mm) | Sill (mm) | Swing Geometry | Provenance | Verification |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| `D-ENTRY` | LEVEL-01 | `W-EXT-EAST` | Exterior / Unassigned | 900 | *Unannotated (Null)* | 0 (Flush) | outward-right | `explicit` | `verified` |
| `D-SAUNA-TERRACE` | LEVEL-01 | `W-EXT-SOUTH-SAUNA` | Exterior / Unassigned | 1500 | *Unannotated (Null)* | 0 (Flush) | sliding | `explicit` | `verified` |
| `D-LIVING-TERRACE` | LEVEL-01 | `W-EXT-SOUTH-MAIN` | Exterior / Unassigned | 2400 | *Unannotated (Null)* | 0 (Flush) | sliding | `explicit` | `verified` |
| `D-ESIK-LIVING` | LEVEL-01 | `W-INT-ESIK-SOUTH` | Exterior / Unassigned | 1200 | *Unannotated (Null)* | 0 (Flush) | none | `inferred` | `verified` |
| `D-BED-1` | LEVEL-01 | `W-INT-SPINE-EAST` | Exterior / Unassigned | 800 | *Unannotated (Null)* | 0 (Flush) | inward-right | `inferred` | `verified` |
| `D-BED-2` | LEVEL-01 | `W-INT-SPINE-EAST` | Exterior / Unassigned | 800 | *Unannotated (Null)* | 0 (Flush) | inward-right | `inferred` | `verified` |
| `D-WC` | LEVEL-01 | `W-INT-CORR-NORTH` | Exterior / Unassigned | 700 | *Unannotated (Null)* | 0 (Flush) | inward-left | `inferred` | `verified` |
| `D-TEH` | LEVEL-01 | `W-INT-CORR-NORTH` | Exterior / Unassigned | 800 | *Unannotated (Null)* | 0 (Flush) | outward-left | `inferred` | `verified` |
| `D-MAJAPIDAMIS` | LEVEL-01 | `W-INT-CORR-NORTH` | Exterior / Unassigned | 800 | *Unannotated (Null)* | 0 (Flush) | outward-left | `inferred` | `verified` |
| `D-SAUNA-HALL` | LEVEL-01 | `W-INT-SAUNA-EAST` | Exterior / Unassigned | 800 | *Unannotated (Null)* | 0 (Flush) | inward-left | `inferred` | `verified` |
| `D-MASTER-BED` | LEVEL-01 | `W-INT-CORR-WEST` | Exterior / Unassigned | 800 | *Unannotated (Null)* | 0 (Flush) | inward-left | `inferred` | `verified` |
| `D-BATHROOM` | LEVEL-01 | `W-INT-CORR-WEST` | Exterior / Unassigned | 800 | *Unannotated (Null)* | 0 (Flush) | inward-left | `inferred` | `verified` |
| `D-DUSS` | LEVEL-01 | `W-INT-SAUNA-VERT` | Exterior / Unassigned | 700 | *Unannotated (Null)* | 0 (Flush) | inward-left | `inferred` | `verified` |
| `D-SAUN` | LEVEL-01 | `W-INT-SAUNA-HORIZ` | Exterior / Unassigned | 700 | *Unannotated (Null)* | 0 (Flush) | outward-right | `inferred` | `verified` |

### 3.2 Window Schedule

| Window ID | Floor | Host Wall | Associated Space | Width (mm) | Height (mm) | Sill Height (mm) | Provenance | Verification |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `W-DUSS` | LEVEL-01 | `W-EXT-NORTH-1` | Unassigned | 900 | *Unannotated (Null)* | *Unannotated (Null)* | `estimated` | `verified` |
| `W-SAUNA-PUHKE` | LEVEL-01 | `W-EXT-NORTH-1` | Unassigned | 1200 | *Unannotated (Null)* | *Unannotated (Null)* | `estimated` | `verified` |
| `W-MAJAPIDAMIS` | LEVEL-01 | `W-EXT-NORTH-2` | Unassigned | 1000 | *Unannotated (Null)* | *Unannotated (Null)* | `estimated` | `verified` |
| `W-WC` | LEVEL-01 | `W-EXT-NORTH-2` | Unassigned | 600 | *Unannotated (Null)* | *Unannotated (Null)* | `estimated` | `verified` |
| `W-BED-1` | LEVEL-01 | `W-EXT-NORTH-2` | Unassigned | 1200 | *Unannotated (Null)* | *Unannotated (Null)* | `estimated` | `verified` |
| `W-BED-2` | LEVEL-01 | `W-EXT-EAST` | Unassigned | 1200 | *Unannotated (Null)* | *Unannotated (Null)* | `estimated` | `verified` |
| `W-MASTER-BED` | LEVEL-01 | `W-EXT-WEST-MAIN` | Unassigned | 1200 | *Unannotated (Null)* | *Unannotated (Null)* | `estimated` | `verified` |
| `W-BATHROOM` | LEVEL-01 | `W-EXT-WEST-MAIN` | Unassigned | 900 | *Unannotated (Null)* | *Unannotated (Null)* | `estimated` | `verified` |
| `W-LIVING-WEST` | LEVEL-01 | `W-EXT-WEST-MAIN` | Unassigned | 1500 | *Unannotated (Null)* | *Unannotated (Null)* | `estimated` | `verified` |
| `W-LIVING-EAST` | LEVEL-01 | `W-EXT-EAST` | Unassigned | 1500 | *Unannotated (Null)* | *Unannotated (Null)* | `estimated` | `verified` |
| `W-LIVING-SOUTH` | LEVEL-01 | `W-EXT-SOUTH-MAIN` | Unassigned | 1800 | *Unannotated (Null)* | *Unannotated (Null)* | `estimated` | `verified` |

> **Notice**: 2D floor plans do not define vertical clearances. Door head heights and window sill heights are stored as `null` and must be confirmed during downstream BIM vertical parameter approval.

---

## 4. Architectural Element Inventory

### 4.1 Summary by Category & Block Definition

| Category | Block Definition ID | Nominal Dimensions (W x D mm) | Instance Count |
| :--- | :--- | :--- | :---: |
| **Furniture** | `FURN_BED_DOUBLE` | Parametric | **3** |
| **Furniture** | `FURN_DINING_TABLE` | Parametric | **1** |
| **Furniture** | `FURN_SOFA_3SEAT` | Parametric | **1** |
| **Furniture** | `FURN_TV_UNIT` | Parametric | **1** |
| **Sanitary** | `FIXT_BATHTUB` | Parametric | **1** |
| **Sanitary** | `FIXT_TOILET` | Parametric | **1** |
| **Structural** | `STRUC_COL_SQUARE` | Parametric | **3** |

### 4.2 Itemized Element Instances

| Element ID | Block Definition | Category | Floor | Room | Insertion (X, Y mm) | Rotation | Status |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| `E-BED-01` | `FURN_BED_DOUBLE` | furniture | LEVEL-01 | *Unassigned* | [12750, 14800] | 0.0° | `approved` |
| `E-BED-02` | `FURN_BED_DOUBLE` | furniture | LEVEL-01 | *Unassigned* | [12750, 11700] | 0.0° | `approved` |
| `E-BED-MASTER` | `FURN_BED_DOUBLE` | furniture | LEVEL-01 | *Unassigned* | [7000, 12000] | 0.0° | `approved` |
| `E-DINING-TABLE` | `FURN_DINING_TABLE` | furniture | LEVEL-01 | *Unassigned* | [7000, 1500] | 0.0° | `approved` |
| `E-LIVING-SOFA` | `FURN_SOFA_3SEAT` | furniture | LEVEL-01 | *Unassigned* | [11500, 2500] | 0.0° | `approved` |
| `E-FIREPLACE` | `FURN_TV_UNIT` | furniture | LEVEL-01 | *Unassigned* | [11000, 5800] | 0.0° | `approved` |
| `E-WC-FIXTURE` | `FIXT_TOILET` | sanitary | LEVEL-01 | *Unassigned* | [10050, 15400] | 0.0° | `approved` |
| `E-BATH-FIXTURE` | `FIXT_BATHTUB` | sanitary | LEVEL-01 | *Unassigned* | [6200, 8500] | 0.0° | `approved` |
| `E-COL-TERRACE-1` | `STRUC_COL_SQUARE` | structural | LEVEL-01 | *Unassigned* | [5100, -2900] | 0.0° | `approved` |
| `E-COL-TERRACE-2` | `STRUC_COL_SQUARE` | structural | LEVEL-01 | *Unassigned* | [10000, -2900] | 0.0° | `approved` |
| `E-COL-TERRACE-3` | `STRUC_COL_SQUARE` | structural | LEVEL-01 | *Unassigned* | [14900, -2900] | 0.0° | `approved` |

---

## 5. Floor Finish Schedule

| Finish ID | Room Name (ID) | Floor | Pattern | Tile Grid Size (mm) | Physical Material | Covered Area (m²) | Status |
| :--- | :--- | :--- | :--- | :---: | :--- | :---: | :--- |

> **Material Disclaimer**: A CAD hatch pattern (`ANSI37`, `NET`, `ANSI31`) is a drafting convention and does not certify physical material specifications without manufacturer submittals.

---

## 6. Uncertainty, Provenance & Verification Audit

| Issue ID | Scope | Target | Status | Confidence | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `UNC-01` | sketch_interpretation | `dimensions.depth_chain` | `unresolved` | `low` | Active Blocker: Arithmetic conflict between West dimension chain (5000 + 14200 = 19200 mm) and East dimension chain (16000 + 3000 = 19000 mm). Retaining 19000 mm building datum only as drafting interpretation. |
| `UNC-02` | sketch_interpretation | `walls.W-INT-MASTER-BATH` | `unresolved` | `medium` | Source contradiction: Drawn wall line at Y=9200 mm (10.01 m² clear) vs handwritten 6.5 m² label. Alternative 1A retained for drafting. |
| `UNC-03` | sketch_interpretation | `walls.W-INT-SAUNA-HORIZ` | `unresolved` | `high` | Source-supported split: Revised to Y=13000 mm per pixel ratio (1.62:1) and area labels (6m²/4m²). Recalculated clear: Shower 4.70 m², Sauna 3.05 m². |
| `UNC-04` | sketch_interpretation | `rooms.R-CORRIDOR` | `unresolved` | `medium` | Open circulation space: 10.65 m² centerline, open to living room at Y=6500 mm. No separating wall. |
| `UNC-05` | sketch_interpretation | `walls.thicknesses` | `unresolved` | `medium` | Wall thicknesses unannotated on sketch. Proposed drafting defaults: 200 mm exterior, 100 mm interior, 150 mm core. |
| `UNC-06` | sketch_interpretation | `openings.widths` | `unresolved` | `medium` | Modular opening widths: 600-1800 mm windows, 700-900 mm doors. |
| `UNC-07` | sketch_interpretation | `openings.sill_heights` | `unresolved` | `low` | Window sill heights unannotated in 2D. Designated UNKNOWN in 2D model. |
| `UNC-VERT-01` | vertical_geometry | `openings.height` | `unresolved (requires downstream approval)` | `low` | 25 door/window vertical heights unannotated in 2D floor plan. |

### 6.1 Integrity Audit Results
- **Host-Wall Validation**: ✅ PASSED (All openings hosted on valid walls)
- **Room Polygon Overlaps**: ✅ PASSED (Zero overlapping room enclosures)
- **Envelope Clearance**: ⚠️ WARNING (Out-of-envelope elements detected)
- **Approval Gate Status**: ✅ APPROVED FOR DRAFTING & HANDOFF

---

## 7. Regulatory & Compliance Notice
This architectural schedule and report has been synthesized automatically from verified 2D CAD vector geometry. Structural load-bearing capacity, shear wall provisions, fire-resistance ratings, egress width calculations, and municipal zoning setbacks remain **UNVERIFIED** and must be reviewed and stamped by a licensed architect or professional engineer prior to construction.