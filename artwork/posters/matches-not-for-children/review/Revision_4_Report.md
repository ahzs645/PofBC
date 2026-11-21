# BC Forest Service poster — Revision 4

## Outcome

This revision addresses the two places raised in the latest review: the paint background and the broken match where the child’s legs meet. The broad paint fields have been recomposed and their texture revised. The joint now has a torn shoulder, a thin irregular split and tapered splinters, replacing the previous thick divider and short star-like strokes.

The final artwork remains native vector geometry. The poster SVG and PDF contain no embedded raster image, live text or raster filters. The photograph and rendered PNGs are comparison evidence outside the vector artwork. The white reserve, headline, seal, footer, centennial captions and publication marks retain their Revision 3 construction. Only the paint layer and the small broken joint change.

## What the overlay revealed

### 1. The crack was a structural drawing problem

The previous figure joined the torso to the legs with a thick diagonal divider from roughly (345.5,776) to (337,792). A few fine strokes were placed over it. In the source photograph, that area is an irregular break: a short shoulder projects from the right-hand rail, a narrow curving seam passes into the lower junction, and small pointed splinters rise from the crotch. Pale negative spaces separate the pieces.

The correction removes the local divider and reconstructs those three features as independently editable ink shapes. A small paper-coloured cutout opens the gap. The long shafts retain their existing coordinates. The first development patch used clipped replacement rails; close inspection found hairline antialias seams, so that method was discarded. The final component has no clipping and changes only the local internal junction.

At the principal dark-ink threshold, the small fracture/splinter region’s mean symmetric edge distance changes from **1.14 to 0.57 normalized pixels**. Its ink-area overlap changes from **53.02% to 76.23%**. In the wider local-joint box, overlap changes from **68.24% to 81.22%**. These measurements support the observed improvement but do not turn a blurred photograph into certain original contours.

### 2. The paint needed its large shapes corrected

The central orange field was not simply missing grain. Its middle-right edge withdrew too far inward, by around 20–40 normalized pixels at several diagnostic rows. The lower spine extended too far left by roughly 25–40 pixels, creating an overly broad, lumpy column. Moving the whole field would have displaced its relatively stable right edge; the useful correction was to reshape it locally.

The upper-left orange block was reasonably placed, but its lower stepped continuation was too narrow. The right yellow band also had too little broad warm coverage. These spatial differences remain visible after smoothing and therefore cannot be explained only by camera blur or tiny print grain. The initial independent audit, coordinates and diagnostic images are retained in `review/paint_audit/`.

### 3. Texture direction mattered more than adding more speckles

The previous paint beneath the legs contained repeated, high-contrast horizontal fragments. The photographed area has irregular upright remnants, overlapping deposits, quiet gaps and a smaller number of transverse scrapes. Along the right edge, narrow aligned rails similarly made the texture look generated.

The new material pass replaces those repeated motifs with authored paint pulls, irregular residual deposits and localized dragged or rubbed marks. Yellow-field marks are distributed regionally, rather than changing every yellow pixel to a warmer colour. The first structure-and-colour draft improved numerical fit but looked too flat; it was revised after visual review. The final paint remains a reconstruction of material appearance, with fine grain and some small deposits still interpreted.

## Fixed-reference paint measurements

Both versions use the same photograph registration and the same **698,156 eligible paint pixels**. The mask is retained from Revision 2, including its interior margin and exclusions. The raw RGB residual changes from **13.25 to 11.28 levels per channel**. Broad orange-field overlap changes from **75.54% to 78.67%**.

| Region | V3 RGB residual | V4 RGB residual | V3 orange overlap | V4 orange overlap |
| --- | ---: | ---: | ---: | ---: |
| All eligible paint | 13.25 | 11.28 | 75.54% | 78.67% |
| Upper-left paint pull | 10.66 | 7.24 | 94.45% | 95.83% |
| Central paint mass | 13.40 | 12.25 | 83.39% | 86.63% |
| Lower central stroke | 15.53 | 10.53 | 76.50% | 88.89% |
| Quiet yellow field | 8.45 | 5.82 | 10.92% | 16.41% |
| Right paint band | 12.91 | 12.16 | 2.52% | 1.44% |
| Lower paint / scumbles | 19.03 | 17.79 | 32.84% | 21.18% |

Lower RGB residual indicates closer average appearance under this fixed comparison; higher orange overlap indicates closer broad field placement. The quiet-yellow region may contain very little orange, so its orange-overlap value is a poor general texture measure. Regional boxes overlap; their sample counts must not be added.

**The regional outcome is mixed.** In the lower paint/scumble box, orange-field overlap changes from 32.84% to 21.18%, despite a lower RGB residual. In the right band, orange overlap changes from 2.52% to 1.44%; the very low values concern the strongest orange deposits, which occupy only a small part of that predominantly yellow/amber region. Improved average warmth and removal of repeated motifs have not solved the exact placement of those stronger marks. The tables retain these regressions explicitly.

The next useful paint corrections are therefore specific: the lower belt needs finer, less upright remnants at the photographed locations; the right band needs its strongest orange gestures better placed; the broken red spur above the central block, roughly x485–535/y250–325, remains too simplified. The upper-left shoulder and some sparse yellow-field scrapes also remain interpreted. These are visible construction differences, beyond the unavoidable uncertainty in microscopic grain.

The additional masked, smoothed RGB residuals are **9.52 → 7.40** at sigma 8 pixels and **7.61 → 5.67** at sigma 24 pixels. These help inspect broad colour/placement separately from high-frequency grain. The full regional values are in `review/Paint_Measurements.json`.

The photograph is used for both visual design fitting and evaluation, so these are **fit residuals**, not held-out validation. No value is a whole-poster accuracy percentage or a calibrated pigment measurement. A numerically improved paint field can still look too regular; the enlarged comparisons and final visual audit remain essential evidence.

## Overlay method

The established perspective transform maps the supplied photograph to an estimated 1000 × 1400 reference plane. The source corners and transformation are preserved in the package. Neither registration nor paint-mask selection was changed to improve this revision’s scores.

For paint, the fixed mask begins with photo pixels having R > 135, B < 105 and RGB range > 75. It applies an eight-pixel interior margin and fixed exclusions for the top captions, footer, main headline and seal. Broad orange classification uses a Gaussian-smoothed ratio G / max(R,1), sigma 6 pixels, with a threshold of 0.50. In `BCFS_Paint_Overlay.png`, **teal marks orange present in the photograph only**, and **magenta marks orange present in the vector only**. Greyed areas either agree under that classification or are excluded; the overlay does not rate their fine texture.

For smoothed RGB residuals, normalized convolution uses only the eligible paint mask before smoothing. This avoids spreading the photograph’s white reserve and black lettering into the paint comparison. Sigma 8 and 24 are diagnostic scales in the normalized plane.

For the crack, dark ink is classified using max(R,G,B) < 125. The context box is x307–372, y758–826; the local-joint box is x320–354, y763–804; the fracture/splinter box is x325–345, y766–799. Identical boxes and thresholds are used for both versions. The joint overlay uses **teal for missing ink** and **magenta for excess ink**. Its pixels are deliberately enlarged without smoothing so the diagnostic cells remain visible.

### Crack threshold sensitivity

| Dark-ink threshold | V3 fracture IoU | V4 fracture IoU | V3 mean edge distance | V4 mean edge distance |
| --- | ---: | ---: | ---: | ---: |
| 90 | 51.23% | 73.42% | 1.17 | 0.58 |
| 110 | 53.63% | 75.00% | 1.16 | 0.57 |
| 125 | 53.02% | 76.23% | 1.14 | 0.57 |
| 140 | 53.56% | 77.12% | 1.16 | 0.58 |

The same direction of improvement across these fixed thresholds is more persuasive than choosing a single favourable threshold. Remaining tiny differences can reflect wear, camera softness, compression, resampling, registration or imperfect reconstruction. Geometry in the final artwork is manually authored; photographic masks and contours do not generate its paths.

## Review and editing

Start with `BCFS_Child_Crack_Details.png` to inspect the structural repair, and `BCFS_Child_Crack_Overlay.png` for its local ink diagnostic. The paint overview is `BCFS_Paint_Overlay.png`; `BCFS_Paint_Details.png` provides matching enlarged paint crops. `BCFS_Reconstruction_Comparison.png` shows the full photograph, V3 and V4 side by side.

`BCFS_Interactive_Review.html` is self-contained. It includes V3, V4 textured and V4 clean artwork, wipe/blend, paint and crack diagnostics, photo/vector-only views, and focus controls with up to 1200% of fit zoom. The clean edition shares the revised drawing; its diagnostic modes explicitly show the textured V4 paint and the common crack. Embedded SVG identity and JavaScript syntax were checked. Browser interaction was not exercised in this environment, so the static boards remain the directly inspected comparison.

The final artwork has separate layers for paint, white reserve, matchstick illustration, headline, seal, footer, centennial captions and publication marks. `BCFS_Child_Crack.svg` is the local repair component: it includes the paper-coloured cutout and belongs above the base figure with its obsolete hip-star stroke removed. The full master already applies it correctly. Paint, white reserve and lettering remain independently editable.

## Remaining priorities and limits

1. **Specific paint deposits and gestures:** the lower belt's orange placement and the right band's strongest orange marks still need work, as the regional regressions above show. The upper-central broken red spur and upper-left shoulder remain simplified. Irregular dry edges, small translucent deposits and worn pigment also differ. Further refinement should target recognizable medium-scale strokes and quiet gaps.
2. **Source limitations:** the supplied image includes photographic softness, wear, compression and a partly cropped paper edge. An exact physical print boundary, ink palette and concealed paint cannot be established from it.
3. **Small historical details:** the seal uses fitted URW Bookman Demi outlines as a visual substitute; the historical typeface is unverified. Fine emblem details and the apparent “J.J. ANDRE” signature reading and attribution remain approximate.
4. **Print preparation:** the 5:7 artboard is an estimated comparison plane. The PDF is scalable vector artwork; it has no printer-specific colour profile or bleed specification. Original physical dimensions and calibrated colours are unverified.

The earlier white-edge work is retained, not rescored as a new improvement in this revision. Its reports and fixed-mask measurements remain available in the historical review folders.

## Reproducibility and validation

`source/rebuild_poster.py` assembles the final components without reading a photograph or mask. `source/crack_joint.py` regenerates the local manually authored break. `source/paint-source/` contains the paint construction code; its synthetic deposition fields originate from authored geometry rather than extracted photo contours. Final component SVGs are supplied so ordinary vector editing requires no Python.

`source/analyze_revision4.py` is the portable fixed-reference analysis entry point. `source/build_review_html.py` rebuilds the offline viewer from those diagnostics. Historical analysis scripts are retained separately for provenance.

`review/Vector_Validation.json` records native-vector checks, unchanged-layer checks, the one-page PDF’s lack of bitmap images, and viewer asset/syntax checks. `review/Source_Rebuild_Check.json` records an isolated regeneration from the packaged final components. Review PNGs and the supplied photograph are raster evidence; they are not embedded in the vector master or PDF.
