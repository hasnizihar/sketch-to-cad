# Sketch-to-CAD Real-World Pilot Benchmark Report (Milestone 13)

- **Benchmark Run Timestamp:** `2026-11-03T12:31:32Z`
- **Total Pilot Samples Evaluated:** 22
- **Agent-Native AI Runs:** 1 (PILOT-02 Authentic User Sketch)
- **Mock Baseline Regression Runs:** 21

> [!IMPORTANT]
> **Provenance & Independence Disclosure**: `PILOT-02` (authentic user villa sketch) was evaluated using independent prediction data extracted via `agent_native` vision inference. Input prompts contain strictly zero ground-truth leakage. Challenge baseline samples verify geometric constraint checking and uncertainty logging without misrepresenting mock baselines as external API runs.

## 1. Category Summary Metrics

| Category | Samples | Mean Wall F1 | Mean Opening F1 | Mean Room IoU | Mean Dim Acc % | Uncertainty Capture % |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Clean Hand-Drawn Plans** | 2 | 1.00 | 1.00 | 1.00 | 100.0% | 100.0% |
| **Category B: Rough Hand-Drawn Plans** | 1 | 0.80 | 0.00 | 0.00 | 100.0% | 50.0% |
| **Rough Pencil Sketches** | 2 | 1.00 | 1.00 | 1.00 | 100.0% | 100.0% |
| **Incomplete & Missing Wall Sketches** | 1 | 1.00 | 1.00 | 1.00 | 100.0% | 100.0% |
| **Contradictory Annotations** | 1 | 1.00 | 1.00 | 1.00 | 100.0% | 100.0% |
| **Rotated & Skewed Scans** | 2 | 1.00 | 1.00 | 1.00 | 100.0% | 100.0% |
| **Low-Resolution & Noisy Mobile Photos** | 1 | 1.00 | 1.00 | 1.00 | 100.0% | 100.0% |
| **Non-Rectangular Footprints** | 4 | 1.00 | 1.00 | 1.00 | 100.0% | 100.0% |
| **Multi-Room Residential Layouts (5+ rooms)** | 3 | 1.00 | 1.00 | 1.00 | 100.0% | 100.0% |
| **Complex Room Junctions & Openings** | 2 | 1.00 | 1.00 | 1.00 | 100.0% | 100.0% |
| **Multi-Storey Residential Sketches** | 2 | 1.00 | 1.00 | 1.00 | 100.0% | 100.0% |
| **Multi-Page PDF Floor Plan Sets** | 1 | 1.00 | 0.00 | 1.00 | 100.0% | 100.0% |

## 2. Per-Sample Detailed Benchmark Results

| Sample ID | Category | Type | Walls F1 | Ep. Err (mm) | Openings F1 | Rooms IoU | Dims Acc % | Uncertainties |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `PILOT-01` | Clean Hand-Drawn Plans | ⚪ Mock Baseline | 1.00 | 0 | 1.00 | 1.00 | 100% | 0/0 |
| `PILOT-02` | Category B: Rough Hand-Drawn Plans | 🟢 Agent-Native | 0.80 | 0 | 0.00 | 0.00 | 100% | 1/2 |
| `PILOT-03` | Rough Pencil Sketches | ⚪ Mock Baseline | 1.00 | 0 | 1.00 | 1.00 | 100% | 0/0 |
| `PILOT-04` | Incomplete & Missing Wall Sketches | ⚪ Mock Baseline | 1.00 | 0 | 1.00 | 1.00 | 100% | 2/2 |
| `PILOT-05` | Contradictory Annotations | ⚪ Mock Baseline | 1.00 | 0 | 1.00 | 1.00 | 100% | 1/1 |
| `PILOT-06` | Rotated & Skewed Scans | ⚪ Mock Baseline | 1.00 | 0 | 1.00 | 1.00 | 100% | 1/1 |
| `PILOT-07` | Rotated & Skewed Scans | ⚪ Mock Baseline | 1.00 | 0 | 1.00 | 1.00 | 100% | 1/1 |
| `PILOT-08` | Low-Resolution & Noisy Mobile Photos | ⚪ Mock Baseline | 1.00 | 0 | 1.00 | 1.00 | 100% | 1/1 |
| `PILOT-09` | Rough Pencil Sketches | ⚪ Mock Baseline | 1.00 | 0 | 1.00 | 1.00 | 100% | 0/0 |
| `PILOT-10` | Non-Rectangular Footprints | ⚪ Mock Baseline | 1.00 | 0 | 1.00 | 1.00 | 100% | 0/0 |
| `PILOT-11` | Non-Rectangular Footprints | ⚪ Mock Baseline | 1.00 | 0 | 1.00 | 1.00 | 100% | 0/0 |
| `PILOT-12` | Non-Rectangular Footprints | ⚪ Mock Baseline | 1.00 | 0 | 1.00 | 1.00 | 100% | 0/0 |
| `PILOT-13` | Multi-Room Residential Layouts (5+ rooms) | ⚪ Mock Baseline | 1.00 | 0 | 1.00 | 1.00 | 100% | 0/0 |
| `PILOT-14` | Multi-Room Residential Layouts (5+ rooms) | ⚪ Mock Baseline | 1.00 | 0 | 1.00 | 1.00 | 100% | 0/0 |
| `PILOT-15` | Complex Room Junctions & Openings | ⚪ Mock Baseline | 1.00 | 0 | 1.00 | 1.00 | 100% | 0/0 |
| `PILOT-16` | Complex Room Junctions & Openings | ⚪ Mock Baseline | 1.00 | 0 | 1.00 | 1.00 | 100% | 1/1 |
| `PILOT-17` | Clean Hand-Drawn Plans | ⚪ Mock Baseline | 1.00 | 0 | 1.00 | 1.00 | 100% | 0/0 |
| `PILOT-18` | Multi-Storey Residential Sketches | ⚪ Mock Baseline | 1.00 | 0 | 1.00 | 1.00 | 100% | 0/0 |
| `PILOT-19` | Multi-Storey Residential Sketches | ⚪ Mock Baseline | 1.00 | 0 | 1.00 | 1.00 | 100% | 0/0 |
| `PILOT-20` | Multi-Page PDF Floor Plan Sets | ⚪ Mock Baseline | 1.00 | 0 | 0.00 | 1.00 | 100% | 0/0 |
| `PILOT-21` | Non-Rectangular Footprints | ⚪ Mock Baseline | 1.00 | 0 | 1.00 | 1.00 | 100% | 0/0 |
| `PILOT-22` | Multi-Room Residential Layouts (5+ rooms) | ⚪ Mock Baseline | 1.00 | 0 | 1.00 | 1.00 | 100% | 0/0 |

## 3. Detailed Architectural Notes by Sample

### `PILOT-01`: Clean Hand-Drawn Plans
- **Execution Type:** `mocked` | **Provider:** `pilot_benchmark_evaluator` (deterministic_pilot_v1)
- **Source SHA-256:** `7c22c95ce5a59383...`
- **Wall Detection:** F1 = 1.00, Mean Endpoint Error = 0.0 mm
- **Opening Detection:** F1 = 1.00, Width Error = 0.0 mm
- **Room Reconstruction:** IoU = 1.00, Net Area Error = 0.0%
- **Dimension Accuracy:** 100.0% within 50mm
- **Uncertainties:** 0 detected / 0 expected in ground truth
  - *Audit Note:* Execution used mocked or pre-supplied observations. Results do NOT reflect real multimodal AI vision inference.

### `PILOT-02`: Category B: Rough Hand-Drawn Plans
- **Execution Type:** `agent_native` | **Provider:** `antigravity_agent` (antigravity-native-vision-v1)
- **Source SHA-256:** `8683c2cd307c28ca...`
- **Wall Detection:** F1 = 0.80, Mean Endpoint Error = 0.0 mm
- **Opening Detection:** F1 = 0.00, Width Error = 0.0 mm
- **Room Reconstruction:** IoU = 0.00, Net Area Error = 0.0%
- **Dimension Accuracy:** 100.0% within 50mm
- **Uncertainties:** 1 detected / 2 expected in ground truth
  - *Audit Note:* Authentic user sketch: handwritten annotations and arithmetic contradiction (1800+4100+3200=9100 vs 8700mm) verified by agent.

### `PILOT-03`: Rough Pencil Sketches
- **Execution Type:** `mocked` | **Provider:** `pilot_benchmark_evaluator` (deterministic_pilot_v1)
- **Source SHA-256:** `bfa74fc0b6854cdf...`
- **Wall Detection:** F1 = 1.00, Mean Endpoint Error = 0.0 mm
- **Opening Detection:** F1 = 1.00, Width Error = 0.0 mm
- **Room Reconstruction:** IoU = 1.00, Net Area Error = 0.0%
- **Dimension Accuracy:** 100.0% within 50mm
- **Uncertainties:** 0 detected / 0 expected in ground truth
  - *Audit Note:* Execution used mocked or pre-supplied observations. Results do NOT reflect real multimodal AI vision inference.

### `PILOT-04`: Incomplete & Missing Wall Sketches
- **Execution Type:** `mocked` | **Provider:** `pilot_benchmark_evaluator` (deterministic_pilot_v1)
- **Source SHA-256:** `e8fbee2a331e4f3f...`
- **Wall Detection:** F1 = 1.00, Mean Endpoint Error = 0.0 mm
- **Opening Detection:** F1 = 1.00, Width Error = 0.0 mm
- **Room Reconstruction:** IoU = 1.00, Net Area Error = 0.0%
- **Dimension Accuracy:** 100.0% within 50mm
- **Uncertainties:** 2 detected / 2 expected in ground truth
  - *Audit Note:* Execution used mocked or pre-supplied observations. Results do NOT reflect real multimodal AI vision inference.
  - *Audit Note:* Incomplete geometry: unclosed south terrace boundary correctly logged in uncertainty register.

### `PILOT-05`: Contradictory Annotations
- **Execution Type:** `mocked` | **Provider:** `pilot_benchmark_evaluator` (deterministic_pilot_v1)
- **Source SHA-256:** `09a0385f1a6508c2...`
- **Wall Detection:** F1 = 1.00, Mean Endpoint Error = 0.0 mm
- **Opening Detection:** F1 = 1.00, Width Error = 0.0 mm
- **Room Reconstruction:** IoU = 1.00, Net Area Error = 0.0%
- **Dimension Accuracy:** 100.0% within 50mm
- **Uncertainties:** 1 detected / 1 expected in ground truth
  - *Audit Note:* Execution used mocked or pre-supplied observations. Results do NOT reflect real multimodal AI vision inference.
  - *Audit Note:* Arithmetic contradiction: internal rooms sum to 6400mm vs 7000mm overall logged in uncertainty register.

### `PILOT-06`: Rotated & Skewed Scans
- **Execution Type:** `mocked` | **Provider:** `pilot_benchmark_evaluator` (deterministic_pilot_v1)
- **Source SHA-256:** `f0103d13631faed8...`
- **Wall Detection:** F1 = 1.00, Mean Endpoint Error = 0.0 mm
- **Opening Detection:** F1 = 1.00, Width Error = 0.0 mm
- **Room Reconstruction:** IoU = 1.00, Net Area Error = 0.0%
- **Dimension Accuracy:** 100.0% within 50mm
- **Uncertainties:** 1 detected / 1 expected in ground truth
  - *Audit Note:* Execution used mocked or pre-supplied observations. Results do NOT reflect real multimodal AI vision inference.
  - *Audit Note:* Rotated scan: rotation detected and logged.

### `PILOT-07`: Rotated & Skewed Scans
- **Execution Type:** `mocked` | **Provider:** `pilot_benchmark_evaluator` (deterministic_pilot_v1)
- **Source SHA-256:** `01e6196227e9f996...`
- **Wall Detection:** F1 = 1.00, Mean Endpoint Error = 0.0 mm
- **Opening Detection:** F1 = 1.00, Width Error = 0.0 mm
- **Room Reconstruction:** IoU = 1.00, Net Area Error = 0.0%
- **Dimension Accuracy:** 100.0% within 50mm
- **Uncertainties:** 1 detected / 1 expected in ground truth
  - *Audit Note:* Execution used mocked or pre-supplied observations. Results do NOT reflect real multimodal AI vision inference.
  - *Audit Note:* Rotated scan: rotation detected and logged.

### `PILOT-08`: Low-Resolution & Noisy Mobile Photos
- **Execution Type:** `mocked` | **Provider:** `pilot_benchmark_evaluator` (deterministic_pilot_v1)
- **Source SHA-256:** `14c676c0acc5bf4e...`
- **Wall Detection:** F1 = 1.00, Mean Endpoint Error = 0.0 mm
- **Opening Detection:** F1 = 1.00, Width Error = 0.0 mm
- **Room Reconstruction:** IoU = 1.00, Net Area Error = 0.0%
- **Dimension Accuracy:** 100.0% within 50mm
- **Uncertainties:** 1 detected / 1 expected in ground truth
  - *Audit Note:* Execution used mocked or pre-supplied observations. Results do NOT reflect real multimodal AI vision inference.
  - *Audit Note:* Low-resolution mobile photo: faint graphite lines flagged for surveyor confirmation.

### `PILOT-09`: Rough Pencil Sketches
- **Execution Type:** `mocked` | **Provider:** `pilot_benchmark_evaluator` (deterministic_pilot_v1)
- **Source SHA-256:** `4ffca215ed572422...`
- **Wall Detection:** F1 = 1.00, Mean Endpoint Error = 0.0 mm
- **Opening Detection:** F1 = 1.00, Width Error = 0.0 mm
- **Room Reconstruction:** IoU = 1.00, Net Area Error = 0.0%
- **Dimension Accuracy:** 100.0% within 50mm
- **Uncertainties:** 0 detected / 0 expected in ground truth
  - *Audit Note:* Execution used mocked or pre-supplied observations. Results do NOT reflect real multimodal AI vision inference.

### `PILOT-10`: Non-Rectangular Footprints
- **Execution Type:** `mocked` | **Provider:** `pilot_benchmark_evaluator` (deterministic_pilot_v1)
- **Source SHA-256:** `22a215a0a3702a8b...`
- **Wall Detection:** F1 = 1.00, Mean Endpoint Error = 0.0 mm
- **Opening Detection:** F1 = 1.00, Width Error = 0.0 mm
- **Room Reconstruction:** IoU = 1.00, Net Area Error = 0.0%
- **Dimension Accuracy:** 100.0% within 50mm
- **Uncertainties:** 0 detected / 0 expected in ground truth
  - *Audit Note:* Execution used mocked or pre-supplied observations. Results do NOT reflect real multimodal AI vision inference.

### `PILOT-11`: Non-Rectangular Footprints
- **Execution Type:** `mocked` | **Provider:** `pilot_benchmark_evaluator` (deterministic_pilot_v1)
- **Source SHA-256:** `22519c6325709a53...`
- **Wall Detection:** F1 = 1.00, Mean Endpoint Error = 0.0 mm
- **Opening Detection:** F1 = 1.00, Width Error = 0.0 mm
- **Room Reconstruction:** IoU = 1.00, Net Area Error = 0.0%
- **Dimension Accuracy:** 100.0% within 50mm
- **Uncertainties:** 0 detected / 0 expected in ground truth
  - *Audit Note:* Execution used mocked or pre-supplied observations. Results do NOT reflect real multimodal AI vision inference.

### `PILOT-12`: Non-Rectangular Footprints
- **Execution Type:** `mocked` | **Provider:** `pilot_benchmark_evaluator` (deterministic_pilot_v1)
- **Source SHA-256:** `4e59ee3344d36594...`
- **Wall Detection:** F1 = 1.00, Mean Endpoint Error = 0.0 mm
- **Opening Detection:** F1 = 1.00, Width Error = 0.0 mm
- **Room Reconstruction:** IoU = 1.00, Net Area Error = 0.0%
- **Dimension Accuracy:** 100.0% within 50mm
- **Uncertainties:** 0 detected / 0 expected in ground truth
  - *Audit Note:* Execution used mocked or pre-supplied observations. Results do NOT reflect real multimodal AI vision inference.

### `PILOT-13`: Multi-Room Residential Layouts (5+ rooms)
- **Execution Type:** `mocked` | **Provider:** `pilot_benchmark_evaluator` (deterministic_pilot_v1)
- **Source SHA-256:** `d899ec2512a69b83...`
- **Wall Detection:** F1 = 1.00, Mean Endpoint Error = 0.0 mm
- **Opening Detection:** F1 = 1.00, Width Error = 0.0 mm
- **Room Reconstruction:** IoU = 1.00, Net Area Error = 0.0%
- **Dimension Accuracy:** 100.0% within 50mm
- **Uncertainties:** 0 detected / 0 expected in ground truth
  - *Audit Note:* Execution used mocked or pre-supplied observations. Results do NOT reflect real multimodal AI vision inference.

### `PILOT-14`: Multi-Room Residential Layouts (5+ rooms)
- **Execution Type:** `mocked` | **Provider:** `pilot_benchmark_evaluator` (deterministic_pilot_v1)
- **Source SHA-256:** `e5e4cae4af8afd48...`
- **Wall Detection:** F1 = 1.00, Mean Endpoint Error = 0.0 mm
- **Opening Detection:** F1 = 1.00, Width Error = 0.0 mm
- **Room Reconstruction:** IoU = 1.00, Net Area Error = 0.0%
- **Dimension Accuracy:** 100.0% within 50mm
- **Uncertainties:** 0 detected / 0 expected in ground truth
  - *Audit Note:* Execution used mocked or pre-supplied observations. Results do NOT reflect real multimodal AI vision inference.

### `PILOT-15`: Complex Room Junctions & Openings
- **Execution Type:** `mocked` | **Provider:** `pilot_benchmark_evaluator` (deterministic_pilot_v1)
- **Source SHA-256:** `5bb2395d3a9c65c9...`
- **Wall Detection:** F1 = 1.00, Mean Endpoint Error = 0.0 mm
- **Opening Detection:** F1 = 1.00, Width Error = 0.0 mm
- **Room Reconstruction:** IoU = 1.00, Net Area Error = 0.0%
- **Dimension Accuracy:** 100.0% within 50mm
- **Uncertainties:** 0 detected / 0 expected in ground truth
  - *Audit Note:* Execution used mocked or pre-supplied observations. Results do NOT reflect real multimodal AI vision inference.

### `PILOT-16`: Complex Room Junctions & Openings
- **Execution Type:** `mocked` | **Provider:** `pilot_benchmark_evaluator` (deterministic_pilot_v1)
- **Source SHA-256:** `fde268ef51e7981c...`
- **Wall Detection:** F1 = 1.00, Mean Endpoint Error = 0.0 mm
- **Opening Detection:** F1 = 1.00, Width Error = 0.0 mm
- **Room Reconstruction:** IoU = 1.00, Net Area Error = 0.0%
- **Dimension Accuracy:** 100.0% within 50mm
- **Uncertainties:** 1 detected / 1 expected in ground truth
  - *Audit Note:* Execution used mocked or pre-supplied observations. Results do NOT reflect real multimodal AI vision inference.
  - *Audit Note:* Unannotated window sill: 900mm default assigned and flagged as assumed_default_unverified.

### `PILOT-17`: Clean Hand-Drawn Plans
- **Execution Type:** `mocked` | **Provider:** `pilot_benchmark_evaluator` (deterministic_pilot_v1)
- **Source SHA-256:** `bd38c27a038a6d8b...`
- **Wall Detection:** F1 = 1.00, Mean Endpoint Error = 0.0 mm
- **Opening Detection:** F1 = 1.00, Width Error = 0.0 mm
- **Room Reconstruction:** IoU = 1.00, Net Area Error = 0.0%
- **Dimension Accuracy:** 100.0% within 50mm
- **Uncertainties:** 0 detected / 0 expected in ground truth
  - *Audit Note:* Execution used mocked or pre-supplied observations. Results do NOT reflect real multimodal AI vision inference.

### `PILOT-18`: Multi-Storey Residential Sketches
- **Execution Type:** `mocked` | **Provider:** `pilot_benchmark_evaluator` (deterministic_pilot_v1)
- **Source SHA-256:** `c7925749bd20d272...`
- **Wall Detection:** F1 = 1.00, Mean Endpoint Error = 0.0 mm
- **Opening Detection:** F1 = 1.00, Width Error = 0.0 mm
- **Room Reconstruction:** IoU = 1.00, Net Area Error = 0.0%
- **Dimension Accuracy:** 100.0% within 50mm
- **Uncertainties:** 0 detected / 0 expected in ground truth
  - *Audit Note:* Execution used mocked or pre-supplied observations. Results do NOT reflect real multimodal AI vision inference.

### `PILOT-19`: Multi-Storey Residential Sketches
- **Execution Type:** `mocked` | **Provider:** `pilot_benchmark_evaluator` (deterministic_pilot_v1)
- **Source SHA-256:** `4397c554c20666b0...`
- **Wall Detection:** F1 = 1.00, Mean Endpoint Error = 0.0 mm
- **Opening Detection:** F1 = 1.00, Width Error = 0.0 mm
- **Room Reconstruction:** IoU = 1.00, Net Area Error = 0.0%
- **Dimension Accuracy:** 100.0% within 50mm
- **Uncertainties:** 0 detected / 0 expected in ground truth
  - *Audit Note:* Execution used mocked or pre-supplied observations. Results do NOT reflect real multimodal AI vision inference.

### `PILOT-20`: Multi-Page PDF Floor Plan Sets
- **Execution Type:** `mocked` | **Provider:** `pilot_benchmark_evaluator` (deterministic_pilot_v1)
- **Source SHA-256:** `ce6c7ed3a77e1eae...`
- **Wall Detection:** F1 = 1.00, Mean Endpoint Error = 0.0 mm
- **Opening Detection:** F1 = 0.00, Width Error = 0.0 mm
- **Room Reconstruction:** IoU = 1.00, Net Area Error = 0.0%
- **Dimension Accuracy:** 100.0% within 50mm
- **Uncertainties:** 0 detected / 0 expected in ground truth
  - *Audit Note:* Execution used mocked or pre-supplied observations. Results do NOT reflect real multimodal AI vision inference.

### `PILOT-21`: Non-Rectangular Footprints
- **Execution Type:** `mocked` | **Provider:** `pilot_benchmark_evaluator` (deterministic_pilot_v1)
- **Source SHA-256:** `4c706a1b446c2499...`
- **Wall Detection:** F1 = 1.00, Mean Endpoint Error = 0.0 mm
- **Opening Detection:** F1 = 1.00, Width Error = 0.0 mm
- **Room Reconstruction:** IoU = 1.00, Net Area Error = 0.0%
- **Dimension Accuracy:** 100.0% within 50mm
- **Uncertainties:** 0 detected / 0 expected in ground truth
  - *Audit Note:* Execution used mocked or pre-supplied observations. Results do NOT reflect real multimodal AI vision inference.

### `PILOT-22`: Multi-Room Residential Layouts (5+ rooms)
- **Execution Type:** `mocked` | **Provider:** `pilot_benchmark_evaluator` (deterministic_pilot_v1)
- **Source SHA-256:** `d6422e27a4ba35be...`
- **Wall Detection:** F1 = 1.00, Mean Endpoint Error = 0.0 mm
- **Opening Detection:** F1 = 1.00, Width Error = 0.0 mm
- **Room Reconstruction:** IoU = 1.00, Net Area Error = 0.0%
- **Dimension Accuracy:** 100.0% within 50mm
- **Uncertainties:** 0 detected / 0 expected in ground truth
  - *Audit Note:* Execution used mocked or pre-supplied observations. Results do NOT reflect real multimodal AI vision inference.
