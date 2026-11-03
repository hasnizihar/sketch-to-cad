"""
Apply controlled Revision 04 to Test-01 Model:
1. Master Bedroom North Wall: Add W-INT-MASTER-NORTH at Y=12400 mm ([5000, 12400] to [9000, 12400], th=100 mm).
   Establishes the explicit horizontal circulation walkway corridor (Y in [12400, 13600], width 1200 mm)
   connecting the central hallway, Utility room, Tech room, and Sauna Lounge.
2. WC Layout & Size: Add W-INT-WC-SOUTH at Y=14500 mm ([9600, 14500] to [10500, 14500], th=100 mm).
   Revises WC from an oversized 2400 mm depth down to a compact 1500 mm depth (900 x 1500 mm) per source sketch
   and user feedback ("and the WC next to it was way smaller"). Leaves an open access alcove south of Y=14500.
3. Wall Intersection Hierarchy & Flush Wall: Update W-INT-SAUNA-EAST thickness to 200 mm ([5000, 11000] to [5000, 16000])
   so it is perfectly flush with W-EXT-WEST-MAIN at X=5000 mm, completely eliminating the 25 mm offset jog.
4. Correct Bed Locations:
   - E-BED-01: [12000, 13850], headboard flush with north exterior inner face (Y=15850), zero wall intrusion.
   - E-BED-02: [12000, 10850], headboard flush with north partition south face (Y=12850), zero partition penetration.
   - E-BED-MASTER: [5900, 10100], headboard flush with Master Bedroom north wall (Y=12100), clear walkways on all 3 sides.
5. Door Realignments:
   - D-SAUNA-HALL: center [5000, 13000], on W-INT-SAUNA-EAST inside the horizontal walkway.
   - D-MAJAPIDAMIS: center [6900, 13600], on W-INT-CORR-NORTH.
   - D-TEH: center [8600, 13600], on W-INT-CORR-NORTH.
   - D-WC: center [10050, 14500], on W-INT-WC-SOUTH.
   - D-MASTER-BED: center [9000, 11700], on W-INT-CORR-WEST.
6. Recompute revision hash, validate approval package schema, and enforce human approval gate.
"""

import sys
import json
import copy
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

if "revision_history" not in obs:
    obs["revision_history"] = []

obs["revision_history"].append({
    "timestamp": "2026-11-04T00:00:00Z",
    "reviewer": "Human Reviewer / Antigravity Agent",
    "action": "controlled_model_revision_rev04",
    "reason": (
        "Layout correction per user review and source sketch inspection: (1) Added Master Bedroom north enclosing wall "
        "at Y=12400 mm establishing the distinct horizontal circulation walkway (Y=12400..13600 mm) connecting hallway, "
        "utility, tech, and sauna lounge; (2) Reduced WC depth from 2400 mm to 1500 mm via south wall at Y=14500 mm to match "
        "compact source sketch powder room proportion; (3) Aligned west separating wall W-INT-SAUNA-EAST to 200 mm thickness "
        "eliminating 25 mm offset jog at X=5000 mm; (4) Corrected bed insertion coordinates for E-BED-01, E-BED-02, and "
        "E-BED-MASTER eliminating wall and door clashes; (5) Realigned doors to host walls in the new circulation walkway."
    )
})

# Add UNC-08 for WC dimension reconciliation
obs["uncertainties"].append({
    "id": "UNC-08",
    "field": "rooms.R-WC_geometry",
    "description": (
        "WC compact powder room reconciliation: In source sketch, labeled 'WC 2.4 m²'. "
        "Modeled as width 900 mm (X=9600..10500) and depth 1500 mm (Y=14500..16000), yielding clear area 1.12 m² "
        "(gross 1.35 m²). The previous 2400 mm deep tubular space was identified by user as conflicting with the sketch. "
        "Compact 1500 mm depth is adopted per human instruction; 2.4 m² label discrepancy is recorded as an authentic variance."
    ),
    "severity": "warning",
    "suggested_action": "Retain 900x1500 mm compact powder room with south door; document 2.4 m² label variance.",
    "conflicting_values": [
        "1.12 m² clear / 1.35 m² gross (from compact 1500 mm depth partition)",
        "2.4 m² (from handwritten source text label)"
    ]
})

with open(TEST_DIR / "extracted_observations.json", "w", encoding="utf-8") as f:
    json.dump(obs, f, indent=2)

print("Updated extracted_observations.json with REV-04 history and UNC-08.")

# 2. Update draft_model.json
with open(TEST_DIR / "draft_model.json", "r", encoding="utf-8") as f:
    draft_model = json.load(f)

draft_model["metadata"]["revision"] = "REV-04"
draft_model["metadata"]["updatedAt"] = "2026-11-04T00:00:00Z"
draft_model["metadata"]["status"] = "awaiting_human_approval"
draft_model["status"] = "awaiting_human_approval"

# Walls
walls = draft_model["walls"]
# Remove any existing REV-04 additions if re-running
walls = [w for w in walls if w["id"] not in ("W-INT-MASTER-NORTH", "W-INT-WC-SOUTH")]

for w in walls:
    if w["id"] == "W-INT-SAUNA-EAST":
        w["thickness"] = 200.0
    elif w["id"] == "W-INT-CORR-NORTH":
        w["end"] = [9600.0, 13600.0]

walls.append({
    "id": "W-INT-MASTER-NORTH",
    "layer": "A-WALL-INTR",
    "start": [5000.0, 12400.0],
    "end": [9000.0, 12400.0],
    "thickness": 100.0,
    "type": "interior"
})

walls.append({
    "id": "W-INT-WC-SOUTH",
    "layer": "A-WALL-INTR",
    "start": [9600.0, 14500.0],
    "end": [10500.0, 14500.0],
    "thickness": 100.0,
    "type": "interior"
})
draft_model["walls"] = walls

# Openings
openings = draft_model["openings"]
for op in openings:
    if op["id"] == "D-SAUNA-HALL":
        op["center"] = [5000.0, 13000.0]
        op["hostWall"] = "W-INT-SAUNA-EAST"
    elif op["id"] == "D-MAJAPIDAMIS":
        op["center"] = [6900.0, 13600.0]
        op["hostWall"] = "W-INT-CORR-NORTH"
    elif op["id"] == "D-TEH":
        op["center"] = [8600.0, 13600.0]
        op["hostWall"] = "W-INT-CORR-NORTH"
    elif op["id"] == "D-WC":
        op["center"] = [10050.0, 14500.0]
        op["hostWall"] = "W-INT-WC-SOUTH"
    elif op["id"] == "D-MASTER-BED":
        op["center"] = [9000.0, 11700.0]
        op["hostWall"] = "W-INT-CORR-WEST"

# Elements
elements = draft_model.get("elements", [])
for el in elements:
    if el["id"] == "E-BED-01":
        el["position"] = [12000.0, 13850.0]
    elif el["id"] == "E-BED-02":
        el["position"] = [12000.0, 10850.0]
    elif el["id"] == "E-BED-MASTER":
        el["position"] = [5900.0, 10100.0]
    elif el["id"] == "E-WC-FIXTURE":
        el["position"] = [10050.0, 15600.0]

# Rooms
rooms = draft_model.get("rooms", [])
for r in rooms:
    if r["id"] == "R-MASTER-BED":
        r["boundary"] = [[5000.0, 9200.0], [9000.0, 9200.0], [9000.0, 12400.0], [5000.0, 12400.0]]
    elif r["id"] == "R-WC":
        r["boundary"] = [[9600.0, 14500.0], [10500.0, 14500.0], [10500.0, 16000.0], [9600.0, 16000.0]]

new_hash = calculate_geometry_hash(draft_model)
draft_model["metadata"]["geometryHash"] = new_hash

with open(TEST_DIR / "draft_model.json", "w", encoding="utf-8") as f:
    json.dump(draft_model, f, indent=2)

print(f"Updated draft_model.json to REV-04. Geometry Hash: {new_hash}")

# 3. Create approval package
approval_package = create_approval_package(
    draft_model=draft_model,
    observations=obs,
    project_name="Real-World Test 01 - Nordic Residential Villa"
)

# Validate approval package schema
with open(REPO_ROOT / "skills" / "sketch-to-cad" / "schemas" / "approval-package.schema.json", "r", encoding="utf-8") as f:
    app_schema = json.load(f)
validate(instance=approval_package, schema=app_schema)
print(f"REV-04 approval package validation: PASSED (Revision Hash: {approval_package['revision_hash']})")

with open(TEST_DIR / "approval_package.json", "w", encoding="utf-8") as f:
    json.dump(approval_package, f, indent=2)

# 4. Generate proposal markdown
proposal_md = generate_proposal_markdown(approval_package)
with open(TEST_DIR / "proposal.md", "w", encoding="utf-8") as f:
    f.write(proposal_md)

# 5. Update uncertainty register JSON and MD
uncertainty_reg = {
    "project": "Real-World Test 01 - Nordic Residential Villa",
    "source_file": "source_sketch.jpg",
    "source_sha256": "12ca802a25cd855467a62473c7c35f423ca01ed53ab3818b61b7b75cf9259957",
    "audit_status": "AWAITING_HUMAN_APPROVAL",
    "revision_id": "REV-04",
    "revision_hash": approval_package["revision_hash"],
    "total_uncertainties": len(obs["uncertainties"]),
    "blocking_count": sum(1 for u in obs["uncertainties"] if u["severity"] == "blocker"),
    "warning_count": sum(1 for u in obs["uncertainties"] if u["severity"] == "warning"),
    "info_count": sum(1 for u in obs["uncertainties"] if u["severity"] == "info"),
    "uncertainties": obs["uncertainties"]
}

with open(TEST_DIR / "uncertainty_register.json", "w", encoding="utf-8") as f:
    json.dump(uncertainty_reg, f, indent=2)

# 6. Update execution_log.json
exec_log = {
    "test_id": "TEST-01",
    "timestamp": "2026-11-04T00:00:00Z",
    "status": "AWAITING_HUMAN_APPROVAL",
    "revision_id": "REV-04",
    "revision_hash": approval_package["revision_hash"],
    "source_image": {
        "file_name": "source_sketch.jpg",
        "sha256": "12ca802a25cd855467a62473c7c35f423ca01ed53ab3818b61b7b75cf9259957",
        "dimensions": "845x1024 px"
    },
    "authorized_decisions_applied": {
        "master_bedroom_north_wall": "Added W-INT-MASTER-NORTH at Y=12400 mm forming explicit 1200 mm walkway corridor",
        "wc_depth_correction": "Added W-INT-WC-SOUTH at Y=14500 mm reducing WC depth to 1500 mm (per user critique)",
        "wall_intersection_alignment": "Updated W-INT-SAUNA-EAST thickness to 200 mm, flush with exterior wall at X=5000 mm",
        "bed_insertion_geometry": "Corrected origins to account for [0,0] foot-origin (E-BED-01, E-BED-02, E-BED-MASTER)",
        "door_realignments": "Realigned D-SAUNA-HALL, D-MAJAPIDAMIS, D-TEH, D-WC, D-MASTER-BED to walkway corridor",
        "unc_01_status": "UNRESOLVED_BLOCKER (14200 mm and 16000+3000 mm preserved; 19000 mm datum drafting interpretation)"
    },
    "governance": {
        "approval_gate": "ENFORCED",
        "approval_status": "awaiting_approval",
        "cad_generation_blocked": True
    }
}

with open(TEST_DIR / "execution_log.json", "w", encoding="utf-8") as f:
    json.dump(exec_log, f, indent=2)

print(f"Revision 04 successfully built. Target Hash: {approval_package['revision_hash']}")

