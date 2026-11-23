# Greater Trail CHC — replacement overlap audit

Updated 22 November 2026. This audit supersedes the earlier audit of the normalized master.

## What is compared

The replacement master now preserves the source positions and baseline differences. The overlay uses the exact delivered SVG artwork. Only its outer canvas is changed to match the source's 1166 × 488 coordinate system; no artwork geometry is changed for comparison.

| Region | Previous delivered | Previous source-aligned | Replacement |
| --- | ---: | ---: | ---: |
| Full logo | 81.8% | 86.2% | 90.3% |
| Symbol | 94.1% | 94.1% | 94.4% |
| GREATER | 59.6% | 60.6% | 82.1% |
| TRAIL | 44.4% | 69.9% | 84.2% |
| COMMUNITY | 66.7% | 71.6% | 78.3% |
| HEALTH | 66.4% | 72.4% | 77.5% |
| COUNCIL | 46.8% | 70.4% | 78.0% |
| Underline | 54.2% | 80.6% | 82.2% |

The previous delivered master had leveled baselines. The previous source-aligned version used the same old lettering at the source positions. Including both makes the effect of placement and the effect of revised letterforms visible separately. All scores above were recomputed with the same renderer and regions. Main-name regions stop at y=406 to avoid the underline.

## Findings

- The caption now uses Albertus-derived outlines, with consistent refinements to repeated letters. The C terminals, O counter, U foot, N upright, and L foot were revised.
- GREATER / TRAIL uses custom reconstructed serif capitals after comparative font testing. It is not assigned an unverified historic font name.
- The lower-left outer oval and the underline were refined while retaining simple editable geometry.
- The supplied screenshot remains the primary reference. Its small raster defects are not replicated as new vector nodes.

## Definition and limitation

Foreground IoU = shared black area / combined black area, measured at the screenshot resolution with black <128. This is a diagnostic of silhouette overlap, not a percentage of historical accuracy or a probability of font identity. Blur, scan artifacts and subpixel placement affect it.

The exact source and delivered-SVG hashes, fixed regions, intermediate-pass scores and before/after results are recorded in Greater-Trail-Overlap-Metrics.json.
