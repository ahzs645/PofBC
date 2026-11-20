# British Columbia Forest Service raccoon advertisement

Recreated 20 November 2026 from the original advertisement in **Gulf Islands Driftwood, 2 December 1971, printed page 11**, using the user's supplied raccoon photograph and the existing PofBC Forest Service emblem geometry.

## Open these files

| File | Purpose |
|---|---|
| `Forest_Service_Raccoon_Ad_Editable.svg` | Layered artwork with five editable text lines, an embedded photograph, and vector panels, border and emblem. |
| `Forest_Service_Raccoon_Ad_Outlined.svg` | Same design with lettering converted directly from font glyphs to paths. Use for reliable sharing and import. |
| `Forest_Service_Raccoon_Ad.pdf` | One-page print artwork. Lettering, panels, border and emblem remain vector; the photograph remains raster. |
| `Forest_Service_Raccoon_Ad.png` | 1130 x 2088 pixel preview. |
| `Forest_Service_Raccoon_Comparison.pdf` | Original scan beside the reconstruction, with a short explanation. |
| `Forest_Service_Raccoon_Comparison.png` | Image version of the comparison proof. |
| `Forest_Service_Raccoon_Review.html` | Self-contained comparison viewer with a side-by-side view and an adjustable opacity overlay. Open locally in a browser. |
| `fonts/` | Desktop font, web font, original Jost source, font build script, and SIL Open Font License. |
| `assets/` | Supplied photograph, unchanged PofBC colour master, and the derived newspaper paint treatment. |
| `reference/` | Original ad crop, source provenance, placement data, typography notes, and verification record. |

## What was reconstructed

The design follows the source's 565 x 1044 proportions. The photograph is positioned at x 60, y 17, width 452; its supplied aspect ratio is preserved, without cropping or retouching. The main panel is at x 75, y 714, 420 x 116. The signature panel is at x 94, y 870, 401 x 115. The border is rebuilt as a clean four-unit rectangle.

The original copy and line breaks are retained:

> With proper management  
> British Columbia’s forests  
> will last a coon’s age.

The issuer is set on two lines: **British Columbia** / **Forest Service**.

The photograph is the supplied 1040 x 1513 image. It is not claimed to be the original archival photographic master. Its pixel content is unchanged. All other visible components are vector objects or editable font text. No automatic tracing was used.

## Typography: identification and working substitute

**Likely historical family: Futura oblique, in a medium-to-demi/bold print weight.** The single-storey a and g, geometric bowls, oblique stems and straight-footed t support this reading. The available scan does not establish the exact foundry, cut or weight, and related geometric sans families cannot be ruled out. The PDF's invisible OCR fonts do not identify its printed lettering.

**Font actually used: Jost Italic, weight 600**, packaged as the static working font **Forest Ad Sans SemiBold Italic**. Jost's author describes it as an interpretation of Futura with deliberate differences. It is a substitute, not an authenticated historical font. The W, r, capital proportions and some spacing remain different from the source.

The current Jost italic has a single-storey a by default. The working font preserves it and disables its optional double-storey alternate. Glyph outlines were not traced or redesigned. The font is renamed and supplied under the original SIL Open Font License, with its source and rebuild script.

The lettering is set at 34 working units, with 96% vertical scale, a small reduction in slant, and separate tracking adjustments for each line. Measured target ink widths are 409, 404, 351, 259 and 214 units. Fitting these widths is a placement technique; it is not a font-identification accuracy score. The first three baselines are 745, 782 and 818; the footer baselines are 911 and 948.

For desktop text editing, install `fonts/ForestAdSans-SemiBoldItalic.ttf` before opening the editable SVG. An embedded web font also supports compatible browser previews. SVG font embedding support varies between design programs; the outlined SVG and PDF are the stable alternatives. Keep `fonts/OFL.txt` with any redistributed font.

## Emblem treatment

The emblem comes from the user-selected [PofBC Forest Service emblem page](https://projects.ahmadjalil.com/PofBC/?view=internal&internal=forests&internal-logo=forest-service-emblem), at repository revision `00cf5d68d7574897a52414f8b0744c1a4c0e508d`.

The source colour master has a bowed badge, a provincial mainland, three detached islands, a triangular conifer crown and a trunk. Their path coordinates are retained. The newspaper treatment changes paint only: a dark badge, a light border, an outlined mainland, light islands and a light filled tree. This is a separate treatment from the site's filled one-ink silhouette, which does not match the construction visible in this ad.

The complete emblem is placed proportionally in a 114 x 121 frame, preserving the square master. Its tree is broader than the one in the newspaper impression; the coastline and island spacing also differ slightly. These differences remain because the requested PofBC vector geometry is retained. Both the PofBC asset and this treatment are reference-based reconstructions, not authenticated official historic masters.

## Colour and print size

The clean paper field is `#E9CDAD`; the dark ink is `#3D372F`. These are reproduction choices informed by the scan, not verified historic colour specifications. The supplied photograph keeps its original colour and halftone texture.

The PDF and SVG are set to **100 mm wide x 184.78 mm high**. This is a convenient export size, not a verified original physical advertisement size. At that size the photo is 80 mm wide, providing approximately 330 pixels per inch. Borders, lettering and emblem can scale without loss; photo resolution decreases when the whole ad is enlarged. The PDF is RGB artwork without added bleed or printer marks.

## Review and rebuilding

The comparison viewer registers the two full artboards; the opacity slider is a visual inspection aid. It is not a claim of pixel-identical reproduction. The source contains scan skew, irregular ink edges and paper noise; the reconstructed layout uses clean geometry and the user-supplied image.

The final PNG and PDF were visually reviewed. The editable SVG and outlined SVG were rendered at the same size and compared; their lettering agreed to subpixel rasterization differences. The photograph embedded in each SVG was verified against the supplied file. Emblem path coordinates were compared with the selected source master. The original line breaks and punctuation were checked. The optional HTML viewer's script syntax and embedded images were checked; interactive browser validation could not run in the production environment, so its browser behavior is not claimed as verified.

To rebuild, install Python 3 with Pillow (RAQM text shaping), fontTools and reportlab, plus Inkscape and Poppler. Run `python3 build_ad.py`. The report proof uses the standard DejaVu Sans installation at `/usr/share/fonts/truetype/dejavu`; change those two paths for another system. The supplied static font is sufficient to rebuild the art. `fonts/build-font.py` can regenerate it from the included Jost variable font.

## Sources

1. [Gulf Islands Driftwood, 2 December 1971, page 11](https://saltspringarchives.com/driftwood/1971/v12n47Dec2-1971.pdf#page=11).
2. [PofBC source emblem SVG, pinned revision](https://github.com/ahzs645/PofBC/blob/00cf5d68d7574897a52414f8b0744c1a4c0e508d/src/internal/forest-service-emblem.svg).
3. [Jost author's design explanation](https://indestructibletype.com/Jost).
4. [Google Fonts Jost distribution and license](https://github.com/google/fonts/tree/main/ofl/jost).

## In this repository

Kept: this README, `build_ad.py`, `SHA256SUMS.txt` (the supplied hashes, including files not kept),
both SVG masters, `assets/raccoon-supplied.png` (the supplied photograph, unchanged),
`assets/forest-service-emblem-newspaper.svg`, the `reference/` JSON and Markdown, and `fonts/`
(Jost Italic, the derived Forest Ad Sans TTF and WOFF, `build-font.py`, `README-font.txt` and
`OFL.txt`, under the SIL Open Font License).

Changed: the two SVG masters name the photograph as `assets/raccoon-supplied.png` instead of
embedding it as base64 (5.5 MB each); otherwise they are as supplied, so their hashes no longer
match `SHA256SUMS.txt`. `build_ad.py` writes the embedded versions again.

Left out: the newspaper scan (`reference/original-ad-1971-12-02.png`), the font comparison image,
the PNG and PDF exports, the comparison PDF and PNG, the review HTML, and
`assets/forest-service-emblem-original.svg`, which is a copy of this repository's
`src/internal/forest-service-emblem.svg`. `build_ad.py` reads the newspaper treatment, not that copy,
for the artwork; its comparison proof needs the scan.

The Posters view (`?view=posters&poster=coons-age`) shows `src/posters/forest-service/coons-age.svg`
with the photograph as `coons-age-raccoon.webp`: see `../README.md`.

