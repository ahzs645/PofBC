# Patch catalogue: coverage, template families and storage

Reviewed 13 November 2026. The current library has **154 patch and emblem variants and 14 badges**, displayed as 126 patch cards and 14 badge cards. This review identifies a documented expansion queue, adds a second way to browse related layouts, and improves repeated SVG loading. **No candidate artwork or source photographs were added by this work.**

The research baseline is PofBC [`1fb9e08`](https://github.com/ahzs645/PofBC/commit/1fb9e08dbb105bd691bed0790c81365b46ebc4f0), with Patcher [`68f145d`](https://github.com/ahzs645/patcher/commit/68f145d3f91fd3d915b0810b4faf19dd81b1e7e3). The Patcher implementation is published at [`da92d58`](https://github.com/ahzs645/patcher/commit/da92d583addc66b62d3f243a9684eccb3f9a73ec) in [Patcher PR #5](https://github.com/ahzs645/patcher/pull/5). Its tree, `420a5d723c7c41409ee3a36b5aa822dc0ade2747`, matches the tested implementation. Candidate comparisons retain the earlier baseline so later additions do not silently change what the research means.

## Review files

| File | Purpose |
| --- | --- |
| [patch-candidates-2026-11-13.json](patch-candidates-2026-11-13.json) | 44 candidate records, 43 sources, nearest baseline comparisons, proposed families, evidence status and next steps |
| [museum-specimens-2026-11-13.json](museum-specimens-2026-11-13.json) | 55 accession records from a bounded International Police Museum search, with deduplication and scope decisions still required |
| [research-findings.md](research-findings.md) | Source-linked research narrative and collection boundaries |
| [storage-audit.json](storage-audit.json) | Reproducible counts, storage measurements, existing groups, new families and exact preview duplicates |
| [validation.md](validation.md) | Commands, results and the limits of the browser checks |

## What the existing collection covers

The collection is strongest in Forest Service, Parks, Fish and Wildlife, and Conservation Officer history. Smaller groups cover Sheriff Service, Corrections, highways, institutional security, Hydro, Expo 86 and related organizations. Patcher has 22 organizations across both collections; 21 contain patches. Nine existing variant groups cover 37 designs and account for the difference between the 168 designs and 140 cards. The [storage report](storage-audit.json) records these totals directly from the manifest and files.

The atlas import already accounts for five merged repeat-photograph entries and 27 entries absorbed into supplied variants. Their old identifiers remain aliases. It also explicitly excludes 108 atlas entries, largely logos, signs, decals and other objects outside this patch collection. **Those exclusions are not a list of 108 missing patches.** The baseline Patcher [library documentation](https://github.com/ahzs645/patcher/blob/68f145d3f91fd3d915b0810b4faf19dd81b1e7e3/library/README.md) describes the import and its boundaries.

## Missing-design research

The candidate queue contains **43 patch candidates and one badge/pin candidate**. Its statuses describe the quality and kind of evidence; they do not declare that artwork is ready or that every candidate has been authenticated from a full-resolution photograph.

| Evidence status | Records | Meaning |
| --- | ---: | --- |
| Documented missing | 29 | A museum object or official publication establishes a design absent from the baseline labels/organizations; exact visual comparison and reconstruction remain |
| Collector candidate | 8 | Specialist, dealer or photographer evidence identifies a likely addition; issue authenticity and dates need confirmation |
| Documented, needs comparison | 2 | A physical component is documented, but attribution or relationship to existing designs needs image review |
| Documented, needs image | 2 | An agency confirms the patch exists; a specific usable visual specimen is still needed |
| Held: unverified issue | 1 | An object exists, but operational issue is unproven |
| Held: printed design only | 1 | A printed emblem is documented without a confirmed cloth equivalent |
| Held: planned only | 1 | The source describes a planned patch without confirmation of production |
| **Total** | **44** | **A bounded research queue, not an enumeration of every BC patch ever issued** |

There are also **11 corroboration records** for existing designs and a dated **30-crew research roster**. Neither is added to the missing-design count. The crew list comes from a July 2020 newsletter; it is not a current roster and does not prove 30 separate patch designs. See the [candidate inventory](patch-candidates-2026-11-13.json) for the source, status definitions and individual qualifications.

### Priorities with useful source evidence

| Priority addition | Why it belongs in the next collection pass | Evidence |
| --- | --- | --- |
| **Recreation**, **Revenue Inspector**, and **Forests and Lands** title strips | Specific forestry wordings missing from the current roster; accession components identify physical examples and duplicates | [Pemberton Museum, BCFS Patches, 014.06.11](https://www.pembertonmuseum.org/objects/bcfs-patches/) |
| **Forest Service / British Columbia / Aviation** | A museum-held aviation design to compare with the existing Airtanker artwork; the titles should not be treated as interchangeable | [Ingenium 2003.0257.001](https://collection.ingenium.ca/en/id/2003.0257.001/) |
| **Parattack**, winged parachutist | A distinct forestry aviation subject absent from the baseline | [Ingenium 2005.0019.001](https://collection.ingenium.ca/en/id/2005.0019.001/) |
| Later **BC Sheriff Service heraldic shoulder flash** | The current Sheriff group contains earlier crest and title layouts; compare the service-specific achievement separately | [Photographed shoulder flash](https://commons.wikimedia.org/wiki/File:BCSS_shoulder_flash_2.jpg), [Canadian Heraldic Authority grant](https://www.gg.ca/en/heraldry/public-register/project/2209) |
| **Vancouver Police city-arms shoulder flash** | An accessioned example starts a municipal-police family with physical-object evidence | [Museum of Vancouver H998.19.4](https://openmovportal.ca/argus/final/ViewRecord.aspx?lang=en-CA&record=0c543f81-f00f-4821-b5b7-fbfa5b65e3d1&template=Object) |
| **Surrey Police Service 2021 shoulder flash** | Official uniform and crest announcements provide an agency source for a new organization | [Uniform revealed](https://www.surreypolice.ca/news-events/news/surrey-police-service-uniform-revealed), [new crest](https://www.surreypolice.ca/news-events/news/new-crest-surrey-police-service) |
| **Saanich Police 2024 raven crest** | The agency's annual report documents the new crest; keep artist attribution and adoption context with the record | [Saanich Police 2024 Annual Report](https://saanichpolice.ca/wp-content/uploads/2025/09/2024-Annual-Report-Final-Version.pdf) |
| **South Coast BC Transportation Authority Police shoulder flash** | Adds the transit-police organization with an official publication; earlier BC Transit/TransLink collector examples remain a separate verification queue | [Transit Police 2013 Report to the Community](https://transitpolice.ca/wp-content/uploads/2016/04/2013_report_to_the_community.pdf) |
| Four **BC Railway Police crescent layouts** | Museum descriptions distinguish a white crescent, BC Rail lettering, dogwood disc and full railway name; compare the images before assigning exact issue periods | [International Police Museum uniforms inventory](https://www.internationalpolicemuseum.org/explore.php?category=Uniforms), [Railroad Police patches A–H](https://www.therailroadpolice.com/page-p) |
| **Ambulance / British Columbia shoulder roundel** | An important provincial service absent from the present collection; the paramedic tab and retired pocket crest need separate review | [BCEHS 2023/24 Progress Report](https://www.bcehs.ca/about-site/Documents/bcehs_progress_report_2023-24.pdf), [photographed badge](https://commons.wikimedia.org/wiki/File:British_Columbia_Ambulance_Badge.jpg) |
| **Fraser Unit Crew patch** | The newsletter establishes existence, while the specific visual reference remains outstanding | [Coastal Fire Centre Wildfire News, 17 July 2020](https://www.thetisislandfire.ca/newsletters/2020-07-17-Issue6-Coastal-Wildfire-News.pdf) |

The remaining candidate records include municipal memorial and ceremonial editions, historical transit security titles, BC Ferries, Natural Resource Officers, ambulance variants and Stl'atl'imx Tribal Police. Search and rescue, wildfire crews and local emergency services warrant their own collection passes. A provincial-police presentation piece, Student Ranger printed graphic and planned Haida guardian patch stay held for the reasons recorded in the [research findings](research-findings.md).

### The museum pass is a specimen inventory

The separate [International Police Museum inventory](https://www.internationalpolicemuseum.org/explore.php?category=Uniforms&subcategory=Patch) pass found **55 relevant accession records**:

| Classification | Accessions |
| --- | ---: |
| Potential additional design or variant specimens | 23 |
| Additional specimens linked to candidates already in the research queue | 19 |
| Potential corroboration of existing baseline designs | 7 |
| Collection-scope reviews | 5 |
| Unresolved rank insignia | 1 |

**Do not add 55, or the 23 potential additions, to the 44 candidate total.** Several accessions may depict one design; some explicitly overlap the candidate queue. The final pass includes three Matsqui specimens, six Port Moody specimens awaiting comparison with the existing candidate, and a Dawson Creek RCMP item requiring a scope decision. The pass used indexed catalogue descriptions, did not inspect every image, and did not retrieve the museum's entire inventory. Units omitted by the source remain unspecified. Two misleading geographical matches were excluded rather than admitted as BC patches. These limits are recorded beside the accession data in [museum-specimens-2026-11-13.json](museum-specimens-2026-11-13.json).

## Organizing patches by template

The curated Patcher [template catalogue](https://github.com/ahzs645/patcher/blob/da92d583addc66b62d3f243a9684eccb3f9a73ec/library/template-families.json) assigns **98 designs to 26 layout families**. For patches alone, this is **94 designs in 25 families**; the remaining family contains four numbered Park Ranger metal badges. Seventy designs across both collections remain unclassified and available under **Other designs**.

The largest useful cross-organization example is **Provincial ministry shield**: 15 designs across BC Parks, Environment, Corrections, Attorney General, and Highways. Other families cover Parks semicircles and title rockers, Game Warden/Commissioner/Inspector caps, Fish & Game/Fish & Wildlife shields, Conservation Officer shoulder and cap layouts, centennial tabs, and Sheriff/Corrections rockers. Existing Forest Oval groups are referenced once instead of repeating their member lists.

This relationship expresses a reviewed common arrangement. It does not establish an identical die, manufacturer, issue period or physical specimen. Each design retains its wording, organization, source sightings, limitations and artwork. Detached tabs remain separate from the shoulder patches they may accompany. A shared coat of arms alone is not enough to establish a template family.

The [gallery implementation](../../../src/patches/PatchesView.jsx) provides:

- Organization or template-family grouping, with organization and family filters that intersect.
- Search across names, variant wording, media, identifiers, aliases and family labels.
- Selection of the matching secondary variant, including its own thumbnail and link; an exact ID takes precedence over a longer ID containing it.
- Counts distinguishing cards and their matching variants.
- Preserved grouping, filters and query when opening a patch, closing it, or using browser history.
- Existing merged/absorbed links resolving to their canonical designs, with invalid filters recoverable.
- A generated-colourway notice only when the source notes explicitly identify a generated recolour, and source-photo counts that avoid counting multiple crops of the same photo twice.
- A lazy detail-view boundary so the gallery does not initialize the viewer until it opens.

An example review URL is `?view=patches&group=template&family=provincial-ministry-shield`. Browser visual acceptance remains outstanding; the checked behavior and its limits are described in [validation.md](validation.md).

## Storage and loading efficiency

The existing library already stores repeated SVG blocks and path outlines once. That architecture saves **71.17%** of logical drawing bytes and is retained. These are uncompressed file sizes, not measured HTTP transfer sizes or Git pack sizes. All figures below come from [storage-audit.json](storage-audit.json).

| Stored material | Bytes |
| --- | ---: |
| Full reconstructed drawings, if stored independently | 28,903,909 |
| Actual per-design SVG fragments | 1,950,183 |
| Shared blocks and path bundles | 6,383,691 |
| **Actual stored drawing data** | **8,333,874** |
| **Bytes already saved through sharing** | **20,570,035** |
| Gallery previews | 4,175,688 |
| Retained editable sources, references and review packages | 10,752,381 |
| Root catalogue/documentation metadata after this change | 359,062 |
| **Complete `library/` working-tree files after this change** | **23,621,005** |

There are 61 shared blocks and 294 shared paths in 15 bundles. A stored patch fragment must be joined with its dependencies to become a standalone SVG. The unchanged artwork hashes verify that this reconstruction preserves the original bytes.

The new improvement is a **16 MiB cache of completed joined SVG text**, with concurrent-request sharing, failure retry and least-recently-used eviction. It avoids re-fetching, rejoining and rehashing a recently opened drawing. In the file-backed loader check, `FO-green-gold-black` needed three asset fetches on its first load and **zero additional fetches on its second load**, with the expected SHA-256. This is evidence of loader behavior, not a browser-network benchmark or new disk-space saving. The limit covers retained UTF-8 text, not total browser heap; oversized drawings are returned without retention.

The `eager` asset imports register URL strings. They do not fetch every SVG body when the gallery starts. Shared bodies load on demand, and source packages under `supplied/` are excluded from these shallow runtime asset globs. Preserving those packages retains the material needed to explain and rebuild the artwork.

### Exact preview duplicates and the next large target

Three pairs of previews have identical bytes: `S56-O14`/`S56-O16`, `S56-O30`/`S56-O09`, and `S56-O27`/`S56-O10`. They account for **87,294 duplicate working-tree bytes**. Identical thumbnails do not prove identical historical specimens. Git already shares identical blob contents, and a bundler can deduplicate output assets, so this figure should not be presented as guaranteed repository-history or network savings.

The largest remaining shared component is the native Conservation Officer Service artwork, **4,829,306 bytes**, used by three designs. It accounts for approximately 58% of stored drawing data. A future display derivative could be investigated, with source preservation, attribution, visual comparison at relevant sizes, and independent quality review. No path simplification, source replacement, or speculative size reduction was performed here.

For future collecting, retain one source document or photograph and reference its page/crop from multiple sightings. Keep a template, its wording/role edition, physical specimen evidence and generated exports as distinct records. Source dates, collection dates, first-seen dates and verified issue periods should remain separately attributable.

## Acceptance and next decisions

The focused checks pass: **29 tests**, all **168 reconstructed drawing hashes**, Patcher typechecking, and the targeted viewer production build. DOM integration exercised grouping, search, aliases and history. **Desktop/mobile layout, browser networking and actual embroidery rendering have not been verified** because Chromium could not start under the runtime's socket restrictions and the cloud browser could not reach the local preview. The full site build and full site suite were outside this review. See [validation.md](validation.md) for the exact boundary.

The next collection step is to inspect the strongest museum/agency images, resolve candidate overlap, record edition and specimen evidence, and then create reviewed artwork. Source access does not establish reuse permission; the candidate inventory records the outstanding rights checks. The current queue deliberately preserves uncertainty instead of presenting research leads as completed catalogue additions.
