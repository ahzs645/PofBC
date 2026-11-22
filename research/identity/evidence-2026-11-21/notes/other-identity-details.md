# PofBC: research on the seven remaining non-municipal, non-health identities

Research pass: 21 November 2026. Repository baseline: `cbaf4ebe1361f79ac65eb7f24a61529300c89006`, with 108 subjects lacking accepted artwork. This report covers seven of them. No repository changes or external messages were made.

## Findings at a glance

| Subject | New evidence in this pass | Appropriate classification | Closes an independent-logo gap? |
|---|---|---|---|
| BC Archives | Original bitmap from its historical official website; a 1998 homepage explicitly references the asset, and the recovered image has a 10 June 2000 capture | Authentic historical website masthead, with separate dates for the HTML and image | Candidate if website wordmarks qualify; not proof of a general corporate logo |
| BC Harbours Board | Complete 1977 railway timetable scan and a 1980 letter signed by its chair | Shared provincial coat of arms and provincial/ministry letterhead, positively documented | No distinct Board symbol established |
| Metro Transit Operating Company | Museum of Vancouver's Spring 1983 *Transit Exchange* cover | Publication masthead and an exact archival lead | No |
| Crown-era BC Electric | Museum objects and catalogue text documenting BC Electric-branded tokens continuing under BC Hydro | Continued use of inherited branding on transit tokens | Not a newly demonstrated Crown-era corporate logo |
| Pacific Vehicle Testing Technologies | Official TransLink reports confirm PVTT/AirCare relationship; manual reproduction explains ownership of AirCare mark | Program branding, not independently attributable corporate artwork | No |
| Provincial Rental Housing Corporation | Official administrative and financial-report context | Still unresolved; BC Housing branding should not be relabelled PRHC | No |
| W.L.C. Developments | Official corporate-history sources and more precise search boundaries | Still unresolved; successor and Whistler resort identities are not interchangeable | No |

“No” means the inspected material does not establish a distinct mark. It does not mean the subject never used one.

## 1. BC Archives: original historical website artwork recovered

### The useful discovery

The archived official homepage captured on **23 January 1998 at 16:07:26 UTC** contains an image reference to `/general/icons/archives2.gif`, explicitly labelled “British Columbia Archives,” with dimensions 543 × 67 pixels:

- [1998 official homepage capture](https://web.archive.org/web/19980123160726/http://www.bcarchives.gov.bc.ca/index.htm)
- Original image location: `http://www.bcarchives.gov.bc.ca/general/icons/archives2.gif`
- [Actual recovered image capture, 10 June 2000 at 10:58:38 UTC](https://web.archive.org/web/20000610105838im_/http://www.bcarchives.gov.bc.ca/general/icons/archives2.gif)

The actual bitmap was downloaded and visually inspected. It is the full name **British Columbia Archives** rendered in shaded brown/rust/red lettering on a light grey background. It is an original raster graphic, not a reconstruction. There is no separate pictorial emblem in this asset.

**Recommended record description:** “British Columbia Archives historical website masthead. Original official-site GIF; image preserved in a 10 June 2000 capture. The same asset path appears on the 23 January 1998 homepage.”

That wording matters. The archived HTML proves the asset path was in use in 1998, but the recovered image's pixels are from the 2000 capture. This pass does not prove the image contents were identical in 1998. Nor does a website masthead alone establish that the treatment appeared on stationery or represented a formal corporate identity.

Local source files:

- `bcarchives-home-1998.html`: archived HTML inspected for the actual image reference.
- **`bcarchives-web-masthead-capture-20000610.gif`**: correctly dated copy of the recovered 18,341-byte, 543 × 67-pixel image.
- Earlier intermediate filename `bcarchives-archives2-1998.gif` contains the same bitmap; do not use that filename as evidence of its capture date.

SHA-256 of the GIF: `fb0f18b5a7bd104ac07ef724424803b418d7e032d1f63e01125c2c61e7f179d1`.

### Checks that constrain the conclusion

The [current official site](https://bcarchives.ca/) has a text “BC Archives” header and a separate Royal BC Museum link/mark. Its HTML styles the name as `archives-logo`, but that CSS class is not independent proof of a pictorial or historical logo.

Both pages of the official [June 2025 BC Archives brochure](https://bcarchives.ca/wp-content/uploads/sites/2/2025/07/BC-Archives-Brochure-June-2025.pdf) were rendered and inspected. The cover uses the heading “Welcome to the BC Archives” and the Royal BC Museum mark. It did not supply a separate Archives pictorial mark. Local files: `bcarchives-2025-brochure.pdf`, `bcarchives-brochure-1.png`, `bcarchives-brochure-2.png`.

A further Wayback check exposed an important attribution hazard. Homepages around 2000–2001 reference `images/bmain_02.jpg`, but requests for that image resolved to a **25 September 2003** capture containing a Royal BC Museum mark. It must not be labelled a 2000 or 2001 specimen merely because the enclosing homepage has an earlier timestamp. The requested 2000 homepage resolved to **17 June 2000, 06:23:10 UTC**, and uses a newer design; it does not independently demonstrate the old masthead's continued prominence in June 2000.

**Confidence:** High that the GIF is an authentic graphic from the historical official Archives website. Moderate that it should meet the project's artwork threshold, because acceptance depends on whether entity-specific website mastheads qualify. No claim of formal all-purpose identity adoption is made.

## 2. BC Harbours Board: inspectable shared identity, with original documents

### A complete 1977 timetable

The earlier audit had catalogue leads for timetables but no verified visual specimen. This pass recovered a complete eight-page scan of **British Columbia Harbours Board Railway, Time Table 5**, effective **0001 Sunday, 24 April 1977**.

- [WX4 timetable source index](https://www.wx4.org/to/foam/maps/and_timetables4.html)
- [Original PDF URL](https://wx4.org/to/foam/maps/1Perry4/1977-04-24BritishColumbiaHarboursBoardRailway5-SheldonPerry.pdf)
- [Complete archived PDF, captured 31 August 2022 at 02:16:33 UTC](https://web.archive.org/web/20220831021633id_/http://wx4.org/to/foam/maps/1Perry4/1977-04-24BritishColumbiaHarboursBoardRailway5-SheldonPerry.pdf)

The original document is a primary historical specimen, even though its digital scan is hosted by a private railway-history collector. The indexed filename credits Sheldon Perry. The document itself supplies the issuer and effective date.

**Visually inspected:** all eight PDF pages. Pages 1, 2 and 8 were inspected individually; pages 3–7 were also inspected as a contact sheet. On PDF page 1, the front cover is on the right half of the spread. It places the full Board Railway name above the **provincial coat of arms**, followed by the timetable title and effective date. It lists J. Davis as chairman and M. C. Norris and J. D. King as members. PDF page 2 states that management is contracted to British Columbia Railway Company.

This establishes use of **shared provincial armorial identity on a Board Railway publication**. It does not establish a distinct BC Harbours Board logo or that the arms were the Board's separate corporate seal. The British Columbia Railway management relationship also should not be used to relabel a BCR logo as Harbours Board artwork.

Local verified files:

- **`harbours-1977-timetable-complete.pdf`**: 3,240,552 bytes, eight pages.
- `harbours-1977-1.png` through `harbours-1977-8.png`.
- `harbours-1977-contact.png`: pages 3–7.
- `harbours-timetable-cdx.json`: archive-capture metadata used to find a complete copy.

SHA-256 of the complete PDF: `a763c56a2c37a8c111d75d50e6fd9224bc8c6cefba15283b70e3a50a13609c29`.

**Access warning specific to this source:** the direct original returned HTTP 403 during downloading. An earlier Wayback capture dated 9 May 2021 was truncated at exactly 1,048,576 bytes; its response explicitly reported a truncation warning and the original crawler length of 3,240,552 bytes. The 2022 capture above is complete and rendered successfully. The local files `harbours-1977-timetable.pdf` and `harbours-1977-timetable-archived.pdf` are failed/truncated intermediates and must not be delivered as source documents.

### A 1980 chairman's letter corroborates shared provincial branding

The BC Ombudsperson's [*The Cuthbert Case*, Special Report No. 3](https://bcombudsperson.ca/wp-content/uploads/2025/08/Special-Report-No-03-The-Cuthbert-Case.pdf), published in 1981, reproduces an **October 6, 1980** letter from Don Phillips. On **PDF pages 47–48, printed pages 43–44**, the first page uses the provincial coat of arms and the letterhead “Province of British Columbia / Office of the Minister / Ministry of Industry and Small Business Development.” The signature page identifies Phillips as “Minister and Chairman, British Columbia Harbours Board.” Both pages were visually inspected.

Local files: `harbours-cuthbert-report.pdf`, `harbours-cuthbert-47.png`, `harbours-cuthbert-48.png`. Other pages were text-searched, but the conclusion here is limited to those two inspected pages.

**Recommended classification:** “Shared provincial identity documented, 1977 railway timetable and 1980 chairman correspondence.” This is a meaningful evidential improvement over “name-only lead.” It is not a reason to claim discovery of an original Board-specific logo.

**Confidence:** High for the visible use and issuer/date; high for the shared provincial-armorial classification.

## 3. Metro Transit Operating Company: precise new archival lead, not a corporate-logo recovery

The Museum of Vancouver holds the **Spring 1983 issue of *Transit Exchange***, described as being for MTOC employees:

- [Museum record](https://openmovportal.ca/argus/final/Portal/Main.aspx?component=AAFG&record=039deb30-dd48-4139-b838-b7387660097b)
- Museum collection number **H2015.37.548**, accession **2015.9.548**.
- [Museum cover image](https://openmovportal.ca/argus/final/ViewImage.aspx?field=DerivedIma&hash=59360fc7c2a63e2c5d9103d9a443b0c9&lang=en-CA&r=-1735779844&template=Image)
- Local inspected image: **`mtoc-transit-exchange-1983.jpg`**.

The green cover has a large white **TRANSIT exchange** publication masthead and an employee-publication subheading identifying Metro Transit Operating Company. Its photograph shows employees holding a large safety shield. The museum describes this as the Metro Transit Traffic Shield awarded to the Port Coquitlam centre for 1982.

The supplied 314 × 400-pixel image was visually inspected twice. The shield is too small to identify an independent corporate device. The masthead is a publication title; calling it the MTOC corporate logo would repeat the attribution problem already identified for *The Buzzer*.

**What to do with it:** add this accession as an exact follow-up lead. The most useful next item is a high-resolution scan of the issue's back cover, masthead/imprint page, and any corporate notice or letterhead reproduced inside. Those pages were not accessible from the single-image record and were not inspected in this pass. No museum contact was sent.

The museum also holds an [MTOC-distributed Sunday & Holiday Pass](https://openmovportal.ca/argus/final/Portal/Main.aspx?component=AAFG&record=54247542-bc82-42ae-99da-06dc02ddccf9), H2015.37.241, dated 1980–1985. That record is a related lead only; its image was not inspected here. Distribution by MTOC does not prove that a regional transit-system mark belongs uniquely to MTOC.

SHA-256 of the inspected cover: `5e1622e79239c7c3fd51710724d2208fd3b01da5722d70292b2d7c06dffe9066`.

**Confidence:** High for publication, employer and issue; low for identifying any corporate symbol on the shield. No independent MTOC logo established.

## 4. Crown-era BC Electric: inherited identity continued on transit tokens

The Museum of Vancouver's token catalogue supplies more specific evidence than an undated collector image or a modern BC Hydro retrospective:

- [A token record](https://openmovportal.ca/argus/final/Portal/Main.aspx?component=AAFG&record=42752437-ccbf-4329-9b85-8f43bfbbd00c): **H2016.18.3**, accession **2016.17.3**, dated 1960–1970.
- [B token record](https://openmovportal.ca/argus/final/Portal/Main.aspx?component=AAFG&record=233138fa-2875-46c8-a9af-9a8ef8b6727f): **H2015.37.13**, accession **2015.9.13**, dated 1960–1970.
- [A token image](https://openmovportal.ca/argus/final/ViewImage.aspx?field=DerivedIma&hash=9bbc6232f9e01c2d07af4b56dbf042e0&lang=en-CA&r=-1735779844&template=Image)
- [B token image](https://openmovportal.ca/argus/final/ViewImage.aspx?field=DerivedIma&hash=40090b1f174be071e21ef4e48703af2d&lang=en-CA&r=-1735779844&template=Image)

Both images were downloaded and visually inspected as `bce-token-A.jpg` and `bce-token-B.jpg`. The A-token photograph clearly shows the large central A and surrounding BC Electric / transit-token lettering. The B-token photograph is smaller and less legible. These are physical transport-token designs; they do not by themselves supply a clean standalone rendition of the familiar circular BCE corporate device.

The museum's explanatory text says A and B tokens retained BC Electric branding after 1962 to avoid wasting previously minted stock, while C tokens used BC Hydro branding. It says tokens were discontinued on April 1, 1970. This is **explicit evidence of inherited BC Electric identity continuing during public operation**, but the dating of these particular objects spans both pre- and post-takeover years.

**Recommended use:** record a carefully qualified continuity note and museum accession. Do not recategorize a pre-takeover symbol as a newly created Crown corporation identity. A contemporary 1961–1962 letterhead, annual report or dated corporate advertisement would remain stronger evidence for the exact BC Electric corporate entry. The previous audit's 2013 BC Hydro retrospective should remain a secondary corroboration, not the primary dating basis.

**Confidence:** High that BC Electric-branded tokens exist; moderate-to-high for the continuation history because it rests on the museum's curatorial account. The photographed token itself is not independently dated to the narrow Crown-company period.

## 5. Pacific Vehicle Testing Technologies: distinguish the company from AirCare

The [TransLink 2014 annual report](https://www.translink.ca/-/media/translink/documents/about-translink/corporate-reports/translink_annual_report/tl_annual_report_2014.pdf) describes PVTT as commonly known as AirCare and states that the program ended on December 31, 2014. The [2010 annual report](https://www.translink.ca/-/media/translink/documents/about-translink/corporate-reports/translink_annual_report/tl_annual_report_2010.pdf) was downloaded and inspected at the most relevant spreads:

- PDF page 8, printed pages 14–15: a governance diagram with an ordinary-text **PVTT (AirCare)** box, not an individual logo.
- PDF page 13, printed pages 24–25: AirCare operational material, with report-wide TransLink branding.

Local files: `pvtt-translink-2010.pdf`, `pvtt-2010-page-8.png`, `pvtt-2010-page-13.png`.

A [2010 *AirCare Certified Emissions Repair Manual* reproduction](https://www.scribd.com/document/74235848/AirCare-Repair-Manual) identifies PVTT as its copyright holder and, in Appendix D, “Permissible use of AirCare mark,” describes AirCare as a registered official mark of the Province of British Columbia, administered through PVTT subject to superintendent consent. This is a useful **text lead**, not a visually verified logo source: the original official PDF and its graphic pages were not recovered. A [RepairNet guide reproduction](https://manualzilla.com/doc/6859685/aircare-repairnet-user-guide-version-5.0) similarly links the program to PVTT but did not resolve the separate-logo question.

**Recommended status:** “AirCare program relationship confirmed; separate PVTT corporate mark unresolved.” An AirCare mark may be appropriate to a program entry, or to a clearly labelled shared/program-branding section; it should not silently stand in for PVTT's separate corporate identity.

## 6. Provincial Rental Housing Corporation: no independently attributable artwork recovered

The [official BC Housing organizational description](https://www.bchousing.org/about/our-organization) explains PRHC's role and its administration through BC Housing. The [2023 PRHC financial statement](https://www.bchousing.org/publications/Provincial-Rental-Housing-Corporation-Financial-Statement-2023.pdf) is a genuine corporation-specific source, but it was already reviewed in the repository's previous pass. This research did not obtain a new distinct graphic from it.

Other sources identified were official group-home operator material linked from [PRHC Group Homes](https://www.bchousing.org/projects-partners/housing-provider-info/prhc-group-homes), the [2013/14 BC Housing annual report](https://www.bcbudget.gov.bc.ca/Annual_Reports/2013_2014/pdf/agency/bch.pdf), and municipal project/affidavit packets naming PRHC. These were search/text leads, not newly visually verified corporate marks. Architect logos and commissioner seals in such packets should not be attributed to the landowner corporation.

**Recommended status:** unchanged unresolved entry, with an explicit shared-administration note. The lack of a separate mark in these sources is not proof that none ever existed.

## 7. W.L.C. Developments: keep legal-entity and successor identities separate

Official corporate-history evidence helps tighten the date range and avoid assigning nearby Whistler brands:

- [Land and Water British Columbia 2003/04 financial statements](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2003-04/sup-e/land-and-water-bc-fs-2003-04.pdf) state that the entity was incorporated on January 5, 1983 as W.L.C. Developments, renamed British Columbia Assets and Land Corporation on June 1, 1998, and renamed Land and Water British Columbia in February 2002.
- A [1998 provincial release](https://archive.news.gov.bc.ca/releases/archive/pre2001/1998/october/nr065.asp) discusses the earlier Whistler land-development role and its expanded mandate. The release's broader origin narrative should not override the legal incorporation date in audited statements.
- [Whistler Museum's discussion of resort identity](https://whistlermuseum.org/tag/whistler-village/page/2/) concerns the Whistler Resort Association's circle-of-Ws treatment. That is not evidence of a W.L.C. Developments mark.

The earlier repository audit had already inspected the [municipal contract packet](https://pub-rmow.escribemeetings.com/filestream.ashx?DocumentId=14101) and found corporate-seal execution areas blank. This pass did not overturn that conclusion. Legal language requiring a seal, or a blank space marked for one, does not recover its artwork.

**Recommended next archival target:** actual W.L.C. Developments correspondence, letterhead, annual accounts or corporate seals from 1983–1998 in Whistler/municipal holdings. The Whistler Village Land Company, Whistler Resort Association, BC Assets and Land Corporation, and Land and Water BC have related histories but cannot supply artwork for the W.L.C. label without dated usage evidence.

**Recommended status:** unresolved; no new independently attributable graphic established.

## Evidence priorities for the project

1. Review the recovered BC Archives bitmap against the gallery's acceptance rule for historical website wordmarks. If accepted, date the exact image capture to 2000 and state that the path was referenced in 1998.
2. Upgrade BC Harbours Board from a name-only lead to **documented shared provincial branding**, with the 1977 timetable and 1980 letter. It should not remain described as wholly uninspected.
3. Add the MTOC Spring 1983 issue accession as a targeted archival task, while retaining unresolved corporate-artwork status.
4. Add the BC Electric token continuation evidence as a scoped historical note, with the caveat that the physical objects' catalogue date range crosses the ownership transition.
5. Keep PVTT, PRHC and W.L.C. unresolved. This pass narrowed attribution and source choices without establishing absence of logos.

## Web-source reference IDs for the coordinating researcher

These IDs are provided for source reopening in the final combined answer; direct URLs above are the durable record.

| Evidence | Web references |
|---|---|
| Harbours timetable original PDF and index | , ,  |
| Harbours Cuthbert report | ,  |
| Current BC Archives site and 2025 brochure | , ,  |
| MTOC Transit Exchange record and image | , ,  |
| BC Electric token B and A records | ,  |
| BC Electric token images | ,  |
| PVTT official TransLink reports | ,  |
| AirCare manual text reproductions | , ,  |
| PRHC official organization / financial statement | ,  |
| WLC official corporate-history sources | ,  |

The Wayback files were retrieved using their public URLs after the web tool could not open them. No fabricated search-reference ID is assigned to those captures. Actual image timestamps, archived HTML references and complete PDF bytes were checked locally.
