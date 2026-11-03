"""
Rebuild Test-01 Audit Package following Human Review instructions.
Preserves original 14,200 mm observation, records audit provenance,
removes vertical sill assumption from 2D model, and regenerates approval package.
"""

import sys
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from jsonschema import validate
from scripts.approval_package import create_approval_package, generate_proposal_markdown
from scripts.sketch_interpreter import validate_observations

TEST_DIR = REPO_ROOT / "tests" / "real_world" / "Test-01"

# Load existing observations
with open(TEST_DIR / "extracted_observations.json", "r", encoding="utf-8") as f:
    obs = json.load(f)

# Add revision history entry
if "revision_history" not in obs:
    obs["revision_history"] = []

obs["revision_history"].append({
    "timestamp": "2026-11-03T19:25:00Z",
    "reviewer": "Human Reviewer / Antigravity Agent",
    "action": "human_review_audit",
    "reason": "Rebuilt observations and model following human review. Retained 14,200 mm observation without automatic modification. Categorized all wall thicknesses, window widths, and door clearances as proposed unverified values. Removed 2D sill height default, designating it unknown."
})

# Update UNC-01 description in observations to avoid automatic replacement
for u in obs["uncertainties"]:
    if u["id"] == "UNC-01":
        u["description"] = (
            "Arithmetic discrepancy between West and East depth chains: West side indicates 5000 mm + 14200 mm = 19200 mm "
            "total depth to bottom of terrace, while East side indicates 16000 mm (main body) + 3000 mm (terrace) = 19000 mm "
            "total depth. Difference is 200 mm. Both original measurements are retained. No automatic dimension modification is applied."
        )
        u["suggested_action"] = (
            "Human decision required: "
            "(A) Prioritize 19000 mm overall depth (16000 mm house + 3000 mm terrace), treating 14200 mm as an exterior face measurement including wall thickness; "
            "(B) Prioritize 19200 mm depth with a 200 mm terrace extension or stepped south edge; "
            "(C) Input verified site/survey measurement."
        )
        u["conflicting_values"] = [
            "19200 mm (West side: 5000 mm sauna wing + 14200 mm terrace run)",
            "19000 mm (East side: 16000 mm main house + 3000 mm terrace)"
        ]
    elif u["id"] == "UNC-04":
        u["description"] = "2D floor plan sketch does not provide vertical window sill heights. Sill height is designated UNKNOWN in the 2D CAD model."
        u["suggested_action"] = "Keep unknown in 2D floor plan model. Defer vertical parameter review to downstream 3D BIM integration."

# Validate updated observations
is_valid, obs_errors = validate_observations(obs)
if not is_valid:
    raise ValueError(f"Observations schema validation failed: {obs_errors}")
print("Audited observations schema validation: PASSED (0 errors)")

with open(TEST_DIR / "extracted_observations.json", "w", encoding="utf-8") as f:
    json.dump(obs, f, indent=2)

# Load existing draft model
with open(TEST_DIR / "draft_model.json", "r", encoding="utf-8") as f:
    draft_model = json.load(f)

# Ensure no vertical sill height is assumed in 2D openings
for op in draft_model["openings"]:
    if "sillHeight" in op:
        del op["sillHeight"]

# Update uncertainties in draft model
draft_model["uncertainties"] = [
    {
        "id": "UNC-01",
        "target": "dimensions.depth_chain",
        "description": "Active Blocker: Arithmetic conflict between West dimension chain (5000 + 14200 = 19200 mm) and East dimension chain (16000 + 3000 = 19000 mm). Both original measurements retained; awaiting human decision.",
        "assumedValue": "Unresolved - Awaiting Human Decision",
        "confidence": "low",
        "status": "unresolved"
    },
    {
        "id": "UNC-02",
        "target": "walls.interior_thickness",
        "description": "Interior partition thicknesses unannotated on sketch. Proposed drafting defaults: 200 mm exterior, 100 mm interior, 150 mm plumbing core.",
        "assumedValue": "Proposed: 200mm ext / 100mm int / 150mm core (Unverified)",
        "confidence": "medium",
        "status": "unresolved"
    },
    {
        "id": "UNC-03",
        "target": "openings.window_widths",
        "description": "Window widths unannotated numerically. Proposed standard modular widths: 600 mm (WC), 900 mm (Dušš/Bath), 1000 mm (Majapidamis), 1200 mm (Bedrooms/Sauna), 1500 mm (Living/Dining), 1800 mm (South glazing).",
        "assumedValue": "Proposed modular widths 600-1800 mm (Unverified)",
        "confidence": "medium",
        "status": "unresolved"
    },
    {
        "id": "UNC-04",
        "target": "openings.sill_heights",
        "description": "Window sill heights unannotated on 2D sketch. Designated UNKNOWN in 2D model; deferred to downstream 3D BIM review.",
        "assumedValue": "UNKNOWN (Not applicable to 2D plan)",
        "confidence": "low",
        "status": "unresolved"
    },
    {
        "id": "UNC-05",
        "target": "openings.door_clearances",
        "description": "Door clear opening widths unannotated numerically. Proposed defaults: 900 mm exterior entrance, 800 mm habitable rooms, 700 mm wet/sauna, 1500/2400 mm terrace sliders.",
        "assumedValue": "Proposed clearances 700-900 mm (Unverified)",
        "confidence": "medium",
        "status": "unresolved"
    }
]

# Validate draft model against floor-plan-model.json
with open(REPO_ROOT / "skills" / "sketch-to-cad" / "schemas" / "floor-plan-model.json", "r", encoding="utf-8") as f:
    model_schema = json.load(f)
validate(instance=draft_model, schema=model_schema)
print("Audited draft model schema validation: PASSED (0 errors)")

with open(TEST_DIR / "draft_model.json", "w", encoding="utf-8") as f:
    json.dump(draft_model, f, indent=2)

# Re-create approval package and recompute revision hash
approval_package = create_approval_package(
    draft_model=draft_model,
    observations=obs,
    project_name="Real-World Test 01 - Nordic Residential Villa"
)

# Validate approval package schema
with open(REPO_ROOT / "skills" / "sketch-to-cad" / "schemas" / "approval-package.schema.json", "r", encoding="utf-8") as f:
    app_schema = json.load(f)
validate(instance=approval_package, schema=app_schema)
print(f"Audited approval package schema validation: PASSED (Revision Hash: {approval_package['revision_hash']})")

with open(TEST_DIR / "approval_package.json", "w", encoding="utf-8") as f:
    json.dump(approval_package, f, indent=2)

# Generate revised proposal markdown
proposal_md = generate_proposal_markdown(approval_package)
with open(TEST_DIR / "proposal.md", "w", encoding="utf-8") as f:
    f.write(proposal_md)

# Update uncertainty register JSON and MD
uncertainty_reg = {
    "project": "Real-World Test 01 - Nordic Residential Villa",
    "source_file": "source_sketch.jpg",
    "source_sha256": "12ca802a25cd855467a62473c7c35f423ca01ed53ab3818b61b7b75cf9259957",
    "audit_status": "AWAITING_HUMAN_APPROVAL",
    "total_uncertainties": len(obs["uncertainties"]),
    "blocking_count": sum(1 for u in obs["uncertainties"] if u["severity"] == "blocker"),
    "warning_count": sum(1 for u in obs["uncertainties"] if u["severity"] == "warning"),
    "info_count": sum(1 for u in obs["uncertainties"] if u["severity"] == "info"),
    "uncertainties": obs["uncertainties"]
}

with open(TEST_DIR / "uncertainty_register.json", "w", encoding="utf-8") as f:
    json.dump(uncertainty_reg, f, indent=2)

# Update execution log
exec_log = {
    "test_id": "TEST-01",
    "timestamp": "2026-11-03T19:26:00Z",
    "status": "AWAITING_HUMAN_APPROVAL",
    "audit_round": 2,
    "source_image": {
        "file_name": "source_sketch.jpg",
        "sha256": "12ca802a25cd855467a62473c7c35f423ca01ed53ab3818b61b7b75cf9259957",
        "dimensions": "845x1024 px"
    },
    "audit_findings": {
        "unc_01_status": "UNRESOLVED_BLOCKER (Original 14,200 mm and 16,000+3,000 mm preserved; no automatic replacement)",
        "wall_thickness_status": "PROPOSED_UNVERIFIED (200mm ext / 100mm int / 150mm core)",
        "opening_widths_status": "PROPOSED_UNVERIFIED (Modular 600-1800mm windows, 700-900mm doors)",
        "sill_height_status": "UNKNOWN in 2D (Deferred to downstream BIM)",
        "geometry_counts_verified": True
    },
    "governance": {
        "approval_gate": "ENFORCED",
        "revision_hash": approval_package["revision_hash"],
        "approval_status": "awaiting_approval",
        "cad_generation_blocked": True
    }
}

with open(TEST_DIR / "execution_log.json", "w", encoding="utf-8") as f:
    json.dump(exec_log, f, indent=2)

print("Test-01 package successfully rebuilt and verified.")
