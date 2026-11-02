# Sketch-to-CAD Architectural Vision Benchmark Dataset

This directory contains the **Real-World Architectural Benchmark Dataset** and automated evaluation tools for the Sketch-to-CAD system.

---

## 1. Directory Structure

- `images/`: High-resolution input raster floor plans (PNG, JPEG).
- `pdfs/`: Multi-page architectural documents (PDF).
- `ground_truth/`: Certified reference geometry (`.ground_truth.json`) with exact millimeter coordinates.
- `metadata/`: Cryptographic catalog (`dataset_manifest.json`) indexing all samples with SHA-256 hashes and dimensions.
- `results/`: Output benchmark evaluation deliverables (`benchmark_report.json` and `benchmark_report.md`).

---

## 2. Benchmark Categories

| Category | Identifier | Primary Input Challenge | Source File |
| :--- | :--- | :--- | :--- |
| **Category A** | `BENCH-CAT-A-01` | Clean orthogonal hand plan with full explicit dimensions | `sample-a-clean-ortho.png` |
| **Category B** | `BENCH-CAT-B-01` | Rough hand sketch with uneven lines and arithmetic mismatches | `sample-b-rough-sketch.jpg` |
| **Category C** | `BENCH-CAT-C-01` | Incomplete plan with missing depth dimension and unclosed envelope | `sample-c-incomplete.png` |
| **Category D** | `BENCH-CAT-D-01` | Complex non-rectangular plan with 45° chamfered exterior wall | `sample-d-complex-nonrect.png` |
| **Category E** | `BENCH-CAT-E-01` | Multi-storey residential PDF with vertical stair alignment | `sample-e-multistorey.pdf` |
| **Category F** | `BENCH-CAT-F-01` | Low-quality optical degradation: perspective rotation, lighting shadows, blur | `sample-f-lowqual-tilted.jpg` |

---

## 3. Running the Benchmark

Run benchmark evaluation across all 6 categories:
```bash
python scripts/benchmark_engine.py
```

Outputs are written to:
- `tests/benchmark/results/benchmark_report.json`
- `tests/benchmark/results/benchmark_report.md`

---

## 4. Evaluation Metrics

Evaluated through spatial bipartite matching:
- **Walls**: Spatial endpoint tolerance ($\le 200\text{ mm}$), Precision, Recall, F1 score.
- **Openings**: Center position proximity ($\le 300\text{ mm}$), width error, type accuracy.
- **Rooms**: Polygon IoU ($\ge 0.30$), net square meter area relative error %, label accuracy.
- **Dimensions**: Extracted handwritten values matching within $50\text{ mm}$ tolerance.

---

## 5. Benchmark Integrity Notice

To maintain strict scientific and professional integrity:
- If executed without external vision API credentials, evaluation runs in deterministic mock baseline mode (`execution_type: mocked`).
- Mock baseline scores confirm evaluation harness correctness; they are **never** represented as genuine multimodal AI model accuracy.
