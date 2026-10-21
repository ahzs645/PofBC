# GO B.C. Ferries — vector reconstruction

Rebuilt from the supplied **Vintage GO B.C. Ferries Sticker(2).png**, 1354 × 1161 pixels. The input is preserved unchanged inside `source/`.

## Main files

- `go-bc-ferries.svg`: complete editable master, transparent outside the sticker; named layers, separate shapes and outlined lettering.
- `go-bc-ferries.pdf`: vector PDF exported from that master. Scale to the required reproduction size; no original physical sticker dimensions were supplied.
- `go-bc-ferries.png`: 2708 × 2322 transparent PNG preview/export.
- `go-bc-ferries-comparison.png`: four-panel reference / reconstruction / equal overlap / magenta-edge review.
- `go-bc-ferries-edge-overlap.png`: full source-grid magenta edge overlap.
- `go-bc-ferries-50-percent-overlap.png`: equal-opacity blend on the unchanged source grid.
- `go-bc-ferries-interactive-comparison.html`: self-contained offline opacity, wipe and edge comparator with zoom. Open it in a browser; no network access or installation is needed.
- `comparison-metrics.json`: machine-readable checks and their limitations.
- `components/`: separate editable artwork groups and lettering geometry/build data.
- `build.py`: reassembles the master from the component SVGs using only Python's standard library. With `--export`, Inkscape also generates PDF and PNG.

## Construction

This is a full geometric reconstruction. No bitmap contour tracing was used to generate the artwork. The SVG contains **145 paths, 23 rectangles, 15 circles and 2 ellipses**. It contains **no `<image>` or live `<text>` elements** and requires no installed font.

The perimeter and inner field are built from eight smooth cubic arcs each, with sparse manually selected construction landmarks and fixed endpoint tangents. Mountain ridges, snowcaps, gull, feather tips, ferry hull/decks, flag cloth and flower are authored as simple paths and primitives. Repeated windows and portholes are separate editable objects. Both wings and all visible ferry details are retained. The gull correctly covers the ferry.

The main title and upper route alphabet are custom geometric lettering. The lower route combines custom geometry and saved font outlines. The small authority subtitle uses saved DejaVu Sans Bold glyph outlines with individual reference-based placement. Letters are editable as paths, with no font lookup at display time. These are visual reconstructions, not recovered historical font files.

## Preserved wording

- VICTORIA - VANCOUVER - NANAIMO
- SUNSHINE COAST / GULF ISLANDS (separated by the flagpole in the layout)
- GO B.C. FERRIES
- BRITISH COLUMBIA TOLL AUTHORITY FERRY SYSTEMS

## Flat palette

| Area | Hex |
| --- | --- |
| Cream | #fce6a3 |
| Teal | #1da4a9 |
| Green | #047634 |
| Dark navy | #031e24 |
| Lettering / ink | #070a09 |
| Gold edge | #efb247 |

These flat colours approximate the reference's dominant colours. Tonal variation, paper grain and fuzzy edge fringe are intentionally omitted.

## Overlap comparison and limits

Every component is drawn on the original **1354 × 1161** canvas. Both original and reconstruction use the identity transform **[1, 0, 0, 1, 0, 0]** for comparisons. There is no post-comparison translation, rotation, scale fit or local warp. Any display resizing applies equally to both images. The new silhouette is regularized; source fringe is retained in the reference views.

The outer alpha silhouette has an intersection-over-union of **99.73%**, with a **2.00 px** 95th-percentile symmetric boundary separation. This metric evaluates the outside sticker shape only. It must not be interpreted as a whole-artwork similarity score.

Independent rendered lettering-mask IoU on the original grid:

| Lettering region | IoU |
| --- | --- |
| Main title | 96.05% |
| Upper route | 93.76% |
| Lower route | 89.07% |
| Authority subtitle | 92.63% |

Mask IoU measures intersecting shape area divided by union area, after segmentation of the named source region. Thin letter strokes are sensitive to small contour/weight differences and antialiasing. These figures do not imply recovery of original production geometry.

During comparison, the gull's lower wing was narrowed by about 5–7 source pixels where necessary, its feather notches were shortened, and the long upper-wing shoulder was lowered to follow the supplied reference. Ferry deck windows, nine visible portholes, funnel panel and hull were checked separately. Final review found no missing major motif, route wording or unintended overlap.

Remaining differences are small letter shapes/weights (particularly some lower curves and the upper M), the dogwood's internal seams/tiny marks, and the deliberately regularized border. Ferry shapes hidden beneath the gull are inferred so the editable shapes continue coherently.

## Source identity

Source SHA-256: `40e933772582c546e77afd19949e8568782e9340726d45c6bb0a65c8b4786f07`

Master SVG SHA-256: `e5cd55c3655ae76d433d4b0c43d4b2c95bd09bd3962806db32a0f618bedb331b`

Created 21 October 2026 from the user-supplied reference.
