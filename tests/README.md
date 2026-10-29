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
