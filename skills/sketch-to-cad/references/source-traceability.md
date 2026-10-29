# Source Traceability Reference

This document outlines how architectural entities in generated CAD drawings and BIM models trace back to their origin in the original hand-drawn sketch or document.

---

## 1. Traceability Principles

1. **End-to-End Lineage**: Every wall, door, window, room, and dimension retains an auditable link to its source bounding box in the input sketch.
2. **Normalized Coordinates**: Bounding boxes use normalized image coordinates `[ymin, xmin, ymax, xmax]` in the range `[0.0, 1.0]`, ensuring resolution independence regardless of whether the source is a 72 DPI smartphone photo or a 600 DPI scanner PDF.
3. **Evidence Separation**: Original sketch evidence (pixel bounding box, handwritten text) is kept separate from derived model geometry (millimeter CAD coordinates).

---

## 2. Traceability Schema Structure

Entities in `floor-plan-model.json` and `<project>.handoff.json` incorporate a `source_traceability` object:

```json
{
  "id": "W-EXT-NORTH",
  "type": "exterior",
  "start": [0.0, 8700.0],
  "end": [8000.0, 8700.0],
  "thickness": 200.0,
  "source": "explicit",
  "source_traceability": {
    "source_file": "sketch-before.jpg",
    "page_number": 1,
    "source_bbox": [0.08, 0.10, 0.10, 0.90],
    "raw_annotation": "8000",
    "confidence": 0.96,
    "provenance": "sketch_annotation",
    "review_status": "approved"
  }
}
```

### Traceability Properties:

| Field | Type | Description |
| :--- | :--- | :--- |
| `source_file` | `string` | Base filename of original sketch. |
| `page_number` | `integer` | Page index in source document (1-based). |
| `source_bbox` | `[ymin, xmin, ymax, xmax]` | Normalized bounding box in range `[0.0, 1.0]`. |
| `raw_annotation` | `string` | Original handwritten or printed text string. |
| `confidence` | `number` | Heuristic interpretation confidence `[0.0, 1.0]`. |
| `provenance` | `string` | Source origin: `sketch_annotation`, `sketch_symbol`, `architectural_convention`, `user_correction`. |
| `review_status` | `string` | Review state: `unreviewed`, `approved`, `corrected`. |

---

## 3. Heuristic Confidence Semantics

Confidence values represent heuristic indicators of visual clarity and pattern certainty. They are **not** statistically calibrated probability distributions:

- **`0.90 - 1.00` (High Confidence)**: Crisp, unambiguous handwriting or clear orthogonal drafting lines with explicit numerical dimension tags.
- **`0.75 - 0.89` (Medium Confidence)**: Legible handwriting or standard symbol with slight geometric distortion or partial dimension chain.
- **`< 0.75` (Low Confidence / Flagged)**: Ambiguous line work, unannotated elements, conflicting dimension chains, or non-standard architectural symbols. Automatically logged in `uncertainties`.

---

## 4. Downstream Downlink into BIM & Reports

1. **BIM Handoff (`.handoff.json`)**:
   Entities exported to downstream BIM skills (`dxf-to-3d-bim`) carry the `source` category (`explicit`, `estimated`, `inferred`), enabling BIM modelers to distinguish field-verified dimensions from estimated defaults.
2. **Architectural Reports (`.report.pdf` & `.report.md`)**:
   The Element & Dimension Schedules tabulate the source classification for each wall, opening, and room, providing human certifiers with an immediate audit of non-explicit assumptions.

