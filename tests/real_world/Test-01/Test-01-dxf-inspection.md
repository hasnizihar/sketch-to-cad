# Independent Architectural DXF Inspection Report: Test-01-floor-plan.dxf

## Executive Summary
- **File Path:** `D:\Agent Skills\sketch-to-cad-main\tests\real_world\Test-01\Test-01-floor-plan.dxf`
- **File Size:** 86,155 bytes
- **SHA-256 Hash:** `a776cd4cf45c5c543a84d736c69cf89f3dca051be9d8771939d6178ecf983990`
- **Overall Audit Status:** **PASSED**
- **DXF Version:** `AC1032`
- **Units:** `Millimeters` ($INSUNITS = 4)
- **Extents Span:** 16050.0 x 19000.0 mm

## Entity & Geometry Inventory

| Entity Type | Count in Drawing |
| :--- | :---: |
| `ARC` | 12 |
| `DIMENSION` | 6 |
| `INSERT` | 16 |
| `LINE` | 211 |
| `TEXT` | 31 |

## Layer Architecture Compliance

| Layer Name | Entities | AIA Standard? | Status |
| :--- | :---: | :---: | :---: |
| `0` | 0 | Non-standard | Empty |
| `Defpoints` | 0 | Non-standard | Empty |
| `A-WALL-EXTR` | 70 | Yes | Active |
| `A-WALL-INTR` | 78 | Yes | Active |
| `A-DOOR` | 28 | Yes | Active |
| `A-GLAZ` | 47 | Yes | Active |
| `A-FURN` | 11 | Yes | Active |
| `A-FIXT` | 2 | Yes | Active |
| `A-STAIR` | 0 | Yes | Empty |
| `A-COLS` | 3 | Yes | Active |
| `A-FLOR-FIN` | 0 | Yes | Empty |
| `A-ANNO-TEXT` | 31 | Yes | Active |
| `A-ANNO-DIMS` | 6 | Yes | Active |

## Quality & Topological Checks
- **Default Layer '0' Cleanliness:** Clean (0 entities)
- **Duplicate Entities:** 0
- **Degenerate Line Segments (< 10mm):** 0

## Model-to-DXF-to-BIM Consistency Cross-Audit
- **Walls:** Model = 22 walls | DXF = 211 lines
- **Openings:** Model = 26 openings | DXF = 12 arcs
- **Elements:** Model = 16 elements | DXF = 16 block references
- **Handoff Coordination:** Walls Match: True | Openings Match: True