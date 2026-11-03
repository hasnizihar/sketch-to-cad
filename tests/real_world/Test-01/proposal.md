# Architectural Floor Plan Proposal: Real-World Test 01 - Nordic Residential Villa

> **Model Revision:** `646c0d8b8c9a` | **Status:** `AWAITING_APPROVAL` | **Source:** `source_sketch.jpg`

## 1. Footprint & Envelope Summary

- **Overall Width:** 15000 mm
- **Overall Depth:** 16000 mm
- **Gross Footprint Area:** 240.00 m²
- **Levels Count:** 1
- **Total Rooms:** 13
- **Total Walls:** 22 (22 segments)
- **Total Openings:** 25 doors & windows

## 2. Extracted Dimensions & Provenance

| Dimension ID | Source Text | Value (mm) | Category | Target |
| :--- | :--- | :--- | :--- | :--- |
| `DIM-TOP-1` | `5000` | 5000 mm | `explicit` | overall_width |
| `DIM-TOP-2` | `10000` | 10000 mm | `explicit` | overall_width |
| `DIM-RIGHT-1` | `16000` | 16000 mm | `explicit` | overall_depth |
| `DIM-RIGHT-2` | `3000` | 3000 mm | `explicit` | overall_depth |
| `DIM-LEFT-1` | `5000` | 5000 mm | `explicit` | overall_depth |
| `DIM-LEFT-2` | `14200` | 14200 mm | `explicit` | overall_depth |

## 3. Detected Conflicts & Critical Uncertainties

- 🔴 **BLOCKER**: Active Blocker: Arithmetic conflict between West dimension chain (5000 + 14200 = 19200 mm) and East dimension chain (16000 + 3000 = 19000 mm). Retaining 19000 mm building datum only as drafting interpretation. *(Type: `arithmetic_mismatch`)*
- 🔴 **BLOCKER**: Source contradiction: Drawn wall line at Y=9200 mm (10.01 m² clear) vs handwritten 6.5 m² label. Alternative 1A retained for drafting. *(Type: `arithmetic_mismatch`)*

## 4. Unannotated Information & Defaults

- `walls.W-INT-SAUNA-HORIZ`: Source-supported split: Revised to Y=13000 mm per pixel ratio (1.62:1) and area labels (6m²/4m²). Recalculated clear: Shower 4.70 m², Sauna 3.05 m². *(Default: `Standard Residential Practice`)*
- `rooms.R-CORRIDOR`: Open circulation space: 10.65 m² centerline, open to living room at Y=6500 mm. No separating wall. *(Default: `Standard Residential Practice`)*
- `walls.thicknesses`: Wall thicknesses unannotated on sketch. Proposed drafting defaults: 200 mm exterior, 100 mm interior, 150 mm core. *(Default: `Standard Residential Practice`)*
- `openings.widths`: Modular opening widths: 600-1800 mm windows, 700-900 mm doors. *(Default: `Standard Residential Practice`)*
- `openings.sill_heights`: Window sill heights unannotated in 2D. Designated UNKNOWN in 2D model. *(Default: `Standard Residential Practice`)*

## 5. Required Approval Actions

### Action 1: Conflict detected on 'dimensions.depth_chain': Active Blocker: Arithmetic conflict between West dimension chain (5000 + 14200 = 19200 mm) and East dimension chain (16000 + 3000 = 19000 mm). Retaining 19000 mm building datum only as drafting interpretation.. Which value should be prioritized?
- **Options:** Prioritize overall building envelope, Prioritize room dimensions chain, Input custom dimension
- **Current Status:** `pending`

### Action 2: Conflict detected on 'walls.W-INT-MASTER-BATH': Source contradiction: Drawn wall line at Y=9200 mm (10.01 m² clear) vs handwritten 6.5 m² label. Alternative 1A retained for drafting.. Which value should be prioritized?
- **Options:** Prioritize overall building envelope, Prioritize room dimensions chain, Input custom dimension
- **Current Status:** `pending`

---

### How to Approve or Correct (Headless Protocol)

To approve this proposal, execute the approval command with a verified human reviewer name:
```json
{"reviewer_name": "Dr. Aris Thorne, Licensed Architect", "action": "approve", "details": {"notes": "Approved as drafted."}}
```
*Notice: Reviewer identities are recorded as unverified assertions. AI agents are strictly prohibited from self-approving.*