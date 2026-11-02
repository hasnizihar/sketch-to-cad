# Source-to-CAD Visual QA Report: Residential Hand Sketch Project

- **Source Sketch:** `sketch-before.jpg`
- **CAD Output:** `residential-hand-sketch-project.dxf`
- **Overall Evaluation:** 🟡 REVIEW REQUIRED (Warnings Present)
- **Checks Passed:** 5 / 6
- **Severity Counts:** 0 Blocking, 0 Major, 1 Warning, 5 Informational

## Detailed Feature Checks

| Check | Status | Severity | Findings / Architectural Reasoning |
| :--- | :--- | :--- | :--- |
| `footprint_aspect_ratio` | ⚠️ DISCREPANCY | `warning` | Hand sketch is out-of-scale relative to explicit annotations: sketch image aspect ratio is 1.41 (landscape), but handwritten dimensions establish 8000x8700 mm (ratio 0.92, portrait). Reconstruction correctly honored explicit dimensions over distorted sketch linework. |
| `room_topology_and_count` | ✅ PASS | `informational` | All 3 observed rooms correctly represented in CAD model. |
| `openings_count_and_distribution` | ✅ PASS | `informational` | Openings count verified: 1 doors, 1 windows. |
| `dimensions_fidelity` | ✅ PASS | `informational` | All 2 observed dimensions verified within 50.0mm tolerance. |
| `staircase_alignment` | ✅ PASS | `informational` | Staircases: observed 1, drafted 1. |
| `duplicate_entities` | ✅ PASS | `informational` | Zero duplicate entity IDs detected across walls, openings, and rooms. |

## Architectural QA Policy & Discrepancy Reconciliation

> **Important Principle**: Hand-drawn residential sketches are frequently out-of-scale.
> When explicit handwritten dimensions conflict with image pixel aspect ratios,
> Sketch-to-CAD prioritizes explicit ground-truth dimensions. The resulting ratio difference
> is classified as a warning/informational note, NOT a geometric reconstruction defect.
> Visual QA findings provide auditable review evidence and never automatically alter approved CAD geometry.