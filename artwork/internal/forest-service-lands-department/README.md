# British Columbia Forest Service / Lands Department — vector reconstruction, V2

## Start here

- `svg/bcfs-lands-department-v2-editable.svg` — primary, grouped vector artwork.
- `svg/bcfs-lands-department-v2-white.svg` — the same artwork on a white page.
- `print/bcfs-lands-department-v2-vector.pdf` — vector print export, no embedded images or fonts.
- `print/bcfs-lands-department-v2-vector.eps` — vector EPS export on the full white page.
- `review/side-by-side-comparison.pdf` — eight coordinate-matched reference / V1 / V2 proof sheets.
- `review/compare.html` — local interactive comparison. Extract the entire ZIP before opening it.

The PNG files are previews only. They are not the vector masters.

## What changed

The earlier substitute tree, uniform procedural sprays, generic cone scales and substitute font setting have been replaced. The revision follows the supplied reference's actual visible structure rather than reusing those generic constructions.

**Tree crown.** The reference-specific branch network, unequal branch lengths, rounded foliage ends, overlapping interior limbs and white openings are retained in editable curved ink geometry. The earlier regularly tiered conifer is gone.

**Main trunk.** The narrow, slightly right-offset trunk between FOR and EST has been rebuilt, including its tapered end above the V and its short white bark slit. The lower trunk has the reference's upper notch, asymmetrical internal cuts and spreading root flare, instead of the previous smooth, nearly symmetrical construction.

**Lettering.** All 43 letter instances were re-positioned and fitted individually. Reusable capital-letter outlines were authored and adjusted, with particular correction of S, E and H. Weight, letter widths, rotation and spacing were measured against the supplied image. The master does not use Inter or another live-text substitute. The historical typeface's name has not been verified; these are reconstructed letter shapes, not a supplied or identified font.

**Exterior.** Both sets of boughs, terminal needles, cone engraving and lower stems were reworked against the reference. The preceding evenly repeated needles and fan-like cone scales are not retained in the revised master.

**Oval.** The oval was fitted to the reference's border, including its slight tilt, rather than retaining the earlier nominal ellipse unchanged.

## How the artwork is constructed

This is a component-based vector reconstruction, not a single full-image outline autotrace. It is also not wholly freehand illustration: reference-derived centerline measurements and numerical geometric fitting were used.

1. Visible ink networks were measured as centerline graphs with local stroke widths.
2. Their branches were rebuilt as curved vector strokes and variable-width geometric envelopes. Overlapping vector disc geometry was united and compacted into smooth paths; this operation acts on vector geometry, not raster boundary contours.
3. The main trunk, roots and reusable letter outlines are separately authored paths whose coordinates were fitted to the reference.
4. The oval is an independent ellipse. Each letter is an independent outlined vector object.

The files retain groups for the central seal, tree crown, upper trunk, lower trunk/roots, lettering, left/right exterior regions, bough regions, cone regions and lower stem ends. The engraving components preserve visible intersections; they are not speculative drawings of hidden botanical parts. Near bough/cone joins, crossing ink strokes are assigned to one editing region rather than duplicated into hypothetical complete needles or scales.

Fine paper noise and subpixel ink irregularities are simplified. This is a reconstruction from the supplied image, not an authenticated historical production master or a claim of pixel-perfect identity.

## Verification

The master contains 6,567 paths and 5,049 circles, plus the oval and grouping/metadata. It contains **zero embedded raster images** and **zero live text objects**. The vector PDF contains **zero image objects and zero fonts**. IDs are unique and all artwork lies within the page.

The revised artwork was rendered at the source's 1536 × 1024 coordinate size and compared with the supplied reference. Black-ink intersection-over-union (IoU; threshold <130) changed as follows:

| Measured region | V1 | V2 |
|---|---:|---:|
| Full emblem | 43.9% | 95.1% |
| All 43 letters, isolated | 31.1% | 95.4% |
| Tree crown, isolated | 58.1% | 96.4% |
| Upper main trunk, isolated | 69.6% | 96.7% |
| Lower trunk and roots, isolated | 53.9% | 96.4% |

These are **diagnostic ink-overlap measurements**, not percentages of historical authenticity or proof that a historical typeface has been identified. Antialiasing, deliberate smoothing and source sampling affect them. Exact masks, thresholds and crop coordinates are documented in `review/verification.json`.

An independent PyMuPDF render of the print PDF was also compared with the CairoSVG preview. Native-resolution ink overlap between the two renderers is 99.38%; small edge differences are normal antialiasing differences. The EPS was independently rendered with Ghostscript as an additional export check.

## Transparency and editing

The editable master has no full-page background. The oval field is intentionally opaque white. The white-page variant supplies a full-page white rectangle. The outside engraving's unpainted spaces remain transparent in the transparent version.

No font installation is required. Letter shapes remain individually editable, but this is **not a live-text font document**. The package deliberately does not include the earlier live-text approximation or any font files.

The detailed engraving produces many small vector objects. Edit at the group level first, then expand the relevant group for a local change. The `components` folder contains tightly framed component SVGs; all geometry remains vector.

## Rebuilding the master

The `source` folder contains the geometry data, reusable glyph outlines and builder. The build reads these vector/graph data files; it does not open a bitmap or load a font.

Requirements: Python 3.10+, NumPy, lxml and Shapely. CairoSVG is optional for preview and print export.

```sh
python -m pip install numpy lxml shapely cairosvg
python source/build_emblem.py --output svg/rebuilt.svg --preview previews/rebuilt.png
```

The graph JSON records editable branch centerline points, radii and junctions. `letter_placements.json` controls each letter's position, scale, rotation and weight; `custom_lettering.py` and `glyph_refinements.json` provide the reusable outlines. `tree_root_refinements.json` contains the final trunk/root curves. `oval_geometry.json` contains the measured ellipse.

To make a fresh print export after editing:

```python
import cairosvg
cairosvg.svg2pdf(url="svg/rebuilt.svg", write_to="print/rebuilt.pdf")
cairosvg.svg2eps(url="svg/rebuilt.svg", write_to="print/rebuilt.eps")
```

## Reference and review files

`reference/original-reference.png` is the user's supplied image. `reference/previous-v1-render.png` is a render of the previously delivered vector, retained only for comparison. Neither is embedded in the SVG or vector print PDF.

The eight-page proof booklet and the proof PNGs intentionally contain raster comparison crops. Use the separate SVG/PDF/EPS artwork files for production. Checksums are listed in `SHA256SUMS.txt`.
