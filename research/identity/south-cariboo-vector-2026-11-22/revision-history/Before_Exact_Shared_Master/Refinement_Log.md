# Tree reconstruction review — second round

Selected: **round2-candidate07**, 22 November 2026. Comparison baseline: the previously delivered **pass07**.

## Why work resumed

The user's criticism was correct. Pass07's broad rounded shelves, smooth cups and lower-tree gaps did not capture the source's directional brush forms. The previous stopping judgment was premature. This round treated those as drawing errors and rebuilt the affected shapes.

## Revision sequence

| Candidate | Decision | Dark overlap | Pale-window overlap | Dark lower overlap |
| --- | --- | ---: | ---: | ---: |
| candidate01 | Rebuild clipped branch strokes; first draft over-angular and missing crown connectivity. | 79.33% | 90.82% | 75.95% |
| candidate02 | Restore crown connection and east bough; reject excessive regular stepping. | 81.81% | 91.00% | 75.95% |
| candidate03 | Recover flowing left sweeps, spine and thin right tips; remove unsupported lumps. | 85.35% | 91.03% | 77.20% |
| candidate04 | Integrate shared pale structure, upper channels and lower construction; remove false detached marks. | 87.53% | 93.47% | 81.02% |
| candidate05 | Rebuild the pale right canopy and visible brush windows. | 87.53% | 93.44% | 81.02% |
| candidate06 | Restore hook tongue, inner lobe return, base ink bridge and stem crossing; correct basal flecks. | 89.34% | 94.37% | 87.32% |
| candidate07 | Finish only five small openings with uneven curved shoulders; preserve the rebuilt structure. | 89.19% | 94.43% | 87.23% |

The numbered candidates record combined drafts; several local reviews and rejected trials occurred between them. The table is a progression record, not an instruction to maximize a pixel score.

## Structural decisions

- Replaced broad rounded shelves with directional curved sweeps, clipped shoulders and irregular thin ends. Early drafts were too angular, so curvature was restored where the source supports it.
- Used the repeated left branches and internal voids to construct a shared authored master. Eleven visually selected feature pairs fit an approximately 0.83 scale plus translation. Their 0.279-source-pixel RMS residual is below the roughly 0.5–1 px selection uncertainty; matrix decimals are computational precision, not proof of historical subpixel accuracy.
- Kept the pale right canopy as an instance-specific completion. Several dark right openings are absent in the pale source and were deliberately excluded.
- Removed unsupported detached specks and lumps. Preserved only marks with coherent source evidence; a small pale basal fleck is an explicit colour/coverage interpretation.
- Restored the lower hook's inner tongue and the return beneath the y100 lobe. Tapered the diagonal base cuts while retaining the ink bridge between them.
- Replaced the false long vertical root gap with a short enclosed upper slit and a separate bottom exit, retaining the source's crossing near y137. Added the missing connected base edge.
- Gave five tiny interior openings asymmetric curved shoulders. The outer tree contours remain deliberately irregular.
- Kept the four-line lettering and original authored alignment. No extra whole-tree overlay warping was introduced.

## Before and after

| Window | Previous pass07 overlap | Current overlap | Mean boundary distance |
| --- | ---: | ---: | ---: |
| All | 88.66% | 91.51% | 0.418 → 0.322 px |
| Dark | 82.93% | 89.19% | 0.689 → 0.443 px |
| Pale | 90.93% | 94.43% | 0.696 → 0.463 px |
| Type | 89.53% | 89.53% | 0.211 → 0.211 px |
| Dark crown | 85.48% | 90.81% | 0.740 → 0.432 px |
| Dark middle | 84.75% | 89.29% | 0.696 → 0.505 px |
| Dark lower | 77.47% | 87.23% | 0.671 → 0.397 px |

Continuous density error decreased by 36.9% overall and 47.3% in the dark-tree window. These figures are secondary checks on the visual changes.

## Measurement method

Both images are compared on the source's 315 × 141 grid. Inkscape renders the SVG at 1890 × 846; Lanczos reduces that render to the source grid. The original authored alignment is retained, with no additional registration of the overlay.

Ink density is clip(dot(255−RGB,[190,133,197])/dot([190,133,197],[190,133,197]),0,1). Whole/pale masks use density ≥ 0.25; dark/type masks use density ≥ 0.75. The dark window is x < 74. Crown is y < 50; middle 50 ≤ y < 101; lower y ≥ 101. The lettering window is x ≥ 140. The pale window is x < 105 and x > (70 if y < 92 else 52); it is a visible spatial window, not perfect object segmentation, and includes a few dark detached marks.

Foreground overlap (IoU) is intersection divided by union of the two thresholded masks. Boundary distance is the symmetric nearest-neighbour distance between 4-neighbour erosion boundaries, calculated on the full masks before window clipping. Continuous density error uses mean squared density difference without a threshold. The red/cyan overlay has RGB = 255 × [1−vector_density,1−source_density,1−source_density]: red means more source ink, cyan more vector ink, and neutral areas have similar density.

These diagnostics measure agreement with a small raster reference. They do not prove historical authenticity, and a higher score alone is not sufficient reason to prefer a drawing.

## Selection and remaining interpretation

The selected revision was inspected at original size and enlarged scale, using source/vector comparisons and continuous overlays. The branch direction, missing lower stroke and root connections were resolved before selection. The final pass addressed local mechanical-looking corners without introducing extra texture or islands merely to fit pixels.

The low-resolution source cannot uniquely specify every fine brush tip or concealed pale branch. The current SVG is an authored reconstruction, not an authentic recovered master. Further improvements should be driven by a coherent visible shape difference or stronger evidence; remaining differences should not automatically be dismissed as raster artifacts.
