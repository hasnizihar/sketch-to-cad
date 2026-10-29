# Sketch Interpretation Contract

This reference defines the formal architectural contract for converting hand-drawn sketches and scanned floor plans into structured observations and canonical models within Sketch-to-CAD.

---

## 1. Supported Input Formats & Ingestion

The sketch interpretation engine supports:
- **Image Formats**: `.jpg`, `.jpeg`, `.png` (RGB/Grayscale, arbitrary resolutions).
- **Document Formats**: `.pdf` (single-page or multi-page architectural plan sets).
- **Multi-Floor Documents**: Multi-page PDFs where each page represents a distinct building level.

### Ingestion Contract:
1. **Source Preservation**: Original source sketches are treated as read-only artifacts and are NEVER modified or overwritten.
2. **Metadata Capture**: Ingestion extracts and persists `source_file`, `file_type`, `dimensions_pixels`, `dpi`, `page_number`, `total_pages`, `orientation_degrees`, and `preprocessing_applied`.
3. **Deterministic Preprocessing**: Only deterministic transformations (RGB normalization, EXIF orientation correction) are applied.

---

## 2. Structured Observation Schema

Extracted visual features are validated against `skills/sketch-to-cad/schemas/sketch-observations.schema.json` before geometric reconstruction.

### Key Observation Entities:
- **`walls`**:
  - `id`: Unique identifier (e.g., `W-EXT-NORTH`, `W-INTR-01`).
  - `wall_type`: `exterior`, `interior`, `partition`, `low_wall`.
  - `start_point_pixel`, `end_point_pixel`: Coordinates in image pixel space.
  - `thickness_mm`: Explicitly annotated or `null`.
  - `thickness_category`: `explicit`, `estimated`, `inferred`, `unknown`.
  - `source_bbox`: `[ymin, xmin, ymax, xmax]` in normalized `0.0..1.0` image space.
- **`openings`**:
  - `id`: Opening identifier (e.g., `D-01`, `W-01`).
  - `type`: `door`, `window`, `cased_opening`.
  - `width_mm`: Explicit width or `null`.
  - `swing_direction`: `inward_left`, `inward_right`, `outward_left`, `outward_right`, `sliding`, or `null`.
  - `host_wall_ref`: Associated host wall ID.
- **`rooms`**:
  - `id`: Room identifier (e.g., `R-01`).
  - `raw_label`: Verbatim text label from sketch (e.g., `"LIVING / DINING"`).
  - `standardized_type`: Standardized functional type.
  - `approx_width_mm`, `approx_depth_mm`: Annotated room dimensions.
- **`dimensions`**:
  - `id`: Dimension identifier.
  - `source_text`: Verbatim handwritten or printed dimension text (e.g., `"8000"`, `"3.60 m"`).
  - `value_mm`: Value converted to millimeters.
  - `category`: Provenance category (see Section 3).
  - `target_entity_type`: `overall_width`, `overall_depth`, `room_width`, `wall_thickness`, etc.
- **`stairs` & `columns`**:
  - Vertical circulation and structural elements with riser counts and direction hints.
- **`uncertainties`**:
  - Explicit list of missing dimensions, ambiguous symbols, and arithmetic contradictions.

---

## 3. Dimension Provenance & Categorization

To maintain architectural integrity and prevent AI hallucination, EVERY dimension extracted from a sketch MUST be classified into one of five strict categories:

| Category | Definition | Handling in Pipeline |
| :--- | :--- | :--- |
| **`explicit`** | Numbers and units explicitly handwritten or printed on the sketch. | Directly drafted; highest priority in geometry reconstruction. |
| **`estimated`** | Estimated by architectural convention or standard element sizes (e.g., 200mm exterior wall, 900mm entry door). | Drafted with standard defaults; logged in uncertainties for human review. |
| **`inferred`** | Calculated algebraically from other explicit dimensions (e.g., total width minus room A width). | Verified against overall envelope; flagged if contradictory. |
| **`proposed`** | Suggested by the AI to resolve an ambiguous or missing dimension. | Clearly highlighted in review package; requires explicit human confirmation. |
| **`unknown`** | Completely absent from source sketch with no reliable anchor. | Set to `null`; flagged as a **`blocker`** uncertainty. |

> [!CAUTION]
> **No Fabricated Dimensions**: The AI agent must never invent or fabricate real-world millimeter dimensions from pixel measurements without an explicit scale anchor.

---

## 4. Geometric Reconstruction & Contradiction Detection

The geometric reconstruction engine (`scripts/sketch_interpreter.py`) applies deterministic rules to convert observations into 2D CAD geometry:

1. **Orthogonal Snapping**:
   - Wall angles within $\pm 5^\circ$ of $0^\circ, 90^\circ, 180^\circ, 270^\circ$ are snapped to strict orthogonal coordinates.
   - Genuinely angled walls (e.g., $15^\circ, 30^\circ, 45^\circ$) are **preserved** with exact angles and marked `is_orthogonal: false`. Angled geometry is never forced to orthogonal.
2. **Wall Connectivity**:
   - Builds an endpoint graph to detect dangling walls and unclosed exterior boundaries.
3. **Arithmetic Contradiction Detection**:
   - Verifies whether interior room dimension chains match the overall building envelope.
   - Example: If overall envelope is $8000\text{ mm}$, but interior room dimensions sum to $4500 + 4600 = 9100\text{ mm}$, a **`blocker`** conflict (`arithmetic_mismatch`) is generated.
   - The engine **NEVER** silently stretches, compresses, or warps rooms to force a fit.
4. **Draft Model Compilation**:
   - Compiles a canonical `floor-plan-model.json` with status strictly set to `"awaiting_approval"`.
   - Embeds source traceability metadata on every wall, opening, and room.

