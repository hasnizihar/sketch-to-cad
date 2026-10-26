# Sample Project: Studio Apartment Sketch to CAD

This reference project demonstrates the complete, deterministic execution of the 
`sketch-to-cad` workflow from user sketch interpretation to verified CAD generation.

## 1. Input Scenario
A user uploads a rough sketch of a studio apartment with the notation `6000 x 5000` along the exterior walls, with an enclosed bathroom in the top-right corner, a kitchenette near the entrance, and a main studio living space.

---

## 2. Structured Intermediate Floor Plan Model
```json
{
  "$schema": "../schemas/floor-plan-model.json",
  "metadata": {
    "projectName": "Studio-Unit-A1",
    "author": "Antigravity Sketch-to-CAD Agent",
    "version": "1.0",
    "createdAt": "2026-10-26T21:30:00Z"
  },
  "status": "approved",
  "approval": {
    "approvedBy": "User",
    "approvedAt": "2026-10-26T21:35:00Z",
    "approvalNotes": "Confirmed 6m x 5m layout, 1.6m bathroom width, and 200mm exterior wall thickness."
  },
  "units": "mm",
  "envelope": {
    "width": 6000,
    "depth": 5000,
    "origin": [0, 0],
    "widthSource": "explicit",
    "depthSource": "explicit"
  },
  "uncertainties": [
    {
      "id": "U1",
      "target": "Bathroom Width",
      "description": "Partition position unlabeled in sketch.",
      "assumedValue": "1600mm",
      "confidence": "medium",
      "status": "confirmed"
    },
    {
      "id": "U2",
      "target": "Wall Thickness",
      "description": "Wall thickness not annotated on sketch.",
      "assumedValue": "Ext=200mm, Int=100mm",
      "confidence": "high",
      "status": "confirmed"
    }
  ],
  "walls": [
    { "id": "W-EXT-S", "type": "exterior", "start": [0, 0], "end": [6000, 0], "thickness": 200, "layer": "A-WALL-EXTR", "source": "explicit", "openingIds": ["WIN-1", "D-ENTR"] },
    { "id": "W-EXT-E", "type": "exterior", "start": [6000, 0], "end": [6000, 5000], "thickness": 200, "layer": "A-WALL-EXTR", "source": "explicit", "openingIds": [] },
    { "id": "W-EXT-N", "type": "exterior", "start": [6000, 5000], "end": [0, 5000], "thickness": 200, "layer": "A-WALL-EXTR", "source": "explicit", "openingIds": ["WIN-2"] },
    { "id": "W-EXT-W", "type": "exterior", "start": [0, 5000], "end": [0, 0], "thickness": 200, "layer": "A-WALL-EXTR", "source": "explicit", "openingIds": [] },
    { "id": "W-INT-V", "type": "interior", "start": [4300, 200], "end": [4300, 4800], "thickness": 100, "layer": "A-WALL-INTR", "source": "estimated", "openingIds": [] },
    { "id": "W-INT-H", "type": "interior", "start": [4400, 2600], "end": [5800, 2600], "thickness": 100, "layer": "A-WALL-INTR", "source": "estimated", "openingIds": ["D-BATH"] }
  ],
  "openings": [
    { "id": "D-ENTR", "type": "door", "wallId": "W-EXT-S", "center": [5000, 100], "width": 900, "swing": "inward-left", "source": "inferred" },
    { "id": "D-BATH", "type": "door", "wallId": "W-INT-H", "center": [4900, 2650], "width": 750, "swing": "inward-right", "source": "inferred" },
    { "id": "WIN-1", "type": "window", "wallId": "W-EXT-S", "center": [2100, 100], "width": 1800, "sillHeight": 900, "source": "estimated" },
    { "id": "WIN-2", "type": "window", "wallId": "W-EXT-N", "center": [5100, 4900], "width": 800, "sillHeight": 1400, "source": "estimated" }
  ],
  "rooms": [
    { "id": "R1", "name": "STUDIO / LIVING", "approximateArea": 19.3, "labelPosition": [2150, 2500], "boundaryCorners": [[200, 200], [4300, 200], [4300, 4800], [200, 4800]] },
    { "id": "R2", "name": "BATHROOM", "approximateArea": 3.1, "labelPosition": [5100, 3700], "boundaryCorners": [[4400, 2700], [5800, 2700], [5800, 4800], [4400, 4800]] },
    { "id": "R3", "name": "KITCHEN / ENTRY", "approximateArea": 3.4, "labelPosition": [5100, 1400], "boundaryCorners": [[4400, 200], [5800, 200], [5800, 2600], [4400, 2600]] }
  ],
  "dimensions": [
    { "id": "DIM-1", "tier": 3, "p1": [0, 0], "p2": [6000, 0], "at": [3000, -500], "source": "explicit", "text": "6000" },
    { "id": "DIM-2", "tier": 3, "p1": [0, 0], "p2": [0, 5000], "at": [-500, 2500], "source": "explicit", "text": "5000" }
  ]
}
```

---

## 3. Verified CAD Execution Sequence

```python
# 1. New Metric Drawing Session
new_drawing(metric=true)

# 2. Define Standard AIA Layers
execute(command="layer.new", params={"name": "A-WALL-EXTR", "color": "cyan"})
execute(command="layer.new", params={"name": "A-WALL-INTR", "color": "green"})
execute(command="layer.new", params={"name": "A-DOOR", "color": "yellow"})
execute(command="layer.new", params={"name": "A-GLAZ", "color": "blue"})
execute(command="layer.new", params={"name": "A-ANNO-TEXT", "color": "red"})
execute(command="layer.new", params={"name": "A-ANNO-DIMS", "color": "magenta"})

# 3. Draw Exterior Envelope (segmented around door and window openings)
execute(command="layer.current", params={"name": "A-WALL-EXTR"})

# South Wall (Outer face segments around WIN-1 at [1200-3000] and D-ENTR at [4550-5450])
execute(command="line", params={"points": [[0, 0], [1200, 0]]})
execute(command="line", params={"points": [[3000, 0], [4550, 0]]})
execute(command="line", params={"points": [[5450, 0], [6000, 0]]})

# South Wall (Inner face segments offset by 200mm)
execute(command="line", params={"points": [[200, 200], [1200, 200]]})
execute(command="line", params={"points": [[3000, 200], [4550, 200]]})
execute(command="line", params={"points": [[5450, 200], [5800, 200]]})

# East Wall (Solid)
execute(command="line", params={"points": [[6000, 0], [6000, 5000]]})
execute(command="line", params={"points": [[5800, 200], [5800, 4800]]})

# North Wall (Outer face segments around WIN-2 at [4700-5500])
execute(command="line", params={"points": [[6000, 5000], [5500, 5000]]})
execute(command="line", params={"points": [[4700, 5000], [0, 5000]]})

# North Wall (Inner face segments)
execute(command="line", params={"points": [[5800, 4800], [5500, 4800]]})
execute(command="line", params={"points": [[4700, 4800], [200, 4800]]})

# West Wall (Solid)
execute(command="line", params={"points": [[0, 5000], [0, 0]]})
execute(command="line", params={"points": [[200, 4800], [200, 200]]})

# 4. Draw Interior Partition Walls
execute(command="layer.current", params={"name": "A-WALL-INTR"})
# Vertical Partition
execute(command="line", params={"points": [[4300, 200], [4300, 4800]]})
execute(command="line", params={"points": [[4400, 200], [4400, 4800]]})
# Horizontal Partition (segmented around bathroom door [4525-5275])
execute(command="line", params={"points": [[4400, 2600], [4525, 2600]]})
execute(command="line", params={"points": [[5275, 2600], [5800, 2600]]})
execute(command="line", params={"points": [[4400, 2700], [4525, 2700]]})
execute(command="line", params={"points": [[5275, 2700], [5800, 2700]]})

# 5. Draw Doors & Swings
execute(command="layer.current", params={"name": "A-DOOR"})
# Main Entry Door Leaf (open 90°) & Arc
execute(command="line", params={"points": [[4550, 200], [4550, 1100]]})
execute(command="arc", params={"center": [4550, 200], "radius": 900, "start": 0, "end": 90})
# Bathroom Door Leaf & Arc
execute(command="line", params={"points": [[4525, 2700], [4525, 3450]]})
execute(command="arc", params={"center": [4525, 2700], "radius": 750, "start": 0, "end": 90})

# 6. Draw Windows
execute(command="layer.current", params={"name": "A-GLAZ"})
# WIN-1 (South Window): Jambs and Centerline
execute(command="line", params={"points": [[1200, 0], [1200, 200]]})
execute(command="line", params={"points": [[3000, 0], [3000, 200]]})
execute(command="line", params={"points": [[1200, 100], [3000, 100]]})
# WIN-2 (North Window): Jambs and Centerline
execute(command="line", params={"points": [[4700, 5000], [4700, 4800]]})
execute(command="line", params={"points": [[5500, 5000], [5500, 4800]]})
execute(command="line", params={"points": [[4700, 4900], [5500, 4900]]})

# 7. Add Room Labels
execute(command="layer.current", params={"name": "A-ANNO-TEXT"})
execute(command="text", params={"at": [2150, 2500], "text": "STUDIO / LIVING", "height": 180, "justify": "MC"})
execute(command="text", params={"at": [5100, 3700], "text": "BATHROOM", "height": 160, "justify": "MC"})
execute(command="text", params={"at": [5100, 1400], "text": "KITCHEN / ENTRY", "height": 160, "justify": "MC"})

# 8. Add Dimensions
execute(command="layer.current", params={"name": "A-ANNO-DIMS"})
execute(command="dimlinear", params={"p1": [0, 0], "p2": [6000, 0], "at": [3000, -500]})
execute(command="dimlinear", params={"p1": [0, 0], "p2": [0, 5000], "at": [-500, 2500]})

# 9. Frame Extents & Validate
execute(command="zoom", params={"mode": "extents"})
inspect_drawing(entities=true)
render(fit=true)

# 10. Persist Outputs
save(path="studio-plan.dxf")
save(path="studio-plan.png")
```
