# Logo gallery vector review, 27 November 2026

The gallery holds **1,228 designs in 614 collections**. Each row in the inventory links to one design, identifies its collection and representative status, and records the artwork the gallery opens in each theme. It includes historical designs, supplied files, reconstructions and designs drawn by the gallery. [Design-by-design inventory](inventory.csv)

| What appears in the gallery | All-vector preview | Raster image | SVG with bitmap content | Total |
| --- | ---: | ---: | ---: | ---: |
| Designs on light pages | 808 | 411 | 9 | 1,228 |
| Designs on dark pages | 812 | 408 | 8 | 1,228 |
| Collection representatives on light pages | 427 | 183 | 4 | 614 |
| Collection representatives on dark pages | 430 | 181 | 3 | 614 |

**430 collections show vector artwork in at least one theme.** The other 184 have raster or mixed-media previews throughout. The preview counts describe how the artwork renders. The inventory’s provenance column separately identifies original supplied, publisher-sourced, reconstructed and other artwork. In particular, an SVG can contain the publisher’s raster photograph, and an entirely vector drawing can be a documented reconstruction.

## The two school districts

- **Nanaimo Ladysmith (SD68).** The collection previously opened the website PNG. Its August 2026 accessibility plan supplies the same salmon and title-case lettering as 50 original vector paths. The current design now opens and downloads as SVG. The uppercase 2023 arrangement and both original website PNGs remain available. [Accessibility plan, cover](https://www.sd68.bc.ca/wp-content/uploads/2026-nlps-accessibility-plan-1.pdf#page=1) · [2023 learning report, cover](https://www.sd68.bc.ca/wp-content/uploads/SD-68-FINAL-ESL-2023.pdf#page=1)
- **Gold Trail (SD74).** The gallery features the **2021 strategic-plan badge** and labels its sighting. It has bold “GOLD TRAIL” above mixed-case “School District 74”. The current badge has thin capitals around the full rim. The district’s 2026 climate report embeds the current badge as a 388 × 388 image. Its current-design page retains the published image. [Strategic plan, p. 3](https://22.files.edl.io/2e4e/04/03/25/155406-7bc6389e-28ec-4b66-899d-2ea68bd4a125.pdf#page=3) · [Climate report, cover](https://22.files.edl.io/3c2b/08/31/26/163619-ae850870-2629-407f-9b57-7ca5cc351bd6.pdf#page=1)

The school review documents all 60 districts. It identifies matching native artwork for 31 current district designs and names the publications checked for the remaining 29. [District-by-district evidence](../../education/school-districts/VECTOR-REVIEW.md)

## Other changes

- Nanaimo and Prince George airports now open with the full-colour signatures in their annual reports. The Prince George globe retains 20 radial gradients. Northwest Regional Airport Terrace–Kitimat features the positive print signature from its advertising rate card, which also supplies the reverse. The official website signature with a white keyline has its own entry. [Nanaimo annual report](https://ycd.ca/wp-content/uploads/2026/06/2025-YCD-Annual-Report-Final.pdf) · [Prince George annual report](https://www.pgairport.ca/wp-content/uploads/2024/07/PGAA_2023_Annual_Report.pdf#page=1) · [Terrace–Kitimat rate card, p. 2](https://yxt.ca/wp-content/uploads/2024/10/NWRA-AD-PRICING-.pdf#page=2)
- The gallery uses the existing verified vectors for Sechelt’s teal signature and the Squamish-Lillooet Regional District’s blue-and-gold signature. Kelowna’s 2024 draft Urban Forest Strategy supplied 73 native paths. Its original print inks and a version using the documented website colours are selectable. West Coast Express, the City of Prince Rupert’s standalone wordmark, White Rock and Pacific Heliport Services now use source paths in their documented positive inks. Each version records its geometry and colour sources. [Kelowna strategy](https://hdp-ca-prod-app-kelowna-involved-files.s3.ca-central-1.amazonaws.com/6417/1562/8132/Kelowna_SUFS_May_2024_for_Engagement.pdf) · [Colour evidence and sources](../../../src/gallery/verifiedSourceColours.js)
- The uploaded publications supplied the black Land and Water British Columbia signature and three separate historical postsecondary designs. They are the UCFV initials, the UFV wave-and-leaf wordmark, and UFV’s 40th-anniversary emblem. The Fraser Valley College shield was already held. The former BC Human Rights Commission’s report prints its letters as vectors but embeds pixels in its emblem. [Artwork records and archive sources](../../../src/gallery/archivalReportArtwork.js)
- Gardens BC’s monochrome website signature now has its own gallery entry and represents the collection. The orange signature on a textured dark field remains a separate design with its published raster specimens. [Gardens BC media page](https://gardensbc.com/about/media/)

## Why some designs still use pixels

| Design | Artwork used and outstanding source |
| --- | --- |
| Innovate BC | The positive uses the service-plan cover’s star-trail photograph inside a native circle and native lettering. Dark pages use the white logo-kit EPS. |
| Coast Mountain Bus Company | The colour route-map specimen is an embedded image. Dark pages use the 2022 presentation’s published white-lettered vector signature. |
| SD84 Vancouver Island West | The website’s black-lettered crest remains raster. Dark pages show the light-lettered native crest from the 2025–2030 strategic plan. |
| Historical SD93 Conseil scolaire francophone | The positive illustrated-book logo has an oval and a blue background. Dark pages show the annual report’s white-lettered reverse. |
| BC Geological Survey, 1995 centennial | The title-page scan uses a solid black “100” and heavy lettering. The selectable map version uses a hatched “100” and different lettering drawn with 544 paths. |
| BC Geological Survey, hammer seal | The 2017 specimen has a shaded field. The selectable 1999 vector has flat inks and a different treatment of the hammers and lettering. |

The two Geological Survey designs are the only rows in which both previews contain pixels and the *same design page* offers an additional verified native vector. Its controls identify the precise source for each treatment. Other open cases include Prince Rupert Airport’s published materials, Atlin’s web signature and Vanderhoof’s complete municipal wordmark. Prince Rupert Airport is distinct from the City of Prince Rupert. [Geological Survey comparisons](../bc-geological-survey/README.md) · [Earlier source leads](../vector-recovery-2026-11-26/remaining-gaps.json)

## Reproducing the inventory

Run these commands from the repository root.

```sh
npm run build:cleanbc-artwork --silent
node research/identity/gallery-vector-review-2026-11-27/inventory.mjs
```

The script enumerates the gallery’s collection and design registry, resolves each themed tile through the renderer, checks registered downloads exist locally, and inspects displayed SVGs for image content. The broader source search checked 962 local SVGs under the identity artwork directories and screened 150 previously cited publisher pages for unresolved sources. External-source findings are limited to the files and pages successfully examined. The CSV gives existing publisher evidence and outstanding source leads per design. [Inventory script](inventory.mjs)
