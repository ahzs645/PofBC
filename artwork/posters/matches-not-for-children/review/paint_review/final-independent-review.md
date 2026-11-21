# Independent final paint review — Revision 4

**Verdict:** retain the final V4 paint as an improvement in broad composition and removal of repeated texture motifs. The main horizontal stripe belt and vertical rails no longer dominate. This is a qualified improvement, with meaningful local fidelity limits in the lower deposits, right band, and several source-specific brush gestures. No rendering blocker was found.

## Exact SVG proof

I independently rendered the frozen `work/revision4/paint_v4.svg` with Inkscape at 1000 × 1400. The result is **pixel-identical** to `paint_v4.png`: maximum absolute RGB-channel difference is **0**. Review crops use that independent render, the original normalized photograph, and the previous V2 paint retained in V3. They use the same fixed V2 paint mask, with identical neutral exclusions.

The independent proof and boards are in `work/revision4/paint-audit/`: `final-exact-render.png`, `final-full-paint.png`, `final-central.png`, `final-lower.png`, `final-right.png`, and `final-quiet.png`.

## Improvements visible in the final file

- The central field’s right pull around y480–620 has been restored, and the lower spine’s left boundary around y800–950 has been moved right. The broad vertical composition is closer to the photograph.
- The previous repeated horizontal fragments beneath the child and narrow vertical rails on the right have been removed. The material has more varied, broken coverage.
- The intermediate draft’s rounded header caps, pale rings inside the core, and strongest solid amber islands were reduced or removed. The final central pale scrape is narrower, quieter, and more broken.
- The yellow areas contain more low-contrast pigment variation. Small edge breakup is still visibly synthesized at high magnification, but it no longer dominates the whole-poster reading as the former stripes did.

## Remaining regional limits and regressions

1. **Lower deposits, x90–520 / y890–1015:** the final pattern is still made of comparatively coarse upright islands. The source has more localized thin remnants, rubbed transitions, and quiet gaps. Directional repetition is improved, but exact deposit placement regresses under the fixed broad-orange metric: IoU **0.3284 → 0.2118**, despite lower RGB residual (**19.03 → 17.79**). This region should not be presented as a uniformly closer match.
2. **Right band, x870–995 / y70–1110:** broader warm coverage is visually better than the rails, but several strong orange gestures remain displaced or too weak, especially the worn mid-band deposits around y550–680 and lower border around y900–1110. Orange IoU is **0.0252 → 0.0144**, while RGB residual improves **12.91 → 12.16**. Average colour and recognizable mark placement are different measures here.
3. **Upper central spur, approximately x485–535 / y250–325:** the photograph’s broken upright red extension remains simplified and underrepresented. The core below it is closer, but this identifying gesture is not fully recovered.
4. **Upper-left shoulder, approximately x10–180 / y100–255:** the new diagonal transition reads more cleanly and uniformly filled than the source’s overlapping, rubbed paint. The broad block farther down is improved; the upper shoulder retains a geometric character.
5. **Quiet yellow:** the final low-contrast variation is useful, but the photograph’s slender arcs and scratches are only approximated. Adding uniform grain would not recover those particular gestures.

The numerical values above are from the root’s final `Paint_Measurements.json`, using the unchanged 698,156-pixel V2 mask. No mask, registration, or artwork was changed during this final audit. The photograph is an appearance reference; the review does not establish original pigment calibration, physical dimensions, or exact historic wear.
