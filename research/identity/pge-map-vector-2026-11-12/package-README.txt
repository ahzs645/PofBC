PGE - SHARED-ASSET SOLID VARIANTS
================================

Recreated from the supplied green-livery reference, 12 November 2026.
This is a reference-based reconstruction, not an original archival master.

MAIN FILES
PGE-solid-white-panel.svg / .pdf
  Isolated white folded panel with black BC and PGE artwork.
  Exterior is transparent in SVG and PNG; the white panel is opaque artwork.

PGE-green-livery.svg / .pdf
  The same emblem on two green fields separated by a white horizontal band.

PGE-shared-template.svg
  Original striped version, new solid emblem and green livery together.
  Every BC and PGE shape is defined once in <defs> and reused through <use>.
  Editing a shared path in this template updates all its instances.

PGE-shared-geometry.json
  Canonical path data, hashes, and variant transforms/colors.

PGE-striped-original.svg
  Unchanged copy of the earlier standalone striped SVG.

PNG exports, a preview, a source comparison, validation results, and the
construction scripts are also included.

WHAT IS SHARED
The BC mainland, western island, six coastal cutouts, and P, G and E letter
paths are identical to the earlier vector. The new standalone SVGs contain
those exact paths directly, for portability; the family template defines
each asset once. There are no embedded images or live font dependencies.

WHAT CHANGES
The upper stripe grid is omitted, the panel becomes white, and the map and
lettering become black. Map size/placement and one shared wordmark affine
transform match the new reference. The panel uses the same folded-polygon
construction with a slightly reduced lean. No individual letter was redrawn.
The solid version also has a separate white coastal separator to match the
continuous gap beside Vancouver Island in this reference. This editable
overlay leaves every shared map path unchanged. Hide the solid-coastal-
treatment group to show only the exact shared coastal cutouts.

COLOR AND REFERENCE LIMITS
Upper green: #728B76. Lower green: #345135. White: #FFFFFF. Ink: #000000.
The greens are approximate screenshot samples, not verified paint standards.
The screenshot is only 151 x 167 px. The overall map follows the shared asset,
with a separate coastal-gap treatment. The small yellow curve and photographic artifacts are not
part of the isolated emblem or the clean livery presentation.

EDITING
The standalone SVG groups are named for the panel, map and lettering. Keep
the map's black shapes and white coastal cutouts together when transforming.
The letters are outlined, with a true even-odd compound counter in the P.
The template's neutral background is a separate preview-background object.

REGENERATION
Run recreate_pge_variants.py with reconstruct_pge.py beside it.
Dependencies: Pillow, NumPy, svgpathtools, ReportLab and PyMuPDF.
Primary artwork is generated from paths alone. Reference images are optional
and only used for comparisons; place them under upload/ if needed.
