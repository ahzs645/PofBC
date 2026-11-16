# Current bodies: vector search, 2026-11-16

Targets: 22 raster logos of current public bodies (website PNG/WebP, or images embedded in PDFs).
For each, the bodies' own websites, media libraries (WordPress `wp-json/wp/v2/media`), official
templates and PDFs (annual reports, service and strategic plans, terms of reference, toolkits) were
searched for the logo as vector artwork. Every URL tried, with its outcome, is in
`source-register.json`. The 12 new SVGs are listed, as records ready to merge, in `proposed-assets.json`.

## Results

| Target | Result | New file (under `public/`) |
|---|---|---|
| BC Pension Corporation | Vector: Wave 2 Strategic Plan cover (2024-03) | `identity-expanded/bc-pension-corporation/wave-2-strategic-plan-2024-colour.svg` |
| ETSI-BC | Vector of the full-name horizontal lockup (bylaws 2026, colour; CK-RAC terms 2024, white). The website's stacked short-name lockup was not found as vector. | `identity-expanded/etsi-bc/bylaws-2026-full-name-colour.svg`, `…/rac-terms-2024-full-name-reversed.svg` |
| Metro Vancouver Transit Police | Vector: 2025 Report to the Community cover, white, same lockup as the website PNG | `identity-expanded/metro-vancouver-transit-police/report-to-community-2025-reversed.svg` |
| E-Comm 9-1-1 | Vector: (a)SPIRE strategic plan cover (2019-04), same design as the website logo. Reports from 2021 on carry it only as images. | `identity-expanded/e-comm/aspire-strategic-plan-2019-colour.svg` |
| Liquor Distribution Branch | Vector: the LDB lockup isolated from the LDB Wholesale Operations website SVG (B.C. logo black, name #C60C46; the bcldb.com PNG has a grey B.C. logo and brighter red) | `identity-expanded/liquor-distribution-branch/ldb-wholesale-site-ldb-lockup.svg` |
| Vancouver Convention Centre | Vector of the one-colour white version (Sustainability Toolkit, 2026-08-20). The website logo's photographic letter fill is not in it. | `identity-expanded/sub-vancouver-convention-centre/sustainability-toolkit-2026-reversed.svg` |
| Simon Fraser University | Vector: SVG embedded in SFU's official PowerPoint template, kept byte for byte | `identity-expanded/simon-fraser-university/powerpoint-template-horizontal-colour.svg` |
| BCIB (mobile: helmet + BCIB) | Vector: helmet and letters isolated from the 2025/26 report cover | `identity-collected/bc-infrastructure-benefits/bcib-2026-short-reversed-source-vector.svg` |
| BCIB (Building Opportunity Here, stacked, reverse) | Not found. Only the horizontal tagline lockup exists as vector, and the repo already holds it (`vector-bcib-2025-tagline-reversed-source-vector`). | — |
| BCeID | Reconstruction: EB Garamond, outlined | `identity-collected/bceid/bceid-reversed-rebuilt.svg` |
| Compass needle symbol | Reconstruction: fitted geometry | `identity-expanded/compass/needle-symbol-rebuilt.svg` |
| Compass C symbol (website) | Reconstruction: same geometry, colours swapped | `identity-expanded/compass/c-symbol-rebuilt.svg` |
| Coast Mountain Bus Company | Not done. Raster everywhere checked; translink.ca's `cmbc_logo.svg` URL serves a 695 × 216 PNG (a better raster than the held one). | — |
| West Coast Express | Not done. Raster everywhere checked; `wce_logo.svg` URL serves a 2114 × 419 PNG. | — |
| Island Coastal Economic Trust | Not done. The 2026 Impact Report has the wordmark as vector but the paddle symbol as a 97 × 59 image; the symbol is too detailed to rebuild honestly from the website WebP. | — |
| Nechako-Kitamaat Development Fund | Not done. Every annual report and business plan from 1999 to 2026 (Word/PowerPoint exports) carries the logo as an image; the sun and script letters are too detailed to rebuild honestly. | — |
| BC Ferries Commissioner | Not done. Raster in every source; the seal holds the full-colour arms. | — |
| B.C. Ferry Authority | Not done. The website image is the name set in an unidentified bold serif; the Authority's reports set the name as live text in TheSerif, a different design. | — |
| Northern Development Initiative Trust | Not done. The site answers 403 to automated requests, and fetching its PDFs by other routes was declined by this session's permission system. Candidate PDFs (e.g. the 2026–2028 strategic plan) are listed in the register. | — |
| BC Cannabis Stores, BC Cannabis Wholesale | Not done. No vector found (Shopify PNGs; supplier PDFs carry images). The heavy sans of "BC CANNABIS" was not identified with confidence, and the 1200 px Stores PNG crops the tops of the letters, so a font rebuild would be a guess. | — |

## Method

**PDF extraction** (`scripts/pdfvec.py`, driven by `scripts/build.py`): the page is copied, everything
outside the logo's rectangle is removed with MuPDF redactions, and MuPDF converts the page to SVG with
text as glyph outlines. Glyph `<use>` references are inlined as `<path>`s. Raster `<image>` elements
(cover photographs behind or near the logo) are dropped. Any leaf shape whose bounds fall outside the
rectangle is dropped (this also removes off-page leftovers). The viewBox is fitted to the rendered
extent. Paths, transforms and fills are the PDF's own. No tracing or recolouring.

**SVG component** (`scripts/svgcomponent.py`): for the LDB lockup, the leaf elements of the official
SVG that lie inside the lockup's box are kept unchanged and the banner's elements removed.

**Reconstructions** (`scripts/rebuild/`):
- *BCeID* (`bceid.py`): the letters are set in EB Garamond (SIL OFL; Google Fonts) and converted to
  outlines with fontTools. The capitals are Regular (weight 400) and the e is Italic at weight 600,
  each weight chosen by best overlap with the source. Each letter is scaled to its height in the
  220 × 58 source and placed in its measured box. Overlap with the source (IoU) is 0.79 for the
  capitals and 0.65 for the e. Gold #E3A82B is sampled. The exact Garamond cut is not verified.
- *Compass* (`compass_fit.py`, `compass_build.py`): the needle is a large circle joined by its
  tangents to a small rounded tip; the C is a ring cut by two horizontal lines. Circle and ring
  parameters are optimised for overlap with the 561 px needle PNG. The cut heights are measured from
  the image. IoU: needle 0.998, C 0.987, and 0.997/0.990 against the 81 × 80 website sprite. Colours
  are sampled: #0099CC (needle PNG) and #009DDC (website sprite).

To rebuild: download the PDFs named in `scripts/build.py` (URLs in `source-register.json`) into a
folder and run `python -I scripts/build.py FOLDER` from the repo root. Hashes are checked. For the
reconstructions, run `python -I scripts/rebuild/bceid.py <bceid png> <font dir> <out.svg> <review.png>`
and `python -I scripts/rebuild/compass_build.py <needle png> <sprite png> <out dir> <review dir>`.
Requires PyMuPDF 1.28, fontTools, svgelements, scipy and the repo's `@resvg/resvg-js`.

## Review images

`review/*.webp`: for extractions, the source page region (left) beside the SVG (right). For
reconstructions, the source (red channel) over the rebuild (cyan): white is agreement.

## Limits

- Extracted components (Pension, BCIB, LDB) are parts of larger official lockups, not standalone
  masters.
- ETSI, Transit Police and VCC finds are official vectors but not the exact file the website shows:
  a different lockup (ETSI), or a one-colour version (VCC). They are labelled as such in `notes`.
- The E-Comm find dates from 2019. The design matches the current website logo, but no later vector
  sighting was found.
- Source PDFs are not stored here, because of their size. `build.py` checks the SHA-256 of each
  re-downloaded file.
