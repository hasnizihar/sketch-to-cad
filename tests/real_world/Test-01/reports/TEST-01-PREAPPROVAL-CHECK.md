# Real-World Test 01: Final Pre-Approval Consistency Check

**Project:** Sketch-to-CAD Real-World Validation  
**Test Identifier:** `TEST-01`  
**Document:** `TEST-01-PREAPPROVAL-CHECK.md`  
**Execution Phase:** Phase 3 Quality Gate (Pre-Approval Consistency Check)  
**Status:** **`AWAITING_HUMAN_APPROVAL`** (CAD Vector Generation Paused)  
**Model Revision Hash:** `32e311edb076b4191061245d953bd22a6c873755899b6c743127d6e1ec0142c2`  

---

## 1. Executive Summary & Policy Compliance

In accordance with the Human Reviewer's instructions, a comprehensive consistency check was conducted across [`draft_model.json`](file:///d:/Agent%20Skills/sketch-to-cad-main/tests/real_world/Test-01/draft_model.json), [`extracted_observations.json`](file:///d:/Agent%20Skills/sketch-to-cad-main/tests/real_world/Test-01/extracted_observations.json), and [`approval_package.json`](file:///d:/Agent%20Skills/sketch-to-cad-main/tests/real_world/Test-01/approval_package.json).

### Adopted Approval Policy
- **Original Dimensions**: 100% preserved (`5000`, `10000`, `16000`, `3000`, `5000`, `14200` mm).
- **200 mm Discrepancy (`UNC-01`)**: **Active, Unresolved Blocker** (neither Option A nor Option B is chosen automatically).
- **Proposed Defaults**: Wall thicknesses ($200 / 100 / 150\text{ mm}$), door clearances ($700 - 900\text{ mm}$), and window widths ($600 - 1800\text{ mm}$) remain explicitly tagged as **unverified proposals pending human approval**.
- **Window Sill Heights**: Designated **UNKNOWN** in 2D model; deferred to downstream 3D BIM.
- **CAD Drafting Gate**: **BLOCKED** until the human reviewer resolves the dimensional blocker.

---

## 2. Geometry Reconciliation & Discrepancy Resolution

### 2.1 Exterior Wall Count vs. Envelope Polygon (7 Segments vs. 6 Sides)
- **Visual Sketch Shape**: The enclosed building footprint is a **6-sided stepped orthogonal polygon**:
  1. North Edge: $X \in [0, 15000]$ at $Y = 16000\text{ mm}$ (Length $15000\text{ mm}$)
  2. East Edge: $Y \in [0, 16000]$ at $X = 15000\text{ mm}$ (Length $16000\text{ mm}$)
  3. South Edge: $X \in [5000, 15000]$ at $Y = 0\text{ mm}$ (Length $10000\text{ mm}$)
  4. West Edge (Main Body): $Y \in [0, 11000]$ at $X = 5000\text{ mm}$ (Length $11000\text{ mm}$)
  5. South Edge (Sauna Wing): $X \in [0, 5000]$ at $Y = 11000\text{ mm}$ (Length $5000\text{ mm}$)
  6. West Edge (Sauna Wing): $Y \in [11000, 16000]$ at $X = 0\text{ mm}$ (Length $5000\text{ mm}$)
- **Model Entity Structure (7 Wall Entities)**:
  The continuous $15000\text{ mm}$ North edge is represented by two collinear wall entities:
  - `W-EXT-NORTH-1` ($0 \to 5000\text{ mm}$): Exterior wall above Sauna Wing.
  - `W-EXT-NORTH-2` ($5000 \to 15000\text{ mm}$): Exterior wall above Main House Body.
  *Rationale*: Matches the source sketch's top dimension annotations, which explicitly split the North boundary into `5000` mm and `10000` mm segments.
- **Vertex Continuity Verification**:
  Every exterior wall connects to the next with exact floating-point coordinate equality (`match: True` on all 7 vertices), guaranteeing a 100% sealed outer envelope.

### 2.2 Footprint Area Calculation (Bounding Box vs. Actual Polygon)
- **Bounding Box Extents**: $15000\text{ mm} \times 16000\text{ mm} = 240.00\text{ m}^2$.
- **Actual Enclosed Footprint Area**: Calculated via the Shoelace formula on the 6-sided polygon vertices:
  $$\text{Area} = \frac{1}{2} \left| \sum_{i=0}^{n-1} (x_i y_{i+1} - x_{i+1} y_i) \right| = \mathbf{185.00\text{ m}^2}$$
  $$\text{Sauna Wing } (5.0\text{ m} \times 5.0\text{ m} = 25.0\text{ m}^2) + \text{Main House Body } (10.0\text{ m} \times 16.0\text{ m} = 160.0\text{ m}^2) = 185.00\text{ m}^2$$
- **Gross Covered Footprint** (including $10.0\text{ m} \times 3.0\text{ m} = 30.0\text{ m}^2$ South covered terrace): **$215.00\text{ m}^2$**.

### 2.3 Interior Partition Junctions (13 Wall Entities)
Programmatic intersection analysis confirmed that all 13 interior partitions connect cleanly at both endpoints (`start` and `end`) to an exterior perimeter wall or intersecting interior wall:
- `W-INT-SAUNA-VERT`: Connects `W-EXT-SOUTH-SAUNA` to `W-EXT-NORTH-1`.
- `W-INT-SAUNA-HORIZ`: Connects `W-EXT-WEST-SAUNA` to `W-INT-SAUNA-VERT`.
- `W-INT-SAUNA-EAST`: Connects `W-EXT-WEST-MAIN` to `W-EXT-NORTH-1 / W-EXT-NORTH-2`.
- `W-INT-CORR-NORTH`: Connects `W-INT-SAUNA-EAST` to `W-INT-SPINE-EAST`.
- `W-INT-UTIL-1` & `W-INT-UTIL-2`: Connect `W-INT-CORR-NORTH` to `W-EXT-NORTH-2`.
- `W-INT-SPINE-EAST`: Connects `W-INT-ESIK-SOUTH` to `W-EXT-NORTH-2`.
- `W-INT-BED-1-2`, `W-INT-BED-2-ESIK`, `W-INT-ESIK-SOUTH`: Connect `W-INT-SPINE-EAST` to `W-EXT-EAST`.
- `W-INT-CORR-WEST`: Connects `W-INT-BATH-LIVING` to `W-INT-CORR-NORTH`.
- `W-INT-MASTER-BATH` & `W-INT-BATH-LIVING`: Connect `W-EXT-WEST-MAIN` to `W-INT-CORR-WEST`.
- **Result**: Zero unanchored or floating wall segments.

---

## 3. Room Count Reconciliation

The apparent discrepancy between space counts is fully reconciled as follows:

| Space Level | Count | Entities Included | Explanation |
| :--- | :---: | :--- | :--- |
| **Source Sketch Labeled Spaces** | **15** | 12 Rooms + 1 Corridor + 2 Terraces | Every distinct spatial zone with a handwritten label in [`extracted_observations.json`](file:///d:/Agent%20Skills/sketch-to-cad-main/tests/real_world/Test-01/extracted_observations.json). |
| **Internal Conditioned Spaces** | **13** | 12 Conditioned Rooms + 1 Corridor | Modeled in [`draft_model.json`](file:///d:/Agent%20Skills/sketch-to-cad-main/tests/real_world/Test-01/draft_model.json) on layer `A-ANNO-TEXT`. |
| **Conditioned Habitable Rooms** | **12** | Dušš, Saun, Puhkeruum, Majapidamis, TEH, WC, Bed 1, Bed 2, Esik, Master Bed, Vannituba, Elutuba köök | Spaces with explicit written area tags ($162.3\text{ m}^2$ total). |
| **Internal Circulation Spaces** | **1** | `R-CORRIDOR` (Koridor) | Central circulation hallway ($10.5\text{ m}^2$ estimated). |
| **Outdoor Terrace Spaces** | **2** | `R-TERRACE-SOUTH`, `R-TERRACE-WEST` | Modeled as exterior covered/open areas on `A-FLOR-OTLN` and `A-COLS`. Excluded from conditioned floor area. |

### Complete Internal Room Inventory

| Room ID | Estonian Label | Standardized Name | Centroid Coordinate `[X, Y]` (mm) | Annotated Area | Model Area |
| :--- | :--- | :--- | :---: | :---: | :---: |
| `R-DUSS` | `Dušš` | Shower Room | `[900.0, 14750.0]` | $6.0\text{ m}^2$ | $4.50\text{ m}^2$ |
| `R-SAUN` | `Saun` | Sauna Room | `[900.0, 12250.0]` | $4.0\text{ m}^2$ | $4.00\text{ m}^2$ |
| `R-SAUNA-PUHKE` | `Sauna Puhkeruum` | Sauna Lounge | `[3400.0, 13500.0]` | $15.0\text{ m}^2$ | $15.00\text{ m}^2$ |
| `R-MAJAPIDAMIS` | `MAJAPIDAMIS` | Utility / Laundry | `[6300.0, 14800.0]` | $6.0\text{ m}^2$ | $5.50\text{ m}^2$ |
| `R-TEH` | `TEH` | Technical / Boiler | `[8600.0, 14800.0]` | $5.0\text{ m}^2$ | $4.80\text{ m}^2$ |
| `R-WC` | `WC` | Guest Toilet | `[10050.0, 14800.0]` | $2.4\text{ m}^2$ | $2.20\text{ m}^2$ |
| `R-BED-1` | `Magamistuba 1` | Bedroom 1 (Northeast) | `[12750.0, 14500.0]` | $12.0\text{ m}^2$ | $12.00\text{ m}^2$ |
| `R-BED-2` | `Magamistuba 2` | Bedroom 2 (East) | `[12750.0, 11400.0]` | $12.0\text{ m}^2$ | $12.00\text{ m}^2$ |
| `R-ESIK` | `Esik` | Entry Vestibule / Foyer | `[12750.0, 8150.0]` | $12.8\text{ m}^2$ | $12.80\text{ m}^2$ |
| `R-MASTER-BED` | `Magamistuba (Suur)`| Master Bedroom | `[7000.0, 11400.0]` | $17.6\text{ m}^2$ | $17.60\text{ m}^2$ |
| `R-BATHROOM` | `Vannituba` | Main Bathroom | `[7000.0, 7850.0]` | $6.5\text{ m}^2$ | $6.50\text{ m}^2$ |
| `R-LIVING-KITCHEN`| `Elutuba köök` | Open Living & Kitchen | `[10000.0, 3250.0]` | $65.0\text{ m}^2$ | $65.00\text{ m}^2$ |
| `R-CORRIDOR` | `Koridor` | Central Circulation Hall | `[9750.0, 10000.0]` | (unannotated) | $10.50\text{ m}^2$ |
| **Totals** | | **13 Internal Spaces** | | **$162.3\text{ m}^2$** | **$172.40\text{ m}^2$** |

---

## 4. Host-Wall Reference & Opening Relationship Validation

Every door and window entity in `draft_model.json` was validated against the wall graph:
- **Total Openings**: 25 (14 Doors + 11 Windows).
- **Missing / Dangling Host Wall References**: **0**.
- **Centerline Projection**: Every opening center coordinate lies exactly along the linear vector axis of its host wall.

| Opening ID | Type | Host Wall ID | Center `[X, Y]` (mm) | Width (mm) | Swing / Operation |
| :--- | :---: | :--- | :---: | :---: | :---: |
| `D-ENTRY` | door | `W-EXT-EAST` | `[15000.0, 8200.0]` | 900.0 | outward-right |
| `D-SAUNA-TERRACE` | door | `W-EXT-SOUTH-SAUNA` | `[3500.0, 11000.0]` | 1500.0 | sliding |
| `D-LIVING-TERRACE` | door | `W-EXT-SOUTH-MAIN` | `[11500.0, 0.0]` | 2400.0 | sliding |
| `D-ESIK-LIVING` | door | `W-INT-ESIK-SOUTH` | `[11500.0, 6500.0]` | 1200.0 | none (cased opening) |
| `D-BED-1` | door | `W-INT-SPINE-EAST` | `[10500.0, 13800.0]` | 800.0 | inward-right |
| `D-BED-2` | door | `W-INT-SPINE-EAST` | `[10500.0, 10500.0]` | 800.0 | inward-right |
| `D-WC` | door | `W-INT-CORR-NORTH` | `[10000.0, 13600.0]` | 700.0 | inward-left |
| `D-TEH` | door | `W-INT-CORR-NORTH` | `[8600.0, 13600.0]` | 800.0 | outward-left |
| `D-MAJAPIDAMIS` | door | `W-INT-CORR-NORTH` | `[6300.0, 13600.0]` | 800.0 | outward-left |
| `D-SAUNA-HALL` | door | `W-INT-SAUNA-EAST` | `[5000.0, 13800.0]` | 800.0 | inward-left |
| `D-MASTER-BED` | door | `W-INT-CORR-WEST` | `[9000.0, 10000.0]` | 800.0 | inward-left |
| `D-BATHROOM` | door | `W-INT-CORR-WEST` | `[9000.0, 8500.0]` | 800.0 | inward-left |
| `D-DUSS` | door | `W-INT-SAUNA-VERT` | `[1800.0, 14500.0]` | 700.0 | inward-left |
| `D-SAUN` | door | `W-INT-SAUNA-HORIZ` | `[900.0, 13500.0]` | 700.0 | outward-right |
| `W-DUSS` | window | `W-EXT-NORTH-1` | `[900.0, 16000.0]` | 900.0 | fixed/casement |
| `W-SAUNA-PUHKE` | window | `W-EXT-NORTH-1` | `[3400.0, 16000.0]` | 1200.0 | fixed/casement |
| `W-MAJAPIDAMIS` | window | `W-EXT-NORTH-2` | `[6300.0, 16000.0]` | 1000.0 | fixed/casement |
| `W-WC` | window | `W-EXT-NORTH-2` | `[10000.0, 16000.0]` | 600.0 | fixed/casement |
| `W-BED-1` | window | `W-EXT-NORTH-2` | `[12800.0, 16000.0]` | 1200.0 | fixed/casement |
| `W-BED-2` | window | `W-EXT-EAST` | `[15000.0, 11400.0]` | 1200.0 | fixed/casement |
| `W-MASTER-BED` | window | `W-EXT-WEST-MAIN` | `[5000.0, 11400.0]` | 1200.0 | fixed/casement |
| `W-BATHROOM` | window | `W-EXT-WEST-MAIN` | `[5000.0, 7800.0]` | 900.0 | fixed/casement |
| `W-LIVING-WEST` | window | `W-EXT-WEST-MAIN` | `[5000.0, 3200.0]` | 1500.0 | fixed/casement |
| `W-LIVING-EAST` | window | `W-EXT-EAST` | `[15000.0, 3200.0]` | 1500.0 | fixed/casement |
| `W-LIVING-SOUTH`| window | `W-EXT-SOUTH-MAIN` | `[8000.0, 0.0]` | 1800.0 | fixed/casement |

---

## 5. Structured Model Entity Counts Inventory

| Entity Collection | `draft_model.json` Count | `extracted_observations.json` Count | Reconciliation Rationale |
| :--- | :---: | :---: | :--- |
| **Exterior Walls** | 7 | 7 | North wall split into two collinear segments per explicit top dimension callouts. |
| **Interior Partitions** | 13 | 13 | 100% matched across model and observations. |
| **Doors & Openings** | 14 | 14 | 100% matched across model and observations. |
| **Windows** | 11 | 11 | 100% matched across model and observations (verified TEH has no window). |
| **Rooms / Spaces** | 13 | 15 | Model holds 13 internal rooms (12 rooms + corridor); observations track 15 spaces (includes 2 terraces). |
| **Architectural Elements** | 11 | 11 | Fireplace, island, cooktop, dining table, sofa, beds, wardrobes, WC, bathtub, 3 columns. |
| **Explicit Dimensions** | 6 | 6 | `5000`, `10000`, `16000`, `3000`, `5000`, `14200` mm. |
| **Uncertainties** | 5 | 7 | 5 canonical drafting uncertainties in model; 7 forensic visual items in observations. |

---

## 6. Dimensional Blocker Status (`UNC-01`)

```
Left Chain:  5000 mm (Sauna Depth) + 14200 mm (West Terrace Run) = 19200 mm
Right Chain: 16000 mm (House Depth) +  3000 mm (East Terrace Depth) = 19000 mm
Discrepancy: 200 mm
```

### Blocker State: **UNRESOLVED DESIGN DECISION**
- Both measurements are preserved as authentic, source-derived observations.
- Neither Option A ($14000\text{ mm}$ reconciled terrace run) nor Option B ($19200\text{ mm}$ extended depth) is selected automatically.
- **CAD vector drafting will not proceed until the human reviewer provides an explicit dimensional decision.**

---

## 7. Status of Proposed Drafting Values

| Attribute | Source Status | Proposed Value | Approval Status | Note |
| :--- | :---: | :---: | :---: | :--- |
| **Exterior Walls** | Unannotated | $200\text{ mm}$ | **Proposed (Unverified)** | Standard residential envelope |
| **Interior Partitions** | Unannotated | $100\text{ mm}$ | **Proposed (Unverified)** | Standard interior framing |
| **Plumbing Core Wall** | Unannotated | $150\text{ mm}$ | **Proposed (Unverified)** | Wet wall for utility runs |
| **Entrance Door Clear** | Unannotated | $900\text{ mm}$ | **Proposed (Unverified)** | Standard exterior entrance |
| **Internal Room Doors** | Unannotated | $800\text{ mm}$ | **Proposed (Unverified)** | Standard habitable room clear width |
| **Wet Area Doors** | Unannotated | $700\text{ mm}$ | **Proposed (Unverified)** | Standard secondary bathroom clear width |
| **Terrace Sliders** | Unannotated | $1500 / 2400\text{ mm}$ | **Proposed (Unverified)** | Glazed terrace patio sliders |
| **Window Widths** | Unannotated | $600 - 1800\text{ mm}$ | **Proposed (Unverified)** | Modular sizes per room typology |
| **Window Sill Heights** | Unannotated | **UNKNOWN / None** | **Deferred to 3D BIM** | **Excluded from 2D floor plan model** |

---

## 8. Final Approval Readiness

- **Schema Compliance**: All files validate cleanly with `0 errors` against Draft-07 schemas.
- **Model Revision Hash**: `32e311edb076b4191061245d953bd22a6c873755899b6c743127d6e1ec0142c2`.
- **Anti-Self-Approval**: Verified active. The agent cannot self-approve.
- **Execution State**: **PAUSED at Approval Gate**. Zero DXF files have been generated.

