# British Columbia school district historical evidence

Research date: 22 November 2026.

## Curated outputs

This document preserves the consolidated historical research findings. Current artwork counts, brand-event coverage, and build instructions are maintained in the [collection guide](README.md); the [illustrated catalogue](CATALOGUE.md) provides a readable current-district and merger index.

[`history.json`](history.json) is the final integration manifest. It contains all 60 current districts from the provincial directory, 123 current-district timeline events, and 31 immediate historical predecessors explicitly abolished in the 1996 amalgamations. The historical predecessor records include sourced abolition dates and, for 18 exact name-and-number matches, a separate earlier 1946 boundary notice. The manifest is marked `source-reviewed`.

[`gazette-1946-district-index.json`](gazette-1946-district-index.json) independently indexes all 74 numbered districts in the original 18 April 1946 Gazette. It preserves their original names, departmental notice date, publication date, and printed/PDF page locators. This is an archival roster, not a mapping by number to the current districts.

The southern 20-district research contribution is merged into the reviewed history input. Downloaded PDFs, HTML, OCR images, and extracted text were inspected as working evidence; source URLs and precise locators are retained in the manifest. The repository build reads the curated inputs. Intermediate extraction scripts are not authoritative replacements for those records.

## Coverage and date semantics

| Measure | Count |
| --- | ---: |
| Current districts | 60 |
| Dated establishment or institutional-origin claims | 52 |
| Day precision claims | 46 |
| Year precision claims | 6 |
| Unresolved establishment dates | 8 |
| Legally effective 1996 creations supported by original OICs | 15 |
| Other reported establishment dates | 34 |
| Institutional-origin dates | 3 |
| Current timeline events | 123 |
| Immediate 1996 predecessor entities | 31 |
| Earlier boundary-notice events attached to historical predecessors | 18 |

A dated claim is not automatically a verified legal commencement date. `established.kind` distinguishes `legal-creation`, `reported-establishment`, `institutional-origin`, and `unresolved`. `established.disputed` identifies unresolved source differences. `meaning`, `evidenceType`, `notes`, and `locator` should remain visible or readily accessible in the product.

The eight unresolved current establishment dates are **SD28 Quesnel, SD41 Burnaby, SD45 West Vancouver, SD46 Sunshine Coast, SD47 qathet, SD54 Bulkley Valley, SD61 Greater Victoria, and SD63 Saanich**. Every one has an original 1946 numbered-district boundary notice in its timeline. The inspected financial statements omit a formation date. A null establishment field therefore represents a specific evidence gap, alongside concrete historical evidence.

The year-only selected claims are SD36 Surrey (1946), SD69 Qualicum (1946), SD70 Pacific Rim (1887 institutional origin), SD71 Comox Valley (1946), SD81 Fort Nelson (1955 institutional origin, disputed), and SD93 CSF (1995 original authority, disputed).

## Original 1946 notices

Primary source: [The British Columbia Gazette, 18 April 1946, volume 86, no. 16](https://archive.org/details/governmentgazett86nogove_m4u8), created by the Government of British Columbia and digitized by University of Victoria Libraries. The source record provides the original PDF and searchable OCR; the index retains printed and PDF page locators.

The education notices for SD1–74 are dated **12 April 1946** and published **18 April 1946**. Their operative wording defines district boundaries; it does not separately state a legal commencement date. These are `boundary-notice` events. They have not been used to populate unresolved establishment fields or replace dates explicitly reported by the districts.

The enabling [Public Schools Act Amendment Act 1946, chapter 64](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/723856512), section 8, re-enacted the relevant power to create districts and define boundaries. Section 121 provides for commencement by proclamation. Retrieving the original creation orders and relevant proclamation remains the appropriate next research step for the eight unresolved dates.

There are genuine date distinctions in the retained primary material:

| District | Audited establishment claim | Original boundary notice |
| --- | --- | --- |
| SD10 Arrow Lakes | 10 April 1946 | 12 April 1946 |
| SD22 Vernon | 1 April 1946 | 12 April 1946 |
| SD43 Coquitlam | 1 July 1946 | 12 April 1946 |
| SD50 Haida Gwaii | 1 April 1946 | 12 April 1946 |
| SD52 Prince Rupert | 1 April 1946 | 12 April 1946 |
| SD57 Prince George | 15 April 1946 | 12 April 1946 |

These are different source statements and potentially different milestones. No blanket 12 April date was assigned across districts.

## The 1996 amalgamations

All 15 current amalgamated districts in this set were legally created **2 December 1996**. The original OICs explicitly abolish the predecessor districts on the same effective date and transfer their assets and liabilities. Order approval dates are separate events. The July and August approval events contain no predecessor links, so they do not generate duplicate lineage.

| Current district | Original OIC | Immediate predecessors |
| --- | --- | --- |
| 5 Southeast Kootenay | 861/1996 | 1 Fernie; 2 Cranbrook |
| 6 Rocky Mountain | 862/1996 | 3 Kimberley; 4 Windermere; 18 Golden |
| 8 Kootenay Lake | 970/1996 | 7 Nelson; 86 Creston-Kaslo |
| 20 Kootenay Columbia | 971/1996 | 9 Castlegar; 11 Trail |
| 51 Boundary | 867/1996 | 12 Grand Forks; 13 Kettle Valley |
| 53 Okanagan Similkameen | 868/1996 | 14 Southern Okanagan; 16 Keremeos |
| 58 Nicola-Similkameen | 869/1996 | 17 Princeton; 31 Merritt |
| 67 Okanagan Skaha | 870/1996 | 15 Penticton; 77 Summerland |
| 73 Kamloops/Thompson | 871/1996 | 24 Kamloops; 26 North Thompson |
| 74 Gold Trail | 872/1996 | 29 Lillooet; 30 South Cariboo |
| 78 Fraser-Cascade | 873/1996 | 32 Hope; 76 Agassiz-Harrison |
| 79 Cowichan Valley | 874/1996 | 65 Cowichan; 66 Lake Cowichan |
| 82 Coast Mountains | 875/1996 | 80 Kitimat; 88 Terrace |
| 83 K̓wsaltktnéws ne Secwepemcúl’ecw | 876/1996 | 21 Armstrong-Spallumcheen; 89 Shuswap |
| 91 Nechako Lakes | 877/1996 | 55 Burns Lake; 56 Nechako |

Primary OIC URLs follow the exact source links in each record, for example [OIC 870/1996](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0870_1996). The cited BC Laws URLs provide the original scans inspected during this research.

The contemporary [April 1996 government announcement](https://archive.news.gov.bc.ca/releases/archive/pre2001/1996/nr13-96.asp) described a proposal to reduce the number of districts to 57 and referred to a December 1 target. It is not evidence of the final enacted roster or effective creation date. The final orders govern these records.

## Source differences requiring visible qualifications

### SD70 Pacific Rim: earlier institutional origin

The district's [2024 audited accounts](https://media.sd70.bc.ca/media/Default/medialib/sd70-final-signed-fs-6-30-2024-package_revised.d3e1699110.pdf), PDF page 11, Note 1, report establishment in **1887**. This predates the modern numbered system. The selected field is explicitly `institutional-origin`; it is not labelled legal creation of the current numbered district.

The original 1946 SD70 Alberni boundary notice is separately retained. [OIC 528/2020](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0528_2020) changed the name to Pacific Rim on **20 September 2020**.

### SD75 Mission: 1946 financial claim versus later separation

The [2021–2022 SOFI](https://www.mpsd.ca/Board/Reports/Budgets/Financial%20info/2021%202022/2021-22%20SOFI_for%20website.pdf), Note 1, reports **12 April 1946**. However, the original 1946 Gazette names **SD34 Abbotsford-Mission** and its numbered list ends at SD74. A historical study reports Mission's separation on **30 June 1947**, but that original legal notice has not been retrieved. The selected financial claim is marked `disputed: true` and must not be presented as a resolved creation date for an independent SD75.

Research lead for the 1947 notice: [School Sports & Mission Teenagers in the 1950s](https://roncoreau74.opened.ca/physical-education-and-sport-in-british-columbia%EF%BF%BC/). This lead is not used as primary legal evidence.

### SD81 Fort Nelson: 1955 versus 1959

The [2025 SOFI](https://www2.gov.bc.ca/assets/gov/education/administration/resource-management/school-district-financial-reporting/financial-information/sd81-sofi-2025.pdf), PDF page 13, Note 1, reports **1955**. The district-hosted [2024–2025 financial report](https://sd81.bc.ca/wp-content/uploads/2024-25-Financial-Statements-and-Financial-Discussion-Analysis.pdf) corroborates that claim.

[OIC 3065/1962](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/3065_1962), first page, describes an establishment order dated **20 April 1959**, published at page 1497 of the 1959 Gazette. The latter might represent a later constitution, but the original 1959 notice is needed to establish that. The dataset selects the district-reported institutional origin of 1955, marks it disputed, and records the 1959 legal cross-reference separately.

### SD92 Nisga’a: 1975 supported, other publications inconsistent

The [2025 SOFI](https://www2.gov.bc.ca/assets/gov/education/administration/resource-management/school-district-financial-reporting/financial-information/sd92-sofi-2025.pdf), PDF page 14, Note 1, and the district's [Long Range Facilities Plan](https://www.nisgaa.bc.ca/links/SD92%20Final%20LRFP.pdf), printed page 6, both state **1 January 1975**. This is the selected establishment claim.

The district's 2023 student-learning report instead says 1 January 1976, and its 2024 report says 1974. Nisga’a Lisims Government also reported a 50th-anniversary celebration in November 2024. An order made in 1974 and effective in 1975 could explain part of this, but that is a hypothesis, not a verified conclusion. The original creation instrument remains outstanding, so the claim retains `disputed: true` and source-difference notes.

### SD93 Conseil scolaire francophone: authority creation and subsequent milestones

A [contemporaneous 1997 provincial announcement](https://archive.news.gov.bc.ca/releases/archive/pre2001/1997/0607.asp) describes creation of the original francophone authority by regulation in **1995**. The [School Amendment Act 1997](https://free.bcpublications.ca/civix/document/id/hstats/hstats/1429105205), section 26, retrospectively validates the original regulation effective **2 November 1995**; section 21 continues the authority under the CSF name.

The CSF's [2024–2025 SOFI](https://www.csf.bc.ca/wp-content/uploads/2025/12/SOFI-2024-2025-Rapport.pdf), PDF page 36, Note 1, separately states establishment on **3 January 1996**. The dataset preserves the 1995 original-authority year and the 1996 financial claim, and marks unresolved source differences.

[OIC 341/1998](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0341_1998) directly verifies two subsequent jurisdiction milestones: eight additional district areas on **1 July 1998**, and the whole province on **1 July 1999**. Neither is substituted for original formation. The 2012 and 2022 visual-identity announcements are separate branding events.

## Names, numbers, and identity

District numbers are reused. Examples from the original 1946 roster include SD5 Creston, SD6 Kootenay Lake, SD8 Slocan, SD20 Salmon Arm, SD51 Portland Canal, SD53 Terrace, SD58 McBride, SD67 Ladysmith, SD73 Alert Bay, and SD74 Quatsino. These are not interchangeable with the current entities that use those numbers.

The predecessor links in the manifest preserve both number and name and use the actual effective amalgamation date. Parent integration should assign stable entity IDs using the historical identity, not the number alone.

Verified current-name milestones include:

- SD48 Howe Sound → Sea to Sky, effective **1 January 2009**, OIC 687/2008 as printed in the 9 October 2008 Gazette.
- SD70 Alberni → Pacific Rim, **20 September 2020**, OIC 528/2020.
- SD47 public adoption of qathet, **25 September 2023**. The district's later letter requesting provincial legal amendment is separately cited; public use and legal order are not assumed to be the same date.
- SD83 board adoption of its gifted Secwépemctsín name, **24 September 2024**, per the district's 16 October 2024 release. This is distinguished from the later ceremony and provincial legal confirmation.

Earlier district names in 1946 are retained as aliases where the continuity is supported. Predecessor incarnations created through mergers remain separate entities.

## Historical coverage still to expand

The 31 historical records cover the immediate predecessors of the 15 final 1996 amalgamations. They do not constitute an exhaustive history of all 19th- and 20th-century rural, municipal, and numbered districts. Further work should verify original creation and reconstitution instruments for those predecessors, pre-1996 amalgamations and partial transfers, and associated name changes.

Two leads specifically remain outside the curated lineage: the SD58 McBride absorption into Prince George, for which accessible retrospective sources disagree between 1968 and 1970; and earlier splits or transfers involving SD67 Ladysmith and SD8 Slocan. The source-review pass did not promote these unresolved leads into definitive graph edges.

## Validation performed

The final manifest has exactly 60 unique current district numbers matching the provincial roster and exactly 31 immediate historical predecessor records. All 15 amalgamations use 2 December 1996; every historical abolition date is a structured, sourced date object. Approval events have empty predecessor arrays. All timeline events contain a source URL, source title, and locator. Null establishment dates use `precision: unknown`. Source-provided precision is preserved, with no fabricated January 1 dates for year-only evidence.

Scanned 2025 financial notes for SD49, SD60, SD69, SD81, SD84, and SD92 were OCR-extracted locally; the retained PDF page locators identify the original evidence. Primary notices and OIC text were inspected directly. Quesnel and Burnaby's original Gazette pages were also visually checked by the southern researcher.
