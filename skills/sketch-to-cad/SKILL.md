---
name: sketch-to-cad
description: Interprets rough residential floor-plan sketches, creates a structured and dimensioned layout proposal, obtains explicit approval, generates CAD drawings through connected CADCraft MCP tools, validates geometry, performs visual QA, and exports editable CAD formats.
---

# Sketch-to-CAD

## Purpose
Convert user-provided residential floor-plan sketches and design requirements into structured, reviewable, editable CAD drawings using the connected CADCraft MCP server. The initial preview version supports single-storey residential floor plans.

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
Extract visible walls, wall junctions, room boundaries, openings, elements, and annotations.
Classify every measurement and recognized element as:
- `explicit`: Hand-written dimensions or explicitly drawn element symbols on the sketch.
- `estimated`: Proportional measurements derived from scale.
- `inferred`: Architectural defaults (standard wall thickness, door widths, right angles, sanitary fixture in bathroom).
- `proposed`: Agent-suggested spatial layout additions (requires explicit user confirmation).
Read [workflows/interpret-sketch.md](workflows/interpret-sketch.md) and refer to [references/residential-drawing-standards.md](references/residential-drawing-standards.md) and [references/architectural-element-library.md](references/architectural-element-library.md).

### Phase 3: Build Structured Model & Obtain User Approval (Approval Gate)
Synthesize the geometry into a coordinate-based model conforming to [schemas/floor-plan-model.json](schemas/floor-plan-model.json) with status `awaiting_approval`.
Ensure:
- Origin `(0, 0)` is established at the bottom-left corner of the exterior perimeter.
- Wall endpoints and thicknesses are assigned to standard AIA layers.
- Openings are assigned to host walls with explicit center coordinates and widths.
- Uncertainties are enumerated with proposed values, confidence levels, and impacts.

Present the structured proposal and uncertainty log to the user.
Wait for explicit confirmation or corrections before drafting.
**DO NOT proceed to Phase 4 without explicit user approval.**

### Phase 4: Deterministic CAD Generation
Translate the approved model into CADCraft MCP operations via [workflows/generate-drawing.md](workflows/generate-drawing.md):
1. Initialize drawing with `new_drawing(metric=true)`.
2. Establish standard AIA layers (`A-WALL-EXTR`, `A-WALL-INTR`, `A-DOOR`, `A-GLAZ`, `A-FURN`, `A-FIXT`, `A-STAIR`, `A-COLS`, `A-FLOR-FIN`, `A-ANNO-TEXT`, `A-ANNO-DIMS`).
3. Draw exterior and interior double walls with clean openings and transverse jamb end-caps sealing wall cavities.
4. Draw door leaves and swing arcs on `A-DOOR` and glazing on `A-GLAZ`.
5. Register and insert approved architectural element blocks (`block`, `insert`) from [references/architectural-element-library.md](references/architectural-element-library.md) on `A-FURN`, `A-FIXT`, `A-STAIR`, and `A-COLS`.
6. Apply room floor finish boundaries and optional tile hatches (`hatch`) on `A-FLOR-FIN` where specified.
7. Configure legible architectural dimension styles (`textHeight >= 150mm`, `arrowSize >= 120mm`) and draw dimension chains on `A-ANNO-DIMS`.
8. Insert centered, non-colliding room labels on `A-ANNO-TEXT` (use stacked text in narrow circulation spaces).
9. Frame viewport using `execute(command="zoom", params={"mode": "extents"})`.

### Phase 5: Geometric & Topological Validation
Execute the automated checks in [references/validation-checklist.md](references/validation-checklist.md) and [workflows/validate-and-export.md](workflows/validate-and-export.md):
1. Query active topology via `inspect_drawing(entities=true)`.
2. Verify bounding extents match building envelope plus dimension margins.
3. Verify entity counts and ensure default layer `0` contains zero entities.
4. Verify all room label centroids reside inside room polygons.

### Phase 6: Mandatory Visual QA & Source Comparison (Visual Quality Gate)
**A generated CAD drawing is not necessarily a correct drawing.** Before accepting or delivering:
1. Render high-resolution preview via `render(fit=true)` or raster preview export.
2. Visually verify dimension readability: Confirm numeric values and tick/arrow marks are readable at standard viewing zoom.
3. Compare against original sketch: Confirm opening orientations (e.g. entrance wall face), door swing arcs, and room adjacencies strictly match the sketch.
4. Inspect wall junctions & jambs: Check that wall cavities are capped at openings and partition intersections have 0 gaps or crossing collision lines.
5. Inspect annotation clearance: Verify room labels do not collide with wall linework, door arcs, or circulation boundaries.
6. If any visual check fails, halt acceptance, rectify the vector geometry, and re-render.

### Phase 7: Deliver Final Deliverables
1. Save master vector DXF: `save(path=".../floor-plan.dxf")`.
2. Generate companion BIM handoff metadata: `<drawing-name>.handoff.json` conforming to [schemas/bim-handoff.schema.json](schemas/bim-handoff.schema.json) and documented in [references/bim-handoff-contract.md](references/bim-handoff-contract.md).
3. Export visual preview PNG: `save(path=".../floor-plan.png")`.
4. Verify files on disk (existence and non-zero size).
5. Deliver structured acceptance report with PASSED / FAILED / UNVERIFIED statuses and non-compliance disclaimer.

## Recovery
If an MCP call fails:
1. Inspect the error message and tool schema.
2. Check server status and backend connectivity.
3. Retry idempotent commands safely.
4. If an unrecoverable failure occurs, halt and report the exact error with context.
