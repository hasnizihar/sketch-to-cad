# Vision Provider Benchmark & Evaluation Reference

This document describes the architectural interpretation benchmark suite, test fixtures, evaluation metrics, and scoring procedures used to verify multimodal vision models in Sketch-to-CAD.

---

## 1. Benchmark Objectives

1. **Empirical Evaluation**: Evaluate how reliably a vision provider detects walls, openings, rooms, labels, and dimensions from diverse architectural sketch styles.
2. **Standardized Ground Truth**: Benchmark test fixtures are paired with human-certified reference observations in `tests/fixtures/sketches/`.
3. **No Fabricated Scores**: Metrics are evaluated through automated mathematical intersection calculations (IoU and dimension tolerances) without arbitrary heuristic inflation.

---

## 2. Benchmark Dataset Manifest

The benchmark suite evaluates five distinct residential floor-plan scenarios:

| Fixture ID | Name | Type | Key Challenge | Expected Evaluation Target |
| :--- | :--- | :--- | :--- | :--- |
| **`CASE-A`** | Clean Single-Storey Plan | Synthetic PNG | Orthogonal linework, complete dimension chain | 100% precision & recall, 0 blockers |
| **`CASE-B`** | Incomplete Sketch | Synthetic PNG | Missing overall depth dimension, unannotated wall thickness | Flags 1 blocker uncertainty (`envelope.depth`) |
| **`CASE-C`** | Contradictory Sketch | Synthetic PNG | Conflicting dimension chains ($8000\text{ mm}$ vs $9100\text{ mm}$) | Flags 1 blocker conflict (`arithmetic_mismatch`) |
| **`CASE-D`** | Multi-Page Two-Storey PDF Set | Synthetic PDF | Multi-page PDF floor plan separation, vertical stair alignment | Separate Ground/First floors, continuous stair core |
| **`CASE-E`** | Non-Rectangular Plan | Synthetic PNG | Intentionally angled northern boundary wall ($\sim 24^\circ$ slope) | Preserves angled wall geometry without forced orthogonal snapping |

---

## 3. Evaluation Metrics & Formulas

### 3.1 Entity Detection (Precision, Recall, IoU)
Given ground-truth entities $R$ and predicted entities $P$:
- An entity pair $(r \in R, p \in P)$ is a **True Positive (TP)** if `type(r) == type(p)` and normalized bounding-box $\text{IoU}(r, p) \ge 0.25$.
- Entities in $P$ without a matching $r$ are **False Positives (FP)**.
- Entities in $R$ not predicted by $P$ are **False Negatives (FN)**.

$$\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}}, \quad \text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}}$$

### 3.2 Dimension Extraction Accuracy
Explicit dimensions $D_{\text{ref}}$ extracted from handwritten numbers:
$$\text{Accuracy}_{\text{dim}} = \frac{|\{d \in D_{\text{ref}} \mid \exists p \in D_{\text{pred}} \text{ s.t. } |v_d - v_p| \le 50.0\text{ mm}\}|}{|D_{\text{ref}}|}$$

### 3.3 Contradiction Detection Rate
Measures whether expected arithmetic contradictions (e.g., room chain sum exceeding overall building footprint) are successfully identified as blocker issues:
$$\text{Rate}_{\text{contradiction}} = \frac{\text{Cases with Blocker Flagged}}{\text{Cases with Expected Blocker}}$$

---

## 4. Running the Benchmark

Execute via CLI:
```bash
# Evaluate default or mock provider
python scripts/evaluate_vision.py --provider mock --output tests/output/benchmark_results.json

# Evaluate Google Gemini (requires GEMINI_API_KEY)
python scripts/evaluate_vision.py --provider google_gemini --output tests/output/gemini_benchmark.json

# Evaluate OpenAI (requires OPENAI_API_KEY)
python scripts/evaluate_vision.py --provider openai --output tests/output/openai_benchmark.json
```

Outputs:
- JSON Results: `<output>.json` (adheres to `schemas/vision-benchmark-result.schema.json`)
- Markdown Report: `<output>.md`
