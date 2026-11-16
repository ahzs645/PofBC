# PofBC gallery and municipal identity audit

**As of 15 November 2026, America/Vancouver.** Repository snapshot: [`8f95bd67`](https://github.com/ahzs645/PofBC/commit/8f95bd6793e1e88e491db66ee3218148c37a17e4).

## Main finding

The highest-value next step is to make the gallery, identity register, heraldry and municipal records use one explicit organization catalogue. Municipal corporate branding is an entire missing collection family. At the same time, several existing artwork collections are absent from the register, so collecting additional images alone would leave the current navigation and coverage problems in place.

This audit identifies **162 current municipal or municipality-equivalent identities requiring a corporate-logo catalogue record**. That scope comprises **161 municipalities in BC's current legal municipal boundary layer, plus the separately classified shíshálh Nation Government District**. The current Logos gallery has no municipal corporate-logo subjects or entries. This is a statement about the collection's coverage, not a claim that every one of these governments has adopted a distinct corporate logo.

The repository already has useful municipal foundations: **119 municipalities with salary-employer records, 160 with council-pay labels, and 59 with heraldic-register references**. Those existing records can be connected without treating a heraldic reference or a salary record as a collected municipal logo.

## 1. What is already in the collection

| Measure | Audit count | Interpretation |
|---|---:|---|
| Gallery collections | 128 | Shelves and organization/program collections, not necessarily unique legal bodies |
| Unique gallery artwork entries | 291 | Entry IDs deduplicated across collections |
| Identity-register subjects | 269 | 105 curated subjects plus 164 inherited Crown/health subjects |
| Registered subjects with artwork | 123 | 76 vector-evidence, 39 raster-evidence and 8 reconstruction subjects |
| Source leads without accepted artwork | 36 | Research routes are present, but the subject does not yet own an accepted artwork entry |
| Other unresolved subjects | 110 | Includes 98 artwork-wanted, 11 distinct-identity-unconfirmed and 1 shared-identity record |
| Existing collections without a registered subject | 12 | A coverage/navigation join problem, not a new artwork acquisition problem |
| Unique entries absent from register coverage | 53 | 51 in the 12 collections plus two BC Cancer Foundation entries |
| Reconstruction entries with suppressed provenance presentation | 57 | Source metadata exists, but the relevant UI labels/descriptions are intentionally omitted |
| Entries with unknown artwork dates | 116 | Unknown dates should remain explicit until supported by evidence |
| Current municipal corporate-logo subjects/entries | 0 | Municipal branding is not yet a Logos collection family |

Counts were calculated from the [gallery collections](https://github.com/ahzs645/PofBC/blob/8f95bd6793e1e88e491db66ee3218148c37a17e4/src/gallery/collections.js), [identity subjects](https://github.com/ahzs645/PofBC/blob/8f95bd6793e1e88e491db66ee3218148c37a17e4/src/gallery/identitySubjects.js) and [coverage join](https://github.com/ahzs645/PofBC/blob/8f95bd6793e1e88e491db66ee3218148c37a17e4/src/gallery/identityCoverage.js). The gallery landing page independently displayed 269 subjects, 123 with artwork and 36 source leads. A live Collection register search for WorkSafeBC returned zero subjects, while the gallery contains five WorkSafeBC entries.

The counts use different units deliberately. A collection can contain several owners or eras, one subject can own several entries, and a colour variation can be part of a single design. The 53 unregistered entries should not become 53 new organizations. This audit found no duplicate IDs among the 291 unique gallery entries.

## 2. Municipality baseline and recent changes

The baseline joins all seven pages of [CivicInfo's current municipal directory](https://www.civicinfo.bc.ca/municipalities) to BC's [Municipalities — Legally Defined Administrative Areas layer](https://delivery.maps.gov.bc.ca/arcgis/rest/services/mpcm/bcgwpub/MapServer/3). All 161 provincial municipal records matched exactly one directory record. The additional CivicInfo entry is shíshálh Nation Government District, retained with its distinct governance classification.

The older [Municipalities in B.C. overview](https://www2.gov.bc.ca/gov/content/governments/local-governments/facts-framework/systems/municipalities) still says 161 and is dated November 2023. The current comparison must account for the **District of Okanagan Falls**, whose incorporation took effect **6 November 2026**. The [official Gazette notice](https://www.bclaws.gov.bc.ca/civix/document/id/bcgaz1/bcgaz1/470736345) records the effective date, and the new municipality appears in the current provincial layer and directory.

Important matching rules:

- **Langley City and Langley Township** are two records. **North Vancouver City and North Vancouver District** are also two records.
- **Daajing Giids** is the current municipal name. Queen Charlotte belongs in the historical aliases.
- **Northern Rockies Regional Municipality** is a current municipality. Fort Nelson is a historical predecessor, not an additional current coverage credit. The provincial layer does not assign Northern Rockies a separate parent regional district.
- **shíshálh Nation Government District and the District of Sechelt** remain separate records. The shíshálh district's former Sechelt Indian Government District name is an alias. Its [provincial naming update](https://news.gov.bc.ca/releases/2024IRR0021-000645) and [enabling legislation](https://www.bclaws.gov.bc.ca/civix/document/id/consol43/consol43/00_96416_01) establish the distinct context.
- **Jumbo Glacier** belongs only in historical coverage. Its [dissolution notice](https://www.bclaws.gov.bc.ca/civix/document/id/bcgaz1/bcgaz1/834862237) records dissolution in December 2021.
- Older demographic data split shíshálh across two statistical areas. Those parts represent one government identity here.
- Regional districts, First Nations, improvement districts, unincorporated communities, tourism organizations and municipal service brands require their own categories. A logo sharing a place name does not automatically belong to the municipal government.
- The new [Okanagan Falls website](https://okanaganfalls.ca/) was found, but this audit did not establish an adopted corporate logo. Its row should remain acquisition/research pending.

### Complete current list missing from the municipal corporate-logo catalogue

All names below lack a municipal corporate-logo entry in the audited Logos collection. Some have arms or other references elsewhere in PofBC. The workbook and CSV provide individual website, source and existing-record links for each row.

| Regional grouping | Count | Municipalities / government identities |
|---|---:|---|
| Alberni-Clayoquot | 3 | Port Alberni, Tofino, Ucluelet |
| Bulkley-Nechako | 8 | Burns Lake, Fort St. James, Fraser Lake, Granisle, Houston, Smithers, Telkwa, Vanderhoof |
| Capital | 13 | Central Saanich, Colwood, Esquimalt, Highlands, Langford, Metchosin, North Saanich, Oak Bay, Saanich, Sidney, Sooke, Victoria, View Royal |
| Cariboo | 4 | 100 Mile House, Quesnel, Wells, Williams Lake |
| Central Kootenay | 9 | Castlegar, Creston, Kaslo, Nakusp, Nelson, New Denver, Salmo, Silverton, Slocan |
| Central Okanagan | 4 | Kelowna, Lake Country, Peachland, West Kelowna |
| Columbia Shuswap | 4 | Golden, Revelstoke, Salmon Arm, Sicamous |
| Comox Valley | 3 | Comox, Courtenay, Cumberland |
| Cowichan Valley | 4 | Duncan, Ladysmith, Lake Cowichan, North Cowichan |
| East Kootenay | 8 | Canal Flats, Cranbrook, Elkford, Fernie, Invermere, Kimberley, Radium Hot Springs, Sparwood |
| Fraser Valley | 6 | Abbotsford, Chilliwack, Harrison Hot Springs, Hope, Kent, Mission |
| Fraser-Fort George | 4 | Mackenzie, McBride, Prince George, Valemount |
| Kitimat-Stikine | 5 | Hazelton, Kitimat, New Hazelton, Stewart, Terrace |
| Kootenay Boundary | 8 | Fruitvale, Grand Forks, Greenwood, Midway, Montrose, Rossland, Trail, Warfield |
| Metro Vancouver | 21 | Anmore, Belcarra, Bowen Island, Burnaby, Coquitlam, Delta, Langley (City), Langley (Township), Lions Bay, Maple Ridge, New Westminster, North Vancouver (City), North Vancouver (District), Pitt Meadows, Port Coquitlam, Port Moody, Richmond, Surrey, Vancouver, West Vancouver, White Rock |
| Mount Waddington | 4 | Alert Bay, Port Alice, Port Hardy, Port McNeill |
| Nanaimo | 4 | Lantzville, Nanaimo, Parksville, Qualicum Beach |
| North Coast | 5 | Daajing Giids, Masset, Port Clements, Port Edward, Prince Rupert |
| North Okanagan | 6 | Armstrong, Coldstream, Enderby, Lumby, Spallumcheen, Vernon |
| Northern Rockies Regional Municipality (no separate regional-district parent) | 1 | Northern Rockies |
| Okanagan-Similkameen | 7 | Keremeos, Okanagan Falls, Oliver, Osoyoos, Penticton, Princeton, Summerland |
| Peace River | 7 | Chetwynd, Dawson Creek, Fort St. John, Hudson's Hope, Pouce Coupe, Taylor, Tumbler Ridge |
| qathet | 1 | Powell River |
| Squamish-Lillooet | 4 | Lillooet, Pemberton, Squamish, Whistler |
| Strathcona | 5 | Campbell River, Gold River, Sayward, Tahsis, Zeballos |
| Sunshine Coast | 3 | Gibsons, Sechelt, shíshálh Nation Government District |
| Thompson-Nicola | 11 | Ashcroft, Barriere, Cache Creek, Chase, Clearwater, Clinton, Kamloops, Logan Lake, Lytton, Merritt, Sun Peaks |
| **Total** | **162** | **161 provincial-layer municipalities plus shíshálh Nation Government District** |

## 3. Existing municipal information that should connect

| Existing record set | Current municipalities matched | Proposed connection |
|---|---:|---|
| Municipal salary employers | 119 | Link the exact existing employer slug from the municipality profile and link back from its salary page |
| Council-pay labels | 160 | Add a Council pay section without changing or merging the source records |
| Heraldic-register references | 59 | Link arms, flags, badges and seals as distinct emblem types, with grant/registration dates preserved |
| Corporate logos in the Logos catalogue | 0 | Add current identity records and acquire original artwork against those records |

The 73 entries in the current municipal heraldry grouping are **registrations**, not 73 current municipalities. Of these, 69 registrations map to 59 current municipalities or their earlier municipal classifications; three belong to separate historical predecessor organizations; one belongs to the **Union of British Columbia Municipalities**, an association. The historical predecessor records are the District of Abbotsford, District of Matsqui and Town of Kinnaird. Their relationships should remain explicit rather than silently reassigned as current arms.

The current municipality arm references are rendered as external Canadian Heraldic Authority links in [ArmsView.jsx](https://github.com/ahzs645/PofBC/blob/8f95bd6793e1e88e491db66ee3218148c37a17e4/src/arms/ArmsView.jsx). They are useful evidence, but they are not locally held logo artwork. All 119 municipal salary-employer records have `body: null`; [EmployerPage.jsx](https://github.com/ahzs645/PofBC/blob/8f95bd6793e1e88e491db66ee3218148c37a17e4/src/salaries/EmployerPage.jsx) consequently has no organization-profile destination to offer for them. The existing [related-body system](https://github.com/ahzs645/PofBC/blob/8f95bd6793e1e88e491db66ee3218148c37a17e4/src/government/relatedBodies.js) provides a pattern for public bodies outside provincial ministry chronology.

The two current baseline jurisdictions without existing council-pay labels are Okanagan Falls and shíshálh Nation Government District. This audit checked record presence and identity joins; it did not re-audit the completeness or accuracy of the underlying remuneration data.

## 4. Prioritized cleanup

### 1. Register completeness (P1)

12 existing gallery collections have no subject in the Collection register. In total, 53 of 291 unique artwork entries are not represented by a registered subject.

**Evidence:** WorkSafeBC has five gallery marks but a live register search returns zero subjects. Other examples are BC Timber Sales, BC Parks, JIBC, BC OnLine and Shared Services BC.

**Recommended change:** Add explicit owner subjects for every existing collection and specimen, then calculate gallery and register counts from the same ownership mapping.

[Implementation evidence](https://github.com/ahzs645/PofBC/blob/8f95bd6793e1e88e491db66ee3218148c37a17e4/src/gallery/identityCoverage.js). Verification: Current main source inventory and live WorkSafeBC register search.

### 2. Municipal coverage (P1)

The Logos gallery has no municipal-government family or current municipal corporate-logo entries.

**Evidence:** 162 identities in this audit scope: 161 provincial-layer municipalities plus the separately classified shíshálh Nation Government District. Metro Vancouver and West Vancouver Blue Bus are not municipal corporate-logo coverage.

**Recommended change:** Add a Municipalities family with stable provincial IDs, legal type, regional district, historical aliases and explicit corporate-logo acquisition status.

[Implementation evidence](https://github.com/ahzs645/PofBC/blob/8f95bd6793e1e88e491db66ee3218148c37a17e4/src/gallery/identitySubjects.js). Verification: Full current provincial-layer/CivicInfo join and gallery subject inventory.

### 3. Connect existing municipal records (P1)

Municipal information is spread across Arms, salary employers and council-pay records without one shared municipal profile.

**Evidence:** 119 municipal salary employers have body:null. The arms register contains 73 municipal-group registrations, including historical recipients and an association, rendered as external register links.

**Recommended change:** Join current municipality, corporate logos, heraldry sources, council pay and salary employers using explicit mappings. Preserve historical recipients and separate legal entities.

[Implementation evidence](https://github.com/ahzs645/PofBC/blob/8f95bd6793e1e88e491db66ee3218148c37a17e4/src/arms/ArmsView.jsx). Verification: Source inspection plus stored arms and salary metadata inventories.

### 4. Artwork provenance (P1)

The gallery deliberately suppresses reconstruction provenance/fidelity labels for 57 artwork entries.

**Evidence:** BC Development Corporation has five reconstructed entries and two raster specimens, but its collection chip reads Published image. BC Trade's reconstructed SVG has no provenance chip.

**Recommended change:** Show concise Original vector, Extracted vector, Raster specimen or Reconstruction labels consistently on cards and details. Keep source specimens and reconstructions linked for comparison.

[Implementation evidence](https://github.com/ahzs645/PofBC/blob/8f95bd6793e1e88e491db66ee3218148c37a17e4/src/gallery/GalleryView.jsx). Verification: Current main provenance inventory and rendering-condition inspection.

### 5. Organization relationships (P2)

Identity details display outgoing relationships only, so parent organizations do not show the full set of children that point to them.

**Evidence:** TransLink has 16 incoming relations and no outgoing relations. PHSA has five incoming, PavCo two and LTSA one. Family membership is a separate concept.

**Recommended change:** Derive inverse relationship links and label subsidiaries, services, operators, predecessors and successors distinctly. Show both directions without equating membership with ownership.

[Implementation evidence](https://github.com/ahzs645/PofBC/blob/8f95bd6793e1e88e491db66ee3218148c37a17e4/src/gallery/IdentityCoverage.jsx). Verification: Source relation inventory and detail rendering inspection.

### 6. Gallery navigation (P2)

The landing gallery presents a long combined public-body shelf; family and evidence filters are confined to the register.

**Evidence:** Current home view and GalleryView map all bodies into one section. Municipalities would substantially enlarge that list.

**Recommended change:** Add family, region, current/historical, artwork type and evidence filters to the image gallery, backed by the same records as the register. Offer an A–Z list alongside thumbnails.

[Implementation evidence](https://github.com/ahzs645/PofBC/blob/8f95bd6793e1e88e491db66ee3218148c37a17e4/src/gallery/GalleryView.jsx). Verification: Live home view and source rendering inspection.

### 7. Consistent context links (P2)

Artwork pages exclude legacy subjects from IdentityCollectionLinks, leaving many historical records without the same register context links as curated subjects.

**Evidence:** subjectsForCollection(collectionId).filter(subject => !subject.legacy) controls the shared context section.

**Recommended change:** Give every artwork page the same links to its identity profile, history, related bodies and research gaps, including legacy records.

[Implementation evidence](https://github.com/ahzs645/PofBC/blob/8f95bd6793e1e88e491db66ee3218148c37a17e4/src/gallery/IdentityCoverage.jsx). Verification: Current main component inspection.

### 8. Dates and names (P2)

116 of 291 unique entries have unknown artwork dates. Organization lifetime and logo-use evidence need distinct presentation.

**Evidence:** The existing applicability metadata distinguishes adoption, first observation, dated specimen and unknown dates; many collection cards still lead with organization years or Dates unestablished.

**Recommended change:** Display organization lifespan separately from the dated logo specimen. Record new municipal branding changes and keep undated marks explicitly undated.

[Implementation evidence](https://github.com/ahzs645/PofBC/blob/8f95bd6793e1e88e491db66ee3218148c37a17e4/src/gallery/collections.js). Verification: Current main entry metadata count and live card labels.

### 9. Link behaviour (P3)

Gallery collection and subject navigation is primarily implemented as buttons, although a reusable SiteLink component already exists.

**Evidence:** CollectionCard and SubjectButton invoke navigation callbacks instead of exposing ordinary link destinations.

**Recommended change:** Use real anchors for navigation so people can copy links, open another tab, use browser menus and retain gallery/register filter context.

[Implementation evidence](https://github.com/ahzs645/PofBC/blob/8f95bd6793e1e88e491db66ee3218148c37a17e4/src/site/navigation.jsx). Verification: Live DOM roles and component inspection.

### Existing collections to reconcile first

| Collection | Existing entries | Link |
|---|---:|---|
| BC Timber Sales | 2 | [Open collection](https://projects.ahmadjalil.com/PofBC/?view=gallery&logos=bcts) |
| WorkSafeBC | 5 | [Open collection](https://projects.ahmadjalil.com/PofBC/?view=gallery&logos=worksafebc) |
| BC Parks | 5 | [Open collection](https://projects.ahmadjalil.com/PofBC/?view=gallery&logos=bc-parks) |
| On the BC mark | 18 | [Open collection](https://projects.ahmadjalil.com/PofBC/?view=gallery&logos=bc-mark) |
| BC Public Service | 1 | [Open collection](https://projects.ahmadjalil.com/PofBC/?view=gallery&logos=specimens-public-service) |
| Canada Starts Here | 2 | [Open collection](https://projects.ahmadjalil.com/PofBC/?view=gallery&logos=specimens-pacific-gateway) |
| StrongerBC | 6 | [Open collection](https://projects.ahmadjalil.com/PofBC/?view=gallery&logos=specimens-stronger-bc) |
| WelcomeBC | 2 | [Open collection](https://projects.ahmadjalil.com/PofBC/?view=gallery&logos=specimens-welcome-bc) |
| WorkBC | 2 | [Open collection](https://projects.ahmadjalil.com/PofBC/?view=gallery&logos=specimens-work-bc) |
| JIBC | 2 | [Open collection](https://projects.ahmadjalil.com/PofBC/?view=gallery&logos=collected-justice-institute) |
| BC OnLine | 2 | [Open collection](https://projects.ahmadjalil.com/PofBC/?view=gallery&logos=collected-sub-bc-online) |
| Shared Services BC | 4 | [Open collection](https://projects.ahmadjalil.com/PofBC/?view=gallery&logos=collected-shared-services-bc) |

The additional two unregistered entries belong to BC Cancer Foundation. They are stored within the BC Cancer collection but have distinct artwork ownership. Add a Foundation subject rather than assigning the Foundation's artwork to the health agency. Some program specimens share collections by design; reconciliation should preserve those arrangements.

The legacy-context issue affects 66 subjects that already hold artwork. For example, BC Assessment, BC Games, Legal Aid BC and FPCC can have an atlas connection while still lacking the uniform register context link. This is specifically a missing register return/context path, not a claim that those pages have no links at all.

## 5. Original municipal artwork and useful sources located

This research pass produced **24 annotated municipal acquisition records**. It directly fetched and checked the formats of **26 official-site files for 23 municipalities**. Four municipalities serve SVG files containing vector geometry and no embedded raster image elements. Nineteen have verified official PNG references. Kitimat supplies the remaining brand-guide lead. These are source acquisitions for review; they have not been imported into PofBC.

### Immediate original-SVG candidates

| Municipality | Official source asset | Acquisition consideration |
|---|---|---|
| Burnaby | [Official SVG](https://www.burnaby.ca/themes/custom/burnaby/logo.svg) | Keep the current source and research the documented 1976/1992 identity history |
| Surrey | [Official footer SVG](https://www.surrey.ca/themes/custom/surrey/images/logo-footer.svg) | Identify this exact variant and obtain other official layouts/grounds where available |
| Saanich | [Official SVG](https://www.saanich.ca/images/saanich-logo.svg) | Keep the published green, black and reverse-white variants distinct |
| Vanderhoof | [Logo SVG](https://vanderhoof.ca/wp-content/themes/vanderhoof/img/logo-2.svg) and [dark variant](https://vanderhoof.ca/wp-content/themes/vanderhoof/img/logo-dark-2.svg) | Preserve both original website variants and verify their intended backgrounds |

### Complete first source batch

| Municipality | Verified file / lead | Primary page | History or acquisition note |
|---|---|---|---|
| Abbotsford | [PNG](https://www.abbotsford.ca/sites/default/files/city%20of%20abbotsford%20logo.png) | [Official source](https://laws.abbotsford.ca/civix/document/id/coa/coaother/c00201) | Municipal policy distinguishes corporate logo, arms, seal, flag and tartan; tagline city in the country. City logo and coat of arms should be separate records. |
| Burnaby | [SVG](https://www.burnaby.ca/themes/custom/burnaby/logo.svg) | [Official source](https://www.burnaby.ca/our-city/about-burnaby/coat-arms-and-city-symbols) | Official history says logo adopted in 1976 and redesigned with new colour/font in 1992. Coat of arms, seal, flag and civic badge are separate symbols. |
| Burns Lake | [PNG](https://www.burnslake.ca/sites/default/files/Burns%20Lake%20Logo.png) | [Official source](https://www.burnslake.ca) | Current municipal website logo verified; adoption date and historical variants not established. |
| Chilliwack | [PNG](https://www.chilliwack.com/images/logo.png) | [Official source](https://www.chilliwack.com/main/home.cfm) | Current municipal website logo verified; adoption date and historical variants not established. |
| Coquitlam | [PNG](https://www.coquitlam.ca/ImageRepository/Document?documentID=42) | [Official source](https://www.coquitlam.ca/FormCenter/Corporate-Services-15/City-Logo-Request-100) | Current homepage masthead independently verified PNG. Manual source is a stale/unresolved lead. |
| Dawson Creek | [PNG](https://media-002-ca.cdn.govstack.com/dawsoncreek-013-ca/media/fjanq1di/dawson-creek-logo.png) | [Official source](https://www.dawsoncreek.ca) | Current municipal website logo verified; adoption date and historical variants not established. |
| Fort St. John | [PNG](https://www.fortstjohn.ca/sites/default/files/Fort%20St%20John%20Logo.png) | [Official source](https://www.fortstjohn.ca/) | Current municipal website logo verified; adoption date and historical variants not established. |
| Kamloops | [PNG](https://www.kamloops.ca/sites/default/files/kamloops-logo-home.png) | [Official source](https://www.kamloops.ca/recreation-culture/event-hosting/event-planning-guidelines) | Official event guidance names Canada’s Tournament Capital logo and provides a logo-request route. |
| Kelowna | [PNG](https://www.kelowna.ca/sites/all/themes/kelowna/images/kelowna-logo-main.png) | [Official source](https://www.kelowna.ca/city-hall/contact-us/visual-identity-and-logo-request) | Official site offers EPS and PNG by request; current website serves stacked and horizontal PNG layouts. Neither PNG is vector. |
| Kitimat | [PDF source lead](https://docs.kitimat.ca/docs/2026-05-04-reg.pdf) | [Official source](https://www.kitimat.ca/municipal-office/communications-policy) | Corporate snowflake logo/wordmark documented in official brand guide. Kitimat Bound/Kitimat Now are separate promotional identities, not interchangeable city logos. |
| Mackenzie | [PNG](https://districtofmackenzie.ca/wp-content/uploads/2020/11/Logo-mobile.png) | [Official source](https://districtofmackenzie.ca/) | Current municipal website logo verified; adoption date and historical variants not established. |
| Nanaimo | [PNG](https://www.nanaimo.ca/images/site-images/logo.png) | [Official source](https://www.nanaimo.ca/about-nanaimo/history-of-nanaimo/the-city%27s-emblems) | Official page distinguishes City Logo and Community Logo. The 2024 150th-anniversary logo is another time-limited mark, not a replacement to infer from a report cover. |
| Prince George | [PNG](https://www.princegeorge.ca/sites/default/files/pg-logo-2024-oct.png) | [Official source](https://www.princegeorge.ca/sites/default/files/2025-06/Prince%20George%20Annual%20Report%202024%20-%20FINAL.pdf) | The 2024 annual report, printed page 14, says the new brand launched in May and the refreshed logo retained the fraise and confluence. Catalogue pre-2024 and 2024 versions separately. Report is 48 MB and exceeds web-reader limit. |
| Prince Rupert | [PNG](https://www.princerupert.ca/sites/7/files/logo_3.png) | [Official source](https://www.princerupert.ca/index-pages/news/city-prince-rupert-adopts-new-look) | 2022 redesign by Will Creative with Ts’msyen artist Russell Mather. Official notice describes modified rainbow arch and custom formline-influenced lettering. |
| Quesnel | [PNG](https://www.quesnel.ca/themes/custom/quesnel/images/logo.png) | [Official source](https://www.quesnel.ca/city-hall/reports-documents/brand-visual-language) | Official corporate visual-language publication dated 2017; current website logo independently verified as PNG. |
| Richmond | [PNG](https://www.richmond.ca/__shared/templates/assets/img/logo.png) | [Official source](https://www.richmond.ca) | Current municipal website logo verified; adoption date and historical variants not established. |
| Saanich | [SVG](https://www.saanich.ca/images/saanich-logo.svg) | [Official source](https://www.saanich.ca/EN/main/local-government/saanich-logo.html) | Guide specifies green, white reverse and black versions, and says the green/yellow version is being discontinued. Do not treat former green/yellow as current. |
| Smithers | [PNG](https://www.smithers.ca/themes/custom/smithers/images/smithers-tagline-logo.png) | [Official source](https://www.smithers.ca) | Current municipal website logo verified; adoption date and historical variants not established. |
| Surrey | [SVG](https://www.surrey.ca/themes/custom/surrey/images/logo-footer.svg) | [Official source](https://www.surrey.ca) | Official website footer logo verified as true SVG. Adoption date not established. |
| Terrace | [PNG](https://www.terrace.ca/sites/default/files/header-logo.png) | [Official source](https://www.terrace.ca/) | Current municipal website logo verified; adoption date and historical variants not established. |
| Vancouver | [PNG](https://vancouver.ca/images/cov/ui/covLogo.png) | [Official source](https://vancouver.ca/news-calendar/city-symbols.aspx) | Emblem adopted July 18 2006; arms are a different ceremonial identity. Guide states black/white emblems use gaps absent in colour artwork and must not be made by simply recolouring the colour mark. |
| Vanderhoof | [SVG](https://vanderhoof.ca/wp-content/themes/vanderhoof/img/logo-2.svg) | [Official source](https://vanderhoof.ca/) | Two current website SVG variants verified; adoption date not established. |
| Victoria | [PNG](https://www.victoria.ca/sites/default/files/Victoria%20Logo_0.png) | [Official source](https://www.victoria.ca) | Current municipal website logo verified; adoption date and historical variants not established. |
| Williams Lake | [PNG](https://www.williamslake.ca/ImageRepository/Document?documentID=5607) | [Official source](https://www.williamslake.ca) | Current municipal website logo verified; adoption date and historical variants not established. |

### Sources that change how the gallery should work

**Vancouver: geometry differs between official colour variants.** The [February 2018 visual standards guide](https://policy.vancouver.ca/CP00103P2.pdf), printed page 5, shows that the black and reverse-white emblems have gaps absent from the colour emblem. Consequently, a generic recolouring operation would not reproduce the official black/white geometry. Store the supplied variants and choose the appropriate one for the background. The same guide treats the corporate emblem and coat of arms separately.

**Saanich: a historical colourway should not become the default current mark.** Its [official one-page guide](https://www.saanich.ca/assets/Local~Government/Documents/logo-guidelines-third-parties.pdf) identifies green, black and white-reverse options and says the green/yellow version is being discontinued. Keep that older version as a dated specimen when evidence supports its dates.

**Burnaby: the modern logo has a documented history independent of the arms.** The [city's symbols page](https://www.burnaby.ca/our-city/about-burnaby/coat-arms-and-city-symbols) records a 1976 logo adoption and a 1992 change to colour and typography, alongside separate civic arms, seals, flag and badge. This supplies a strong example for a municipality profile with several distinct symbol types and eras.

**Prince Rupert: preserve designer and cultural provenance.** The [2022 redesign announcement](https://www.princerupert.ca/index-pages/news/city-prince-rupert-adopts-new-look) credits Will Creative and Ts’msyen artist Russell Mather. It explains the rainbow arch and custom formline-influenced lettering. Those details belong in the artwork's evidence record; a generic rainbow or substituted typeface would lose relevant design information.

**Nanaimo: municipal and community marks are distinct.** The [city's emblems page](https://www.nanaimo.ca/about-nanaimo/history-of-nanaimo/the-city%27s-emblems) distinguishes the City Logo and Community Logo. The [150th anniversary identity](https://www.nanaimo.ca/NewsReleases/NR240325Recognizing150YearsOfIncorporation.html) also warrants its own dated record. A single place-name thumbnail cannot capture these distinctions.

**Prince George: keep the 2024 refresh separate from older specimens.** The [2024 annual report](https://www.princegeorge.ca/sites/default/files/2025-06/Prince%20George%20Annual%20Report%202024%20-%20FINAL.pdf), printed page 14, is indexed with the brand refresh account. The current official homepage PNG was fetched and checked. The approximately 48 MB report exceeded the web reader limit in this pass; the refresh passage was available through the search index, and no claim is made that the report's vector content was inspected.

**Quesnel, Kelowna, Coquitlam and Kitimat need careful source follow-through.** Quesnel's official publication page yields a [visual-language PDF link](https://www.quesnel.ca/sites/default/files/2024-11/migrated/files/city_of_quesnel_visual_language_final.pdf), but its contents were not opened successfully in this pass. Kelowna's [current identity page](https://www.kelowna.ca/city-hall/contact-us/visual-identity-and-logo-request) offers an EPS/PNG request route; an older indexed guide URL returned 404. An indexed Coquitlam standards PDF also returned 404, so the register uses the verified website PNG and [current request route](https://www.coquitlam.ca/FormCenter/Corporate-Services-15/City-Logo-Request-100). Kitimat's [May 4, 2026 agenda](https://docs.kitimat.ca/docs/2026-05-04-reg.pdf) contains brand guidance, but an agenda attachment alone does not establish final adoption: retrieve the final policy/guide before assigning a logo era.

## 6. Suggested information model and interface

### A municipality profile should provide one place to enter the collection

For example, a Prince George profile would identify the City, its stable provincial identifier, official website and regional-district membership. It would then connect the corporate logo, heraldic arms, historical specimens, council pay and salary-employer record. The profile would show which artwork is held and which source leads still need collection.

| Record | Owns | Connects to |
|---|---|---|
| Municipality / organization | Stable ID, legal name, type, current and historical aliases, official site | Regional membership, predecessors, services, salary-employer slugs, council-pay labels |
| Identity / emblem | Corporate mark, arms, seal, flag, badge, community brand, tourism brand or service identity | Its actual organization owner and documented period of use |
| Artwork specimen | Original file, format, checksum, layout, official colourway, source and observation date | The identity it represents and any linked reconstruction/comparison |
| Evidence record | Source URL, document title/page, retrieval date, credited creator, date basis | The claims supported by that source |
| Relationship | Typed edge with source and dates where known | Member-of, owned-by, operated-by, service-of, predecessor-of and successor-of connections |

Municipalities should not be assigned to provincial ministries just to satisfy the current `body` field. Regional-district membership also should not be represented as ownership. Add an appropriate organization/profile destination and preserve the already distinct salary sources.

### The main gallery needs a few visible controls

Recommended primary controls are **Search**, **Family**, **Region**, **Current/historical**, **Artwork type** and **Evidence**. The image gallery and register should read the same filters and catalogue. A list view should let researchers compare names, dates and coverage without scrolling through every large thumbnail. A map can be added after the shared IDs and regional affiliations are reliable; it is not a prerequisite for solving the present gaps.

Opening an artwork should retain its organization context and offer its related specimens, source document and next research step. A person who opens a municipality from Salaries should be able to reach its symbols and return to the same employer record. Gallery navigation should expose real links, so opening two marks in separate tabs is a normal browser action.

Show **format**, **provenance** and **review state** separately. A reconstructed SVG has a vector format but reconstruction provenance. A raster scan can be an authentic source specimen. A complete-looking colourway does not prove historical completeness. The existing evidence-state design already captures much of this distinction; the presentation should use it consistently.

## 7. Recommended implementation sequence

### First change: reconcile existing records and links

Add the missing gallery-owner subjects; account for all 291 entries; include legacy context links; derive incoming as well as outgoing relations; restore visible reconstruction provenance. Keep the existing collection and mark URLs working. Confirm that WorkSafeBC is discoverable from both the gallery and register and that the displayed totals describe their scope clearly.

### Second change: add the complete municipality registry

Add the 162-record baseline with a 161-municipality subtotal and a separately classified shíshálh record. Connect the 119 salary employers, 160 council labels and 59 municipalities with heraldry references through explicit IDs. Preserve the historical predecessor arms separately and classify UBCM as an association. New records should be visible as acquisition gaps before their logo files arrive.

### Third change: import the first original-artwork batch

Start with Burnaby, Surrey, Saanich and Vanderhoof's available SVGs, then the northern/central BC group: Prince George, Quesnel, Williams Lake, Terrace, Prince Rupert, Fort St. John, Dawson Creek, Smithers, Burns Lake, Mackenzie and Kitimat. Accept verified PNGs as raster evidence while original vector acquisition continues. Add official source guidance and dated historical variants as evidence permits.

### Fourth change: make the expanded collection easy to browse

Add gallery filters, list view and consistent profile breadcrumbs, then extend the same acquisition process across the remaining municipal records. Keep geographical filters, municipal-service identities and tourism brands distinct. A future map can use the already collected provincial IDs rather than a second parallel municipality list.

### Acceptance criteria for the future implementation

- Every held gallery entry has an explicit owner or a documented deliberate ownerless category.
- The register and gallery agree about held artwork for the same subject.
- Both Langley jurisdictions and both North Vancouver jurisdictions remain independently searchable.
- Okanagan Falls appears as a current municipality with unestablished corporate-artwork status; Jumbo remains historical.
- Salary, council and arms links point to exact existing records without merging their data.
- TransLink, PHSA, PavCo and LTSA expose relevant incoming relationships with correct labels.
- Original/reconstructed, vector/raster, organization dates and specimen dates remain distinct.
- Official colour variants keep their own geometry where the source specifies it.
- Copy-link, open-in-new-tab, browser Back and filtered-list return work from gallery and subject pages.

These are proposed checks for an implementation. This audit did not modify the repository, deploy changes, run GitHub Actions, or send requests to municipalities.

## 8. Method, evidence and limits

The analysis used the live gallery and register, a read-only source checkout at the pinned commit, the complete municipal directory and official legal boundary records, the repository's current salary/council/heraldry metadata, and official municipal branding sources. Source inventory counts were calculated from the current JavaScript collection/coverage exports. The municipality crosswalk preserves source identifiers and explicit collision handling.

The **full current-municipality gap list is complete against the stated baseline**. The **24-row logo-source pass is a prioritized first batch**, not an exhaustive search for every historical municipal logo or vector master. All 162 baseline rows have official website leads listed in CivicInfo, but every destination was not opened individually. The workbook distinguishes directory-supplied website leads from directly fetched original SVG/PNG files and from uninspected guide links.

The live home, register categories, WorkSafeBC zero-result search and TransLink relationship presentation were reviewed. Early browser interaction with the first gallery tab timed out; the register worked in a fresh tab, so this was not treated as a proven product-wide navigation defect. No claim of complete mobile, accessibility or export testing is made.

Repository findings are tied to the stated commit. A later merge or deployment can change these counts. Source formats, checksums and URLs were recorded for the first acquisition batch. An original asset's existence does not establish complete historical coverage, an adoption date or the availability of all official colourways.

## Files accompanying this report

- **PofBC_Municipal_Logo_Audit_2026-11-15.xlsx** — municipality checklist, verified source leads, prioritized cleanup and existing register gaps.
- **BC_Municipal_Logo_Gaps_2026-11-15.csv** — the complete individual municipal coverage and connection table, suitable for import or further research.

The workbook is the convenient review surface. The CSV preserves row-level source links and existing-record connections. This report explains the decisions and recommended implementation order.
