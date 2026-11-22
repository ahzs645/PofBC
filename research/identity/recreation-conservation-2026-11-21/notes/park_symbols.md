# Proposed park symbols — 1971

This set reconstructs **all 22 pictograms** on the page headed **PROPOSED PARK SYMBOLS**, printed page **DD67**, PDF page **68**, of the British Columbia Department of Recreation and Conservation annual report for 1971. The report was published in 1972. The source labels them **proposed**; this package does not imply that every sign was approved or installed.

## Deliverables

- `svg/`: 22 individual, editable vector symbols. Each has a 200 × 200 viewBox, a nominal 1000 × 1000 display size, a transparent background, and no embedded image or live text.
- `png/`: transparent 600-pixel renderings for review or small-image use.
- `Park_Symbols_1971_Reconstructed.svg` and `.pdf`: the complete vector contact sheet. Its modern editorial labels have been converted to outlines; they are not a reconstruction of the original caption font.
- `Park_Symbols_1971_Reconstructed.png`: readable overview.
- `Park_Symbols_1971_Overlay_Review.png` and `overlays/`: source, reconstruction, and registered overlays.
- `sources/`, `sources.json`, and `native_page.png`: the actual native-pixel source evidence and crop locations.
- `metrics.json`: per-symbol overlap measurements, source provenance, and geometric placement refinements.

## Construction

The symbols were rebuilt with authored circles, rectangles, polygons, strokes, and cubic Bézier curves. Common elements include the circular border, trailer, boat, parking P, and the repeated snowflake arms. Negative spaces in the tent, trailer, parking letter and toilet panels are transparent compound-path holes. The vehicle and human silhouettes are independently drawn components. No bitmap contour tracer was used.

An additional numerical step refined the position, overall x/y scale and rotation of each authored pictogram within its fixed circle. This step never extracted contours or changed the authored component silhouettes. The resulting matrix is retained in the SVG and in `placement_refinement.json`. The normalisation of printed circle bounds is documented in the metrics; no local warp was used for the source overlays.

## Fidelity and limits

The source circles are approximately 160–170 native pixels across. The reconstruction regularises scan roughness and the circles themselves. The simple firewood, water, table, tent, parking and related vehicle symbols are strongly supported. Small people, animal anatomy, ropes, and the ornamental winter-recreation snowflake retain more interpretation. The overlays show those remaining differences rather than concealing them.

Overlap scores measure binary ink intersection-over-union against a small printed scan; they are **not percentages of historical accuracy**. Full-symbol scores include the common border; the separate interior score is the more demanding check of the pictogram itself. Black is a reusable master colour, not a claimed original ink specification.

## Rebuilding

`build_park_symbols.py` writes the symbols, PNGs, overlays, metrics and raster contact sheets. `refine_placement.py` performs the affine placement refinement on those authored components. `build_vector_sheet.py` assembles the outlined-label SVG and vector PDF sheet. The scripts use Pillow, NumPy, SciPy, OpenCV, CairoSVG, lxml and fontTools; the sheet labels use the installed DejaVu Sans outline font.

## Primary source

British Columbia Department of Recreation and Conservation, annual report for 1971, printed DD67 / PDF68:
https://www.for.gov.bc.ca/hfd/Library/Annual/DoRC_AR1971.pdf

Alternative colour scan:
https://rbcm.ca/wp-content/uploads/2025/07/annual_report_1971.pdf#page=68
