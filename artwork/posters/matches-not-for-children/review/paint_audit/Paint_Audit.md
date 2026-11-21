# Revision 4 paint audit — current V3 poster / V2 paint

The strongest remaining mismatch is the organization of the paint: the central orange field has the wrong silhouette in several places, while the synthetic texture repeatedly runs across or along the image in conspicuous bands. A modest mean RGB residual obscures both problems. The quieter yellow areas can have a close average colour while lacking the brush marks that make the photograph recognizable.

This audit compares `work/reference-rectified.png` with the current poster and `work/revision2/paint_v2.png`, rendered from the paint component. Coordinates refer to the existing 1000 × 1400 normalization. All numerical paint diagnostics use the unchanged V2 background mask of 698,156 pixels. No artwork was edited.

## Ranked actions

| Priority | Location | Visible mismatch | Action for the paint reconstruction |
|---|---|---|---|
| 1 | Central field, x420–770 / y250–1015 | The middle-right boundary retreats too far inward, while the lower vertical spine extends too far left. The result is a lumpy diagonal column instead of the photograph’s more rectilinear overlapping paint pulls. | Restore the right pull near y480–620; narrow the lower spine from its left side near y800–950. Preserve the mostly well-placed upper core around x480–608 / y340–390. |
| 2 | Lower belt, x70–540 / y835–1015 | Repeated horizontal, high-contrast fragments form an artificial striped belt. The photo has upright, broken deposits, irregular overpainting, and a few transverse scrapes. | Remove/recompose the repeated horizontal texture. Build a small number of localized upright remnants and differently angled scrapes; retain irregular quiet gaps. |
| 3 | Quiet left yellow, x180–295 / y210–830 | Average yellow is close, but the surface is conspicuously empty. Existing high-contrast fragments cluster at an unrelated edge instead of occupying the source’s sparse interior marks. | Add diluted, localized marks near x216/y250–300, x215/y350–405, curved marks in x205–270/y475–555, and an angled remnant around x210–245/y735–800. Do not make the entire yellow field more orange. |
| 4 | Right band, x875–995 / y70–1110 | The vector reads as a clean yellow strip with narrow vertical rails. The source has broader, uneven warm coverage and softer overlapping remnants. | Widen and break up the amber underpainting, especially through the lower half. Remove the long aligned rail fragments. Use regional coverage and colour variation rather than a global palette shift. |
| 5 | Left red field, x10–220 / y95–700 | The large upper block is reasonably placed, but its lower continuation is too narrow. Its interior contains excessive horizontal texture where the photo shows largely vertical deposition. | Preserve the main block around y300–500; restore the stepped tail below it, particularly x56–95/y540–575. Reduce interior horizontal bands. |
| 6 | Central upper spur, approximately x480–540 / y250–325 | The current rounded isolated tip and clean yellow surrounding it simplify the source’s broken red column and amber overlap. | Replace the rounded cap with a more fragmented upright deposit and nearby thin warm overlap, keeping this subordinate to the main field. |

## Useful broad-field landmarks

These are approximate orange-region boundaries from the fixed diagnostic, not contour paths to trace. They should guide a deliberate redraw and then be checked visually.

| Row y | Source central right edge | Current right edge | Implication |
|---:|---:|---:|---|
| 480 | 726 | 707 | Extend the right pull about 19 px. |
| 580 | 723 | 695 | Extend it about 28 px. |
| 620 | 721 | 678 | The deepest inward notch is roughly 43 px too far left. |

| Row y | Source lower-spine left edge | Current left edge | Implication |
|---:|---:|---:|---|
| 800 | 608 | 579 | Move the left side right about 29 px. |
| 860 | 615 | 585 | Move it right about 30 px. |
| 920 | 622 | 578 | Move it right about 44 px. |

The source’s lower-spine right side remains approximately x718–719 at these rows, so moving the entire field right would create another error. Narrow it from the left. For the left red tail, the source reaches x108 at y520, x95 at y560, and x78 at y680; the current field reaches only x88, x56, and x64 respectively.

## Palette and texture interpretation

The fixed-mask right-band median is RGB **241, 179, 15** in the photo versus **242, 193, 13** in the vector. The field diagnostic finds 4,459 missing orange pixels against only 143 extra orange pixels in that ROI. This supports adding broader warm coverage. It does not establish that every yellow swatch should lose fourteen green levels: placement and coverage also change a region’s median.

The quiet-yellow ROI illustrates the weakness of average-colour scoring: its medians are **242, 192, 9** and **242, 193, 14**, but the photographed marks are visibly absent. In the lower belt, missing and extra orange areas are both large (5,934 and 6,621 pixels); comparable total coverage cannot make the misplaced striping look right. Exact values are in `regional-diagnostics.json`.

Some source softness comes from the photographed print, registration resampling, and compression. The illustrative 1.2 px blur in `03-texture-and-blur.png` softens the vector edges but leaves its repeated stripes and rails obvious. Camera softness does not explain the displaced 20–40 px paint-field boundaries, the empty yellow interiors, or the wrong direction of the large fragments. Conversely, subpixel grain and very faint mottling should not be copied as crisp high-contrast dots.

## Review files

- `01-full-poster.png`: source and current poster at the same registration and scale.
- `02-orange-field-overlay.png`: fixed-mask field errors; teal is missing orange, magenta is extra orange, gray is excluded.
- `central-mass.png`, `left-core.png`, `lower-scumble.png`, `quiet-left-yellow.png`, `right-band.png`: matching photo, vector-paint, and field-error crops. The first two columns use the same neutral exclusion mask.
- `03-texture-and-blur.png`: texture comparison and a small illustrative blur check.
- `regional-diagnostics.json`: bounds, fixed-mask sample counts, medians, signed RGB residuals, and broad-field error areas.

For final validation, prioritize the corrected field silhouette, removal of repeated directional motifs, and source-located quiet-area marks. Improved average RGB fit alone is insufficient. The photograph remains an estimated registration and appearance reference, not calibrated evidence of the original pigments or dimensions.
