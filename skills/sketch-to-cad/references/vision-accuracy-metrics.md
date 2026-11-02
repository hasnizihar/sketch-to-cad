# Architectural Vision Accuracy Metrics & Spatial Evaluation Reference

This document defines the mathematical models, spatial matching algorithms, and tolerance thresholds used by the **Benchmark Evaluation Engine** (`scripts/benchmark_engine.py`) to measure the geometric accuracy of multimodal vision model predictions against architectural ground truth.

---

## 1. Spatial Matching Problem & Principle

In real-world architectural sketch interpretation, predicted entity IDs rarely match ground-truth IDs. Furthermore, wall endpoints may be returned in reverse order, and room polygons may begin at arbitrary vertices.

To address this without heuristic inflation, Sketch-to-CAD uses **spatial bipartite matching**:
- Geometry is evaluated in world coordinates ($\text{mm}$).
- Predictions are mapped to ground-truth entities based on geometric proximity and spatial overlap.
- Each ground-truth entity can match at most one prediction (greedy bipartite matching).

---

## 2. Wall Detection & Endpoint Tolerance

### 2.1 Orientation-Invariant Matching
A predicted wall $W_{\text{pred}} = (P_{\text{start}}, P_{\text{end}})$ is compared against a ground-truth wall $W_{\text{gt}} = (G_{\text{start}}, G_{\text{end}})$. The endpoint error accounts for segment reversal:

$$d_{\text{direct}} = \|P_{\text{start}} - G_{\text{start}}\| + \|P_{\text{end}} - G_{\text{end}}\|$$
$$d_{\text{reversed}} = \|P_{\text{start}} - G_{\text{end}}\| + \|P_{\text{end}} - G_{\text{start}}\|$$
$$E_{\text{endpoints}} = \frac{1}{2} \min(d_{\text{direct}}, d_{\text{reversed}})$$

### 2.2 Tolerance Thresholds
- **Maximum Match Distance**: $E_{\text{endpoints}} \le 200.0\text{ mm}$ (configurable).
- A prediction satisfying this condition is classified as a **True Positive (TP)**. Unmatched predictions are **False Positives (FP)**, and unpredicted ground-truth walls are **False Negatives (FN)**.

$$\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}}, \quad \text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}}, \quad \text{F1} = \frac{2 \cdot \text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$

---

## 3. Opening Detection & Classification

Openings (doors and windows) are evaluated by center-point proximity:

$$\Delta_{\text{center}} = \|C_{\text{pred}} - C_{\text{gt}}\|$$

- **Center Distance Tolerance**: $\Delta_{\text{center}} \le 300.0\text{ mm}$.
- **Type Accuracy**: Evaluated on matched true positives:
  $$\text{Accuracy}_{\text{type}} = \frac{|\{ (p, g) \in \text{Matches} \mid \text{type}(p) = \text{type}(g) \}|}{\text{TP}}$$
- **Width Error**:
  $$E_{\text{width}} = |W_{\text{pred}} - W_{\text{gt}}|$$

---

## 4. Room Reconstruction & Polygon IoU

Rooms are closed 2D polygons evaluated via Intersection over Union (IoU) and area fidelity:

### 4.1 Polygon IoU
$$\text{IoU}(A, B) = \frac{\text{Area}(A \cap B)}{\text{Area}(A \cup B)} = \frac{\text{Area}(A \cap B)}{\text{Area}(A) + \text{Area}(B) - \text{Area}(A \cap B)}$$

- Matched when $\text{IoU}(A, B) \ge 0.30$.
- Polygonal intersection area is computed using rasterized grid sampling or analytical polygon clipping.

### 4.2 Area Relative Error
For matched rooms, net area error measures dimensional drift:
$$E_{\text{area}} = \frac{|\text{Area}_{\text{pred}} - \text{Area}_{\text{gt}}|}{\text{Area}_{\text{gt}}} \times 100\%$$

---

## 5. Dimension Extraction & Numeric Accuracy

Dimensions annotated on sketches are matched to ground-truth dimension chains:

- **Proximity**: Matched to nearest reference dimension chain ($\le 500\text{ mm}$).
- **Numeric Accuracy Threshold**: A prediction is counted as numerically correct if and only if:
  $$|V_{\text{pred}} - V_{\text{gt}}| \le 50.0\text{ mm}$$
- **Numeric Accuracy Metric**:
  $$\text{Accuracy}_{\text{dim}} = \frac{\text{Count of Correct Values}}{\text{Total Matched Dimensions}} \times 100\%$$

---

## 6. Provenance Enforcement

All evaluation records require an explicit `execution_type` field:
- `real_api`: Verified call to live provider API (OpenAI, Gemini, Anthropic) with signed payload hash and request duration.
- `agent_native`: Antigravity native multimodal vision reasoning on attached images.
- `mocked`: Local deterministic baseline fixture for unit testing and CI pipelines.
