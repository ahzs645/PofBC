# Revised paint background

## Result

`paint_v2.svg` is the final full background on the shared 1000 × 1400 artboard. It has eight named layers and 145 filled path objects containing 27,875 subpaths (about 2.73 MB). It contains no embedded image, filter, live text, opacity effect or external reference. `paint_v2_clean.svg` contains 28 paths in five layers (about 26 KB), retaining the main authored paint fields without the fine texture.

The supplied paint study was used as a material-construction reference. Its generated texture is substantially less repetitive than the first poster's thin vertical marks. A direct paste of the study was not used: its palette was too bright, and some paint fields aligned less closely than the first reconstruction.

## Specific changes

1. **Correct painted-area alignment.** The supplied study's actual painted area was x=6..668, y=8..936 inside its 685 × 937 canvas. That painted area, rather than the whole canvas, is mapped to 1000 × 1400. The transformation is `matrix(1.510574018 0 0 1.508620690 -9.063444109 -12.068965517)`.
2. **Recomposed paint fields.** The large upper-left field, stepped central mass and lower red field use the prior manually mapped composition, with separate denser deposits in the left and central fields. These fields are stored as deliberately authored construction polygons.
3. **Multiscale paint material.** The supplied study's deterministic paint-deposition model supplies coarse, medium and fine coverage variation, vertical residue, horizontal scumbling and limited paint skips. Its generated fields are converted to filled paths. The input is construction geometry, not the photograph.
4. **Controlled overpainting.** Pale scumbles over the opaque orange cores use a warmer, thinner-looking deposit. Bright yellow no longer cuts arbitrarily large holes through the main orange fields.
5. **Photo-appearance colour fit.** A robust median offset of -7 red, -21 green and -10 blue levels was applied to the study palette, using the explicit background-only mask described below. This matches the appearance of the supplied photograph. It does not establish the physical printing inks or compensate for an unknown camera/scan profile.
6. **Continuous lower red edge.** A red undercoat is extended beyond the crop beneath the textured passes. Ragged procedural stroke ends no longer expose a yellow sawtooth border at the bottom.

The white reserve is intentionally excluded from both files. The poster uses a separately refined reserve component; the inaccurate optional reserve from the supplied paint study is not part of the final background.

## Layers

1. Paper and yellow ground.
2. Yellow pigment variations.
3. Broken amber underpainting, including the red lower undercoat extension.
4. Orange paint pulls.
5. Yellow overpainting and scraped areas.
6. Fragmented brush residue.
7. Directional scumbling.
8. Small paint skips and the lower print edge.

Each layer has the same native-to-poster transform. The poster generator can embed the child groups directly inside its full-artboard clip. Avoid adding the native study reserve.

## Overlay and fitting diagnostics

The fixed evaluation mask contains **698,156 pixels** from the 1000 × 1400 normalized source photo. A pixel is eligible when R>135, B<105, and max(R,G,B)-min(R,G,B)>75. An eight-pixel margin is removed around non-paint. The following areas are then excluded: header y<65; footer y>=1325; headline box x=30..778/y=1015..1325; seal box x=832..998/y=1115..1325.

On that same fixed mask:

| Diagnostic | Previous vector | Revised paint |
| --- | ---: | ---: |
| Mean absolute RGB residual, per channel on a 0–255 scale | 13.93 | 13.25 |
| Broad orange-field intersection-over-union | 0.7507 | 0.7554 |

For the broad-field diagnostic, G/max(R,1) is smoothed with Gaussian sigma=6 pixels and a pixel is classified as orange when that ratio is below 0.50. The comparison is limited to the same fixed paint mask.

These are fitting diagnostics, not historical-authenticity scores or calibrated colour measurements. The palette was fitted on this mask, so the residual is not held-out validation. Regional outcomes are mixed: the right band and lower scumbles improve in this numerical comparison, while parts of the central and quiet-yellow areas have larger local residuals. The strongest improvement is the visible paint character and removal of repetitive marks. Exact grain, stains, wear, and paint hidden behind foreground elements remain interpreted.

Files for review:

- `paint_v2_detail_comparison.png`: original, previous and revised paint crops.
- `background-evaluation-mask.png`: fixed eligible-paint mask.
- `paint-error-before.png` and `paint-error-after.png`: RGB residual maps with a common 0–65 scale; neutral areas are excluded.
- `paint_v2_metrics.json`: exact masks, ROI definitions, sample medians and results.
- `paint_v2_validation.json`: XML structure and vector-only checks.
- `paint-lower-edge-check.png`: final continuous red edge.

## Reproduce

The source inputs are `paint-rebuild/work/construction-geometries.svg`, `paint-rebuild/work/paint-layout.json`, the two generation scripts in that folder, and `finish_paint_v2.py` in the parent directory. Python dependencies: NumPy, SciPy, Pillow and contourpy. The construction stage does not load the original photograph.

Run from a directory preserving that layout:

```bash
python3 paint-rebuild/work/refine_paint.py
python3 paint-rebuild/work/finalize_vectors.py
python3 finish_paint_v2.py
```

Run the finalizer once on fresh refinement output. It expects uncompressed absolute construction paths. The finishing script applies the documented crop mapping and fixed photo-appearance RGB offset, and writes both full and clean components. An SVG editor can modify the supplied final artwork without regenerating it.
