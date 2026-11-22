# Municipal logos: vector sources (2026-11-16)

Vector copies of the B.C. municipal logos that the gallery held only as website PNGs. Targets came from
`municipalIdentityData.js`: 18 raster records across 17 municipalities.

The search went in this order:

1. **The websites themselves.** All 17 homepages were fetched. Every header logo is a PNG. None of them
   serves the logo as an SVG file, an inline `<svg>` or an SVG favicon.
2. **Brand guides.** Mackenzie (Brand Book V2, 2018) and Quesnel (Brand Guidelines v02, 2016) publish
   theirs. Smithers, Abbotsford, Coquitlam and Kamloops supply guides or logo files only on request.
3. **City PDFs.** For every other municipality, the logo came from a PDF the city published itself:
   annual reports, plans, profiles and information sheets made in InDesign. PDFs made with Word, Canva,
   Publisher, Piktochart or a scanner almost always carry the logo as an image, so they were rejected.
4. **The Wayback Machine.** The CDX API was "Temporarily Offline" or returned 502/504 for the whole
   session, so no archived SVGs could be checked.

`source-register.json` lists every URL tried, with what it gave.

## Results

| Municipality | Result | Source (PDF page) | Match to the website PNG |
|---|---|---|---|
| Abbotsford | vector | 2025 Annual Report (p. 140) | same design and colours |
| Burns Lake | vector | 2024 Interim Housing Needs Report (p. 1) | same design and colours |
| Chilliwack | vector ×2 | Corporate Climate Action Plan 2022 (p. 1): horizontal; City Climate Actions summary 2022 (p. 1): stacked | The horizontal lockup is the website's arrangement, but in this printing "City of" is dark green and the snowcaps are open. The stacked lockup has the website's colours and white ground. |
| Coquitlam | vector ×2 | 2025 Treasury Report: white (p. 1), blue (p. 12) | The white version is what the website shows (the website file adds a drop shadow). |
| Dawson Creek | vector | Community Profile 2024 (p. 40) | Same design and colours. The steps at the foot of the building are drawn slightly differently. |
| Fort St. John | vector, **different lockup** | Official Community Plan bylaw, Dec 2025 (p. 1) | Same logo and colours, but **stacked**. The website PNG is horizontal, and no horizontal vector was found. The cover of the 2025 annual report has only a white stacked version. |
| Kamloops | vector (with gradients) | Annual Report 2025 (p. 142) | Same artwork, with the tagline in white as on the website. See below. |
| Mackenzie | vector | Brand Book V2, Nov 2018 (p. 2) | same design and colours |
| Nanaimo | vector | 2025 Annual Report (p. 1) | Same design. The print colours are brighter process blues and the waves have thin black keylines. |
| Prince George | vector, **different lockup** | 2025 Annual Report (p. 1) | Same 2024 logo and colour, but **horizontal**. The website PNG is stacked. Every vector instance found is horizontal. |
| Prince Rupert | vector, **different lockup** | Complete Community Assessment & Plan 2024 (p. 1) | This is the full logo: the red arch over "The City of Prince Rupert". The website PNG is a wider wordmark-only arrangement, which was not found as a vector. |
| Quesnel (×2 targets) | vector ×2 | Brand Guidelines v02, Dec 2016 (p. 7) | Same design. The website PNGs draw "Quesnel" and the wave taller relative to "City of", so the proportions differ. |
| Richmond | vector | Council Strategic Plan term highlights, Jul 2026 (p. 1) | same design and colours |
| Smithers | vector ×2 | New Resident Guide 2026: stacked with a slate name (p. 2); horizontal with a white name and tagline (p. 1) | The website PNG is stacked with a white name and the tagline. Neither PDF version has that exact combination. |
| Terrace | **not done** | — | Every colour copy found is an embedded image (annual reports 2022–2025, budget, climate plan). The only vector copy is a one-colour newspaper-notice version built from hairline-outlined paths and clips. A plain path extraction does not reproduce it, and it is not the colour logo. |
| Victoria | vector | 2025 property tax information sheet (p. 4) | Same design. The blue is slightly lighter and the lettering pure black. The annual-report covers carry only the white and black versions. |
| Williams Lake | **not done** | — | The badge is an embedded image in every PDF checked. The Strategic Plan is an InDesign file but places the logo as an image, and the OCP engagement PDFs are flattened. No reconstruction was made: the badge uses gradients, and an official vector should exist. |

All 19 SVGs are in `public/identity-municipal/<body>/` beside the PNGs.

## Method

- `scripts/extract.py` (driven by `scripts/jobs.json`) keeps only the PDF drawings that fall entirely
  inside the logo's rectangle on the page, exactly as `pymupdf` `page.get_drawings()` reports them:
  - the paths are the PDF's own, in page coordinates;
  - each colour is the PDF's own colour, converted to RGB by MuPDF;
  - even-odd fills are kept as even-odd;
  - the `viewBox` is tight to the kept shapes plus a 0.5 pt margin.

  There is no tracing, redrawing or recolouring. Each job checks the PDF's SHA-256 before it runs.
- `scripts/kamloops_shading.py` handles Kamloops. The logo's colour ramps are 26 axial shadings (`sh`)
  painted inside clipping paths, and `get_drawings()` does not report those. The script replays the
  logo's own marked-content block (`/PlacedGraphic /MC0`) from the page content stream:
  - paths and clips are written exactly as drawn, with nested `clipPath`s for intersecting clips;
  - each shading becomes an SVG `linearGradient`. Its `gradientTransform` is the shading's matrix, and
    its stops are the shading's 64 sampled CMYK colours (type-0 functions with linear interpolation),
    so the ramp is exact. CMYK and the Cyan separation are converted to RGB by MuPDF;
  - the `viewBox` is the placed graphic's own clip rectangle.
- `scripts/build_proposed.py` writes `proposed-assets.json`. It reads each SVG's hash, size and
  `viewBox` from the file.
- `scripts/probe.py`, `hunt.py`, `scan.py`, `firstlast.py` and `inspect_region.py` are the triage tools:
  they download PDFs, find pages whose small vector fills use the logo's colours, and list the drawings,
  text and images in a region.
- The review images are made by `review.sh` (`render.mjs` with resvg, then `review.py`). Each one shows
  the website PNG (left) beside the vector (right), on white and on grey.

The PDFs are not kept in this package. Their URLs and SHA-256 values are in `source-register.json`.
To re-run, download them into a folder at the names that `jobs.json` gives and run
`python3 -I scripts/extract.py <folder>`.

## Limits

- **Dates.** Each date is the document's own publication or PDF-creation date, not an adoption date.
  The one exception is Prince Rupert: its release (princerupert.ca/node/647) says the arch logo was
  approved by Council on 28 February 2022.
- **Colours.** These are the print colours of each PDF as MuPDF converts them from CMYK. They can
  differ slightly from the website PNG's RGB, as with Nanaimo and Victoria.
- **Different lockups.** The Fort St. John, Prince George, Prince Rupert and Smithers vectors are other
  lockups or colourways of the same current logos, not the arrangement in the website PNG. They are
  proposed alongside the PNG, not as like-for-like replacements.
- **Quesnel proportions.** The website PNGs are proportioned differently from the 2016 guide's artwork.
  The website version may be a later redraw. That was not established.
