# Sketch-to-CAD

[![Release](https://img.shields.io/badge/release-v0.1.0--preview-blue.svg)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Antigravity-lightgrey.svg)](docs/installation.md)
[![CAD Backend](https://img.shields.io/badge/CAD%20Backend-CADCraft%20MCP-orange.svg)](docs/cadcraft-mcp-setup.md)

An AI agent skill for turning rough residential floor-plan sketches into reviewable, editable CAD drawings using CADCraft MCP.

---

## Overview

**Sketch-to-CAD** is a reusable skill for Google Antigravity that bridges hand-drawn architectural sketches and computer-aided drafting (CAD).

Instead of treating CAD generation as an unguided black box, Sketch-to-CAD enforces a strict engineering workflow: it interprets hand-written dimensions, documents uncertainties in a structured data model, requires human approval for any proposed corrections, drafts clean vector geometry on standard AIA layers via CADCraft MCP, and conducts both automated and visual quality checks before delivering final files.

```
Sketch ──► Interpretation ──► User Approval ──► CAD Generation ──► Geometric Validation ──► Visual QA ──► Final Deliverables
```

---

## Key Features

- **Strict User Approval Gate**: Never generates CAD geometry without explicit human review and confirmation of dimensions, room layouts, and proposed corrections.
- **Dimension Classification**: Distinguishes between `explicit` (written on sketch), `estimated` (proportional), and `inferred` (standard architectural conventions) dimensions.
- **Uncertainty Logging**: Automatically captures handwriting ambiguities, missing dimensions, and dimension chain conflicts in a structured JSON model.
- **Standard AIA Layering**: Organizes vector geometry into `A-WALL-EXTR`, `A-WALL-INTR`, `A-DOOR`, `A-GLAZ`, `A-ANNO-TEXT`, and `A-ANNO-DIMS`.
- **Sealed Wall Cavities & Clean Openings**: Subdivides walls around doors and windows with transverse jamb end-caps, avoiding open cavities or crossing lines.
- **Legible Architectural Dimensions**: Scales dimension text, arrows, and orientations for clear readability at standard architectural scales.
- **Dual Deliverables**: Produces both an editable vector `.dxf` drawing and an instant raster `.png` visual preview.

---

## Supported Environment

- **Operating System**: Windows 10 / 11 (tested)
- **AI Agent Host**: Google Antigravity IDE / Agent runtime
- **CAD Engine**: [CADCraft CLI](docs/cadcraft-mcp-setup.md) v0.8.0+ (Headless MCP mode over stdio)
- **Scope**: Single-storey orthogonal residential floor plans

*Note: macOS, Linux, and non-orthogonal floor plans are currently untested.*

---

## Quick Start Installation

### 1. Prerequisites
1. Ensure [CADCraft](docs/cadcraft-mcp-setup.md) is installed on your system.
2. Open PowerShell in your local project or clone this repository:
   ```bash
   git clone https://github.com/hasnizihar/sketch-to-cad.git
   cd sketch-to-cad
   ```

### 2. Run the Installer
Run the included PowerShell installer to install the skill into your Antigravity workspace:

```powershell
# Preview installation (no files touched):
.\scripts\install.ps1 -DryRun

# Install into your target workspace:
.\scripts\install.ps1 -WorkspacePath "C:\Path\To\Your\Workspace"
```

### 3. Configure the CADCraft MCP Server
In your workspace, create or update `.agents/mcp_config.json` with the path to your CADCraft CLI binary:

```json
{
  "mcpServers": {
    "cadcraft": {
      "command": "C:\\Program Files\\CADCraft\\cadcraft-cli.exe",
      "args": ["mcp"]
    }
  }
}
```

*(See [docs/cadcraft-mcp-setup.md](docs/cadcraft-mcp-setup.md) for full configuration details and interactive GUI options).*

---

## How to Use the Skill

1. **Upload your sketch**: Place a photo or scan of your hand-drawn residential floor plan in your workspace.
2. **Invoke Antigravity**:
   > *"Interpret this residential floor-plan sketch using the sketch-to-cad skill. Extract the dimensions, classify uncertainties, build the floor-plan model, and show me the proposal. Stop after Phase 3 and wait for my approval before drafting."*
3. **Review the Proposal**:
   The agent presents the building envelope, room program, and an **Uncertainty Table** highlighting conflicts (e.g., room sums vs. overall footprint) with proposed reconciliation options.
4. **Approve or Correct**:
   Reply with your decision:
   > *"Approved. Proceed with Option A (8000mm overall depth, 3700mm middle room). Generate the CAD drawing."*
5. **Receive Deliverables**:
   The agent generates the vector geometry, conducts geometric validation, performs visual QA, and delivers:
   - `floor-plan.dxf`: Master editable CAD drawing.
   - `floor-plan.png`: Rendered visual preview.
   - `floor-plan-model.json`: Structured intermediate data model.
   - Acceptance and quality audit report.

---

## Project Structure

```
sketch-to-cad/
├── README.md              # Project overview, installation, and usage
├── LICENSE                # MIT license
├── CONTRIBUTING.md         # Contribution guidelines
├── CHANGELOG.md            # Version history and release notes
├── .gitignore             # Protection against secret and artifact uploads
├── skills/
│   └── sketch-to-cad/     # The reusable Antigravity skill
│       ├── SKILL.md       # Master skill instruction file
│       ├── references/    # MCP schemas, drawing standards, validation checklist
│       ├── schemas/       # JSON schema for floor-plan models
│       ├── workflows/     # Phase-by-phase workflow guides
│       └── examples/      # Canonical sample project execution
├── scripts/
│   ├── install.ps1        # Beginner-friendly PowerShell installer
│   └── validate-skill.ps1 # Skill and schema integrity test script
├── docs/
│   ├── installation.md    # Detailed installation guide
│   ├── cadcraft-mcp-setup.md # CADCraft MCP configuration instructions
│   ├── workflow.md        # Deep dive into the 7-stage quality gate
│   ├── troubleshooting.md # Common issues and recovery steps
│   └── limitations.md     # Honest appraisal of v0.1.0 and future roadmap
└── tests/
    ├── README.md          # Test suite documentation
    └── fixtures/          # Validated test floor-plan models
```

---

## Known Limitations

- **Orthogonal Layouts Only**: Currently supports 0° and 90° straight walls; angled or curved walls are not supported in v0.1.0.
- **Single-Storey Typologies**: Multi-storey vertical stacking and stairwells are planned for future versions.
- **Human Disambiguation Required**: When handwritten sketch numbers conflict mathematically, human decision is required.

See [docs/limitations.md](docs/limitations.md) for full details and version roadmap.

---

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on code formatting, testing with `validate-skill.ps1`, and pull request workflows.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

> [!CAUTION]
> **Preliminary Drafting Notice**  
> Drawings generated by this skill are intended solely as preliminary schematic drafting aids and conceptual transcriptions of user sketches. Structural load-bearing capacity, shear walls, foundation engineering, egress safety, and municipal building code compliance are **UNVERIFIED**. All drawings must be reviewed, calculated, and stamped by a licensed architect or professional engineer before construction use.
