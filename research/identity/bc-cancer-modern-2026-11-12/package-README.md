# BC Cancer: modern vector logo collection

Research and source retrieval: November 12, 2026.

This collection contains eight verified vector logo variants, extending the older circular BC Cancer Agency emblem documented in the supplied README. The artwork comes from official websites and publications. Three SVG files are unchanged official downloads; five contain original vector path elements exported from official PDFs. No tracing, letter reconstruction, substitute fonts or invented colour variants were used.

## Files

Each basename below has an SVG in `svg/`, a vector PDF in `pdf/`, and a transparent PNG in `png/`. The PNGs are previews; the SVG and PDF files are the scalable artwork. White and reversed artwork is intended to be viewed against a dark background. PDF viewers commonly display a white page, so white artwork may appear blank until placed over a coloured background in a layout application.

| Basename | Artwork | SVG path count | Source |
| --- | --- | ---: | --- |
| `bc-cancer-phsa-colour` | BC Cancer - Colour + PHSA line | 41 | Wayfinding standards / PDF p.18 |
| `bc-cancer-research-colour` | BC Cancer Research - Colour + PHSA line | 47 + 2 polygons | Original SVG / official research site |
| `bc-cancer-research-white-purple` | BC Cancer Research - White + purple / 2018 report | 49 | 2018 Research Report / PDF p.1 |
| `bc-cancer-research-institute-white` | BC Cancer Research Institute - White / 2022 report | 58 | 2022 Research Report / PDF p.1 |
| `bc-cancer-foundation-2018-colour` | Foundation / earlier identity - Colour / 2018 report | 18 | 2018 Impact Report / PDF p.2 |
| `bc-cancer-foundation-2018-white-purple` | Foundation / earlier identity - White + purple / 2018 report | 18 | 2018 Impact Report / PDF p.24 |
| `bc-cancer-foundation-2026-navy-purple` | Foundation / current assets - Navy + purple / 2026 website asset | 9 | Original SVG / official media archive |
| `bc-cancer-foundation-2026-white-purple` | Foundation / current assets - White + purple / 2026 website asset | 9 | Original SVG / live official website |

`bc-cancer-modern-vector-preview.png` displays all eight variants. Dark backgrounds appear only on the comparison sheet; they are not baked into the SVGs, PDFs or transparent PNGs.

## Organization and date distinctions

BC Cancer announced its simplified name and the shared BC Cancer / BC Cancer Foundation identity on November 15, 2017. The stacked wordmark highlights CAN within CANCER. Official launch statement:

https://bccancerfoundation.com/news-and-media/blog/bc-cancer-and-bc-cancer-foundation-strengthen-partnership-break-down-cancer/

Official history:

https://www.bccancer.bc.ca/about/history

The Foundation is the fundraising organization associated with BC Cancer. Its newer 2026 website assets are distinct from the BC Cancer care and research marks. They use navy or white BC / CAN / CER lettering, a circular counter in A, and purple FOUNDATION below the stack. The two original media records are dated October 1, 2026. That date establishes the media-record timing; a precise public launch date was not established here.

https://bccancerfoundation.com/wp-json/wp/v2/media/101955
https://bccancerfoundation.com/wp-json/wp/v2/media/101956

The 2018 and 2022 names refer to the years of the source reports, not claims that those variants were first introduced in those years. The supplied 2018 Research Report was exported in 2019, and the 2022 Research Report was exported in 2023, according to their PDF metadata. Source metadata is retained in the manifest.

## Primary sources

### Main BC Cancer logo with the PHSA line

New Surrey Hospital & Cancer Centre, Appendix 1R: Wayfinding Standards & Requirements, PDF page 18. The internal wayfinding document is dated January 12, 2022; the public filename is a 2023 agreement appendix within an April 2024 upload directory. The logo contains 41 original paths. Crop bounds, checksums and verification are recorded in the manifest.

https://www.infrastructurebc.com/wp-content/uploads/2024/04/2023-09-01-NSHBCCC-DBA-Schedule-1-App-1R-Final.pdf

### BC Cancer Research: original colour SVG

The current research homepage links directly to this unchanged SVG:

https://www.bccrc.ca/themes/custom/bccrc/logo.svg

Referring page: https://www.bccrc.ca/

### BC Cancer Research: white and purple

2018 BC Cancer Research Annual Report, PDF page 1:

https://www.bccrc.ca/sites/bccrc.ca/files/BC%20Cancer%20Research%20AR%202018.pdf

### BC Cancer Research Institute: white

2022 BC Cancer Research Report, PDF page 1:

https://www.bccancer.bc.ca/Documents/2022_ResearchReport_FINAL_Web.pdf

### BC Cancer Foundation: earlier identity

BC Cancer Foundation Impact Report 2018, PDF page 2 (colour) and page 24 (white and purple):

https://bccancerfoundation.com/wp-content/uploads/2021/07/bccf_2018_annual_report_-_lowres_single_pages.pdf

### BC Cancer Foundation: current 2026 assets

Original navy/purple SVG:

https://bccancerfoundation.com/wp-content/uploads/2026/10/bccf-logo-dark.svg

Original white/purple SVG:

https://bccancerfoundation.com/wp-content/uploads/2026/10/bccf-logo.svg

The white variant is used in the live official website header/footer; the navy variant is published in the same official media archive. Referring site:

https://bccancerfoundation.com/

## Colour fidelity

Native SVG files retain their original colour values. For example, the official Research SVG specifies turquoise #35C1D4 and purple #9361A8. The PDF exports preserve their source-specific RGB rendering: the main logo and older Foundation logo export purple as #9361A9; the 2018 Research white/purple specimen exports it as #7B348C. These publication differences were not normalized or silently recoloured.

For independent print-colour evidence, page 18 of the wayfinding document labels BC Cancer Brand Colours as Pantone 3115 C (CMYK 66/0/17/0) and Pantone 2583 C (CMYK 47/72/0/0). These printed specifications are distinct from the RGB conversion in the extracted SVG artwork.

The newer Foundation files specify #072952 and #873199 in the navy version, and white plus #C550DF in the white version. Those are values in the original SVGs, not an inferred palette.

## Vector validation and provenance

All eight SVG files contain vector paths, have zero embedded raster images, and have no live text requiring a font. The Research website SVG also contains two polygons. Original website SVGs are copied unchanged. For PDF extracts, original exported path data and transforms are retained; the only assembly changes isolate the intended artwork and set its canvas.

The PDF companions were exported from the supplied SVGs. They are one-page vector files with zero embedded images and no font dependencies. They are convenient vector derivatives, not source-document crops. Full source publications are linked above rather than bundled.

`source-manifest.json` records each source, extraction bounds where applicable, checksums, colour notes, vector counts, metadata and output validation. `provenance/` retains detailed source records. The main BC Cancer extraction was additionally compared against a source render: binary silhouette overlap was 99.79%, with small antialiasing differences between rendering engines.

## Additional source lead

The wayfinding document references an October 2018 BC Cancer branding guideline, but a public complete master logo package or standalone copy of that guide was not recovered. The official BC Cancer media page directs logo requests to comms@bccancer.bc.ca:

https://www.bccancer.bc.ca/about/news-stories/media-enquiries
