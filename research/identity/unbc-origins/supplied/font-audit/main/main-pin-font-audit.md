# Interior University Society: independent main-mark and pin font audit

## Decision

Retain Nimbus Sans Bold as the practical reconstruction base for the photographed print mark. The supplied photograph supports a Helvetica-like grotesk with a curved R leg and a bold, rather than regular, stroke. This is a family-level visual assessment; it does not identify the exact original typeface, foundry, cut or weight designation.

The pin deserves a separate weight treatment. Its photographed black inlays appear heavier and their counters tighter than the current compressed Nimbus Sans Bold reconstruction. Both a +0.020-cap and a +0.025-cap black-edge experiment improve the apparent ink/metal balance. The +0.020 trial is the more conservative change and has been adopted for the production enamel pin and its one-colour adaptation. The +0.025 alternative remains an unadopted comparison trial. The +0.025 trial is visually somewhat closer to the photographed mass, but neither can distinguish true inlay boundaries from relief shadows and blur. Do not chase the photograph's darkest fringes or label either trial an authenticated historic font.

## Evidence and method

This audit uses the original brochure photograph IMG_7953(1).jpeg and the original close-up pin photograph IMG_7956(2).jpeg, plus the current vector masters. Earlier generated cleanups were not used as historical type evidence. The brochure's letterhead-size glyphs contain only about a dozen to a few dozen native image pixels across important features. Enlargement does not recover detail. The pin was re-rectified from the full-resolution, EXIF-corrected photograph, rather than from the earlier downsized inspection image.

Six printed candidates were independently typeset at a common cap height and natural widths: Nimbus Sans Bold, Nimbus Sans Regular, a clearly labeled synthetic intermediate-weight experiment, Liberation Sans Bold, DejaVu Sans Bold and URW Gothic Demi. Nimbus Sans Narrow Bold was additionally compared for the pin. The intermediate-weight experiment is normalized back to the same final cap height. It is not a real identified Medium font.

Font geometry was read directly with fontTools. Production horizontal fitting uses the actual ink bounds, matching the builder's convention; advance widths would give different and misleading percentages. No source pixels were traced into production contours.

## Character evidence

| Feature | Original print observation | Assessment |
|---|---|---|
| R leg | Both Rs in INTERIOR have a curved transition into a near-upright lower leg, with a small outward foot. | Supports the Nimbus/Helvetica-style R. Liberation's straight diagonal leg is less faithful. |
| S terminals | Broad S with roughly horizontal end cuts; low resolution prevents a reliable fine terminal-angle match. | Consistent with Nimbus, insufficient for an exact font identification. |
| O | Vertically oriented rounded oval; clear counter remains fairly open. | More consistent with the grotesk specimen than the strongly geometric URW Gothic alternative. |
| U bowl | Straight upper stems transitioning into a broad, rounded bottom. | Nimbus shape is a reasonable match. The source cannot resolve every curvature difference. |
| Stem weight | The two I stems measure approximately 0.18-0.23 cap height under reasonable source thresholds. | Nimbus Bold's I width is 0.2058 cap; Regular is 0.1289. Bold is defensible; Regular is visibly too light. |
| O counter | The photo's midline counter is roughly 0.55-0.60 of the O's outer width. | Nimbus Bold contour ratio is 0.57265; Regular is 0.73580. This independent proportion supports Bold. |

The source estimates are descriptive ranges, not calibrated print measurements or statistical confidence intervals. They include paper texture, perspective, sampling and blur.

## Horizontal fitting: exact current construction

| Row | Main print factor | Pin factor |
|---|---:|---:|
| INTERIOR | 100.6644% | 86.0011% |
| UNIVERSITY | 101.4813% | 87.7454% |
| SOCIETY | 100.4463% | 87.0767% |

The main print's 0.4-1.5% width adjustments are minor; the letters are essentially at their natural proportions. The pin is deliberately 12-14% narrower than natural Nimbus Sans Bold. That produces a different O oval, stem/cap ratio and R stance. Whether this reproduces a condensed original cut or compensates for uncertain pin aspect cannot be established from the angled photograph alone.

## Pin weight experiment

At the O's widest region, the photographed light counter appears about 0.35-0.43 of the dark O's outer width across plausible thresholds. Current Nimbus Bold has an approximately 0.573 contour ratio before the metal effects. The smaller observed opening supports a heavier apparent pin treatment, but reflection and moulded depth also shrink the visible light region.

The trial artwork keeps the existing metal backing and glyph positions, then expands the black contour by either 0.020 or 0.025 of the original 108-unit cap height per edge (2.16 or 2.70 drawing units). The black outline widths are therefore 4.32 and 5.40 units. This also expands total cap height by 4% or 5%; it is explicitly a visual experiment, not a finished independent typeface weight. Any adopted production change should document that construction choice.

Adopted decision: the modest +0.020-cap black-edge treatment is applied separately to the enamel pin and one-colour adaptation. The unchanged first-version SVGs remain in reference/font-audit/v1-before for comparison. Do not replace the main print font, and do not claim that the pin uses the exact same original typeface as the print mark.

## Files

- main-font-comparison.png: original print / current reconstruction, plus six independent candidates.
- pin-font-comparison.png: original pin / current reconstruction, natural vs compressed and narrow specimens.
- pin-weight-trials.png: original / v1 before audit / adopted +0.020 / unadopted +0.025 comparison.
- pin-weight-trial-020.svg and pin-weight-trial-025.svg: vector comparison artwork; +0.020 matches the adopted optical treatment, while +0.025 is an unadopted trial.
- font-metrics.json: exact font contour measurements and production fitting factors.
- compare_fonts.py and pin_weight_trials.py: reproducible comparison builders.

The first-stage audit was read-only. After review, build_core.py was updated to apply the adopted +0.020-cap black-edge adjustment; all core SVGs and their core manifest were rebuilt. Metal backing contours remain unchanged. The main print font and geometry remain unchanged.
