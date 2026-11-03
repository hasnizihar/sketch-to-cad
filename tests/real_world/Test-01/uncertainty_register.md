# Uncertainty Register: Real-World Test 01 - Nordic Residential Villa (Revision 03)

**Source File:** `source_sketch.jpg`  
**Source SHA-256:** `12ca802a25cd855467a62473c7c35f423ca01ed53ab3818b61b7b75cf9259957`  
**Revision ID:** `REV-03`  
**Model Revision Hash:** `7cf483c4f2f27282cad5a0662b55b1336de7974a194e28ef5fe83bf8ac46e6cf`  
**Total Uncertainties:** 7 (1 Blocker, 4 Warnings, 2 Informational)  
**Status:** `AWAITING_HUMAN_APPROVAL` (Zero DXF Generated, No Model Approved)  

---

## 1. Uncertainty & Contradiction Summary Table

| ID | Domain | Severity | Source Observation & Measured Coordinates | Technical Analysis & Decision State | Human Decision Required | Status |
| :--- | :--- | :---: | :--- | :--- | :--- | :---: |
| **`UNC-01`** | `dimensions.depth_chain` | 🔴 **BLOCKER** | **West Chain**: `5000` + `14200` = `19200 mm`.<br>**East Chain**: `16000` + `3000` = `19000 mm`.<br>**Difference**: `200 mm`. | **Both original measurements preserved as authentic source truth without automatic alteration.** 19000 mm building datum retained only as a current drafting interpretation with flag note. | **Confirm datum flag note** | **ACTIVE BLOCKER** (Awaiting Final Approval) |
| **`UNC-02`** | `walls.W-INT-MASTER-BATH` | 🟡 **WARNING** | **Source Conflict**: Drawn line at $Y \approx 460\text{ px}$ ($Y = 9200\text{ mm}$, clear area $10.01\text{ m}^2$) vs written text `vannituba 6,5 m²`. | **Alternative 1A retained per human instruction.** Prioritizes drawn wall line and fixture clearances over conflicting handwritten label. Conflict preserved in records. | **Authorized for drafting (1A)** | **Documented Variance** |
| **`UNC-03`** | `walls.W-INT-SAUNA-HORIZ` | 🟡 **WARNING** | **Source Evidence**: Ink row $Y = 241\text{ px}$ ($136\text{ px} : 84\text{ px} = 1.62:1$); written labels $6\text{ m}^2 : 4\text{ m}^2 = 1.50:1$. | **Revised to $Y = 13000\text{ mm}$ per Alternative 2A.** Shower depth $3000\text{ mm}$ (clear $4.70\text{ m}^2$), Sauna depth $2000\text{ mm}$ (clear $3.05\text{ m}^2$). Source-supported interpretation. | **Authorized for drafting (2A)** | **Source-Supported Interpretation** |
| **`UNC-04`** | `rooms.R-CORRIDOR` | 🔵 **INFO** | **Source Layout**: Circulation space open to living room at $Y = 6500\text{ mm}$. No dividing wall. | **Preserved as open circulation space** ($10.65\text{ m}^2$ centerline, $9.87\text{ m}^2$ clear) without artificial separator. | **Confirmed open layout** | **Inferred Circulation** |
| **`UNC-05`** | `walls.thicknesses` | 🟡 **WARNING** | **Source Value**: `None` (unannotated freehand lines). | Proposed drafting defaults: **$200\text{ mm}$ exterior**, **$100\text{ mm}$ interior**, **$150\text{ mm}$ core**. Preliminary defaults. | **Confirm or modify** | **Pending Final Approval** |
| **`UNC-06`** | `openings.widths` | 🟡 **WARNING** | **Source Value**: `None` (unannotated modular cutouts). | Proposed standard modular widths: $600-1800\text{ mm}$ windows, $700-900\text{ mm}$ doors. | **Confirm or modify** | **Pending Final Approval** |
| **`UNC-07`** | `openings.sill_heights` | 🔵 **INFO** | **Source Value**: `None` (2D plan cannot provide vertical elevations). | **Designated UNKNOWN in 2D model.** Excluded from 2D CAD drafting; deferred to downstream 3D BIM integration. | **Review in 3D BIM** | **Deferred to 3D BIM** |

---

## 2. Governance Protocol

- **Approval Gate**: **ENFORCED**.
- **Revision Identifier**: `REV-03`
- **Model Revision Hash**: `7cf483c4f2f27282cad5a0662b55b1336de7974a194e28ef5fe83bf8ac46e6cf`
- **CAD Vector Generation**: **BLOCKED** until final human review and authorization.
