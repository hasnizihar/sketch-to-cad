# Sketch-to-CAD | Test 01: Controlled Model Revision & Approval Package Regeneration Report
**Document ID:** `TEST-01-REVISION-AND-APPROVAL-REPORT`  
**Date:** November 3, 2026  
**Project:** Sketch-to-CAD (Real-World Test 01 — Nordic Residential Villa)  
**Revision Identifier:** `REV-03`  
**Source Image:** [`source_sketch.jpg`](file:///d:/Agent%20Skills/sketch-to-cad-main/tests/real_world/Test-01/source_sketch.jpg) ($845 \times 1024\text{ px}$, SHA-256: `12ca802a25cd855467a62473c7c35f423ca01ed53ab3818b61b7b75cf9259957`)  
**New Model Geometry Revision Hash:** `7cf483c4f2f27282cad5a0662b55b1336de7974a194e28ef5fe83bf8ac46e6cf`  
**Gate Status:** `AWAITING_HUMAN_APPROVAL` (Strictly Enforced, Zero DXF Generated, No BIM Generated)  

---

## 1. Explicit Authorized Decisions Applied

In accordance with human reviewer directives, the following controlled architectural revisions were applied to the draft model:

| Decision Domain | Choice / Action Applied | Evidence & Architectural Rationale |
| :--- | :---: | :--- |
| **Bathroom Partition** | **Alternative 1A** (Retain $Y = 9200\text{ mm}$) | Retained drawn wall line (`W-INT-MASTER-BATH`) at $Y = 9200\text{ mm}$ prioritizing visible ink stroke ($Y \approx 460\text{ px}$), bathtub fixture length ($1550\text{ mm}$), and door clearance over conflicting handwritten `$6,5\text{ m}^2$` label. Original label preserved; discrepancy documented as an unresolved source conflict. |
| **Shower / Sauna Partition** | **Alternative 2A** (Revise to $Y = 13000\text{ mm}$) | Relocated `W-INT-SAUNA-HORIZ` from arbitrary midpoint ($Y = 13500\text{ mm}$) to $Y = 13000\text{ mm}$. Directly supported by visible ink row ($Y = 241\text{ px}$, ratio $136 : 84 = 1.62:1$) and written area labels ($6.0\text{ m}^2 : 4.0\text{ m}^2 = 1.50:1$). Preserved as a source-supported interpretation. |
| **Opening Host Realignment** | Realiged `D-SAUN` & `W-MASTER-BED` | `D-SAUN` moved to $[900.0, 13000.0]$ to lie on revised host wall. `W-MASTER-BED` centered to $[5000.0, 10100.0]$ to lie on exterior wall `W-EXT-WEST-MAIN` ($Y \in [9200, 11000]$) facing terrace, fixing former erroneous coordinate ($Y = 11400$). |
| **Dimensional Discrepancy** | **`UNC-01` Preserved as Active Blocker** | Both original callouts ($14200\text{ mm}$ and $16000 + 3000 = 19000\text{ mm}$) preserved. No automatic alteration to $14000\text{ mm}$ or $19200\text{ mm}$. $19000\text{ mm}$ building datum retained strictly as drafting interpretation with sheet flag note. |
| **Central Corridor** | **Preserved as Open Circulation** | Maintained as an open circulation space ($10.65\text{ m}^2$ centerline, $9.87\text{ m}^2$ clear) open to living room at $Y = 6500\text{ mm}$ without artificial divider. |

---

## 2. Changed Model Entities and Coordinates

| Entity Type | Entity ID | Revision Status | Previous Coordinate / Property | Revised Coordinate / Property (`REV-03`) | Architectural Role |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **Interior Wall** | `W-INT-SAUNA-HORIZ` | **REVISED** | `start: [0, 13500]`, `end: [1800, 13500]` | `start: [0, 13000]`, `end: [1800, 13000]` | Dividing wall between Dušš and Saun |
| **Door Opening** | `D-SAUN` | **REVISED** | `center: [900, 13500]` | `center: [900, 13000]` | Sauna exit door swinging out into Shower |
| **Window Opening** | `W-MASTER-BED` | **REVISED** | `center: [5000, 11400]` *(off host wall)* | `center: [5000, 10100]` *(on W-EXT-WEST-MAIN)* | Master bedroom exterior window facing terrace |
| **Room Definition** | `R-DUSS` | **REVISED** | `labelPosition: [900, 14750]`, `area: 4.5` | `labelPosition: [900, 14500]`, `area: 5.4` | Shower room spatial centroid & nominal area |
| **Room Definition** | `R-SAUN` | **REVISED** | `labelPosition: [900, 12250]`, `area: 4.5` | `labelPosition: [900, 12000]`, `area: 3.6` | Sauna room spatial centroid & nominal area |
| **Interior Wall** | `W-INT-MASTER-BATH` | **RETAINED** | `start: [5000, 9200]`, `end: [9000, 9200]` | `start: [5000, 9200]`, `end: [9000, 9200]` | Master bedroom / Bathroom partition (1A) |

---

## 3. Room Area Comparison (Before vs. After Revision 03)

The table below documents room areas, distinguishing between **nominal centerline grid areas**, **clear inside face areas**, and the author's **handwritten area labels**:

| Room ID | Room Name | Handwritten Label | REV-02 Centerline | REV-02 Clear Area | REV-03 Centerline | REV-03 Clear Area | Delta (REV-03 Clear vs. Label) | Interpretation Provenance |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `R-DUSS` | Dušš (Shower) | **$6.0\text{ m}^2$** | $4.50\text{ m}^2$ | $3.88\text{ m}^2$ | **$5.40\text{ m}^2$** | **$4.70\text{ m}^2$** | $-1.30\text{ m}^2$ | Source-Supported Split (Alternative 2A) |
| `R-SAUN` | Saun (Sauna) | **$4.0\text{ m}^2$** | $4.50\text{ m}^2$ | $3.88\text{ m}^2$ | **$3.60\text{ m}^2$** | **$3.05\text{ m}^2$** | $-0.95\text{ m}^2$ | Source-Supported Split (Alternative 2A) |
| `R-SAUNA-PUHKE`| Sauna Lounge | **$15.0\text{ m}^2$** | $16.00\text{ m}^2$ | $14.76\text{ m}^2$ | **$16.00\text{ m}^2$** | **$14.76\text{ m}^2$** | $-0.24\text{ m}^2$ | Directly Observable Boundaries |
| `R-MAJAPIDAMIS`| Utility / Laundry | **$6.0\text{ m}^2$** | $6.24\text{ m}^2$ | $5.57\text{ m}^2$ | **$6.24\text{ m}^2$** | **$5.57\text{ m}^2$** | $-0.43\text{ m}^2$ | Directly Observable Boundaries |
| `R-TEH` | Technical Room | **$5.0\text{ m}^2$** | $4.80\text{ m}^2$ | $4.27\text{ m}^2$ | **$4.80\text{ m}^2$** | **$4.27\text{ m}^2$** | $-0.73\text{ m}^2$ | Directly Observable Boundaries |
| `R-WC` | Guest Toilet | **$2.4\text{ m}^2$** | $2.16\text{ m}^2$ | $1.80\text{ m}^2$ | **$2.16\text{ m}^2$** | **$1.80\text{ m}^2$** | $-0.60\text{ m}^2$ | Directly Observable Boundaries |
| `R-BED-1` | Bedroom 1 (NE) | **$12.0\text{ m}^2$** | $13.50\text{ m}^2$ | $12.40\text{ m}^2$ | **$13.50\text{ m}^2$** | **$12.40\text{ m}^2$** | $+0.40\text{ m}^2$ | Observable (Wardrobe unmodeled) |
| `R-BED-2` | Bedroom 2 (E) | **$12.0\text{ m}^2$** | $14.40\text{ m}^2$ | $13.48\text{ m}^2$ | **$14.40\text{ m}^2$** | **$13.48\text{ m}^2$** | $+1.48\text{ m}^2$ | Observable (Wardrobe unmodeled) |
| `R-ESIK` | Entry Vestibule | **$12.8\text{ m}^2$** | $14.85\text{ m}^2$ | $13.92\text{ m}^2$ | **$14.85\text{ m}^2$** | **$13.92\text{ m}^2$** | $+1.12\text{ m}^2$ | Observable (Wardrobe unmodeled) |
| `R-MASTER-BED` | Master Bedroom | **$17.6\text{ m}^2$** | $17.60\text{ m}^2$ | $16.55\text{ m}^2$ | **$17.60\text{ m}^2$** | **$16.55\text{ m}^2$** | $-1.05\text{ m}^2$ | Alternative 1A (Conflict Recorded) |
| `R-BATHROOM` | Main Bathroom | **$6.5\text{ m}^2$** | $10.80\text{ m}^2$ | $10.01\text{ m}^2$ | **$10.80\text{ m}^2$** | **$10.01\text{ m}^2$** | $+3.51\text{ m}^2$ | Alternative 1A (Conflict Recorded) |
| `R-LIVING-KITCHEN`| Living & Kitchen | **$65.0\text{ m}^2$** | $65.00\text{ m}^2$ | $62.23\text{ m}^2$ | **$65.00\text{ m}^2$** | **$62.23\text{ m}^2$** | $-2.77\text{ m}^2$ | Directly Observable Boundaries |
| `R-CORRIDOR` | Central Hallway | *(open)* | $10.65\text{ m}^2$ | $9.87\text{ m}^2$ | **$10.65\text{ m}^2$** | **$9.87\text{ m}^2$** | *(est. 10.5)* | Inferred Open Circulation Space |
| **Totals** | **12 Labeled Rooms** | **$164.30\text{ m}^2$** | **$174.35\text{ m}^2$** | **$162.76\text{ m}^2$** | **$174.35\text{ m}^2$** | **$162.76\text{ m}^2$** | — | **Gross Envelope Unchanged** |
| **Totals + Hall** | **All 13 Spaces** | — | **$185.00\text{ m}^2$** | **$172.63\text{ m}^2$** | **$185.00\text{ m}^2$** | **$172.63\text{ m}^2$** | — | **Exact Centerline Conservation** |

---

## 4. Geometry and Area Validation Results

### 4.1 Categorized Area Breakdown
To eliminate mathematical ambiguity, areas are rigorously distinguished by architectural category:
1. **Gross Enclosed Footprint (Shoelace):** **$185.0000\text{ m}^2$**
   - Sauna Wing ($5.0 \times 5.0\text{ m}$): $25.00\text{ m}^2$
   - Main House Body ($10.0 \times 16.0\text{ m}$): $160.00\text{ m}^2$
   - Total Gross Bounding Box: $15.0 \times 16.0\text{ m} = \mathbf{240.00\text{ m}^2}$
2. **Exterior Wall Physical Footprint ($200\text{ mm}$ thickness):** **$12.24\text{ m}^2$**
   - $P \cdot T - 4 \cdot T^2 = (62.00 \times 0.20) - (4 \times 0.04) = 12.40 - 0.16 = \mathbf{12.24\text{ m}^2}$
3. **Clear Enclosed Space Inside Exterior Envelope:** **$172.76\text{ m}^2$**
   - $185.00\text{ m}^2 - 12.24\text{ m}^2 = \mathbf{172.76\text{ m}^2}$
4. **Interior Partition Footprint ($100 - 150\text{ mm}$ thickness, $60.2\text{ m}$ linear run):** **$\approx 6.27\text{ m}^2$**
5. **True Net Internal Usable Floor Area:** **$\approx 166.49\text{ m}^2$**
   - $172.76\text{ m}^2 - 6.27\text{ m}^2 = \mathbf{166.49\text{ m}^2}$ (corroborating the sum of handwritten labels $164.30\text{ m}^2$)
6. **Individual Clear Room Sum:** **$162.76\text{ m}^2$** (12 rooms) $+ 9.87\text{ m}^2$ (corridor) $= \mathbf{172.63\text{ m}^2}$

### 4.2 Topological & Structural Validation
- **Exterior Loop Closure:** All 7 exterior wall segments form a continuously closed planar boundary (0 gaps, 0 self-intersections).
- **Interior Partition Connectivity:** All 13 interior partition walls connect cleanly at both ends to either exterior walls or intersecting partitions (0 dangling or orphaned segments).
- **Opening Host Collinearity:** **25/25 openings (100%)** are verified to lie collinearly and strictly within their respective host walls.
- **Door Clearance & Swing Validation:**
  - `D-SAUN` ($700\text{ mm}$, swing outward-right into Shower) verified clear of fixtures and walls at revised coordinate $[900.0, 13000.0]$.
  - `D-DUSS` ($700\text{ mm}$, swing inward-left into Shower) verified clear at $[1800.0, 14500.0]$.
  - `D-BATHROOM` ($800\text{ mm}$, swing inward-right) verified clear of bathtub contour at $[9000.0, 7200.0]$.
  - `W-MASTER-BED` ($1200\text{ mm}$) verified hosted on exterior wall `W-EXT-WEST-MAIN` at $[5000.0, 10100.0]$.

---

## 5. Source Evidence Traceability & Revision History

| Revision | Action | Reviewer | Key Changes & Rationale | Geometry Hash |
| :---: | :--- | :--- | :--- | :---: |
| **REV-01** | Initial Automated Interpretation | AI Vision Pipeline | Initial automated extraction; forced 14200 to 14000 mm; 900 mm default sills. | `f28d8ec...` |
| **REV-02** | Forensic Human Audit | Antigravity / User | Retained 14200 mm; removed 2D sill default; unverified defaults logged. | `32e311e...` |
| **REV-03** | Controlled Model Revision | Antigravity / User | Retained Bathroom at $Y=9200\text{ mm}$ (1A, conflict logged); revised Sauna/Shower to $Y=13000\text{ mm}$ (2A, source-supported); UNC-01 active; corridor open. | **`7cf483c4f2f2...`** |

---

## 6. Uncertainty Register (`REV-03`)

| ID | Domain | Severity | Current Status | Governance Directive |
| :---: | :--- | :---: | :---: | :--- |
| **`UNC-01`** | `dimensions.depth_chain` | 🔴 **BLOCKER** | **UNRESOLVED** | $14200\text{ mm}$ callout preserved; $19000\text{ mm}$ building datum retained as drafting interpretation with sheet flag note. |
| **`UNC-02`** | `walls.W-INT-MASTER-BATH` | 🟡 **WARNING** | **DOCUMENTED VARIANCE** | Alternative 1A retained for drafting ($Y=9200\text{ mm}$); conflict with $6.5\text{ m}^2$ label recorded. |
| **`UNC-03`** | `walls.W-INT-SAUNA-HORIZ` | 🟡 **WARNING** | **SOURCE-SUPPORTED** | Alternative 2A ($Y=13000\text{ mm}$) applied per $1.62:1$ pixel ratio and $6/4\text{ m}^2$ area labels. |
| **`UNC-04`** | `rooms.R-CORRIDOR` | 🔵 **INFO** | **INFERRED SPACE** | Preserved as open circulation space ($9.87\text{ m}^2$ clear) open to living room. |
| **`UNC-05`** | `walls.thicknesses` | 🟡 **WARNING** | **PROPOSED DEFAULT** | $200\text{ mm}$ exterior, $100\text{ mm}$ interior, $150\text{ mm}$ core (Unverified). |
| **`UNC-06`** | `openings.widths` | 🟡 **WARNING** | **PROPOSED DEFAULT** | Modular $600-1800\text{ mm}$ windows, $700-900\text{ mm}$ doors (Unverified). |
| **`UNC-07`** | `openings.sill_heights` | 🔵 **INFO** | **UNKNOWN in 2D** | Excluded from 2D model; deferred to downstream 3D BIM review. |

---

## 7. Approval Package Hash & Governance State

- **Approval Package File:** [`approval_package.json`](file:///d:/Agent%20Skills/sketch-to-cad-main/tests/real_world/Test-01/approval_package.json)
- **Model Revision Hash (SHA-256):**  
  `7cf483c4f2f27282cad5a0662b55b1336de7974a194e28ef5fe83bf8ac46e6cf`
- **Package Status:** `awaiting_approval`
- **Review Status:** `None`
- **Approval Gate:** `Enforced (cad_generation_blocked = True)`
- **Self-Approval Check:** AI self-approval strictly prevented.

---

## 8. Test and Validator Execution Results

1. **Python Automated Test Suite:**
   - **Command:** `python -m unittest discover tests`
   - **Result:** **240 passed, 0 failed** in 2.172s (`OK`).
2. **Skill Integrity Validator:**
   - **Command:** `powershell -ExecutionPolicy Bypass -File scripts/validate-skill.ps1`
   - **Result:** **19 passed, 0 failed** (Validation Summary: 19 PASSED, 0 FAILED).
3. **JSON Schema Validations:**
   - `floor-plan-model.json`: **PASSED (0 errors)**
   - `approval-package.schema.json`: **PASSED (0 errors)**
   - `observations.schema.json`: **PASSED (0 errors)**

---

## 9. Explicit Confirmation: Zero DXF Generated

> [!IMPORTANT]
> **Explicit Confirmation:**  
> In strict accordance with the mandatory stop condition, **NO DXF FILE HAS BEEN GENERATED**, and **NO DOWNSTREAM 3D BIM BUILD HAS BEEN INITIATED**.  
> The system has halted at the `AWAITING_HUMAN_APPROVAL` checkpoint.

---

## 10. Summary for Human Review & Authorization Request

The draft model has been updated with your authorized revisions:
- The bathroom partition remains at $Y = 9200\text{ mm}$ (Alternative 1A) with the area label conflict recorded.
- The shower/sauna partition is updated to $Y = 13000\text{ mm}$ (Alternative 2A) with room areas and door placement reconciled.
- The window `W-MASTER-BED` has been corrected to lie on the exterior wall facing the terrace ($Y = 10100\text{ mm}$).
- Blocker `UNC-01` remains active and unresolved.
- The central corridor remains open without a separating wall.

**The regenerated approval package is now ready for your final review.** Please provide explicit authorization when you are ready to proceed to CAD vector generation.

