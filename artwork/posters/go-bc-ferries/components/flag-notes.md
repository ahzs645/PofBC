# Dogwood flag reconstruction

`flag.svg` uses the unmodified source coordinate system (`viewBox="0 0 1354 1161"`). Import the `dogwood-flag` group directly into the assembled artwork; no registration transform is required.

## Construction

- Manually authored Bézier flag outline, preserving the asymmetric upper wave, concave free edge, lower pointed corner and curved lower hem.
- Five individually named cream dogwood bracts, a cream joining disc, a dark surround and six separately editable centre/detail shapes.
- Pole rebuilt from two simple polygons plus two rotated ellipses for the finial.
- 15 paths, two ellipses and one circle. No images, text objects, fonts, automatic contour tracing, filters or raster effects.
- Palette aligned to root measurements: cream `#fce6a3`, green `#047634`, navy `#031e24`, ink `#0b0f0b`.

## Comparison

The component was rendered to the original 1354 × 1161 pixels and compared directly with the source. `work/flag-detail/flag-edge-overlay.png` shows magenta rebuilt edges on the original pixels. The source was not translated, resized, rotated or warped for the comparison. `flag-comparison.png` is a three-panel local study; its rebuilt panel uses a temporary flat teal background, not the complete sticker.

The cloth silhouette and pole align closely. The flower is a clean geometric reconstruction: its tiny radial marks and the inner petal seams differ by about one to a few source pixels in places. The source texture, fuzzy transitions and faint fringe have intentionally not been encoded as vector geometry. No original production file, exact historical colour standard or original manufacturing dimensions was available.

The SVG itself is the editable reconstruction source; all control points are explicitly recorded in its path data.
