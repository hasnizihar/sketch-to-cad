# Workflow: Interpret Sketch & Obtain Approval

This workflow governs how the AI agent analyzes residential floor-plan sketches, extracts architectural constraints, categorizes uncertainties, and obtains explicit user approval before any CAD drafting begins.

## Step 1: Input Ingestion & Multi-Format Support

The sketch interpretation pipeline accepts:
- **Raster Formats**: `.jpg`, `.jpeg`, `.png` (scanned drawings, photographed hand sketches).
- **Vector / Scanned Documents**: `.pdf` (single-page or multi-page floor plans).
- **Multi-Floor Identification**: Multi-page PDF sets or multiple drawings separated by level.

Original files are preserved without modification. Source metadata is captured:
- `source_file`, `file_type`, `dimensions_pixels`, `dpi`, `page_number`, `total_pages`, `orientation_degrees`.

---

## Step 2: Visual Decomposition & Dimension Classification

Every element extracted from a user sketch or drawing prompt must be tagged with its **Dimension Source**:

1. **`explicit`**:
   - Numbers and units explicitly hand-written or printed on the sketch (e.g., `5.00m`, `3500`, `12'-6"`, `Living 4x5`).
   - These are binding ground truth and must not be altered without user consent.
2. **`estimated`**:
   - Dimensions calculated from image pixel ratios against an explicit reference (e.g., total length is known to be 8m, so an unlabeled bedroom is calculated as ~3.6m).
   - Must be flagged as estimates with an associated confidence level (`low`, `medium`, `high`).
3. **`inferred`**:
   - Geometry assumed based on architectural convention rather than visual measurement:
     - $90^\circ$ square corners.
     - Wall collinearity and alignments.
     - Standard exterior wall thickness (200mm) and interior partition thickness (150mm).
     - Standard door widths (900mm entry, 800mm room, 750mm bath).
4. **`proposed`**:
   - Elements, fixtures, or spatial furniture arrangements suggested by the AI agent to verify space planning.
   - All `proposed` elements are initialized with `status: "unresolved"` and **must not be drafted** into the CAD model until explicitly approved.
5. **`unknown`**:
   - Completely absent dimensions; flagged as blocker uncertainties.

> [!CAUTION]
> **No Fabricated Dimensions**: The AI agent must never invent or fabricate real-world millimeter dimensions from pixel measurements without an explicit scale anchor.

---

## Step 3: Structured Observation Schema & Traceability

Extracted visual features are validated against [`schemas/sketch-observations.schema.json`](../schemas/sketch-observations.schema.json).

Each extracted entity includes source traceability:
- `source_bbox`: Normalized bounding box `[ymin, xmin, ymax, xmax]` in range `[0.0, 1.0]`.
- `confidence`: Interpretation confidence `[0.0, 1.0]`.
- `provenance`: Origin of observation (`sketch_annotation`, `sketch_symbol`, `architectural_convention`).

See detailed specification in [`references/source-traceability.md`](../references/source-traceability.md).

---

## Step 4: Geometric Reconstruction & Contradiction Detection

`scripts/sketch_interpreter.py` reconstructs coherent 2D geometry:
1. **Orthogonal Snapping**: Walls within $\pm 5^\circ$ of orthogonal snap to $0^\circ, 90^\circ, 180^\circ, 270^\circ$. **Genuinely angled walls are preserved**.
2. **Wall Connectivity**: Validates closed exterior boundary and identifies dangling walls.
3. **Arithmetic Contradiction Detection**: Compares interior room dimension chains against the overall envelope.
   - If sum of room chain exceeds overall dimension (e.g. 9100mm vs 8000mm), a **`blocker`** conflict (`arithmetic_mismatch`) is generated.
   - Rooms are never silently stretched or compressed.

---

## Step 5: Compiling the Draft Model & Approval Package

1. Compiles draft canonical model conforming to [`schemas/floor-plan-model.json`](../schemas/floor-plan-model.json) with status strictly set to `"awaiting_approval"`.
2. Computes deterministic SHA-256 revision hash of model geometry.
3. Generates structured review package conforming to [`schemas/approval-package.schema.json`](../schemas/approval-package.schema.json) and Markdown proposal `<project>.proposal.md`.

---

## Step 6: Mandatory Human Approval Gate

```markdown
> [!IMPORTANT]
> **Mandatory Human Approval Gate**: CADCraft generation must halt until explicit human approval is received.
> Automated AI agents are strictly prohibited from self-approving their own proposals.
```

### Reviewer Decisions Supported:
- **`approve`**: Requires human reviewer name and notes; sets model status to `"approved"`.
- **`reject`**: Records rejection reason; halts drafting.
- **`correct_dimension`**: Updates target dimension, recalculates revision hash.
- **`correct_room_label`**: Updates room label, recalculates revision hash.
- **`resolve_uncertainty`**: Confirms or corrects an unannotated parameter.

Any geometry modification made after package creation invalidates the revision hash, requiring renewed approval.
