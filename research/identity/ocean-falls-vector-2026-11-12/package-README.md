# Ocean Falls Corporation - OFC vector reconstruction

Prepared 12 November 2026 from the supplied reference package.

## Start here

**Ocean_Falls_OFC.svg** is the main editable vector. It contains three named filled paths: O, F and C. The O has a true transparent counter. There is no embedded raster, live font, tracing filter, clipping mask or white shape covering the hole.

| File | Purpose |
| --- | --- |
| `Ocean_Falls_OFC.svg` | Black master, transparent background; three editable paths |
| `Ocean_Falls_OFC_white.svg` | Reversed white master, transparent background |
| `Ocean_Falls_OFC.pdf` | Vector PDF; one page, three vector drawings, no images or fonts |
| `Ocean_Falls_OFC.eps` | EPS vector export |
| `Ocean_Falls_OFC_transparent.png` | Black raster export, 3600 pixels wide, transparent background |
| `Ocean_Falls_OFC_white_transparent.png` | White raster export, 3600 pixels wide, transparent background |
| `OFC_preview.png` | Presentation preview on white |
| `OFC_overlay_comparison.png` | Source, reconstruction and fixed-coordinate difference overlay |
| `source/` | Manually authored geometry, rebuild script and comparison scripts |
| `reference/` | The two supplied artwork references, copied without modification |
| `verification/` | Source-aligned model, comparison metrics and supplementary Gazette check |

The SVG, PDF and EPS remain scalable. The PNG files are convenient raster derivatives. The white SVG/PNG is intended for a dark background and can appear blank on white.

## How the mark was rebuilt

The three letterforms were constructed directly using straight segments and a small number of cubic and quadratic Bezier curves. The drawing is authored in an upright coordinate space and then given a shared forward shear of **0.562**, equivalent to **29.336 degrees from vertical**. This is a measured reconstruction parameter; it is not a recovered original design specification.

The model preserves the broad diagonal strokes, thinner horizontal bars, long F arm, narrow O counter, open C and small top/baseline offsets visible in the CIPO reproduction. The outer O and C corners were refined after comparing the first vector draft with the source. Smooth curves deliberately omit the raster's pixel stair-steps.

The builder does not open or process any source image. Its contour definitions are explicit in `source/build_ofc.py`, with the same model recorded in `source/geometry.json`. Raster comparisons are a separate verification step and do not create or alter the vector paths. No autotracing, contour extraction to SVG, or stock-font substitution was used.

## Overlay validation

The CIPO image is the primary shape reference. The vector was rendered at four times its 747 x 341 canvas, reduced to native size with Lanczos resampling, then compared as a binary silhouette. Reference black was defined as grayscale below 128; vector ink was defined as alpha above 127. The reference and vector share the same coordinate canvas; **no alignment warp was applied** for this comparison.

| Measure | Result |
| --- | ---: |
| Silhouette intersection | 101,796 pixels |
| Silhouette union | 102,524 pixels |
| Intersection divided by union | **99.2899%** |
| Reference-only pixels | 401 |
| Vector-only pixels | 327 |

In the comparison sheet, charcoal shows overlap, magenta shows reference only, and cyan shows vector only. This percentage describes agreement with the supplied raster, not a percentage of historical design accuracy.

The Gazette scan was also checked using one global affine registration for the entire mark, with no separate letter alignment or local deformation. Its raw thresholded silhouette overlap is **96.02%**. This corroborates the overall design while exposing small differences between the two reproductions. The F top, C top and O right edge do not align identically in both source images. The CIPO-based vector was retained instead of deforming it to combine these differences.

The Gazette fit used lightly smoothed source edges and removed small print speckles for registration only. The reported 96.02% overlap uses the unmodified scan thresholded directly. The exact transform and method are recorded in `verification/gazette/gazette_check.json`.

## Source provenance

Primary reference: `reference/OFC_CIPO_official_747x341.png`, supplied as the Canadian Intellectual Property Office artwork for application **0390863**, OFC DESIGN.

- Image: https://ised-isde.canada.ca/cipo/trademark-search/media/390863.png
- Record: https://ised-isde.canada.ca/cipo/trademark-search/0390863?lang=eng
- Supplied image SHA-256: `46772330cbd8082197bba829daab5f14ccd2cdbe748684ae6e925d416655f110`

Secondary reference: `reference/OFC_1977_Gazette_logo_890x310.png`, the supplied native-resolution crop from the **31 May 1977 USPTO Official Gazette, printed page TM 241**.

- Page: https://archive.org/details/sim_official-gazette-us-patent-trademark-office-trademarks_1977-05-31_958_5/page/n28/mode/1up
- Supplied crop SHA-256: `d5cc2dea42c5bc71daead175a494f0dee68762da03b1518925199b29a7a8d697`

Provenance descriptions and URLs are carried forward from the supplied research package. This recreation task did not undertake new historical research. The original uploaded package has not been modified.

This is newly reconstructed artwork, **not an original vector recovered from the corporation or trademark office**. The original designer, mathematical construction rules and corporate colour specifications are not established by the supplied reference material. Black follows the supplied monochrome artwork; white is a practical reverse version.

## Rebuild and edit

For ordinary editing, open the SVG in a vector editor and select its named O, F or C path. All artwork is outlined geometry; no typeface is needed. Recolour the `OFC-monogram` group's fill to recolour all three letters.

To rebuild the SVGs from the explicit model, use Python with `svgpathtools` installed:

```sh
python source/build_ofc.py
```

To reproduce the PNG used for comparison, render the source-aligned SVG at exactly 2988 pixels wide:

```sh
inkscape verification/OFC_source_aligned.svg --export-type=png --export-width=2988 --export-filename=verification/OFC_source_aligned_4x.png
```

The proof scripts additionally use Pillow, NumPy and SciPy. `make_proof.py` uses DejaVu Sans fonts for the comparison sheet only; the logo itself has no font dependency.

```sh
python source/make_proof.py
python source/check_gazette.py
```

Exports were produced using Inkscape. The PDF was rendered and visually inspected; it contains three vector drawing objects, zero embedded raster images and zero fonts. The SVG was inspected for exactly three paths and no raster or live-text elements. The EPS uses the same final master.
