# Real-World Architectural Sketch Benchmark Dataset Reference

This document establishes the architecture, provenance standards, ground-truth annotation guidelines, and dataset expansion workflows for the **Sketch-to-CAD Real-World Architectural Benchmark Dataset** (`tests/benchmark/`).

---

## 1. Objectives & Provenance Principles

1. **Empirical Architectural Validation**: Validate the entire interpretation and drafting pipeline against real-world and synthetic architectural floor plans reflecting actual drafting variations.
2. **Transparent Provenance**: Every benchmark sample is indexed with its SHA-256 cryptographic digest, original dimensions, and execution mode.
3. **No Synthetic Inflation**: Mock runs are explicitly tagged as `execution_type: mocked`. AI vision accuracy claims require genuine API execution records (`execution_type: real_api` or `agent_native`).

---

## 2. Dataset Categories & Taxonomy

The benchmark dataset encompasses six essential architectural scenarios:

| Category | Identifier | Primary Input Challenge | Ground Truth File |
| :--- | :--- | :--- | :--- |
| **Category A: Clean Hand-Drawn Plans** | `BENCH-CAT-A-01` | Orthogonal single-storey linework with explicit dimension chains and standard openings. | `sample-a-clean-ortho.ground_truth.json` |
| **Category B: Rough Hand-Drawn Plans** | `BENCH-CAT-B-01` | Canonical user sketch with uneven linework, handwriting variance, and arithmetic dimension mismatches. | `sample-b-rough-sketch.ground_truth.json` |
| **Category C: Incomplete Plans** | `BENCH-CAT-C-01` | Missing depth dimension and unclosed building perimeter requiring uncertainty logging. | `sample-c-incomplete.ground_truth.json` |
| **Category D: Complex Residential Plans** | `BENCH-CAT-D-01` | Non-rectangular layout with angled exterior wall (45° chamfer) and non-standard room geometries. | `sample-d-complex-nonrect.ground_truth.json` |
| **Category E: Multi-Storey Plans** | `BENCH-CAT-E-01` | Multi-page PDF floor plans with vertical coordination between Ground and First floor stair cores. | `sample-e-multistorey.pdf` |
| **Category F: Low-Quality Inputs** | `BENCH-CAT-F-01` | Real-world optical degradation: perspective rotation, lighting gradient shadows, and blur. | `sample-f-lowqual-tilted.jpg` |

---

## 3. Directory Layout & Artifact Storage

```
tests/benchmark/
├── images/                   # High-resolution raster images (PNG, JPEG)
│   ├── sample-a-clean-ortho.png
│   ├── sample-b-rough-sketch.jpg
│   ├── sample-c-incomplete.png
│   ├── sample-d-complex-nonrect.png
│   └── sample-f-lowqual-tilted.jpg
├── pdfs/                     # Multi-page architectural documents
│   └── sample-e-multistorey.pdf
├── ground_truth/             # Certified reference geometry & architectural annotations
│   ├── sample-a-clean-ortho.ground_truth.json
│   ├── sample-b-rough-sketch.ground_truth.json
│   ├── sample-c-incomplete.ground_truth.json
│   ├── sample-d-complex-nonrect.ground_truth.json
│   ├── sample-e-multistorey.ground_truth.json
│   └── sample-f-lowqual-tilted.ground_truth.json
├── metadata/                 # Dataset catalog & cryptographic manifest
│   └── dataset_manifest.json
└── results/                  # Automated benchmark evaluation deliverables
    ├── benchmark_report.json
    └── benchmark_report.md
```

---

## 4. Ground-Truth Schema Specification

Each `.ground_truth.json` file contains verified architectural elements in millimeters:

- `sampleId`: Canonical sample identifier (e.g. `BENCH-CAT-A-01`).
- `category`: Category designation matching `dataset_manifest.json`.
- `provenance`: Origin of file (`user_provided`, `synthetic_drawn_for_testing`, or `field_scan`).
- `envelope`: Outer building dimensions (`width`, `depth`, `units`).
- `walls`: Array of wall segments with `id`, `start: [x, y]`, `end: [x, y]`, and `thickness`.
- `openings`: Array of openings with `id`, `type` (`door` or `window`), `center: [x, y]`, `width`, and optional `sillHeight`.
- `rooms`: Array of rooms with `id`, `name`, `polygon: [[x, y], ...]`, and `expectedAreaSqM`.
- `dimensions`: Array of explicit annotations with `id`, `value`, `start: [x, y]`, `end: [x, y]`.
- `uncertainties`: Known ambiguities expected to be flagged by the visual QA inspector.

---

## 5. Adding New Benchmark Samples

To extend the benchmark dataset with a new real-world plan:

1. **Place Source File**: Add image to `tests/benchmark/images/` or PDF to `tests/benchmark/pdfs/`.
2. **Compute SHA-256**: Calculate cryptographic hash of raw file bytes.
3. **Author Ground Truth**: Create `tests/benchmark/ground_truth/<name>.ground_truth.json` specifying verified millimeter geometry.
4. **Register in Manifest**: Add entry to `tests/benchmark/metadata/dataset_manifest.json` updating `totalSamples`.
5. **Run Evaluation**: Execute `python scripts/benchmark_engine.py` to re-score and refresh reports.
