# Historic Crown corporations: vector search and rebuilds (2026-11-16)

This package finds or rebuilds SVGs for 24 raster assets of historic B.C. Crown corporations.
It holds 15 new SVGs: 3 native PDF vector extractions and 12 labelled reconstructions.
The records, ready to merge into `src/gallery/collectedData.js`, are in `proposed-assets.json`.
Every source tried is listed in `source-register.json`. Overlays and side-by-side comparisons are in `review/`.

## Native vectors found (PDF paths, no tracing or recolouring)

| Target | New file | Source |
|---|---|---|
| BCTC 2006 service-plan JPEG | `bc-transmission-corporation/bc-transmission-corporation-2004-annual-report.svg` | 2004 Annual Report (Wayback, bctc.com), p. 55 |
| PCT 2009 CNAR JPEG | `pacific-carbon-trust/pacific-carbon-trust-2011-service-plan.svg` | 2011/12–2013/14 Service Plan (bcbudget), p. 1 |
| BCBC 2003 service-plan bitmap | `bc-buildings-corporation/bc-buildings-corporation-2000-services-folder.svg` | BCBC Services folder, March 2000 (Wayback, bcbc.bc.ca), p. 1 |

- **BCTC:** an overlay with the 2006 JPEG agrees in outline (IoU 0.90 with JPEG blur). The JPEG prints the greens darker.
- **PCT:** the 2009 JPEG is the same stacked design, squeezed to about half its width.
- **BCBC:** a reversed white version of the same drawing is on the 2001 annual report cover.

All three were extracted with `scripts/extract.py`, which writes the PDF's own fills and fill rules for every drawing inside a clip box.

## Reconstructions (each labelled `reconstruction: true`, `vector-reconstruction`)

Shapes were fitted to the best available scan by a coordinate-descent overlap (IoU) fit (`scripts/fitlib.py`).
Lettering is set in outlined fonts. Spacing is fitted by moving whole letters; no letter is narrowed or distorted.
No bitmap tracing was used anywhere.

- **UTA double arrow (1980):** two 45° polygons, the lower a half-turn of the upper. IoU 0.97.
- **UTA 1980 regional signature:** the same arrow, with the lines in Nimbus Sans Bold. The ad's halftone bands and the "6-28" code are omitted.
- **UTA Commons drawing:** a vector copy of the 2020 third-party PNG, with the arrow and Nimbus Sans Regular. Its orange panel is kept. This is not evidence of the originals.
- **BCDC 1985:** the gallery's own BC Flag Symbol (flagMark.js plus the flag renderer's outlined BC). The flag's size and place are fitted to the microfiche.
- **LWBC 2004:** constructed square, triangle and sun, Bézier water bands, and P052 Bold (Palatino clone) lettering.
  - The fit is to the colour 2004/05 cover image, because the 2003/04 target is a grey scan.
  - The serif is not identified.
  - Colours are sampled. The grey scan shows heavier waves.
- **BCAL 1999 letterhead:** URW Bookman Light Italic, a close fit. The letterhead's vertical rule is not drawn.
- **BCRIC 1979 wordmark:** Gelasio Bold led the original study (IoU 0.77). A later comparison of six historical styles found that Gelasio also fit both printed brochure impressions more closely. The original face is unidentified. The green is sampled. [Historical specimens, scores and overlays](../bcric-wordmark-comparison/README.md)
- **Expo 86 CIPO 1982 symbol:** rings, a bar and round-ended strokes, with true arcs. IoU 0.97.
- **Expo 86 1986 wordmark:** capsules and rings, white for a dark ground. The ™ is omitted. IoU 0.95.
- **Shared Services BC 2006/07 and 2015, and Solutions BC 2006 letterhead:** composed from the gallery's Best Place on Earth mark (`src/assets/oneOffMarks.js`, drawn by `src/gallery/renderOneOff.js`, so the sun glow is radial gradients).
  - Shared Services BC uses the Province's Garamond letters lifted from the gallery's one-offs (`scripts/ssbc-compose.mjs`). Each letter is placed where the 2015 brochure prints it.
  - Solutions BC uses PT Sans outlines (`scripts/solbc-compose.mjs`). The original humanist sans is unverified.

## Not done

| Target | Why |
|---|---|
| Toll Authority ferry emblem (1960) | Halftone tonal sky and sea, plus a hand-drawn gull and flag. Rebuilding it would be guesswork. |
| Ferry Authority dogwood flag and 1964 signature | The device is 99 × 95 px. The signature is mostly the advertisement's typeset address lines. |
| BCRIC certificate header and full certificate | Detailed engraved family illustration and context scan. Not a logo. |
| UTA 1979 italic signature | Custom italic lettering interleaved with the ad's border strokes. Which strokes belong to the mark cannot be settled at 455 × 112. |
| BC Enterprise Corporation 1988 | A photograph with a strong colour cast. The symbol's parts are not legible enough. |
| BCeID (reversed), named in the brief | No such asset was in this target list. Not searched. |

## Limits and how to rerun

- **Script paths:** the scripts were run from this session's scratchpad. Paths to downloaded PDFs (`dl/…`) and to work images are scratchpad-relative. The PDFs are identified by URL and sha256 in `source-register.json`.
- **Fonts:** fonts are from the system URW set or Google Fonts (OFL), and none is the verified original. Instances were made with `fonttools varLib.instancer` (EB Garamond, Gelasio etc.).
- **Rendering:** checks used resvg (`scripts/render.js`).
- **Dates:** every date is a sighting, not an adoption date.
