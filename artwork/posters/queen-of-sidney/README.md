# Queen of Sidney sticker: vector reconstruction

## Files

- **Queen-of-Sidney-rebuilt.svg** is the editable master. Its lettering is outlined, and its objects are organized into named layers and subgroups.
- **Queen-of-Sidney-rebuilt.pdf** is the vector print/export copy. It contains one page and no raster images.
- **Queen-of-Sidney-preview.png** is a 3915 × 3618 PNG. The white sticker is retained; the area beyond its outline is transparent.
- **Queen-of-Sidney-comparison.png** is the four-panel proof: original, reconstruction, 50% overlap, and magenta reconstructed edges over the source.
- **Queen-of-Sidney-overlap-50.png** is the overlap at the native 1305 × 1206 size.
- **Queen-of-Sidney-edge-overlap.png** is the edge proof at the native size.
- **Queen-of-Sidney-comparison.html** is a self-contained offline viewer. Open it in a browser for opacity, wipe, edge, original and rebuilt views, with zoom. The embedded SVG can also be downloaded from the viewer.

## What was rebuilt

The orange field and white sticker outline, helm ring and individual handles, flag and pole, two different outlined dogwood flowers, small flag flower, forested shorelines, four sky birds, sea waves, curved ribbon with folded ends, ferry, and all wording are vector artwork.

The ferry includes the hull and blue bow marks, green waterline, dark lower hull, bridge and saloon windows, upper cabin, roof, deck railings, bow staff, mast and fittings, antennas, hanging anchor, aft open deck and perforated bulwark. These are separately editable subgroups.

The master has **254 path elements**, **55 geometric primitives** (rectangles, ellipses and circles), and **47 groups**. It has **zero embedded images** and **zero live text elements**. No image-tracing operation was used to produce its contours.

## Construction method

The artwork was reconstructed from the visible shapes using authored Bézier curves, lines, rounded forms, concentric ellipses, repeated window geometry and individual letter outlines. Features were placed directly in the original image's coordinate system.

The upper wording uses outlined Nimbus Sans Regular glyphs, fitted individually to the reference's visible letter bounds and spacing. This is a visual typeface reconstruction, not a claim that the original production typeface was recovered. The thirteen letters in QUEEN OF SIDNEY were constructed from explicit geometric outlines and individually positioned and rotated.

Ten named top-level layers cover the sticker/field, flag, scenery, helm, flowers, ferry, exposed helm overlap, sea, ribbon and lettering. The extra exposed-helm layer preserves the original drawing order where the ring crosses the bow.

## Overlap method

The original and reconstruction both use a **1305 × 1206** canvas. Their comparison transform is the identity matrix:

```text
[1, 0, 0, 1, 0, 0]
```

No global or local translation, fitted scale, rotation, perspective correction, or warp was introduced to make the proof match. The 50% proof composites the vector at half opacity over the original. Outside the vector's transparent exterior, the original image remains visible.

For the magenta proof, the visible boundaries of the rendered vector are overlaid on a lightly faded original. These boundaries are derived from the finished vector render, not traced from the source. Display thumbnails in the four-panel sheet were reduced only after the full-size proofs had been composed.

The HTML viewer retains the same registration in every mode. Zoom changes only the shared display size of both images. It loads no external assets or fonts and requires no network connection.

## Review and corrections

The review checked the original and reconstruction side by side and in registered overlays. Corrections included:

- The spacing and curvature of the blue and white bow bands.
- The upper bridge windows and right hull edge.
- The small exposed helm wedge above the bow.
- The white wave crest that crosses the lower-left helm.
- More irregular forest branches.
- The width and slanted outer edge of the right flower's lower-right bract.
- The angle and counter shape of the ribbon's Q.

The PDF was rendered and visually inspected. Its page resources contain no raster images. The offline viewer was checked in a desktop and narrow mobile viewport; opacity, wipe, edge and rebuilt modes functioned without JavaScript errors.

## Deliberate cleanup and remaining interpretation

The original photograph's paper grain, faded ink, uneven lighting, wear and drop shadow were removed. Colours are clean RGB approximations chosen from the reference. They are not recovered historical ink specifications or verified spot-colour values.

Major contours and placement follow the source. Fine flower veins, small railings and fittings, forest marks, wave scallops and letter curvature remain clean hand reconstructions of the available raster reference. They do not reproduce every printing irregularity. The wheel and sticker boundaries have been regularized into smooth geometry.

The SVG is suitable for further editing and scaling. No original physical sticker dimensions were inferred. The PDF uses the SVG's native canvas at the standard 96-pixel-per-inch export conversion; set the desired finished size when printing. This is a reconstruction, not recovered original production artwork.

## Source package

The ZIP includes these deliverables under `output/`, authored components and scripts under `src/`, the unmodified supplied reference under `reference/`, and compact validation records under `qa/`.

The master SVG and PDF need no font installation. To reassemble edited component SVGs, use Python with `lxml` and run `python src/assemble.py` from the extracted package root. `build_scene.py` regenerates the manually authored scenery. The existing `lettering.svg` already contains all outlines; regenerating it through `build_lettering.py` additionally requires FontTools, Pillow, NumPy, Inkscape and Nimbus Sans Regular at the font path recorded in that script.

To regenerate proofs, render the master through Inkscape to `qa/final-native.png` at 1305 × 1206, then run `python src/build_proofs.py` with Pillow, NumPy and SciPy available. The authored `ferry.svg` can be edited directly in a vector editor.
