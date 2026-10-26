# Limitations & Version Roadmap

This document outlines the verified scope, known limitations, and roadmap for `sketch-to-cad`.

---

## 1. Scope & Verified Environment in v0.1.0

### Verified Setup
- **Operating System**: Windows 10/11
- **Agent Platform**: Google Antigravity
- **CAD Engine**: CADCraft CLI v0.8.0 (Headless MCP mode)
- **Typology**: Single-storey orthogonal residential floor plans

Other platforms (macOS, Linux), CAD engines, or multi-storey typologies are **untested** in this release.

---

## 2. Current Known Limitations

### 1. Orthogonal Geometry Only
- v0.1.0 assumes rectilinear, orthogonal geometry (0° and 90° wall angles).
- Non-orthogonal walls, circular segments, and complex angled geometries are not yet supported.

### 2. Single-Storey Typologies
- The intermediate model format supports a single building envelope level.
- Multi-storey alignment, vertical stair shafts, and floor-to-floor structural stacking are deferred to future versions.

### 3. Hand-Drawn Ambiguities Require Human Decisions
- The skill does not guess or invent missing dimensions.
- Arithmetic conflicts on rough sketches (e.g. sum of room widths $\ne$ overall envelope) require explicit user choice between proposed reconciliation options.

### 4. Non-Certified Drafting Assistance
- Outputs are preliminary drafting aids.
- Structural load-bearing capacity, shear wall calculations, fire egress regulations, and municipal building code compliance are **UNVERIFIED** and must be reviewed and certified by a licensed architect or professional engineer before construction use.

---

## 3. Version Roadmap

### v0.1.0 · Initial Public Preview (Current)
- Core 7-stage quality gate workflow.
- Hand-drawn sketch decomposition and dimension classification (`explicit`, `estimated`, `inferred`).
- Mandatory User Approval Gate before CAD drafting.
- AIA layer structure (`A-WALL-EXTR`, `A-WALL-INTR`, `A-DOOR`, `A-GLAZ`, `A-ANNO-TEXT`, `A-ANNO-DIMS`).
- Sealed door jamb end-caps and legible dimension style scaling.
- Mandatory Visual QA & Source Comparison Gate.
- DXF, PNG, and JSON deliverables.

### v0.2.0 · Geometric Reliability & Automated Regression
- Automated geometric regression test harness.
- Advanced wall-junction collision resolver for complex multi-partition intersections.
- Automated dimension tier spacing and collision avoidance.
- Support for cased openings and pocket sliding doors.

### v0.3.0 · Enhanced Sketch Interpretation
- Robust OCR and handwriting recognition for low-resolution or skewed photos.
- Automatic visual perspective correction for angled mobile phone photos of sketches.
- Multi-room area schedule generation (gross vs. net internal floor areas).

### Future Milestones
- Multi-storey residential support with stairwell vertical continuity.
- Support for additional MCP CAD backends (e.g., LibreCAD, FreeCAD, AutoCAD).
- Export to IFC (Industry Foundation Classes) BIM formats.
