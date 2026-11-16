# Railway marks: vector search and reconstructions — 16 November 2026

Targets: the raster railway assets in `src/gallery/collectedData.js` for the British Columbia
Railway Company (`bc-railway-company`) and the Pacific Great Eastern Railway
(`pacific-great-eastern-railway`). The 14 targets are listed in the table below. No original
vector was found for any of them. Twelve are rebuilt as labelled vector reconstructions, and two
are not done.

All new SVGs are in `public/identity-collected/<body>/…-rebuilt.svg`. Records ready to merge are in
`proposed-assets.json`, each with `reconstruction: true` and `evidenceType: vector-reconstruction`.
Review sheets are in `review/*.webp`: each shows the source, the vector and an overlay, where
grey = both, red = source only and blue = vector only.

## Search for original vectors

**British Columbia Railway Company website wordmark.** Through this session's proxy, `bcrco.com`
serves a TLS certificate that does not match its name. The site was therefore read through the
Wayback Machine (CDX listing of 543 URLs). Results:

- **Logo files.** All are raster. The archive has the current `bcrco_logo-1.png` (236 × 124,
  byte-identical to the gallery file), a 462 × 238 version from 2023 and a 485 × 250 version from
  2022. No SVG of the logo was ever captured. The 2006 `bcrlogo.gif` is the BCR Properties mark.
- **63 archived Company PDFs.** These are the annual reports for 2001–2009, the service plans,
  statements of financial information (2009, 2017–2023), board attendance, policies, terms of
  reference, compensation disclosures and vegetation plans. All were downloaded and inspected for
  coloured vector paths and embedded images. None carries the website's heavy italic acrostic as
  vector:
  - fia2018–2021 hold the cover acrostic as a 600 × 327 bitmap.
  - The 2006, 2008 and 2009 annual reports set the acrostic as live Eurostile-Demi text.
  - Policies, attendance sheets and the privacy notice use small Verdana-style bitmaps.
  - kinder_news.pdf uses live Verdana Bold Italic, which is the letterhead lettering that
    `bc-railway-vector-2026-11-12` already extracted.
  - Six captures are truncated at 1 MiB, and one would not download.

  The 2001 and 2003 annual reports carry an earlier **blue "BCRC" cover monogram as real vector
  paths**. That is a different mark from the target, so it was not extracted. It is a lead for a
  later pass. Every URL and its outcome is in `source-register.json`.

**PGE marks.** These come from *The Cariboo*, Issue 3 (1991), and two Streamliner Memories
brochure scans. The Cariboo PDF holds the illustrations as 1-bit scans at about 300 dpi, so the
registered 300-dpi crops already contain all the detail there is. The brochures are JPEG scans at
about 302 dpi. For those two marks, the logo region was re-rendered from the PDF at the scan's own
resolution, because the registered crops are smaller. These marks predate desktop publishing, and
no vector original exists online.

## Reconstruction method

The method follows `bc-housing-1978-vector-2026-11-12`. All coordinates are in source pixels, so
each SVG lies directly over its source crop for checking.

- **Geometry.** Rings, discs, diamonds and ovals are fitted to *both* edges of each printed line:
  - circles by least squares over 720 radial samples;
  - diamond sides by line fits;
  - ovals by ellipse fits.

  The fitted values are recorded in `fit/m_*.json` and in `config/*.json`.
- **Lettering.** Lettering is set in the closest free typeface found and converted to outlines.
  There is no `<text>` and no font dependency. Each printed letter is a connected component in the
  scan. For each run of lettering, one size and one width factor are shared by all letters. Each
  glyph is then turned to the tangent of the ring or oval and placed by centroid, followed by a
  ±4° and 0.25-px search (`scripts/ringtext.py`). Candidate typefaces were scored by mean
  per-letter overlap (IoU), and the best was kept. **No original typeface is verified.**
- **Automatic tracing.** Automatic tracing (potrace, by way of `potracer`) was used for exactly
  three kinds of complex drawn element, and this is disclosed in each `fidelityNote`:
  - the caribou heads;
  - the interlaced Roman monogram of the square diamond;
  - the script P-G-E monogram.

  The greyscale scan is upsampled ×4 (bicubic) and thresholded at 50%. Specks under about 40–60
  upsampled pixels are dropped. The trace is used as drawn. **It was not hand-redrawn.** This is
  more than the "starting guide" the brief prefers. If that is not acceptable, the reviewer can
  drop those assets. Rings and lettering are never traced.
- **The Point Ellice diamond is drawn entirely by hand.** It uses fitted diamond and ring
  geometry, and the monogram is built from monoline strokes. There is no tracing and no type.
- **Colours.** Colours are sampled from the scans, or are near-black (#1A1A1A) for the
  one-colour illustrations. They are approximations.

## Results

| Target asset | New SVG | Type / tracing | Overlap with source |
| --- | --- | --- | --- |
| `source-bc-railway-company-bc-railway-company-png` | bcrc-website-wordmark-rebuilt.svg | Source Sans 3 Italic 800 (Myriad-family match), widened ~118%, +4° slant; 29 letters placed | ~0.84 vs 485-px capture; 0.79 vs the 236-px file |
| `cariboo-pge-point-ellice-diamond-1929` | pge-point-ellice-diamond-1929-rebuilt.svg | hand-drawn monoline monogram; fitted diamond and ring | 0.88 |
| `cariboo-pge-square-diamond-unshaded-c1934` | pge-square-diamond-unshaded-c1934-rebuilt.svg | fitted diamonds and ring; **monogram traced** | 0.91 |
| `cariboo-pge-circular-script-monogram-1935` | pge-circular-script-monogram-1935-rebuilt.svg | fitted rings; **script traced** | 0.97 |
| `cariboo-pge-caribou-rolling-stock-1945` | pge-caribou-rolling-stock-1945-rebuilt.svg | Oswald Bold; **caribou traced** | 0.86 (letters 0.81/0.79) |
| `cariboo-pge-caribou-corporate-light-1946` | pge-caribou-corporate-light-1946-rebuilt.svg | Montserrat SemiBold, widened; **caribou traced** | 0.91 (letters 0.75/0.83) |
| `cariboo-pge-caribou-corporate-bold-1948` | pge-caribou-corporate-bold-1948-rebuilt.svg | Poppins ExtraBold; **caribou traced** | 0.88 (letters 0.85/0.84) |
| `cariboo-pge-caribou-rolling-stock-mid1946` | pge-caribou-rolling-stock-mid1946-rebuilt.svg | Oswald Bold; **caribou traced** | 0.88 (letters 0.78/0.79) |
| `cariboo-pge-caribou-passenger-roman-1947` | pge-caribou-passenger-roman-1947-rebuilt.svg | C059 Bold (Century Schoolbook style); **caribou traced** | 0.84 (letters 0.72/0.74) |
| `cariboo-pge-caribou-oval-advertising-1956` | pge-caribou-oval-advertising-1956-rebuilt.svg | Poppins Black, widened; **caribou traced** | 0.87 (letters 0.79/0.79) |
| `source-pacific-great-eastern-railway-pge-brochure-logo-png` | pge-brochure-logo-rebuilt.svg | Poppins Black, widened; **caribou traced** | 0.85 (letters 0.80/0.78) |
| `source-pacific-great-eastern-railway-pge-scenic-route-brochure-logo-png` | pge-scenic-route-brochure-logo-rebuilt.svg | Poppins ExtraBold; **caribou traced** | 0.88 inside badge (letters 0.84/0.84) |
| `cariboo-pge-square-diamond-shaded-1935` | — | not done | — |
| `cariboo-bcr-dogwood-stacked-wordmark-masthead-1991` | — | not done | — |

The overlap figures are silhouette IoU against the 50%-binarised source. They measure geometric
agreement, not historical accuracy. Letters drawn along an arc are slightly wedge-shaped, while
type is not, so the per-letter scores have a ceiling of roughly 0.85.

## Not done

- **PGE square diamond, shaded (1935).** The illustration's shading is a stipple. Its bands are
  reported as black, vermilion and ultramarine on yellow, but the illustration does not show which
  band carries which colour. A flat-tone vector would have to invent that mapping. The ring and
  monogram also differ from the unshaded version, so its geometry cannot be reused.
- **BC Railway dogwood masthead (The Cariboo, 1991).** This is the same lockup as the existing
  reconstructions `bcr-dogwood-white` and `bcr-dogwood-dark` (bc-railway-dogwood-vector-2026-11-12).
  A one-colour version would recolour that geometry rather than fit this masthead, which would
  duplicate an existing vector.

## Limits

- Typefaces are free matches. The BCRC website lettering has a Myriad-like structure, and Source
  Sans 3 is its open relative. Noto Sans Italic scored marginally higher (0.856 against 0.836
  whole-mark), but its letterforms are less like the source's.
- The traced caribou keeps scan irregularities. On the scenic-route badge, the soft colour scan
  loses the neck shading.
- Only the 1956 oval source crop clips the left edge of the oval. The shape is completed from the
  ellipse fit.
- The thin white edge around the website wordmark, which is a web-image effect, and the white
  sticker edge around the scenic-route badge are left out.

## Reproducing

The scripts are in `scripts/`. They need PyMuPDF, OpenCV, scikit-image, scipy, fontTools and
potracer (`pip install potracer`), plus Node with `@resvg/resvg-js` for `render.js` and
`overlay.py`.

- **BCRC:** `bcrc_fit.py` (typeface search), then `bcrc_build.py`.
- **Point Ellice:** `build_point_ellice.py`.
- **Square diamond:** `build_square_diamond.py`.
- **Script monogram:** `build_script_monogram.py`.
- **Caribou badges:** `build_badge.py config/<mark>.json`. In the configs, `<repo>`, `<work>` and
  `<fonts>` stand for the repository, the working folder and the downloaded Google Fonts files.
- **Records:** `write_proposed_assets.py` regenerates `proposed-assets.json`.
