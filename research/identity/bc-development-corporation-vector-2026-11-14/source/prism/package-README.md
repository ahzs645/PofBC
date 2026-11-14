# British Columbia Development Corporation

## Reconstructed vector artwork

Prepared 13 November 2026 from the three newspaper reference images supplied in this conversation.

Start with **BCDC-symbol.svg** for the symbol alone, or **BCDC-logo.svg** for the symbol with the four-line name. Both have transparent backgrounds and contain actual filled vector paths. Their appearance does not depend on an installed font.

This package is a reconstruction from printed references. It is not an authenticated original artwork file or a recovered corporate standards manual.

## Files

| File | Purpose |
| --- | --- |
| BCDC-symbol.svg | Primary symbol; four compound paths and twelve transparent face openings. |
| BCDC-logo.svg | Symbol and four-line serif name; all lettering converted to filled outlines. |
| BCDC-symbol-white.svg | White symbol for placement on a dark background; transparent openings and background. |
| BCDC-logo-white.svg | White version of the full name lockup. |
| BCDC-historical-address.svg | Separate historical advertisement layout including the address shown in the references. |
| BCDC-symbol-construction.svg | Editable construction with one stroke-based prism repeated four times. |
| BCDC-vector-artwork.pdf | Three vector artboards: symbol, name lockup, historical address layout. No embedded bitmap artwork or font dependency. |
| BCDC-symbol.png | 1120 x 1200 transparent convenience export. |
| BCDC-logo.png | 2608 x 1200 transparent convenience export. |
| BCDC-preview.png / .svg | Full logo displayed on a white presentation background. |
| BCDC-overlay-comparison.png | Symbol comparisons against all three references, including aligned overlays. |
| BCDC-lettering-comparison.png | Name comparison against the largest reference; shows the remaining type differences. |
| BCDC-construction.json | Reconstruction parameters, including geometry, type fitting, and optical spread. |
| rebuild_bcdc.py | Reproducible geometric and font-outline source. |

The PDF pages use the artwork's own bounds rather than a standard paper size. They can be imported as vector artwork or printed with the desired page scaling.

## How the symbol was rebuilt

The symbol was constructed from one idealized three-face prism. Its outer face and two diagonal faces share connected boundaries. The module is repeated through four quarter turns in a square construction system; the completed form is then scaled vertically by 15/14.

The resulting symbol is 280 units wide and 300 units high. The slightly tall form is supported by both larger references, including their outer face openings. Within the square base system, the chosen face side is 60 units, the diagonal extension is 57.5 units in each direction, the line weight is 11.5 units, and the clear central gap is 22 units. These are reconstruction choices, not asserted historical specifications.

The production symbol expands the geometry into four compound filled paths. Each module has one outside contour and three inside contours. The face openings use an even-odd fill rule, so they remain transparent on any background. No white polygons conceal the background.

No autotracing or bitmap embedding was used. The printed grain, small asymmetries, and irregular ink edges were not incorporated into the master geometry.

## Lettering and historical layout

The exact historical typeface could not be established from these scans. The name uses **Nimbus Roman Regular**, fitted to the visible widths, alignment, and line spacing of the references. A small optical spread of 0.35 unit on each side strengthens the thin strokes. That spread is expanded and united with each glyph, so the delivered lettering consists of filled contours rather than live text or stroked text.

The result is an outlined serif approximation. It should not be described as an exact font identification. The lettering comparison deliberately shows the remaining differences, including the lowercase t and some descender proportions.

The address uses an outlined Nimbus Roman Bold Italic approximation. It is provided only in the historical layout:

272 Granville Square,  
200 Granville Street,  
Vancouver, B.C.

This reproduces the supplied advertisement text and does not present it as current contact information. The small marks after "Corporation" in the largest scan were omitted because the second serif reference does not support them as part of the name.

The separate advertisement's all-capital sans-serif typesetting was not substituted for the repeated serif lockup.

## Comparison and validation

The same symbol master was compared against all three references. Each symbol overlay uses only position and bounding-box scale for alignment; the vector contours are unchanged between rows. Source ink is shown in magenta, the reconstruction in cyan, and agreement in a darker combined colour. The small advertisement is less precise because its original strokes occupy very few pixels.

The lettering comparison uses one placement and scale derived from the symbol in the largest source. Individual glyphs were not warped to hide differences in the overlay.

The production SVGs contain no raster images and no live text. The primary symbol has four separate modules and twelve enclosed transparent faces. The PDF was checked for vector content and visually rendered for inspection.

## Editing and reuse

- Recolour the production artwork by changing the group fills. Its holes and background stay transparent.
- Scale proportionally to preserve the reconstructed 14:15 symbol aspect ratio.
- Use the construction SVG or the source script to change the geometric model. The production SVG is intended for ordinary placement, scaling, and recolouring.
- The logo files contain no external links, font files, scripts, or embedded image data.

To regenerate the core artwork, install Python with fontTools, Pillow, and PyMuPDF, plus Inkscape and the URW Base 35 fonts. Adjust FONT_DIR in the source if those fonts are installed elsewhere, then run:

```bash
python rebuild_bcdc.py --pdf
```

The script writes the SVG artwork, convenience PNGs, preview, parameter JSON, and PDF beside itself. The two comparison sheets are review artifacts made from the supplied images; the source images are not redistributed in this package.
