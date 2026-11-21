# Refined Forest Service emblem lettering

## Final result

The 28-letter layer is a true vector reconstruction in the original 1709 x 2048 coordinate system. It contains individually named outline paths, with no image elements, live text, external references or fonts required to use it.

The same-threshold lettering-mask overlap improved from 92.8236% to 95.3064% IoU (+2.4828 percentage points). Twelve letters improved; the other sixteen are unchanged. This is a measurement of lettering masks only, not of the whole emblem or original font identity.

## What changed

All three Rs and Ss, both Cs and Bs, and the M and A now use dimensioned typographic constructions. Each model has a fixed small set of straight lines and cubic Bezier curves. Named dimensions describe stems, bowls, counters, terminals and diagonal legs. The two Cs and three Rs have separate dimensions, reflecting visible differences in the reference. Their positions, widths, heights, rotations and modest shears were fitted independently.

No reference-pixel contour was exported. Reference masks were used to measure the fit of the designed letter models. The retained F/E/T/H/L outlines were built earlier from dimensioned stems and bars.

| Character | Before IoU | Refined IoU | Change |
|---|---:|---:|---:|
| R in FOREST (letter 3) | 92.48% | 95.40% | +2.92 pp |
| S in FOREST (letter 5) | 89.38% | 94.01% | +4.63 pp |
| S in SERVICE (letter 1) | 92.06% | 94.50% | +2.44 pp |
| R in SERVICE (letter 3) | 87.68% | 94.58% | +6.90 pp |
| C in SERVICE (letter 6) | 88.45% | 96.14% | +7.68 pp |
| B in BRITISH (letter 1) | 92.10% | 96.54% | +4.44 pp |
| R in BRITISH (letter 2) | 89.44% | 94.30% | +4.85 pp |
| S in BRITISH (letter 6) | 91.33% | 94.78% | +3.45 pp |
| C in COLUMBIA (letter 1) | 86.62% | 95.84% | +9.22 pp |
| M in COLUMBIA (letter 5) | 90.35% | 97.38% | +7.03 pp |
| B in COLUMBIA (letter 6) | 94.56% | 96.50% | +1.95 pp |
| A in COLUMBIA (letter 8) | 91.75% | 96.86% | +5.11 pp |

## Typeface notes

The retained O, V, I and U outlines use calibrated Open Sans Bold, Nimbus Sans Bold, DejaVu Sans Mono Bold and Liberation Sans Bold shapes. Those are construction sources, not an identification of the historical original font. No one tested typeface matched every letter in the supplied image.

The exact retained source glyph outlines are stored in font-outline-sources.json, so rebuilding this delivery does not require font installations. Each final glyph source, dimensions and affine transformation is recorded in lettering-transforms.json.

## Comparison method

Both the reference and the rendered vector are 1709 x 2048 pixels. Inkscape renders the vector with fill #30312d over background #d1d296. The dark-pixel threshold is max(R,G,B) < 115 in both images. Each of the 28 reference characters is matched one-to-one to a rendered connected component. Borders, dots and the illustration are excluded. No image registration, resizing or post-render warping is applied.

The final intersection contains 192,882 pixels; the union contains 202,381 pixels. The original-image SHA-256 is recorded in lettering-comparison.json.

In overlay-final.png and overlay-final-full.png, dark shows agreement, pink shows reference-only pixels, and cyan shows reconstruction-only pixels. Remaining discrepancies are chiefly small terminal and curve differences in the Ss and Rs and the retained font-derived O/U/V shapes, plus source edge irregularity and JPEG softness.

## Rebuilding the selected artwork

Run `python build_lettering.py`. It reads the frozen lettering-parameters.json, the dimensioned models in refined_models.py and custom_glyphs.py, and font-outline-sources.json. It writes lettering.svg and lettering-transforms.json. Python dependencies are FontTools, NumPy and Pillow. No fonts need to be installed.

To reproduce the comparison, run `python compare_lettering.py --reference /absolute/path/to/the-original.jpeg`. This additionally needs SciPy and Inkscape. The script renders baseline-lettering.svg and lettering.svg afresh and records both mask metrics and individual-glyph results.

The fitting research is also retained: fit_refined_models.py, fits-refined.json, baseline-transforms.json and labels.npz. Refitting writes candidate parameters for review; the frozen delivered parameter file is not replaced automatically. Editing or using the SVG itself needs none of these dependencies.
