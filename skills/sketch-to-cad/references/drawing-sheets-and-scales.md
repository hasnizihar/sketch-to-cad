# Drawing Sheets, Standard Scales & Title Block Standards

## 1. Overview
The Sheet Generation Engine (`scripts/sheet_generator.py`) generates professional, publication-quality printable drawing sheets in standard ISO paper formats (A4 through A1) with vector PDF rendering, strict scale enforcement, ANSI/ISO title blocks, and conditional North Arrow validation.

---

## 2. Standard ISO Paper Formats & Margins

Standard sheet dimensions in millimeters (width $\times$ height):

| Format | Landscape (mm) | Portrait (mm) | Standard Border Margin (mm) | Typical Architectural Use |
|:---:|:---:|:---:|:---:|:---|
| **A4** | $297 \times 210$ | $210 \times 297$ | $10\text{ mm}$ (left $20\text{ mm}$) | Single room cabins, reports, details |
| **A3** | $420 \times 297$ | $297 \times 420$ | $15\text{ mm}$ (left $20\text{ mm}$) | Standard residential single-storey |
| **A2** | $594 \times 420$ | $420 \times 594$ | $15\text{ mm}$ (left $25\text{ mm}$) | Multi-room villas, two-storey residences |
| **A1** | $841 \times 594$ | $594 \times 841$ | $20\text{ mm}$ (left $30\text{ mm}$) | Large estates, multi-unit residential |

---

## 3. Standard Architectural Scales & Viewport Fitting Mathematics

Supported architectural scales:
- **1:50** ($1\text{ mm} = 50\text{ mm}$ model): Detailed residential floor plans, small cabins.
- **1:100** ($1\text{ mm} = 100\text{ mm}$ model): Industry standard residential plan scale.
- **1:200** ($1\text{ mm} = 200\text{ mm}$ model): Large footprint residences and site coordination.

### Strict Scale Enforcement (`ScaleOverflowError`)
CAD drawings must never be silently squeezed or scaled to fit a sheet, as this corrupts physical scale measurements taken with an architectural scale ruler.

The engine calculates printable viewport bounds:
$$\text{Width}_{\text{avail}} = \text{PaperWidth} - \text{MarginLeft} - \text{MarginRight} - \text{TitleBlockWidth}$$
$$\text{Height}_{\text{avail}} = \text{PaperHeight} - \text{MarginBottom} - \text{MarginTop}$$

The scaled model footprint is:
$$W_{\text{paper}} = \frac{W_{\text{model}} + 2 \times \text{DimMargin}}{\text{ScaleFactor}}$$
$$H_{\text{paper}} = \frac{H_{\text{model}} + 2 \times \text{DimMargin}}{\text{ScaleFactor}}$$

If $W_{\text{paper}} > \text{Width}_{\text{avail}}$ or $H_{\text{paper}} > \text{Height}_{\text{avail}}$, the engine raises `ScaleOverflowError`:
```
ScaleOverflowError: Plan dimensions (14000 x 12000 mm) at 1:50 require 310 x 270 mm,
exceeding A4 viewport (227 x 190 mm). Recommended standard scale: 1:100 on A3.
```
Silent downscaling is strictly prohibited.

---

## 4. Title Block Standards (ANSI / ISO / AIA)

Every generated sheet features a standardized title block located in the lower-right quadrant:
- **Project Name & Address**: Clear identification of building project.
- **Sheet Title**: Floor identification (e.g. `GROUND FLOOR PLAN`).
- **Sheet Number**: AIA numbering convention (e.g. `A-101`, `A-102`).
- **Floor Identification**: `LEVEL-01`, `LEVEL-02`, or `ROOF`.
- **Nominal Scale**: Declared scale and paper format (e.g. `1:100 @ A3`).
- **Release Status**: `FOR APPROVAL`, `APPROVED`, or `PRELIMINARY`.
- **Revision History Block**: Date, rev number, change description, and reviewer initials.
- **Architectural Legend**: Line type conventions, wall hatches, and symbol keys.

---

## 5. Conditional North Arrow Policy

Residential architectural drawings require orientation indicators. However, an unverified North orientation must never be invented:
1. **Verified Orientation**: When the sketch observations contain verified solar or orientation notes (e.g. `North = 0°` or `North = 45°`), a styled vector North Arrow compass rose is rendered with true bearing.
2. **Unverified / Missing Orientation**: If orientation is not explicitly observed, the North Arrow is omitted from the sheet title block, and an informational note is recorded in the title block notes: `NORTH ORIENTATION NOT VERIFIED ON SOURCE SKETCH`.
