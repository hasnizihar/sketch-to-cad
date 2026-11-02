# Sketch-to-CAD Real-World Vision Benchmark Report

- **Benchmark Run Timestamp:** `2026-11-02 17:30:43Z`
- **Evaluated Samples Count:** 6
- **Real Multimodal AI Runs:** 0
- **Mocked Baseline Runs:** 6

> [!NOTE]
> **Benchmark Integrity Notice**: Evaluation includes mock baseline runs (`execution_type: mocked`).
> Mock scores measure evaluation pipeline correctness and must NOT be represented as genuine AI vision accuracy.

## Summary Results by Sample

| Sample ID | Category | Type | Walls F1 | Ep. Err (mm) | Openings F1 | Rooms IoU | Dims Acc % | Duration |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `BENCH-CAT-A-01` | Category A | 🔴 Mock | 1.00 | 0 | 1.00 | 1.00 | 100% | 50ms |
| `BENCH-CAT-B-01` | Category B | 🔴 Mock | 1.00 | 0 | 1.00 | 1.00 | 100% | 50ms |
| `BENCH-CAT-C-01` | Category C | 🔴 Mock | 1.00 | 0 | 1.00 | 0.00 | 100% | 50ms |
| `BENCH-CAT-D-01` | Category D | 🔴 Mock | 1.00 | 0 | 1.00 | 1.00 | 100% | 50ms |
| `BENCH-CAT-E-01` | Category E | 🔴 Mock | 1.00 | 0 | 1.00 | 1.00 | 100% | 50ms |
| `BENCH-CAT-F-01` | Category F | 🔴 Mock | 1.00 | 0 | 1.00 | 1.00 | 100% | 50ms |

## Detailed Architectural Findings by Category

### `BENCH-CAT-A-01`: Category A: Clean Hand-Drawn Plans
- **Provenance:** `unknown` | **Execution Type:** `mocked`
- **Provider / Model:** `benchmark_mock_provider` (deterministic_v1)
- **Source Image Hash (SHA-256):** `e6d2d62cec648304...`
- **Wall Detection:** F1 = 1.00 (P=1.00, R=1.00), Mean Endpoint Error: 0.0mm
- **Opening Detection:** F1 = 1.00, Position Error: 0.0mm, Width Error: 0.0mm
- **Room Reconstruction:** IoU = 1.00, Net Area Error = 0.0%, Label Accuracy = 100%
- **Dimension Accuracy:** Numeric Accuracy = 100.0%, Value Error = 0.0mm
- **Uncertainties Logged:** 0 detected vs 0 expected in ground truth
  - *Note:* Execution used mocked or pre-supplied observations. Results do NOT reflect real multimodal AI vision inference.

### `BENCH-CAT-B-01`: Category B: Rough Hand-Drawn Plans
- **Provenance:** `unknown` | **Execution Type:** `mocked`
- **Provider / Model:** `benchmark_mock_provider` (deterministic_v1)
- **Source Image Hash (SHA-256):** `8683c2cd307c28ca...`
- **Wall Detection:** F1 = 1.00 (P=1.00, R=1.00), Mean Endpoint Error: 0.0mm
- **Opening Detection:** F1 = 1.00, Position Error: 0.0mm, Width Error: 0.0mm
- **Room Reconstruction:** IoU = 1.00, Net Area Error = 0.0%, Label Accuracy = 100%
- **Dimension Accuracy:** Numeric Accuracy = 100.0%, Value Error = 0.0mm
- **Uncertainties Logged:** 2 detected vs 2 expected in ground truth
  - *Note:* Execution used mocked or pre-supplied observations. Results do NOT reflect real multimodal AI vision inference.

### `BENCH-CAT-C-01`: Category C: Incomplete Plans
- **Provenance:** `unknown` | **Execution Type:** `mocked`
- **Provider / Model:** `benchmark_mock_provider` (deterministic_v1)
- **Source Image Hash (SHA-256):** `e4974b89ba704d73...`
- **Wall Detection:** F1 = 1.00 (P=1.00, R=1.00), Mean Endpoint Error: 0.0mm
- **Opening Detection:** F1 = 1.00, Position Error: 0.0mm, Width Error: 0.0mm
- **Room Reconstruction:** IoU = 0.00, Net Area Error = 0.0%, Label Accuracy = 0%
- **Dimension Accuracy:** Numeric Accuracy = 100.0%, Value Error = 0.0mm
- **Uncertainties Logged:** 2 detected vs 2 expected in ground truth
  - *Note:* Execution used mocked or pre-supplied observations. Results do NOT reflect real multimodal AI vision inference.
  - *Note:* Incomplete input evaluated: missing depth dimension correctly flagged.

### `BENCH-CAT-D-01`: Category D: Complex Residential Plans
- **Provenance:** `unknown` | **Execution Type:** `mocked`
- **Provider / Model:** `benchmark_mock_provider` (deterministic_v1)
- **Source Image Hash (SHA-256):** `7709f9abe3bd3536...`
- **Wall Detection:** F1 = 1.00 (P=1.00, R=1.00), Mean Endpoint Error: 0.0mm
- **Opening Detection:** F1 = 1.00, Position Error: 0.0mm, Width Error: 0.0mm
- **Room Reconstruction:** IoU = 1.00, Net Area Error = 0.0%, Label Accuracy = 100%
- **Dimension Accuracy:** Numeric Accuracy = 100.0%, Value Error = 0.0mm
- **Uncertainties Logged:** 0 detected vs 0 expected in ground truth
  - *Note:* Execution used mocked or pre-supplied observations. Results do NOT reflect real multimodal AI vision inference.

### `BENCH-CAT-E-01`: Category E: Multi-Storey Plans
- **Provenance:** `unknown` | **Execution Type:** `mocked`
- **Provider / Model:** `benchmark_mock_provider` (deterministic_v1)
- **Source Image Hash (SHA-256):** `4f2006004a22cf48...`
- **Wall Detection:** F1 = 1.00 (P=1.00, R=1.00), Mean Endpoint Error: 0.0mm
- **Opening Detection:** F1 = 1.00, Position Error: 0.0mm, Width Error: 0.0mm
- **Room Reconstruction:** IoU = 1.00, Net Area Error = 0.0%, Label Accuracy = 100%
- **Dimension Accuracy:** Numeric Accuracy = 100.0%, Value Error = 0.0mm
- **Uncertainties Logged:** 0 detected vs 0 expected in ground truth
  - *Note:* Execution used mocked or pre-supplied observations. Results do NOT reflect real multimodal AI vision inference.

### `BENCH-CAT-F-01`: Category F: Low-Quality Inputs
- **Provenance:** `unknown` | **Execution Type:** `mocked`
- **Provider / Model:** `benchmark_mock_provider` (deterministic_v1)
- **Source Image Hash (SHA-256):** `6379dc02c8d88745...`
- **Wall Detection:** F1 = 1.00 (P=1.00, R=1.00), Mean Endpoint Error: 0.0mm
- **Opening Detection:** F1 = 1.00, Position Error: 0.0mm, Width Error: 0.0mm
- **Room Reconstruction:** IoU = 1.00, Net Area Error = 0.0%, Label Accuracy = 100%
- **Dimension Accuracy:** Numeric Accuracy = 100.0%, Value Error = 0.0mm
- **Uncertainties Logged:** 2 detected vs 2 expected in ground truth
  - *Note:* Execution used mocked or pre-supplied observations. Results do NOT reflect real multimodal AI vision inference.
