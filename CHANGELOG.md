# Changelog

All notable changes to the `sketch-to-cad` project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- **Milestone 12: Real-World Pilot, Independent Validation & Production Acceptance**:
  - Reconciled and audited test count baseline across all 23 test modules (confirming 220 tests cleanly discovered).
  - Formalized human review governance: explicitly defined review as an asserted identity (`auth_method: "identity_assertion"`) with formal disclaimers regarding professional licensing authentication.
  - Created dedicated 22-sample Real-World Pilot Dataset (`tests/benchmark/pilot_dataset/`) spanning 12 distinct challenge categories: Clean Hand-Drawn Plans, User Hand-Drawn Authentic Sketch, Rough Pencil Sketches, Incomplete & Missing Wall Sketches, Contradictory Annotations, Rotated & Skewed Scans, Low-Resolution Mobile Photos, Non-Rectangular Footprints, Complex Room Junctions & Openings, Multi-Room Residential Layouts (5+ rooms), Multi-Storey Residential Sketches, and Multi-Page PDF Sets.
  - Indexed all pilot samples in `tests/benchmark/pilot_dataset/metadata/pilot_manifest.json` with audited SHA-256 digests and independent ground truth annotations.
  - Implemented `scripts/pilot_benchmark_runner.py` executing spatial bipartite matching for walls, openings, rooms, and dimensions, generating machine-readable `pilot_benchmark_report.json` and executive audit report `pilot_benchmark_report.md`.
  - Enforced strict provenance tracking distinguishing `real_api`, `agent_native`, and `mocked` execution, evaluating the authentic user sketch (`PILOT-02`) under `agent_native` vision execution.
  - Authored 3 comprehensive reference standards in `skills/sketch-to-cad/references/`:
    * `references/real-world-pilot-validation.md`: Dataset taxonomy, empirical findings, and operational tolerances.
    * `references/independent-benchmark-methodology.md`: Mathematical bipartite matching formulations, tolerances, IoU metrics, and uncertainty capture rates.
    * `references/production-acceptance-criteria.md`: Formal acceptance decisions (`ACCEPTED_FOR_CONTROLLED_PILOT`, `ACCEPTED_WITH_LIMITATIONS`, `NOT_READY_FOR_PRODUCTION`), 10 engineering gates, and reviewer assertion governance.
  - Added 10 automated unit and integration tests in `tests/test_pilot_validation.py`, expanding repository test coverage to **230 tests** (100% passing in 6.8s).
  - Updated `scripts/validate-skill.ps1` with Validation Check 18 (18/18 checks passed, 41/41 reference and schema files verified).
- **Milestone 11: Professional Drawing Output, Human Review & Release Readiness**:
  - Implemented professional visual drawing hierarchy in `scripts/drawing_generator.py`: strict AIA layer lineweights (0.50mm exterior walls/columns, 0.35mm interior partitions/stairs, 0.25mm doors/windows/text, 0.18mm dimensions/furniture, 0.13mm finishes), door swing representation, multi-line glazing and sills on `A-GLAZ`.
  - Codified window sill-height non-silent provenance policy: fallback 900mm for unannotated windows is explicitly tagged with `sillHeightProvenance = "assumed_default_unverified"` and `source = "inferred"` in `compile_bim_handoff` and logged in `uncertainties` register with status `unresolved`.
  - Built comprehensive 3-tier architectural dimensioning engine `scripts/dimension_engine.py` (mirrored in `skills/sketch-to-cad/scripts/dimension_engine.py`): Tier 1 overall building footprint (exterior bounding box), Tier 2 chained exterior wall openings, Tier 3 internal room callouts (Width x Depth m and mm, area m²). Implemented automated collision detection (`detect_dimension_collisions`) and resolution (`resolve_collisions`) with offset staggering and minimum 50mm clearance.
  - Implemented configurable vector drawing sheet generator `scripts/sheet_generator.py` (mirrored in `skills/sketch-to-cad/scripts/sheet_generator.py`): standard ISO formats (A4 through A1, landscape and portrait), architectural scales (1:50, 1:100, 1:200), strict viewport boundary mathematics raising `ScaleOverflowError` without silent scaling, ANSI/ISO/AIA standardized title block, revision table, legend, and conditional North Arrow validation (rendered only when verified from source observations).
  - Implemented production release packaging engine `scripts/release_packager.py` (mirrored in `skills/sketch-to-cad/scripts/release_packager.py`): assembles isolated, self-contained project deliverables under `output/<project_name>/` across 7 standardized subdirectories (`source/`, `review/`, `drawings/`, `sheets/`, `handoff/`, `reports/`, `qa/`). Generates cryptographic `manifest.json` with SHA-256 digests for all deliverables, revision hashes, and approval metadata.
  - Added package integrity verification `ReleasePackager.verify_package_integrity` verifying deliverable checksums, and enforced security gates prohibiting AI agent self-approvals.
  - Authored 4 comprehensive reference standards: `references/professional-drawing-standards.md`, `references/dimensioning-engine.md`, `references/drawing-sheets-and-scales.md`, and `references/release-packaging.md`.
  - Added 32 new automated tests across 4 test suites (`tests/test_dimension_engine.py`, `tests/test_sheet_generator.py`, `tests/test_release_packager.py`, `tests/test_release_regression.py`), expanding total repository test coverage to 220 tests (100% passing).
  - Implemented 15-scenario release regression test suite (`tests/test_release_regression.py`) covering small single-storey, large multi-room, two-storey duplex with stairs, angled walls, diverse doors/windows, dense dimension chains, conflicting dimensions, incomplete sketches, rotated inputs, unannotated sill provenance, unapproved revisions, invalid wall junctions, duplicate DXF entities, and unresolved BIM handoff assumptions.
  - Updated `scripts/validate-skill.ps1` with Validation Check 17 (17/17 checks passed, 38/38 reference and schema files verified).
- **Milestone 10: Real-World Validation, Benchmarking & Production Reliability**:
  - Implemented real-world architectural sketch benchmark dataset (	ests/benchmark/) across 6 categories (A through F): Clean Hand-Drawn Plans (BENCH-CAT-A-01), Rough Hand-Drawn Plans (BENCH-CAT-B-01), Incomplete Plans (BENCH-CAT-C-01), Complex Non-Rectangular Plans (BENCH-CAT-D-01), Multi-Storey PDF Plans (BENCH-CAT-E-01), and Low-Quality Degraded Inputs (BENCH-CAT-F-01).
  - Authored dataset catalog manifest 	ests/benchmark/metadata/dataset_manifest.json indexing file formats, image dimensions, SHA-256 cryptographic hashes, and provenance metadata.
  - Authored certified ground-truth annotation files in 	ests/benchmark/ground_truth/ with exact millimeter coordinates for walls, openings, rooms, explicit handwritten dimensions, and expected uncertainty flags.
  - Built spatial bipartite benchmark evaluation engine scripts/benchmark_engine.py (mirrored in skills/sketch-to-cad/scripts/benchmark_engine.py): orientation-invariant wall endpoint matching, opening center proximity and width error tracking, room polygon IoU clipping and net area relative error, and explicit dimension extraction tolerance (<=50mm).
  - Enforced strict benchmark provenance policy: explicit tagging of is_genuine_ai and execution_type (
eal_api, gent_native, mocked), preventing synthetic or mock inference from being represented as genuine AI vision accuracy.
  - Implemented independent architectural and structural DXF inspector scripts/dxf_inspector.py (mirrored in skills/sketch-to-cad/scripts/dxf_inspector.py): DXF header verification (=4 mm, DXF version, bounding extents), AIA layer compliance, layer 0 cleanliness, entity inventory counting, duplicate entity detection, degenerate segment detection (<10mm blocking), model-to-DXF-to-BIM consistency cross-auditing, and Markdown audit report generation.
  - Implemented downstream BIM integration and interoperability validator scripts/bim_integration_validator.py (mirrored in skills/sketch-to-cad/scripts/bim_integration_validator.py): validates handoff contract against downstream dxf-to-3d-bim requirements, checks coordinate systems and units, verifies opening host referential integrity, defaults window sill heights (900mm) to prevent downstream NoneType multiplication errors, maps uncertainty statuses to valid downstream enums, and executes genuine downstream preflight inspection (dxf_to_3d_bim inspect) and intermediate model preparation (dxf_to_3d_bim prepare).
  - Proved downstream interoperability through genuine CLI execution with dxf-to-3d-bim, generating native .bimcraft models, IFC4 exports, axonometric 3D projections, elevations, and building sections.
  - Implemented enterprise-grade production reliability engine scripts/pipeline_reliability.py (mirrored in skills/sketch-to-cad/scripts/pipeline_reliability.py): retry strategy with exponential backoff and randomized jitter, transient vs permanent error classification (is_error_retryable), and atomic file write operations (tomic_write_text, tomic_write_json, tomic_write_bytes) with rollback preventing partial or corrupt deliverables.
  - Implemented high-resolution performance and resource profiling framework scripts/performance_profiler.py (mirrored in skills/sketch-to-cad/scripts/performance_profiler.py): captures phase durations, entity processing counts, and renders Markdown performance audit reports.
  - Authored 5 comprehensive reference specifications: 
eferences/real-world-benchmark.md, 
eferences/vision-accuracy-metrics.md, 
eferences/dxf-inspection.md, 
eferences/bim-integration-validation.md, and 
eferences/production-reliability.md.
  - Authored dataset documentation in 	ests/benchmark/README.md.
  - Added 34 new automated tests across 5 test suites (	ests/test_benchmark_engine.py, 	ests/test_dxf_inspector.py, 	ests/test_bim_integration.py, 	ests/test_pipeline_reliability.py, 	ests/test_performance_profiler.py), expanding test coverage to 188 tests (100% passing).
  - Updated scripts/validate-skill.ps1 with Validation Check 16 (16/16 checks passed, 34/34 reference and schema files verified).
- **Milestone 9: Advanced Architectural Drafting & Engineering Standards**:
  - Implemented advanced wall geometry and junction handling: clean cavity trimming, transverse jamb end-caps sealing openings, and deterministic T-junction trimming (partition double lines trimmed by host wall half-thickness to prevent penetration into host cavity).
  - Enhanced door and window drafting in scripts/drawing_generator.py: support for single-leaf swing doors (inward-left, inward-right, outward-left, outward-right), double-leaf doors (double), sliding/pocket doors (sliding), and sliding bypass windows with dual offset sashes on A-GLAZ.
  - Upgraded dimensioning and architectural annotation system: tiered dimension hierarchy, room area callouts (m²), standardized drawing title block header (LEVEL: ... | SCALE: ... | UNITS: ...), and strict conditional North Arrow policy (drawn if and only if orientation or north angle is provided; strictly omitted if unknown to prevent unverified assumptions).
  - Implemented comprehensive Architectural Geometry Validation Engine scripts/geometry_validation.py (mirrored in skills/sketch-to-cad/scripts/geometry_validation.py): wall network connectivity, junction typology (L, T, Cross, disconnected endpoints), degenerate wall detection (<10mm blocking), minimum 50mm corner clearance structural return, overlapping openings detection, door swing clearance conflicts, Gauss Shoelace area computation, self-intersection (bowtie polygon) detection, interior room overlap detection, envelope boundary containment, and multi-storey level filtering.
  - Implemented unified Architectural & Engineering QA Validator scripts/architectural_qa.py: 4-tier architectural severity model (locking, major, warning, informational), BIM handoff referential integrity checks, and Markdown audit report rendering (generate_engineering_qa_markdown).
  - Authored 6 challenging architectural test fixtures in 	ests/fixtures/sketches/: Case F (complex junctions & thickness transitions), Case G (diverse openings & corner clearances), Case H (irregular L-shaped footprint with 5-vertex non-convex salon polygon), Case I (compact 32 m² studio/ADU plan with dense symbols), Case J (2-storey duplex with vertical stair and column alignment), and Case K (incomplete ambiguous sketch rejected by Approval Gate).
  - Authored 4 comprehensive architectural reference standards: 
eferences/architectural-drafting-standards.md, 
eferences/geometry-validation.md, 
eferences/dimensioning-and-annotations.md, and 
eferences/architectural-qa.md.
  - Added 34 new automated tests across 4 test suites (	ests/test_geometry_validation.py, 	ests/test_architectural_qa.py, 	ests/test_advanced_drafting.py, 	ests/test_challenging_fixtures.py), bringing repository total to 154 tests (100% passing).
  - Updated scripts/validate-skill.ps1 with Validation Check 15 (15/15 checks passed).
- **Milestone 8: Genuine Vision Integration & Production Reliability**:
  - Implemented pluggable, verifiable multimodal vision provider architecture `scripts/vision_provider.py` and configuration manager `scripts/vision_config.py` supporting Google Gemini (`gemini-2.5-flash`), OpenAI (`gpt-4o`), Antigravity Agent native vision, and deterministic mock providers.
  - Authored Draft-07 JSON Schema `skills/sketch-to-cad/schemas/vision-execution-record.schema.json` v1.0.0; pipeline generates structured audit records (`<project>.vision-execution.json`) capturing image SHA-256 fingerprint, provider/model metadata, request timestamps, duration in ms, token usage, and status (`real_api`, `agent_native`, `mocked`) without secret leakage (`mask_secret`).
  - Strengthened human approval security in `scripts/approval_package.py`: enforces token-based AI agent self-approval blocking while exempting genuine professional credentials (e.g., `AIA` registrations), rejects placeholder/demo reviewer identities (`Jane Doe`, `John Doe`) in strict production mode, records review decisions with explicit `auth_method: "identity_assertion"` advisories, and enforces SHA-256 geometry hash invalidation.
  - Upgraded source-to-CAD visual quality assurance engine `scripts/visual_qa.py`: implemented 4-tier architectural severity classification (`blocking_discrepancy`, `major_discrepancy`, `warning`, `informational`), explicit architectural reasoning distinguishing out-of-scale hand sketches (e.g., 1.41 image aspect ratio vs 0.92 explicit CAD ratio) from CAD algorithm drift, duplicate entity ID detection, and non-destructive reporting.
  - Built architectural benchmark evaluation suite `scripts/evaluate_vision.py` and dataset `tests/fixtures/sketches/benchmark_manifest.json` conforming to `skills/sketch-to-cad/schemas/vision-benchmark-result.schema.json`; evaluates bounding box IoU, precision, recall, dimension accuracy within 50mm tolerance, and arithmetic contradiction detection across 5 canonical benchmark cases.
  - Authored comprehensive architectural specifications: `references/vision-provider-contract.md`, `references/vision-benchmark.md`, `references/approval-security.md`, and `references/vision-integration-guide.md`.
  - Added 29 new automated tests across 4 test suites (`tests/test_vision_provider.py`, `tests/test_approval_security.py`, `tests/test_visual_qa_severity.py`, `tests/test_vision_benchmark.py`), bringing repository total to 120 tests (100% passing).
  - Updated `scripts/validate-skill.ps1` with Validation Check 14 (14/14 checks passed).
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
- **Milestone 8: Genuine Vision Integration & Production Reliability**:
  - Implemented pluggable, verifiable multimodal vision provider architecture `scripts/vision_provider.py` and configuration manager `scripts/vision_config.py` supporting Google Gemini (`gemini-2.5-flash`), OpenAI (`gpt-4o`), Antigravity Agent native vision, and deterministic mock providers.
  - Authored Draft-07 JSON Schema `skills/sketch-to-cad/schemas/vision-execution-record.schema.json` v1.0.0; pipeline generates structured audit records (`<project>.vision-execution.json`) capturing image SHA-256 fingerprint, provider/model metadata, request timestamps, duration in ms, token usage, and status (`real_api`, `agent_native`, `mocked`) without secret leakage (`mask_secret`).
  - Strengthened human approval security in `scripts/approval_package.py`: enforces token-based AI agent self-approval blocking while exempting genuine professional credentials (e.g., `AIA` registrations), rejects placeholder/demo reviewer identities (`Jane Doe`, `John Doe`) in strict production mode, records review decisions with explicit `auth_method: "identity_assertion"` advisories, and enforces SHA-256 geometry hash invalidation.
  - Upgraded source-to-CAD visual quality assurance engine `scripts/visual_qa.py`: implemented 4-tier architectural severity classification (`blocking_discrepancy`, `major_discrepancy`, `warning`, `informational`), explicit architectural reasoning distinguishing out-of-scale hand sketches (e.g., 1.41 image aspect ratio vs 0.92 explicit CAD ratio) from CAD algorithm drift, duplicate entity ID detection, and non-destructive reporting.
  - Built architectural benchmark evaluation suite `scripts/evaluate_vision.py` and dataset `tests/fixtures/sketches/benchmark_manifest.json` conforming to `skills/sketch-to-cad/schemas/vision-benchmark-result.schema.json`; evaluates bounding box IoU, precision, recall, dimension accuracy within 50mm tolerance, and arithmetic contradiction detection across 5 canonical benchmark cases.
  - Authored comprehensive architectural specifications: `references/vision-provider-contract.md`, `references/vision-benchmark.md`, `references/approval-security.md`, and `references/vision-integration-guide.md`.
  - Added 29 new automated tests across 4 test suites (`tests/test_vision_provider.py`, `tests/test_approval_security.py`, `tests/test_visual_qa_severity.py`, `tests/test_vision_benchmark.py`), bringing repository total to 120 tests (100% passing).
  - Updated `scripts/validate-skill.ps1` with Validation Check 14 (14/14 checks passed).
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
  - `Sketch â†’ Interpretation â†’ User Approval â†’ CAD Generation â†’ Geometric Validation â†’ Visual QA & Source Comparison â†’ Final Deliverables`.
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
