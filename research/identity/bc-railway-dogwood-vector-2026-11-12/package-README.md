# British Columbia Railway: reconstructed vector logo

Created 12 November 2026 from the supplied references.

## Start here

- **BCR_Logo_White_Lettering.svg**: transparent artwork with the original-style white lettering, for a dark background.
- **BCR_Logo_Dark_Lettering.svg**: transparent artwork with dark lettering, for a light background.
- **BCR_Logo_On_Green.svg**: complete white-lettering version on a green background.
- **BCR_Dogwood_Emblem.svg**: standalone flower emblem.
- **BCR_Wordmark.svg**: standalone three-line lettering, in dark ink.
- **BCR_Vector_Logos.pdf**: three vector pages: green-background logo, dark-lettering logo, standalone emblem.
- **BCR_Reconstruction_Preview.png**: overview of the main artwork and variants.

The PNG versions are convenience exports. The SVG and PDF files contain vector
geometry. All logo lettering is outlined; no font installation is required.

## What was reconstructed

This is a manually constructed remake, not an automatic bitmap trace or a raster
image placed in an SVG. The flower uses two true circles, five individually
authored white petal paths, five distinct green leaf paths, fine dark contours,
and fifteen gold stamen strokes. The natural asymmetry of the reference has been
retained; the petals are not rotated copies of a single generic shape.

Fourteen capital letter shapes were drawn for the three-line wordmark. The
construction preserves its broad, squared curves, shallow B counters, curved R
leg with a vertical terminal, flat-topped A counters, flat internal M crotch and
tight RAILWAY kerning. Repeated characters reuse the same authored geometry.

The principal geometry reference was the supplied railcar photograph
**IMG_7919.jpeg**. The enlarged flower in **IMG_7923.png** provided a useful
secondary check. The supplied smaller flat graphic **IMG_7921.png** has a
different flower construction and proportions; it was not merged into this
five-petal master. The book-cover and advertisement images were cross-checks.

No supplied photographs or third-party logo downloads are embedded in these
deliverables.

## Typeface evidence

**Microgramma Bold Extended** is the best-supported family/style identification.
The British Columbia Railway Historical & Technical Society's *The Cariboo*,
issue 31 (January 1998), describes the post-1972 roadname lettering as
"microgramma bold extended typeface" in the "Painting" section of the flatcar
article. The railway lettering is also discussed in issue 27.

- The Cariboo, issue 31: https://www.cwrailway.ca/sites/default/files/Cariboo/Cariboo%20-%20Issue%2031.pdf
- The Cariboo, issue 27: https://www.cwrailway.ca/sites/default/files/Cariboo/Cariboo%20-%20Issue%2027.pdf

The delivered wordmark contains **custom reconstructed outlines**, not glyphs
extracted from a licensed Microgramma font file. The typeface identification is
better supported than the claim that any particular modern digital cut exactly
matches the original artwork. No authenticated corporate master or brand
standards sheet was used.

## Proportions and colours

The three line widths follow the approximate photographed ratio
**636 : 898 : 759**. The flower disc is close to the total three-line lettering
height, and the complete horizontal artwork is approximately 4:1.

| Component | Reconstruction colour |
| --- | --- |
| Gold disc, centre and stamens | `#F8BF00` |
| Green leaves and background | `#005631` |
| White petals and white lettering | `#FFFFFF` |
| Dark contour and dark lettering | `#15251D` |

These are clean digital reconstruction colours. The supplied images differ in
lighting, printing and reproduction, so these values are **not verified
historical colour specifications**.

## Editing

Open the SVGs in Illustrator, Inkscape, Affinity Designer or another SVG editor.
The emblem, leaves, petals, stamens, centre, wordmark lines and individual
letters have labelled groups or IDs. Counters are true holes using the even-odd
fill rule. The flower's thin outlines and stamens remain editable vector
strokes and scale with the artwork. Expand those strokes if a particular
fabrication workflow requires filled outlines only.

For the white-lettering transparent version, the white text may disappear
against an editor's white canvas. Place a dark rectangle behind it or use the
green-background version to inspect it.

## Reproducible source

The `source` folder contains the manual flower paths and a Python 3 SVG builder.
Run `python source/build_logo.py` from this package to regenerate the SVG files
and construction notes. Only Python's standard library is required for SVG
generation. PNG and PDF exports were made with Inkscape; the combined PDF was
assembled without rasterizing the artwork.

## Checks completed

- Visual comparison with the supplied references and a matched-scale overlay.
- Independent review of the reconstructed lettering and flower details.
- SVG structure checks for raster images, external links, live text and duplicate IDs.
- PDF inspection for raster image objects, plus rendered-page review.

This is a reference-based reconstruction of the five-petal version, not an
authenticated original corporate file.
