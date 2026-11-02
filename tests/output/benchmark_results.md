# Vision Provider Benchmark Report: mock (mock-architectural-v1)

- **Benchmark ID:** `BM-1793634118`
- **Timestamp:** `2026-11-02T15:41:58.837735+00:00`
- **Test Cases Evaluated:** 5

## Overall Metrics Summary

| Evaluation Metric | Score | Assessment |
| :--- | :--- | :--- |
| Wall Detection Precision | **100.0%** | Proportion of predicted walls that match reference |
| Wall Detection Recall | **100.0%** | Proportion of reference walls detected |
| Opening Detection Precision | **100.0%** | Door & window classification accuracy |
| Opening Detection Recall | **100.0%** | Coverage of doors & windows |
| Room Detection Precision | **100.0%** | Enclosed space identification |
| Room Detection Recall | **100.0%** | Coverage of functional room program |
| Dimension Extraction Accuracy | **100.0%** | Explicit millimeter values matched |
| Contradiction Detection Rate | **100.0%** | Blocker conflict identification |

## Per-Fixture Results

| Fixture | Status | Wall P / R | Opening P / R | Room P / R | Dim Acc | Contradiction Detected |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Fixture A: Clean Single-Storey Plan | `evaluated` | 100% / 100% | 100% / 100% | 100% / 100% | 100% | ✅ Yes |
| Fixture B: Incomplete Sketch (Missing Dimensions) | `evaluated` | 100% / 100% | 100% / 100% | 100% / 100% | 100% | ✅ Yes |
| Fixture C: Contradictory Dimensions & Chains | `evaluated` | 100% / 100% | 100% / 100% | 100% / 100% | 100% | ✅ Yes |
| Fixture D: Multi-Page Two-Storey PDF Set | `evaluated` | 100% / 100% | 100% / 100% | 100% / 100% | 100% | ✅ Yes |
| Fixture E: Non-Rectangular Angled Boundary Plan | `evaluated` | 100% / 100% | 100% / 100% | 100% / 100% | 100% | ✅ Yes |