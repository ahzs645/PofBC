# British Columbia school districts

This collection connects the **60 current British Columbia public school districts** to their formation evidence, historical predecessors, names, logos, and existing salary-employer records. The current roster is grounded in the [provincial district directory](https://studentsuccess.gov.bc.ca/all/school-districts); the reviewed snapshot is dated **22 November 2026**.

Start with the [illustrated catalogue](CATALOGUE.md), the [November 25 vector review](VECTOR-REVIEW.md), or the [historical research notes](HISTORY-NOTES.md). The [original contact sheet](current-logos.jpg) shows the November 22 holdings. The application exposes the collection through `?view=school-districts`, with connected district detail, history, logo, source, and salary links.

## Coverage

| Material | Reviewed scope |
| --- | --- |
| Current district records | 60, each connected to its existing salary employer |
| Dated establishment or institutional-origin claims | 52: 46 with day precision and 6 with year precision |
| Unresolved current establishment dates | 8, with historical evidence retained in their timelines |
| Original-OIC-supported 1996 amalgamations | 15, creating 31 predecessor-to-successor connections |
| Historical predecessor records | 31 immediate predecessors abolished by those orders |
| Original 1946 archival district index | 74 numbered districts with original names and Gazette page locators |
| Current primary logos | 60: 29 vector and 31 raster |
| Additional logo assets | 6 earlier designs and 30 alternate files |
| Total logo files | 96 |
| Brand-history events | 12 sourced events in the logo research records |
| Recruitment-profile logo fallbacks | 2, explicitly labelled for SD50 and SD85 |

These figures are derived from [history.json](history.json), [logos.json](logos.json), and the [generated catalogue](../../../public/education/school-districts/catalogue.json). The 31 predecessor records establish the immediate 1996 lineage. The earlier logo files document marks used by current districts, and the predecessor artwork remains open.

## Reading a formation date

The establishment fields preserve the source's precision and meaning. A year-only statement remains a year; an unknown date remains `null`.

| Kind | Interpretation |
| --- | --- |
| `legal-creation` | The effective creation date stated in an original legal instrument. This applies to the 15 documented 1996 amalgamations. |
| `reported-establishment` | A date reported by the district or another retained historical source. Its source and qualifications remain attached. |
| `institutional-origin` | An earlier institutional or authority origin, which may precede the current numbered district or its later legal constitution. |
| `unresolved` | The inspected evidence does not establish a sufficiently supported formation date. |

The eight unresolved current dates are **SD28 Quesnel, SD41 Burnaby, SD45 West Vancouver, SD46 Sunshine Coast, SD47 qathet, SD54 Bulkley Valley, SD61 Greater Victoria, and SD63 Saanich**. Each has an original numbered-district boundary notice in its timeline. The [18 April 1946 Gazette](https://archive.org/details/governmentgazett86nogove_m4u8) dates those notices **12 April 1946**, but does not separately state legal commencement. Notice, publication, and effective creation dates therefore remain distinct.

The `disputed` flag identifies four unresolved source disagreements:

| District | Retained claims and qualification |
| --- | --- |
| SD75 Mission | Audited accounts report 12 April 1946, while the original 1946 Gazette identifies SD34 Abbotsford-Mission. The original instrument for Mission's later separation remains outstanding. |
| SD81 Fort Nelson | Accounts report an origin in 1955; a 1962 OIC cites an establishment instrument dated 20 April 1959. A possible later constitution has not been resolved. |
| SD92 Nisga’a | Audited accounts and the facilities plan support 1 January 1975. Other district publications give 1974 or 1976. |
| SD93 CSF | The original francophone authority is documented in 1995; the financial accounts separately report 3 January 1996. Later jurisdiction changes are separate milestones. |

The institutional-origin label applies to **SD70 Pacific Rim (1887)**, **SD81 Fort Nelson (1955)**, and **CSF (1995)**. Detailed citations and the reasoning behind these distinctions are in [HISTORY-NOTES.md](HISTORY-NOTES.md#source-differences-requiring-visible-qualifications). The catalogue places a source link and qualification beside every selected date.

## Merger evidence and identity

All **15 documented 1996 amalgamations took effect on 2 December 1996**. The orders approved on 25 July and 15 August are retained as separate events; their approval dates do not create additional lineage edges. The [merger table](CATALOGUE.md#the-1996-amalgamations) links each successor and its named predecessors to the original OIC. Each predecessor's abolition date is a sourced date object.

District numbers are reused. For example, historical **SD58 McBride** and current **SD58 Nicola-Similkameen** are different entities. The [1946 index](gazette-1946-district-index.json) also includes SD5 Creston, SD6 Kootenay Lake, SD8 Slocan, SD20 Salmon Arm, SD67 Ladysmith, SD73 Alert Bay, and SD74 Quatsino. Join records through their explicit identity and source-qualified relationship, rather than the district number alone.

The 74-entry index is a transcription aid for the original Gazette roster. It does not assert that all 74 entries have been connected to present-day successors or that their notice dates establish formation dates.

## Logo evidence

Every current district has a captured primary logo with its source URL, publisher or context, observation date, format, fidelity notes, and file hash. Where adoption evidence exists, it is recorded separately from the date on which a website or document was observed.

The selected current logos include 40 website captures, 18 based on district publications and two from **Make a Future** recruitment profiles for SD50 Haida Gwaii and SD85 Vancouver Island North. Those two fallbacks are identified in the data and catalogue.

The collection contains **29 vector primary marks and 31 raster primary marks**. An SVG that contains only bitmap artwork is classified as raster. Extracted source vectors preserve their native geometry. The data records each publication, page, extraction bounds and method. The gallery keeps the existing design links and provides the published images and source colourways through the version selector. The **12 brand-history events** retain their source and distinguish announcements, adoption, observed use, and related name changes.

White artwork is shown on a dark background in the application. The Markdown catalogue labels those marks so they remain identifiable when a document viewer uses a white canvas.

## Files and maintenance

| File | Purpose |
| --- | --- |
| [roster.json](roster.json) | Reviewed current provincial roster and official district URLs |
| [employers.json](employers.json) | Mapping to existing salary-employer slugs |
| [history.json](history.json) | Formation claims, source qualifications, timeline events, and immediate predecessors |
| [logos.json](logos.json) | Artwork provenance, assets, variants, and brand-history events |
| [VECTOR-REVIEW.md](VECTOR-REVIEW.md) | Vector coverage and remaining leads for all 60 districts |
| [gazette-1946-district-index.json](gazette-1946-district-index.json) | Original 74-district Gazette roster and page locators |
| [CATALOGUE.md](CATALOGUE.md) | Human-readable date, logo, and merger tables |
| [HISTORY-NOTES.md](HISTORY-NOTES.md) | Historical evidence, disagreements, and remaining research scope |
| [Public JSON catalogue](../../../public/education/school-districts/catalogue.json) | Generated current and historical entities, assets, and connections |
| [Generated application data](../../../src/schools/districtData.js) | Application copy of the reviewed catalogue |
| [Logo files](../../../public/education/school-districts/logos/) | Captured artwork used by the application and catalogue |
| [Retained artwork sources](../../../public/education/school-districts/sources/) | Source files needed to substantiate artwork extraction or conversion |

From the repository root, rebuild the application and public JSON outputs offline:

```sh
npm run build:school-districts
```

Check generated-file freshness, the district data and connections, and rendered integration links:

```sh
npm run check:school-districts
```

The check includes the school-district unit tests and a server-rendering check of directory, detail, gallery, source, and salary links at the `/PofBC/` base path. It verifies data and rendering structure; visual review remains a separate step. A focused freshness-only check is also available:

```sh
node scripts/build-school-districts.mjs --check
```

Edit the reviewed research inputs before rebuilding. Keep this documentation and the Markdown catalogue synchronized when changing the roster, date qualifications, lineage, or selected logos; the current data build does not regenerate these Markdown files.

### November 26 recovery supplement

[The review ledger](recoveries-2026-11-26.json) records all 70 researched
items against stable district IDs. It adds 62 artwork files, including 16
source-native SVGs, and preserves eight items as source links rather than
additional gallery artwork. The latter are three administrative
letterheads, one duplicate reproduction, three qathet/Powell River
items subject to external-use review, and the attributed Chilliwack
reconciliation programme artwork. Original source URLs, exact PDF page
locators where available, known artist credits, and extraction details
are preserved without republishing complete reports or correspondence.

The 2023 Gulf Islands full-colour SVG is the preferred version of the
existing current design; the original PNG remains available. The other
native recoveries are variants, separately documented signatures, or
historical evidence, not assumed current-logo replacements. The five
former district marks belong to the former entities, not their
successors. Related programme artwork is labeled separately from
district marks. Source document dates do not establish adoption dates.
Current and former district histories and succession links are unchanged.
