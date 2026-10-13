BRITISH COLUMBIA FOREST SERVICE
Reconstructed vector artwork
============================

START HERE
----------
Open bc-forest-service.svg for the editable vector master.
Use bc-forest-service.pdf or bc-forest-service.eps for vector interchange.
The PNG files are convenience previews, not the vector master.

This package reconstructs the supplied oval emblem using geometric ellipses,
custom outlined letters and explicitly authored Bezier and polygon paths.
It is not an automatic bitmap trace. The SVG, PDF and EPS artwork contains
no embedded raster images.

This is an independent reconstruction from the supplied reference, not an
authenticated official vector master. Letter contours, small landscape
features, spacing and colours are visually reconstructed. The oval geometry
and cloud bands have been regularized; photographic texture and small image
distortions were not reproduced. It is a vector rebuild of the original
reference, not an exact conversion of the AI-generated PNG preview.

MAIN FILES
----------
bc-forest-service.svg
  Main layered vector, with transparent space outside the oval.
  All lettering consists of individual custom paths; no font is required.

bc-forest-service-white.svg
  The same vector with a separate white background layer.

bc-forest-service.pdf
  Single-page vector PDF, with no embedded raster images or fonts.
  Artboard: 200 x 253.7815 mm. Scale proportionally for other sizes.
  Flat RGB colours; not a CMYK or spot-colour production specification.

bc-forest-service.eps
  Vector EPS export for workflows that require PostScript artwork.

bc-forest-service-transparent.png
  Raster convenience export, 3000 pixels high, with alpha transparency.

bc-forest-service-preview.png
  White-background raster preview, 1800 pixels high.

reference-comparison.png
  The supplied image beside the rebuilt vector, at matching proportions.
  This comparison sheet is a raster image, not production artwork.

COMPONENT FILES
---------------
components/evergreen.svg
  Separate central evergreen, including its trunk and interior details.

components/central-landscape.svg
  Separate oval-clipped scene: tree, mountains, sky, lake and foreground.

components/oval-and-lettering.svg
  Separate outer oval, gold rules and lettering, without the landscape.

EDITING
-------
Named top-level layers separate oval geometry, landscape, upper lettering,
and lower lettering. Within the landscape, named groups separate the sky,
mountains, distant forest, lake, ground and main evergreen.

Ellipses and cloud-band rectangles remain simple geometric objects.
The main tree has separate black silhouette, green infill, trunk and needle
cut paths. Mountains, rock shadows, snow breaks, ripples and ground details
remain separate editable vector objects.

Letters are custom outline drawings, not live text. They can be selected,
scaled, moved or recoloured independently. No font files are included or
needed. New wording requires reusing/redrawing glyphs and adjusting placement;
this package is not an automatic font or full-alphabet system.

The central scene uses a standard SVG ellipse clipping path. Keep that clip
when moving the scene or exporting the badge as a whole.

COLOURS
-------
Badge green:     #00381E
Gold:            #E6C786
Scene green:     #005737
Sky / lake blue: #0FB4E0
Black outline:   #080C0A
Snow white:      #FFFFFF
Rock grey:       #8D8F8D

These are flat RGB approximations of the supplied image, not verified
institutional colour specifications or prescribed print spot colours.

REBUILD SOURCE
--------------
source/rebuild.py
  Pure-Python standard-library SVG generator. It contains explicitly authored
  path geometry and the custom capital-letter drawings.

source/letter-layout.json
  Per-letter position, angle and dimensions. These are placement measurements,
  not traced glyph contours.

source/palette.json
  Human-readable record of the colour palette. To change generated colours,
  edit PALETTE in rebuild.py; the script then rewrites palette.json.

Run from any directory with Python 3.9 or newer:
  python source/rebuild.py

The script regenerates the five SVG files and palette.json. PDF, EPS and PNG
exports are separate. Example Inkscape commands, run from the package folder:
  inkscape bc-forest-service.svg --export-type=pdf
  inkscape bc-forest-service.svg --export-type=eps
  inkscape bc-forest-service.svg --export-type=png --export-height=3000

CHECKS PERFORMED
---------------
- SVG XML parsed successfully; no embedded images, live text, font resources,
  scripts, external resources or SVG filters.
- Twenty-eight individually positioned outlined letters checked against
  FOREST SERVICE and BRITISH COLUMBIA.
- Main artwork rendered with Inkscape and CairoSVG.
- Exported PDF rendered with Poppler and visually inspected; it contains one
  page, no raster images and no embedded fonts.
- EPS independently rendered with Ghostscript.
- Transparent PNG has an alpha channel; the white-background export is opaque.
- ZIP integrity checked; no font files included.

See source/validation.json for the structural checks. This is a design rebuild,
not a certification for embroidery, cutting or very-small-size reproduction.
