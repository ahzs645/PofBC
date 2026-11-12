# British Columbia Housing Management Commission — 1978 logo

This package contains a clean vector reconstruction of the BC house symbol and the complete three-line logo in the supplied 1978 annual report. Created 12 November 2026.

## Choose a file

- **Full_Logo_Brown.svg:** the complete logo, with the name outlined as vector paths.
- **Symbol_Brown.svg:** the standalone house-shaped BC monogram.
- **Black.svg / White.svg variants:** the same artwork in a single flat colour. White artwork is intended for placement on a dark background.
- **Full_Logo.pdf / Symbol.pdf:** vector PDFs with closely fitted pages. The complete logo page is 10 inches wide; the symbol page is 4 inches wide.
- **Transparent.png files:** 3600-pixel-wide complete logo and 2000-pixel-wide symbol, both with alpha transparency.
- **Comparison.png:** the original scan, reconstructed artwork, and an aligned colour overlay at the same scale.
- **Preview.png:** the complete logo rendered on white for quick viewing.

All artwork filenames begin with `BC_Housing_1978_`. The SVG and PNG artwork has transparent backgrounds, including the internal counter and the narrow roof slit. The preview and comparison sheet have white backgrounds.

## How it was rebuilt

The house symbol was drawn with **two intentionally constructed filled paths**. Straight roof slopes and walls are joined by a small number of deliberate curves. The B's inward cusp, stepped counter, continuous roof slit, C opening, and rounded corners were reconstructed from the design visible in the report. No automatic bitmap contour tracing was used.

The full name uses **Nimbus Sans Bold outlines**, with closely fitted letter spacing and adjusted word gaps. The compact appearance is reproduced mainly through spacing; the letters are not broadly squeezed to fit. Each of the 42 letters is a separate path, organized into three named line groups. The complete logo therefore contains 44 paths, and the standalone symbol contains two. There are no raster images, live text, external fonts, filters, or external references in the artwork SVGs.

## Source and reconstruction limits

Source: the user-supplied `151845_bc_housing_ar_1978.pdf`, British Columbia Housing Management Commission, annual report for 1978.

- **PDF page 2:** cover; complete logo and colour reference.
- **PDF page 3:** title page; primary reference for symbol proportions and the full name.
- **PDF page 13:** enlarged symbol above “Housing Communities”; used to clarify the joins and curves.

The cover and title-page symbols have closely matching proportions. The enlarged interior reproduction is slightly narrower, so it was used to interpret the details without overriding the primary lockup's proportions.

**The original historical typeface is not verified.** Nimbus Sans Bold is a close visual reconstruction. The brown, **#836458**, approximates the cover scan; it is not a verified original ink or brand colour specification. Scan texture, uneven edges and small printing distortions were not built into the vector paths.

## Validation

The rebuilt symbol and lettering were visually checked against the scan using an aligned overlay. The SVG structure was inspected to confirm the path counts and the absence of embedded raster images or font dependencies. Both PDFs were reopened, inspected for vector drawings, and rendered for visual review. PNG alpha transparency was checked.

## Editable source

The `source` folder includes the three reference extracts, an outlined wordmark master, typography parameters, provenance and validation metadata, and `rebuild_logo.py`. The rebuild script uses the saved vector wordmark and manually authored symbol paths, so it does not need the original font installed. It requires Python, PyMuPDF (`fitz`), NumPy and Pillow; its optional comparison-sheet labels use the DejaVu Sans fonts at the paths recorded in the script. The SVGs themselves have no such dependencies.

Run `python source/rebuild_logo.py` from the unpacked package to regenerate the artwork and rendered previews. The full report is not duplicated in this package.
