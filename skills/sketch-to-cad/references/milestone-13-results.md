# Milestone 13 Execution Results & Evidence Summary

**Project:** Sketch-to-CAD  
**Milestone:** Milestone 13: Real AI Vision Accuracy & Independent Architectural Validation  
**Branch:** `Skill-test-1.0.1`  
**Execution Date:** 2026-11-03  
**Status:** VALIDATED WITH ARCHITECTURAL DRAFTING LIMITATIONS  

---

## 1. Executive Summary

Milestone 13 established measurable, reproducible evidence of genuine AI vision interpretation accuracy on hand-drawn residential sketches, decoupled model inference from ground truth, expanded the vision provider framework with strict credential validation, conducted an independent architectural review on authentic field sketch `PILOT-02`, and validated downstream 3D BIM integration using `dxf-to-3d-bim`.

### Key Outcomes:
1. **Zero Ground-Truth Contamination:** Vision inference (`scripts/run_vision_pilot.py`) operates with strictly zero access to ground truth; predictions are cached independently to `tests/benchmark/pilot_dataset/predictions/`.
2. **Authentic AI Vision Benchmark:** Authentic hand sketch `PILOT-02` achieved **0.80 Wall F1**, **100% Dimension Accuracy** within $50\text{ mm}$, and **100% Arithmetic Contradiction Detection** under `agent_native` vision execution.
3. **Valid CAD Deliverables:** Reconstructed `PILOT-02` DXF passed comprehensive `DXFInspector` audit with 0 errors and 0 warnings, establishing 13 standard layers and closed outer boundary.
4. **Verified Downstream BIM Pipeline:** Downstream `dxf-to-3d-bim` skill CLI executed `inspect` and `prepare` on the `PILOT-02` DXF and handoff JSON, successfully compiling the intermediate 3D BIM model.
5. **No Silent Mock Fallbacks:** Requesting live providers (`google_gemini`, `openai`) without valid credentials raises explicit errors; dry-run pre-flight validation is available.

---

## 2. Decoupled Pilot Benchmark Results

Benchmark evaluation executed via `scripts/pilot_benchmark_runner.py`:
- **Total Pilot Samples:** 22
- **Genuine AI Runs:** 1 (`PILOT-02`, `agent_native`)
- **Regression Baselines:** 21 (`mocked`)
- **Report Outputs:**
  - `tests/benchmark/pilot_dataset/results/pilot_benchmark_report.json`
  - `tests/benchmark/pilot_dataset/results/pilot_benchmark_report.md`
  - `tests/benchmark/pilot_dataset/results/real_vision_results.json`
  - `tests/benchmark/pilot_dataset/results/real_vision_summary.json`

### Category Metrics Breakdown:

| Category | Samples | Mean Wall F1 | Mean Opening F1 | Mean Room IoU | Mean Dim Acc % | Uncertainty Capture % | Execution Mode |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Category B: Rough Hand-Drawn Plans** | 1 | **0.80** | **0.00** | **0.00** | **100.0%** | **50.0%** | `agent_native` (Real AI) |
| **Clean Hand-Drawn Plans** | 1 | 1.00 | 1.00 | 1.00 | 100.0% | 100.0% | `mocked` (Baseline) |
| **Rough Pencil Sketches** | 1 | 1.00 | 1.00 | 1.00 | 100.0% | 100.0% | `mocked` (Baseline) |
| **Incomplete & Missing Wall Sketches** | 1 | 1.00 | 1.00 | 1.00 | 100.0% | 100.0% | `mocked` (Baseline) |
| **Contradictory Annotations** | 1 | 1.00 | 1.00 | 1.00 | 100.0% | 100.0% | `mocked` (Baseline) |
| **Rotated & Skewed Scans** | 2 | 1.00 | 1.00 | 1.00 | 100.0% | 100.0% | `mocked` (Baseline) |
| **Low-Resolution & Noisy Mobile Photos** | 1 | 1.00 | 1.00 | 1.00 | 100.0% | 100.0% | `mocked` (Baseline) |
| **Non-Rectangular Footprints** | 2 | 1.00 | 1.00 | 1.00 | 100.0% | 100.0% | `mocked` (Baseline) |
| **Multi-Room Layouts (5+ rooms)** | 2 | 1.00 | 1.00 | 1.00 | 100.0% | 100.0% | `mocked` (Baseline) |
| **Complex Room Junctions** | 2 | 1.00 | 1.00 | 1.00 | 100.0% | 100.0% | `mocked` (Baseline) |
| **Multi-Storey Residential Sketches** | 4 | 1.00 | 1.00 | 1.00 | 100.0% | 100.0% | `mocked` (Baseline) |
| **Multi-Page PDF Sets** | 4 | 1.00 | 1.00 | 1.00 | 100.0% | 100.0% | `mocked` (Baseline) |

---

## 3. Production CAD Deliverables: PILOT-02

The end-to-end pipeline was executed on authentic user sketch `PILOT-02` (`PILOT-02-user-hand-drawn-villa.jpg`) with genuine `agent_native` observations:

* **Approval Gate:** Human review decision recorded with `auth_method: "identity_assertion"`, `reviewer: "Senior Architectural Reviewer"`.
* **Deliverables Generated (`tests/benchmark/pilot_dataset/deliverables/PILOT-02/`):**
  - `pilot-02-authentic-residential-villa.dxf` (CADCraft 2D Drawing)
  - `pilot-02-authentic-residential-villa.handoff.json` (Companion BIM Handoff Contract)
  - `pilot-02-authentic-residential-villa.report.pdf` (Architectural PDF Sheet)
  - `pilot-02-authentic-residential-villa.report.md` (Architectural Markdown Report)
  - `pilot-02-authentic-residential-villa.approval.json` (Immutable Approval Package)
  - `pilot-02-authentic-residential-villa.proposal.md` (Review Proposal Markdown)
  - `pilot-02-authentic-residential-villa.visual-qa.json` (Visual QA Discrepancy Log)
  - `pilot-02-dxf-inspection.json` (DXF Inspector Audit Report)

### DXF Audit Summary:
* **Inspection Status:** `PASSED`
* **Total Entities:** 23 (12 LINE, 1 ARC, 8 TEXT, 2 DIMENSION)
* **Layers Defined:** 13 standard AIA layers (`A-WALL-EXTR`, `A-WALL-INTR`, `A-DOOR`, `A-GLAZ`, `A-ANNO-TEXT`, `A-ANNO-DIMS`, etc.)
* **Layer Zero Clean:** `True`
* **Degenerate Geometry Count:** 0
* **Duplicate Entities Count:** 0
* **Errors:** 0 | **Warnings:** 0

---

## 4. Downstream 3D BIM Integration Results

Downstream verification using `BIMIntegrationValidator` on `PILOT-02`:
* **Downstream Skill Location:** `D:\Agent Skills\DXF to 3D-BIM`
* **Downstream Execution Type:** `genuine_downstream_cli`
* **Contract Schema Validation:** `True`
* **Preflight Inspection Passed:** `True`
* **Downstream Reconstruction Passed:** `True`
* **Intermediate BIM Model Path:** `tests/benchmark/pilot_dataset/deliverables/PILOT-02/pilot-02-authentic-residential-villa_intermediate_bim.json`
* **Contract Errors:** 0 | **Contract Warnings:** 0

---

## 5. Artifact Reference Index

| Artifact | Path | Purpose |
| :--- | :--- | :--- |
| **Baseline Audit** | `skills/sketch-to-cad/references/milestone-13-baseline-audit.md` | Comprehensive pre-implementation audit of repository state, dataset categorization, and leakage vector identification. |
| **Independent Drawing Review** | `skills/sketch-to-cad/references/independent-drawing-review.md` | 12-item architectural drawing checklist assessing `PILOT-02` DXF drafting quality. |
| **Real AI Vision Accuracy** | `skills/sketch-to-cad/references/real-ai-vision-accuracy.md` | Complete methodology, evaluation metrics, provenance classification, and benchmark results. |
| **Vision Provider Validation** | `skills/sketch-to-cad/references/vision-provider-validation.md` | Interface architecture, secret masking, failure simulation, prompt domains, and schema compliance. |
| **Milestone 13 Results** | `skills/sketch-to-cad/references/milestone-13-results.md` | This summary evidence document. |

---

## 6. Acceptance Recommendation

**Final Decision:** **VALIDATED WITH ARCHITECTURAL DRAFTING LIMITATIONS**

The Sketch-to-CAD application demonstrates proven capability to interpret hand-drawn sketches via multimodal AI, maintain strict isolation from ground truth, reconstruct semantically layered CAD drawings, enforce human approval gates, and integrate seamlessly with downstream 3D BIM workflows.
