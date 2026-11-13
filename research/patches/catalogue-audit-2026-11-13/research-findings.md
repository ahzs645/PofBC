# PofBC patch expansion research — 13 November 2026

Baseline: Patcher `68f145d3f91fd3d915b0810b4faf19dd81b1e7e3`, embedded by PofBC `1fb9e08dbb105bd691bed0790c81365b46ebc4f0`. This review compares the manifest labels, organization roster, variant groups and source metadata. It is not an image-by-image authentication of every physical specimen.

The structured inventory keeps missing designs, collector candidates, held leads and corroborating evidence separate. None of the listed candidates has been added as completed artwork.

## Results

- 44 candidate records: 29 documented-missing; 8 collector-candidate; 2 documented-needs-comparison; 2 documented-needs-image; 1 held-unverified-issue; 1 held-printed-design-only; 1 held-planned-only.
- 11 source-improvement/corroboration records, kept out of the missing-design count.
- A 30-crew research roster from a dated 2020 newsletter; it does not represent 30 verified new patch designs.

## Priority additions

| Candidate | Evidence | Nearest existing ID | Source |
| --- | --- | --- | --- |
| Recreation — brown and white title strip | documented-missing | `S49-O01` | [Pemberton Museum: BCFS Patches, 014.06.11 abcdefghijklmn](https://www.pembertonmuseum.org/objects/bcfs-patches/) |
| Revenue Inspector — navy and white title strip | documented-missing | `S49-O01` | [Pemberton Museum: BCFS Patches, 014.06.11 abcdefghijklmn](https://www.pembertonmuseum.org/objects/bcfs-patches/) |
| Forests and Lands — brown and white title strip | documented-missing | `S49-O01` | [Pemberton Museum: BCFS Patches, 014.06.11 abcdefghijklmn](https://www.pembertonmuseum.org/objects/bcfs-patches/) |
| Forest Service / British Columbia / Aviation | documented-missing | `FO-airtanker` | [Ingenium 2003.0257.001: Forest Service British Columbia Aviation](https://collection.ingenium.ca/en/id/2003.0257.001/) |
| Parattack — winged parachutist | documented-missing | None identified | [Ingenium 2005.0019.001: Parattack fabric badge](https://collection.ingenium.ca/en/id/2005.0019.001/) |
| BC Sheriff Service — service-specific heraldic shoulder flash | documented-missing | `S56-O01`, `S56-O02` | [BCSS shoulder flash 2.jpg](https://commons.wikimedia.org/wiki/File:BCSS_shoulder_flash_2.jpg); [Canadian Heraldic Authority: BC Sheriff Service grant](https://www.gg.ca/en/heraldry/public-register/project/2209) |
| Vancouver Police — city-arms shoulder flash | documented-missing | None identified | [Museum of Vancouver H998.19.4: Vancouver Police shoulder flash](https://openmovportal.ca/argus/final/ViewRecord.aspx?lang=en-CA&record=0c543f81-f00f-4821-b5b7-fbfa5b65e3d1&template=Object) |
| Surrey Police Service — 2021 shoulder flash | documented-missing | None identified | [Surrey Police Service Uniform Revealed](https://www.surreypolice.ca/news-events/news/surrey-police-service-uniform-revealed); [New Crest for Surrey Police Service](https://www.surreypolice.ca/news-events/news/new-crest-surrey-police-service) |
| Saanich Police — 2024 raven crest | documented-missing | None identified | [Saanich Police 2024 Annual Report: New Crest Design](https://saanichpolice.ca/wp-content/uploads/2025/09/2024-Annual-Report-Final-Version.pdf) |
| South Coast BC Transportation Authority Police — shoulder flash | documented-missing | None identified | [Transit Police 2013 Report to the Community](https://transitpolice.ca/wp-content/uploads/2016/04/2013_report_to_the_community.pdf) |
| BC Railway Police — white crescent, red BC and blue lettering | documented-missing | None identified | [International Police Museum: Uniforms collection](https://www.internationalpolicemuseum.org/explore.php?category=Uniforms); [The Railroad Police: Patches A–H](https://www.therailroadpolice.com/page-p) |
| BC Railway Police — dark crescent with BC Rail lettering | documented-missing | None identified | [International Police Museum: Uniforms collection](https://www.internationalpolicemuseum.org/explore.php?category=Uniforms); [The Railroad Police: Patches A–H](https://www.therailroadpolice.com/page-p) |
| BC Railway Police — dark crescent with dogwood disc | documented-missing | None identified | [International Police Museum: Uniforms collection](https://www.internationalpolicemuseum.org/explore.php?category=Uniforms); [The Railroad Police: Patches A–H](https://www.therailroadpolice.com/page-p) |
| BC Railway Police — dark crescent with full railway name | documented-missing | None identified | [International Police Museum: Uniforms collection](https://www.internationalpolicemuseum.org/explore.php?category=Uniforms); [The Railroad Police: Patches A–H](https://www.therailroadpolice.com/page-p) |
| Ambulance / British Columbia — shoulder roundel | documented-missing | None identified | [BCEHS 2023/24 Progress Report](https://www.bcehs.ca/about-site/Documents/bcehs_progress_report_2023-24.pdf); [British Columbia Ambulance Badge.jpg](https://commons.wikimedia.org/wiki/File:British_Columbia_Ambulance_Badge.jpg) |
| Fraser Unit Crew — crew patch | documented-needs-image | None identified | [Coastal Fire Centre Wildfire News, issue 6, 17 July 2020](https://www.thetisislandfire.ca/newsletters/2020-07-17-Issue6-Coastal-Wildfire-News.pdf) |

## Additional museum specimen pass

A bounded search of the [International Police Museum patch inventory](https://www.internationalpolicemuseum.org/explore.php?category=Uniforms&subcategory=Patch) produced 55 relevant accession records. They are stored separately in `museum-specimens-2026-11-13.json`: 23 potential additional design/variant specimens, 19 specimens linked to the candidates above, 7 potential baseline corroborations, 5 items requiring scope decisions, and 1 unresolved rank item. These are specimen records, not additional confirmed design totals.

The strongest further leads are Vancouver Police title and Reserve strips, Victoria title and civic-arms patches, New Westminster crown variants, West Vancouver palettes and shapes, Delta title/crest patches, Matsqui specimens, the older Saanich title, and a Nelson standard patch. Six Port Moody accession records extend the existing research candidate. Abbotsford has a small and a large accessioned specimen; compare scale and construction before declaring two designs.

Two misleading search matches were excluded: a Vancouver-labelled record whose description identifies Queensland Police, Australia, and Victoriaville in Quebec. No suitable Surrey BC, Oak Bay or BC Hydro accession was established in the retrieved excerpts. This is a limitation of the source pass, not proof those patches do not exist. Expo’s generic exposition roundel is a scope lead, distinct from the existing Security and Crime Prevention shields. The Dawson Creek RCMP local crest is also retained for scope review.

## How to use the inventory

Open the JSON for all candidates, source URLs, evidence type, baseline comparison IDs, proposed template family and the next verification step. The proposed family field is a research label: it does not assert identical geometry.

No source images were downloaded into the project, no candidate art was created, and reuse rights have not been cleared. Each source carries an explicit rights-review field. The Ingenium pages show an apparent mismatch between the displayed license label and linked license; resolve that before reuse.

Promote a candidate only after examining the source image and recording the specific evidence. A museum’s dimensions can be approximate storage dimensions; do not use them as manufacturing specifications. Preserve author and agency attribution for designs incorporating commissioned Indigenous art.

Use an official record to establish who adopted a design and why, a photograph or museum record to establish a physical specimen, and a separate artwork record to describe a reconstruction. This permits multiple photos and several historical manufacturing variants to share one design without erasing their differences.

## Coverage and boundaries

The present catalogue is heavily weighted toward forest, parks and conservation history. The highest-value expansions are museum-held forestry role titles and aviation/Parattack patches, the later Sheriff Service crest, transit and rail police, ambulance insignia, and municipal policing. SAR, wildfire crews and local emergency services are additional collection programmes, each requiring its own documented scope.

The BCPP auction listing is a framed presentation piece; it is held rather than labelled an authentic historical issue. A Student Ranger recruitment graphic and the planned Haida guardian patch also remain held until physical production is documented. The BC Ferries branding archive is a useful lead, but its 325-page PDF exceeded the web reader size limit and was not reviewed.

Most principal patches on the Moosecop BC Parks history page already correspond to baseline designs. Additional photographs should strengthen evidence rather than multiply cards. In particular, a separately sewn RANGER tab, one-piece outerwear patch and cap-size version need explicit construction/scale attributes.

## Organization and storage recommendations

- A specimen photograph is evidence for a design, not automatically a new design.
- Keep organization, design family, wording/role, palette, manufacture/backing, and evidence status in separate fields.
- Generated recolours and a physical issue need different evidence states even when they share artwork.
- A detached title or qualification tab can form a documented assembly with a main patch without becoming a duplicate combined design.
- Shared template geometry does not establish organizational or historical identity.
- Save source documents once and refer to image/page/crop coordinates from multiple sightings; do not duplicate the same museum image for each accession component.
- Source dates, catalogue dates, first-seen dates and verified issue periods must remain distinct.

## Research record

Searches used official agency releases and annual reports, museum catalogues, heraldic grants, specialist collectors and dealer records. Museum or official publication is stronger evidence of physical use than an uncaptioned logo. Some pages describe design dates but not issue dates. The JSON records these limitations beside the relevant source.
