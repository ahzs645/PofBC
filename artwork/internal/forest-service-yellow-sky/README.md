# British Columbia Forest Service - editable vector package

## Start here

The artwork is supplied as real SVG path/primitive geometry, with vector PDF and EPS exports. The PNG files are previews, not the vector deliverables.

Two clearly separated reconstructions are included:

1. **01_Preview_Style** - a bold, flat-colour redraw of the two-badge generated preview shown in the conversation. Green and cream variants, plus a two-colourway artboard.
2. **02_Photo_Reference_Style** - an additional redraw based on the two supplied photographs, retaining the more slender trunk and asymmetric, wind-shaped upper boughs. Green and cream variants, plus a two-colourway artboard.

Within each set, the green and cream variants have identical geometry. Only the palette changes. The two sets intentionally differ in lettering, tree treatment, line weights and foreground detail; they should not be confused as the same master.

## What is editable

Open an individual file from a set's `SVG` folder. The main named groups are:

- `oval-rings` - analytic ellipse geometry and ring field.
- `scene` - separately grouped sky, mountains, lake, distant forest, foreground and central evergreen.
- `central-evergreen` - individual branch tiers, shading, branch detail, trunk and roots.
- `inner-frame` - editable elliptical scene boundary.
- `lettering-upper`, `lettering-lower` - individually editable outlined letters.
- `separators` - the two circular side dots.

The illustration is clipped by an editable ellipse. Nothing in the vector masters is a bitmap, generated-image embed, texture overlay or automatic raster trace. Shapes are built from editable paths, circles and ellipses. Solid fills and strokes are used, without gradients or filters.

Text is outlined: no font installation is required to use the supplied artwork. The words cannot be changed by typing into these outlines; new wording requires new lettering. No font files are included. The photo-reference set uses custom condensed block-letter outlines; the preview set uses fitted Roboto Condensed Bold outlines. Neither is asserted to be the original historical font.

## Formats and folders

Each artwork set contains:

- `SVG` - editable vector masters: green, cream and both colourways.
- `PDF` - corresponding vector exports.
- `EPS` - corresponding vector exports.
- `PNG` - transparent previews, 3000 pixels high.

Additional folders:

- `Components` - isolated tree and landscape SVGs for both reconstruction styles.
- `Previews` - side-by-side images rendered from the actual final SVGs.
- `Reference_Images` - the supplied photographs and the earlier generated raster preview, retained for comparison only.
- `Tools` - palette data, a dependency-free recolouring script and vector-validation results.

The single-badge artboard is nominally 152 x 200 mm, including a small transparent margin. This is a convenient working size, not a measured historical production size. Scale proportionally. The combined artboards are 320 x 204 mm.

## Recolour without changing the geometry

Every colour-bearing shape or group has a `data-fill` or `data-stroke` token, such as `ring`, `sky`, `foliage` or `ink`.

For example, from the package's root folder:

```sh
python3 Tools/recolour.py \
  01_Preview_Style/SVG/BCFS_preview_green.svg \
  --palette-json Tools/palettes.json \
  --palette preview-cream \
  --output custom-cream.svg
```

For a single-colour adjustment:

```sh
python3 Tools/recolour.py \
  01_Preview_Style/SVG/BCFS_preview_green.svg \
  --set 'ring=#176B45' \
  --output custom-green.svg
```

The script uses only the Python standard library. It changes paint values, not paths, letter positions or oval geometry. The original input is not overwritten unless explicitly selected as the output with `--overwrite`.

## Fidelity and verification

These are independent redraws, not recovered official production artwork. The earlier generated preview was a raster image; the vectors are newly constructed artwork, not an exact pixel-for-pixel conversion. Fine conifer detail, terrain marks, typography and colours are approximations. The source photographs are small and affected by reproduction/photographic conditions, so their precise original colours and minute details cannot be established from them.

All final SVGs were checked for embedded images, live text, filters and gradients: none are present. All PDF exports were checked for embedded raster images: none are present. Green/cream geometry was compared within each set and found identical. The PDF artwork was also independently rendered and visually inspected. The validation results are in `Tools/vector_validation.json`.

Use the actual SVG-rendered images in `Previews` to review the delivered geometry, rather than treating the earlier generated image as an exact proof of these files.
