# Lower Mainland health regions: vector search and reconstructions (2026-11-16)

Covers the raster logos of six 1997–2003 bodies: South Fraser Health Region, Simon Fraser Health Region,
Vancouver/Richmond Health Board, North Shore Health Region, Coast Garibaldi Community Health Services
Society and Sunshine Coast Community Health Council. Proposed gallery records are in
[`proposed-assets.json`](proposed-assets.json). Every source tried is in
[`source-register.json`](source-register.json). Nothing under `src/` was changed.

## Results

| Body | Result | New file (under `public/identity-collected/`) |
|---|---|---|
| North Shore Health Region | **Original vector found.** 1999/2000 Annual Report cover (Quark PDF, Sept. 2000), native paths | `north-shore-health-region/north-shore-health-region-annual-report-2000.svg` |
| South Fraser Health Region | **Reconstruction**, horizontal colour 2001: original 2001 newsletter outlines moved into the horizontal layout | `south-fraser-health-region/south-fraser-health-region-horizontal-colour-2001-rebuilt.svg` |
| South Fraser Health Region | **Reconstruction**, reversed horizontal 1998: original outlines plus the tagline set in Yesteryear | `south-fraser-health-region/south-fraser-health-region-horizontal-1998-rebuilt.svg` |
| South Fraser Health Region | **Reconstruction**, stacked 1998: original symbol outline plus the name set in Enriqueta SemiBold | `south-fraser-health-region/south-fraser-health-region-stacked-1998-rebuilt.svg` |
| Simon Fraser Health Region | **Reconstruction**, monochrome and purple/cyan colourways: S symbol fitted; caps in URW Classico; *region* fitted to the bitmap contour | `simon-fraser-health-region/simon-fraser-health-region-monochrome-rebuilt.svg`, `…-colour-rebuilt.svg` |
| Coast Garibaldi Community Health Services Society | **Reconstruction** from a larger bitmap found inside a June 2000 Word header (765 × 246 px). Name in Gelasio Bold Italic | `coast-garibaldi-community-health-services-society/coast-garibaldi-health-rebuilt.svg` |
| Vancouver/Richmond Health Board | **Not done.** No vector source found. The apple-and-heart emblem is a painterly brush illustration, which could only be redrawn by tracing | — |
| Sunshine Coast Community Health Council | **Not done.** Only web JPEGs exist. The emblem is about 100 px tall inside a photographic banner, so a redraw would invent detail and a new lockup | — |

## South Fraser (the priority)

- **What survives as vector.** The April–May 2001 newsletter has the stacked black logo as native paths
  (already in the gallery). The symbol has four crescent paths. The name has 23 glyph outlines and the
  tagline 36. There is also one rule.
- **Archived PDFs from 1999–2000** (the April 2000 HR application and three news releases) do draw the logo
  as vector. However, Acrobat PDFWriter quantised the Word WMF to a 0.75 pt staircase, and the small text
  became bitmap glyphs. That geometry is unusable, as the
  [evidence renders](evidence/south-fraser-hrapplication-2000-quantized-vector.webp) show. The HR
  application does preserve the four exact RGB fills of the colour symbol (#338C95, #006F7A, #80D4C8,
  #00A891), which are recorded as evidence.
- **Horizontal colour, 2001.** Each part of the newsletter vector was fitted to the July 2001 raster. The
  fitted parts were the symbol, the two name lines, the rule and the two tagline lines.
  - All five parts fit at one common scale (6.79 ± 0.005 px/pt), and the text lines keep the newsletter's
    exact vertical spacing. So the colour lockup is the same artwork rearranged.
  - The parts are only translated; nothing is reshaped. The overlay IoU is 0.92.
  - The colours are averages of the dithered raster under each part. The rule weight (0.42 pt) is measured.
- **Reversed horizontal, 1998.** The name lines fit at one scale (13.52/13.57 px/pt) with the same line
  spacing. The symbol is the same emblem. Both are therefore reused, in white on a measured black panel.
  - The "Working together for a healthy future" script is not identified. It is set in Yesteryear (OFL,
    the best of about 45 script candidates), word by word at a common scale, and converted to outlines.
  - It only approximates the original pen script. The review overlay shows the differences.
- **Stacked, 1998.** The symbol matches the 2001 emblem. The photocopied scan's ink spread closes its white
  gaps, but the 2001 outline still fits.
  - The name is in a different, heavier serif, possibly Friz Quadrata (not verified). It is set in
    Enriqueta SemiBold (OFL), which fit best of about 80 serif candidates, and converted to outlines.
  - The fit was made on the native 369 dpi thesis scan, not the 288 dpi gallery crop.

## Others

- **North Shore.**
  - The cover logo is drawn as 49 native paths: the box, the green ground, the mountain and every glyph.
    The cover is a 270°-rotated Quark spread, and the extraction only undoes the rotation.
  - The green is CMYK 100/0/69/30 in the content stream, written as MuPDF's RGB (#00805F). It is the same
    design as the November 1999 advertisement and the reversed trail-panel raster, in colour.
- **Simon Fraser.** Fitted to the 1943 × 990 one-bit Continuum bitmap. The overlay IoU is 0.95 against
  that bitmap and 0.89 against the website JPEG at one uniform scale.
  - S symbol: the straight block edges are placed at measured positions, and each curved edge is one
    least-squares Bézier chain fitted to edge points sampled row by row or column by column.
  - Capitals: URW Classico (Optima design) expanded horizontally to 133.5%. With that expansion all three
    lines overlay almost exactly. Whether the original is Optima stretched or a wide face is not verified.
    URW Classico's licence status is unclear (see its CTAN README); only outlines are used.
  - *region*: hand lettering, so its outline is fitted automatically to the bitmap contour. This is
    disclosed bitmap-contour fitting, not a font.
  - Colours are averaged from the 2001 website JPEG.
  - The same design appears on the 1997 letterhead and the 2003 advertisement.
- **Coast Garibaldi.**
  - Source: the Word "Save as Web Page" export of the Community Grant Application has an `oledata.mso`
    archive. Inside is a zlib-compressed Word 8.0 header object, created 2000-06-21. Its only picture is a
    765 × 246 greyscale PNG of the logo, kept as
    [evidence](evidence/coast-garibaldi-2000-word-header-bitmap.png). There is no WMF or EMF.
  - From that bitmap: the disc is a circle fit (rms 3.8 px, raised by the white lines meeting its edge),
    and the six bars are measured centroids.
  - The ridge and sun lines are stroked Béziers through the skeletonised centrelines, clipped to the disc.
  - The name is in Gelasio Bold Italic (best of 20 bold-italic candidates; the original is probably a wide
    Lucida-like face and is not verified).
  - Colours are from the 2001 GIF.

## Review images

`review/` holds three-row images: the source, then the vector, then an overlay where grey means
agreement, magenta is source-only and green is vector-only. North Shore has a side-by-side of the PDF
render, the SVG and the 1999 advertisement instead.

## Scripts

`scripts/` contains the fitting and building code, with the fitted parameters as `fit_*.json`. It expects
the downloaded sources and fonts under a scratch folder (the paths are in the scripts), and needs PyMuPDF,
fontTools, uharfbuzz, scikit-image and SciPy. Rendering checks used PyMuPDF and `@resvg/resvg-js`.

- `extract_pdf_vector.py`: North Shore extraction.
- `build_colour2001.py`, `build_h98.py`, `build_st98.py`: South Fraser.
- `build_sf.py` and `sf_symbol.py`: Simon Fraser.
- `build_cg.py` and `cg_strokes.py`: Coast Garibaldi.
- `fontcmp.py`: font candidate ranking.

The fonts used (Yesteryear, Enriqueta, Gelasio, URW Classico) are not committed; only their outlines
appear in the SVGs.

## Limits

- Every reconstruction is labelled `reconstruction: true`. The substitute typefaces are stand-ins, and
  their colours are approximations from web rasters.
- The Vancouver/Richmond search covered every archived vrhb.bc.ca PDF and Word file plus web searches. No
  vector turned up, and none of the documents is a full annual report.
- The search for South Fraser 1998–1999 print material found no vector: the board manual and the
  strategic-priorities cover survive only as thesis scans.
