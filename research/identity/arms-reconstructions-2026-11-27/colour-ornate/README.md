# Historical coat of arms: vector reconstruction

This package rebuilds the supplied “Ornate historical coat of arms.png” as scalable, editable vector artwork. It is a reconstruction of that specific supplied drawing, not an authenticated official vector master.

## Main files

- `historical-bc-coat-of-arms.svg`: main editable artwork, on the source's 1261 × 1247 coordinate system, with a transparent outer background.
- `historical-bc-coat-of-arms.pdf`: one-page vector export. No raster images are embedded.
- `historical-bc-coat-of-arms-4000px.png`: transparent raster export, 4000 pixels wide, for convenient use in applications that do not accept SVG.
- `previews/historical-bc-coat-of-arms-preview.png`: the finished artwork on a warm neutral background.
- `previews/historical-bc-coat-of-arms-comparison.png`: reference and reconstruction at the same scale and registration.
- `previews/historical-bc-coat-of-arms-detail-review.png`: aligned reference / first vector / revised vector closeups for the antlers, inner scrolls, shield, and crown.
- `previews/historical-bc-coat-of-arms-silhouette-overlay.png`: cyan reference boundaries and magenta vector boundaries. This checks external contours only; it does not measure the accuracy of internal details.

## Reconstruction decisions

The lion, stag, and ram retain source-guided outlines and engraving-like details. Printed halftone dots were removed before curves were fitted and cleaned. Contact points, hooves, and stray colour fragments were inspected separately.

The shield, flag geometry, waves, sun rays, small crown, ribbon curves, large-crown jewels, and pearl beads were selectively redrawn or regularised. The clean result deliberately differs from the coarse printed texture.

## Revision 2: detail corrections

- Antlers: restored narrowed ivory runs and excessive black weight at branch crossings. The outer silhouette, number of tines, and spacing between branches are unchanged. The thin upper-left twig interior was rebuilt as a tapered curve.
- Scrolls: recovered the rounded inner curls, continuous edge into the SINE panel, original bowl depth, and outer roll seams. Removed the first version's triangular fold closures and duplicate edges below the hooves. The 18 outlined letters are unchanged.
- Shield: reconstructed the inset, rounded red diagonal tips and open white junctions; corrected the small crown's oval underside and the chief's dividing line. Refitted the sun-ray curves against the source while keeping the visible ray tips anchored.
- Crest: repaired the small crown's disconnected gold arch and the overlap that hid the lion's toe tips. Preserved more mane detail, restored the shoulder incision, and corrected crown gem interiors separately from their borders.

These changes followed enlarged, registered comparisons. The very small cross lobes and fine printed mane edges remain interpretations of the supplied raster.

The motto is outlined vector lettering, preserving the original letter widths, positions, and curved baseline without substituting a font. The visible break in the N of SINE was repaired. The text reads SPLENDOR SINE OCCASU.

The palette is normalised to ink #171513, warm ivory #FFF5DF, gold #FFC928, red #EE3429, blue #168FC1, ribbon outline #CD365A, and the flag's narrow red edge #AE3343. This is a visual reconstruction palette, not a claim about official colour specifications.

## Editing

Open the SVG in Inkscape, Illustrator, Affinity Designer, or another vector editor. Named groups separate the shield, crowns, lion, stag, ram, ribbon, and motto. All visible SVG content is vector geometry, including the lettering. There are no bitmap images or external font dependencies in the SVG. The supporters contain compound paths; their internal contours can be edited with a node tool.

The PDF is also vector. The PNG files are preview/convenience exports and are not editable vector artwork.

## Rebuilding

The `rebuild` directory includes the source raster, component SVGs, and the Python source used to make the artwork. Requirements: Python 3, NumPy, SciPy, Pillow, lxml, the system libpotrace library, and Inkscape for export.

From the `rebuild` directory:

```sh
python build_artwork.py
inkscape output/historical-bc-coat-of-arms.svg --export-type=pdf --export-filename=output/historical-bc-coat-of-arms.pdf
```

The main build script rebuilds all five components before assembling them. The reconstruction uses a combination of source-guided curve fitting and manually defined geometry. It should not be described as an entirely manual redraw or as untouched original artwork.

## Verification

The final SVG and PDF were rendered and visually inspected, including the faces, antlers, horns, crown, shield contacts, hooves, ribbon, and motto. The final files were checked for embedded images and live text. Machine-readable format checks are in `vector-validation.json`.
