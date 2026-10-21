# Ferry reconstruction notes

## Deliverable

`ferry.svg` is a standalone transparent SVG in the same 1354 × 1161 pixel viewBox as the supplied image. Insert its `ferry-illustration` group after the mountains and before the gull.

The component is manually constructed from Bézier curves, polygons, rectangles and circles. There are no raster images, linked assets, font dependencies, automatic contour paths, filters or masks. `ferry_build.py` reproduces the component.

## Contents

- Sloping funnel, dark cap, cream band, small teal funnel panel and inclined mast.
- Stepped cream superstructure and lower deck.
- Six bridge windows, five small upper windows, main window row, curved forward saloon window and sloping forward panes.
- Nine repeated circular portholes and two angled stern openings.
- Upper teal band with diagonal bow stripe, lower teal waterline and dark navy hull with the shaped stern.

## Registration and comparison

All geometry uses the supplied source coordinates directly. No similarity registration, perspective fit, post-render translation, scaling or warping was used. The component is rendered with Inkscape and assessed against the reference in this coordinate system.

The ferry-edge-overlay.png proof shows magenta vector boundaries on the original crop (x140–1200, y430–700). It is displayed at 2× for inspection.

A binary dark-fill check restricted to the visible windows and portholes in x390–1100, y535–645 gives 95.63% intersection-over-union. Symmetric boundary distance has a median of 0 px, a 95th percentile of 1.0 px, and a maximum of 1.42 px. Source segmentation is used only for this validation and measurement, never to create vector contours. These values are specific to that ROI and do not describe the entire sticker.

## Deliberate reconstruction choices

- Curves and straight edges are clean design geometry; reference grain, antialiasing, and color mottling are omitted.
- Portholes use regular circles, and nearly rectangular windows use regular rectangles.
- The superstructure and windows underneath the gull are continued coherently, but the concealed shapes cannot be recovered from this reference. The supplied gull should cover them in the assembled artwork.
- Fill colors are provisional shared palette tokens and may be normalized by the parent assembly.
