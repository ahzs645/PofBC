# Official logo vector recovery — 21 November 2026

This batch adds 13 original SVG/PDF pairs to the PofBC gallery, using official source PDFs.
The new search is registered in the existing identity-expansion builder.


## What was recovered

Thirteen source-derived specimens across eight identities, supplied as 13 SVGs and 13 corresponding vector PDFs.
All SVGs contain original vector outlines, with no embedded images or live text. All PDF counterparts contain
zero images, zero font resources and zero extracted text. Northern Development's original gradient shadings
remain native SVG gradients.

| Identity | Recovered treatment(s) | Gallery effect |
| --- | --- | --- |
| BC Cannabis Wholesale | Black and white horizontal wordmarks, without underline | First native vector; existing underlined website image retained separately |
| Liquor Distribution Branch | White provincial-symbol lockup | Adds an evidenced variation to an identity already held as vector |
| Northern Development Initiative Trust | Stacked and horizontal; colour and gradient/white treatments | First native vectors; stacked and horizontal groups remain separate |
| Consumer Protection BC | Colour and reversed horizontal corporate marks | First native vectors; existing matching website image retained |
| Island Coastal Economic Trust | Earlier four-line white wordmark | First native vector for the subject; current paddle design remains unresolved |
| Elections BC | Colour symbol/name with original Legislature tagline | First native vector for the matching existing lockup |
| Forest Practices Board | Ordinary colour horizontal mark | First native vector; anniversary artwork remains separate |
| GameSense | White capsule with green letters and white BCLC endorsement | First native vector; standalone website capsule remains a separate design |

## Official sources

Page numbers are one-based PDF pages. Path counts include any clipping paths. Exact source hashes,
crop boxes in top-left PDF points, output hashes and comparison details are in source-register.json.
Document periods and URL-directory dates are recorded as source context, never as inferred logo adoption
or retirement dates.

| Specimen | Official document / date context | PDF page | SVG paths |
| --- | --- | ---: | ---: |
| BC Cannabis Wholesale – official black wordmark | [March 2026 shipping requirements guide](https://www.bcldb.com/sites/default/files/2026-06/Wholesale_Shipping_Guidelines_March_2026.pdf) | 1 | 19 |
| BC Cannabis Wholesale – official reversed wordmark | [FY2026 Q2 quarterly sales report](https://www.bcldb.com/sites/default/files/BC%20Cannabis%20Wholesale%20Quarterly%20Sales%20Report%20--%20Q2%202026.pdf) | 1 | 19 |
| Liquor Distribution Branch – official reversed lockup | [FY2026 Q2 quarterly sales report](https://www.bcldb.com/sites/default/files/BC%20Cannabis%20Wholesale%20Quarterly%20Sales%20Report%20--%20Q2%202026.pdf) | 1 | 44 |
| Northern Development – stacked, gradient symbol and white name | [2023 annual report; official URL path includes /2024/05/](https://www.northerndevelopment.bc.ca/wp-content/uploads/2024/05/NDIT_2023-AR-_Web.pdf) | 51 | 37 |
| Northern Development – stacked, colour | [2020 annual report; official URL path includes /2021/04/](https://www.northerndevelopment.bc.ca/wp-content/uploads/2021/04/NDIT2020AR_Final_Web.pdf) | 1 | 27 |
| Northern Development – horizontal, colour | [2020 annual report; official URL path includes /2021/04/](https://www.northerndevelopment.bc.ca/wp-content/uploads/2021/04/NDIT2020AR_Final_Web.pdf) | 13 | 26 |
| Northern Development – horizontal, reversed | [2023 annual report; official URL path includes /2024/05/](https://www.northerndevelopment.bc.ca/wp-content/uploads/2024/05/NDIT_2023-AR-_Web.pdf) | 1 | 26 |
| Consumer Protection BC – colour corporate logo | [2017 annual report; official URL path includes /2018/06/](https://www.consumerprotectionbc.ca/wordpress/wp-content/uploads/2018/06/Annual-Report-2017.pdf) | 1 | 24 |
| Consumer Protection BC – reversed corporate logo | [Undated rack card; official URL path includes /2017/06/](https://www.consumerprotectionbc.ca/wordpress/wp-content/uploads/2017/06/Funeral-services-rack-card.pdf) | 1 | 24 |
| Island Coastal Economic Trust – four-line wordmark, 2023–24 report | [2023–24 impact report; official URL path includes /2026/08/](https://islandcoastaltrust.ca/wp-content/uploads/2026/08/Island-Coastal-Economic-Trust-2023-24-Impact-Report-Web.pdf) | 1 | 26 |
| Elections BC – colour logo with Legislature tagline | [2025/26 annual report, dated 21 September 2026](https://elections.bc.ca/docs/rpt/2025-26-ARSP-September-2026.pdf) | 1 | 64 |
| Forest Practices Board – colour horizontal logo | [2022–2023 annual report, official November 2023 URL](https://www.bcfpb.ca/wp-content/uploads/2023/11/FPB-2022-2023-Annual-Report.pdf) | 1 | 25 |
| GameSense – reversed capsule with BCLC endorsement | [GameSense Info Card, official 2025 file](https://www.bclcretailerhub.com/content/dam/retailerhub/training/resources/GameSense_Info_Card-2025.pdf) | 1 | 18 |

## Extraction and fidelity

The artwork was isolated from native PDF drawing content. Where a source used embedded font glyphs,
those original glyphs were converted to outlines. Existing page transforms, shapes and colour treatments
were preserved while unrelated page content and backgrounds were removed. No bitmap tracing,
replacement fonts, redrawing or manual recolouring was used.

MuPDF was used for most path exports. Northern Development required Poppler's SVG export because
MuPDF rasterised its PDF gradient shadings. The four Northern Development exports retain two
linearGradient elements each. PDF counterparts were exported from the clean SVGs using PyMuPDF
or Inkscape and inspected for raster images and residual fonts.

These are specimens recovered from official documents, not supplied standalone brand masters.
PDF-to-RGB conversion can affect displayed colours; no colour value here is asserted to be an official
brand specification. The vector geometry remains scalable. The white/reversed assets need a contrasting
background to be visible. Dark backgrounds in the previews are presentation aids and are not part of
the transparent vector files.

## Source comparison checks

Every selected logo was compared visually with its source crop. The comparison PNGs show original
source crops and independent SVG renders, with foreground overlays where applicable. No clipped
letters, missing symbols or altered arrangement were found.

Measured foreground overlap was 99.95–100% for the LDB/Wholesale group, 98.87–99.88% for the regional
group, 98.59% for Elections BC, 99.32% for Forest Practices Board, and 99.89% for GameSense's white
foreground. These are rasterisation comparisons rather than promises of identical pixels. Sampling
resolution and masks differ across groups. Regional reversed specimens compare white lettering only,
because a single threshold does not reliably isolate a gradient symbol from the source background.
Antialiasing and PDF colour handling explain small raster differences; the original vector paths were
retained. Per-specimen metrics and qualifications are recorded in source-register.json.

## Gallery coverage

The audit used repository main at 118aa1c25c9a924ea9d6a0fa25d712dbb2fc0d73.

| Coverage state | Before | After |
| --- | ---: | ---: |
| Subjects with an accepted native vector | 165 | 172 |
| Subjects with only raster artwork | 164 | 157 |
| Reconstruction only | 14 | 14 |
| Other accepted artwork | 6 | 6 |
| Artwork missing | 100 | 100 |
| Source located, no accepted artwork | 2 | 2 |
| Distinct identity unconfirmed | 4 | 4 |
| Shared identity | 1 | 1 |
| Total subjects | 456 | 456 |

Seven subjects gain their first source vector. The LDB addition is a variation and does not increase
subject coverage. Coverage is measured per subject, so the ICET earlier wordmark qualifies that subject
while its current paddle design remains a separate gap.

All previously accepted asset IDs remain present. Existing source PNGs and distinct artwork variants
are retained. New vectors have source links, evidence notes, output checksums and vector PDF downloads.

## Remaining work and rejected leads

This is a verified recovery batch, not an exhaustive resolution of all 157 remaining raster-only subjects.
The remaining-subject CSV provides the exact queue.

- **BC Cannabis Stores:** the checked official image guide, holiday-hours PDF and selected local-government
  documents held raster logos or scanned pages. No native Stores vector was accepted. A Commons SVG
  derived from a PNG was excluded from this original-vector batch.
- **Island Coastal Economic Trust:** the recovered specimen is the earlier four-line wordmark. The
  current paddle-symbol design remains unresolved.
- **Nechako–Kitamaat Development Fund:** no new native vector was recovered. The earlier project search
  had already checked annual reports and business plans; that work was not repeated or reclassified.
- **BC Ambulance Service:** a cardiac report contained the separate BCEHS identity, while a selected
  BCAS badge in an RDOS agenda was raster. Neither supplies the missing native BCAS badge.
- **Forest Practices Board:** the 2024–25 report cover logo was raster; the accepted ordinary colour
  specimen comes from the 2022–23 report.

Other leads were checked selectively. A failed download or a raster logo in one report is not proof
that no native source exists elsewhere.


## Repository records and verification

- proposed-assets.json is the builder input. Public SVG/PDF paths and grouping rules are recorded there.
- source-register.json uses repository-root-relative artwork and comparison paths.
- coverage-before.json and coverage-after.json preserve the coverage audit.
- raster-only-before.csv and raster-only-remaining.csv record the subject queue.
- validation.json records the SVG/PDF content checks and gallery verification totals.
- REVIEW.md records the independent catalogue and visual review.
- review/ contains source comparisons and the contact sheet.
- SOURCE-CHECKS.md records limitations and rejected source leads.

The original full source PDFs are linked with SHA-256 identifiers in the register. The local sourceFile
names are provenance labels, not paths to committed copies of the complete documents.

Verification performed:

~~~sh
node scripts/build-current-extras.mjs
node scripts/build-identity-expansion.mjs
node --test scripts/identity-expansion.test.mjs src/gallery/collectedCollections.test.js src/gallery/identityCoverage.test.js src/gallery/collectedDisplay.test.js
git diff --check
~~~

The four targeted suites passed 25 tests with zero failures. The identity builder verified 379 referenced
files for 240 identity bodies and 299 source-linked artworks. The default optional current-extras module
was generated locally using the project's existing script; it is ignored and not part of this change.
The independent reviewer additionally checked asset-ID retention, all variant groups and source comparison
boards. A full production build and browser smoke test were not run for this asset-and-catalogue batch.

The implementation changes the builder's search list and regenerated data only; gallery component
behaviour is unchanged.
