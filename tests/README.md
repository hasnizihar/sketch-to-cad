# Sketch-to-CAD Tests & Fixtures

This directory contains test specifications, reference fixtures, and validation procedures for the `sketch-to-cad` skill.

## Test Strategy

1. **Schema Integrity**:
   - Verify that test models validate against [`schemas/floor-plan-model.json`](../skills/sketch-to-cad/schemas/floor-plan-model.json).
   - Ensure required fields (`metadata`, `envelope`, `walls`, `openings`, `rooms`, `dimensions`, `uncertainties`) are enforced.
2. **Geometric Consistency**:
   - Check that exterior walls form a closed perimeter matching the `envelope` dimensions.
   - Verify that openings lie within their host wall bounds.
   - Ensure room labels sit within room polygon boundaries.
3. **Approval Gate Validation**:
   - Ensure drafting procedures reject models where `status` is not `"approved"`.
4. **Visual QA Gate**:
   - Confirm that dimension styles, opening jamb closures, and label non-overlap rules pass visual inspection.

## Included Fixtures

- [`fixtures/sample-model.json`](fixtures/sample-model.json): Baseline canonical intermediate model representing an unfurnished 6m x 5m studio apartment with 3 rooms, 2 doors, 2 windows, and 2 dimension chains.
- [`fixtures/sample-model-with-elements.json`](fixtures/sample-model-with-elements.json): Furnished 6m x 5m studio apartment fixture demonstrating architectural blocks across `A-FURN`, `A-FIXT`, `A-COLS`, and tile floor finish on `A-FLOR-FIN`.
- [`fixtures/sample-model-with-elements.handoff.json`](fixtures/sample-model-with-elements.handoff.json): Validated companion BIM handoff contract fixture conforming to `bim-handoff.schema.json` v1.0.0.
- [`fixtures/sample-model-two-storey.json`](fixtures/sample-model-two-storey.json): Two-storey duplex residence fixture demonstrating coordinated Ground Floor (`LEVEL-01`) and First Floor (`LEVEL-02`), aligned staircase vertical circulation, and continuous structural columns.
- [`fixtures/sample-model-two-storey-misaligned.json`](fixtures/sample-model-two-storey-misaligned.json): Diagnostic fixture containing stair and column offsets exceeding 50mm tolerance to verify vertical coordination failure detection.
- [`fixtures/sample-model-two-storey-unapproved.json`](fixtures/sample-model-two-storey-unapproved.json): Diagnostic fixture with unapproved upper floor to verify per-floor approval gate enforcement.

## Automated Test Suites

1. **Skill Integrity & Static Check**:
   ```powershell
   .\scripts\validate-skill.ps1
   ```
2. **Architectural Element Library Test Suite**:
   ```powershell
   python -m unittest tests/test_element_library.py
   ```
   Covers catalog completeness, positive dimensions, base points, layer mappings, instance validation rules, schema backward compatibility, mocked CADCraft block calls, and real CADCraft CLI execution.
3. **CAD Drawing Generator Workflow Integration Tests**:
   ```powershell
   python -m unittest tests/test_drawing_generator.py
   ```
   Validates end-to-end model compilation, Approval Gate enforcement, unapproved proposal rejection, duplicate ID handling, envelope clearance warnings, and real CADCraft headless MCP DXF+PNG generation.
4. **BIM Handoff Contract Test Suite (Milestone 4)**:
   ```powershell
   python -m unittest tests/test_bim_handoff.py
   ```
   Validates Draft-07 compliance of `bim-handoff.schema.json`, full JSON compilation, backward compatibility with un-furnished models, null-preservation of unverified vertical elevations, host-wall relationships, and real CADCraft DXF+JSON consistency.
5. **Architectural Reports & Schedules Test Suite (Milestone 5)**:
   ```powershell
   python -m unittest tests/test_architectural_reports.py
   ```
   Validates Shoelace net area calculations, perimeter lengths, axis-aligned rectangle detection without false dimensioning, missing boundary handling, room polygon overlap detection, separate door/window schedules, element category/block aggregations, finish area coverage, uncertainty preservation, approval gate enforcement, legacy fixture compatibility, JSON schema validation (`architectural-report.schema.json`), Markdown/PDF rendering, and unified CADCraft pipeline execution.
6. **Multi-Storey Floor Plans & Vertical Coordination Test Suite (Milestone 6)**:
   ```powershell
   python -m unittest tests/test_multi_storey.py
   ```
   Validates multi-level floor plan schema rules, per-floor approval gate enforcement, independent DXF drawing generation, entity isolation without inter-floor leakage, shared Cartesian coordinate system, staircase vertical circulation alignment ($<=50\text{mm}$ tolerance), structural column continuity across levels, companion multi-storey BIM handoffs, and real CADCraft multi-floor execution.

7. **End-to-End Sketch Interpretation & CAD Generation Test Suite (Milestone 7)**:
   ```powershell
   python -m unittest tests/test_sketch_to_cad_e2e.py
   ```
   Validates all 24 required capabilities across the end-to-end pipeline:
   - JPG and PNG input handling (`load_sketch_input`).
   - Multi-page PDF input handling and page rendering.
   - Corrupted, empty, or unsupported format rejection with actionable errors.
   - Immutability of original sketch files and source metadata preservation.
   - Structured observation validation against `sketch-observations.schema.json`.
   - Dimension provenance classification (`explicit`, `estimated`, `inferred`, `proposed`, `unknown`).
   - Missing dimension handling and uncertainty logging without arbitrary fabrication.
   - Arithmetic contradiction detection between room chains and overall envelope.
   - Wall graph connectivity and dangling wall detection.
   - Closed room boundary reconstruction and area computation.
   - Opening-to-wall host associations.
   - Unrecognized symbol preservation in uncertainty log.
   - Single-floor versus multi-floor identification.
   - Multi-floor source separation from multi-page PDFs.
   - Structured human approval package creation and proposal markdown rendering.
   - Reviewer rejection handling and decision logging.
   - Strict prohibition of AI agent self-approval.
   - SHA-256 geometry hash revision tracking and tampered model invalidation.
   - Canonical draft model compilation with status `awaiting_approval`.
   - Human approval transition to `approved` state.
   - Real CADCraft editable DXF generation.
   - Companion BIM handoff consistency (`bim-handoff.schema.json`).
   - Architectural report generation (PDF and Markdown).
   - Source-to-CAD feature-level visual quality assurance (`perform_visual_qa`).
   - Complete end-to-end fixture execution from sketch image to approved deliverables.

### Sketch Fixtures (Milestone 7)

Located in `tests/fixtures/sketches/`:
- `fixture-a-clean-single-floor.png`: Clean orthogonal single-floor hand sketch with complete explicit dimensioning.
- `fixture-b-incomplete.png`: Incomplete sketch missing depth dimension and wall thicknesses.
- `fixture-c-contradictory.png`: Contradictory sketch with room chain sum exceeding overall envelope.
- `fixture-d-two-storey.pdf`: Multi-page PDF containing coordinated Ground and First floor plans with aligned staircase.
- `fixture-e-nonrectangular.png`: Nonrectangular floor plan with an intentionally angled boundary wall.
