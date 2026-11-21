# Upright white reserve — Revision 3

## Construction and integration

`upright_reserve.py` contains the manually authored contour as `UPRIGHT_PATH` (also `PATH` and `RESERVES["right-upright-reserve"]`). Running it writes the isolated, transparent 1000 × 1400 component `upright_reserve.svg`. It retains the existing path ID and fill **#e7f3f2**. It has no image input, raster content, filters, tracing operation, random perturbation or dependency on the review mask.

Replace only the existing `right-upright-reserve` path with this contour. Do not use `upright-v3-composite.svg` as the merged final: that review composite deliberately retains the other four Revision 2 contours, so it isolates this change.

## Source-specific shape changes

- The top narrowing now follows a continuous taper with small local shifts in width. The left paint recess at y185–210 and its lower return around y280–330 have distinct shapes.
- The right edge has smaller, controlled shoulders around y310–370, followed by the widening into the diagonal match-head reserve. The four other reserve contours remain V2 in these comparison images, so their overlap still determines parts of the diagonal head and opening.
- At y595–640, the left shoulder has an asymmetric shallow step and a second lower recess, with small lobes around its margins. The previous single polygonal bend no longer determines the full shoulder.
- Beside the middle match head, the y690–730 taper has several small source-informed lobes and indentations. This preserves the longer tongue-shaped paint intrusion instead of a large angular notch.
- The y855–865 right cut-in has a narrow tip and short rounded lip. Below it, the side width varies gently instead of joining a few straight segments.
- The y1008–1110 left return has a shorter upper shelf, a recessed middle section, a broader lower lobe and smaller local scallops. The lower return is no longer a large pointed wedge.
- The bottom shelf near the seal has a flatter upper reach and a rounded, nearly level lower foot. Its hidden continuation behind the seal remains an overlap, not a claim about the source.

The photo was inspected in enlarged crops with coordinate grids. Sparse cross-section measurements helped check landmark placement. Curves were specified directly in the source; no boundary extraction or photo-to-path conversion supplied their geometry. The final small width correction was a deliberate 0.65-pixel adjustment of the lower right edge, followed by a slight underside-shelf correction.

## Fixed-mask checks

This evaluation uses the **unchanged Revision 2 reference mask**, the same 1000 × 1400 registration, the same upright region [750, 165, 890, 1245], and the same expanded oval-seal exclusion. The other four V2 reserve contours stay fixed. The computations use `analyze_edges.measures` so the boundary-tolerance definitions match the root analysis.

| Measure | V2 | V3 upright only |
| --- | ---: | ---: |
| Reserve mask IoU | 0.9678 | 0.9761 |
| Mean symmetric edge distance | 1.32 px | 0.98 px |
| 95th-percentile edge distance | 4.12 px | 3.16 px |
| Boundary F1 within 1 px | 68.3% | 80.1% |
| Boundary F1 within 2 px | 84.0% | 90.6% |
| Boundary F1 within 3 px | 91.6% | 94.5% |
| Excess white pixels | 2,194 | 1,137 |
| Missing white pixels | 850 | 1,091 |

Boundary F1 combines the fraction of the vector boundary close to the photo boundary and the converse. The improved close-tolerance result is more relevant to the remaining local edge problem than the high area IoU alone. These remain measurements of the fitted photographic mask, not historical authenticity. Other contour revisions can change the final union results.

## Review files and limits

`upright-upper-comparison.png`, `upright-middle-comparison.png` and `upright-lower-comparison.png` show the photograph, V2 and this isolated V3 change at 3×. The matching `upright-overlay-top.png`, `upright-overlay-middle.png` and `upright-overlay-bottom.png` show teal for missing white and magenta for excess white. `upright_metrics.json` includes smaller regional diagnostics. `review_upright.py` reproduces these checks and images without modifying the master output.

The reconstructed border is still a vector interpretation of a blurred and worn printed edge. The small faded yellow islands inside the pale reserve and fine translucent grain have not been recreated as holes: cutting them out would expose the much stronger paint below and misrepresent their low contrast. A few local slivers remain in the fixed-mask overlay, especially around paint residue beside the middle match head and at overlap with the diagonal reserve. Physical dimensions and calibrated original ink colour remain unverified.
