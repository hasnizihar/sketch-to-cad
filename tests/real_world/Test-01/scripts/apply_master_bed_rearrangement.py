import sys
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.approval_package import create_approval_package, generate_proposal_markdown, calculate_geometry_hash
from jsonschema import validate

TEST_DIR = REPO_ROOT / "tests" / "real_world" / "Test-01"

# 1. Update draft_model.json
with open(TEST_DIR / "draft_model.json", "r", encoding="utf-8") as f:
    model = json.load(f)

# Update elements
elements = model.get('elements', [])
elements = [e for e in elements if e['id'] not in ('E-NIGHTSTAND-M-L', 'E-NIGHTSTAND-M-R', 'E-WARDROBE-MASTER')]

for e in elements:
    if e['id'] == 'E-BED-MASTER':
        e['position'] = [5825.0, 10350.0]

elements.append({
    'id': 'E-NIGHTSTAND-M-L',
    'blockId': 'FURN_BEDSIDE_TABLE',
    'category': 'furniture',
    'position': [5225.0, 11900.0],
    'rotation': 0.0,
    'source': 'explicit',
    'status': 'approved'
})

elements.append({
    'id': 'E-NIGHTSTAND-M-R',
    'blockId': 'FURN_BEDSIDE_TABLE',
    'category': 'furniture',
    'position': [7725.0, 11900.0],
    'rotation': 0.0,
    'source': 'explicit',
    'status': 'approved'
})

elements.append({
    'id': 'E-WARDROBE-MASTER',
    'blockId': 'FURN_WARDROBE',
    'category': 'furniture',
    'position': [8350.0, 12350.0],
    'rotation': 270.0,
    'source': 'explicit',
    'status': 'approved'
})

model['elements'] = elements

# Update openings: D-MASTER-BED to Y=9900 south of wardrobe
for op in model.get('openings', []):
    if op['id'] == 'D-MASTER-BED':
        op['center'] = [9000.0, 9900.0]
        op['swing'] = 'inward-right'

# Update room label positions: clear of furniture
for r in model.get('rooms', []):
    if r['id'] == 'R-MASTER-BED':
        r['labelPosition'] = [6725.0, 9750.0]
    elif r['id'] == 'R-WC':
        r['labelPosition'] = [10050.0, 15150.0]

new_hash = calculate_geometry_hash(model)
model['metadata']['geometryHash'] = new_hash
model['status'] = 'awaiting_human_approval'
model['metadata']['status'] = 'awaiting_human_approval'
model['metadata']['revision'] = 'REV-04'

with open(TEST_DIR / "draft_model.json", "w", encoding="utf-8") as f:
    json.dump(model, f, indent=2)

print(f"Updated draft_model.json. New hash: {new_hash}")

# 2. Update extracted_observations.json
with open(TEST_DIR / "extracted_observations.json", "r", encoding="utf-8") as f:
    obs = json.load(f)

obs["revision_history"].append({
    "timestamp": "2026-11-04T00:15:00Z",
    "reviewer": "Human Reviewer / Antigravity Agent",
    "action": "master_bedroom_arrangement_alignment",
    "reason": (
        "Realigned Master Bedroom furniture arrangement per user review and source sketch closeup (media_1793731256114_e201db4c.png): "
        "(1) Moved bed headboard flush against north wall inner face (Y=12350 mm, pos=[5825, 10350]); "
        "(2) Added flanking bedside nightstands E-NIGHTSTAND-M-L and E-NIGHTSTAND-M-R; "
        "(3) Added east wall wardrobe E-WARDROBE-MASTER (kapp); "
        "(4) Realigned entry door D-MASTER-BED to Y=9900 mm south of wardrobe; "
        "(5) Repositioned room label to [6725, 9750] in clear floor area below bed to eliminate text-furniture collision."
    )
})

with open(TEST_DIR / "extracted_observations.json", "w", encoding="utf-8") as f:
    json.dump(obs, f, indent=2)

# 3. Create approval package
approval_package = create_approval_package(
    draft_model=model,
    observations=obs,
    project_name="Real-World Test 01 - Nordic Residential Villa"
)

# Validate approval package schema
with open(REPO_ROOT / "skills" / "sketch-to-cad" / "schemas" / "approval-package.schema.json", "r", encoding="utf-8") as f:
    app_schema = json.load(f)
validate(instance=approval_package, schema=app_schema)
print(f"Approval package schema validation: PASSED (Hash: {approval_package['revision_hash']})")

with open(TEST_DIR / "approval_package.json", "w", encoding="utf-8") as f:
    json.dump(approval_package, f, indent=2)

# 4. Generate revised proposal markdown
proposal_md = generate_proposal_markdown(approval_package)
with open(TEST_DIR / "proposal.md", "w", encoding="utf-8") as f:
    f.write(proposal_md)

# 5. Update uncertainty register JSON
with open(TEST_DIR / "uncertainty_register.json", "r", encoding="utf-8") as f:
    uncertainty_reg = json.load(f)

uncertainty_reg["revision_hash"] = approval_package["revision_hash"]
with open(TEST_DIR / "uncertainty_register.json", "w", encoding="utf-8") as f:
    json.dump(uncertainty_reg, f, indent=2)

print("Saved all packages successfully.")

