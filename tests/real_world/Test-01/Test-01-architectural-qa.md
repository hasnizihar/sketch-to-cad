# Architectural & Engineering QA Audit Report: Real-World Test 01 - Nordic Residential Villa

## Executive Summary
- **Drawing / Output:** `Test-01-floor-plan.dxf`
- **Target Level:** `LEVEL-01`
- **Overall Audit Status:** **REVIEW_REQUIRED**
- **Total Issues Cataloged:** 5

## Severity Breakdown
- **Blocking:** 0
- **Major:** 0
- **Warning:** 3
- **Informational:** 1

## Itemized Audit Findings

| Issue ID | Severity | Category | Description | Affected Entities | Suggested Action | Approval Req? |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| `QA-SYMB-001` | 🟡 WARNING | `symbols` | Element 'E-COL-TERRACE-1' at [5100.0, -2900.0] falls outside the exterior building envelope. | `E-COL-TERRACE-1, envelope` | Reposition element within interior room boundaries. | Yes |
| `QA-SYMB-002` | 🟡 WARNING | `symbols` | Element 'E-COL-TERRACE-2' at [10000.0, -2900.0] falls outside the exterior building envelope. | `E-COL-TERRACE-2, envelope` | Reposition element within interior room boundaries. | Yes |
| `QA-SYMB-003` | 🟡 WARNING | `symbols` | Element 'E-COL-TERRACE-3' at [14900.0, -2900.0] falls outside the exterior building envelope. | `E-COL-TERRACE-3, envelope` | Reposition element within interior room boundaries. | Yes |
| `QA-VISU-004` | MAJOR_DISCREPANCY | `source_comparison` | Openings count discrepancy: Doors observed=0 / CAD=15; Windows observed=0 / CAD=11. | `openings_count_and_distribution` | Investigate visual discrepancy. | No |
| `QA-PRES-005` | 🔵 INFO | `presentation` | Multiple dimensions with identical text detected. Verify tiered chains are not redundant. | `dimensions` | Consolidate duplicate dimension strings. | No |

## Recommended Corrective Actions

> **Deterministic Drafting Policy**:
> 1. Wall geometries must terminate with clean cavity closures and valid L, T, or Cross junctions.
> 2. Door swings must maintain clearance without cutting into partition walls or colliding with adjacent leaves.
> 3. Room boundaries must form closed non-self-intersecting polygons with non-zero Shoelace areas.
> 4. All dimensions and annotations must be non-colliding and legible at standard architectural scales.
> 5. Any geometric repair that changes room areas or wall positions mandates explicit human review.