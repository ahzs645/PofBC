# Prevent Forest Fires — constructed vector recreation

## Revision 6: repeated overlap and visual refinement

This delivery continues from the frozen revision-5 files. Branches, timber,
ground openings, flame folds and lettering were repeatedly rendered, compared
with the supplied photograph, edited as vector construction, and reviewed again.
Rejected experiments remain in the history. The final comparison uses all
accepted modules together, so it includes any interactions between layers.

The main changes are more varied canopy boughs and clearer branch attachments,
better leaning-trunk/root proportions, corrected fallen-log faces and curved
branches, connected ground gaps, unequal curved flame peaks, and closer script,
headline and selected footer lettering. Exposed lower wood has a separate
pale-gold colour so it no longer uses the vivid sky/flame yellow.

### Fixed dark-ink overlap

| Area | Revision 5 | Revision 6 | Change |
|---|---:|---:|---:|
| Upper trees | 74.04% | 76.08% | +2.04 percentage points |
| Lower woodland | 78.66% | 80.60% | +1.94 percentage points |
| Lower trunks and logs | 70.73% | 73.02% | +2.29 percentage points |
| Roots and ground | 88.83% | 90.28% | +1.45 percentage points |

These numbers measure dark-ink intersection-over-union at the fixed reference
alignment. They are not percentages of historical accuracy or a 0–10 visual
rating. The trunks/logs and dense ground are shown separately. The analysis
report supplies counts, precision, recall, sensitivity and edge-distance checks.
The iteration review adds script, headline and local orange-field measurements,
accepted/rejected decisions, and the reasons colour review affected acceptance.

## What the artwork contains

The master is an editable reconstruction of the supplied British Columbia
Forest Service poster. Trees, woodcut marks, flame shapes and letters are
constructed vector geometry. No mask was converted into a path and no bitmap
is embedded in any artwork SVG or the print PDF. There is no automatic tracing.

Some letter positions, proportions and brush weights were calibrated within
bounded ranges using the already constructed glyph masters. This numerical
fitting is disclosed in the iteration report. The result remains editable
curves, without a live-font dependency. The artwork builder does not read the
source photograph or any diagnostic raster.

The exact historical typefaces, artist, date, original print dimensions and
ink specifications are not identified by this reconstruction. Fine needle
edges, torn grain, photographed print wear and some letter contours remain
interpreted. This is not presented as a pixel-identical archival facsimile.

## Main files

| File | Use |
|---|---|
| `artwork/BC_Forest_Service_Reconstructed.svg` | Complete layered, editable master. |
| `artwork/BC_Forest_Service_Illustration.svg` | Trees, flames and woodland without lettering. |
| `artwork/BC_Forest_Service_Lettering.svg` | Lettering and its small sparks on a transparent background, in the same registration. |
| `artwork/BC_Forest_Service_Print.pdf` | One-page vector PDF. |
| `artwork/BC_Forest_Service_Preview.png` | 3000 × 4320 convenience render of the SVG. |
| `review/BC_Forest_Service_Refinement_Overview.png` | Source / delivered revision 5 / revision 6 at equal scale. |
| `review/BC_Forest_Service_Iteration_Review.md` | Refinement decisions, exact combined results and method limitations. |
| `review/BC_Forest_Service_Iteration_Metrics.json` | Exact new diagnostics and selected source states. |
| `review/BC_Forest_Service_Tree_Details.png` | Large aligned canopy and lower-timber views. |
| `review/BC_Forest_Service_Remaining_Details.png` | Focused source / previous / current views of corrected shapes. |
| `review/BC_Forest_Service_Tree_Overlap.png` | Shared, missing and extra dark ink. |
| `review/BC_Forest_Service_Tree_Blend.png` | 50% photograph/vector colour overlays. |
| `review/BC_Forest_Service_Overlap_Viewer.html` | Self-contained version, region, opacity and mask controls. |
| `review/BC_Forest_Service_Overlap_Analysis.md` | Fixed primary tree method, sensitivity, counts and reproduction commands. |
| `review/BC_Forest_Service_Flame_Overlap_Analysis.md` | Separate fixed yellow-ribbon checks and scope. |

Additional JSON/CSV tables and labelled comparison boards are included. The
source photograph appears only in review and analysis material.

## Canvas and editable layers

The SVG viewBox is **1000 × 1440**. The SVG and PDF page is **250 × 360 mm**, a
convenient output size rather than a claim about the historical print. Scale
proportionally to another size. The PNG is approximately 305 ppi at this size.
No bleed or crop marks are added.

1. Yellow field.
2. Conifer canopy.
3. Orange flame field and yellow tongues.
4. Burnt trunks, fallen logs, roots and woodcut marks.
5. Prevent script.
6. FOREST FIRES headline.
7. Lower slogan and service credit.

Layers use Inkscape labels and standard SVG groups. Other vector editors may
show groups instead of named layers. Timber highlights use vector clipping
where needed to keep grain inside the wood. All lettering is outlines; wording
changes require editing or constructing letter paths rather than typing text.

## Working colours

| Role | sRGB |
|---|---|
| Dark ink | `#242332` |
| Sky and flame yellow | `#F5E928` |
| Orange field | `#F77913` |
| Ivory letters and keylines | `#F5F0D7` |
| Exposed lower wood | `#ECD878` |

The pale-gold wood is an interpretive colour choice informed by the photograph.
A separate colour-only trial confirmed that its geometry was unchanged.
These five working colours are not certified historical spot inks. Small
designed bark variations may use additional colour values. The PDF retains RGB
colour; print production can apply a device-specific conversion.

## Review method

The photographed artwork is rectified once using the visible corners
(248,27), (1183,29), (1207,1423), (216,1427), to 1000 × 1440. The surrounding
photographed surface is excluded. Both before/after renders are 3000 × 4320
and reduced once with Lanczos sampling. No individual trees or reference regions
are locally warped. The primary regions, exclusions and thresholds are held
unchanged from the prior delivery. Local script/headline/footer scopes are
recorded before their respective edits.

Colour review accompanies each meaningful geometry iteration. Dark-ink masks
alone cannot distinguish a pale-gold wood face from an orange opening. Thin
ivory outlines are measured separately from headline fill. Orange-field regions
contain nearby lettering and bark, so their scores are not isolated-flame scores.
Overlapping regions are not added or averaged into a global accuracy rating.

The HTML viewer retains its established controls. Its embedded images and
JavaScript were statically checked; this revision does not claim a successful
live-browser UI test. PNG comparison boards provide an independent review route.

## Rebuild the artwork

Python 3 and the standard library are enough to regenerate the SVGs:

```bash
python3 source/build_poster.py --output-dir artwork
```

With Inkscape installed, export the print PDF and preview:

```bash
inkscape artwork/BC_Forest_Service_Reconstructed.svg --export-filename=artwork/BC_Forest_Service_Print.pdf
inkscape artwork/BC_Forest_Service_Reconstructed.svg --export-filename=artwork/BC_Forest_Service_Preview.png --export-width=3000
```

## Reproduce the final measurements

The diagnostic scripts require Python 3, Pillow, NumPy and SciPy. Run from the
unpacked package root. The following commands use the packaged fixed evidence:

```bash
python3 source/analyze_tree_overlap.py --reference analysis/reference-rectified.png --candidate analysis/before_preview.png --label before --output-dir analysis
python3 source/analyze_tree_overlap.py --reference analysis/reference-rectified.png --candidate artwork/BC_Forest_Service_Preview.png --label after --output-dir analysis
python3 source/analyze_detail_areas.py --reference analysis/reference-rectified.png --candidate analysis/before_preview.png --label before --output-dir analysis/details
python3 source/analyze_detail_areas.py --reference analysis/reference-rectified.png --candidate artwork/BC_Forest_Service_Preview.png --label after --output-dir analysis/details
python3 source/analyze_constructed_details.py --reference analysis/reference-rectified.png --candidate analysis/before_preview.png --scope analysis/constructed/scope_before_edits.json --label before --output-dir analysis/constructed/before
python3 source/analyze_constructed_details.py --reference analysis/reference-rectified.png --candidate artwork/BC_Forest_Service_Preview.png --scope analysis/constructed/scope_before_edits.json --label after --output-dir analysis/constructed/after
python3 source/analyze_headline.py --reference analysis/reference-rectified.png --baseline analysis/before_preview.png --candidate artwork/BC_Forest_Service_Preview.png --scope analysis/headline/scope_before_edits.json --label after --output-dir analysis/headline
python3 source/analyze_footer.py --reference analysis/reference-rectified.png --baseline analysis/before_preview.png --candidate artwork/BC_Forest_Service_Preview.png --scope analysis/footer/scope_before_edits.json --label after --output-dir analysis/footer
```

The flame report supplies the corresponding yellow-ribbon and shoulder commands.
After the measurements, regenerate the review files in this order:

```bash
python3 source/make_overlap_review.py
python3 source/make_detail_review.py --trees-only
python3 source/make_remaining_review.py
python3 source/make_flame_review.py
python3 source/make_iteration_review.py
```

## Package evidence and checks

- `source/` contains the delivered construction modules and final diagnostic/report scripts.
- `analysis/` contains the reference, supplied photo, delivered revision-5 SVG/PNG, fixed scopes, final before/after metrics, masks and review crops.
- `history/` retains per-area ledgers, rejected and accepted source snapshots, metric checkpoints and selected visual evidence. Original working paths in those historical records document provenance; the portable final commands are listed above.
- `analysis/iteration_manifest.json` identifies every selected module with its source hash.
- `SHA256SUMS.txt` records every other packaged file.

The SVG XML, IDs, vector-only elements and external-reference checks are recorded
in `analysis/validation.json`. The print PDF has one page and no raster image
objects; it was independently rendered and visually reviewed. A clean extraction
is used to check file hashes, byte-identical SVG regeneration, and repeatability
of the final numerical analyses. Rendering/library versions can affect image
anti-aliasing on another system even when the SVG geometry is identical.

## In this repository

Kept: this README, `SHA256SUMS.txt` (the supplied hashes, every file listed; those not kept are
marked “not kept in this repository”), the three artwork SVGs and the print PDF, `source/` (the
construction modules and the diagnostic and review scripts), and the measurements: the JSON under
`analysis/` and the JSON, CSV and Markdown reports under `review/`. Every kept file matches its
supplied hash except this README, which has this section added.

Left out: `analysis/source_photo.jpg`, `analysis/reference-rectified.png` and every other PNG (the
preview, the before and after renders, crops and comparison boards, all of which carry or are
measured against the photograph), the `.npz` masks, `analysis/before_vector.svg` (the superseded
revision-5 drawing, 1.5 MB), `review/BC_Forest_Service_Overlap_Viewer.html` (it embeds the
photograph) and `history/` (727 files of per-pass source snapshots, ledgers and metrics). The
measurement scripts need the reference and preview images, so they will not run here without them;
`python3 source/build_poster.py --output-dir artwork` rebuilds the SVGs from `source/` alone.

The Posters view (`?view=posters&poster=prevent-forest-fires`) shows
`src/posters/forest-service/prevent-forest-fires.svg`: `artwork/BC_Forest_Service_Reconstructed.svg`
with every id prefixed `pff-`, its `<title>` and `<desc>` reworded, its Inkscape layer labels kept as
`data-label`, whitespace removed between tags and inside path data, and fills already inherited from
a parent removed. No number is changed. It is 1,561,659 bytes in place of 1,673,863, and a render in
Chromium at three times its size differs from the supplied file in no pixel. The shelf card is
`prevent-forest-fires.thumb.jpg`, 333 × 480, made from that render.
