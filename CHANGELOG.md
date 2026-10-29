# Changelog

All notable changes to the `sketch-to-cad` project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- **Milestone 7: End-to-End Sketch Interpretation & CAD Generation**:
  - Implemented multimodal sketch ingestion engine `scripts/sketch_interpreter.py` supporting `.jpg`, `.jpeg`, `.png`, and multi-page `.pdf` floor-plan sets without mutating source files.
  - Authored structured observation schema `skills/sketch-to-cad/schemas/sketch-observations.schema.json` capturing walls, openings, rooms, stairs, columns, symbols, normalized bounding boxes `[ymin, xmin, ymax, xmax]`, and confidence.
  - Implemented deterministic geometric reconstruction engine `reconstruct_geometry`: validates wall graph connectivity, performs orthogonal snapping ($\pm 5^\circ$) while preserving genuinely angled walls, checks closed room polygons, associates door/window openings to host walls, and performs arithmetic contradiction checks between room chains and overall envelope without silent warping.
  - Authored revision-aware approval schema `skills/sketch-to-cad/schemas/approval-package.schema.json` and human review module `scripts/approval_package.py`.
  - Enforced mandatory human approval gate: computes deterministic SHA-256 geometry revision hash; strictly prohibits AI agents and automated bots from self-approving proposals; invalidates approval upon subsequent geometry changes.
  - Implemented source-to-CAD feature-level visual quality assurance engine `scripts/visual_qa.py`: verifies footprint aspect ratio, room topology and count, opening counts, and dimension fidelity, outputting `<project>.visual-qa.json` and `<project>.visual-qa.md` discrepancy reports.
  - Built unified end-to-end pipeline orchestrator `scripts/sketch_to_cad_pipeline.py` connecting sketch ingestion, observation extraction, geometry reconstruction, human review gate, CADCraft DXF drafting, BIM handoff compiling, architectural PDF/Markdown reporting, and visual QA.
  - Generated synthetic and canonical sketch fixture dataset in `tests/fixtures/sketches/`: Fixture A (clean single floor), Fixture B (incomplete/missing dimensions), Fixture C (arithmetic contradictions), Fixture D (multi-page two-storey PDF), and Fixture E (nonrectangular angled plan).
  - Executed end-to-end pipeline against the user's canonical hand-drawn sketch `docs/assets/sketch-before.jpg`.
  - Added new references: `references/sketch-interpretation-contract.md`, `references/source-traceability.md`, and `references/end-to-end-pipeline.md`.
  - Created automated test suite `tests/test_sketch_to_cad_e2e.py` covering all 24 required capabilities (repository total: 91 passed tests).
  - Updated `scripts/validate-skill.ps1` with Validation Check 13 (13/13 passed).
- **Milestone 6: Multi-Storey Residential Floor Plans**:
  - Extended intermediate model schema `skills/sketch-to-cad/schemas/floor-plan-model.json` to support multi-storey definitions: root `floors` array, `stairs` vertical circulation, `approval.floorApprovals`, and optional `floorId` on all entities with 100% legacy backward compatibility.
  - Implemented independent per-floor drawing separation: `DrawingGenerator.build_floor_drawing` and `DrawingGenerator.build_multi_floor_drawings` generate isolated DXF drawings for each storey (`<project>-level-01.dxf`, `<project>-level-02.dxf`) in distinct CADCraft sessions with zero entity leakage.
  - Standardized shared Cartesian project coordinate system: all storeys share common origin `[0.0, 0.0]` and envelope bounds for seamless downstream BIM assembly.
  - Implemented automated vertical coordination checker `validate_vertical_coordination(model)`: checks stair connectivity, verifies footprint and centroid alignment within $\le 50.0\text{ mm}$ tolerance, and validates structural column continuity across levels.
  - Extended `bim-handoff.schema.json` with `dxf.floorDrawings` dictionary and `stairs` schema.
  - Extended architectural reporting engine and `architectural-report.schema.json` with `summary.floorCount`, floor-by-floor schedules, and `audit.verticalCoordination`.
  - Enforced two-tier approval gate: halts CAD drafting if any individual storey status is not `"approved"`.
  - Added multi-storey reference documentation: `skills/sketch-to-cad/references/multi-storey-floor-plans.md`.
  - Created test fixtures: `sample-model-two-storey.json` (aligned duplex), `sample-model-two-storey-misaligned.json` (misalignment detection), and `sample-model-two-storey-unapproved.json` (approval gate enforcement).
  - Added automated test suite `tests/test_multi_storey.py` with 20 tests (repository total: 67 passed tests).
  - Updated `scripts/validate-skill.ps1` with Check 12 (12/12 passed).
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
- **Milestone 7: End-to-End Sketch Interpretation & CAD Generation**:
  - Implemented multimodal sketch ingestion engine `scripts/sketch_interpreter.py` supporting `.jpg`, `.jpeg`, `.png`, and multi-page `.pdf` floor-plan sets without mutating source files.
  - Authored structured observation schema `skills/sketch-to-cad/schemas/sketch-observations.schema.json` capturing walls, openings, rooms, stairs, columns, symbols, normalized bounding boxes `[ymin, xmin, ymax, xmax]`, and confidence.
  - Implemented deterministic geometric reconstruction engine `reconstruct_geometry`: validates wall graph connectivity, performs orthogonal snapping ($\pm 5^\circ$) while preserving genuinely angled walls, checks closed room polygons, associates door/window openings to host walls, and performs arithmetic contradiction checks between room chains and overall envelope without silent warping.
  - Authored revision-aware approval schema `skills/sketch-to-cad/schemas/approval-package.schema.json` and human review module `scripts/approval_package.py`.
  - Enforced mandatory human approval gate: computes deterministic SHA-256 geometry revision hash; strictly prohibits AI agents and automated bots from self-approving proposals; invalidates approval upon subsequent geometry changes.
  - Implemented source-to-CAD feature-level visual quality assurance engine `scripts/visual_qa.py`: verifies footprint aspect ratio, room topology and count, opening counts, and dimension fidelity, outputting `<project>.visual-qa.json` and `<project>.visual-qa.md` discrepancy reports.
  - Built unified end-to-end pipeline orchestrator `scripts/sketch_to_cad_pipeline.py` connecting sketch ingestion, observation extraction, geometry reconstruction, human review gate, CADCraft DXF drafting, BIM handoff compiling, architectural PDF/Markdown reporting, and visual QA.
  - Generated synthetic and canonical sketch fixture dataset in `tests/fixtures/sketches/`: Fixture A (clean single floor), Fixture B (incomplete/missing dimensions), Fixture C (arithmetic contradictions), Fixture D (multi-page two-storey PDF), and Fixture E (nonrectangular angled plan).
  - Executed end-to-end pipeline against the user's canonical hand-drawn sketch `docs/assets/sketch-before.jpg`.
  - Added new references: `references/sketch-interpretation-contract.md`, `references/source-traceability.md`, and `references/end-to-end-pipeline.md`.
  - Created automated test suite `tests/test_sketch_to_cad_e2e.py` covering all 24 required capabilities (repository total: 91 passed tests).
  - Updated `scripts/validate-skill.ps1` with Validation Check 13 (13/13 passed).
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
