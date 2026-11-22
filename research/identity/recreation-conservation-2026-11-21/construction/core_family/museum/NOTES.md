# BCPM monogram reconstruction

## Deliverable

`museum.svg` is a transparent, monochrome 1000 x 1000 SVG with named groups and custom paths. It has no embedded raster image, font dependency, or automatic contour tracing. `museum.pdf` is the same vector artwork; `museum.png` is a transparent raster preview. The generator is `build_museum.py`.

## Geometry

The design is constructed from a rounded square enclosure, three shared stems, three independently drawn Bezier bowls, a custom filled C curve with horizontal terminals, and two M diagonals. The B/P and C/M relationships are retained; these are not four typeset letters fitted into a box. A small filled connector joins the B/C/P/M intersection without a false white gap. The top B stroke joins the enclosing frame.

## Source

Primary geometry reference: official Department of Recreation and Conservation annual report for 1971, printed in 1972, PDF page 98 (unnumbered museum divider in the DD97 position). Local source: `sources/forgov_1971.pdf`. The page's embedded 1698 x 2197 monochrome image is stored upside down and was rotated 180 degrees for inspection. Museum glyph crop bounds in the upright native image: x1183, y750, x1391, y960; crop is 208 x 210 pixels. The glyph bounding box was normalized to 1000 x 1000 for the comparison, with no local warp. `source_forgov_1971_native.png` preserves the original crop, while `source_crop.png` is the enlarged registration image.

Cross-checks: user's larger colour screenshot of the General Administration divider; reverse-ink report-cover screenshot; official museum divider in the 1973 report, PDF page 112. These confirm the same letter construction. The 1973 family plate also shows a changed Fish & Wildlife identity while retaining BCPM.

## Overlay revisions

1. Constructed border, shared stems and B/P bowls; checked against the supplied colour screenshot.
2. Switched to the sharper official monochrome report crop.
3. Rebuilt C as a closed outline to preserve the horizontal terminal cuts.
4. Raised the M apex and realigned both diagonals to match the interior counter.
5. Removed a spurious white gap at the four-letter intersection and a thin upper B/frame gap.
6. Inspected the source/reconstruction side-by-side and the cyan/red overlay.

Overlay colours: cyan is source-only ink; red is reconstruction-only ink; dark overlap is agreement. It is an analysis display, not an alternate logo colour.

## Quantitative QA

Against the normalized monochrome scan: silhouette IoU 0.9055; Dice overlap 0.9504; mean symmetric boundary distance 3.59 normalized pixels (about 0.75 native source pixel); 95th-percentile edge distance 9 normalized pixels (about 1.9 native source pixels). Interior IoU, excluding most enclosure area, is 0.9251. Exact values are in `metrics.json`.

These measure agreement with one raster scan, not fidelity to an unavailable original drawing. The scan has jagged pixel boundaries, slight geometric distortion and print spread. The reconstruction smooths those artifacts and regularizes the enclosure. The original brand's dimensional specification, precise ink colour, designer and introduction date are not established here.
