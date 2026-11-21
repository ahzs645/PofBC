# Forest Service BC - refinement and overlap report

The artwork has been refined using the supplied image. This report compares the initial delivered reconstruction with the updated package.

## Consistent before / after measurements

| Region | Before | Refined | Change |
| --- | ---: | ---: | ---: |
| All 28 letters | 92.8% | 95.3% | +2.5 percentage points |
| Two outer border strokes | 82.5% | 93.2% | +10.6 percentage points |
| Central canopy silhouette | 88.7% | 95.7% | +7.0 percentage points |
| Central canopy dark details | 50.0% | 77.7% | +27.7 percentage points |
| Mountains, lake and foreground dark details | 40.6% | 68.0% | +27.4 percentage points |
| All dark marks in the emblem | 75.8% | 87.7% | +11.9 percentage points |

IoU is intersection divided by union: matching selected pixels divided by pixels occupied by either shape. Empty canvas area does not inflate it. These are shape-mask measurements, not a universal percentage of logo fidelity.

## What changed

- Rebuilt the weaker C, R, S, M, B and A letterforms using dimensioned typographic geometry.
- Recalibrated the oval arcs and replaced scaled nested outlines with consistent-width border strokes.
- Refined the designed tree whorls, hanging tips, internal green openings and dark cuts.
- Replaced generic small trees with individual irregular silhouettes and refined the mountain cliff columns and snow cuts.
- Redrew the foreground saplings, terrain loops, root fan and small ground marks; adjusted the lake ripples.

## Method

Both candidate images were rendered in the original 1709 x 2048 source coordinates. No additional alignment, stretching or warping was applied to their comparison renders. Dark marks use max(R,G,B)<115. The lower-scene region is the original oval mask eroded by 14 pixels and is held fixed between versions. The canopy silhouette uses G-R>12; the dark-detail region is one shared union of the source, previous and refined canopy silhouettes expanded by 3 pixels within the fixed canopy box. This same region is used for both versions. The previous vector is re-evaluated in that common region rather than reusing a score measured on a different region. The border comparison isolates the two exterior strokes. The lettering check matches the 28 isolated character components in the actual full-color renders.

The source filename and dimensions, pixel counts, region definitions and thresholds are recorded in Forest_Service_BC_Overlap_Measurements.json. Thresholds 100, 115 and 130 are retained as a sensitivity check.

## Reading the images

Dark green marks agreement, pink marks source-only pixels and cyan marks vector-only pixels. White in those diagnostic views means neither selected mask includes a pixel; it does not show the original fill color.

## Remaining differences

The raster reference contains soft edges and color texture that are represented here with crisp vector edges and flat fills. Small illustration details and some letter curves still differ. The exact historical font and official color specification have not been established from the supplied image.

Prepared 2026-11-20.
