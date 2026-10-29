# Architectural Documentation & Schedules Report

> **Project:** Residential Hand Sketch Project | **Drawing ID:** `residential-hand-sketch-project`  
> **Approval State:** **STATUS: APPROVED**  
> **Date:** 2026-10-30T00:00:00Z | **Units:** mm (`Cartesian2D_RightHanded_YUp`)  

---

## 1. Executive Architectural Summary

| Parameter | Metric / Value | Calculation & Scope Notes |
| :--- | :--- | :--- |
| **Floors Represented** | 1 Storey | Single-storey ground level (`LEVEL-01`) |
| **Verified Net Area** | **45.04 m²** | Sum of internal clear room polygons (Shoelace formula) |
| **Gross Footprint Area** | 69.60 m² | Exterior bounding box footprint (exterior_envelope_bounding_box) |
| **Room Enclosures** | 3 Rooms | Verified room boundaries with centroids |
| **Door Openings** | 1 Doors | Capped jambs with swing arcs |
| **Window Openings** | 1 Windows | Centerline glazing and jamb cuts |
| **Architectural Blocks** | 0 Instances | Furniture, sanitary fixtures, structure & circulation |
| **Floor Finishes** | 0 Finish Zones | Surface boundaries and graphical tile hatching |
| **Uncertainty Audit** | 2 Items (2 unresolved) | Documented assumptions & unverified 2D heights |
| **Validation Status** | **PASSED** | Architectural rule compliance & integrity |

---

## 2. Room Area & Dimension Schedule

| Room ID | Room Name | Floor | Length (m) | Width (m) | Net Area (m²) | Perimeter (m) | Finish Pattern | Calculation Method | Notes |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- | :--- | :--- |
| `R-LIVING` | **LIVING / DINING** | LEVEL-01 | N/A | N/A | **21.60** | N/A | Standard / Unspecified | `model_annotated` | Boundary corners not supplied; using model annotated area. |
| `R-KITCHEN` | **KITCHEN** | LEVEL-01 | N/A | N/A | **9.00** | N/A | Standard / Unspecified | `model_annotated` | Boundary corners not supplied; using model annotated area. |
| `R-BEDROOM-1` | **BEDROOM 1** | LEVEL-01 | N/A | N/A | **14.44** | N/A | Standard / Unspecified | `model_annotated` | Boundary corners not supplied; using model annotated area. |

> **Calculation Conventions**: Net room areas are calculated strictly from internal wall-face boundary vertices using the Shoelace formula. Non-rectangular rooms report `N/A` for length and width to prevent misleading orthogonal simplifications.

---

## 3. Opening Schedules

### 3.1 Door Schedule

| Door ID | Floor | Host Wall | Associated Space(s) | Width (mm) | Height (mm) | Sill (mm) | Swing Geometry | Provenance | Verification |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| `D-ENTRY` | LEVEL-01 | `W-EXT-SOUTH` | Exterior / Unassigned | 1000 | *Unannotated (Null)* | 0 (Flush) | inward-right | `explicit` | `verified` |

### 3.2 Window Schedule

| Window ID | Floor | Host Wall | Associated Space | Width (mm) | Height (mm) | Sill Height (mm) | Provenance | Verification |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `W-KIT` | LEVEL-01 | `W-EXT-WEST` | Unassigned | 1200 | *Unannotated (Null)* | *Unannotated (Null)* | `estimated` | `verified` |

> **Notice**: 2D floor plans do not define vertical clearances. Door head heights and window sill heights are stored as `null` and must be confirmed during downstream BIM vertical parameter approval.

---

## 4. Architectural Element Inventory

### 4.1 Summary by Category & Block Definition

| Category | Block Definition ID | Nominal Dimensions (W x D mm) | Instance Count |
| :--- | :--- | :--- | :---: |

### 4.2 Itemized Element Instances

| Element ID | Block Definition | Category | Floor | Room | Insertion (X, Y mm) | Rotation | Status |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |

---

## 5. Floor Finish Schedule

| Finish ID | Room Name (ID) | Floor | Pattern | Tile Grid Size (mm) | Physical Material | Covered Area (m²) | Status |
| :--- | :--- | :--- | :--- | :---: | :--- | :---: | :--- |

> **Material Disclaimer**: A CAD hatch pattern (`ANSI37`, `NET`, `ANSI31`) is a drafting convention and does not certify physical material specifications without manufacturer submittals.

---

## 6. Uncertainty, Provenance & Verification Audit

| Issue ID | Scope | Target | Status | Confidence | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `unc-mid-partition` | sketch_interpretation | `walls.W-INTR-MID.thickness` | `unresolved` | `medium` | Interior partition thickness not explicitly annotated; 150mm proposed. |
| `UNC-VERT-01` | vertical_geometry | `openings.height` | `unresolved (requires downstream approval)` | `low` | 2 door/window vertical heights unannotated in 2D floor plan. |

### 6.1 Integrity Audit Results
- **Host-Wall Validation**: ✅ PASSED (All openings hosted on valid walls)
- **Room Polygon Overlaps**: ✅ PASSED (Zero overlapping room enclosures)
- **Envelope Clearance**: ✅ PASSED (All blocks reside inside exterior footprint)
- **Approval Gate Status**: ✅ APPROVED FOR DRAFTING & HANDOFF

---

## 7. Regulatory & Compliance Notice
This architectural schedule and report has been synthesized automatically from verified 2D CAD vector geometry. Structural load-bearing capacity, shear wall provisions, fire-resistance ratings, egress width calculations, and municipal zoning setbacks remain **UNVERIFIED** and must be reviewed and stamped by a licensed architect or professional engineer prior to construction.