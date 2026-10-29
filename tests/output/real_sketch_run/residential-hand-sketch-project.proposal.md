# Architectural Floor Plan Proposal: Residential Hand Sketch Project

> **Model Revision:** `c3d86284cb2f` | **Status:** `AWAITING_APPROVAL` | **Source:** `sketch-before.jpg`

## 1. Footprint & Envelope Summary

- **Overall Width:** 8000 mm
- **Overall Depth:** 8700 mm
- **Gross Footprint Area:** 69.60 m²
- **Levels Count:** 1
- **Total Rooms:** 3
- **Total Walls:** 5 (5 segments)
- **Total Openings:** 2 doors & windows

## 2. Extracted Dimensions & Provenance

| Dimension ID | Source Text | Value (mm) | Category | Target |
| :--- | :--- | :--- | :--- | :--- |
| `DIM-WIDTH` | `8000` | 8000 mm | `explicit` | overall_width |
| `DIM-DEPTH` | `8700` | 8700 mm | `explicit` | overall_depth |

## 3. Detected Conflicts & Critical Uncertainties

✅ No geometric or arithmetic conflicts detected.

## 4. Unannotated Information & Defaults

✅ All required architectural dimensions and parameters are fully defined.

## 5. Required Approval Actions

### Action 1: Approve floor plan layout (8000 x 8700 mm, 3 rooms) for CAD generation?
- **Options:** Approve without changes, Reject proposal, Request specific dimension changes
- **Current Status:** `pending`

---

### How to Approve or Correct (Headless Protocol)

To approve this proposal, execute the approval command with a human reviewer name:
```json
{"reviewer_name": "Jane Doe, Architect", "action": "approve", "details": {"notes": "Approved as drafted."}}
```
*Note: AI agents cannot self-approve. CAD generation will halt until valid human approval is recorded.*