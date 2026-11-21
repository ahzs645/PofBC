# Revision 4 paint — construction and overlay analysis

## Result and scope

The Revision 4 paint retains the registered 1000 × 1400 plane but replaces the earlier material construction and adjusts the large fields. The baseline is the **Revision 3 poster**, whose paint component is byte-for-byte the Revision 2 paint. The white reserve, black drawing, lettering, seal and the child's revised crack are outside this component's scope.

The strongest improvements are the central orange column's placement and the removal of the repeated horizontal marks beneath the legs. The central field has a straighter right pull around y480–620 and a narrower lower-left edge around y800–920. The upper-left field's short stepped continuation is broader. The right yellow band has more widespread warm underpainting, and selected gestures are restored in the quiet yellow areas.

The final paint is still an interpretation. The lower-belt deposits remain coarser upright islands than those in the photograph; the right band's strongest orange gestures are displaced or underrepresented; and the broken red spur above the central core is simplified. Several thin angled scrapes in the quiet yellow field remain absent. These limitations are visible in the final crops and overlays.

## What the overlay analysis separates

A single pixel residual cannot distinguish a misplaced large field from newly drawn grain that differs from the source. This analysis therefore keeps three views of the same fixed paint-only domain:

1. **Raw RGB residual:** mean absolute difference per display-RGB channel, showing both colour-field and fine-detail mismatch.
2. **Broad colour fields:** normalized Gaussian convolution through the paint mask at σ4, σ8, σ24 and σ48 pixels. The photo's white reserve, black ink and lettering are excluded before this smoothing, so they do not leak into the broad RGB comparison.
3. **Texture structure:** a green-channel bandpass, σ1.2 minus σ8, showing short-scale contrast and predominant direction. This helps reveal repeated ridges without interpreting every different grain mark as a geometric error.

The primary eligibility mask is **unchanged from Revision 2**, with **698,156 pixels**. It retains the existing paint classification and eight-pixel non-paint margin, and excludes the header, footer, headline box and seal region. The mask hash is recorded in the JSON files. The field calculations use identical registration and mask definitions for both versions.

A few separate, explicitly paint-coloured header/lower-red sample regions informed the palette outside that primary domain. Those samples excluded pale paper and dark ink by colour and an erosion margin; they are not added to the primary metric. No foreground pixels are used to create the paint geometry.

## Final exact-SVG measurements

The final measurements use `paint_v4.svg` rendered by Inkscape at 1000 × 1400, rather than the direct synthetic-coverage draft. Vector contour smoothing, simplification and antialiasing can make the exact SVG render differ slightly from that draft.

| All eligible paint | V3 | V4 |
| --- | ---: | ---: |
| Mean absolute RGB residual, per channel on the 0–255 scale | 13.25 | **11.28** |
| Broad orange-field IoU | 0.7554 | **0.7867** |

| Smoothed RGB comparison | V3 residual | V4 residual |
| --- | ---: | ---: |
| Gaussian σ4 px | 10.43 | 8.40 |
| Gaussian σ8 px | 9.52 | 7.40 |
| Gaussian σ24 px | 7.61 | 5.67 |
| Gaussian σ48 px | 6.34 | 4.63 |

The reduced coarse-scale residual supports a genuine change in field placement and colour balance, rather than only adding texture. The same photograph was used for design fitting and evaluation, so these are **fit diagnostics, not held-out validation**. They do not measure overall historical fidelity or authenticate the printing colours.

### Regional outcomes, including regressions

| Region | V3 RGB residual | V4 RGB residual | V3 orange IoU | V4 orange IoU |
| --- | ---: | ---: | ---: | ---: |
| All eligible paint | 13.25 | 11.28 | 0.7554 | 0.7867 |
| Upper-left paint pull | 10.66 | 7.24 | 0.9445 | 0.9583 |
| Central paint mass | 13.40 | 12.25 | 0.8339 | 0.8663 |
| Lower central stroke | 15.53 | 10.53 | 0.7650 | 0.8889 |
| Quiet yellow field | 8.45 | 5.82 | 0.1092 | 0.1641 |
| Right paint band | 12.91 | 12.16 | 0.0252 | 0.0144 |
| Lower paint and scumbles | 19.03 | 17.79 | 0.3284 | 0.2118 |

The **lower central stroke** is the clearest structural improvement. Its orange IoU increases from 0.7650 to 0.8889, and its RGB residual decreases from 15.53 to 10.53. The broad main core and upper-left pull also fit more closely.

The **lower paint/scumble region and right band have mixed results**. Their average RGB residuals improve, but strong-orange placement becomes worse under the fixed classifier: the lower region changes from 0.3284 to 0.2118 orange IoU, and the right band from 0.0252 to 0.0144. The right-band score is already very low in both versions. Warmer widespread amber colour does not reproduce the actual locations of the strongest orange deposits. Likewise, removing the artificial horizontal pattern improves the lower belt's material character without placing its new orange islands exactly where the photographed islands occur.

Those two regions remain priorities for another location-focused paint pass. The overall number should not be used to hide their regressions.

The legacy orange diagnostic is preserved for comparison: smooth G/max(R,1) with Gaussian σ6, classify orange below 0.50, then evaluate on the same eligible mask. It scores one thresholded colour family; it cannot distinguish calibrated historical ink from a camera colour cast, or establish whether the new grain is physically authentic.

### Texture contrast and direction

For the entire eligible domain, texture-band RMS is 11.74 in the photograph, 14.77 in V3, and 12.61 in V4. Overall short-scale contrast is therefore closer to the photo, although the lower-belt contrast remains stronger than the source.

The directional ratio is the mean absolute adjacent-pixel difference across x divided by that across y, evaluated on the paint mask eroded another four pixels. Values above one indicate more vertically oriented structure. This ratio is **1.15 for the photo, 1.22 for V3, and 1.50 for V4**. V4 still has too much vertical structure in this aggregate check. The repeated horizontal hatch defect is removed, but the texture's full directional balance has not been recovered. This diagnostic is sensitive to region choice and measures an image statistic, not the original painter's technique.

## How the paint was rebuilt

The source is separated into a placement file and a material generator:

- `paint-source/paint_design.py` contains the authored polygon fields, layered yellow lifts, a connected lower undercoat region and selected cubic-centreline brush gestures. Coordinates are manually chosen source landmarks, not an extracted photo contour.
- `paint-source/build_paint_v4.py` creates seeded coarse, medium and fine deposition fields. Their direction and coverage are combined with the authored shapes, then converted into opaque filled SVG paths. The generator does not read the photograph or any diagnostic mask.

The earlier study's repeated directional-scuff geometry is not reused. Long orange/red pulls have irregular thin deposits beneath denser bodies; local dry coverage breaks their edges. Pigment variation uses smaller colour steps within the opaque cores. The lower belt is an unevenly exposed connected undercoat, rather than an array of horizontal stripes or separate identical brush ends. Right-band amber is spread through broken coverage, with quiet gaps retained.

Visual review rejected a first material pass that was too flat and a second pass whose broad Gaussian deposits resembled opaque rounded islands. The final pass reduces those colour jumps and breaks the coverage with finer irregular deposition. The header wash fades through grain instead of ending in a row of rounded caps. The pale upper-right central scrape was narrowed, its contrast reduced, and its dry coverage made uneven. Only the larger lower-belt cores in the audited x280–500/y930–1015 vicinity were locally muted in the finishing pass.

These are newly constructed paint marks. The final vector paths describe the authored synthetic material, not a pixel-outline dump of the original photograph. Fine print grain, faded residue and paint hidden behind foreground elements remain interpreted.

## Editable vector assets

| Component | Path objects | Compound subpaths | Named layers | Size |
| --- | ---: | ---: | ---: | ---: |
| `paint_v4.svg` | 267 | 36,657 | 8 | 11.19 MB |
| `paint_v4_clean.svg` | 28 | 28 | 6 | 8.7 KB |

The full layers are yellow ground/pigment, warm underpainting, long orange/red pulls, yellow lifts/overlap, lower remnants, located dry-brush gestures, local pigment grain and the continuous lower red finish. The clean version retains the authored fields with simpler coverage; it is useful for layout, recolouring and macro-shape editing.

The full file contains many small subpaths. Edit major placement in `paint_design.py` or use the clean component, and preserve the named layer groups when moving/recolouring textured paint. The generator's internal construction counter excludes two directly authored full-artboard/edge polygons; `paint_v4_validation.json` gives the authoritative total of 267 SVG path objects.

Both components were parsed and rendered. They contain **zero embedded images, live text, filters, gradients, opacity attributes or external references**. The exact full SVG render was independently reproduced and compared pixel-for-pixel. This validation concerns the paint components, not the separate full-poster PDF export performed by the main assembly.

## Final evidence files

All final review files are under `paint-analysis/` with the prefix `final-`:

- `final-metrics.json`: raw, multiscale, region and texture measurements, with the fixed-mask identity and method.
- `final-multiscale-review.png`: V3/V4 common-scale raw and σ24 residual maps, plus a lower-belt texture-band comparison.
- `final-v3-error-sigma0.png` and `final-v4-error-sigma0.png`: raw residual heatmaps on the same 0–65 scale.
- `final-v3-error-sigma24.png` and `final-v4-error-sigma24.png`: broad-field residual heatmaps on the same 0–40 scale.
- `final-v3-orange-overlay.png` and `final-v4-orange-overlay.png`: teal is strong orange present only in the photo; magenta is strong orange present only in the vector.
- `final-full-comparison.png`, `final-central-comparison.png`, `final-lower-comparison.png`, `final-right-comparison.png`, `final-quiet-comparison.png`: registered photo/V3/V4 paint comparisons.

Those paint-specific preview boards retain the V3 foreground to isolate the background change. The final merged master and its review boards also contain the separately revised child-leg crack. Earlier draft families are working records and should not be treated as final evidence.

The underlying estimated 5:7 artboard, unknown physical print size and uncalibrated photographic colour remain unchanged. A 1000-plane pixel measurement is not a physical distance on the original poster.

## Reproduce

Keep the `paint-source` folder beside the two component SVG outputs. The pinned dependencies in that folder record the environment used for the export; the random seed is 14201967.

```bash
python3 -m pip install -r paint-source/requirements.txt
python3 paint-source/build_paint_v4.py --svg
inkscape paint_v4.svg --export-width=1000 --export-filename=paint_v4.png
```

`paint-source/README.md` explains draft mode and the separate diagnostic script. `paint_v4_provenance.json` records source, generator and fixed-mask hashes. Construction requires no photo or mask. The comparison analysis does require the supplied reference and preserved masks; it is intentionally separated from artwork generation.
