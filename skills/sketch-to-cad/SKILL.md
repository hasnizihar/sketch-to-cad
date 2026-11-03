---
name: sketch-to-cad
description: Interprets hand-drawn residential sketches and PDFs (JPG, PNG, PDF), extracts structured architectural observations, enforces revision-aware human approval gates, generates validated 2D CADCraft DXF drawings and companion BIM handoffs, creates professional architectural reports, and runs feature-level visual QA.
---

# Sketch-to-CAD

## Purpose
Convert hand-drawn residential floor-plan sketches (JPG, JPEG, PNG, PDF) into structured, reviewable, editable CAD drawings using connected CADCraft MCP tools. Features an end-to-end automated pipeline comprising deterministic ingestion, structured observation extraction, geometric reconstruction with contradiction detection, human review proposal packaging, revision-aware approval governance, CADCraft DXF drafting, companion BIM handoff compiling, comprehensive architectural reporting (JSON, Markdown, PDF), and source-to-CAD visual QA.

## Mandatory Principles
1. **Discover & Adhere to Verified Schemas**: Use only discovered CADCraft MCP tools (`execute`, `new_drawing`, `open`, `save`, `inspect_drawing`, `query_entities`, `find_text`, `render`, `command_line`, `script`, `cancel`). Never invent tool names, parameters, or return fields.
2. **Strict Phase Separation**: Maintain clear boundaries between sketch interpretation, geometry planning, user approval, CAD generation, geometric validation, visual QA, and deliverables.
3. **No Fabricated Dimensions**: Never invent dimensions that the sketch does not establish. All dimensions must be categorized as `explicit`, `estimated`, or `inferred`.
4. **Explicit Uncertainty Logging**: Record all assumptions, ambiguities, and estimated values in an uncertainty log before drafting.
5. **Mandatory User Approval Gate**: Never generate final CAD geometry or modify an existing drawing without explicit user approval of the proposed layout.
6. **Isolated Drawing Sessions**: Initialize disposable drawing sessions (`new_drawing(metric=true)`) for new tasks; never erase or overwrite existing user drawings without explicit authorization.
7. **Rigorous Validation & Visual QA**: A generated drawing is not necessarily a correct drawing. Perform both automated geometric verification and manual/raster visual QA against the source sketch before declaring success.
8. **Professional Review Boundary**: Always report regulatory, structural, and life-safety compliance as unverified, subject to licensed professional review.

## Workflow

The complete end-to-end process follows seven disciplined phases:
`Sketch → Interpretation → User Approval → CAD Generation → Geometric Validation → Visual QA & Source Comparison → Final Deliverables`.

### Phase 1: Discover Capabilities & Gather Requirements
Inspect connected CADCraft MCP tool inventory and input schemas.
Refer to [references/mcp-capabilities.md](references/mcp-capabilities.md) and [references/architectural-element-library.md](references/architectural-element-library.md).
Identify:
- Source sketch image, scan, or textual brief.
- Specified dimensions and units (metric millimeters or imperial feet/inches).
- Overall building footprint and required room program.
- Openings (doors, windows) and circulation paths.
- Identified furniture, sanitary fixtures, kitchen fittings, or structural elements.
- Desired output formats (`.dxf`, `.png`, `.svg`, `.pdf`).

### Phase 2: Interpret Sketch & Classify Dimensions
Extract visible walls, wall junctions, room boundaries, openings, elements, and annotations using pluggable multimodal vision providers (Gemini 2.5 Flash, GPT-4o, Antigravity Agent native vision, or deterministic mock).
Classify every measurement and recognized element as:
- `explicit`: Hand-written dimensions or explicitly drawn element symbols on the sketch.
- `estimated`: Proportional measurements derived from scale.
- `inferred`: Architectural defaults (standard wall thickness, door widths, right angles, sanitary fixture in bathroom).
- `proposed`: Agent-suggested spatial layout additions (requires explicit user confirmation).

Log structured vision execution records conforming to [schemas/vision-execution-record.schema.json](schemas/vision-execution-record.schema.json).
Read [workflows/interpret-sketch.md](workflows/interpret-sketch.md) and refer to [references/sketch-interpretation-contract.md](references/sketch-interpretation-contract.md), [references/source-traceability.md](references/source-traceability.md), [references/vision-provider-contract.md](references/vision-provider-contract.md), [references/vision-integration-guide.md](references/vision-integration-guide.md), [references/residential-drawing-standards.md](references/residential-drawing-standards.md), and [references/architectural-element-library.md](references/architectural-element-library.md).
Benchmark accuracy and edge-case resilience are evaluated against [schemas/vision-benchmark-result.schema.json](schemas/vision-benchmark-result.schema.json) and [references/vision-benchmark.md](references/vision-benchmark.md).

### Phase 3: Build Structured Model & Obtain User Approval (Approval Gate)
Synthesize the geometry into a coordinate-based model conforming to [schemas/floor-plan-model.json](schemas/floor-plan-model.json) with status `awaiting_approval`.
Ensure:
- Origin `(0, 0)` is established at the bottom-left corner of the exterior perimeter.
- Wall endpoints and thicknesses are assigned to standard AIA layers.
- Openings are assigned to host walls with explicit center coordinates and widths.
- Uncertainties are enumerated with proposed values, confidence levels, and impacts.

Generate structured review package conforming to [schemas/approval-package.schema.json](schemas/approval-package.schema.json) and Markdown proposal.
Present the structured proposal and uncertainty log to the user.
Wait for explicit human confirmation or corrections before drafting.
Refer to [references/approval-security.md](references/approval-security.md):
- AI agents and automated bots are strictly prohibited from self-approving.
- Placeholder reviewer identities (`Jane Doe`, `John Doe`, etc.) are rejected in production mode.
- Plain-text reviewer assertions are logged with `auth_method: "identity_assertion"` and explicit security warnings.
- Any subsequent geometry modification immediately invalidates the approval revision hash.
**DO NOT proceed to Phase 4 without explicit human approval.**

### Phase 4: Deterministic CAD Generation
Translate the approved model into CADCraft MCP operations via [workflows/generate-drawing.md](workflows/generate-drawing.md):
1. Initialize drawing with `new_drawing(metric=true)`.
2. Establish standard AIA layers (`A-WALL-EXTR`, `A-WALL-INTR`, `A-DOOR`, `A-GLAZ`, `A-FURN`, `A-FIXT`, `A-STAIR`, `A-COLS`, `A-FLOR-FIN`, `A-ANNO-TEXT`, `A-ANNO-DIMS`).
3. Draw exterior and interior double walls with clean openings, transverse jamb end-caps sealing wall cavities, and T-junction cavity trimming per [references/architectural-drafting-standards.md](references/architectural-drafting-standards.md).
4. Draw door leaves (inward/outward single-leaf, double-leaf, sliding) on `A-DOOR` and glazing (casement, sliding) on `A-GLAZ` per [references/architectural-drafting-standards.md](references/architectural-drafting-standards.md).
5. Register and insert approved architectural element blocks (`block`, `insert`) from [references/architectural-element-library.md](references/architectural-element-library.md) on `A-FURN`, `A-FIXT`, `A-STAIR`, and `A-COLS`.
6. Apply room floor finish boundaries and optional tile hatches (`hatch`) on `A-FLOR-FIN` where specified.
7. Configure tiered dimension chains on `A-ANNO-DIMS`, sheet title block header, and conditional North Arrow per [references/dimensioning-and-annotations.md](references/dimensioning-and-annotations.md).
8. Insert centered, non-colliding room labels on `A-ANNO-TEXT` (use stacked text in narrow circulation spaces).
9. Frame viewport using `execute(command="zoom", params={"mode": "extents"})`.

### Phase 5: Geometric & Topological Validation
Execute automated geometric validation per [references/geometry-validation.md](references/geometry-validation.md), [references/validation-checklist.md](references/validation-checklist.md), and [workflows/validate-and-export.md](workflows/validate-and-export.md):
1. Query active topology via `inspect_drawing(entities=true)`.
2. Verify bounding extents match building envelope plus dimension margins.
3. Verify entity counts and ensure default layer `0` contains zero entities.
4. Verify all room label centroids reside inside room polygons.

### Phase 6: Mandatory Visual QA & Source Comparison (Visual Quality Gate)
Execute unified Architectural & Engineering QA via `scripts/architectural_qa.py` (refer to [references/architectural-qa.md](references/architectural-qa.md) and [references/end-to-end-pipeline.md](references/end-to-end-pipeline.md)):
**A generated CAD drawing is not necessarily a correct drawing.** Before accepting or delivering:
1. Render high-resolution preview via `render(fit=true)` or raster preview export.
2. Classify all detected discrepancies under the 4-tier architectural severity model: `blocking_discrepancy`, `major_discrepancy`, `warning`, or `informational`.
3. Out-of-scale sketch reasoning: When handwritten annotations conflict with distorted pixel aspect ratios, verify explicit dimensions govern and classify discrepancy as a non-fatal warning (`out_of_scale_source_sketch`).
4. Duplicate entity detection: Audit CAD model entities for identical IDs across walls, openings, and rooms.
5. Compare against original sketch: Confirm opening orientations, door swing arcs, and room adjacencies strictly match the sketch without silent geometric drift.
6. Non-destructive reporting: Visual QA findings are auditable review evidence; they never silently alter approved CAD geometry.

### Phase 7: Deliver Final Deliverables
1. Save master vector DXF (single-storey) or per-floor DXF files (`<project>-level-01.dxf`, `<project>-level-02.dxf` for multi-storey projects conforming to [references/multi-storey-floor-plans.md](references/multi-storey-floor-plans.md)).
2. Save structured vision execution record: `<drawing-name>.vision-execution.json` conforming to [schemas/vision-execution-record.schema.json](schemas/vision-execution-record.schema.json) capturing model ID, source SHA-256, validation, and duration.
3. Generate companion BIM handoff metadata: `<drawing-name>.handoff.json` conforming to [schemas/bim-handoff.schema.json](schemas/bim-handoff.schema.json) and documented in [references/bim-handoff-contract.md](references/bim-handoff-contract.md).
4. Compile architectural documentation and schedules: `<drawing-name>.report.json`, `<drawing-name>.report.md`, and optional `<drawing-name>.report.pdf` conforming to [schemas/architectural-report.schema.json](schemas/architectural-report.schema.json) and documented in [references/architectural-reporting-guide.md](references/architectural-reporting-guide.md).
5. Export visual preview PNG: `save(path=".../floor-plan.png")`.
6. Compile Visual QA Discrepancy Report: `<drawing-name>.visual-qa.json` and `<drawing-name>.visual-qa.md` with severity counts and discrepancy breakdown.
7. Verify files on disk (existence and non-zero size).
8. Deliver structured acceptance report with PASSED / FAILED / UNVERIFIED statuses and non-compliance disclaimer.

### Phase 8: Independent Quality Auditing & Downstream Preflight (Milestone 10)
Execute automated post-generation checks before external handoff:
1. **Independent Structural DXF Inspection**: Run scripts/dxf_inspector.py per [references/dxf-inspection.md](references/dxf-inspection.md) to verify =4 (mm), DXF version, AIA layer adherence, zero entities on layer 0, duplicate entity elimination, degenerate segment (<10mm) absence, and model-to-DXF-to-BIM cross-consistency.
2. **Downstream BIM Integration Validation**: Run scripts/bim_integration_validator.py per [references/bim-integration-validation.md](references/bim-integration-validation.md) to verify semantic handoff contract, window sill heights (default 900mm), and execute genuine downstream preflight inspection (dxf_to_3d_bim inspect) and intermediate model preparation (dxf_to_3d_bim prepare) when dxf-to-3d-bim is present.
3. **Real-World Architectural Benchmark Validation**: Benchmark vision models against the 6 canonical architectural categories in 	ests/benchmark/ using scripts/benchmark_engine.py per [references/real-world-benchmark.md](references/real-world-benchmark.md) and [references/vision-accuracy-metrics.md](references/vision-accuracy-metrics.md). Enforce strict provenance tagging (
eal_api, gent_native, mocked).
4. **Production Reliability & Atomic File Operations**: Employ scripts/pipeline_reliability.py and scripts/performance_profiler.py per [references/production-reliability.md](references/production-reliability.md) for retry backoff with jitter on transient errors, atomic file writes with automatic rollback, secret masking, and phase-level resource profiling.


### Phase 9: Professional Drawing Presentation, Sheet Printing & Release Packaging (Milestone 11)
Produce publication-grade deliverables and assemble isolated project release packages via `scripts/release_packager.py`:
1. **Professional Visual Drawing Hierarchy**: Enforce AIA lineweights (0.50mm exterior walls/columns, 0.35mm interior partitions/stairs, 0.25mm doors/windows/text, 0.18mm dimensions/furniture, 0.13mm finishes) and explicit non-silent window sill height provenance (`assumed_default_unverified` for 900mm fallback) per [references/professional-drawing-standards.md](references/professional-drawing-standards.md).
2. **Dimensioning & Annotation Engine**: Generate 3-tier dimension chains (Tier 1 overall footprint, Tier 2 chained exterior openings, Tier 3 internal room callouts) with automated collision detection and offset resolution via `scripts/dimension_engine.py` per [references/dimensioning-engine.md](references/dimensioning-engine.md).
3. **Printable Vector Drawing Sheets**: Render vector PDF sheets in standard ISO formats (A4 through A1) at architectural scales (1:50, 1:100, 1:200) with strict viewport fitting (`ScaleOverflowError`), ANSI/ISO/AIA title blocks, and conditional North Arrow validation via `scripts/sheet_generator.py` per [references/drawing-sheets-and-scales.md](references/drawing-sheets-and-scales.md).
4. **Production Release Packaging**: Assemble structured project packages under `output/<project_name>/` containing `source/`, `review/`, `drawings/`, `sheets/`, `handoff/`, `reports/`, `qa/`, and a cryptographic `manifest.json` with SHA-256 hashes for all deliverables via `scripts/release_packager.py` per [references/release-packaging.md](references/release-packaging.md).
5. **Release Integrity Verification**: Audit deliverable integrity via `ReleasePackager.verify_package_integrity(package_dir)` and enforce AI agent self-approval security gates.


### Phase 10: Real-World Pilot Validation, Benchmarking & Acceptance (Milestone 12)
Execute empirical validation across the dedicated 22-sample pilot dataset via `scripts/pilot_benchmark_runner.py`:
1. **Dedicated 22-Sample Pilot Dataset**: Test against 12 challenge categories (clean, rough pencil, incomplete loops, arithmetic contradictions, hardware scan skew 7.5°/15°, low-res mobile photos, non-rectangular footprints, varied opening types, 5+ room layouts, multi-storey, multi-page PDF sets) documented in [references/real-world-pilot-validation.md](references/real-world-pilot-validation.md).
2. **Independent Benchmark Methodology**: Execute spatial bipartite matching for walls, openings, rooms, and dimensions with strict execution modality segregation (`real_api`, `agent_native`, `mocked`) documented in [references/independent-benchmark-methodology.md](references/independent-benchmark-methodology.md).
3. **Formal Production Acceptance Criteria**: Evaluate against the 10 engineering criteria and classify outcomes (`ACCEPTED_FOR_CONTROLLED_PILOT`, `ACCEPTED_WITH_LIMITATIONS`, `NOT_READY_FOR_PRODUCTION`) documented in [references/production-acceptance-criteria.md](references/production-acceptance-criteria.md).
4. **Asserted Identity Review Governance**: Clarify human review as an asserted identity (`auth_method: "identity_assertion"`), disclaim professional licensing authentication, and enforce security blocks against AI agent self-approval.

### Phase 11: Real AI Vision Accuracy, Provider Validation & Benchmark Decoupling (Milestone 13)
Execute decoupled multimodal AI vision inference and independent architectural validation via `scripts/run_vision_pilot.py` and `scripts/pilot_benchmark_runner.py`:
1. **Strict Ground-Truth Isolation**: Vision inference receives only source sketch bytes and prompt instructions; zero access to ground-truth coordinates or answers. Predictions are cached independently in `tests/benchmark/pilot_dataset/predictions/` and evaluated post-hoc.
2. **Pluggable Multimodal Interface**: Support Google Gemini (`gemini-2.5-flash`), OpenAI (`gpt-4o`), Antigravity Agent native vision, and Mock simulation with zero silent fallback to mock when external providers are requested without credentials. Pre-flight `--dry-run` inspection verifies configurations without network requests per [references/vision-provider-validation.md](references/vision-provider-validation.md).
3. **8-Domain Architectural Vision Prompt**: Enforce systematic visual extraction across Envelope, Partitions, Doors, Windows, Rooms, Handwritten Dimensions, Vertical Circulation, and Contradictions with a strict anti-extrapolation prohibition.
4. **Observation Evidence & Revision Audit**: Track `source_evidence`, `review_status`, and immutable `revision_history` entries via `apply_human_correction()` with SHA-256 state tracking.
5. **Decoupled Accuracy Evaluation**: Measure wall bipartite spatial matching, opening classification, room polygon IoU, and numeric dimension accuracy per [references/real-ai-vision-accuracy.md](references/real-ai-vision-accuracy.md).
6. **Independent Architectural Drawing Review**: Audit generated CAD outputs against the 12-item architectural drafting checklist per [references/independent-drawing-review.md](references/independent-drawing-review.md) and verify downstream 3D BIM generation with `dxf-to-3d-bim` per [references/milestone-13-results.md](references/milestone-13-results.md).

## Recovery
If an MCP call fails:
1. Inspect the error message and tool schema.
2. Check server status and backend connectivity.
3. Retry idempotent commands safely.
4. If an unrecoverable failure occurs, halt and report the exact error with context.
