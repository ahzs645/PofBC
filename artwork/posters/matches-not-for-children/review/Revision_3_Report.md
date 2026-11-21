# BC Forest Service poster — Revision 3

## Result and scope

Revision 3 continues the white-edge work after the enlarged V2 edges still looked unfinished. The change is confined to the pale illustration reserve. The painted background, black matchstick drawing and ties, headline, seal, signature and other lettering retain their Revision 2 construction.

A sparse group of manually drawn pale amber residue marks is also included inside the reserve, clipped to its geometry and placed beneath the black illustration. These marks describe the clearly visible deposits studied near the child’s right leg and the upright foot. They do not change the reserve-mask geometry or its boundary scores.

On the same fixed photograph mask, mean white-boundary distance is **1.23 px**, compared with **1.41 px** in V2. Boundary F1 within two normalized pixels is **87.9%**, compared with **82.7%**. Reserve-area IoU is **96.63%**, compared with **95.86%**. These values describe fit to the registered photograph; none is a historical-authenticity or whole-poster fidelity score.

## Why the earlier area score was insufficient

V2 already achieved 95.9% white-reserve IoU. A broad white shape can overlap most of the photographed reserve while retaining visible polygonal corners, stiff side runs or oversized local notches. Those defects occupy little area, so a high area score can coexist with an unfinished appearance when enlarged.

This pass therefore used close photo/vector comparisons to reconstruct recognizable local shapes, then checked both boundary position and area overlap. It did not apply a blanket smoothing operation to the old contours. The new boundaries include specific lobes, recesses, narrow returns and changes in width where the photograph supports them.

## What changed in the contours

| Region | Revision 3 work |
| --- | --- |
| Upper beam and triangular opening | More specific top-edge lobes, shallow recesses and lower paint cut-ins. The edge inside the triangular opening has a less faceted profile. |
| Diagonal brace | Local shoulders and broken paint-edge shapes replace long stepped transitions. A small number of source-visible flecks are constructed separately within the path geometry. |
| Thread and child | The thread column has subtler local width changes. The head, shoulders, arms, crotch, legs and foot reserve include deliberate small recesses and rounded brush ends. |
| Upright | Asymmetric shoulder steps, the broken taper beside the middle head, the narrow right-hand notch, the lower left return and the near-horizontal bottom shelf are reconstructed individually. |

The construction uses manually specified Bézier geometry, plus a few deliberately placed source-supported flecks. Photograph masks are used for separate review; their contours do not generate the vector artwork. The compiled `source/reserves_v3.py` contains the complete current reserve and reads no photograph or diagnostic mask.

## Common-reference measurements

Both V2 and V3 are evaluated on the **same 1000 × 1400 reference plane**, with the same estimated perspective transformation, fixed photographic mask and seal exclusion. The metrics below come from `review/White_Edge_Measurements.json` in this package.

### Area and boundary distance

| Region | V2 IoU | V3 IoU | V2 mean edge distance | V3 mean edge distance |
| --- | ---: | ---: | ---: | ---: |
| All visible illustration reserve | 95.86% | 96.63% | 1.41 px | 1.23 px |
| Hanging thread and upper knot | 95.57% | 96.26% | 1.16 px | 0.98 px |
| Child head and neck | 96.70% | 97.42% | 0.93 px | 0.74 px |
| Child arms, body and legs | 94.92% | 96.91% | 1.29 px | 0.84 px |
| Upper beam and diagonal brace | 95.91% | 96.13% | 1.50 px | 1.55 px |
| Upright support | 96.78% | 97.51% | 1.32 px | 1.02 px |

The full-reserve 95th-percentile boundary distance is 3.16 px in V3 and 4.00 px in V2. Excess white area is 5,206 pixels versus 7,338; missing white area is 2,525 pixels versus 2,244. Region boxes overlap, so regional pixel counts must not be summed.

### Boundary agreement at close tolerances

| Region | V2 F1 within 1 px | V3 F1 within 1 px | V2 F1 within 2 px | V3 F1 within 2 px |
| --- | ---: | ---: | ---: | ---: |
| All visible illustration reserve | 62.3% | 73.0% | 82.7% | 87.9% |
| Hanging thread and upper knot | 65.6% | 76.1% | 92.0% | 94.1% |
| Child head and neck | 75.8% | 88.9% | 95.6% | 98.7% |
| Child arms, body and legs | 61.0% | 82.6% | 82.2% | 94.6% |
| Upper beam and diagonal brace | 59.6% | 64.2% | 82.4% | 83.2% |
| Upright support | 68.3% | 78.8% | 84.0% | 89.0% |

At each tolerance, precision is the fraction of the vector boundary lying within that distance of the reference boundary; recall measures the converse. F1 is their harmonic mean. This makes a small local edge displacement more visible in the evaluation than area IoU alone. A “two-pixel” result refers to the normalized comparison plane, not millimetres on an original print.

Some measures are mixed in Upper beam and diagonal brace. The tables retain those outcomes rather than presenting the revision as uniformly better at every tolerance.

## Overlay method and limits

The fixed reference mask uses pale/dark photographic classification within the illustration region, a one-pixel closing operation, components selected at fixed figure locations and filling of enclosed holes smaller than 50 pixels. The large painted opening is retained. The candidate reserve is rasterized at 1000 × 1400 and its alpha coverage is thresholded at 127/255. The seal footprint, expanded to radii 74 × 90 normalized pixels, is excluded: the photograph cannot establish the hidden reserve beneath it.

In the overlay, **teal marks white missing from the reconstruction** and **magenta marks white extending beyond the reference mask**. Boundary distance is the pooled symmetric nearest-boundary distance. The same definitions are applied to both revisions.

The photograph includes print wear, camera blur and colour fringe. Tiny isolated slivers can therefore reflect the mask threshold or estimated registration as well as an imperfect vector edge. The larger connected discrepancies are more useful editing targets. The contours remain an interpretation of the visible painted edge, and fine translucent yellow residue is not fully recreated as holes in the white reserve: doing that would expose stronger paint underneath and exaggerate its contrast.

## How to inspect the result

Start with `BCFS_White_Edge_Details.png` for the upper knot and child-head regions from the supplied screenshots. `BCFS_Contour_Refinement.png` expands the comparison to the diagonal opening, child legs and upright shoulder. `BCFS_White_Edge_Overlay.png` and the offline `BCFS_Interactive_Review.html` provide the common-reference diagnostics.

The HTML offers V2, V3 textured and V3 clean artwork, wipe/blend comparison, white-edge diagnostics, photo/vector-only views, and fit/150%/200%/300%/400% zoom. It includes its image and SVG assets. Its JavaScript was syntax-checked; browser interaction was not exercised in this environment. The static boards can be inspected independently.

Additional component crops and notes are in `review/edge_components/`. They isolate one contributor's changes while holding other contours at V2; their regional measurements are supporting analysis rather than substitutes for the final merged metrics above.

## What remains from Revision 2

The more varied vector paint, continuous lower red edge, fitted seal lettering and manually drawn signature remain in place. Their construction and separate limitations are documented in `review/history/revision2/Revision_2_Report.md` and the retained paint/detail review files. No new paint, seal or lettering fidelity claim is made by this edge-only revision.

The **5:7 ratio** remains an estimate from a partly cropped photograph. The 1000 × 1400 coordinate plane is a working registration, not a verified physical print size. Colours match the supplied photograph's appearance and have not been calibrated to original inks. URW Bookman Demi remains a fitted visual substitute for the seal lettering; its historical identity is unconfirmed. The apparent signature reading “J.J. ANDRE” and artist attribution remain unconfirmed.

## Construction and validation records

- `source/reserves_v3.py` and `source/reserves_v3.svg`: independent compiled reserve, ready for assembly.
- `source/upper_reserves.py`, `source/child_reserves.py` and `source/upright_reserve.py`: editable contour sources and their component SVGs.
- `source/rebuild_poster.py`: assembles current reserves with retained V2 paint/seal/signature assets and the existing drawing/lettering.
- `source/analyze_white_edges.py`: portable rerun of the common-reference evaluation; requires the package's fixed masks, normalized photograph, preview and Inkscape.
- `review/diagnostics/`: reference, V2 and V3 masks for reproduction.
- `review/Vector_Validation.json`: structural checks of delivered SVGs and the exported PDF, plus unchanged-layer checks against V2.

The SVG checks reject embedded images, live text, filters and external references. The one-page PDF is checked for zero embedded bitmap images. Review PNGs and the photograph remain raster evidence outside the vector artwork.

## Detached-fleck sensitivity check

The original connected photographic mask has one connected component. V3 adds three small, source-visible detached paper flecks; those features are not represented by that old mask. The primary tables above deliberately retain the unchanged mask and all V3 geometry, so they count the detached features as excess reserve and include their distance in the boundary average. This helps explain the mixed raw result for the upper region.

A supplementary check retains only the largest four-connected component in each of the reference, V2 and V3 masks. Under that same rule for all three masks, the upper-region mean distance changes from 1.50 to 1.33 px. The full main contour changes from 1.41 to 1.10 px. This sensitivity result is separate from the primary comparison and does not replace it. Definitions, component areas and exact values are in `Main_Contour_Sensitivity.json`.
