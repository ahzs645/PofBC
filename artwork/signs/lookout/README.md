# British Columbia Forest Service — LOOKOUT

Constructed vector reconstruction of the sign in the supplied reference image.

## Start here

- `svg/BC_Lookout_Master.svg` — main artwork. White sign panel; transparent outside the panel. All lettering is outlined, with no installed fonts required.
- `pdf/BC_Lookout_Master.pdf` — vector PDF of the same artwork.
- `eps/BC_Lookout_Master.eps` — vector EPS export.
- `svg/BC_Lookout_Black_Background.svg` — the sign on a separate black presentation-background layer, matching the reference's presentation. Also supplied as PDF and PNG.

## How this was rebuilt

The sign is not an embedded photograph and was not produced by automatic bitmap tracing. Its panel and outer frame are constructed from a triangle, mathematically offset edges, and circular corner arcs. The inner triangular border is another pair of offset polygons.

Every letter is a separately selectable vector path. The green alphabet was deliberately constructed from straight segments and smooth Bezier curves, with character widths and placement matched to the reference. The red LOOKOUT lettering is custom geometry: three differently proportioned O forms, the tall K, and the angled L, U, and T. There is no substituted live-text font in the production artwork and no font files are included or needed.

The production master contains 38 visible paths, organized into five named layers:

1. White panel / outer silhouette.
2. Outer green border.
3. Inner green triangle.
4. Custom green lettering, with separately grouped words.
5. Custom LOOKOUT lettering, with separately named letters.

## Additional SVGs

- `BC_Lookout_Reference_Palette.svg` — a softer off-white panel with darker green/red approximated from the supplied raster image. This is an optional appearance variant, not an official palette.
- `BC_Lookout_Green_Separation.svg` — green borders and lettering only, transparent background.
- `BC_Lookout_Red_Separation.svg` — LOOKOUT lettering only, transparent background.
- `BC_Lookout_Panel_Silhouette.svg` — the panel outline, filled black for visibility. It represents the white sign substrate in the master.
- `BC_Lookout_Construction_Guides.svg` — artwork plus a removable guide layer. Do not send this guide variant as production artwork.

All three separations use exactly the same viewBox so their registration is preserved when they are overlaid without independent resizing or cropping.

## Editing

Open the master SVG in a vector editor. Use the named groups/layers to change the panel, either border, the green text, or the red wordmark. Ungroup a word to edit an individual letter's nodes. The lettering is editable as curves, not as typed text.

To change colors parametrically or reproduce the SVG files, edit `source/design.json` and run:

```sh
python source/build_sign.py --config source/design.json --output svg
```

The SVG builder uses Python's standard library only. It does not read the reference image, perform image processing, use an online service, or need a font. The EPS/PDF files were exported separately from the master using Inkscape; PNGs are previews, not the vector masters.

## Scale and color

The artwork follows the reference's proportions. No original physical sign dimensions have been inferred. The master page is 1347 × 766 SVG units, including a small clear margin around the panel. Resize proportionally to the required output width before production.

Master colors are flat fills:

| Element | RGB hexadecimal |
| --- | --- |
| Green | `#00543E` |
| Red | `#C5001E` |
| Panel | `#FFFFFF` |

These are reconstruction choices, not verified historical paint or spot-color specifications. The optional reference-palette SVG uses green `#03513B`, red `#B70416`, and panel `#E7ECEB`.

Lighting, grain, shading, edge roughness, and tiny photographic irregularities are deliberately absent. The base edges and lettering baselines have been regularized; the distinctive overall proportions and letter arrangement are retained. This is a reconstruction from the supplied image, not a recovered or authenticated official artwork master.

## Comparison and verification

`comparison/` contains the supplied reference and vector side by side, a 50% overlay, a geometry-alignment diagnostic, and a close comparison of the lettering. Those PNGs are inspection material only; they are not embedded in the SVG, PDF, or EPS artwork.

The geometry diagnostic shows reference-only pixels in magenta, rebuilt-only pixels in cyan, and shared colored-artwork area in grey. Small differences include regularized straight borders, uniform fills, and manually reconstructed glyph details. It is an alignment check, not a certification of exact historical fidelity.

The PDF was rendered back to an image and visually checked. See `VALIDATION.json` for structural checks confirming zero embedded raster images and zero font dependencies in the production SVG/PDF.
