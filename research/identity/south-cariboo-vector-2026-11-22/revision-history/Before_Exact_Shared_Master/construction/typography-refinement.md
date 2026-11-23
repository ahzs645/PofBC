# Typography refinement

The selected SVG preserves 34 separate native Souvenir glyphs in four semantic line groups. There is no autotracing or extracted pixel-contour geometry.

## Iterations

1. Tested coherent optical stroke widths from 0 to 0.40 source pixels, including unchanged baseline, with small whole-wordmark translations. Global translations were rejected.
2. Selected a 0.24 px optical stroke (0.12 px expansion per edge). A 0.32 px stroke slightly minimized continuous ink error, but 0.24 px gave the more conservative balance of mid-density overlap, foreground area, and appearance. Larger weight was not adopted.
3. Tested a common placement correction to the initial C / H / C in Community, Health, and Council. Selected -0.4 px horizontally and -0.2 px vertically. No other characters moved or changed proportions.
4. Expanded the stroke mathematically and unioned each glyph's fill/expanded stroke, retaining one fill-only vector path per character. Compared the expanded result to the stroke version and verified the improvement survives conversion.

## Final results against the baseline trees

Clear-background lettering (x >= 140; density >= 0.75) improves from 87.19% to 89.53% IoU; mean boundary distance falls from 0.247 to 0.211 source pixels. Continuous density MSE decreases by 25.5%.

Initial C/H/C dark-mask IoU improves from 70.50/74.43/76.01% to 76.45/84.17/80.95%, respectively. Their statistics depend slightly on the pale background and should be rechecked after the final pale-tree revision.

The selected output is lettering-final.svg. lettering-optical-editable.svg retains the explicit optical-weight and first-cap transforms for construction documentation. typography-refinement.json records full before/after metrics and parameters. typography-before-after.png gives a visual comparison.

The remaining narrow coloured edge fringes are mixed evidence: native font-cut differences, antialiasing, and compressed source edges. Further per-character contour changes would not be well supported by this small raster.
