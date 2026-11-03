"""
Apply controlled Revision 03 to Test-01 Model:
1. Bathroom partition: Alternative 1A (retain Y=9200 mm, preserve 6.5 m² label, record conflict)
2. Shower/sauna partition: Alternative 2A (revise W-INT-SAUNA-HORIZ to Y=13000 mm, update D-SAUN center to [900, 13000], update room areas)
3. UNC-01: Active unresolved blocker (preserve 14200 and 16000+3000 mm, retain 19000 mm datum only as drafting interpretation)
4. Corridor: Retain as open circulation space (no separating wall)
5. Preserve evidence classification and uncertainty register
6. Recompute revision hash and regenerate approval package
"""

import sys
import json
import hashlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from jsonschema import validate
from scripts.approval_package import create_approval_package, generate_proposal_markdown, calculate_geometry_hash
from scripts.sketch_interpreter import validate_observations

TEST_DIR = REPO_ROOT / "tests" / "real_world" / "Test-01"

# 1. Update extracted_observations.json
with open(TEST_DIR / "extracted_observations.json", "r", encoding="utf-8") as f:
    obs = json.load(f)

# Update revision history
if "revision_history" not in obs:
    obs["revision_history"] = []

obs["revision_history"].append({
    "timestamp": "2026-11-03T20:05:00Z",
    "reviewer": "Human Reviewer / Antigravity Agent",
    "action": "controlled_model_revision_rev03",
    "reason": (
        "Applied authorized drafting decisions: "
        "(1) Bathroom partition retained at Y=9200 mm (Alternative 1A) prioritizing drawn ink line over conflicting 6.5 m² label; "
        "(2) Shower/sauna partition revised to Y=13000 mm (Alternative 2A) per 136px/84px pixel ratio and 6m²/4m² labels; "
        "(3) UNC-01 preserved as active unresolved blocker with 19000 mm building datum retained only as drafting interpretation; "
        "(4) Corridor preserved as open circulation space."
    )
})

# Update wall observation for W-INT-SAUNA-HORIZ to document model interpretation
for w in obs["walls"]:
    if w["id"] == "W-INT-SAUNA-HORIZ":
        w["model_placement_interpretation"] = "Y = 13000 mm (Alternative 2A: source-supported split based on Y=240 px ink row and 6m²/4m² area labels)"
        w["provenance"] = "source_supported_interpretation"

# Update uncertainties in observations
obs["uncertainties"] = [
    {
        "id": "UNC-01",
        "field": "dimensions.depth_chain_arithmetic",
        "description": (
            "Arithmetic conflict between West dimension chain (5000 + 14200 = 19200 mm) and East dimension chain "
            "(16000 + 3000 = 19000 mm). Difference is 200 mm. Both original measurements are preserved. "
            "Building datum 19000 mm is retained only as a current drafting interpretation; the discrepancy remains an active unresolved blocker."
        ),
        "severity": "blocker",
        "suggested_action": "Seek author/client clarification or verify on site. Document as variance on drawing sheet.",
        "conflicting_values": [
            "19200 mm (West side: 5000 mm sauna wing + 14200 mm terrace run)",
            "19000 mm (East side: 16000 mm main house + 3000 mm terrace)"
        ]
    },
    {
        "id": "UNC-02",
        "field": "walls.W-INT-MASTER-BATH_position",
        "description": (
            "Bathroom partition source contradiction: Visible ink line is drawn at Y ≈ 460 px (yielding Y = 9200 mm, "
            "clear area 10.01 m²), whereas written text annotation specifies 'vannituba 6,5 m²'. "
            "Drafting interpretation Alternative 1A retained per human instruction; conflict preserved in records."
        ),
        "severity": "warning",
        "suggested_action": "Retain Y=9200 mm for drafting to accommodate bathtub and door clearances; record label conflict.",
        "conflicting_values": [
            "10.01 m² clear area (from drawn partition line at Y=9200 mm)",
            "6.5 m² (from handwritten room text label)"
        ]
    },
    {
        "id": "UNC-03",
        "field": "walls.W-INT-SAUNA-HORIZ_position",
        "description": (
            "Shower / Sauna partition placement: Revised to Y ≈ 13000 mm per Alternative 2A, providing a 3.0m deep shower "
            "(clear 4.70 m²) and 2.0m deep sauna (clear 3.05 m²). This is supported by drawn pixel ratio (136 px : 84 px = 1.62:1) "
            "and written labels (6 m² : 4 m² = 1.50:1), but remains an interpreted coordinate rather than an explicit dimension."
        ),
        "severity": "warning",
        "suggested_action": "Approved for drafting as source-supported interpretation REV-03.",
        "conflicting_values": [
            "Y = 13000 mm (Alternative 2A: source-supported 3m/2m split)",
            "Y = 13500 mm (Former Alternative 2B: arbitrary 50/50 midpoint)"
        ]
    },
    {
        "id": "UNC-04",
        "field": "rooms.R-CORRIDOR_boundary",
        "description": (
            "Central corridor is an unannotated circulation zone open to the living room at Y = 6500 mm. "
            "No separating wall is drawn. Modeled area (10.65 m² centerline, 9.87 m² clear) is an inferred spatial boundary."
        ),
        "severity": "info",
        "suggested_action": "Preserve as open circulation space without physical divider.",
        "conflicting_values": ["None (unannotated circulation)"]
    },
    {
        "id": "UNC-05",
        "field": "walls.interior_thickness",
        "description": (
            "Wall thicknesses unannotated on sketch. Proposed drafting defaults: 200 mm exterior envelope, "
            "100 mm interior partitions, 150 mm plumbing core / party wall."
        ),
        "severity": "warning",
        "suggested_action": "Confirm or adjust wall thicknesses prior to final CAD/BIM export.",
        "conflicting_values": ["Proposed: 200mm ext / 100mm int / 150mm core (Unverified)"]
    },
    {
        "id": "UNC-06",
        "field": "openings.window_widths",
        "description": (
            "Opening widths unannotated numerically. Proposed standard modular sizes: 600-1800 mm windows, "
            "700-900 mm doors, 1500/2400 mm patio sliders."
        ),
        "severity": "warning",
        "suggested_action": "Confirm or adjust opening schedules.",
        "conflicting_values": ["Proposed modular opening widths (Unverified)"]
    },
    {
        "id": "UNC-07",
        "field": "openings.window_sill_heights",
        "description": (
            "Window sill heights unannotated on 2D floor plan. Designated UNKNOWN in 2D CAD model; "
            "deferred to downstream 3D BIM integration preflight."
        ),
        "severity": "info",
        "suggested_action": "Review in downstream 3D BIM preflight.",
        "conflicting_values": ["UNKNOWN in 2D"]
    }
]

# Validate updated observations
is_valid, obs_errors = validate_observations(obs)
if not is_valid:
    raise ValueError(f"Observations schema validation failed: {obs_errors}")
print("Revised observations schema validation: PASSED (0 errors)")

with open(TEST_DIR / "extracted_observations.json", "w", encoding="utf-8") as f:
    json.dump(obs, f, indent=2)

# 2. Update draft_model.json
with open(TEST_DIR / "draft_model.json", "r", encoding="utf-8") as f:
    draft_model = json.load(f)

# Update wall W-INT-SAUNA-HORIZ to Y = 13000.0 mm
for w in draft_model["walls"]:
    if w["id"] == "W-INT-SAUNA-HORIZ":
        w["start"] = [0.0, 13000.0]
        w["end"] = [1800.0, 13000.0]
        w["source"] = "inferred"

# Update opening D-SAUN center to [900.0, 13000.0] and ensure W-MASTER-BED is hosted on W-EXT-WEST-MAIN
for op in draft_model["openings"]:
    if op["id"] == "D-SAUN":
        op["center"] = [900.0, 13000.0]
        op["source"] = "inferred"
    elif op["id"] == "W-MASTER-BED":
        op["center"] = [5000.0, 10100.0]  # Center of master bedroom exterior wall (Y: 9200 to 11000 mm)
        op["source"] = "estimated"

# Update room approximate areas and centroids for R-DUSS and R-SAUN
for r in draft_model["rooms"]:
    if r["id"] == "R-DUSS":
        r["labelPosition"] = [900.0, 14500.0]
        r["approximateArea"] = 5.4  # centerline: 1.8m * 3.0m = 5.4m² (clear 4.70m²)
    elif r["id"] == "R-SAUN":
        r["labelPosition"] = [900.0, 12000.0]
        r["approximateArea"] = 3.6  # centerline: 1.8m * 2.0m = 3.6m² (clear 3.05m²)

# Update uncertainties in draft_model
draft_model["uncertainties"] = [
    {
        "id": "UNC-01",
        "target": "dimensions.depth_chain",
        "description": "Active Blocker: Arithmetic conflict between West dimension chain (5000 + 14200 = 19200 mm) and East dimension chain (16000 + 3000 = 19000 mm). Retaining 19000 mm building datum only as drafting interpretation.",
        "assumedValue": "Unresolved Blocker - Drafting Interpretation 19000 mm Datum",
        "confidence": "low",
        "status": "unresolved"
    },
    {
        "id": "UNC-02",
        "target": "walls.W-INT-MASTER-BATH",
        "description": "Source contradiction: Drawn wall line at Y=9200 mm (10.01 m² clear) vs handwritten 6.5 m² label. Alternative 1A retained for drafting.",
        "assumedValue": "Alternative 1A (Y=9200 mm, Conflict Documented)",
        "confidence": "medium",
        "status": "unresolved"
    },
    {
        "id": "UNC-03",
        "target": "walls.W-INT-SAUNA-HORIZ",
        "description": "Source-supported split: Revised to Y=13000 mm per pixel ratio (1.62:1) and area labels (6m²/4m²). Recalculated clear: Shower 4.70 m², Sauna 3.05 m².",
        "assumedValue": "Alternative 2A (Y=13000 mm, Source-Supported Interpretation)",
        "confidence": "high",
        "status": "unresolved"
    },
    {
        "id": "UNC-04",
        "target": "rooms.R-CORRIDOR",
        "description": "Open circulation space: 10.65 m² centerline, open to living room at Y=6500 mm. No separating wall.",
        "assumedValue": "Open circulation space (Inferred)",
        "confidence": "medium",
        "status": "unresolved"
    },
    {
        "id": "UNC-05",
        "target": "walls.thicknesses",
        "description": "Wall thicknesses unannotated on sketch. Proposed drafting defaults: 200 mm exterior, 100 mm interior, 150 mm core.",
        "assumedValue": "Proposed: 200mm ext / 100mm int / 150mm core (Unverified)",
        "confidence": "medium",
        "status": "unresolved"
    },
    {
        "id": "UNC-06",
        "target": "openings.widths",
        "description": "Modular opening widths: 600-1800 mm windows, 700-900 mm doors.",
        "assumedValue": "Proposed modular opening widths (Unverified)",
        "confidence": "medium",
        "status": "unresolved"
    },
    {
        "id": "UNC-07",
        "target": "openings.sill_heights",
        "description": "Window sill heights unannotated in 2D. Designated UNKNOWN in 2D model.",
        "assumedValue": "UNKNOWN (Not applicable to 2D plan)",
        "confidence": "low",
        "status": "unresolved"
    }
]

# Validate revised draft model against floor-plan-model.json
with open(REPO_ROOT / "skills" / "sketch-to-cad" / "schemas" / "floor-plan-model.json", "r", encoding="utf-8") as f:
    model_schema = json.load(f)
validate(instance=draft_model, schema=model_schema)
print("Revised draft model schema validation: PASSED (0 errors)")

with open(TEST_DIR / "draft_model.json", "w", encoding="utf-8") as f:
    json.dump(draft_model, f, indent=2)

# 3. Re-create approval package and recompute revision hash
new_rev_hash = calculate_geometry_hash(draft_model)
approval_package = create_approval_package(
    draft_model=draft_model,
    observations=obs,
    project_name="Real-World Test 01 - Nordic Residential Villa"
)

# Validate approval package schema
with open(REPO_ROOT / "skills" / "sketch-to-cad" / "schemas" / "approval-package.schema.json", "r", encoding="utf-8") as f:
    app_schema = json.load(f)
validate(instance=approval_package, schema=app_schema)
print(f"Revised approval package schema validation: PASSED (Revision Hash: {approval_package['revision_hash']})")

with open(TEST_DIR / "approval_package.json", "w", encoding="utf-8") as f:
    json.dump(approval_package, f, indent=2)

# 4. Generate revised proposal markdown
proposal_md = generate_proposal_markdown(approval_package)
with open(TEST_DIR / "proposal.md", "w", encoding="utf-8") as f:
    f.write(proposal_md)

# 5. Update uncertainty register JSON and MD
uncertainty_reg = {
    "project": "Real-World Test 01 - Nordic Residential Villa",
    "source_file": "source_sketch.jpg",
    "source_sha256": "12ca802a25cd855467a62473c7c35f423ca01ed53ab3818b61b7b75cf9259957",
    "audit_status": "AWAITING_HUMAN_APPROVAL",
    "revision_id": "REV-03",
    "revision_hash": approval_package["revision_hash"],
    "total_uncertainties": len(obs["uncertainties"]),
    "blocking_count": sum(1 for u in obs["uncertainties"] if u["severity"] == "blocker"),
    "warning_count": sum(1 for u in obs["uncertainties"] if u["severity"] == "warning"),
    "info_count": sum(1 for u in obs["uncertainties"] if u["severity"] == "info"),
    "uncertainties": obs["uncertainties"]
}

with open(TEST_DIR / "uncertainty_register.json", "w", encoding="utf-8") as f:
    json.dump(uncertainty_reg, f, indent=2)

# 6. Update uncertainty register MD
unc_md_content = f"""# Uncertainty Register: Real-World Test 01 - Nordic Residential Villa (Revision 03)

**Source File:** `source_sketch.jpg`  
**Source SHA-256:** `12ca802a25cd855467a62473c7c35f423ca01ed53ab3818b61b7b75cf9259957`  
**Revision ID:** `REV-03`  
**Model Revision Hash:** `{approval_package['revision_hash']}`  
**Total Uncertainties:** 7 (1 Blocker, 4 Warnings, 2 Informational)  
**Status:** `AWAITING_HUMAN_APPROVAL` (Zero DXF Generated, No Model Approved)  

---

## 1. Uncertainty & Contradiction Summary Table

| ID | Domain | Severity | Source Observation & Measured Coordinates | Technical Analysis & Decision State | Human Decision Required | Status |
| :--- | :--- | :---: | :--- | :--- | :--- | :---: |
| **`UNC-01`** | `dimensions.depth_chain` | 🔴 **BLOCKER** | **West Chain**: `5000` + `14200` = `19200 mm`.<br>**East Chain**: `16000` + `3000` = `19000 mm`.<br>**Difference**: `200 mm`. | **Both original measurements preserved as authentic source truth without automatic alteration.** 19000 mm building datum retained only as a current drafting interpretation with flag note. | **Confirm datum flag note** | **ACTIVE BLOCKER** (Awaiting Final Approval) |
| **`UNC-02`** | `walls.W-INT-MASTER-BATH` | 🟡 **WARNING** | **Source Conflict**: Drawn line at $Y \\approx 460\\text{{ px}}$ ($Y = 9200\\text{{ mm}}$, clear area $10.01\\text{{ m}}^2$) vs written text `vannituba 6,5 m²`. | **Alternative 1A retained per human instruction.** Prioritizes drawn wall line and fixture clearances over conflicting handwritten label. Conflict preserved in records. | **Authorized for drafting (1A)** | **Documented Variance** |
| **`UNC-03`** | `walls.W-INT-SAUNA-HORIZ` | 🟡 **WARNING** | **Source Evidence**: Ink row $Y = 241\\text{{ px}}$ ($136\\text{{ px}} : 84\\text{{ px}} = 1.62:1$); written labels $6\\text{{ m}}^2 : 4\\text{{ m}}^2 = 1.50:1$. | **Revised to $Y = 13000\\text{{ mm}}$ per Alternative 2A.** Shower depth $3000\\text{{ mm}}$ (clear $4.70\\text{{ m}}^2$), Sauna depth $2000\\text{{ mm}}$ (clear $3.05\\text{{ m}}^2$). Source-supported interpretation. | **Authorized for drafting (2A)** | **Source-Supported Interpretation** |
| **`UNC-04`** | `rooms.R-CORRIDOR` | 🔵 **INFO** | **Source Layout**: Circulation space open to living room at $Y = 6500\\text{{ mm}}$. No dividing wall. | **Preserved as open circulation space** ($10.65\\text{{ m}}^2$ centerline, $9.87\\text{{ m}}^2$ clear) without artificial separator. | **Confirmed open layout** | **Inferred Circulation** |
| **`UNC-05`** | `walls.thicknesses` | 🟡 **WARNING** | **Source Value**: `None` (unannotated freehand lines). | Proposed drafting defaults: **$200\\text{{ mm}}$ exterior**, **$100\\text{{ mm}}$ interior**, **$150\\text{{ mm}}$ core**. Preliminary defaults. | **Confirm or modify** | **Pending Final Approval** |
| **`UNC-06`** | `openings.widths` | 🟡 **WARNING** | **Source Value**: `None` (unannotated modular cutouts). | Proposed standard modular widths: $600-1800\\text{{ mm}}$ windows, $700-900\\text{{ mm}}$ doors. | **Confirm or modify** | **Pending Final Approval** |
| **`UNC-07`** | `openings.sill_heights` | 🔵 **INFO** | **Source Value**: `None` (2D plan cannot provide vertical elevations). | **Designated UNKNOWN in 2D model.** Excluded from 2D CAD drafting; deferred to downstream 3D BIM integration. | **Review in 3D BIM** | **Deferred to 3D BIM** |

---

## 2. Governance Protocol

- **Approval Gate**: **ENFORCED**.
- **Revision Identifier**: `REV-03`
- **Model Revision Hash**: `{approval_package['revision_hash']}`
- **CAD Vector Generation**: **BLOCKED** until final human review and authorization.
"""

with open(TEST_DIR / "uncertainty_register.md", "w", encoding="utf-8") as f:
    f.write(unc_md_content)

# 7. Update execution_log.json
exec_log = {
    "test_id": "TEST-01",
    "timestamp": "2026-11-03T20:06:00Z",
    "status": "AWAITING_HUMAN_APPROVAL",
    "revision_id": "REV-03",
    "revision_hash": approval_package["revision_hash"],
    "source_image": {
        "file_name": "source_sketch.jpg",
        "sha256": "12ca802a25cd855467a62473c7c35f423ca01ed53ab3818b61b7b75cf9259957",
        "dimensions": "845x1024 px"
    },
    "authorized_decisions_applied": {
        "bathroom_partition": "Alternative 1A (Retain Y=9200 mm; preserve 6.5 m² label; conflict recorded)",
        "shower_sauna_partition": "Alternative 2A (Revised W-INT-SAUNA-HORIZ to Y=13000 mm; D-SAUN at [900, 13000])",
        "unc_01_status": "UNRESOLVED_BLOCKER (Original 14200 mm and 16000+3000 mm preserved; 19000 mm datum drafting interpretation)",
        "corridor_status": "OPEN_CIRCULATION_SPACE (No artificial separator created)"
    },
    "governance": {
        "approval_gate": "ENFORCED",
        "approval_status": "awaiting_approval",
        "cad_generation_blocked": True
    }
}

with open(TEST_DIR / "execution_log.json", "w", encoding="utf-8") as f:
    json.dump(exec_log, f, indent=2)

print(f"Revision 03 package successfully built. New Revision Hash: {approval_package['revision_hash']}")
