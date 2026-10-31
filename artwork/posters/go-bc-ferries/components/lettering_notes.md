# Reconstructed GO B.C. Ferries lettering

## Files

- `lettering.svg`: complete standalone SVG component on the original 1354 × 1161 coordinate grid.
- `lettering_geometry.json`: named glyphs, literal path data, and individually editable placement matrices.
- `lettering_build.py`: rebuilds the SVG with Python's standard library; no source image, external fonts, or tracing software required.

## Coverage and construction

- **Top ring:** VICTORIA-VANCOUVER-NANAIMO — 26 individually placed glyphs from a deliberately drawn geometric alphabet. These are clean rectangles/polygons/cubic curves, not bitmap contours. The two R occurrences use separate manually drawn bowl proportions where the source differs.
- **Bottom ring:** SUNSHINE COAST / GULF ISLANDS — all 24 glyphs. Eleven use manually drawn geometry and thirteen use saved DejaVu Sans outline geometry with measured letter placement and a small vector stroke correction. The slash in this description is the physical flag-pole gap, not printed punctuation.
- **Main title:** GO B.C. FERRIES — all large letters deliberately drawn from cubic curves and straight stems. Both circular periods are separate editable circles.
- **Subtitle:** BRITISH COLUMBIA TOLL AUTHORITY FERRY SYSTEMS — all 40 letters outlined from DejaVu Sans Bold, individually fitted to the visible spacing/proportions. This is a visual reconstruction, not a claim to have identified the historic typeface.
- Both perimeter separator dots are independent circles.

There are no raster elements, linked images, live text elements, or font dependencies in the component. The source segmentation was used only to measure placement and assess agreement; no segmented pixel contour was converted into a path.

## Comparison

The final rendered SVG was compared directly on the source's 1354 × 1161 grid, with no extra alignment transform applied to the comparison images. Diagnostic masks classify the visible source ink and compare it with the rendered SVG alpha. The geometry-fitting raster sampler's integer pixel indices were converted to physical pixel-center coordinates when constructing the final SVG; that is coordinate convention conversion, not a later proof-image fit.

Final rendered-mask intersection-over-union:

| Region | IoU |
|---|---:|
| Top perimeter lettering | 93.76% |
| Bottom perimeter lettering | 89.07% |
| Main title | 96.05% |
| Small subtitle | 92.63% |

These are region-specific diagnostic overlaps, not an overall accuracy score. The remaining differences are chiefly minor glyph contour/weight differences, particularly the M in NANAIMO and some bottom-ring curves. Source texture and antialiasing are intentionally absent from the clean geometry.

QA image: `work/typography/lettering-mask-overlap.png` (source-only cyan, vector-only magenta, shared ink dark). Exact metrics: `work/typography/lettering-qa-metrics.json`.
