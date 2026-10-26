# Workflow Guide

This document explains the end-to-end 7-stage quality gate architecture used by `sketch-to-cad`.

---

## The 7-Stage Workflow

```
   ┌──────────────────────┐
   │  1. Source Sketch    │  User provides floor-plan sketch & brief
   └──────────┬───────────┘
              │
   ┌──────────▼───────────┐
   │  2. Interpretation   │  Classifies dimensions & logs uncertainties
   └──────────┬───────────┘
              │
   ┌──────────▼───────────┐
   │ 3. USER APPROVAL GATE│  MANDATORY: User reviews & approves corrections
   └──────────┬───────────┘
              │
   ┌──────────▼───────────┐
   │  4. CAD Generation   │  Deterministic CADCraft drawing & layering
   └──────────┬───────────┘
              │
   ┌──────────▼───────────┐
   │ 5. Topology Validate │  Checks bounds, layer counts, label centroids
   └──────────┬───────────┘
              │
   ┌──────────▼───────────┐
   │ 6. VISUAL QA GATE    │  MANDATORY: Raster review & sketch reconciliation
   └──────────┬───────────┘
              │
   ┌──────────▼───────────┐
   │ 7. Deliverables      │  Final DXF, PNG preview & validation report
   └──────────────────────┘
```

---

## Why Quality Gates Matter

In automated CAD generation, **a generated drawing is not necessarily a correct drawing**. 

Tools that skip human approval or raster visual inspection frequently produce drawings where:
- Dimensions sum up to contradictory numbers.
- Dimension text is microscopic or invisible.
- Door cuts leave double-wall cavities open and unsealed.
- Door swings open against the wrong wall face.
- Room labels collide with hallway boundaries.

`sketch-to-cad` implements two mandatory quality gates to eliminate these errors before delivering CAD files.

---

## Gate 1: The User Approval Gate (Phase 3)

Before a single CAD line is drafted, Antigravity constructs a structured coordinate model conforming to `schemas/floor-plan-model.json` with status `"awaiting_approval"`.

The model:
- Establishes a Cartesian origin $(0, 0)$ at the bottom-left exterior corner.
- Classifies every dimension as `explicit` (written on sketch), `estimated` (scaled from image), or `inferred` (standard architectural conventions).
- Reconciles dimension conflicts (e.g. sum of left rooms $\ne$ overall right depth).
- Categorizes all assumptions into an explicit **Uncertainty Log**.

The agent presents the proposal to the user and halts:
> *"Do not generate CAD until I approve the proposed model."*

Only upon receiving explicit user approval (`approved`) does the agent proceed to Phase 4.

---

## Gate 2: The Visual QA & Source Comparison Gate (Phase 6)

After CADCraft drafts the drawing in memory and automated geometric checks pass, the agent renders a visual raster preview (`render(fit=true)` or PNG export) and executes a visual audit against the source sketch:

1. **Dimension Readability**: Confirms that dimension text height and arrow ticks are legible at standard 100% zoom.
2. **Source Reconciliation**: Verifies that door openings and swing directions match the original sketch (e.g. entrance on East exterior wall vs. North wall).
3. **Jamb End-Caps**: Confirms that wall cavities at door and window openings are capped by transverse lines.
4. **Circulation Clearances**: Verifies that room labels do not collide with walls or adjacent labels in narrow corridors.

If visual defects are detected, the drawing geometry is adjusted and re-rendered before final acceptance.

---

## Deliverables Generated

When the workflow completes, the user receives:
1. **Master CAD Drawing (`.dxf`)**: Layered, editable 2D vector CAD format compatible with AutoCAD, LibreCAD, QCAD, and CADCraft.
2. **Visual Preview (`.png`)**: High-resolution raster preview for instant visual verification.
3. **Floor Plan Model (`.json`)**: Structured intermediate coordinate model preserving all dimensions, room areas, and uncertainty reconciliation logs.
4. **Acceptance Report**: Detailed table listing PASSED, FAILED, and UNVERIFIED items with a compliance notice.
