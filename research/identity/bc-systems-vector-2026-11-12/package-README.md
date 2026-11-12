# BCSC - British Columbia Systems Corporation
## 1983 geometric vector reconstruction

Created 12 November 2026 for Ahmad Jalil from the selected PofBC gallery source.
This is a modern reconstruction of the published BCSC mark, not an original
corporate vector master or a verified set of historical brand specifications.

## Main files

- BCSC_1983_Reconstructed.svg - black mark on a transparent background; primary editable file.
- BCSC_1983_White.svg - white mark on a transparent background.
- BCSC_1983_White_on_Black.svg - the white mark with a black background.
- BCSC_1983_Vector.pdf - two vector pages: black/transparent artwork on the first page; white/black on the second.
- BCSC_1983_Black_4800px.png - transparent black PNG, 4800 pixels wide.
- BCSC_1983_White_4800px.png - transparent white PNG, 4800 pixels wide.
- BCSC_1983_Preview.png - white-on-black preview.
- BCSC_1983_Comparison.png - original scan, aligned reconstruction and difference overlay.
- Reconstruction_QA.json - recorded alignment, raster-comparison metrics and structural checks.
- source/build_bcsc.py - the complete manually authored geometric model and export script.
- reference/BCSC_1983_Source_Scan.png - unchanged gallery reference, included for comparison.

## Construction decisions

The four letters are actual editable vector paths, not a raster inside an SVG
and not an automatically traced pixel contour. No font is required for the logo.
The upright B, C and S were rebuilt with straight edges and short quadratic
corner joins, then given a common 30-degree italic shear. A single C master is
used twice and expanded into separate paths for straightforward editing.

The reconstruction preserves the B's narrower upper bowl, its two offset
rectangular counters, the C's characteristic middle elbow and thick lower stem,
and the S's thin upper-left and heavy lower-right strokes. Letter advances and
spacing were measured against the supplied scan. Cap line and baseline are
level in the deliverable. The small downward tilt in the original is treated as
scan distortion.

The design model uses an arbitrary cap height of 224 units. Corner softness,
30-degree slant and regularized dimensions are reconstruction decisions. No
historical typeface, corporate construction grid, original production radius or
colour specification has been verified. Black and white reflect the supplied
monochrome specimen.

## Comparison and validation

The proof sheet applies one common alignment to the entire reconstructed mark:
x = design_x + 21; y = design_y + 25.3 + 0.0125 * x.
This restores the reference's scan tilt only for the comparison. The downloadable
SVG itself retains a horizontal baseline. Individual letters were not locally
warped to force a match to scanner defects.

At the reference size of 1168 x 288 pixels, white-foreground masks were compared
using source luminance > 140 and rendered luminance > 127. The intersection over
union is approximately 94.8%; the symmetric median boundary distance is 1 pixel
and the 95th percentile is approximately 2.83 pixels. These are agreement metrics
against one threshold of a microfiche scan, not percentages of historical
accuracy. Scan softness and local deformation limit any such comparison.

Visual review checked the B counters, C elbows, S openings, slant, proportions
and spacing. Each logo SVG contains four paths and zero image or text elements.
The PDF has two pages and zero embedded raster images.

## Sources and provenance

Selected gallery entry:
https://projects.ahmadjalil.com/PofBC/?layer=boards&view=gallery&logos=collected-bc-systems-corporation&mark=source-bc-systems-corporation-bc-systems-1983-logo-png

Exact raster reference:
https://projects.ahmadjalil.com/PofBC/identity-collected/bc-systems-corporation/bc-systems-1983-logo.png

Underlying annual report: British Columbia Systems Corporation annual report
1982-83, cover (PDF page 1), hosted by Internet Archive:
https://archive.org/details/micro_IA40243510_1370
https://archive.org/download/micro_IA40243510_1370/micro_IA40243510_1370.pdf

The gallery metadata identifies this image as an original annual-report crop.
The 31-page PDF was also inspected; the cover contains the corresponding mark.
The original font could not be established from the accessible evidence.

Reference SHA-256: ae9e1d9e350817d995b15234a971ff35d7c7e1e0310d801444892637d4acf83b

## Rebuilding

Use Python 3.10 or newer. Install source/requirements.txt, then run:

    python source/build_bcsc.py

When run from the delivered package, the script writes new exports and checks
into the package's regenerated/ directory. It does not alter the supplied
original SVG files. DejaVu Sans is used for comparison-sheet labels when present;
the script falls back to a bundled Pillow font if necessary. Logo paths have no
font dependencies. No network access is used for rebuilding.

The source image remains separate from the editable logo artwork. Original
identity and trademark rights remain with their respective rights holders.
