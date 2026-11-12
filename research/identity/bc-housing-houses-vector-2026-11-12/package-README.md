# BC Housing reconstruction - revision 2

## What was wrong with the first delivery

The first delivery was checked with a visual overlay, but that check was accepted
too readily. Broad placement agreed while important local shapes did not. The
reconstruction made the rear windows too rectangular, enlarged several apertures,
altered the three figures, narrowed the left doorway's white corridor, and put
the ground under the facade too low. Roof and wall widths were inconsistent with
the reference. The custom lettering also had systematic counter and stroke errors.

## What was changed

- Rebuilt rear window frames as compound shapes with individual curved apertures.
- Rebuilt the small fanlight openings and their irregular outer shapes.
- Adjusted roof width and the apartment wall's lean; softened selected joins.
- Rebuilt door arches, their internal spaces and the small glass panes.
- Raised the ground under the facade without moving the lower landscape outline.
- Restored the tall figure's wider torso, moved the left figure's lower body, and
  corrected the small right figure's leg and arm. Rounded the small leg opening.
- Rebuilt the front corner-shaped window marks with varying widths.
- Corrected all nine letters, including B counters, C and o curves, H serifs,
  u's lower turn, s's waist, i's stem and dot, n's shoulder and both bowls of g.

These changes use deliberate cubic and quadratic curves. No automatic bitmap
outline tracing was used and no raster image is embedded in the vector files.

## What the overlap analysis measures

The reference and both vectors use the original 1569 x 1038 coordinate system.
No additional rescaling, warping or registration is applied. For diagnostics,
the reference is converted to grayscale, smoothed by 0.7 source pixel and
thresholded at 150/255. Vectors are rendered at the same size and thresholded at
128/255. Sensitivity results at source thresholds 135 and 165 are also retained.

The difference image uses red for reference-only material, blue for vector-only
material, and pale grey for agreement. Pale grey deliberately prevents the large
common black areas from dominating the display.

Intersection over union (IoU) is common black area divided by total black area
in either image. It is a diagnostic of shape agreement, not a percentage of
visual fidelity or historical accuracy. The scan's blur and ink texture make
some edge positions uncertain. White background pixels do not inflate this score.
The boundary distance is the mean of nearest-edge distances in both directions,
in original screenshot pixels. Crops are documented in the JSON file.

| Region | First version IoU | Revised IoU | Mean boundary distance, px |
| --- | ---: | ---: | ---: |
| Illustration | 0.842 | 0.893 | 1.53 -> 1.08 |
| Rear Windows | 0.680 | 0.815 | 1.53 -> 1.04 |
| Fanlights | 0.726 | 0.869 | 1.35 -> 0.71 |
| Doors | 0.796 | 0.877 | 1.70 -> 0.99 |
| People | 0.886 | 0.923 | 1.01 -> 0.69 |
| Wordmark | 0.838 | 0.915 | 0.93 -> 0.50 |

## Remaining limits

This is still an independent reconstruction from a screenshot, not a recovered
official master. Some joins and pane edges remain smoother than the printed
source. Solid black artwork reads more strongly than the reference's halftone
reproduction. Small residual curve differences remain, especially in the serif
lettering; the exact historical typeface remains unverified. The revision should
be assessed using the supplied reference comparison and local difference maps.

## Files

- BC_Housing_Rebuilt.svg: complete editable black vector, transparent background.
- BC_Housing_Symbol.svg: illustration without lettering.
- BC_Housing_White.svg: white vector for dark backgrounds.
- BC_Housing_Vector.pdf: vector PDF with no embedded image or font.
- BC_Housing_Transparent.png: 3200 px wide transparent convenience image.
- BC_Housing_Preview.png: white-background visual preview.
- BC_Housing_Source_Comparison.png: reference / first delivery / revision.
- BC_Housing_Overlap_Analysis.png: explicit missing/added-shape maps.
- BC_Housing_Detail_Review.png: close-up comparisons.
- BC_Housing_Overlap_Measurements.json: measurements, regions and method.
- source/: editable original-coordinate artwork and authored path data.

All text in the logo is outlined. The SVGs have no font requirement. All paths
and negative spaces are vector geometry. The white version is a recolouring of
the same geometry. Scale the complete artwork together.
