# Project Overview: Sketch-to-CAD (Supervised MVP)

**Repository:** `https://github.com/hasnizihar/sketch-to-cad`  
**Branch:** `Skill-test-1.0.1`  
**Version:** `v1.0.0-beta.1` (Supervised Beta MVP)  
**Release Date:** 2026-11-03  
**Status:** `MVP_READY_WITH_LIMITATIONS`  

---

## 1. Executive Summary

**Sketch-to-CAD** is an open-source, headless, AI-assisted architectural drafting skill designed for the **Google Antigravity** agent ecosystem. It bridges the gap between early-stage conceptual hand-drawn residential sketches (JPG, PNG, PDF) and precision, layered 2D Computer-Aided Design (CAD) drawings in standard AutoCAD DXF format.

Unlike conventional generative computer-vision models that produce un-editable raster pixels or hallucinate fictitious dimensions, Sketch-to-CAD operates under an **architectural engineering philosophy**:
1. **Deconstructs visual information** into structured semantic domains (footprints, walls, openings, rooms, dimensions).
2. **Explicitly categorizes confidence and provenance** (`explicit`, `estimated`, `inferred`).
3. **Halts execution at a mandatory Human Approval Gate** whenever ambiguities, geometric inconsistencies, or conflicting dimension chains arise.
4. **Drafts deterministic vector geometry** on standard American Institute of Architects (AIA) CAD layers with sealed wall cavities and trimmed jambs.
5. **Exports downstream BIM handoff contracts** for 3D Building Information Modeling reconstruction in `dxf-to-3d-bim`.

> [!IMPORTANT]
> **Supervised MVP Scope**: Sketch-to-CAD is an architectural drafting assistant and pre-processor intended strictly for supervised use by design professionals. It is **not** autonomous, self-certifying engineering software, and its outputs do not constitute stamped permit-ready construction documents.

---

## 2. Core Problem Solved

Residential design begins with hand sketches on paper, trace, or tablet napkins. However, translating these rough concepts into CAD is labor-intensive, error-prone, and resistant to simplistic automation:
- **Mathematical Contradictions**: Hand-annotated dimensions rarely sum accurately (e.g., room spans $1800 + 4100 + 3200 = 9100\text{ mm}$ while building depth is marked $8700\text{ mm}$).
- **Distorted Aspect Ratios**: Freehand drawings are rarely drawn to orthogonal scale; pixel ratios do not match annotated dimensions.
- **Ambiguous Wall Boundaries**: Rough pencil lines leave wall cavities unsealed, jambs open, and junctions poorly defined.
- **The "Hallucination" Danger**: Black-box AI models guess missing numbers silently, injecting non-existent architectural features without the designer's awareness.

Sketch-to-CAD solves this by replacing silent guesswork with **transparent uncertainty logging and human-in-the-loop governance**. Every contradiction is isolated and presented in a structured proposal before any vector entity is written to disk.

---

## 3. Target Users & Operating Model

| User Role | Workflow Context | Primary Value Received |
| :--- | :--- | :--- |
| **Architectural Designers** | Conceptual design, feasibility studies | Converts client napkin sketches into clean editable 2D DXF layouts in seconds. |
| **CAD Technicians / Draftspersons** | Production drafting, site surveys | Automates initial wall layout, room labeling, and dimension chains with AIA layering. |
| **BIM Coordinators** | Downstream 3D modeling | Generates verified coordinate contracts and `.handoff.json` metadata for 3D BIM pipelines. |
| **AI Agent Developers** | Autonomous architectural systems | Provides a modular, schema-enforced pipeline with zero-secret credential safety. |

---

## 4. Input & Output Formats

### 4.1 Supported Inputs
- **Image Formats**: JPEG / JPG, PNG, WebP (resolution $\ge 1200\text{ px}$ recommended).
- **Document Formats**: Vector or scanned PDF (multi-page documents processed per page).
- **Geometry Scope**: Single-storey and multi-storey orthogonal residential floor plans (0° and 90° wall alignments; non-rectangular orthogonal layouts supported).

### 4.2 Standard Deliverables Package
Each completed workflow run generates an isolated deliverable package with cryptographic verification:

```
deliverables/<project-slug>/
├── <slug>.dxf                   # Precision 2D CAD drawing (AIA layers, millimeter units)
├── <slug>.png                   # High-resolution raster visual preview
├── <slug>.handoff.json          # Downstream BIM handoff contract (Draft-07 schema)
├── <slug>.report.pdf            # Professional multi-page architectural report with schedules
├── <slug>.report.md             # Markdown architectural documentation
├── <slug>.report.json           # Machine-readable area, door/window, and finish schedules
├── <slug>.approval.json         # Cryptographic revision hash and reviewer audit trail
├── <slug>.proposal.md           # Human review proposal with uncertainty register
├── <slug>.vision-execution.json # Multimodal vision execution audit log (SHA-256 fingerprint)
├── <slug>.visual-qa.json        # 4-tier discrepancy analysis and raster comparison
├── <slug>.visual-qa.md          # Visual QA human-readable summary
├── <slug>-inspection.json       # Structural DXF topology audit report
└── manifest.json                # SHA-256 deliverable integrity manifest
```

---

## 5. Architectural Quality Standards

Generated DXF drawings strictly follow professional drafting rules:
- **AIA Layer Standard**: Geometric entities are isolated across 11 standard layers (`A-WALL-EXTR`, `A-WALL-INTR`, `A-DOOR`, `A-GLAZ`, `A-FURN`, `A-FIXT`, `A-STAIR`, `A-COLS`, `A-FLOR-FIN`, `A-ANNO-TEXT`, `A-ANNO-DIMS`).
- **Layer 0 Cleanliness**: Layer `0` and `DEFPOINTS` contain strictly 0 generated geometry.
- **Sealed Wall Cavities**: All wall endpoints at door and window cutouts feature transverse jamb end-caps, preventing open unclosed double-wall lines.
- **T-Junction Cavity Trimming**: Interior-to-exterior and interior-to-interior wall intersections are trimmed cleanly.
- **Tiered Dimensioning**: Hierarchical 3-tier exterior dimension chains (Tier 1 Overall, Tier 2 Openings/Jambs, Tier 3 Room Widths) with collision detection.
- **Standardized Elements**: Parametric 2D architectural blocks for beds, seating, sanitary ware, kitchen sinks/cooktops, and structural columns.

---

## 6. Supervised MVP Boundaries & Release Limitations

This release is designated **`MVP_READY_WITH_LIMITATIONS`**. Design professionals must be aware of the following fundamental boundaries:
1. **Human Oversight Mandatory**: Every draft layout requires explicit review and confirmation. Do not bypass the approval gate.
2. **AI Vision Accuracy Variance**: In empirical benchmarks on real hand sketches, vision providers successfully detect major building perimeters ($F_1 = 0.80$) but show variable detection on internal door/window openings ($F_1 = 0.00$ to $0.50$ without human prompt guidance).
3. **Default 900 mm Window Sill Assumption**: When window sill heights are unannotated on 2D sketches, a 900 mm fallback is recorded in the uncertainty register and flagged as unverified for downstream 3D BIM.
4. **No Structural Engineering or Permit Certification**: The system does not calculate structural loads, soil bearing, seismic resistance, or life-safety egress codes. All outputs require review and professional stamping by a licensed Architect or Registered Professional Engineer.
