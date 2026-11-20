# BC Forest Service - Be Careful - 1960

## What this is

A deliberately reconstructed vector edition of the supplied decal. Geometry is manually authored from design landmarks, using line, quadratic and cubic Bezier segments. The lettering is constructed from reusable custom glyph masters and optical variants. No auto-trace, bitmap contour extraction or raster embedding is used in any SVG, PDF or EPS artwork.

## Files

- `BC_Forest_Service_1960_Master.svg`: primary editable artwork. 43 paths in five named layers; white lettering over a scan-sampled green-grey silhouette; transparent outside the artwork.
- `BC_Forest_Service_1960_Knockout.svg`: single-colour compound path with genuinely transparent lettering. This is useful when the substrate should show through.
- `BC_Forest_Service_1960_Black.svg` and `BC_Forest_Service_1960_White.svg`: knockout variants.
- `BC_Forest_Service_1960_Print.pdf`: vector PDF. No embedded raster images. The page follows the SVG's 1234 x 909 canvas at the conventional 96 CSS pixels per inch; this is not a claim about the original decal's dimensions. Choose the intended print size.
- `BC_Forest_Service_1960_Black.eps`: monochrome vector EPS.
- `BC_Forest_Service_1960_Preview.png`: 2468-pixel-wide white-background preview.
- `BC_Forest_Service_1960_Transparent.png`: 4096-pixel-wide transparent PNG of the knockout artwork.
- `BC_Forest_Service_1960_Review.html`: self-contained, offline comparison with a wipe slider, detail views and a coloured difference map.
- `BC_Forest_Service_1960_Overlap.png`: annotated overview of the geometric comparison.
- `Reconstruction_measurements.json`: exact measurement method and results.
- `Source/`: component SVGs and editable Python construction scripts.
- `Reference/Original_scan.png`: the supplied image, unchanged.

## Editable structure

1. Forest and flames
2. Large B and C
3. Be Careful small lettering
4. Prevent Forest Fires
5. BC Forest Service

Letters are outlined editable vector paths, not live text fields. No font installation is required. The construction scripts preserve the glyph masters, width/height placement, and semantically named silhouette sections for later refinement.

## Typography and reconstruction decisions

The large B and C have an Albertus-like inscriptional structure, but the scan does not establish a specific font, cut, weight or original setting. They are custom masters here. The narrow uppercase lettering is comparable to the Alternate Gothic / condensed sign-lettering tradition; its unusual R leg, A counter and individual widths are deliberately retained. The footer is reconstructed as small humanist lettering. No commercial font files or commercial font outlines are included.

The forest's irregular heights and branch rhythm, the transition into flames, the deep flame valleys, the angled base and the uneven lettering baseline are retained. Print grain, scratches and tiny scan-edge defects are deliberately omitted. The small signature remains the least securely determined portion because of its low source resolution.

Ink colour #525850 is the median sampled inside dark regions of the supplied scan, not a verified original ink or spot-colour specification. Original physical dimensions are unknown.

## Alignment checks

The comparison uses the original 1234 x 909 coordinate system with no affine or projective alignment, rescaling or local warping. Source and rendered artwork are classified as ink when unweighted mean RGB is below 180/255.

- Full ink-shape intersection over union: 97.36%.
- Large B white region: 97.60%.
- Isolated large C white shape: 95.82%.
- Slogan white lettering: 92.30%.
- Small service signature white lettering: 80.39%.
- Symmetric boundary distance, 95th percentile: 2.24 source pixels.

The full-shape score is dominated by solid areas and should not be read as a percentage of historical authenticity. Lettering metrics expose finer differences. A one-pixel edge change has a large effect on very small letters. Differences include intentional smoothing, original print irregularities and residual manual reconstruction differences.

## Historical and type references

- User-supplied scan: B2-02_be_careful_decal_1960(1).png.
- BC Forest Service, Protection Bulletin, No. 3 (1960), printed p. 5, New Protection Decals. The same design is pictured and the text describes decals for vehicle windows and hard hats: https://a100.gov.bc.ca/pub/eirs/finishDownloadDocument.do?subdocumentId=21448
- Monotype, Albertus Nova / Albertus lineage, used as a family-level comparison: https://www.monotype.com/fonts/albertus-nova
- Monotype, Alternate Gothic, used as a condensed-lettering comparison: https://www.monotype.com/fonts/alternate-gothic

## Regenerating geometry

Python 3 is sufficient for the main lettering geometry. Inkscape is used to render and to calculate a vector-only Boolean difference for the knockout edition. Full export/review also uses FontTools, NumPy, SciPy, Pillow and Poppler. Fonts used for comparison-page labels are separate from the reconstructed artwork.

From the package directory:

```sh
python3 Source/silhouette/build_silhouette.py
python3 Source/lettering/build_lettering.py
python3 Source/main/draw_initials_footer.py
python3 Source/main/build_package.py
python3 Source/main/build_review.py
```

Rebuilt exports appear under `Source/exports/`. The scripts never use a raster image to generate an SVG path. The original scan is read only by the review/measurement script.

Prepared 20 November 2026.

## In this repository

Kept: this README, `Reconstruction_measurements.json`, the master, knockout, black and white SVGs,
the vector PDF and EPS, and `Source/` (component SVGs, glyph masters and the construction scripts).

Left out: `Reference/Original_scan.png`, the preview, transparent and overlap PNGs, and the review
HTML. `Source/main/build_review.py` reads the scan, so it will not run here without it.

The Posters view (`?view=posters&poster=be-careful`) shows `src/posters/forest-service/be-careful.svg`:
the master with every id prefixed `bcc-` and its `<title>` re-worded. The date rests on BC Forest
Service, Protection Bulletin No. 3 (1960), p. 5, cited above.

