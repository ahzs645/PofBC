# Revision 3 — upper beam and diagonal reserve

## Deliverable and integration

`upper_reserves.py` writes `upper_reserves.svg` beside itself using only Python's
standard library. It contains exactly these two independently editable paths:

- `upper-beam-reserve`
- `diagonal-brace-reserve`

Copy their `d` attributes into the corresponding master paths, or update the
master reserve dictionary with `upper_reserves.RESERVES`. They use ordinary
nonzero fill. The paper colour remains a generator argument. Neither the V2
source nor the final poster master was edited by this task. The temporary QA
masters retain all three other V2 reserve components unchanged.

## What changed

The beam's upper silhouette now follows the individual shoulders and valleys
visible in the photograph. The transitions into the deep dip beside the brace,
the shallow central ridges, and the irregular upper-right rim are authored
curves instead of long straight links. The lower beam edge has the source's
small pocket beside the upper knot and the low shoulder where it joins the
diagonal. A detached white brush mark to the left of the horizontal match head
is included as a second subpath of the beam.

The triangular painted opening has its two concave white recesses and short
paint fingers reconstructed with curved edges. The diagonal's lower border
has the photographed shoulder near y=215, the narrow raised paint fingers near
y=250–270, and the changing contour around y=330–390. The widths were reviewed
again against the photograph after the first diagnostic exposed a placement
bias. The final changes therefore concern both silhouette and local width.

These are hand-authored shapes selected from enlarged photographic crops. No
threshold boundary, auto-trace, pixel contour, random displacement, or bitmap
appears in the final vector. The masks serve only as a separate check.

## Fixed-mask measurements

The target is the existing, unchanged
`work/revision2/reference-reserve-mask-root.png`. Both candidates are rendered
at 1000 × 1400 on the original photograph registration. IoU is shared area
divided by combined area. Edge distances pool the nearest-boundary distances
in both directions, in normalized pixels. They are not authenticity scores.

| Region | V2 IoU | V3 IoU | V2 mean edge distance | V3 mean edge distance | V2 p95 | V3 p95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Upper beam and brace | 95.91% | 95.95% | 1.50 | 1.62 | 4.00 | 4.00 |
| Top beam | 96.56% | 96.41% | 1.40 | 1.85 | 3.61 | 3.61 |
| Triangle opening | 91.54% | 92.04% | 2.24 | 1.93 | 7.10 | 5.83 |
| Diagonal lower edge | 93.00% | 93.59% | 2.19 | 1.83 | 7.00 | 5.66 |

The whole-region area change is deliberately modest: a broad overlap score
was already high while the angular shape remained visibly unlike the source.
The triangle and lower diagonal boundaries improve in both area overlap and
edge distance. The top-beam raw metric is slightly worse. The existing target
mask omits the detached brush mark now present in the vector, and its connected
component classification does not describe every pale mark in the photograph.
The comparison mask was not changed to improve the score.

## Review images

`upper-analysis/beam-photo-v2-v3.png`,
`upper-analysis/triangle-photo-v2-v3.png`, and
`upper-analysis/diagonal-photo-v2-v3.png` show the same crops at the same scale.
Their corresponding `*-overlay-v2-v3.png` images use teal for white missing
from the vector and magenta for white beyond the fixed source mask.
`upper-analysis/upper-reserve-metrics.json` contains full numeric results and
the exact crop bounds. `upper_reserves_qa.py` reproduces this workspace QA.

## Remaining limits

The source edge includes print porosity, translucent yellow fragments and
photographic blur. A solid white reserve cannot itself reproduce every pale
paint fleck inside the triangular opening. Those are a separate paint/overprint
detail; they were not replaced by conspicuous holes exposing the red paint
underneath. The opposite edge of that opening belongs to the upright reserve
and is not changed here. The same estimated 5:7 normalized artboard is used;
this work does not establish original print dimensions or calibrated colour.
