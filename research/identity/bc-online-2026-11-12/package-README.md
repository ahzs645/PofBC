# BC OnLine — vector reconstruction

Rebuilt from the two raster images supplied with the request, dated 12 November 2026. These are editable reconstructions of the supplied artwork, not recovered official vector masters.

## Files

- **BC-OnLine-logo-black.svg** — complete black wordmark and emblem, using the lighter emblem weight seen in the supplied full-logo reference.
- **BC-OnLine-emblem-blue.svg** — separate emblem with the heavier blue weight seen in the supplied emblem reference; colour `#333B97`.
- **BC-OnLine-emblem-black.svg** — separate black emblem with the full-logo reference's lighter weight.
- **BC-OnLine-wordmark.svg** — separate outlined wordmark.
- **BC-OnLine-logo-black.pdf** and **BC-OnLine-emblem-blue.pdf** — vector PDF copies.
- **previews/** — high-resolution transparent PNGs and a comparison sheet.
- **source/** — the manually authored shape definitions and a portable Python script that regenerates all four production SVGs.
- **references/** — unchanged copies of the two supplied reference images.

## How the artwork was reconstructed

The emblem was decomposed into named shapes: monitor bezel and casing contours, sleeve and cuff, thumb, individual finger contours and openings, lower monitor edge, keyboard frame, and seven individual keys. Each silhouette uses explicitly authored cubic Bézier curves. The curves were adjusted through enlarged side-by-side and overlay comparisons with the supplied references. No automatic bitmap tracing, contour extraction, or image embedding was used in the production SVG files.

The source emblem uses tapered filled ribbons and deliberate gaps. These characteristics were retained instead of replacing every contour with a uniform stroke. The two supplied raster references also have visibly different ink weights, so the blue and black versions use separate silhouette definitions.

The wordmark consists of eight editable letter paths. The two lowercase n forms share the same underlying construction. The lettering retains the broad capitals, slight rightward inclination, varied stroke weights, and small e counter. A small 0.3-unit optical stroke correction is part of the wordmark group. There is no live text and no font dependency. The exact historical typeface has not been verified; the lettering was reconstructed from the supplied reference.

The blue is the dominant solid colour in the supplied transparent emblem: RGB 51, 59, 151 (`#333B97`). The pale edge pixels in the raster were not reproduced as outlines. Both production SVGs and transparent PNGs have transparent backgrounds. White areas between shapes are open transparency, not white paint.

## Editing and use

Open an SVG in a vector editor. The full logo has separate Wordmark and Emblem groups, and the emblem shapes and individual letters have descriptive IDs. Shapes can be selected, recoloured, and adjusted individually. PDF copies retain vector geometry. The production artwork contains no linked files, embedded bitmaps, external font references, scripts, or filters.

SVG page bounds include a small transparent margin to avoid clipping outer tips. The emblem's slant, asymmetry, keyboard perspective, layout, and wordmark spacing are intentionally retained. The comparison sheet includes raster references for review and is not the production logo.

## Rebuilding the SVGs

From this folder, run:

```sh
python3 source/build_vectors.py
```

Only the Python standard library is required. The build script reads the manually authored path data; it never reads the reference bitmaps. Inkscape can optionally render PNG and PDF copies from the SVG output.

## Reference files

- User upload: `BC-OnLine-2005-emblem(1).png`, 181 × 128 pixels, RGBA.
- User upload: `BC-OnLine-2011-original(1).png`, 672 × 145 pixels, black/white.

The years above come from the supplied filenames. They have not been independently established as the introduction or retirement dates of either logo treatment. Fine details are reconstructed interpretations within the limits of these small raster references.
