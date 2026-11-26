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
| Prince George | blue and white vectors | 2025 Annual Report (PDF pp. 1 and 114) | Horizontal versions of the refreshed signature. The matching stacked website vector remains open. The City’s [May 6, 2024 agenda](https://www.princegeorge.ca/city-hall/mayor-council/meetings-agendas-minutes/regular-council-meeting-157) links the presentation, and the staff report identifies a separate brand guide. |
| Prince George, earlier signatures | source vectors | 2024 Annual Report (PDF p. 14), 2020 Climate Change Mitigation Plan (PDF p. 58), 2026–2030 Capital Projects Summary (PDF p. 1) | Earlier stacked signature in blue and black and in white, plus a separate single-line header using the earlier fraise. |
| Prince Rupert | vector, **different lockup** | Complete Community Assessment & Plan 2024 (p. 1) | This is the full logo: the red arch over "The City of Prince Rupert". The website PNG is a wider wordmark-only arrangement, which was not found as a vector. |
| Quesnel (×2 targets) | vector ×2 | Brand Guidelines v02, Dec 2016 (p. 7) | Same design. The website PNGs draw "Quesnel" and the wave taller relative to "City of", so the proportions differ. |
| Richmond | vector | Council Strategic Plan term highlights, Jul 2026 (p. 1) | same design and colours |
| Smithers | vector ×2 | New Resident Guide 2026: stacked with a slate name (p. 2); horizontal with a white name and tagline (p. 1) | The website PNG is stacked with a white name and the tagline. Neither PDF version has that exact combination. |
| Terrace | blue-and-white vector | 2016 Parks and Recreation Master Plan (PDF p. 1, original 114-page file) | The supplied cover crop preserves the bear, semicircle and lettering as paths. The full-colour logo is isolated from the blue page field. The City’s reduced PDF contains a raster logo. |
| Victoria | vector | 2025 property tax information sheet (p. 4) | Same design. The blue is slightly lighter and the lettering pure black. The annual-report covers carry only the white and black versions. |
| Williams Lake | vector coat of arms | 2011 Annual Report (PDF p. 1) | The arms are drawn with native paths and axial and radial shadings. The separate blue and yellow website badge is an embedded image in the Strategic Plan and the OCP engagement PDFs. |

All 19 SVGs are in `public/identity-municipal/<body>/` beside the PNGs.

The [2012 Northern British Columbia Travel Guide](https://digitalcollectionsrepository.llbc.leg.bc.ca/server/api/core/bitstreams/a30e5117-4e75-43f6-b52e-017cdba837e7/content#page=34) also documents the Fort St. John horizontal signature in black. The city’s [Promotional Marketing and Giveaways Policy](https://www.fortstjohn.ca/media/file/27-promotional-marketing-and-giveaways-policy#page=1) identifies the city’s Graphics Standard Manual as available on request. The manual is an open lead for the horizontal colour artwork.

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
