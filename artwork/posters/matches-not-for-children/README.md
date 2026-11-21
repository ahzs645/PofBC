# BC Forest Service — MATCHES ARE NOT FOR CHILDREN!!

## Revision 4: paint and broken match

The paint background has been recomposed and the child’s broken hip junction reconstructed. The central orange column, lower paint remnants and warm yellow-field marks receive this pass; the crack now has a torn shoulder, irregular thin split and tapered splinters. White reserve, headline, seal and supporting lettering retain their earlier construction.

The SVG and PDF remain native vector artwork with no embedded bitmap, live text or raster filter. The geometry is deliberately constructed; the photograph is used for visual reference and diagnostic masks, not automatic contour tracing.

## Start here

| File | Purpose |
| --- | --- |
| `BCFS_Matches_Reconstructed.svg` | Complete current textured poster; named editable layers |
| `BCFS_Matches_Clean.svg` | Same drawing and white reserve with simplified paint fields |
| `BCFS_Matches_Reconstructed.pdf` | One-page scalable vector PDF |
| `BCFS_Matches_Preview.png` | 2000 × 2800 raster preview |
| `BCFS_Interactive_Review.html` | Offline V3/V4 wipe, blend, paint/crack overlays and zoom |
| `BCFS_Reconstruction_Comparison.png` | Photograph, V3 and V4 full-poster comparison |
| `BCFS_Paint_Overlay.png` | Broad orange-field placement diagnostic |
| `BCFS_Paint_Details.png` | Matching enlarged paint crops |
| `BCFS_Child_Crack_Details.png` | Photo / V3 / V4 broken-joint comparison |
| `BCFS_Child_Crack_Overlay.png` | Local ink mismatch overlay |
| `BCFS_Paint_Background.svg` | Separately editable revised paint |
| `BCFS_Child_Crack.svg` | Local broken-joint component with paper-coloured cutout |
| `BCFS_Matchstick_Illustration.svg` | Complete updated matchstick drawing |
| `BCFS_White_Reserve.svg` | Retained Revision 3 pale reserve |
| `BCFS_White_Edge_Residue.svg` | Retained sparse pigment deposits inside reserve |
| `BCFS_Headline.svg`, `BCFS_Forest_Service_Oval.svg` | Separate existing lettering and emblem |
| `review/Revision_4_Report.md` | Findings, method, measurements and remaining limits |
| `review/Paint_Measurements.json`, `review/Joint_Measurements.json` | Current fixed-reference numerical evidence |
| `review/history/` | Historical reports, vectors and comparison boards |
| `source/` | Current assembly, editable construction sources and supplied photograph |

## How to read the diagnostics

Paint analysis retains the earlier mask of 698,156 eligible pixels. Broad orange-field overlap changes from 75.54% to 78.67%; raw RGB fit residual changes from 13.25 to 11.28 levels per channel. These are photo-fitting diagnostics, not whole-poster accuracy or authenticity scores. Paint grain is reviewed visually as well.

The regional result is mixed: the lower scumble and right-band orange-placement scores regress even while average RGB residuals improve. The exact placement of those stronger deposits, the upper-central broken red spur and some thin scrapes remain refinement targets. The report keeps those limitations explicit.

Teal means a classified orange/ink area exists in the photograph only; magenta means it exists in the vector only. Paint and ink overlays use different explicit masks. The crack overlay is limited to its small context box. The report contains fixed threshold sensitivity and wider joint context results.

The comparison plane is estimated at 1000 × 1400 pixels. Original physical dimensions, calibrated inks, the historical seal typeface and signature attribution remain unverified. The PDF canvas has no bleed or printer-specific profile. Fine grain, transparent pigment and concealed details are still interpreted.

## Rebuild the delivered master

The finished SVG needs no fonts or Python to open. To regenerate it from the included final components:

```bash
python3 -m pip install -r source/requirements.txt
python3 source/crack_joint.py
python3 source/rebuild_poster.py
```

The builder reads `paint_v4.svg`, `paint_v4_clean.svg`, the retained `reserves_v3.svg`, `edge_residue.svg`, `emblem_v2.svg`, `signature_v2.svg` and the custom headline construction. It does not read the photograph. DejaVu Sans Bold and DejaVu Serif Bold are used to outline tiny supporting captions; their paths are declared in the builder. Save direct SVG edits before regeneration, which overwrites the master files.

The more expensive paint construction is in `source/paint-source/`; final component files are already supplied. The local cracked-junction component is applied after the base figure and replaces the removed old hip-star strokes. Existing reserve construction sources remain available for editing.

To export and reproduce the current analysis:

```bash
inkscape BCFS_Matches_Reconstructed.svg --export-type=png --export-width=2000 --export-filename=BCFS_Matches_Preview.png
inkscape BCFS_Matches_Reconstructed.svg --export-type=pdf --export-filename=BCFS_Matches_Reconstructed.pdf
python3 source/analyze_revision4.py
python3 source/build_review_html.py
```

Analysis reads the retained reference photograph, unchanged fixed paint mask and immutable V3 artwork from this package. The HTML includes every image and SVG asset; download it and open it locally. Embedded asset identity and JavaScript syntax were checked, but browser interaction was not exercised in this environment.

Current checks are recorded in `review/Vector_Validation.json` and `review/Source_Rebuild_Check.json`. Earlier white-edge reports are historical; no new white-contour improvement is claimed by Revision 4.

## In this repository

Kept, each byte for byte as supplied except this README, which has this section added: the
textured master `BCFS_Matches_Reconstructed.svg`, the clean edition `BCFS_Matches_Clean.svg`, the
component SVGs (centennial mark, child crack, oval seal, headline, matchstick illustration, white
reserve and edge residue), `source/` (the construction and analysis scripts, the smaller component
SVGs and the fitting records), and the measurements and notes under `review/` (its JSON and Markdown).

Left out: the supplied photograph and the crack reference crop (`source/Supplied_Photograph.jpg`,
`source/Crack_Reference_Crop.png`), every PNG (the preview, comparisons, overlays, masks and review
boards, all of which carry or are measured against the photograph), the print PDF (3.7 MB, an export
of the master), `BCFS_Interactive_Review.html` (26 MB, it embeds the photograph), `review/history/`
and the 11 MB paint SVGs `BCFS_Paint_Background.svg` and `source/paint_v4.svg` (the same file; the
paint is the master's `#painted-background` layer) and the superseded `source/paint_v2.svg`.
Without `paint_v4.svg`, the photograph and the outlining fonts, `source/rebuild_poster.py` and the
analysis scripts will not run here; they are kept as the record of how the drawing was made.

The Posters view (`?view=posters&poster=matches-not-for-children`) shows
`src/posters/forest-service/matches-not-for-children.svg`, made from the master by `web_copy.py`:
every id prefixed `mnc-`, the Inkscape layer labels kept as `data-label`, the title and
description reworded, and the paint's outlines simplified within a fifth of a unit, rounded to a
tenth and written as relative moves. No path outside the paint is changed. It is 4,197,902 bytes in
place of 11,329,249 (about 0.9 MB served compressed), and rendered in Chromium at 2000 × 2800 it
differs from the master by more than 16 levels in 0.03% of pixels. The shelf card is
`matches-not-for-children.thumb.jpg`, 333 × 466, made from that render. The seal is also shown on
its own in Internal Logos, as `src/internal/forest-service-one-ink-oval.svg`:
`BCFS_Forest_Service_Oval.svg` with its title and description reworded.
