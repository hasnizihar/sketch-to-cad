# Limitations & Safety Disclaimers: Sketch-to-CAD (Supervised MVP)

**Skill Version:** 1.0.0 (Supervised Beta MVP)  
**Release Date:** 2026-11-03  
**Status:** `MVP_READY_WITH_LIMITATIONS`  

---

## 1. Executive Disclaimer: Supervised MVP Status

Sketch-to-CAD is an **AI-assisted pre-processor and drafting accelerator** designed to operate strictly under the supervision of qualified architectural designers and drafting professionals. 

> [!CAUTION]
> **NOT CERTIFIED ARCHITECTURAL OR ENGINEERING SOFTWARE**:
> All deliverables produced by Sketch-to-CAD—including DXF CAD drawings, companion BIM handoffs, and architectural schedules—are preliminary drafting aids. They **DO NOT** constitute stamped, sealed, or certified construction documents. They have not been evaluated for structural load capacity, foundation stability, fire-resistance ratings, life-safety egress, accessibility compliance (e.g. ADA), or local municipal building codes. All drawings must be reviewed, verified, and stamped by a licensed Architect or Registered Professional Engineer before use in permitting, bidding, or construction.

---

## 2. Benchmark Ground-Truth & AI Vision Coverage

In accordance with strict engineering integrity standards, the empirical performance of multimodal vision models on the 22-sample Pilot Dataset is disclosed transparently:

| Metric | Measured Real AI Value (`PILOT-02`) | Challenge Mock Baselines (21 Samples) | Explanation |
| :--- | :---: | :---: | :--- |
| **Exterior Wall F1** | **0.800** | 0.950 – 1.000 (synthetic) | Strong perimeter detection on clean hand-drawn sketches. |
| **Dimension Accuracy** | **100.0%** | 98.5% (synthetic) | Explicit handwritten dimensions (8000x8700 mm) recognized accurately. |
| **Opening F1 (Doors/Windows)**| **0.000** | 0.900 – 1.000 (synthetic) | Freehand door swings and window double-lines are frequently missed or unsegmented by raw vision inference without prompt hints. |
| **Room Polygon IoU** | **0.000** | 0.880 – 0.960 (synthetic) | Pixel-space room text labels require human assistance to associate with reconstructed geometric boundaries. |

> [!NOTE]
> **Provenance Transparency**: Of the 22 pilot benchmark samples, exactly **1 sample (`PILOT-02`)** represents an authentic user hand-drawn villa evaluated under live agent-native vision extraction. The remaining 21 samples are synthetic challenge fixtures designed to test pipeline error handling, skew detection, arithmetic conflict logging, and multi-storey handling. They are explicitly marked as `mocked` baselines and are **never** averaged into genuine AI accuracy figures.

---

## 3. Geometric & Drafting Limitations

### 3.1 Orthogonal Wall Alignment
The current geometry reconstructor operates on rectilinear Manhattan geometry (0° and 90° angles). Non-orthogonal walls (e.g., 45° bay windows in `PILOT-11`) are approximated or flagged as non-orthogonal warnings. Curved, circular, or freeform organic walls are unsupported.

### 3.2 900 mm Window Sill Fallback
Two-dimensional floor plan sketches almost never depict vertical sill heights. When sill heights are unannotated:
- The system automatically assigns a **900 mm fallback**.
- This assumption is recorded in the **Uncertainty Register** as unverified.
- Downstream BIM compilation tools (`dxf-to-3d-bim`) flag this height for explicit user approval before generating 3D wall cutouts.

### 3.3 Opening Host-Wall Alignment
In raw sketches, drawn door and window symbols often drift several hundred millimeters away from wall axes due to sloppy drawing. Sketch-to-CAD applies vector centerline projection to clamp opening centers onto host walls. If an opening is drawn entirely detached from any wall, it will be skipped and logged in the QA discrepancy report.

---

## 4. Human Review & Security Boundaries

### 4.1 Plain-Text Identity Assertions
The Human Approval Gate records the reviewer's name and role using `auth_method: "identity_assertion"`. This establishes an internal audit trail but **does not verify professional licensure, digital cryptographic signatures, or legal identity**.

### 4.2 Anti-Self-Approval
The system strictly prohibits AI agents or automated scripts from approving their own draft models. Submitting approvals with roles containing `agent`, `bot`, or `ai_assistant` triggers a fatal permission error.

---

## 5. Downstream BIM Handoff Scope

The exported `.handoff.json` contract provides 2D-to-3D bridge metadata (wall axes, thickness, opening locations, level elevations). However:
- Vertical heights (ceiling height, floor-to-floor pitch, roof slope) are set to default residential standards (2700 mm ceiling, 300 mm slab) and must be reviewed.
- Multi-storey stairwell openings require manual coordination in CAD or BIM software to verify clear headroom and riser/tread counts.
