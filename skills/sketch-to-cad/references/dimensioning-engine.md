# Dimensioning Engine & Collision Avoidance

## 1. Overview
The Sketch-to-CAD Dimensioning Engine (`scripts/dimension_engine.py`) generates complete, legible, and professional architectural dimension strings adhering to standard 3-tier dimensioning conventions without overlapping text or obscuring room labels.

---

## 2. Three-Tier Architectural Dimensioning Hierarchy

To avoid visual clutter and provide immediate legibility at multiple scales, dimensions are organized into three hierarchical tiers:

```
[Tier 1: Overall Footprint (Exterior)]  ← 1600mm offset from wall
[Tier 2: Chained Openings (Exterior)]   ←  900mm offset from wall
---------------- Exterior Wall Line -----------------
[Tier 3: Internal Room Callouts]        ← Centered in room
```

### Tier 1: Overall Building Footprint
- Single continuous dimension chain along each cardinal side (South, North, West, East) bounding the total exterior footprint.
- Dimension line offset: $1600\text{ mm}$ from the exterior wall perimeter.
- Dimension text: e.g. `10 000` or `10.00 m`.

### Tier 2: Chained Exterior Openings
- Continuous dimension chain along the exterior wall measuring:
  1. From corner to first opening jamb.
  2. Opening width (window or exterior door).
  3. Solid wall pier between consecutive openings.
  4. From final opening jamb to opposite building corner.
- Dimension line offset: $900\text{ mm}$ from the exterior wall perimeter.
- Summation check: $\sum \text{chained segments} = \text{overall exterior length}$.

### Tier 3: Internal Room Callouts
- Centered annotations inside each enclosed room boundary:
  ```
  LIVING ROOM
  4.00 x 5.00 m (20.0 m²)
  ```
- Formatted in both meters ($4.00 \times 5.00\text{ m}$) and millimeters ($4000 \times 5000\text{ mm}$) with Shoelace area calculation.

---

## 3. Dimension Style Specifications

The standard metric architectural dimension style (`ARCH_METRIC_STANDARD`) defines:

| Parameter | Value (Model mm) | Standard Architectural Practice |
|:---|:---:|:---|
| Text Height | $180\text{ mm}$ | $1.8\text{ mm}$ at 1:100 scale |
| Arrow / Tick Size | $140\text{ mm}$ | $45^\circ$ architectural oblique tick |
| Extension Line Overshoot | $120\text{ mm}$ | Extension past dimension line |
| Extension Line Offset | $60\text{ mm}$ | Gap from measured wall feature |
| Text Offset | $50\text{ mm}$ | Distance above dimension line |
| Decimal Places | $0$ (mm) / $2$ (m) | No fractional millimeters in construction |

---

## 4. Collision Detection & Resolution Algorithms

In dense floor plans, dimension text frequently crosses room labels, door swing arcs, or adjacent witness lines. The engine implements automated collision resolution:

### Collision Types Audited
1. **`label_crossing`**: Dimension text box overlaps a room name label or area callout.
2. **`text_overlap`**: Dimension text overlaps an adjacent dimension's text box.
3. **`line_crossing`**: Dimension witness line intersects another dimension string.

### Resolution Strategy
1. **Vertical / Offset Shifting**: When text overlaps a room label or feature, the engine computes a separation vector and shifts the text position `at` by at least $150\text{ mm}$ perpendicular to the collision.
2. **Tier Staggering**: When adjacent chained dimensions have narrow spans ($< 600\text{ mm}$), alternating dimensions are staggered onto a secondary offset line.
3. **Leader Line Fallback**: If an opening span is narrower than the dimension text width ($< 450\text{ mm}$), the text is placed externally with an architectural leader line.
