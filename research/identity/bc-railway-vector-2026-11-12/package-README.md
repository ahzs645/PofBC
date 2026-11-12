# British Columbia Railway Company: main and letterhead variants

Prepared from the supplied **FIA_2024.pdf**, 12 November 2026.

## What was produced

Two separate wordmarks appear in the supplied report:

| Variant | Source | Typeface finding | Method |
| --- | --- | --- | --- |
| **Main cover logo** | Page 1, repeated on page 36 | **Eurostile Demi**, widened and given an oblique treatment | Rebuilt from genuine typeface curves and fitted to the cover image |
| **Management letterhead** | Page 3 | **Verdana Bold Italic**, confirmed by the embedded font and actual text | Direct extraction of the original glyph outlines and placements |

The main cover wordmark is the primary deliverable. Both SVGs contain 29 individual letter paths grouped into the four original lines. Neither SVG contains embedded images or live text. They remain editable and scalable without installing either font.

These are additional variants. They are distinct from the heavier, white-edged wordmark reconstructed earlier using Myriad Pro Black Condensed Italic.

## Main cover logo

The cover logo in the report is a **600 × 327 pixel JPEG**, not native vector lettering. Its font therefore cannot be identified directly from that image's PDF metadata.

The closest measured match is the normal-width **Eurostile Demi** cut, with a shared horizontal expansion and slant. Genuine Eurostile Demi outlines from the MaxLite type specimen match all 29 letters closely. The nominal Extended Bold cuts were tested and rejected because their weight and the proportions of M, W and O differ from the supplied cover artwork.

The reconstruction keeps the original font curves intact. It uses a common linear transformation for the blue letters, a common larger size for the four red initials, and measured translations for each letter. It does not substitute traced pixel contours, apply individual width distortions, or use an offset stroke to disguise a different weight.

| Setting | Value |
| --- | --- |
| Font used for construction | Eurostile Demi |
| Horizontal expansion relative to equal height | Approximately 131% |
| Forward slant | Approximately 15.4 degrees from vertical |
| Red initial size | Approximately 122.1% of the blue-letter size |
| Red, sampled from cover image | **#E63C2B**, RGB 230, 60, 43 |
| Purple-blue, sampled from cover image | **#3A3376**, RGB 58, 51, 118 |
| Final canvas | 552 × 246 units, transparent |
| Source image crop | x=12 to 564, y=30 to 276 |

The measured full-wordmark silhouette overlap is **0.9703** intersection-over-union, with a mean per-letter value of **0.9714**. These measure geometric agreement, not the probability that the historical attribution is correct. Minor contour differences are visible at the JPEG's pixel scale. No original BCRC production file or brand specification confirming the exact historical typeface setup was recovered.

The colours are sampled RGB values, not verified Pantone or CMYK specifications.

## Management letterhead variant

Page 3 contains native text using the embedded font **HBOKZK+Verdana-BoldItalic**. The delivered paths come directly from that font and preserve the source's individual character origins, size changes and line positions.

| Letter group | Original size |
| --- | --- |
| All blue letters | 11.04 pt |
| Red B, first red C and red R | 12.96 pt |
| Final red C in COMPANY | 14.04 pt |

The final red C is larger than the other red initials in the PDF; that difference is retained. The source colours are preserved exactly: red **#FF0000** and blue **#0000FF**.

The standalone canvas is approximately **96.7493 × 52.6214 units**, including 2 units of padding around the original outlines.

## Files

- **BCRC-main.svg** — primary cover-logo vector master.
- **BCRC-letterhead.svg** — exact outlined letterhead variant from page 3.
- **BCRC-main.pdf** — primary logo as a vector PDF. It contains 29 drawn letter shapes, zero images and zero font resources. Page size is approximately 194.7 × 86.8 mm; it can be scaled to another size.
- **BCRC-main.png** and **BCRC-letterhead.png** — transparent convenience exports, each 2400 pixels wide.
- **BCRC-variants-comparison.png** — reference, main rebuild, alignment overlay and letterhead variant on one review sheet.
- **bcrc_variants_geometry.json** — final paths, per-letter grouping, colour, source placements and provenance for both variants.
- **rebuild_variants.py** — Python 3 standard-library script to regenerate both SVGs from the JSON. No font installation is required.

Open the SVGs in a vector editor and ungroup a line to edit its individual letter shapes. These are outlined objects, rather than live text that can be retyped. No standalone commercial font files are included.

To regenerate the SVGs:

```sh
python rebuild_variants.py
```

## Evidence and provenance

1. **FIA_2024.pdf**, supplied with the request: page 1 cover image and page 3 native letterhead text. Page 36 repeats the cover graphic.
2. [MaxLite 2016 Brand Style Guide](https://www.maxlite.com/PDFs/MaxLite_2016_Style_Guide.pdf), printed page 11 / PDF page 11: full Eurostile family alphabet specimens. The actual embedded Demi program is identified as **DXDIUK+Eurostile-Demi**, with Demi weight and Eurostile copyright/trademark metadata. This supplies the authentic typeface curves; it is not a BCRC brand guide.

The cover logo is a faithful font-based reconstruction. The letterhead logo is a direct recovery of native PDF lettering.
