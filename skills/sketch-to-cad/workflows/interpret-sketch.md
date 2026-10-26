# Workflow: Interpret Sketch & Obtain Approval

This workflow governs how the AI agent analyzes residential floor-plan sketches, extracts architectural constraints, categorizes uncertainties, and obtains explicit user approval before any CAD drafting begins.

## Step 1: Visual Decomposition & Dimension Classification

Every element extracted from a user sketch or drawing prompt must be tagged with its **Dimension Source**:

1. **`explicit`**:
   - Numbers and units explicitly hand-written or printed on the sketch (e.g., `5.00m`, `3500`, `12'-6"`, `Living 4x5`).
   - These are binding ground truth and must not be altered without user consent.
2. **`estimated`**:
   - Dimensions calculated from image pixel ratios against an explicit reference (e.g., total length is known to be 8m, so an unlabeled bedroom is calculated as ~3.6m).
   - Must be flagged as estimates with an associated confidence level (`low`, `medium`, `high`).
3. **`inferred`**:
   - Geometry assumed based on architectural convention rather than visual measurement:
     - 90° square corners.
     - Wall collinearity and alignments.
     - Standard exterior wall thickness (200mm / 8") and interior partition thickness (100mm / 4.5").
     - Standard door widths (900mm entry, 800mm room, 750mm bath).

---

## Step 2: Extracting Spatial Topology

1. **Building Envelope**:
   - Establish the coordinate origin `(0, 0)` at the bottom-left corner of the exterior perimeter.
   - Establish bounding box: width (along X axis) and depth (along Y axis).
2. **Wall Graph**:
   - Map exterior wall boundaries (`A-WALL-EXTR`) and interior partitions (`A-WALL-INTR`).
   - Note which walls intersect to form corners (L-junctions) and partitions (T-junctions).
3. **Openings (Doors & Windows)**:
   - Identify which wall hosts each opening.
   - Record opening width and center coordinates.
   - For doors: identify hinge side, wall face, and swing direction (inward into room against wall).
4. **Rooms & Labels**:
   - List each room function (Living, Dining, Kitchen, Bedroom, Bathroom, Circulation).
   - Calculate approximate enclosed floor area in square meters (or sq ft).
   - Determine label anchor coordinate (visual centroid of the room).

---

## Step 3: Compiling the Uncertainty & Assumption Log

All ambiguities must be formally cataloged into the `uncertainties` array of the floor-plan model:
- Unclear handwritten text or numbers.
- Unlabeled rooms or missing dimensions.
- Conflicting dimension chains (e.g., sum of room dimensions not matching overall envelope).
- Walls that appear non-perpendicular or misaligned.
- Unspecified window dimensions or door swing directions.

Each entry requires:
- `id`: Unique identifier (`U1`, `U2`, ...).
- `target`: Target room, wall, or opening.
- `description`: Plain-English explanation of what is ambiguous.
- `assumedValue`: The provisional value chosen for the plan.
- `confidence`: `low` | `medium` | `high`.
- `status`: `unresolved`.

---

## Step 4: Generating the Structured Model Proposal

Construct the intermediate JSON document according to [`schemas/floor-plan-model.json`](../schemas/floor-plan-model.json) with:
```json
{
  "status": "awaiting_approval",
  ...
}
```

---

## Step 5: Presentation & User Approval Gate

Present the proposed interpretation to the user in a structured review summary:

```markdown
### Proposed Residential Floor Plan Review

#### 1. Building Envelope & Rooms
- **Footprint**: 6.00 m x 5.00 m (Enclosed Area: 30.0 m²)
- **Rooms Identified**:
  - Studio / Living: 4.20 m x 4.60 m (19.3 m²) [Explicit length, Inferred width]
  - Bathroom: 1.60 m x 2.20 m (3.5 m²) [Estimated from sketch layout]
  - Kitchenette / Entry: 1.60 m x 2.40 m (3.8 m²) [Inferred partition]

#### 2. Openings & Fixtures
- Main Entry Door: 900mm width, opening inward
- Bathroom Door: 750mm width, opening inward against partition
- Living Window: 1800mm width, centered on south wall
- Bathroom Window: 600mm width, high sill on north wall

#### 3. Log of Assumptions & Uncertainties
| ID | Target | Observation / Ambiguity | Assumed Value | Confidence |
| :--- | :--- | :--- | :--- | :--- |
| U1 | South Wall | Dimension written as '6000' with arrow | 6000mm overall width | High |
| U2 | Bath Partition | Wall position unlabeled in sketch | 1600mm from east wall | Medium |
| U3 | Wall Thickness | Not annotated | Ext = 200mm, Int = 100mm | Inferred |

> [!IMPORTANT]
> **Approval Gate**: Do not generate CAD geometry until you confirm or correct these dimensions and layout assumptions.
```

Wait for explicit confirmation or user corrections before proceeding to drafting.
