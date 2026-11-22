# British Columbia Ferry Commission — reconstructed vector

## Main files

- `BC_Ferry_Commission_Reconstructed.svg`: the editable master, transparent background, original 841 × 895 proportions.
- `BC_Ferry_Commission_Reconstructed.pdf`: a vector PDF export of the master.
- `BC_Ferry_Commission_Reconstructed.png`: a transparent 3364 × 3580 preview rendered from the SVG.
- `BC_Ferry_Commission_Comparison.png`: original, vector rendering, and contour overlay.
- `components/`: separate shield and lettering SVGs.
- `comparison-metrics.json`: measured checks and file fingerprints.

## Provenance

This file is a reconstructed logo, not a recovered original full-colour master.

Primary visual reference: https://www.bcferrycommission.ca/wp-content/uploads/2021/06/BCFC_full-colour_pos.png

The supplied news release was: https://www.bcferrycommission.ca/download/news-release-commissioner-approves-four-new-major-vessels/

Native sun-ray, sun-disc, and crown curves came from reverse specimen G on page 3 of the Province of British Columbia's corporate identity emblems guide: https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/celebrating-british-columbia/symbols-of-bc/bc-emblems-set.pdf

The source page was recovered from the existing PofBC official sample PDF: https://raw.githubusercontent.com/ahzs645/PofBC/main/research/identity/arms-acquisition-2026-11-16/assets/provincial/bc-1987-monochrome-official-sample.pdf

The reverse artwork's flag and wave gaps differ from the colour specimen. The final SVG therefore retains its native sun/crown curves and reconstructs the colour fields and highlight/shadow layers against the PNG. The perimeter was fitted as two smooth cubic curves from the PNG's coverage boundaries.

## Editable structure

The shield contains named groups for white fields, the Union flag, ocean waves, sun and rays, and antique crown. The upper and lower wording are separate layers. All 30 letters are separate named paths. Their original size, rotation and spacing are retained. The font has not been identified: these are reconstructed letter outlines, not substituted live text.

There are no bitmap images, linked assets, fonts, filters, or scripts in the master SVG. Colours use the published PNG's RGB values; no print spot-colour specification has been inferred.

## Checks

- SVG: 248 paths; zero image elements and zero live-text elements; unique IDs.
- PDF: 1 page; 238 vector drawing objects; zero embedded images and zero font resources.
- Whole-logo silhouette overlap: 99.758% at the reference resolution.
- Mean absolute RGB difference in the occupied artwork neighborhood: 2.809 on a 0–255 channel scale, including antialiasing.
- Source-measured perimeter RMS boundary fit: 0.060 pixels; maximum 0.177 pixels at the sampled rows.

The overlay and enlarged component review were used to check crown highlights, wave joins, ray junctions, letter counters, and source placement. Small edge differences remain because a finite-resolution PNG cannot establish every original control point. The source-native sun/crown curves and reconstructed details are identified separately above.

Open the master SVG in a vector editor to edit paths or spacing. The lettering is outlined; changing the words requires editing or replacing those individual paths.
