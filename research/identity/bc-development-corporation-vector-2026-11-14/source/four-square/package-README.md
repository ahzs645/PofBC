# The Development Corporation — vector reconstruction

Four clean vector versions reconstructed from the four supplied monochrome references.

## Files to use

| File stem | Reference | Contents |
|---|---|---|
| `development-corporation-serif-stacked` | `460346.png` | Serif lettering above the thin, sharp-corner four-panel symbol |
| `development-corporation-symbol` | `494945.png` | Standalone sharp-corner symbol |
| `development-corporation-sans-stacked` | `901351.png` | Heavier lettering above the rounded four-panel symbol |
| `development-corporation-sans-horizontal` | `901352.png` | Rounded symbol to the left of the three-line name |

`svg/` contains transparent, tightly framed artwork. Each master has a black
version and a white version with the suffix `-white`. The white versions are
intended for placement on a dark background. All lettering is outlined as
vector paths, so no font installation is required.

`pdf/` contains individual vector PDF versions and a combined four-page PDF in
the order shown above. The PDF pages have no bitmap logo content.

`reference-aligned/` contains black SVGs on the exact original canvas sizes.
These are useful for comparing against the supplied images. Their artwork is
identical to the tightly framed files; only the artboard changes.

`proofs/` contains a preview sheet and comparison images. The comparison images
are raster proofs; use the SVG or PDF files for production.

`source/` contains the reconstructed lettering, the geometric frame settings,
and the assembly script for rebuilding the SVG set.

## How these were made

The artwork was rebuilt from intentional geometric shapes and manually authored
letter outlines. The source images were used to measure placement, proportions,
weight and distinctive details. No bitmap autotrace or raster image embedded in
an SVG was used.

Each frame is a compound path with a transparent opening. The individual cells
are equalized and aligned within each version, while preserving differences
between the versions. The serif symbol has square corners and lighter horizontal
borders. The sans-serif symbols have heavier borders, rounded corners and much
tighter gaps. A single generic symbol was not stretched into all four versions.

The lettering retains source-specific details, including the open lower bowls
of the serif P, the serif terminals, the different weights in the sans-serif
layouts, and the small terminal projections in the horizontal version.

## Editing

Open an SVG in an editor that supports SVG paths. The top-level `artwork` group
contains separate `lettering` and `four-panel-symbol` groups. Each panel and each
letter remains a separate vector object. Change the fill of `artwork` to recolour
the whole logo. The interiors of the panels and letter counters are transparent,
so they will show the background correctly.

Scale proportionally to preserve the reconstructed layout. The extra whitespace
in the original wide PNGs has been removed in the main SVG files. Use the
reference-aligned files when you need the original canvas dimensions.

## Fidelity and source limits

These are cleaned reconstructions from one-bit raster references, not recovered
official master artwork. The historical font names and exact original outline
geometry have not been authenticated. Small irregularities caused by raster
sampling have deliberately been regularized; distinctive letter construction,
spacing and the differences between the supplied layouts have been preserved.

The proof overlays use cyan for source-only edges, magenta for vector-only
edges and dark ink where the two overlap. Edge fringes can result from both the
intentional cleanup and the original pixel grid.

Source images: the four PNG files supplied with the request. No unprovided
historical dates, official specifications or typeface attribution are asserted.
