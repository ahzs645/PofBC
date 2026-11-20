# Forest Service card: vector reconstruction

Reconstructed from the supplied photograph, using the requested **Forest Service, Lands Department** vector artwork.

## Start here

- **artwork/forest-service-card.svg**: primary warm-paper version. Existing logo components are fitted to the card's layout, keeping the central oval narrow and expanding the lateral boughs separately.
- **artwork/forest-service-card-white.svg**: the same fitted artwork, black on white.
- **artwork/forest-service-card.pdf**: the black-on-white fitted artwork as a vector print PDF.
- **artwork/forest-service-card-original-logo.svg**: warm-paper alternative with the entire website logo uniformly scaled, retaining all its original internal proportions.
- **artwork/forest-service-card-original-logo-white.svg** and **artwork/forest-service-card-original-logo.pdf**: the unchanged-proportions alternative in black on white.
- **review/verification.json**: the structural checks, thresholds and overlay pixel counts described below.

The SVG and PDF artwork files are the vector deliverables.

## What was rebuilt

The frame is an independent vector rule, with two top arms ending beside the logo. Its position is derived from the four printed frame corners, which also establish the photograph's perspective correction. The artwork is normalized to a 1050 × 500 coordinate system.

The card text is preserved exactly:

> “England Expects Every Man to Do His Duty.”
>
> Do Yours: Prevent Forest Fires.

The card lettering is reconstructed from **C059 Bold** outlines, condensed horizontally and fitted by word. C059 is a reconstruction base, not a conclusively identified historic typeface. The lowercase height, descenders, ascenders, `i`, `t`, `g` ear, and quotation marks were adjusted to the observed print. The final capitals are 30 artwork units high; the lowercase body is 18 units; the baselines are 340.5 and 398.2. The wide space after the colon follows the photograph.

Lettering is stored as editable outlined word objects. It does not require the font to be installed, but it is not live text that can be changed by typing.

The warm-paper colour is a clean interpretation of the photographed card, not a calibrated measurement of the original stock. Paper texture, wear, fading, stains, and damaged edges are not built into the production artwork.

## Why there are two logo versions

The requested website logo is already a vector reconstruction. Its lateral boughs are shorter and its engraving is heavier than the logo printed on this particular card.

The primary version adapts the existing component groups to match the card's overall arrangement. All **6,567 paths, 5,049 circles, and one ellipse** from the source emblem are retained; their shape coordinates have not been redrawn. Group transforms reposition and scale the sprays, cones, stems, and central seal. Ink and paper paint values are mapped to the chosen colourway.

The alternative keeps the full website logo under a single uniform transform. It therefore occupies a narrower space, and the top border arms are extended to meet it.

Neither version claims that the source logo's individual needles, cone engraving, or lettering are an exact match to this photograph. The ink overlay records these differences. The source logo has deliberately been reused as requested.

## Editing

The SVG contains four named layers:

1. Paper colour.
2. Printed border.
3. Forest Service emblem, retaining editable component groups.
4. Outlined card lettering, grouped by line and word.

The oval field and the original logo's small white cutouts are painted with the paper colour. If you change the background, change those same paint values too. The files are not advertised as fully transparent single-ink stencils.

The default print size is **210 × 100 mm**. This is a convenient new output size; the photograph does not establish the original physical card dimensions. Both SVG and PDF can be scaled without loss of geometric detail.

## Verification and comparison

All four production SVGs contain **zero embedded raster images, zero live text objects, zero external references**, and unique element IDs. All source-logo path data are preserved in each version.

Each PDF contains one vector page, with **zero image resources and zero font resources**. The PDF was rendered independently with PyMuPDF and Poppler and inspected for missing details, clipping, spacing, and punctuation.

The reference was perspective-corrected once from the measured frame; individual regions were not moved again for the final overlay. In the comparison proof:

- **Dark** is shared ink.
- **Magenta** is photograph-only ink.
- **Cyan** is reconstruction-only ink.

The overlay is sensitive to ink wear, source sampling, antialiasing, and the background/ink threshold. Dense engraving and restored solid text naturally produce differences. Detailed structural checks, thresholds, pixel counts, and sensitivity results are in **review/verification.json**. These diagnostics are not percentages of historical authenticity.

## Source and provenance

- Requested logo page: https://projects.ahmadjalil.com/PofBC/?view=internal&internal=forests&internal-logo=forest-service-lands-department
- Reused SVG: https://github.com/ahzs645/PofBC/blob/main/src/internal/forest-service-lands-department.svg
- Source-logo documentation: https://github.com/ahzs645/PofBC/blob/main/artwork/internal/forest-service-lands-department/README.md
- Original SVG Git blob: `f53eaf0354ab0fd7854a5aeb4c920d2bcee2c780`
- Original SVG SHA-256: `37094db397c7c3cddf0c87ebba5460220bc1ca90d7d0aab286b2655db31cb0be`
- Reference photograph: a supplied photograph, not kept in this repository.

## Rebuild

The **source** directory contains the fitted logo components, outlined lettering, layout and placement records, and a Python builder. No photograph is traced or embedded when generating the SVG files.

SVG generation uses Python's standard library:

```sh
python3 source/build_card.py
```

For preview PNGs and vector PDFs, install CairoSVG and add `--render`:

```sh
python3 -m pip install cairosvg
python3 source/build_card.py --render
```

The optional verification script additionally uses Pillow, NumPy, OpenCV and PyMuPDF. It creates review images and the verification JSON from the saved vector artwork and rectified reference. The production SVGs do not depend on those libraries.

Prepared 20 November 2026.

## In this repository

This package is kept as supplied, minus files this repository leaves out of every source package:

- `review/original-photograph.jpg` and `review/reference-rectified.png`: the reference photograph and its corrected copy.
- `review/forest-service-card-comparison.png`, `review/forest-service-card-ink-overlay.png` and `review/lettering-comparison.png`: comparison images that carry the photograph.
- `artwork/forest-service-card-preview.png` and `artwork/forest-service-card-original-logo-preview.png`: raster previews.
- `artwork/forest-service-card-white.svg`, `artwork/forest-service-card-original-logo-white.svg`, `artwork/forest-service-card.pdf` and `artwork/forest-service-card-original-logo.pdf`: the black-on-white versions and the PDF exports. Each is another 2.3 MB copy of the same 6,567-path emblem, and `python3 source/build_card.py --render` rebuilds them from `source/`.
- `source/website-logo.svg`: a byte-for-byte copy of this repository's `src/internal/forest-service-lands-department.svg` (the same SHA-256, `37094db3…0cb0be`). The builder reads it as `source/website-logo.svg`, so copy that file there before rebuilding.

`SHA256SUMS.txt` still lists the supplied package in full; the files above are marked there as not kept. The site shows `artwork/forest-service-card.svg` as `src/cards/forest-service/england-expects.svg`: its ids prefixed `fsc-`, its title reworded, its Inkscape layer labels kept as `data-label`, whitespace between tags and paint already inherited from a parent removed. A render in Chromium at three times its size differs from the package's file in no pixel. The black-on-white version is the same drawing with two colours swapped, so the site offers it as a switch; the original-proportions alternative is kept here only.
