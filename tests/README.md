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
