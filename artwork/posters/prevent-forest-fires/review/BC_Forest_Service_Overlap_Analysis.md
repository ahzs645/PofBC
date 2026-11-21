# Tree overlap analysis — revision 5 to revision 6

The upper conifers and lower burnt woodland were compared with the supplied photograph using a fixed registration. The differences then guided changes to manually authored tree, log, bark, and root shapes. The image masks did not generate artwork contours.

## Primary result: raw dark-ink overlap

| Region | Before (revision 5) | Revised (revision 6) | Change |
|---|---:|---:|---:|
| Upper trees | 74.0% | 76.1% | +2.0 pp |
| Lower woodland | 78.7% | 80.6% | +1.9 pp |
| Lower trunks and logs | 70.7% | 73.0% | +2.3 pp |
| Roots and ground | 88.8% | 90.3% | +1.5 pp |

**Definition:** ink overlap is intersection-over-union (IoU): the dark-ink pixels shared by both images divided by all pixels dark in either image. Shared background does not count. A higher number indicates closer ink occupancy at this alignment; it is not a percentage of historical or artistic accuracy.

The lower trunks/logs and the dense roots/ground are reported separately. Otherwise the large dark ground field would conceal some of the remaining differences in the individual structures. The combined lower-woodland row includes both.

## How to read the overlays

- Dark gray: dark ink shared by the reference and vector.
- Cyan: dark ink in the reference that is missing from the vector.
- Magenta: extra dark ink in the vector.
- Light gray rectangle: the excluded FIRES lettering area.

`BC_Forest_Service_Tree_Overlap.png` shows the raw maps before and after. `BC_Forest_Service_Tree_Blend.png` shows 50/50 colour blends. `BC_Forest_Service_Overlap_Viewer.html` is a self-contained interactive viewer with upper/lower selection, before/revised selection, colour overlay opacity, raw difference maps, and lightly cleaned maps.

Colour overlays remain necessary: both yellow exposed wood and orange background are outside the dark-ink mask. A better ink overlap score alone cannot determine whether the material shape is correct.

## Ink coverage and excess

Reference ink covered (recall) asks how much source ink appears in the vector. Vector ink supported (precision) asks how much vector ink is also present in the source. Both are reported so that adding dark mass everywhere cannot look like an unqualified improvement.

| Region | Reference covered, before → revised | Vector supported, before → revised | Missing ink pixels, before → revised | Extra ink pixels, before → revised |
|---|---:|---:|---:|---:|
| Upper trees | 86.3% → 86.6% | 83.9% → 86.2% | 17,609 → 17,157 | 21,221 → 17,801 |
| Lower woodland | 88.0% → 90.0% | 88.2% → 88.5% | 16,206 → 13,412 | 15,913 → 15,765 |
| Lower trunks and logs | 83.4% → 85.9% | 82.3% → 83.0% | 11,923 → 10,113 | 12,821 → 12,644 |
| Roots and ground | 93.2% → 94.8% | 95.0% → 95.0% | 4,283 → 3,299 | 3,092 → 3,121 |

## Threshold sensitivity

The same RGB classifier is applied to the reference and each vector render. The primary threshold is 140, with 120 and 160 checked as sensitivity bounds. Requiring every RGB channel to be below the threshold avoids classifying the orange and yellow fields as dark ink. These are diagnostic thresholds, not estimated historical ink colours.

| Region | Threshold 120, before → revised | Threshold 140, before → revised | Threshold 160, before → revised |
|---|---:|---:|---:|
| Upper trees | 72.2% → 74.2% | 74.0% → 76.1% | 75.6% → 77.6% |
| Lower woodland | 77.3% → 79.1% | 78.7% → 80.6% | 79.8% → 81.8% |
| Lower trunks and logs | 68.9% → 71.0% | 70.7% → 73.0% | 72.3% → 74.7% |
| Roots and ground | 87.9% → 89.2% | 88.8% → 90.3% | 89.7% → 91.2% |

## Secondary check: light cleanup

An identical radius-one cross closing is applied to each binary mask, followed by filling only enclosed holes of nine pixels or fewer. This reduces some small print and bark interruptions. There is no opening that would erase thin twigs, and larger holes and background gaps remain. The result is still an ink mask with internal details, not a pure outer-silhouette measurement. The raw scores above remain the primary comparison.

| Region | Light-cleanup overlap, before | Light-cleanup overlap, revised | Change |
|---|---:|---:|---:|
| Upper trees | 76.8% | 79.1% | +2.3 pp |
| Lower woodland | 80.9% | 82.9% | +2.1 pp |
| Lower trunks and logs | 73.4% | 75.8% | +2.5 pp |
| Roots and ground | 90.5% | 92.1% | +1.6 pp |

## Secondary check: ink-edge distances

Edges are computed on the full images before applying the region masks, with a two-pixel guard inside crop and exclusion boundaries. Query and target edges both remain inside that guarded region. A matching edge outside the region is therefore unavailable, which can inflate distances near crop splits; the same restriction is used before and after. The mean distance equally weights the reference-to-vector and vector-to-reference directions. These are all dark-ink edges, including internal grain and print-wear edges; they should not be described as only the exterior tree contour. More mismatched fine details can change these distances even when the main shape improves.

| Region | Mean symmetric distance, before → revised | Edge F1 within 2 px, before → revised | Edge F1 within 4 px, before → revised |
|---|---:|---:|---:|
| Upper trees | 2.57 → 2.32 px | 55.7% → 59.7% | 80.4% → 84.4% |
| Lower woodland | 2.28 → 2.23 px | 64.9% → 66.9% | 85.3% → 85.7% |
| Lower trunks and logs | 2.11 → 2.08 px | 65.4% → 67.0% | 86.4% → 86.9% |
| Roots and ground | 2.84 → 2.76 px | 63.6% → 66.9% | 81.7% → 81.9% |

Directional 95th-percentile distances, exact pixel counts, and component hotspot bounds are included in the JSON files. The CSV includes raw and cleaned counts, scores, and edge metrics for every region.

## Fixed geometry and exclusions

- Reference canvas: 1000 × 1440 pixels.
- Photograph corner registration, clockwise from upper left: (248, 27), (1183, 29), (1207, 1423), (216, 1427).
- Upper trees: x=[0, 1000), y=[0, 425).
- Lower woodland: x=[0, 1000), y=[735, 1145).
- Excluded lower lettering rectangle: x=[125, 830), y=[735, 880).
- Lower trunks and logs: the lower region above y=1075.
- Roots and ground: x=[0, 1000), y=[1075, 1145).
- Both vector previews are 3000 × 4320 pixels and are reduced once with Lanczos resampling to the reference canvas.
- No independent alignment of individual trees, no local warping, and no score-optimizing crop changes.

The corners are visually selected from a photograph. Perspective rectification cannot remove paper curvature, all lens effects, lighting variation, blur, print wear, or JPEG compression. This limits how literally a few-pixel residual should be interpreted. The broad missing and extra ink regions are more reliable guides than isolated speckles.

## What this does and does not establish

The method provides a repeatable comparison of the visible dark printing in the supplied image. The final SVG remains constructed from editable vector objects. Fine needles, small torn edges, and individual engraved marks remain interpreted, and the work should not be represented as a pixel-identical archival facsimile.

## Reproduce the analysis

Python 3 with Pillow, NumPy, and SciPy is required for the analysis; the artwork generator itself uses the standard library. From the unpacked package root:

```bash
python3 source/analyze_tree_overlap.py --reference analysis/reference-rectified.png --candidate analysis/before_preview.png --label before --output-dir analysis
python3 source/analyze_tree_overlap.py --reference analysis/reference-rectified.png --candidate artwork/BC_Forest_Service_Preview.png --label after --output-dir analysis
```

The diagnostic PNGs and JSON metrics can be regenerated without the original image attachment. The fixed rectified reference is supplied in the analysis folder. It is never embedded in the artwork SVG or print PDF.

## Follow-up on the details left after revision 5

The local measurement areas below were fixed before revision 5 and remain unchanged for revision 6. They may overlap, so their counts cannot be added. Some contain adjacent branches or stumps; they are area diagnostics, not isolated-object scores. Lettering is excluded in the leaning-trunk area.

| Fixed local review area | Before | Revised | Change |
|---|---:|---:|---:|
| Left canopy and trunk tip | 77.5% | 78.5% | +0.9 percentage points |
| Second crown and hanging boughs | 75.8% | 76.7% | +0.9 percentage points |
| Central tree and its boughs | 73.7% | 77.4% | +3.8 percentage points |
| Right canopy and outer branches | 72.3% | 74.0% | +1.7 percentage points |
| Leaning trunk and root area | 75.9% | 79.6% | +3.7 percentage points |
| Fallen-log middle span | 71.4% | 74.9% | +3.5 percentage points |
| Rear branches and right-stump area | 71.0% | 71.0% | -0.0 percentage points |
| Right-hand ground openings | 91.9% | 91.8% | -0.1 percentage points |

`BC_Forest_Service_Remaining_Details.png` shows source shapes alongside revisions 5 and 6: left branch shoulders, staggered right boughs, the leaning trunk/root flare, main fallen log, ground junctions, right rear arch and tall broken snag. These qualitative view windows are selected to show the work and differ from the fixed measurement rectangles above.

The supplementary JSON records the exact fixed measurement rectangles, exclusions and pixel counts. These local diagnostics use the same raw dark-ink classifier as the primary analysis. A colour crop must still be checked to distinguish exposed pale-gold wood from orange background.

The local crops and metrics can be regenerated using `source/analyze_detail_areas.py` with `--reference`, `--candidate`, `--label` and `--output-dir`; use the same reference and candidate files as the primary reproduction commands, and set the output directory to `analysis/details`. Run once for label `before` and once for label `after`.

## Separate flame-line review

The five side ribbons are assessed with fixed local yellow masks, separately from the dark-ink tree regions. Full scope, exclusions, colour-threshold sensitivity, counts and reproduction commands are in `BC_Forest_Service_Flame_Overlap_Analysis.md`; `BC_Forest_Service_Flame_Details.png` provides matching colour crops.

| Flame area | Before | Revised |
|---|---:|---:|
| Left long vein, isolated lower shaft | 84.3% | 84.3% |
| Left middle arc | 80.1% | 80.1% |
| Left lower tongue | 81.6% | 81.6% |
| Right oblique cut | 78.9% | 78.9% |
| Right lower edge flick | 79.7% | 79.7% |
