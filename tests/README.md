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

8. **Vision Provider Interface Test Suite (Milestone 8)**:
   ```powershell
   python -m unittest tests/test_vision_provider.py
   ```
   Validates base provider abstract interface, Google Gemini 2.5 Flash formatting, OpenAI GPT-4o vision requests, Antigravity Agent native vision, deterministic mock provider, simulated network failure modes (timeout, rate limit HTTP 429, malformed JSON), schema validation error reporting, source image SHA-256 fingerprinting, duration tracking, and secret masking (`mask_secret`).

9. **Human Approval Security Test Suite (Milestone 8)**:
   ```powershell
   python -m unittest tests/test_approval_security.py
   ```
   Validates token-based rejection of AI agent self-approvals, rejection of placeholder/demonstration identities (`Jane Doe`, `John Doe`, `Test Reviewer`) in strict production mode, allowance of genuine professional credentials (e.g. `AIA` registration numbers), plain-text `identity_assertion` audit logging with explicit security advisories, and SHA-256 geometry hash invalidation upon model alterations.

10. **Visual QA Severity & Out-of-Scale Reasoning Test Suite (Milestone 8)**:
    ```powershell
    python -m unittest tests/test_visual_qa_severity.py
    ```
    Validates 4-tier architectural severity model (`blocking_discrepancy`, `major_discrepancy`, `warning`, `informational`), explicit architectural reasoning for out-of-scale hand sketches (e.g., 1.41 image aspect ratio vs 0.92 explicit CAD ratio), duplicate entity detection across walls, openings, and rooms, and non-destructive reporting policies.

11. **Vision Benchmark Suite & Evaluation Engine (Milestone 8)**:
    ```powershell
    python -m unittest tests/test_vision_benchmark.py
    ```
    Validates architectural benchmark manifest evaluation across all 5 standard test cases (Cases A–E), normalized bounding box IoU calculation, precision and recall for walls/openings/rooms, dimension extraction accuracy within 50mm tolerance, contradiction detection rate, Markdown/JSON report export, and Draft-07 schema compliance of `vision-benchmark-result.schema.json`.

12. **Architectural Geometry Validation Test Suite (Milestone 9)**:
    `powershell
    python -m unittest tests/test_geometry_validation.py
    `
    Validates wall network graph topology, junction classification (L, T, Cross, disconnected endpoints), degenerate wall detection (<10mm blocking), 50mm corner clearance structural return, overlapping openings detection, door swing clearance conflicts, Gauss Shoelace area computation, self-intersection (bowtie polygon) detection, interior room overlap detection, envelope boundary containment, and multi-storey level filtering.

13. **Architectural QA & Engineering Standards Test Suite (Milestone 9)**:
    `powershell
    python -m unittest tests/test_architectural_qa.py
    `
    Validates 4-tier architectural severity model (locking, major, warning, informational), BIM handoff referential integrity checks, coordinate system verification, comprehensive QA execution, and Markdown engineering audit report generation.

14. **Advanced Architectural Drafting Standards Test Suite (Milestone 9)**:
    `powershell
    python -m unittest tests/test_advanced_drafting.py
    `
    Validates wall T-junction cavity trimming (partition double lines trimmed by host wall half-thickness), single-leaf swing geometry (inward-left, inward-right, outward-left, outward-right), double-leaf doors (double), sliding/pocket doors (sliding), sliding bypass windows, sheet title block headers, conditional North Arrow drafting (drawn if orientation known; strictly omitted if unknown), and real CADCraft CLI execution.

15. **Challenging Architectural Test Fixtures Suite (Milestone 9)**:
    `powershell
    python -m unittest tests/test_challenging_fixtures.py
    `
    Validates end-to-end processing across all 6 challenging test cases:
    - Case F (ixture-f-complex-junctions.json): Complex junctions, thickness transitions (200mm exterior, 100mm interior), clean cavity trimming.
    - Case G (ixture-g-complex-openings.json): Diverse opening types (double doors, sliding doors, sliding windows) and corner clearance verification.
    - Case H (ixture-h-irregular-plan.json): Irregular L-shaped building footprint, 5-vertex non-convex salon polygon, Shoelace area calculation.
    - Case I (ixture-i-compact-plan.json): Compact 32 m² studio/ADU plan with dense furniture and sanitary clearances.
    - Case J (ixture-j-multi-storey-complex.json): 2-storey residence with shared envelope, vertical stair & structural column alignment.
    - Case K (ixture-k-incomplete-ambiguous.json): Incomplete ambiguous sketch with unapproved status (waiting_approval) - verifies mandatory Approval Gate rejection.

---

### 16. **Real-World Architectural Benchmark Engine Suite (Milestone 10)**:
    `powershell
    python -m unittest tests/test_benchmark_engine.py
    `
    Validates benchmark dataset manifest loading, ground-truth parsing across all 6 categories (A through F), polygon IoU computation, spatial wall bipartite matching, opening center proximity and width errors, dimension numeric accuracy within 50mm tolerance, execution type provenance enforcement, and Markdown benchmark audit report rendering.

17. **Independent Architectural & Structural DXF Inspector Suite (Milestone 10)**:
    `powershell
    python -m unittest tests/test_dxf_inspector.py
    `
    Validates DXF file integrity, SHA-256 hashing, header inspection (=4 mm, DXF version, bounding extents), layer compliance, layer 0 cleanliness, entity inventory counting, duplicate entity detection, degenerate geometry detection (<10mm blocking), model-to-DXF-to-BIM consistency cross-auditing, and Markdown audit report formatting.

18. **Downstream BIM Integration & Interoperability Validator Suite (Milestone 10)**:
    `powershell
    python -m unittest tests/test_bim_integration.py
    `
    Validates downstream environment detection, handoff semantic contract verification, referential integrity (orphan openings, duplicate wall IDs), window sill height specification warnings, Markdown integration report formatting, and genuine downstream CLI preflight (inspect) and prepare execution.

19. **Production Reliability, Retry Backoff & Atomic Operations Suite (Milestone 10)**:
    `powershell
    python -m unittest tests/test_pipeline_reliability.py
    `
    Validates RetryConfig defaults, transient vs permanent error classification, exponential backoff with jitter, immediate failure on permanent auth or schema errors, atomic text writing, atomic JSON writing, atomic binary bytes writing, and rollback on interrupted write operations.

20. **Pipeline Performance & Resource Profiling Suite (Milestone 10)**:
    `powershell
    python -m unittest tests/test_performance_profiler.py
    `
    Validates phase start/end timing lifecycle, sequential pipeline stage transitions, architectural entity tracking, source metadata recording, profile dictionary serialization, and Markdown performance report rendering.

21. **Dimensioning & Annotation Engine Suite (Milestone 11)**:
    `powershell
    python -m unittest tests/test_dimension_engine.py
    `
    Validates 3-tier dimension generation (overall footprint, chained openings, room callouts), formatting in millimeters and meters, text position offset calculation, collision detection with room labels, and offset staggering collision resolution.

22. **Printable Drawing Sheet Generator Suite (Milestone 11)**:
    `powershell
    python -m unittest tests/test_sheet_generator.py
    `
    Validates paper dimensions (A4-A1 landscape/portrait), printable viewport bounds, strict scale enforcement raising ScaleOverflowError on overflow, ANSI/ISO title block formatting, conditional North Arrow validation, and vector PDF sheet rendering.

23. **Production Release Packager Suite (Milestone 11)**:
    `powershell
    python -m unittest tests/test_release_packager.py
    `
    Validates unapproved model rejection, AI agent self-approval blocking, complete 7-directory release assembly, manifest SHA-256 deliverable inventory, and ReleasePackager.verify_package_integrity tamper detection.

24. **Exhaustive Release Regression Suite (Milestone 11 - 15 Scenarios)**:
    `powershell
    python -m unittest tests/test_release_regression.py
    `
    Validates all 15 release scenarios: small 6x5m plan, large multi-room plan, 2-storey duplex with stairs, non-rectangular angled walls, door subtypes, window configurations, dense dimension collision avoidance, conflicting dimensions detection, incomplete sketches, rotated low-quality inputs, explicit unannotated sill provenance, unapproved revision hash invalidation, invalid wall gaps, duplicate DXF entities, and unresolved BIM handoff assumptions.

---

25. **Real-World Pilot Dataset Integrity & Independent Acceptance Test Suite (Milestone 12)**:
    ```powershell
    python -m unittest tests/test_pilot_validation.py
    ```
    Validates manifest integrity, 22 independent ground truth files, 22 source file hashes, provenance segregation (`agent_native` vs `mocked`), contradiction detection (`PILOT-02`, `PILOT-05`), uncertainty detection (`PILOT-04`, `06`, `07`, `08`, `16`), multi-storey floor plan handling, non-rectangular room IoU matching, end-to-end DXF generation, and human review identity assertion security gates.

---

### Overall Test Suite Execution

Run all 230 automated tests:
`powershell
python -m unittest discover tests
`

Run skill integrity validation (18 automated checks):
`powershell
.\scripts\validate-skill.ps1
`

### Sketch Fixtures (Milestone 7)

Located in `tests/fixtures/sketches/`:
- `fixture-a-clean-single-floor.png`: Clean orthogonal single-floor hand sketch with complete explicit dimensioning.
- `fixture-b-incomplete.png`: Incomplete sketch missing depth dimension and wall thicknesses.
- `fixture-c-contradictory.png`: Contradictory sketch with room chain sum exceeding overall envelope.
- `fixture-d-two-storey.pdf`: Multi-page PDF containing coordinated Ground and First floor plans with aligned staircase.
- `fixture-e-nonrectangular.png`: Nonrectangular floor plan with an intentionally angled boundary wall.
