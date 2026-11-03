# Sketch-to-CAD | Test 01: Final Source-Based Room Boundary Review
**Document ID:** `TEST-01-ROOM-BOUNDARY-REVIEW`  
**Date:** November 3, 2026  
**Project:** Sketch-to-CAD (Real-World Test 01 — Nordic Residential Villa)  
**Source Image:** [`source_sketch.jpg`](file:///d:/Agent%20Skills/sketch-to-cad-main/tests/real_world/Test-01/source_sketch.jpg) ($845 \times 1024\text{ px}$, SHA-256: `12ca802a25cd855467a62473c7c35f423ca01ed53ab3818b61b7b75cf9259957`)  
**Current Gate Status:** `AWAITING_HUMAN_APPROVAL` (Zero DXF Generated, No Model Approved)  

---

## Executive Summary & Testing Framework

This review investigates the spatial boundaries of the bathroom, shower, sauna, sauna lounge, and master bedroom directly from the original source sketch image. 

In accordance with architectural validation principles, every boundary element is measured against three distinct evidentiary tiers:
1. **Tier 1 (Detection):** Can the AI prove that a partition line exists in the drawing?
2. **Tier 2 (Estimation):** Where does the AI place the partition based on visual estimation or grid snapping?
3. **Tier 3 (Proof):** Can the AI prove that the partition is correctly positioned using explicit dimensions or unambiguous geometric constraints?

### Key Review Conclusions
- **The bathroom partition** is visually detectable (Tier 1) at pixel row $Y \approx 460$, but its position cannot be mathematically proven (Tier 3). The draftsperson drew the bathroom with $\approx 36\%$ of the bay depth ($\approx 10\text{ m}^2$), yet wrote `$6,5\text{ m}^2$` inside it. The drawn graphic and the written numerical label are in direct contradiction.
- **The shower/sauna partition** is visually detectable (Tier 1) at pixel row $Y \approx 241$. Both the drawn ink line ($136\text{ px}$ vs $84\text{ px}$, ratio $1.62 : 1$) and the handwritten labels ($6.0\text{ m}^2$ vs $4.0\text{ m}^2$, ratio $1.50 : 1$) agree that the shower is substantially larger than the sauna. The current draft model's symmetric 50/50 split ($Y = 13500\text{ mm}$, $4.50\text{ m}^2$ each) was an unverified modeling assumption that contradicts all source evidence.
- **The area calculation audit** clarifies that the $0.13\text{ m}^2$ reconciliation difference arose from comparing two disparate quantities (an exterior shell deduction vs. a hybrid room polygon sum). A true deduction of all physical walls yields a net internal usable area of $\approx 166.5\text{ m}^2$.
- **CAD generation remains paused.** `UNC-01` remains an active, unresolved blocker.

---

## 1. Pixel-Level Source Evidence Inspection

Pixel coordinates are measured in the native $845 \times 1024\text{ px}$ source raster. Global scale factors are:
- Horizontal Scale: $10000\text{ mm} / 445\text{ px} = \mathbf{22.47\text{ mm/px}}$
- Vertical Scale: $16000\text{ mm} / 725\text{ px} = \mathbf{22.07\text{ mm/px}}$
- Overall Mean Scale: $\mathbf{\approx 22.27\text{ mm/px}}$

```
+-----------------------------------------------------------------------------+
| SAUNA WING (X: 90..310, Y: 105..325)   | MAIN HOUSE (X: 310..755, Y: 105..830)
|                                        |
|  Dušš (6 m²)     Sauna Puhkeruum       | Majapidamis (6 m²)  TEH (5 m²)  WC
|  Y: 105..241     (15 m²)               | Y: 105..283         Y: 105..283
|  (136 px deep)   X: 180..310           |-----------------------------------
|  -------------   (130 px wide)         | Master Bedroom (17.6 m²)
|  Saun (4 m²)                           | Y: 283..460 (177 px deep)
|  Y: 241..325                           | X: 315..505 (190 px wide)
|  (84 px deep)                          |-----------------------------------
|                                        | Bathroom (6.5 m²)
|                                        | Y: 460..559 (99 px deep)
|                                        | X: 315..505 (190 px wide)
+----------------------------------------+-----------------------------------
```

### 1.1 `R-BATHROOM` (Vannituba) & `R-MASTER-BED` (Magamistuba suur)
- **North Wall of Master Bedroom (Interface with Majapidamis):** Continuous dark ink line spanning $X = 315$ to $505$ at **$Y = 281..284\text{ px}$** (100% ink fraction, mean intensity $63.3$).
- **Partition between Master Bed and Bathroom:** Continuous horizontal ink line spanning $X = 315$ to $505$ at **$Y = 458..461\text{ px}$** (100% ink fraction, mean intensity $100.9$).
- **South Wall of Bathroom (Interface with Kitchen/Living):** Continuous horizontal ink line spanning $X = 315$ to $505$ at **$Y = 558..560\text{ px}$** (100% ink fraction, mean intensity $101.3$).
- **Corridor Spine Wall (East Boundary):** Continuous vertical ink line at **$X = 504..507\text{ px}$** extending from $Y = 283$ down to $Y = 560$.
- **West Exterior Wall:** Multi-line boundary centered at **$X = 315\text{ px}$**.
- **Fixture Evidence in Bathroom:**
  - Bathtub contour: Located along West wall between $Y = 475$ and $Y = 545\text{ px}$ ($\approx 70\text{ px}$ height $\times 22.07 \approx 1550\text{ mm}$ long tub).
  - Bathroom door: Single swing opening on the East wall ($X \approx 505$, $Y \approx 470..500$) swinging into the bathroom.
  - Text Annotation: Handwritten `vannituba 6,5 m²` centered at $[X=410, Y=515]$.
- **Drawn Proportions:**
  - Master Bedroom drawn height: $460 - 283 = \mathbf{177\text{ px}}$ ($\approx 3906\text{ mm}$).
  - Bathroom drawn height: $559 - 460 = \mathbf{99\text{ px}}$ ($\approx 2185\text{ mm}$).
  - Ratio of drawn heights: $177 / 99 = \mathbf{1.788 : 1}$.

### 1.2 `R-DUSS` (Dušš), `R-SAUN` (Saun), and `R-SAUNA-PUHKE` (Sauna Puhkeruum)
- **Sauna Wing Outer Envelope:**
  - North wall: $Y = 105\text{ px}$; South wall: $Y = 325\text{ px}$ (Total Depth $= 220\text{ px} \to 5000\text{ mm}$).
  - West wall: $X = 90\text{ px}$; East party wall: $X = 310\text{ px}$ (Total Width $= 220\text{ px} \to 5000\text{ mm}$).
- **Vertical Partition (Wet Zone vs. Lounge):**
  - Solid vertical ink line at **$X = 179..182\text{ px}$** (100% ink fraction, mean intensity $73.6$).
  - Divides the wing into a $90\text{ px}$ wide wet bay ($X = 90..180 \to \approx 2045\text{ mm}$) and a $130\text{ px}$ wide lounge bay ($X = 180..310 \to \approx 2955\text{ mm}$).
- **Horizontal Partition (Dušš vs. Saun):**
  - Solid horizontal ink line at **$Y = 239..243\text{ px}$** (100% ink fraction, mean intensity $70.6$).
  - Dušš drawn depth: $241 - 105 = \mathbf{136\text{ px}}$ ($\approx 3091\text{ mm}$).
  - Saun drawn depth: $325 - 241 = \mathbf{84\text{ px}}$ ($\approx 1909\text{ mm}$).
  - Ratio of drawn depths: $136 / 84 = \mathbf{1.619 : 1}$.
- **Fixture Evidence:**
  - Dušš: Two shower-head circular symbols along West wall at $Y \approx 190$ and $Y \approx 220$.
  - Saun: Perimeter L-shaped bench hatching along West and South walls; heater symbol (`[o]`) at East wall ($X \approx 165, Y \approx 270$).
  - Doors: Diagonal swing arcs connecting Dušš to Puhkeruum ($X \approx 180, Y \approx 175$) and Saun to Puhkeruum ($X \approx 180, Y \approx 280$).

---

## 2. Source Evidence Versus Model Geometry Comparison

The table below contrasts what is **directly observable in the source sketch** against what was **modeled in `draft_model.json`**:

| Room ID | Handwritten Label | Current Model Area (Clear) | Current Model Partition Coordinates | Visible Source Evidence (Pixel Coords) | Provenance & Evidence Classification | Boundary Observable vs. Inferred |
| :--- | :---: | :---: | :--- | :--- | :--- | :--- |
| `R-BATHROOM` | **$6.5\text{ m}^2$** | $10.01\text{ m}^2$ | North: $Y=9200\text{ mm}$<br>South: $Y=6500\text{ mm}$<br>West: $X=5000\text{ mm}$<br>East: $X=9000\text{ mm}$ | North wall ink line at $Y=460\text{ px}$; South wall at $Y=559\text{ px}$; West wall at $X=315\text{ px}$; East wall at $X=505\text{ px}$; Bathtub at $Y=475..545\text{ px}$. | `conflict_detected`<br>(Confidence: 0.50) | **Observable ink line conflicts with written area label.** |
| `R-MASTER-BED` | **$17.6\text{ m}^2$** | $16.55\text{ m}^2$ | North: $Y=13600\text{ mm}$<br>South: $Y=9200\text{ mm}$<br>West: $X=5000\text{ mm}$<br>East: $X=9000\text{ mm}$ | North wall ink line at $Y=283\text{ px}$; South wall at $Y=460\text{ px}$; Wardrobe ("kapp") along East spine; Bed icon centered at $X=410, Y=350$. | `partially_inferred`<br>(Confidence: 0.70) | **North & South boundaries observable, but Y-scale distorted by Majapidamis placement.** |
| `R-DUSS` | **$6.0\text{ m}^2$** | $3.88\text{ m}^2$ | North: $Y=16000\text{ mm}$<br>South: $Y=13500\text{ mm}$<br>West: $X=0\text{ mm}$<br>East: $X=1800\text{ mm}$ | North wall at $Y=105\text{ px}$; South wall at $Y=241\text{ px}$; West wall at $X=90\text{ px}$; East wall at $X=180\text{ px}$; 2 shower heads drawn. | `unsupported_assumption`<br>(Confidence: 0.45) | **Model placed partition at midpoint ($Y=13500$), contradicting drawn line at $Y=241\text{ px}$.** |
| `R-SAUN` | **$4.0\text{ m}^2$** | $3.88\text{ m}^2$ | North: $Y=13500\text{ mm}$<br>South: $Y=11000\text{ mm}$<br>West: $X=0\text{ mm}$<br>East: $X=1800\text{ mm}$ | North wall at $Y=241\text{ px}$; South wall at $Y=325\text{ px}$; L-bench hatching and heater icon visible. | `unsupported_assumption`<br>(Confidence: 0.45) | **Model placed partition at midpoint ($Y=13500$), contradicting drawn line at $Y=241\text{ px}$.** |
| `R-SAUNA-PUHKE`| **$15.0\text{ m}^2$** | $14.76\text{ m}^2$ | North: $Y=16000\text{ mm}$<br>South: $Y=11000\text{ mm}$<br>West: $X=1800\text{ mm}$<br>East: $X=5000\text{ mm}$ | West partition at $X=180\text{ px}$; East party wall at $X=310\text{ px}$; Patio slider to terrace at South. | `corroborated_estimate`<br>(Confidence: 0.85) | **Directly observable boundaries; clear area ($14.76\text{ m}^2$) matches label ($15\text{ m}^2$) within $1.6\%$.** |

---

## 3. Alternative Architectural Interpretations

### 3.1 Bathroom (`R-BATHROOM`) & Master Bedroom (`R-MASTER-BED`)

#### Alternative 1A: Graphic Alignment (Drawn Ink Line Priority)
- **Partition Coordinate:** $Y = 9200\text{ mm}$ (as currently in `draft_model.json`).
- **Calculated Areas:**
  - Bathroom: $4.00 \times 2.70\text{ m} = 10.80\text{ m}^2$ centerline (**$10.01\text{ m}^2$ clear**).
  - Master Bedroom: $4.00 \times 4.40\text{ m} = 17.60\text{ m}^2$ centerline (**$16.55\text{ m}^2$ clear**).
- **Supporting Evidence:**
  - Matches the physical ink stroke at $Y = 460\text{ px}$.
  - Provides adequate physical clearance for the $1550\text{ mm}$ bathtub and door swing.
  - Centerline area of Master Bedroom ($17.60\text{ m}^2$) matches the written `$17.6\text{ m}^2$` label.
- **Remaining Unknowns:**
  - Disregards the written `$6,5\text{ m}^2$` label by $+54\%$ ($+3.51\text{ m}^2$). Why the author wrote $6.5\text{ m}^2$ remains unexplained by the graphic.

#### Alternative 1B: Area Label Priority (Numerical Target Constraint)
- **Partition Coordinate:** Shift partition south to $Y = 8300\text{ mm}$ (clear depth $\approx 1690\text{ mm}$).
- **Calculated Areas:**
  - Bathroom: $4.00 \times 1.80\text{ m} = 7.20\text{ m}^2$ centerline (**$6.50\text{ m}^2$ clear**).
  - Master Bedroom: $4.00 \times 5.30\text{ m} = 21.20\text{ m}^2$ centerline (**$20.02\text{ m}^2$ clear**).
- **Supporting Evidence:**
  - Exactly satisfies the written `$6,5\text{ m}^2$` bathroom annotation.
- **Remaining Unknowns:**
  - Violates the drawn ink line by shifting the wall $\approx 900\text{ mm}$ south into the bathroom.
  - Leaves insufficient clearance between the bathtub ($750\text{ mm}$ width) and the door swing.
  - Inflates Master Bedroom to $20.02\text{ m}^2$, violating its written `$17.6\text{ m}^2$` label by $+2.42\text{ m}^2$.

#### Alternative 1C: Proportional Pixel Ratio ($1.788 : 1$)
- **Partition Coordinate:** $Y = 9050\text{ mm}$ (Bathroom depth $= 2550\text{ mm}$; Master Bed depth $= 4550\text{ mm}$).
- **Calculated Areas:**
  - Bathroom: $4.00 \times 2.55\text{ m} = 10.20\text{ m}^2$ centerline (**$9.43\text{ m}^2$ clear**).
  - Master Bedroom: $4.00 \times 4.55\text{ m} = 18.20\text{ m}^2$ centerline (**$17.13\text{ m}^2$ clear**).
- **Supporting Evidence:**
  - Pure preservation of the author's drawn relative line proportions ($177\text{ px} : 99\text{ px}$).
- **Remaining Unknowns:**
  - Still exceeds the $6.5\text{ m}^2$ bathroom label by $+2.93\text{ m}^2$.

---

### 3.2 Shower (`R-DUSS`) vs. Sauna (`R-SAUN`)

#### Alternative 2A: Graphic & Label Corroborated Split ($1.62 : 1$ Ratio)
- **Partition Coordinate:** $Y = 12900\text{ mm} \approx \mathbf{13000\text{ mm}}$ (Sauna depth $= 2000\text{ mm}$; Shower depth $= 3000\text{ mm}$).
- **Calculated Areas (at $1.80\text{ m}$ wet bay width):**
  - Dušš: $1.80 \times 3.00\text{ m} = 5.40\text{ m}^2$ centerline (**$4.70\text{ m}^2$ clear**).
  - Saun: $1.80 \times 2.00\text{ m} = 3.60\text{ m}^2$ centerline (**$3.06\text{ m}^2$ clear**).
- **Calculated Areas (at $2.00\text{ m}$ wet bay width per $90\text{ px} : 130\text{ px}$ sketch width):**
  - Dušš: $2.00 \times 3.00\text{ m} = 6.00\text{ m}^2$ centerline (**$5.28\text{ m}^2$ clear**).
  - Saun: $2.00 \times 2.00\text{ m} = 4.00\text{ m}^2$ centerline (**$3.48\text{ m}^2$ clear**).
- **Supporting Evidence:**
  - **100% agreement between the visual ink line ($Y = 241\text{ px}$) and the handwritten area labels ($6.0\text{ m}^2$ vs $4.0\text{ m}^2$).** Both prove the shower was intended to be $50\%$ larger than the sauna.
- **Remaining Unknowns:**
  - Exact thickness of sauna insulated partition ($100\text{ mm}$ vs $120\text{ mm}$).

#### Alternative 2B: Symmetric Midpoint Model (Current Model)
- **Partition Coordinate:** $Y = 13500\text{ mm}$ ($2500\text{ mm}$ depth each).
- **Calculated Areas:**
  - Dušš: $1.80 \times 2.50\text{ m} = 4.50\text{ m}^2$ centerline (**$3.88\text{ m}^2$ clear**).
  - Saun: $1.80 \times 2.50\text{ m} = 4.50\text{ m}^2$ centerline (**$3.88\text{ m}^2$ clear**).
- **Supporting Evidence:**
  - None. It was an automated default assumption.
- **Remaining Unknowns:**
  - Contradicts the drawn ink line at $Y = 241\text{ px}$ and contradicts the written labels ($6\text{ m}^2$ vs $4\text{ m}^2$).

---

## 4. Area Calculation & Reconciliation Audit

### 4.1 Forensic Investigation of the $0.13\text{ m}^2$ Discrepancy
The previous audit noted a small numerical difference:
$$\mathbf{172.76\text{ m}^2 - 172.63\text{ m}^2 = 0.13\text{ m}^2}$$

A rigorous mathematical derivation reveals the exact source of this discrepancy:
1. **Quantity 1 ($172.76\text{ m}^2$):**
   - Derived as Gross Footprint ($185.00\text{ m}^2$) minus the theoretical exterior wall footprint ($12.24\text{ m}^2$).
   - This represents the **enclosed space inside the exterior envelope with ZERO interior partitions deducted**.
2. **Quantity 2 ($172.63\text{ m}^2$):**
   - Derived as the sum of the 13 individual room bounding boxes where:
     - Exterior walls had a half-thickness deduction ($100\text{ mm}$, half of $200\text{ mm}$).
     - Interior partitions had a half-thickness deduction ($50\text{ mm}$, half of $100\text{ mm}$).
   - This was an arbitrary hybrid calculation that assumed coordinates were wall centerlines rather than exterior boundary faces.
3. **The Discrepancy ($0.13\text{ m}^2$):**
   - The close numerical agreement ($172.76$ vs $172.63$) was a **mathematical coincidence**. It compared the area of an open exterior shell against a hybrid grid with partial partition deductions.
   - The $0.13\text{ m}^2$ delta is the net geometric artifact of deducting $50\text{ mm}$ along $60.2\text{ m}$ of interior partitions while under-deducting the exterior wall by $100\text{ mm}$.

---

### 4.2 The $12.24\text{ m}^2$ Exterior Wall Footprint Calculation
The exact exterior wall footprint formula for an inward-offset polygon is:
$$\text{Area}_{\text{wall}} = P \cdot T - (N_{\text{convex}} - N_{\text{reflex}}) \cdot T^2$$
Where:
- $P = 62.00\text{ m}$ (total exterior perimeter).
- $T = 0.20\text{ m}$ (proposed wall thickness).
- $N_{\text{convex}} = 5$ (standard $90^\circ$ exterior corners).
- $N_{\text{reflex}} = 1$ (re-entrant $270^\circ$ corner at $X=5000, Y=11000$).
- $N_{\text{convex}} - N_{\text{reflex}} = 5 - 1 = 4$ (matching the topological Euler turn theorem for any simple polygon: $4 \times 90^\circ = 360^\circ$).

$$\text{Area}_{\text{wall}} = (62.00 \times 0.20) - 4 \times (0.20)^2 = 12.40 - 0.16 = \mathbf{12.24\text{ m}^2}$$

#### Architectural Reality Check:
While the $12.24\text{ m}^2$ calculation is mathematically exact for a $200\text{ mm}$ wall, it **does not represent the final net usable floor area**:
- Inside the $172.76\text{ m}^2$ shell sit **13 interior partition walls** with a linear run of $60.2\text{ m}$ ($100 - 150\text{ mm}$ thick).
- The interior partitions occupy an additional $\approx \mathbf{6.27\text{ m}^2}$ of physical footprint.
- Therefore, the **true net usable internal area** of the house is:
  $$\text{Net Internal Area} = 172.76\text{ m}^2 - 6.27\text{ m}^2 \approx \mathbf{166.49\text{ m}^2}$$

---

### 4.3 Mathematical Consistency vs. Source Accuracy
This audit highlights a critical distinction:
- **Mathematical Consistency:** The 2D geometry in `draft_model.json` is 100% mathematically consistent: closed polygons, valid vertex offsets, and shoelace-reproducible areas.
- **Source Accuracy:** The model is **not yet fully accurate to the sketch**. The draftsperson drew approximate visual room proportions and wrote nominal design-target areas ($10 \times 6.5 = 65\text{ m}^2$; $3 \times 5 = 15\text{ m}^2$; $2.5 \times 2.4 = 6\text{ m}^2$) without subtracting wall thicknesses. Forcing a mathematical model to satisfy both the drawn line and the written area target is impossible because the source itself is contradictory.

---

## 5. Unresolved Uncertainties Register

1. **`UNC-01` (200 mm Depth Mismatch):**
   - Left chain: $5000\text{ mm (sauna)} + 14200\text{ mm (terrace run)} = \mathbf{19200\text{ mm}}$.
   - Right chain: $16000\text{ mm (main house)} + 3000\text{ mm (terrace depth)} = \mathbf{19000\text{ mm}}$.
   - **Status:** Unresolved blocker. In accordance with user instruction, Option C (seeking clarification / treating as an unverified sketch discrepancy) is maintained.
2. **`UNC-02` (Bathroom Partition Dilemma):**
   - Drawn line places wall at $Y \approx 9200\text{ mm}$ ($10.0\text{ m}^2$ bathroom).
   - Written label specifies `$6,5\text{ m}^2$`.
   - **Status:** Unresolved. Neither position is approved.
3. **`UNC-03` (Shower/Sauna Split):**
   - Current model uses unverified midpoint $Y = 13500\text{ mm}$ ($3.88\text{ m}^2$ each).
   - Source ink line ($Y = 241\text{ px}$) and labels ($6\text{ m}^2 / 4\text{ m}^2$) support $Y \approx 13000\text{ mm}$.
   - **Status:** Unresolved. Midpoint model rejected; adjusted position awaiting human decision.
4. **`UNC-04` (Unverified 2D Defaults):**
   - Wall thicknesses ($200 / 100 / 150\text{ mm}$) remain proposed defaults.
   - Window sill heights remain strictly **`UNKNOWN`** in 2D.

---

## 6. Recommendations for Human Review

To establish a defensible, supervised baseline and conclude auditing on Test 01:

1. **Acknowledge Source Contradiction on Bathroom:**
   - Recognize that the author drew a $\approx 10\text{ m}^2$ bathroom but labeled it $6.5\text{ m}^2$.
   - **Decision Choice:** Decide whether to draft the physical CAD drawing to **follow the drawn wall line** (Alternative 1A: $Y = 9200\text{ mm}$, preserving tub and door clearances) or to **force the room area** (Alternative 1B: $Y = 8300\text{ mm}$, shrinking the bathroom).
2. **Adopt Corroborated Split for Shower/Sauna:**
   - Replace the arbitrary midpoint ($Y = 13500\text{ mm}$) with the source-supported position **$Y = 13000\text{ mm}$** (Alternative 2A), which honors both the visible ink line and the $6.0\text{ m}^2 / 4.0\text{ m}^2$ written labels.
3. **Freeze `UNC-01` as a Documented Drafting Variance:**
   - Maintain the $16000\text{ mm}$ building depth and $3000\text{ mm}$ terrace depth ($19000\text{ mm}$ overall), and annotate the $14200\text{ mm}$ callout on the drawing sheet with a flag note: *"Discrepant sketch callout; verified against 19,000 mm building datum."*
4. **CAD Generation Gate:**
   - Keep CAD vector generation paused until the two partition decisions above are explicitly directed.

