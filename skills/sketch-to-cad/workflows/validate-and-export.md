# Workflow: Validate and Export

This workflow establishes the rigorous comparison between the active CAD drawing and the approved [`floor-plan-model.json`](../schemas/floor-plan-model.json).

## Phase 1: Automated Model-to-Drawing Geometry Comparison

Call `inspect_drawing(entities=true)` and parse the JSON payload:

1. **Envelope Extents Check**:
   - Compare `extents: [[min_x, min_y], [max_x, max_y]]` with `model.envelope`.
   - Dimension extents will extend slightly beyond walls; ensure wall geometry falls strictly within $[0, 0]$ to $[\text{width}, \text{depth}]$.
2. **Layer Allocation Check**:
   - Verify all 6 AIA layers exist in `layers`.
   - Ensure default layer `0` contains zero geometry lines.
3. **Room Labels Check**:
   - Call `find_text()` or inspect text entities.
   - Verify every room name in `model.rooms` appears exactly once.
   - Confirm insertion point $(x, y)$ is within that room's boundary.
4. **Opening Counts Check**:
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
2. **Visual Preview (PNG)**:
   ```json
   save(path=".../floor-plan.png")
   ```
3. Verify on disk that both files exist and have non-zero file sizes.

---

## Phase 4: Structured Acceptance Report

Deliver the final validation report categorizing checks into **Passed**, **Failed**, and **Unverified**:

```markdown
### CAD Validation & Delivery Report

#### 1. Geometry & Topological Checks
- **Building Footprint**: 8000mm x 8700mm [PASSED]
  - Drawing Extents: X[-1000 to 9400], Y[-1000 to 10000] (including dimension witness lines).
- **Wall Envelope**: Double-wall construction, all openings cut cleanly with jamb end-caps [PASSED].
- **Layer Architecture**: 6 AIA standard layers populated, layer 0 empty [PASSED].
- **Openings**: 8 doors, 6 windows verified in position and swing direction [PASSED].
- **Dimension Readability**: Dimension text legible at standard zoom [PASSED].
- **Room Labels**: 8 rooms labeled at clear centroids with no line collisions [PASSED].

#### 2. Unverified Scope / Compliance Notice
- **Structural Load-Bearing**: Unverified. Requires review by a licensed structural engineer.
- **Egress / Life-Safety Codes**: Unverified. Subject to local municipal building codes.

#### 3. Output Artifacts
- DXF Drawing: `residential-floor-plan.dxf` (Verified: 68,008 bytes)
- Visual Preview: `residential-floor-plan.png` (Verified: 346,185 bytes)
```
