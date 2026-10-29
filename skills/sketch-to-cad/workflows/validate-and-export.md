# Workflow: Validate and Export

This workflow establishes the rigorous comparison between the active CAD drawing and the approved [`floor-plan-model.json`](../schemas/floor-plan-model.json).

## Phase 1: Automated Model-to-Drawing Geometry Comparison

Call `inspect_drawing(entities=true)` and parse the JSON payload:

1. **Envelope Extents Check**:
   - Compare `extents: [[min_x, min_y], [max_x, max_y]]` with `model.envelope`.
   - Dimension extents will extend slightly beyond walls; ensure wall geometry falls strictly within $[0, 0]$ to $[\text{width}, \text{depth}]$.
2. **Layer Allocation Check**:
   - Verify all active AIA layers exist in `layers` (`A-WALL-EXTR`, `A-WALL-INTR`, `A-DOOR`, `A-GLAZ`, `A-FURN`, `A-FIXT`, `A-STAIR`, `A-COLS`, `A-FLOR-FIN`, `A-ANNO-TEXT`, `A-ANNO-DIMS`).
   - Ensure default layer `0` contains zero geometry lines or block references.
3. **Architectural Elements & Blocks Check**:
   - Verify count of `Block Reference` entities matches approved `model.elements` count.
   - Verify all unique `blockId` names appear in `drawing.blocks`.
   - Confirm element insertion positions $(X, Y)$ reside within exterior envelope bounds and assigned room polygons.
4. **Floor Finishes & Tile Hatches Check**:
   - Verify count of `Hatch` entities matches number of defined finishes in `model.finishes`.
   - Verify all hatches are assigned to `A-FLOR-FIN`.
5. **Room Labels Check**:
   - Call `find_text()` or inspect text entities.
   - Verify every room name in `model.rooms` appears exactly once.
   - Confirm insertion point $(x, y)$ is within that room's boundary.
6. **Opening Counts Check**:
   - Verify count of Arc entities equals number of swing doors in `model.openings`.
   - Verify count of glazing lines matches expected window jamb/sash count.

---

## Phase 2: Mandatory Visual QA & Source Comparison

**A generated CAD drawing is not necessarily a correct drawing.** Do not mark a drawing accepted merely because entities were drawn or DXF exported without errors.

1. Call `render(fit=true)` or export a preview image:
2. Visually verify the preview against the source sketch:
   - **Dimension Readability**: Confirm all numerical values (e.g. `8000`, `8700`) and dimension tick marks are clearly visible, unclipped, and legible.
   - **Opening Alignment & Wall Faces**: Confirm doors are placed on the intended exterior/interior walls (e.g., East wall vs. North wall).
   - **Jamb Closures**: Confirm that wall cuts have transverse jamb end-caps sealing the wall thickness rather than showing hollow open cavities.
   - **Circulation & Labels**: Confirm room titles do not collide with walls, door swing paths, or adjacent labels.
3. If any visual check fails, halt acceptance, rectify the drawing geometry, and re-render.

---

## Phase 3: Deliverables Export

Save drawing and exports to explicit output destinations:
1. **Canonical Drawing (DXF)**:
   ```json
   save(path=".../floor-plan.dxf")
   ```
2. **Structured Companion Metadata (BIM Handoff JSON)**:
   Compiled automatically via `compile_bim_handoff(...)` or `build_drawing(..., output_handoff_path=".../floor-plan.handoff.json")`.
   Strictly validated against [`bim-handoff.schema.json`](../schemas/bim-handoff.schema.json).
3. **Architectural Schedules & Reports (JSON + MD + PDF)**:
   Compiled automatically via `compile_architectural_report(...)` or `build_drawing(..., generate_report=True)`.
   Strictly validated against [`architectural-report.schema.json`](../schemas/architectural-report.schema.json).
4. **Visual Preview (PNG)**:
   ```json
   save(path=".../floor-plan.png")
   ```
5. Verify on disk that all deliverable files exist and have non-zero file sizes.

---

## Phase 4: Structured Acceptance Report

Deliver the final validation report categorizing checks into **Passed**, **Failed**, and **Unverified**:

```markdown
### CAD Validation & Delivery Report

#### 1. Geometry & Topological Checks
- **Building Footprint**: 8000mm x 8700mm [PASSED]
  - Drawing Extents: X[-1000 to 9400], Y[-1000 to 10000] (including dimension witness lines).
- **Wall Envelope**: Double-wall construction, all openings cut cleanly with jamb end-caps [PASSED].
- **Layer Architecture**: AIA standard layers populated, layer 0 empty [PASSED].
- **Openings**: 8 doors, 6 windows verified in position and swing direction [PASSED].
- **Elements & Blocks**: 8 block references registered and inserted [PASSED].
- **Finishes & Hatches**: 1 tile grid pattern hatch on A-FLOR-FIN [PASSED].
- **Dimension Readability**: Dimension text legible at standard zoom with zero title collisions [PASSED].
- **Room Labels**: 8 rooms labeled at clear centroids with no line collisions [PASSED].

#### 2. Downstream BIM Handoff Contract
- **Contract Schema**: `bim-handoff.schema.json` v1.0.0 [PASSED]
- **Companion File**: `floor-plan.handoff.json` (Valid JSON Schema Draft-07) [PASSED]
- **Vertical Parameters**: Storey elevations and opening heights explicitly stored as `null` for downstream human approval gate [PASSED]
- **BIM Handshake**: Verified for ingestion by `dxf-to-3d-bim`.

#### 3. Architectural Documentation & Schedules (Milestone 5)
- **Report Schema**: `architectural-report.schema.json` v1.0.0 [PASSED]
- **Room Schedule**: Net areas calculated via Shoelace formula, perimeters, internal dimensions [PASSED]
- **Opening Schedules**: Separate Door and Window schedules with validated host walls [PASSED]
- **Element Inventory**: Category & block aggregations + itemized instance coordinates [PASSED]
- **Finish Schedule**: Floor finish zones and material audit [PASSED]
- **Deliverables**: `.report.json`, `.report.md`, `.report.pdf` [PASSED]

#### 4. Unverified Scope / Compliance Notice
- **Structural Load-Bearing**: Unverified. Requires review by a licensed structural engineer.
- **Egress / Life-Safety Codes**: Unverified. Subject to local municipal building codes.

#### 5. Output Artifacts
- DXF Drawing: `residential-floor-plan.dxf` (Verified: >35KB)
- BIM Handoff JSON: `residential-floor-plan.handoff.json` (Verified: >10KB)
- Architectural Report JSON: `residential-floor-plan.report.json` (Verified: >5KB)
- Architectural Report Markdown: `residential-floor-plan.report.md` (Verified: >4KB)
- Architectural Report PDF: `residential-floor-plan.report.pdf` (Verified: >15KB)
- Visual Preview: `residential-floor-plan.png` (Verified: >300KB)
```
