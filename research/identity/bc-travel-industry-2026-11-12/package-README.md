# British Columbia — Department of Travel Industry

## Reconstructed vector artwork

This package recreates the supplied logo as clean, editable vector geometry.
It preserves the original map and lettering. The central illustration was
reworked on 12 November 2026 to match the additional floral reference: fuller
white petals, separate outlined yellow florets, tapered petal rays, branching
leaf veins, and orange stems with a dark border.

The artwork is deliberately rebuilt from simple line segments and cubic
Bézier curves. It is not an automatic bitmap trace, and the master SVG does
not contain or depend on the reference image.

## Files

| File | Use |
| --- | --- |
| `bc_travel_industry_reconstructed.svg` | Main editable vector, with named layers and a transparent background. |
| `bc_travel_industry_vector.pdf` | Scalable vector export for printing and placement in documents. |
| `bc_travel_industry_transparent.png` | Transparent raster export, 2,576 × 1,872 pixels. |
| `bc_travel_industry_preview.png` | White-background presentation preview. |
| `bc_travel_industry_comparison.png` | Original full-logo reference and current artwork side by side. |
| `bc_travel_industry_flower_detail.png` | Enlarged view of the reworked central illustration. |
| `bc_travel_industry_flower_comparison.png` | New floral reference and revised vector detail side by side. |
| `bc_travel_industry_comparison.html` | Self-contained comparison with side-by-side, wipe, overlay and vector-only views. Open locally in a browser. |
| `source/` | Separate map, flower and lettering SVGs, construction notes and rebuild scripts. |
| `reference/` | Both unchanged user-supplied reference images and a crop for floral comparison. |

## Editing

The main SVG uses the original 644 × 468 coordinate space. It contains
independently editable shapes organized under four top-level layers:

1. Black map edge.
2. British Columbia silhouette.
3. Dogwood flowers, leaves and stems.
4. Reconstructed lettering.

Each of the 41 letters is an individual outline path, grouped by its line.
The lettering therefore stays consistent without installing a font. The
letters can be recoloured, moved or reshaped; they are not live text fields.
Each blossom, leaf and stem is separately accessible in the floral group.

The main SVG contains no raster image, external asset, live text, filter or
font dependency. Its exterior is transparent; the white petal shapes remain
filled parts of the artwork.

## Construction decisions

- The stylized coastline was rebuilt with deliberate anchors, then compared
  to the reference. Local coastal steps and the uneven lower black edge were
  adjusted to preserve the reference's character.
- The central flowers now follow the second supplied reference. Their fuller
  rounded outlines, distinct circular florets, tapered petal rays, leaf veins
  and orange branch were rebuilt as new geometry. The new floral detail was
  scaled into the existing central space; the map and lettering were retained.
- The four lines of lettering use a manually authored glyph system,
  retaining the narrow proportions, subtle flaring, square bowls and slight
  shear visible in the source. Repeated letters share construction geometry
  with individual placement and width adjustments.
- The green, cream, sage, gold and reddish-brown colours were selected from
  the supplied image and simplified to flat fills. Scan grain, compression
  noise and colour fringes were intentionally removed.

The exact historical typeface has not been confirmed. The lettering remains
a reconstruction of the original image, while the floral details follow the
additional reference supplied for this revision. This is a remade vector,
not an authenticated original production master.

## Main palette

| Part | Colour |
| --- | --- |
| Map green | `#116B32` |
| Map shadow | `#080D08` |
| Lettering | `#F9FAE4` |
| Petals | `#FDFDFB` |
| Leaves | `#88B96D` |
| Leaf veins | `#20301F` |
| Stems | `#C95632` |
| Flower centres | `#F2D532` |

## Rebuilding

From the package directory, run:

```sh
python3 source/build.py
```

This assembles the component SVGs and regenerates the comparison HTML.
It needs only Python 3's standard library. It does not trace or analyse the
reference pixels, and it does not access the network.

To also regenerate the transparent PNG and vector PDF, install Inkscape and run:

```sh
python3 source/build.py --export
```

Optional component generators:

```sh
python3 source/rebuild_floral.py
python3 source/rebuild_lettering.py
python3 source/build.py --export
```

The lettering generator additionally uses the Python `fontTools` package
to measure its own hand-authored paths. It does not use any font file.
The source SVGs themselves can be edited directly without running a script.

## Checks completed

The finished SVG and exported PDF were rendered and visually reviewed against
the supplied references. The SVG contains editable paths with unique element
IDs, no image elements and no external links. The one-page PDF contains no
raster image or font resources. The original map and lettering groups were
checked to confirm that the central revision did not change them.
The comparison HTML is self-contained; its script was checked for syntax.

First reconstruction: 11 November 2026. Central floral revision: 12 November 2026.
