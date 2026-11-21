# BC Forest Service poster — revision 2

## What improved

This revision addresses the white borders identified in the screenshots, replaces the first background's repetitive thin marks with a more varied vector paint surface, and refines the oval seal and faint signature. The largest measured improvement is in the white illustration reserve: its intersection-over-union with the fixed photographic reference increases from **0.8604 to 0.9586**, while its mean boundary distance falls from **4.88 to 1.41 normalized pixels**.

Those numbers describe agreement with a registered photograph. They do not mean the complete poster is “95.86% authentic” or that its original dimensions, printing colours, artist or typefaces have been established.

| Element | Revision |
| --- | --- |
| White illustration reserve | Five controlled, manually authored contours replace the earlier randomly perturbed polygons. The rope column, head, shoulders, arms, legs, diagonal brace and upright have been refitted. |
| Paint | The supplied study informed the material construction, but was not pasted into the poster unchanged. Broad paint fields were recomposed, the palette was adjusted to the photo, and the lower red edge was repaired. |
| Oval seal | Existing serif glyph outlines were fitted more closely to the photographed lettering. The tree and inner oval received restrained geometric adjustments. The painted background shows through the negative areas. |
| Signature | Nine manually drawn stroke paths better reproduce the visible spacing and rhythm. The reading and attribution remain uncertain. |

## White-border construction and overlay method

The earlier white reserve contained arbitrary alternating edge changes, especially beside the suspended thread and around the child's neck and shoulders. The replacement uses deliberate Bézier curves and straight segments informed by sparse visual landmarks and cross-section measurements. Its irregularities correspond to recognizable changes in the photographed boundary; there is no randomized edge jitter.

The photograph was **not automatically traced to create these paths**. A separately generated pixel mask is used only to evaluate the finished vector geometry.

Both versions are compared on the **same 1000 × 1400 reference plane**, using the same estimated perspective transformation. The reference mask uses pale/dark photographic classification within a 35-pixel expansion of the previous illustration region, one-pixel closing, components selected at fixed figure locations, and filling of enclosed holes smaller than 50 pixels. The large painted triangular opening is retained. The artwork masks come from the alpha coverage of the isolated reserve layers, rendered at the same resolution and thresholded at 127/255.

The oval seal's footprint is excluded, with its radii expanded to 74 × 90 normalized pixels. The seal touches and obscures part of the white post, so the photograph cannot establish the complete reserve beneath it. The same exclusion applies to both versions.

**Intersection-over-union (IoU)** is the shared reserve area divided by the combined reserve area. **Mean edge distance** is the pooled symmetric nearest-boundary distance. Higher IoU and lower edge distance indicate better fit under this fixed comparison method.

### White-reserve measurements

| Region | Previous IoU | Revised IoU | Previous mean edge distance | Revised mean edge distance |
| --- | ---: | ---: | ---: | ---: |
| All visible illustration reserve | 0.8604 | **0.9586** | 4.88 px | **1.41 px** |
| Hanging thread and upper knot | 0.8939 | **0.9557** | 2.97 px | **1.16 px** |
| Child head and neck | 0.8712 | **0.9670** | 4.09 px | **0.93 px** |
| Child arms, body and legs | 0.7664 | **0.9492** | 6.81 px | **1.29 px** |
| Upper beam and diagonal brace | 0.8804 | **0.9591** | 4.38 px | **1.50 px** |
| Upright support | 0.8785 | **0.9678** | 4.99 px | **1.32 px** |

For the full visible reserve, the 95th-percentile edge distance falls from **13.42 to 4.00 pixels**. Excess white area falls from **20,184 to 7,338 pixels**, and missing white area falls from **13,911 to 2,244 pixels**. Region boxes overlap, so their counts should not be summed.

The practical change is a narrower, more stable rope column and a much less inflated outline around the child's shoulders and limbs. The remaining coloured slivers in the overlays identify local discrepancies rather than a broad placement error. Larger connected slivers are useful candidates for further contour editing; isolated edge speckles can instead reflect blur, ink wear, colour thresholding or the estimated registration. Removing every such speck would risk fitting photographic noise.

All white-reserve figures in this report come from **`White_Edge_Measurements.json`**. They use one common reference-mask definition throughout.

## Background reconstruction and what its measurements show

The supplied paint study has a more convincing mixture of broad deposits, broken residue and horizontal scumbling than the first poster's thin vertical marks. Its palette was initially too bright, however, and some fields were less well aligned. Revision 2 therefore maps the study's actual painted area to the poster, restores deliberately composed large fields, adds denser orange deposits, controls pale overpainting and extends the red undercoat beneath the lower edge.

The paint generator operates on authored construction geometry and synthetic deposition fields. It does not derive its output contours from the uploaded photograph. The generated coverage is converted to filled vector paths. The full paint component has eight named layers and 145 compound path objects; the clean component retains 28 paths in five layers. Neither contains an embedded bitmap or raster effect.

A fixed background-only mask contains **698,156 eligible pixels**. Header, footer, headline, seal and a margin around non-paint are excluded. The study palette receives a documented RGB offset of −7, −21 and −10 levels, estimated from this masked photograph.

| Paint diagnostic | Previous | Revised |
| --- | ---: | ---: |
| Mean absolute RGB residual per channel, 0–255 scale | 13.93 | **13.25** |
| Broad orange-field IoU | 0.7507 | **0.7554** |

These are **modest numerical improvements**, with mixed regional outcomes. The right band and lower scumbles improve under this comparison, while parts of the central and quiet-yellow regions have larger residuals. The main visual benefit is a less repetitive paint surface and a more credible balance between opaque fields, overpainting and broken residue. The residual is also not a held-out validation measure: the palette was fitted using the same mask.

Use the enlarged paint comparisons to judge whether the direction and density of marks suit the original. Use the common-scale residual maps to find misplaced colour fields. The maps cannot distinguish a historically correct ink colour from a camera colour cast, and exact photographed grain remains an interpretation.

## Seal and signature

The seal lettering now uses **URW Bookman Demi outlines as a fitted visual substitute**. Five installed serif candidates were compared, and glyph translation, modest scaling and rotation were adjusted against isolated photographed letter regions. The font contours remain existing vector glyphs; photographic letter contours were not converted into the output. A crowded intermediate arrangement was rejected during visual review.

At the middle ink threshold, full-seal ink IoU increases from **0.641 to 0.728**, and letter-space IoU increases from **0.220 to 0.632**. The direction of improvement persists at all three tested thresholds. The seal also has a small inner-oval adjustment and restrained changes to the manually drawn tree. Its negative lettering, rings and sky remain transparent, exposing the painted surface instead of a uniform ochre patch.

The signature's spacing, larger A, lower following capitals and longer E are represented by nine editable strokes. It remains faint. The apparent reading **J.J. ANDRE** and the poster's authorship are still unconfirmed; this reconstruction is not an authenticated autograph.

## What remains unresolved

- **Physical size:** 1000 × 1400 is a normalized working artboard. The 5:7 ratio is estimated from the photograph, whose upper paper edge is partly cropped. There is no new physical-scale evidence.
- **Original printing colours:** the revised colours match the appearance of the supplied image more closely. Without a colour target or known scan profile, that is not calibrated recovery of the original inks.
- **Hidden and fine details:** paint behind the illustration, reserve behind the seal, disconnected tiny edge flecks, small tree details and exact printed grain remain interpreted.
- **Original typefaces and attribution:** improved visual fits do not independently identify the historical lettering or artist.

For further editing, keep paint, white reserve, black illustration, lettering and seal in separate layers. Use the clean paint component when rearranging or recolouring the design. For another fidelity pass, prioritize the larger remaining edge slivers and regional paint-field mismatches shown by the overlays before adding more fine texture.

## Measurement and construction records

- `White_Edge_Measurements.json`: authoritative white-reserve metrics for this report, including region bounds and exclusions.
- `paint_v2_notes.md` and `paint_v2_metrics.json`: background construction, fixed paint mask, colour-fit method and regional outcomes.
- `details_v2_notes.md` and `emblem_overlay_metrics.json`: seal and signature changes, threshold sensitivity and limitations.
- `reserves_v2.py`: manually specified reserve contours; the photo mask is not an input to its geometry.
