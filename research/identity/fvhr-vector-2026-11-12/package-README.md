# Fraser Valley Health Region — vector reconstruction

Rebuilt from the two supplied screenshots on 12 November 2026.

## Files

| File | Purpose |
| --- | --- |
| `fvhr-emblem-color.svg` | Primary blue-and-green emblem; transparent; eight editable paths. |
| `fvhr-lockup-color.svg` | Colour emblem with outlined organization name and tagline. This combines the two references. |
| `fvhr-lockup-grayscale.svg` | Rebuilt monochrome header with grey, black-outlined petals alternating with black petals. |
| `fvhr-emblem-black.svg` | One-colour derivative of the colour master. |
| `fvhr-vector-artwork.pdf` | Three all-vector pages: colour lockup, grayscale lockup, colour emblem. |
| `fvhr-emblem-color.png` | Transparent 2400 × 2400 px emblem preview. |
| `fvhr-lockup-color.png` | Transparent 3000 px-wide colour lockup preview. |
| `fvhr-lockup-grayscale.png` | Transparent 3000 px-wide grayscale lockup preview. |
| `fvhr-preview.png` | Overview of the reconstruction. |
| `fvhr-reconstruction-comparison.png` | Source comparison and registered silhouette difference map. |
| `source/` | Outline groups, reconstruction parameters, validation results and a small vector rebuilding script. |

The SVGs contain real paths. They contain no embedded bitmap, live font dependency, tracing mesh or image filter. Their backgrounds are transparent, including the central opening and the gaps between petals. Each petal remains a separately editable object.

## Construction

The primary colour emblem uses a single master petal: a semicircular cap joined to a right-isosceles triangular tail. Four quarter-turn rotations and reflection produce the eight petals. Blue and green preserve the ordering in the supplied colour reference.

The clean master uses a cap radius of 100 units, a half-width of 71 units for the central horizontal and vertical channels, and a diagonal offset of 39 units. The northeast petal is:

```svg
<path d="M 71 -110 L 71 -310 A 100 100 0 0 1 271 -310 Z"/>
```

The complete emblem spans 820 × 820 units. Its SVG canvas is 900 × 900 units, allowing 40 units of clear space on each side. The source's small horizontal distortion was removed in this regularized colour master.

This is geometric reconstruction. Raster thresholding was used only to measure and compare the reference with the designed shape; it did not generate the final path nodes.

## Typography

The lettering reads exactly:

**FRASER VALLEY HEALTH REGION**  
**“Integrating Health Care”**

The type was rebuilt using P052 Bold and P052 Bold Italic outlines, a Palatino-style design. These gave the closest fit among seven locally available serif families compared against the reference. Tracking, proportions and optical weight were adjusted; the small scan tilt was removed. The title match is less certain than the italic tagline match.

The outline groups include a small vector stroke, adding roughly 0.8–1 source pixel around glyph edges to reproduce the heavier printed appearance. This could reflect a heavier original font cut, printing gain or scanning effects. It is not evidence that the historical artwork used a stroke.

All letters are delivered as editable vector outlines, so installing the font is unnecessary. They are not live text. The original historical typeface has not been verified.

## Colour

The screenshot's embedded Apple Display ICC profile was converted to sRGB before measuring colours. The chosen values are robust estimates from petal interiors:

| Colour | sRGB |
| --- | --- |
| Blue | `#0E218B` |
| Green | `#02763F` |

These are approximate colours recovered from the supplied reference. They are not verified original brand or print specifications. The grayscale variant uses `#737373` for the grey fills and black outlines.

## Differences between the references

The monochrome header shows grey petals with black outlines, not simply grey conversions of the coloured petals. Its gaps also appear narrower. The grayscale lockup therefore uses a separate low-parameter fit to that printed specimen, including its overall aspect ratio. Printing, scanning and the low image resolution could explain part of the difference; the two screenshots do not establish two distinct historical master drawings.

The full-colour lockup combines the coloured emblem reference with the lettering arrangement from the monochrome header. That complete coloured arrangement has not been independently verified as an original specimen. The original page's horizontal rules are excluded from all logo assets.

## Comparison and verification

The final simplified colour emblem achieved **92.5% silhouette intersection-over-union** with a thresholded, colour-managed source after translation, uniform scaling and a small horizontal registration adjustment. The delivered master itself remains square. The comparison image shows shared silhouette in dark grey, source-only pixels in cyan and vector-only pixels in magenta.

This is a pixel-overlap check against a blurred and irregular screenshot. It is not an authenticity score or a claim of exact historical recovery. Remaining differences mostly occur at rounded cap edges and individual petal positions that vary in the source.

The four production SVGs were checked for zero raster images and zero live text elements. The three-page PDF was checked for zero embedded images and vector drawing operations on every page. The vector artwork and comparison sheets were visually reviewed for colour order, spelling, spacing and clipping.

## Editing or rebuilding

Open the SVGs in a vector editor. Ungroup a lockup to edit its emblem, name or tagline. The black SVG is a convenient starting point for another single-colour treatment.

To recreate the four SVG arrangements from their geometric parameters and the supplied lettering outlines, use Python 3:

```sh
python source/rebuild_vectors.py --output recreated-vectors
```

The script needs only the Python standard library. It does not read or trace the screenshots and does not require the original fonts. PNG and PDF exports are not regenerated by this small script.

## Evidence

The only visual sources used were the two screenshots supplied with the request:

- `Screenshot 2026-11-12 at 10.25.50 AM.png` — blue-and-green emblem.
- `Screenshot 2026-11-12 at 10.07.15 AM(1).png` — monochrome header with organization name and tagline.

This package is a reconstruction, not recovered original vector artwork.
