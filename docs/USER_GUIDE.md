# User Guide: Sketch-to-CAD

**Skill Version:** 1.0.0 (Supervised Beta MVP)  
**Host Environment:** Google Antigravity Agent Runtime  
**Prerequisites:** Python 3.10–3.12, Windows 10/11, CADCraft MCP Server (optional for native vector generator)  

---

## 1. Quick Start Tutorial

### Step 1: Install Dependencies
Open PowerShell in the repository root and install the required Python packages into a virtual environment:

```powershell
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install core runtime dependencies
pip install -r requirements.txt
```

### Step 2: Ingest a Floor-Plan Sketch
Place your source floor-plan image (`.jpg`, `.png`, or `.pdf`) in your working directory. For example:
`C:\Projects\Residence\sketch-ground-floor.jpg`

### Step 3: Trigger the Skill in Antigravity
In the Antigravity chat pane, issue the following instruction:

> *"Interpret sketch-ground-floor.jpg using the sketch-to-cad skill. Extract room boundaries, walls, doors, windows, and dimensions. Compile the draft floor plan model and present the proposal with the uncertainty register. Stop at Phase 3 and wait for my review."*

---

## 2. Navigating the Human Approval Gate

The agent will analyze the sketch and generate two review artifacts:
1. `<project-name>.proposal.md`: A human-readable markdown breakdown.
2. `<project-name>.approval.json`: The formal machine-readable proposal package.

### Reviewing the Uncertainty Register
Before approving, always inspect the **Uncertainty Register** presented in the proposal. It highlights items such as:
- **Dimension Arithmetic Mismatches**: e.g., "Sum of rooms (9100 mm) exceeds exterior envelope (8700 mm). Adjusted middle room to 3700 mm."
- **Unverified Sill Heights**: e.g., "Window sill height unannotated on 2D sketch; assumed 900 mm fallback."
- **Opening Swings**: e.g., "Door swing in Bedroom 2 inferred inward toward adjacent wall."

### Approving the Proposal
If the layout and reconciled dimensions match your architectural intent, respond with:

> *"Approved. The reconciled dimensions (8000x8700 mm) and 900 mm sill height fallback are acceptable. Proceed with CAD generation."*

The agent will record your approval using cryptographic revision locking and proceed to Phase 4 (CAD Drafting).

### Requesting Corrections
If you wish to change an interpreted dimension or room label before drafting, instruct the agent:

> *"Correction: Change Bedroom 2 width to 3500 mm, and relabel 'Store' to 'Pantry'. Re-compile the proposal."*

The agent calls `apply_human_correction()`, recalculates the geometry, updates the revision hash, and presents a fresh proposal for approval.

---

## 3. Working with Multi-Storey Floor Plans

For multi-level residences (e.g. duplexes or 2-storey villas):
1. Provide either a multi-page PDF or separate image files (`level-01.png`, `level-02.png`).
2. The agent reconstructs each level independently, ensuring:
   - Identical exterior envelope footprints across levels.
   - Vertical alignment of load-bearing walls and stair cores.
   - Level-specific room schedules and schedules of finishes.
3. The drafting engine generates coordinated separate DXF files:
   - `<project>-level-01.dxf`
   - `<project>-level-02.dxf`
   along with a unified multi-page PDF architectural report (`<project>.report.pdf`).

---

## 4. Downstream 3D BIM Compilation

To turn your generated 2D DXF into an editable 3D Building Information Model using the companion **DXF-to-3D-BIM** skill:

### 1. Validate the BIM Contract
```powershell
python -c "
from scripts.bim_integration_validator import BIMIntegrationValidator
v = BIMIntegrationValidator()
res = v.validate_handoff_contract('deliverables/my-villa/my-villa.handoff.json')
print('Contract valid:', res['valid'])
"
```

### 2. Run Downstream BIM Build
```powershell
# Step A: Preflight & Vertical Parameter Review
python -m dxf_to_3d_bim.cli preflight deliverables/my-villa/my-villa.dxf --handoff deliverables/my-villa/my-villa.handoff.json --out intermediate_bim.json

# Step B: Approve Vertical Parameters
python -m dxf_to_3d_bim.cli approve intermediate_bim.json --by "Your Name" --notes "Approved for 3D build"

# Step C: Compile Native BIMCraft & IFC4
python -m dxf_to_3d_bim.cli build intermediate_bim.json --out deliverables/my-villa/bim/
```

This compiles:
- `sketchtocadimport.bimcraft` (Native editable 3D BIM model)
- `sketchtocadimport.ifc` (ISO 16739-1:2018 IFC4 standard)
- High-resolution 3D axonometric and elevation raster previews

---

## 5. Troubleshooting Common Issues

| Symptom | Cause | Recommended Solution |
| :--- | :--- | :--- |
| **Pipeline pauses and does not draft** | Working as designed: Human Approval Gate | Read `<project>.proposal.md` and reply with an explicit approval message. |
| **Missing API Key Error** | Live vision provider requested without environment variable | Set `$env:GOOGLE_GEMINI_API_KEY="AIzaSy..."` or `$env:OPENAI_API_KEY="sk-..."` in PowerShell, or use `--provider mock` / agent-native mode. |
| **Line ending discrepancy warnings** | Git Windows CRLF conversions | Configure Git to keep line endings clean: `git config core.autocrlf false`. |
| **Opening not found on host wall in BIM** | Bounding box coordinates unprojected | Ensure opening centers are projected onto host wall segments using latest `scripts/sketch_interpreter.py`. |
