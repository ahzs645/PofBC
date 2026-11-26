> Research snapshot. Acquisition totals and unresolved statuses in this working note may precede final integration. The final audit README, report.json and acquisitions.json take precedence. `unbundled/` names identify receipt files omitted from this repository report.

# Additional six regional-district vector checks

November 26, 2026. Twelve official PDF/Illustrator documents downloaded and inspected, plus public website/media metadata checks. The root's prior homepage SVG sweep was consulted to avoid reclassifying arrows and social icons as district artwork.

## Recovered

`findings.json` contains two genuine native SVGs for **Squamish-Lillooet Regional District**, each with 42 original visible paths:

- `slrd-2016-horizontal-colour.svg`: official Kitchen Catcher label PDF whose title/filename and creation metadata identify 2016. Blue/gold horizontal mountains signature.
- `slrd-2018-horizontal-black.svg`: official editable Illustrator file, creation metadata 2016 and modification metadata January 17, 2018. Black horizontal mountains signature.

Both were directly linked from the official [Recycling Signage & Colour Scheme page](https://www.slrd.bc.ca/services/recycling-composting-waste-landfill/recycling/recycling-signage-colour-scheme). The PDF-compatible AI source remains local. Each SVG was rendered with Inkscape and compared with its exact source crop. No embedded images, live text or tracing remain. Source geometry, clipping and outlined lettering are preserved.

**Do not automatically replace the existing website default.** The horizontal layout matches the website specimen, but the website PNG's major RGB fills are `#004085` / `#FFC62B` while the 2016 PDF conversion renders `#005F9E` / `#FFD15E`. Keep the dated source colourways separate; do not recolour them to manufacture a match. The black source is another documented colourway. The separate stacked and older script designs remain separate.

## Checked but still unresolved

| Regional district | Actual sources inspected | Result |
|---|---|---|
| Bulkley-Nechako | [2021 profile](https://opportunities.rdbn.bc.ca/application/files/5916/2387/5793/RDBN_only.pdf); [2025 public hearing package](https://www.rdbn.bc.ca/application/files/8717/5158/2142/RZ_F-02-25_BL2077_Public_Information_Package_2.pdf) | Cover seals are original embedded raster images, 378x378 and 460x460. No native seal recovered. The [June 16, 2022 committee agenda](https://www.rdbn.bc.ca/application/files/1516/5488/2862/COW_Agenda_June_16_2022SOnilPww.pdf) explicitly describes AI masters in the district's internal Communications folder. That is an original-file lead, not an acquired public vector. |
| Central Kootenay | [2024–2026 strategic plan](https://rdck.ca/wp-content/uploads/2024/11/2024-RDCK-Strategic_Plan-Final.pdf); public WordPress media query for “logo” | Seal is a 300x217 embedded bitmap. Media search exposed raster district artwork and unrelated partner logos; no source vector. Existing homepage inline SVGs are controls/icons. |
| North Okanagan | [2024 Fire Services Strategic Plan](https://www.rdno.ca/sites/default/files/2024-10/2024%20RDNO%20Fire%20Services%20Strategic%20Plan%20Report_0.pdf) | Cover logo/header is a 576x96 embedded raster, zero native cover paths. Later document vector charts/maps do not make the header a vector. |
| Strathcona | [2020 overview, official response package](https://docs.openinfo.gov.bc.ca/Response_Package_CTZ-2020-06016.pdf); [2023 financial statements](https://agenda.strathconard.ca/SRDAttachments/SRDBoard/Open/BRD/22-May-24/20240514-2023-Financial-Statements-and-Audit-Findings-Report.pdf) | Overview: all 94 pages have zero native drawings. Financial-report supplementary cover, PDF page 47: logo is a 267x141 image. No native logo recovered. |
| Thompson-Nicola | [May 2025 OCP exhibition posters](https://wpcdn.tnrd.ca/wp-content/uploads/2025/05/02121436/TNRD-Poster-Boards_May2025_MN_Final.pdf); public WordPress media request | Full horizontal logo on first poster is a 400x85 image. Media endpoint returned403. No native logo recovered. Existing 2018/2020 visual-strategy raster sources were not needlessly redownloaded. |
| Squamish-Lillooet | [2022–2026 financial-plan cover](https://www.slrd.bc.ca/sites/default/files/pdfs/finance/Financial_Plans_Statements/Draft%202022-2026%20Financial%20Plan%20Website.pdf); recycling-signage PDFs and AI files | Financial-plan stacked logo is raster. Kitchen Catcher sources yielded the two verified vectors above. No Thank You Bin Sign contains the separate campaign mark only and was not treated as district identity. |

`source-checks.json` records downloads and failures; `status.json` records all six subjects. `initial-inspection.json`, `page-drawing-counts.json` and `rdck-inspection.json` hold supporting checks. `extract_slrd.py` and per-asset receipts make the two vector extractions reproducible. Findings are a targeted pass, not proof that other public originals do not exist.
