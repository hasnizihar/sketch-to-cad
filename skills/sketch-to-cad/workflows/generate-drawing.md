# Workflow: Generate Drawing

This workflow specifies how to deterministically translate an approved [`floor-plan-model.json`](../schemas/floor-plan-model.json) into CADCraft MCP operations.

## Guiding Principles
1. **Primary Tool: `execute` with Structured JSON**:
   Prefer calling `execute(command="...", params={...})` over raw command line strings. It bypasses text escaping, spacing issues, and interactive prompts.
2. **Openings Cut Cleanly**:
   Wall lines must **never** run continuously across door or window openings. Every wall hosting an opening is subdivided into distinct solid segments on either side of the opening.
3. **Sealed Wall Cavities (Jamb End-Caps)**:
   All door cutouts must be capped across the wall thickness with transverse jamb lines on the wall layer (`A-WALL-EXTR` or `A-WALL-INTR`) so wall cavities do not appear open or unclosed.
4. **Layer Separation**:
   Entities must be drawn on their designated AIA layer (`A-WALL-EXTR`, `A-WALL-INTR`, `A-DOOR`, `A-GLAZ`, `A-ANNO-TEXT`, `A-ANNO-DIMS`).
5. **Readable Dimension Scaling**:
   Standard millimeter architectural plans require scaled dimension styles (`textHeight >= 150mm`, `arrowSize >= 120mm`) so annotations remain crisp and readable at standard zoom levels.

---

## Stage 1: Initialize Clean Drawing Session
```json
new_drawing(metric=true)
```
Verify via `inspect_drawing` that the session starts in an empty model space.

---

## Stage 2: Create Standard AIA Layers & Dimension Style
Call `execute` with `layer.new` for each standard layer:
```python
execute(command="layer.new", params={"name": "A-WALL-EXTR", "color": "cyan"})
execute(command="layer.new", params={"name": "A-WALL-INTR", "color": "green"})
execute(command="layer.new", params={"name": "A-DOOR", "color": "yellow"})
execute(command="layer.new", params={"name": "A-GLAZ", "color": "blue"})
execute(command="layer.new", params={"name": "A-ANNO-TEXT", "color": "red"})
execute(command="layer.new", params={"name": "A-ANNO-DIMS", "color": "magenta"})
```

Create a dedicated architectural dimension style to ensure visible numeric text:
```python
execute(command="dimstyle.new", params={
    "name": "Arch",
    "textHeight": 180.0,
    "arrowSize": 140.0,
    "extExtend": 120.0,
    "extOffset": 60.0,
    "current": true
})
```

---

## Stage 3: Draw Exterior & Interior Walls with Clean Openings

### Layer Activation
```python
execute(command="layer.current", params={"name": "A-WALL-EXTR"})
```

### Deterministic Segmented Wall Generation
For each wall segment from $(x_1, y_1)$ to $(x_2, y_2)$ with thickness $T$:
1. If the wall has **no openings**:
   - Draw outer face: `execute(command="line", params={"points": [[x1_out, y1_out], [x2_out, y2_out]]})`
   - Draw inner face: `execute(command="line", params={"points": [[x1_in, y1_in], [x2_in, y2_in]]})`
2. If the wall has an **opening** of width $W$ at center $C$:
   - Calculate opening start $O_1 = C - (W / 2)$ and opening end $O_2 = C + (W / 2)$.
   - Draw outer face Segment 1: from wall start to $O_1$.
   - Draw outer face Segment 2: from $O_2$ to wall end.
   - Draw inner face Segment 1: from inner start to inner $O_1$.
   - Draw inner face Segment 2: from inner $O_2$ to inner end.
   - **Seal Wall Cavity**: Draw transverse jamb end-caps across the wall thickness at $O_1$ and $O_2$:
     `execute(command="line", params={"points": [P_outer_O1, P_inner_O1]})`
     `execute(command="line", params={"points": [P_outer_O2, P_inner_O2]})`

This guarantees that openings are cleanly cut without overlapping lines or hollow, floating wall cavities.

---

## Stage 4: Add Windows (`A-GLAZ`)
```python
execute(command="layer.current", params={"name": "A-GLAZ"})
```
For each window of width $W$ across wall thickness $T$:
1. **Jamb End Caps**:
   - Left jamb: `execute(command="line", params={"points": [P_outer_left, P_inner_left]})`
   - Right jamb: `execute(command="line", params={"points": [P_outer_right, P_inner_right]})`
2. **Glass Centerline**:
   - `execute(command="line", params={"points": [P_mid_left, P_mid_right]})`

---

## Stage 5: Add Doors & Swings (`A-DOOR`)
```python
execute(command="layer.current", params={"name": "A-DOOR"})
```
For each single swing door of width $W$ at hinge point $(h_x, h_y)$:
1. **Door Leaf**:
   - Draw open panel at 90°:
     `execute(command="line", params={"points": [[hx, hy], [leaf_end_x, leaf_end_y]]})`
2. **Swing Arc**:
   - Draw 90° swing arc:
     `execute(command="arc", params={"center": [hx, hy], "radius": W, "start": start_angle, "end": end_angle})`

Verify that the door leaf sits flush against the host jamb and swings inward against an adjacent wall.

---

## Stage 6: Register & Insert Reusable Architectural Elements

For each element defined in `model.elements`:
1. **Approval Verification**: Verify element provenance. If `source == "proposed"`, confirm that status is explicitly `"approved"`. Never draft unapproved proposals.
2. **Block Registration**: Query drawing blocks via `inspect_drawing()`. If the block definition does not yet exist in the drawing session, register it on its designated AIA layer (`A-FURN`, `A-FIXT`, `A-STAIR`, or `A-COLS`) using `register_cad_block()` from [references/architectural-element-library.md](../references/architectural-element-library.md):
   ```python
   execute(command="block", params={
       "name": element["blockId"],
       "base": [0.0, 0.0],
       "handles": drawn_primitive_handles,
       "keep": "delete"
   })
   ```
3. **Block Placement**: Switch to target layer and insert block reference at room coordinates $(X, Y)$ with specified rotation ($0^\circ, 90^\circ, 180^\circ, 270^\circ$) and scale:
   ```python
   execute(command="insert", params={
       "name": element["blockId"],
       "at": element["position"],
       "rotation": element.get("rotation", 0.0),
       "scale": element.get("scale", 1.0)
   })
   ```

---

## Stage 7: Apply Floor Finishes & Tile Hatches (`A-FLOR-FIN`)

For each floor finish in `model.finishes`:
```python
execute(command="layer.current", params={"name": "A-FLOR-FIN"})
```
1. Draw closed boundary polyline or rectangle along room walls:
   `execute(command="rectang", params={"p1": boundary[0], "p2": boundary[1]})`
2. Apply hatching using the boundary handle:
   ```python
   execute(command="hatch", params={
       "handles": [boundary_handle],
       "pattern": "ANSI37",
       "scale": tile_size / 15.0
   })
   ```

---

## Stage 8: Room Labels & Annotations (`A-ANNO-TEXT`)
```python
execute(command="layer.current", params={"name": "A-ANNO-TEXT"})
```
For each room in `model.rooms`:
- If the space is a wide room:
  ```python
  execute(command="text", params={
      "at": room["labelPosition"],
      "text": room["name"],
      "height": 180,
      "justify": "MC"
  })
  ```
- If the space is a narrow corridor or hallway ($\le 1200\text{ mm}$ wide):
  Format text into two stacked, centered lines (e.g., line 1: `CENTRAL` at $Y+125$, line 2: `CORRIDOR` at $Y-125$, `height: 140`) to maintain clear margins from adjacent partitions.

---

## Stage 9: Dimension Chains (`A-ANNO-DIMS`)
```python
execute(command="layer.current", params={"name": "A-ANNO-DIMS"})
```
For each dimension in `model.dimensions`:
- Set explicit readable text strings (e.g., `"8000"`, `"8700"`).
- For horizontal dimensions:
  ```python
  execute(command="dimlinear", params={
      "p1": dim["p1"],
      "p2": dim["p2"],
      "at": dim["at"],
      "text": str(dim["value"])
  })
  ```
- For vertical dimensions, include `rotation: 90.0` so extension lines and text align along the Y-axis:
  ```python
  execute(command="dimlinear", params={
      "p1": dim["p1"],
      "p2": dim["p2"],
      "at": dim["at"],
      "rotation": 90.0,
      "text": str(dim["value"])
  })
  ```

---

## Stage 10: Frame View Extents & Export DXF
```python
execute(command="zoom", params={"mode": "extents"})
save(path=".../floor-plan.dxf")
```

---

## Stage 11: Compile Companion BIM Handoff JSON
Generate `<drawing-name>.handoff.json` using `compile_bim_handoff(...)`:
- Validated against [`bim-handoff.schema.json`](../schemas/bim-handoff.schema.json).
- Cross-references all DXF layers, registered blocks, entity counts, wall centerlines, and opening hosts.
- Preserves `null` for unannotated vertical dimensions (storey elevations, door/window heights) for downstream human approval.

---

## Multi-Storey Floor Plan Generation (Milestone 6)

For multi-storey residential projects:
1. **Approval Verification**: Verify that every level declared in `floors` has status `"approved"` in `approval.floorApprovals` and `floors[i].status`.
2. **Independent Sessions**: For each storey in sequence:
   - Call `new_drawing(metric=true)`.
   - Setup AIA layers and dimension styles.
   - Filter walls, openings, rooms, elements, finishes, and dimensions matching the target `floorId`.
   - Draw entities, frame extents (`zoom extents`), and save to `<project>-<level-id>.dxf` and `<project>-<level-id>.png`.
3. **Unified Companion Manifest**:
   - Compile `<project>.handoff.json` mapping all per-floor drawings in `dxf.floorDrawings` and recording vertical circulation in `stairs`.
   - Compile consolidated reports (`<project>.report.json`, `.report.md`, `.report.pdf`) with floor-by-floor schedules and vertical coordination verification.

Proceed immediately to [`validate-and-export.md`](validate-and-export.md).

---

## Stage 12: End-to-End Orchestration & Visual QA (Milestone 7)

For full sketch-to-CAD automation, execute through `scripts/sketch_to_cad_pipeline.py`:
1. **Automated Pipeline**: Coordinates sketch ingestion, observation extraction, geometry reconstruction, draft model compilation, human approval gate, DXF drafting, BIM handoff, and reports.
2. **Visual Quality Assurance**: Automatically executes `perform_visual_qa(...)` comparing source sketch features against the generated CAD model, outputting `<project>.visual-qa.json` and `<project>.visual-qa.md`.
3. Reference: See [`references/end-to-end-pipeline.md`](../references/end-to-end-pipeline.md).

