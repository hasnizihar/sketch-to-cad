# Production Release Packaging & Deliverable Distribution

## 1. Overview
The Production Release Packager (`scripts/release_packager.py`) orchestrates the end-to-end assembly, validation, cryptographic integrity verification, and directory structuring of complete Sketch-to-CAD deliverables.

---

## 2. Release Directory Hierarchy

When a project is released, all generated assets are assembled into an isolated, self-contained project directory under `output/<project_name>/`:

```
output/<project_name>/
├── source/
│   ├── source_sketch.png                # Ingested sketch, scan, or PDF page
│   └── visual_observations.json         # Structured AI vision extraction data
├── review/
│   ├── floor_plan_proposal.md           # Professional Markdown proposal for human review
│   ├── approval_package.json            # Machine-readable approval contract & decisions
│   └── uncertainty_register.json        # Location, confidence, and review actions
├── drawings/
│   ├── <project_name>_level_01.dxf      # Multi-layer CAD drawing for Floor 1
│   ├── <project_name>_level_01.png      # High-resolution raster rendering for Floor 1
│   ├── <project_name>_level_02.dxf      # Multi-layer CAD drawing for Floor 2 (duplex)
│   └── <project_name>_level_02.png      # High-resolution raster rendering for Floor 2
├── sheets/
│   ├── <project_name>-level-01-sheet.pdf # Printable vector PDF sheet (A3/A2 1:100)
│   └── <project_name>-level-02-sheet.pdf # Printable vector PDF sheet for Level 2
├── handoff/
│   └── <project_name>.handoff.json       # Versioned BIM contract for dxf-to-3d-bim
├── reports/
│   ├── architectural_report.md          # Architectural area schedule & finish schedule
│   └── architectural_report.pdf         # Formatted PDF architectural documentation
├── qa/
│   ├── engineering_qa_report.md         # 4-tier severity architectural QA audit
│   └── dxf_inspection_report.md         # Geometric entity count & layer audit
└── manifest.json                        # Cryptographic deliverable manifest with SHA-256
```

---

## 3. Master Release Manifest Schema (`manifest.json`)

The manifest file serves as the definitive bill of materials for downstream tools and human archives:

```json
{
  "manifestVersion": "1.1.0",
  "projectId": "villa-paradiso",
  "projectName": "Villa Paradiso",
  "softwareVersion": "1.1.0",
  "releaseTimestamp": "2026-11-03T00:00:00Z",
  "sourceSketch": {
    "fileName": "villa_sketch.png",
    "sha256": "4a7d...39b"
  },
  "geometryRevisionHash": "7f81...e2c",
  "approval": {
    "status": "approved",
    "approvedBy": "Jane Doe, AIA",
    "approvedAt": "2026-11-02",
    "authMethod": "identity_assertion"
  },
  "qaStatus": "RELEASE_READY",
  "qaSummary": {
    "blocking": 0,
    "major": 0,
    "warning": 2,
    "informational": 3
  },
  "deliverablesCount": 11,
  "deliverables": [
    {
      "path": "drawings/villa-paradiso.dxf",
      "format": "DXF",
      "sizeBytes": 42150,
      "sha256": "81f2...50a"
    },
    {
      "path": "sheets/villa-paradiso-level-01-sheet.pdf",
      "format": "PDF",
      "sizeBytes": 128450,
      "sha256": "1a3c...98f"
    }
  ]
}
```

---

## 4. Release Integrity Verification (`verify_package_integrity`)

To prevent tampering, file corruption, or incomplete deliveries, `ReleasePackager.verify_package_integrity(package_dir)`:
1. Locates `manifest.json` in the target package folder.
2. Iterates over every entry in `deliverables`.
3. Verifies physical existence on disk.
4. Recalculates the SHA-256 hash of the on-disk file.
5. Flags any hash mismatches or missing deliverables.

---

## 5. Security Gate: AI Agent Self-Approval Prohibition

The release packager enforces a strict security gate:
- AI assistants, agents, bots, and demo accounts (`Antigravity`, `Gemini`, `Claude`, `auto-reviewer`, `system`) are strictly disallowed as `approvedBy` signatories.
- Attempting to package a model approved by an AI agent raises `ValueError: Security Gate: AI Agent self-approval rejected.`
- Only verified human reviewers and licensed design professionals may release packages.
