# Wordmark reconstruction notes

Source: `bc-assessment-map-1982-letterhead.png`, 1605 × 450 pixels.

The wording is **BRITISH COLUMBIA** and **ASSESSMENT AUTHORITY**. The supplied `work/wordmark.svg` retains source coordinates and contains 34 outlined glyph paths in two semantic groups. It has no raster or live-text dependence. Its path contours derive from Nimbus Sans Bold; the same glyph contour, scale, and weight are used for every occurrence of a letter. Position varies to reproduce the letterhead spacing.

Nimbus Sans Bold is a reconstruction substitute, not an authenticated identification of the original metal type or phototypesetting face. A six-family local comparison tested Nimbus Sans Bold, Liberation Sans Bold, DejaVu Sans Bold, Noto Sans Bold, Open Sans Bold and Open Sans ExtraBold. Moderate weight expansion of Nimbus gave the lowest averaged normalized glyph-shape residual (0.04667, vs 0.04911 for the best Liberation treatment). This statistic chooses among the tested candidates only; it is not a confidence probability for font identity.

Font outlines use a common scale of 0.03435 horizontally and 0.03420 vertically from 1000-unit glyph coordinates. Their common black outline stroke is 31 font units, equivalent to about 1.06 source pixels total, or 0.53 pixels outward on either edge. This models the visibly heavy printed letter shapes without keeping scan defects. Stroke-to-path conversion may be performed downstream for a fully expanded all-fill export.

The left block nominal baseline is y = 182.7756 − 0.00112214(x − 210). The right baseline is y = 180.1652 − 0.00371425(x − 760). A single least-squares line across all source glyphs is y = 184.354267 -0.00490988x, corresponding to -0.2813 degrees. A global positive rotation of about 0.281 degrees therefore removes the overall rising scan trend, although local baselines differ due to scan/print distortion.

## Registered comparison

| Metric | Left text | Right text |
|---|---:|---:|
| Raw binary ink intersection over union | 83.70% | 83.14% |
| Source ink within one source pixel of vector ink | 99.88% | 99.75% |
| Vector ink within one source pixel of source ink | 99.84% | 99.59% |

The comparison uses original scan coordinates before any deskew in the final logo. Raw differences include print voids, jagged scan contours and the intended smoothing. The toleranced statistics describe positional agreement, not proof of exact historical font identity.
