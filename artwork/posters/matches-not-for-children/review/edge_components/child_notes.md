# Revision 3 — thread and child white reserves

## What changed

The two contours in `child_reserves.py` replace `suspension-thread-reserve` and `child-figure-reserve` directly. `child_reserves.svg` contains only those two paths on the existing 1000 × 1400 coordinate system. The child path also includes two small, separately closed paper flecks visible to the right of the torso in the photograph.

The suspended thread now has a rounded, asymmetric side notch, more faithful changes in width, and smaller local paint-edge inflections. The head and neck boundary has been narrowed in the places where V2 overhung the photograph, with a small source-visible protrusion on the left and a continuous concave shoulder transition.

The child’s arms, torso, and legs received the larger redraw. The broad straight facets under the arms, along the torso taper, and around the leg junction have been replaced with controlled curves. The stair steps above the right leg and the polygonal indentation between the legs are now individually shaped paint lobes and notches. The left leg’s outer edge and the right match head’s white border were trimmed after reviewing the overlay; this removes much of V2’s oversized white margin.

These are manually specified cubic and quadratic Bezier segments. No source contour was converted wholesale into SVG, and no random jitter was applied. Sparse photographic landmarks and cross-sections informed the drawing; raster masks are diagnostics only.

## Fixed comparison

The comparison uses the unchanged V2 photographic target, unchanged 1000 × 1400 registration, the same alpha threshold and exclusion domain, and the evaluator from `work/revision2/analyze_revision.py`. The other three reserve paths remain at V2 in this isolated assessment. Parent integration may change measurements in overlapping regions, particularly the upper knot crop.

| Region | V2 IoU | V3 IoU | V2 mean edge distance | V3 mean edge distance |
|---|---:|---:|---:|---:|
| Thread and upper knot | 95.57% | 96.05% | 1.157 px | 1.024 px |
| Child head and neck | 96.70% | 97.42% | 0.932 px | 0.740 px |
| Child arms, body and legs | 94.92% | 96.91% | 1.292 px | 0.836 px |

Full values and area error counts are in `child_metrics.json`. In the arms/body/legs crop, excess white falls from 1,715 to 589 pixels; missing white increases from 372 to 647 pixels. That tradeoff is visible as a more balanced, thinner residual boundary, rather than a consistently oversized halo. The 95th-percentile edge error drops from 3.606 to 2.236 normalized pixels in that crop.

## Review files and limits

`child-comparison.png` and the four `*_detail-comparison.png` boards show photograph, actual V2 artwork, and revised artwork under the same crop and scale. The preview preserves the V2 paint and black illustration so the white contour change is directly reviewable. `child-overlay-comparison.png` displays V2 and V3 against the same target: teal marks missing reserve and magenta marks excess reserve.

The remaining errors mostly follow faint brush residue, soft photographic boundaries, and tiny local paint intrusions. The deliberately limited vector detail remains crisper than the photographed print. This revision addresses the reserve contour geometry; it does not authenticate the print dimensions, establish calibrated original paper colour, or resolve the faint signature attribution.
