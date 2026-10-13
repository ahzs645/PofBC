# BC Ferry System wordmarks — overlay review v2

## Start here
Open `review.html` in a web browser. It is self-contained and works offline.
The original screenshot is under the vector in Photo overlay mode. Adjust opacity,
change the detail crop, and use Blink to compare. The two columns show the actual
previous SVG (v1) and revised SVG (v2), not image-generated approximations.

The close-up proof is `proofs/toll-authority-overlay-review.png`.
The revised, isolated vectors are in `svg/`, in black and white, with transparent backgrounds.

## What was wrong with v1
V1 resized individual glyph widths independently. In the orange AUTHORITY, the two
T glyphs were given widths of 2.92 and 3.92 in source-image coordinate units. The
A was also squeezed relative to neighbouring letters. This created inconsistent
letter proportions, even when the overall word roughly fitted the screenshot.

V2 preserves the native proportions of each font's letters within a row: the same
horizontal and vertical scale is used for every glyph. Positions are adjusted,
but individual letters are not independently narrowed or widened. Each paired
main-text set also shares its scaling. The two Ts in AUTHORITY now have identical
outlines and scaling. The final SVGs have level baselines.

## Reading the overlays
- Photo overlay: unchanged original screenshot + actual vector in magenta.
- Ink comparison: cyan is source ink, magenta is vector ink, and dark areas are
  where the two overlap. Coloured fringes indicate differences, including scan
  blur, raster sampling, ink spread, scan tilt and geometric mismatch.
- The source-ink layer is contrast-normalized within text regions. Background,
  unrelated scratches and adjoining text are omitted from that diagnostic layer.
  They are NOT removed or retouched in the photo-overlay source.

Both vectors are mapped back into the original screenshot coordinate system.
V1 uses the origin recorded in the previous package; its original paths are not
retyped. V2 uses the exact same paths and transforms as the downloadable SVGs.
No letter-specific warp is added just to make an overlay look better.

The originals are deliberately not AI-upscaled or sharpened. The HTML displays
source pixels with nearest-neighbour enlargement while SVG paths stay smooth.
The unaltered images are included in `references/`.

## Typeface status
These remain visual reconstruction candidates, NOT authenticated historical masters.
The small centre lettering is only about 7 pixels high in the orange screenshot;
a cleaner enlargement cannot recover the missing typeface detail.

Actual substitute outlines used in this revision:

| Variant | Main lettering | Supporting lettering |
| --- | --- | --- |
| Orange / condensed | Roboto Condensed Bold | Roboto Condensed Bold |
| Blue / stacked | Inter Display Black | Liberation Sans Regular |
| Black strip / lighter | Inter Display Regular | Roboto Condensed Regular / Medium |

The names describe the modern outline sources used in this reconstruction. They
do not identify the original printer's typefaces. Font files are not included.

## Files and reproducibility
`source/construction-v2.json` contains the fixed vector paths and transforms.
`python source/rebuild.py --out rebuilt-svg` rebuilds the isolated SVGs using
Python's standard library alone. It does not require font files.
`audit/construction-checks.json` records path counts and the repeated-T check.
`audit/font-candidate-tests.json` records exploratory fitting results; those
numbers must not be read as probabilities or evidence of historical authenticity.
Each revised wordmark has 39 editable glyph paths and no embedded raster image.

The user's newer 8.06.58 screenshot was treated as a report of the rejected v1
output, not as a fourth historical reference to fit against.
