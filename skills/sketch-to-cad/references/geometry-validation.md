# Architectural Geometry Validation Engine

This document defines the mathematical, topological, and architectural validation algorithms implemented by `scripts/geometry_validation.py` to ensure engineering integrity before DXF generation and BIM handoff.

---

## 1. Wall Network Graph & Junction Topology

The wall network is modeled as a 2D planar graph $G = (V, E)$, where edges $E$ are wall centerlines and vertices $V$ are endpoints or interior connection points.

### 1.1 Endpoint Clustering & Tolerances
- Geometric connection tolerance: $\text{tol} = 25.0\text{ mm}$ (endpoints within $25\text{ mm}$ are treated as coincident).
- Projection tolerance: $d_{\text{proj}} \le 35.0\text{ mm}$ (points projecting onto an adjacent segment within $35\text{ mm}$ form T-junctions).

### 1.2 Junction Typology Classification
1. **L-Junction**: Exactly 2 endpoints meeting at a vertex ($d \le 30\text{ mm}$).
2. **T-Junction**: An endpoint projecting onto the interior parameter $t \in [0.03, 0.97]$ of another wall segment.
3. **Cross-Junction (X)**: 4 endpoints meeting at a common vertex, or 2 segments intersecting internally.
4. **Disconnected Endpoints**: An endpoint with 0 connections to other walls. If distance to nearest wall is between $35\text{ mm}$ and $250\text{ mm}$, flagged as an **unintended gap (warning)**; otherwise flagged as a **free-standing stub (informational)**.

### 1.3 Degenerate Wall Detection
- Walls with length $L < 10\text{ mm}$ are classified as **blocking** errors.
- Walls with length $10\text{ mm} \le L < 50\text{ mm}$ are classified as **major** errors.

---

## 2. Opening & Door Swing Clearances

### 2.1 Host Wall Interval Containment
Every opening of width $W$ must reside strictly on its host wall $L_{\text{wall}}$:
$$t_1 = d_{\text{start}}, \quad t_2 = d_{\text{start}} + W$$
- If $t_1 < -1.0\text{ mm}$ or $t_2 > L_{\text{wall}} + 1.0\text{ mm}$, flagged as **blocking** (`Opening extends beyond host wall`).

### 2.2 Structural Corner Clearance
Openings must maintain a minimum structural return for framing and trim:
- Minimum corner clearance: $\Delta_{\text{corner}} \ge 50\text{ mm}$.
- If $t_1 < 50\text{ mm}$ or $(L_{\text{wall}} - t_2) < 50\text{ mm}$, flagged as a **warning** (`Corner clearance violation`).

### 2.3 Overlapping Openings
Openings on the same wall are sorted by $t_1$. If $t_2^{(k)} > t_1^{(k+1)}$, the opening spans overlap, which is flagged as a **blocking** error.

### 2.4 Door Swing Interference Check
If two door centers are closer than $0.85 \times (W_1 + W_2)$, their swing arcs have potential leaf collisions, flagged as a **warning** (`Door swing clearance conflict`).

---

## 3. Room Polygon Validation

### 3.1 Shoelace Area Computation
Room areas are computed using the Gauss Shoelace formula over ordered polygon vertices $(x_i, y_i)$:
$$A = \frac{1}{2} \left| \sum_{i=0}^{n-1} (x_i y_{i+1} - x_{i+1} y_i) \right|$$
- Areas computed in $\text{mm}^2$ are converted to $\text{m}^2$ ($1\text{ m}^2 = 1,000,000\text{ mm}^2$).
- Zero or negative area polygons are flagged as **blocking**.

### 3.2 Self-Intersection (Bowtie Polygons)
Any room boundary whose edges cross internally ($e_i \cap e_j \neq \emptyset$ for non-adjacent edges) is classified as a **blocking** error. Non-convex polygons (e.g. L-shaped rooms) are permitted provided they do not self-cross.

### 3.3 Overlapping Room Boundaries
Adjacent interior rooms must not overlap. Overlap is detected via 2D bounding-box rejection, followed by edge intersection checks and interior centroid containment tests. Overlapping room interiors are flagged as **blocking**.

### 3.4 External Envelope Containment
All room vertices and placed elements must fall strictly within the building footprint envelope:
$$-\text{tol} \le x_i \le W_{\text{env}} + \text{tol}, \quad -\text{tol} \le y_i \le D_{\text{env}} + \text{tol}$$
Vertices extending beyond envelope bounds are flagged as **major** discrepancies.

---

## 4. Multi-Storey Level Isolation

When validating multi-storey models, geometry validation filters all elements by floor identifier (`floorId` / `level`). Each level's wall graph, openings, and rooms are verified independently to ensure no cross-level phantom collisions.
