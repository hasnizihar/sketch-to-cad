# Production Reliability, Fault Tolerance & Performance Profiling Reference

This document establishes the production resilience architecture, retry strategy, atomic file writing standards, and profiling procedures implemented in **Sketch-to-CAD** (`scripts/pipeline_reliability.py` and `scripts/performance_profiler.py`).

---

## 1. Reliability Architecture Principles

Production execution of AI-assisted CAD generation must withstand real-world operational challenges:
1. **Zero Corrupted Outputs**: Partial or interrupted disk writes must never leave incomplete CAD files or malformed JSON deliverables on disk.
2. **Transient Resilience**: Temporary network disconnects, rate limits, or backend timeouts must be automatically retried with exponential backoff.
3. **No Retries on Permanent Failures**: Authentication errors, invalid API keys, and contract schema violations must fail immediately to avoid wasted credits and prolonged latency.
4. **Credential Privacy**: API keys, bearer tokens, and secrets must never be logged in execution transcripts, error messages, or reports.

---

## 2. Error Classification & Retry Policy

### 2.1 Error Classification
The `is_error_retryable` predicate classifies exceptions into two distinct categories:

| Error Category | Indicators | Action |
| :--- | :--- | :--- |
| **Transient Errors** | HTTP 429 (Rate Limit), 500, 502, 503, 504; `TimeoutError`; `ConnectionResetError`; `OSError` | Retried automatically with exponential backoff and randomized jitter. |
| **Permanent Errors** | HTTP 400, 401 (Unauthorized), 403 (Forbidden), 404; schema validation errors; invalid file formats | Fails immediately (`raise PermanentFailureError`). |

### 2.2 Exponential Backoff with Jitter
When a transient error occurs, retry delay $D_i$ for attempt $i$ is calculated as:

$$D_i = \min(D_{\text{initial}} \cdot B^{i-1}, D_{\text{max}}) \cdot J$$

where:
- $D_{\text{initial}} = 1.0\text{ s}$ (initial backoff delay)
- $B = 2.0$ (backoff multiplier)
- $D_{\text{max}} = 30.0\text{ s}$ (maximum backoff ceiling)
- $J \in [0.8, 1.2]$ (uniform randomized jitter preventing thundering herds)
- $N_{\text{max}} = 3$ retries.

---

## 3. Atomic File Operations

To guarantee that deliverables (DXF, JSON handoffs, Markdown reports, PDFs) are never corrupted by mid-write crashes or process terminations:

1. **Staging File**: Output is written to a temporary sibling file in the same directory (`prefix="<target>_tmp_"`).
2. **Flush & Fsync**: Buffer is explicitly flushed to OS disk caches via `os.fsync(fd)`.
3. **Atomic Replacement**: File is atomically swapped into place via `shutil.move` / `os.replace`.
4. **Rollback & Cleanup**: If any exception occurs during writing or serializing, the temporary file is unlinked immediately, leaving the original target file untouched.

Available functions:
- `atomic_write_text(file_path, content, encoding="utf-8")`
- `atomic_write_json(file_path, data, indent=2)`
- `atomic_write_bytes(file_path, data)`

---

## 4. Performance & Resource Profiling

The `PipelineProfiler` (`scripts/performance_profiler.py`) tracks high-resolution stage timings and entity counts across all pipeline stages:

- **Tracked Stages**:
  - Image Preprocessing & Rasterization
  - Vision Model Inference
  - Geometric Reconstruction & Constraint Solving
  - Visual QA & Engineering Rule Checks
  - CADCraft DXF Generation & Layer Setup
  - Independent DXF Inspection
  - Companion BIM Handoff Compilation
- **Deliverables**: Outputs structured performance summaries (`PipelineResourceProfile`) in JSON and Markdown table formats.
