# British Columbia Assessment Authority - 1982 logo reconstruction

This package recreates the logo from the supplied **bc-assessment-map-1982-letterhead.png** scan. It is a new vector reconstruction, not a recovered original production file. The address, date, handwriting and unrelated scan marks are excluded from the artwork.

## Main files

| File | Purpose |
| --- | --- |
| bc-assessment-1982.svg | Full logo, black wordmark and gray map with black keyline; transparent background. Recommended editable master. |
| bc-assessment-1982-black.svg | Full logo in solid black; transparent background. |
| bc-assessment-1982-symbol.svg | Separate map symbol in gray and black. |
| bc-assessment-1982-symbol-black.svg | Separate map symbol in solid black. |
| bc-assessment-1982.pdf | Full gray-map logo as a vector PDF. |
| bc-assessment-1982-black.pdf | Full black logo as a vector PDF. |
| bc-assessment-1982.eps | Legacy vector interchange copy of the gray-map logo. |
| bc-assessment-1982-transparent.png | 4,240 x 1,184 transparent PNG for convenient raster placement. |
| bc-assessment-1982-preview.png | 2,120 x 592 preview on white. |
| bc-assessment-1982-comparison.pdf | Two-page reference and overlay review. |
| bc-assessment-1982-comparison.png | Single-image comparison sheet. |
| source-reference.png | The unchanged supplied letterhead scan. |
| source/ | Geometry coordinates, original-coordinate vector, and typography comparison notes. |
| validation.json | Structural verification of the vector artwork and print PDFs. |

## Reconstruction decisions

### Map

The mainland is an angular compound polygon with a true transparent central hole. The three detached islands are separate polygons. The main boundary uses 11 outer and 11 inner structural vertices; the islands use four, five and five vertices. These simple structural paths replace the uneven photocopy edges without introducing detailed modern geographical boundaries.

The scan shows a broken screened fill surrounded by a black edge. The principal version interprets that treatment as a smooth **#646464** gray fill with a **1.25 source-pixel black edge**. This is an estimated appearance from the scan, not a verified original ink specification. The all-black version offers a single-color treatment of the same geometry.

### Lettering

The words were rebuilt from **Nimbus Sans Bold** contours after comparisons with Liberation Sans Bold, DejaVu Sans Bold, Noto Sans Bold, Open Sans Bold and Open Sans ExtraBold. Nimbus Sans Bold was the closest of these tested candidates. Its identification as the original historical typeface is **not established**.

A shared scale and modest weight expansion were applied to the font-derived paths. Repeated letters retain identical contours and scale; their placements are fitted to the supplied lettering. All 34 visible letters are outlines. No installed fonts are required to display the SVG or print PDFs. The weight adjustment is retained as an editable vector stroke on the glyph paths.

### Alignment

The supplied letterhead has a slight rising text baseline and local print/scan distortion. Final artwork has a mild **+0.24-degree global deskew**. The source-coordinate copy in `source/` preserves registration for the overlay measurements. The reconstruction retains the original broad left/right layout and the map's placement between the two wordmark sections.

## Validation and comparison

The full gray SVG contains 42 paths (34 letters and eight map fill/keyline paths). The full black SVG contains 38 paths. The symbol-only SVGs contain eight and four paths respectively. None of the SVG artwork contains embedded raster images or live text. The main print PDFs were reopened and verified to contain vector drawings, zero embedded images and zero font dependencies. SVG and PDF renderings were visually reviewed.

The overlay uses cyan for the reference silhouette, magenta for the reconstruction and dark ink for agreement. The reference map's screened interior was filled **only for the silhouette comparison**; this prevents the source halftone pattern from dominating an edge comparison. Text comparison retains the source print irregularities. Comparison is performed before the final deskew so the geometry stays registered with the source.

The main map's sampled reconstructed edge is about **0.58 source pixels** from the measured source edge on average, with a 95th percentile of **2 pixels**. In the separate text comparison, about **99.9%** of left-wordmark source ink and **99.8%** of right-wordmark source ink falls within one source pixel of the rebuilt text. These are diagnostic alignment measures, not proof of an exact original font or print specification. The raw text overlap is lower because scan defects and jagged edges were deliberately removed. See the numeric files in `source/` for the underlying values.

## Editing

Open the SVG in a vector editor. Map objects are grouped under `bc-map`; the two wordmark sections are grouped separately. For recoloring, select the corresponding vector paths. The SVG background and mainland hole are transparent. SVG and PDF artwork may be scaled without pixelation; the PNG files are convenience previews.

## Source

User-supplied file: `bc-assessment-map-1982-letterhead.png`, 1,605 x 450 pixels. The visible letterhead date is May 1982. No external artwork or original font file has been substituted for the supplied reference.

Source SHA-256: 7146de10d17456a300e75ec521556a5ca756cba08132d8974b143ff7bd8654a7

Prepared 27 November 2026.
