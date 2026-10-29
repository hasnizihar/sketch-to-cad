# Changelog

All notable changes to the `sketch-to-cad` project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- **Milestone 5: Architectural Reports & Schedules**:
  - Implemented deterministic reporting engine `scripts/architectural_reports.py` (mirrored in `skills/sketch-to-cad/scripts/architectural_reports.py`).
  - Authored Draft-07 JSON Schema `skills/sketch-to-cad/schemas/architectural-report.schema.json` v1.0.0.
  - Room schedule calculation: Shoelace formula for internal clear net area, perimeters, and axis-aligned rectangle dimensions (no false dimensioning for irregular spaces).
  - Opening schedules: Separate Door and Window schedules with geometric host-wall validation and preservation of `null` for unannotated 2D heights.
  - Architectural element inventory: Aggregations by category and block definition plus itemized instances with insertion coordinates.
  - Floor finish schedule: Surface boundary areas and physical material specification audit (distinguishing graphical CAD hatch from certified materials).
  - Uncertainty & verification audit: Tracking provenance, invalid host walls, overlapping room polygons, and envelope clearance.
  - Approval-gate enforcement: Flagging unapproved models as DRAFT / NOT APPROVED FOR CONSTRUCTION.
  - Multi-format deliverable exports: `.report.json`, `.report.md`, and paginated ReportLab `.report.pdf`.
  - Added CLI interface in `architectural_reports.py` and integrated `--generate-report` flag into `drawing_generator.py`.
  - Added comprehensive technical guide `skills/sketch-to-cad/references/architectural-reporting-guide.md`.
  - Added automated test suite `tests/test_architectural_reports.py` with 18 tests (repository total: 47 passed tests).
  - Updated `scripts/validate-skill.ps1` with Check 11 (11/11 passed).
- **Milestone 4: DXF Output Standardization & BIM Handoff Contract**:
  - Authored Draft-07 JSON Schema `skills/sketch-to-cad/schemas/bim-handoff.schema.json` v1.0.0.
  - Implemented `compile_bim_handoff(...)` compiler in `scripts/drawing_generator.py` converting approved models into standardized companion JSON metadata (`<drawing-name>.handoff.json`).
  - Added full companion metadata output to `DrawingGenerator.build_drawing(...)` and CLI `--output-handoff`.
  - Added comprehensive technical specification `skills/sketch-to-cad/references/bim-handoff-contract.md`.
  - Added automated test suite `tests/test_bim_handoff.py` (9 tests) verifying schema compliance, unverified vertical parameters as null, host-wall relationships, and genuine CADCraft DXF/JSON consistency.
  - Added companion fixture `tests/fixtures/sample-model-with-elements.handoff.json` and generated `tests/output/furnished-plan.handoff.json`.
  - Added Check 10 to `scripts/validate-skill.ps1` (10/10 passed).
- **Milestone 3: Architectural Element Workflow Integration**:
  - Integrated 20 CAD block definitions and insertion into `drawing_generator.py` pipeline.
  - Added automated preflight validation with Human Approval Gate enforcement for proposed elements.
  - Added CAD hatch generation for floor finishes on `A-FLOR-FIN`.
- **Milestone 2: Reusable Architectural Element Library**:
  - Implemented `scripts/element_library.py` with 20 parametric residential blocks across furniture, sanitary fixtures, kitchen units, structural columns, and circulation elements.
  - Extended model schema `floor-plan-model.json` to v1.1.0 supporting optional `elements` and `finishes`.

## [0.1.0] - 2026-10-26

### Added
- **Initial Public Preview Release** of the reusable `sketch-to-cad` skill for Google Antigravity.
- **7-Stage Quality Gate Workflow**:
  - `Sketch → Interpretation → User Approval → CAD Generation → Geometric Validation → Visual QA & Source Comparison → Final Deliverables`.
- **Mandatory User Approval Gate**:
  - Halts drafting until dimensional conflicts, room classifications, and layout assumptions are reviewed and approved by the user.
- **Structured Intermediate Model**:
  - JSON schema (`schemas/floor-plan-model.json`) defining the coordinate-based representation bridging sketch interpretation and CAD drafting.
- **CADCraft MCP Integration**:
  - Reference documentation and workflow guides for CADCraft CLI MCP server operations.
  - Layer assignment following AIA CAD standards (`A-WALL-EXTR`, `A-WALL-INTR`, `A-DOOR`, `A-GLAZ`, `A-ANNO-TEXT`, `A-ANNO-DIMS`).
  - Transverse jamb end-caps sealing double-wall cavities at door and window openings.
  - Readable architectural dimension styling with vertical dimension rotation.
- **Automated Tooling**:
  - `scripts/install.ps1`: Beginner-friendly PowerShell installer with workspace path resolution, existing installation detection, and dry-run mode.
  - `scripts/validate-skill.ps1`: Automated test validator for JSON schemas, relative links, and path safety checks.
- **Documentation**:
  - Comprehensive `README.md`, `installation.md`, `cadcraft-mcp-setup.md`, `workflow.md`, `troubleshooting.md`, and `limitations.md`.
  - Canonical studio apartment sample project in `examples/sample-project.md`.
