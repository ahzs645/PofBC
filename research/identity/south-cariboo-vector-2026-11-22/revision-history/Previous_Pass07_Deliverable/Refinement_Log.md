# Iterative refinement log

Selected master: pass07. Prepared 22 November 2026.

## Construction rule

Every tree change edits deliberate named branch masses or negative spaces. No autotracing, contour extraction, or image-to-path conversion was used. The typography retains native Souvenir letterforms; a 0.24 px optical stroke (0.12px per edge) was expanded into fills. Initial C/H/C placements moved 0.4 px left and 0.2 px up.

## Root revision sequence

| Pass | Work | Whole IoU | Dark IoU | Dark lower IoU |
|---|---|---:|---:|---:|
| 00 | Baseline | 86.37% | 78.37% | 70.92% |
| 01 | Lower trunk, diagonal opening, terminal branch | 86.71% | 80.58% | 74.51% |
| 02 | Opening topology; closed eye; detached twig | 86.99% | 81.77% | 75.68% |
| 03 | Curved tiers and lower bough draft | 87.18% | 81.95% | 74.53% |
| 04 | Narrower loop, curved tongue and base draft | 87.31% | 81.81% | 73.80% |
| 05 | Merge pale/type; refine curved left tiers | 88.59% | 82.08% | 74.46% |
| 06 | Final diagonal channel; base depth trials | 88.67% | 82.37% | 75.49% |
| 07 | Restore local base and bowl weight; accepted | 88.66% | 82.93% | 77.47% |

The pale tree went through four geometry revisions and a small corner-finishing pass. Typography candidates compared conservative optical weights and placements. Their separate logs are in construction/. These are visual construction decisions checked with overlays, not pixel-contour fitting.

## Decisions that matter

- Restored a closed middle eye and an open diagonal channel in the dark tree. Removed two unsupported enclosed chips.
- Refined the lower trunk edge, lower-right branch mass, left loop, tongue and bowl.
- The base was briefly made too light; later passes restored its local depth while keeping a thin swept stroke.
- Rebuilt pale left branches with sparse curves and corrected the lower hook and return. Hidden right-side pale geometry was retained.
- Tested extra whole-dark-tree offsets up to 0.35 px. Rejected them because selected dark binary scores improved while whole-logo overlap and continuous-density error worsened. Final authored alignment is unchanged.
- Tiny finishing changes were selected for sensible curves, not strictly the maximum value of one metric.

## Measurement method

Both images are compared on the source 315 x 141 grid. Inkscape renders the actual SVG at 1890 x 846; Lanczos reduces this to the source grid. Ink density is clip(dot(255-RGB,[190,133,197])/dot([190,133,197],[190,133,197]),0,1).

All/pale masks use density>=0.25, dark/type masks>=0.75. The dark window is x<74; lettering x>=140. The pale window is x<105 and x>(70 if y<92 else 52), so it is a visible spatial window and can include a few detached dark twigs. Boundary distances are symmetric nearest-neighbor distances between 4-neighbor erosion boundaries. Full-mask boundaries are computed before region clipping.

The red/cyan overlay has RGB=255*[1-vector_density,1-source_density,1-source_density]. It is continuous, without a threshold. Red means more source ink, cyan more reconstructed ink. Black/gray means similar density.

## Stopping judgment

The last candidate passes independent review at native size and magnified scale. It preserves the source hierarchy, tree tilt and branch rhythm while correcting coherent shape mistakes. Small lower terminal twigs, edge bands and brush-texture fragments remain interpretations. Not every residual is compression; the small source does not uniquely determine those curves. Additional tiny islands or per-pixel surgery would add unsupported detail. This is a reconstruction, not a recovered original master.

## Verification

The portable SVG and logo PDF use vector paths. The separate branch model retains editable named components; the main artwork has real transparent openings. No bitmap is embedded and no installed font is required by the portable master.
