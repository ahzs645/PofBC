# Seal and signature refinement - revision 2

## Oval seal

The new seal retains analytic oval rings and individually drawn tree, mountains, water and foreground. Its lettering now uses URW Bookman Demi outlines, fitted as existing glyphs to the photographed letter positions. This is a visual substitute, not a verified identification of the historical typeface.

Five installed serif candidates were compared. Glyph transforms (translation, modest horizontal/vertical scaling, and rotation) were then fitted against isolated photographed letter regions. The fit changes placement and proportions of font contours; it never turns the photograph's contours into output paths. Manual visual review rejected an intermediate fit that crowded adjacent letters; the delivered version has no such collisions.

The inner oval moves left by 0.65 normalized poster unit. The manually drawn tree has a small affine adjustment to width and tip placement; the landscape remains an interpretation of the low-resolution source. The output SVG contains transparent negative lettering, rings and sky. Do not add a uniform ochre patch behind it if the aim is photographic fidelity: the photograph shows the yellow/orange/red painted surface through these negative areas.

## Overlay evidence

`seal_overlay_comparison.png` compares the source, previous ink and revised ink. Teal indicates photographed ink, magenta vector ink and dark their overlap. The reference uses the existing normalized 1000 x 1400 photo. The full seal is evaluated within x842:989, y1128:1307. Letter-space comparison uses a fixed elliptical annulus to exclude the central landscape and outer background.

At the middle ink threshold, the full seal ink IoU improves from 0.641 to 0.728. Letter-space IoU improves from 0.220 to 0.632. The direction of improvement persists at all three tested thresholds (max RGB below 90, 110 and 130). These are mask-registration diagnostics, not font-identification, authenticity or percent-fidelity scores. Low source resolution, blur and printing wear remain visible in the overlays. See `emblem_overlay_metrics.json` for definitions and sensitivity results.

## Signature

`signature_v2.svg` uses nine manually drawn stroke paths. The letter spacing, larger A, lower following capitals and longer E reflect the visible rhythm of the source more closely. The signature stays faint and editable. The apparent reading J.J. ANDRE and authorship remain unconfirmed; the reconstruction is not an authenticated autograph.

## Dimensions and colour

The normalized artboard and photographed colour can be fitted, but neither establishes the paper's original physical dimensions or original ink colours. No new physical scale or colour-target evidence was supplied. Keep the 5:7 ratio labelled photo-estimated and colour adjustments labelled photo-matched rather than calibrated.

## Files to integrate

- `emblem_v2.svg`: transparent full 1000 x 1400 canvas.
- `emblem_v2_isolated.svg`: isolated transparent oval.
- `emblem_v2.py` and `letter_transform_fits.json`: reproducible final seal geometry; requires fonttools and the declared URW Bookman Demi font file.
- `fit_emblem_letters.py`: optional fitting analysis; requires NumPy, SciPy and Pillow plus the source photo.
- `signature_v2.svg` and `signature_v2.py`: final full-canvas signature and manual construction source.
- `seal_overlay_comparison.png`, `emblem_overlay_metrics.json`, `signature_revision_comparison.png`: review evidence.
