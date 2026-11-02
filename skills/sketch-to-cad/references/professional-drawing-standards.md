# Professional Drawing Standards & AIA Layer Hierarchy

## 1. Overview
Sketch-to-CAD generates professional, industry-compliant 2D architectural drawings adhering to the American Institute of Architects (AIA) National CAD Standard (NCS v6) layer guidelines and ISO 128 architectural drafting conventions.

All generated DXF drawings maintain precise line weights, color coding, entity separation, and layer hygiene suitable for direct import into professional BIM software (Revit, ArchiCAD), AutoCAD, or CADCraft.

---

## 2. AIA Layer Standards and Lineweights

The drafting pipeline assigns entities strictly to semantic AIA layers. Lineweights are defined in integer hundredths of a millimeter ($10^{-2}\text{ mm}$) per the DXF specification (`dxf.lineweight`):

| Layer Name | Color (ACI) | Color Name | Lineweight (mm) | Description & Usage |
|:---|:---:|:---|:---:|:---|
| `A-WALL-EXTR` | 1 | Red | 0.50 mm | Exterior perimeter load-bearing walls and building envelope |
| `A-WALL-INTR` | 2 | Yellow | 0.35 mm | Interior partition walls and non-load-bearing room dividers |
| `A-DOOR` | 4 | Cyan | 0.25 mm | Door frames, leaves, and swing arcs |
| `A-GLAZ` | 3 | Green | 0.25 mm | Window assemblies, sashes, and multi-line glazing |
| `A-COLS` | 1 | Red | 0.50 mm | Structural columns (concrete, steel, timber) |
| `A-STAIR` | 6 | Magenta | 0.35 mm | Stair treads, risers, stringers, walk lines, and landings |
| `A-FURN` | 8 | Dark Gray | 0.18 mm | Loose furniture (beds, sofas, dining tables, desks) |
| `A-FIXT` | 8 | Dark Gray | 0.18 mm | Plumbing and sanitary fixtures (WC, basin, shower, tub) |
| `A-FLOR-FIN` | 9 | Light Gray | 0.13 mm | Floor pattern hatches (tile grids, parquet, wet areas) |
| `A-ANNO-TEXT` | 7 | White/Black | 0.25 mm | Room labels, title notes, general text annotations |
| `A-ANNO-DIMS` | 7 | White/Black | 0.18 mm | Exterior overall and chained opening dimension lines |
| `Defpoints` | 7 | White/Black | Default | Dimension definition points (non-printing) |

### Layer Zero (`0`) Hygiene Policy
The default AutoCAD layer `0` is reserved exclusively for internal block definitions and must remain completely clean of primary drawing entities. The DXF Inspector audits `layer0Empty` to guarantee zero stray geometries on layer `0`.

---

## 3. Window Sill-Height Provenance & Non-Silent Default Policy

### The Architectural Problem
Downstream 3D Building Information Modeling (BIM) engines require a numeric window sill height to construct 3D wall openings and window geometry. However, hand-drawn floor plan sketches frequently omit vertical annotations such as sill height ($h_{\text{sill}}$).

Silently inserting an assumed default (e.g. $900\text{ mm}$) without explicit provenance tracking misleads reviewers into believing the dimension was verified from the source drawing.

### The Explicit Provenance Rule
When a window sill height is unannotated in the source sketch:
1. **Fallback Value**: $900.0\text{ mm}$ is supplied to ensure geometric compatibility with downstream BIM engines without causing `TypeError` crashes.
2. **Provenance Tag**: The window entry in `compile_bim_handoff` is explicitly tagged:
   ```json
   {
     "id": "WIN-01",
     "type": "window",
     "sillHeight": 900.0,
     "sillHeightProvenance": "assumed_default_unverified",
     "source": "inferred"
   }
   ```
3. **Uncertainty Register Entry**: An explicit uncertainty item is registered in the companion handoff JSON and approval package:
   ```json
   {
     "id": "unc_WIN-01_sill",
     "target": "openings[WIN-01].sillHeight",
     "description": "Window WIN-01 sill height unannotated in sketch; standard 900mm assumed pending reviewer verification",
     "assumedValue": 900.0,
     "confidence": "low",
     "status": "unresolved",
     "provenance": "assumed_default_unverified"
   }
   ```
4. **Human Review Gate Enforcement**: The project cannot receive final unconditional release until the reviewer acknowledges or updates the assumed parameter.

---

## 4. Door and Window Visual Representations

### Door Representations
- **Single Swing**: Door leaf rendered perpendicular or at $90^\circ$ to jamb, accompanied by a circular arc swing path indicating swing direction (`inward_right`, `inward_left`, `outward_right`, `outward_left`).
- **Double Leaf**: Dual symmetrical leaves originating from opposing jambs and meeting at wall opening center with dual quarter-circle swing arcs.
- **Sliding / Pocket**: Rectangular bypass leaves aligned parallel to wall centerline, indicating door leaf pocket recess.

### Window Glazing Representations
- Multi-line sill and jamb assembly on `A-GLAZ`.
- Exterior and interior sill boundary lines with central double-pane glazing line indicating fixed, casement, or sliding bypass configurations.
