# Identity coverage: implementation and review

The gallery's original automatic acquisition list selected only Crown corporations and health authorities. That left regional authorities such as TransLink, agencies such as the Liquor Distribution Branch, and service identities such as Compass outside the register even when their organizations or salary records were already known.

This change introduces an explicit identity-subject register, accepts source artwork where it can be inspected, and connects the collection to organization and salary records. Research leads remain visible when artwork is still missing. The register is a declared research scope, not a census of every institution in British Columbia.

## What is included

- **105 curated subjects in 19 families**, including the full named audit scope: regional transit, Metro Vancouver, the LDB retail and wholesale family, Creative BC and BC Arts Council, emergency communications, ferry governance, development trusts, specialist health services, regulators, independent officers, courts, and historical agency identities. Six named wider institutions have a separate scope filter.
- **40 additional artwork collections containing 43 entries**: 21 vector artworks and 22 raster specimens. These extend the existing gallery without replacing its historical artwork or public links.
- **56 source and artwork files**, with recorded byte lengths and SHA-256 checksums. Original website assets, archived PDF pages, print-master members and extracted display files retain their own provenance.
- **18 current related-body records** with explicit governance classifications, separate from the provincial executive chronology.
- **12 employer-file links across 11 organizations**, reusing existing salary disclosures. The two Transit Police files remain separate.

The earlier 184-target Crown/health queue is retained. Overlapping curated subjects replace its generic description, so the combined register has **269 unique subjects**. Evidence counts are calculated at runtime from the actual gallery entries.

## Data model

| Layer | Location | Responsibility |
|---|---|---|
| Identity subject | `src/gallery/identitySubjects.js` | Name, aliases, legal/service kind, family, scope, priority, sources, remaining work and typed relationships. It does not assert that artwork is held. |
| Accepted artwork | `research/identity/coverage-expansion-2026-11-15/assets-manifest.json` | Source URLs, locators, publication/observation context, format, checksums, original files and reproducible extraction recipes. |
| Generated artwork data | `src/gallery/expandedIdentityData.js` | Deterministic browser data generated from the manifest. |
| Collection assembly | `src/gallery/collectedCollections.js` | Adds the new records to the established collection machinery. An explicit `graphNode: null` supports a service identity without inventing a legal organization. |
| Runtime coverage | `src/gallery/identityCoverage.js` | Joins subjects to their own entries, derives evidence states, retains the legacy queue and supplies filtering/search. |
| Related organizations | `src/government/relatedBodies.js` | Current sourced records for regional and independent organizations, typed relationships and exact employer-slug links. |

### Ownership determines coverage

A subject receives only entries whose owner resolves to that subject. An explicit parent collection, family relationship or atlas link does not confer the parent's artwork on a service. The same rule works within a shared historical shelf:

- Historical BC Ferry Authority and Urban Transit Authority retain their own raster specimens; their successors' vectors do not upgrade them.
- The BC Cancer Foundation remains a separate owner within the existing BC Cancer family collection.
- The modern `bc-ferry-authority-2003` is distinct from `bc-ferry-authority`, the 1964–1977 body.
- TransLink, CMBC, BCRTC, West Coast Express, the network T marker, SkyTrain, SeaBus, HandyDART and Compass are separate subjects, with relationships between them.
- A search for **GVTA** can find TransLink and the historical **GVTA Police** alias as separate results. **BCRTC** resolves to the operator rather than treating it as another name for the entire network.

The collection register derives the strongest artwork evidence actually held. A raster SVG wrapper is not a source vector, and a reconstruction saved as SVG remains a reconstruction.

| State | Meaning |
|---|---|
| Vector artwork held | At least one source vector is accepted. Other eras, variants or adoption evidence may remain missing. |
| Raster specimen held | A published image is accepted; a clean vector remains a useful acquisition target. |
| Reconstruction held | Reconstructed artwork is explicitly identified. |
| Artwork held | An existing entry has another documented provenance; its own evidence record remains authoritative. |
| Source located | A primary source or request/download route is recorded; no accepted artwork is counted. |
| Shares another identity | A source documents shared identity use, qualified to the evidence actually inspected. |
| Distinct identity unconfirmed | Research has not established a separate identity; this does not assert that none existed. |
| Artwork wanted / not yet catalogued | A known organization or candidate remains open for acquisition and research. |

No overall “percent complete” is claimed. Rights, file provenance, visual fidelity, publication dates and adoption dates remain separate questions.

### Dates and source colours

Website observation dates are not logo adoption dates. A dated document establishes a specimen sighting, with its supplied precision; years embedded in a URL or prose are not promoted to adoption dates. The subject's `graphYear`, where present, is navigation metadata derived from an existing atlas lifespan. It opens a historical organization in a valid year and does not date the logo.

The new artwork uses the source-file viewer, preserving source colours and transparency. White originals receive a dark display plate. There is no automatic palette generator for these files. The TransLink T marker therefore remains in the documented source colourway, with its toolkit guidance attached. Download links distinguish the accepted file from additional original print/source files.

## User-facing flow

The gallery landing page introduces the **Collection register**. Its filters cover names/aliases, family, evidence state and core versus wider-institution scope. Filters live in the URL. A subject page shows its identity context, artwork held, next research work, primary sources, and related subjects. Existing collection and single-mark pages link back to this context.

Organization links open either an existing provincial atlas node or the **Related public bodies** directory. Regional organizations are not inserted into a provincial ministry or projected back through the historical slider. Related records describe their current governance and explicitly say that their full chronology has not yet been reconstructed.

Salary navigation uses the original employer slugs and observations. A small runtime adapter adds exact organization links to both metadata shapes used by the salary UI. It preserves array offsets, periods, numeric values, source records and aliases. TransLink, CMBC, BCRTC and West Coast Express receive a corrected display sector, `Regional transportation`; their original sector remains in source metadata. The adapter neither merges employers nor infers person matches.

## Review routes

Append these query strings to a local checkout's running site. Existing `logos` and `mark` links continue to work.

| Query | What to check |
|---|---|
| `?view=gallery` | Register introduction, existing collections, new collections and alias search. |
| `?view=gallery&coverage=1&identity-family=transit` | Operators and service identities together, with distinct evidence states. |
| `?view=gallery&subject=translink` | Corporate artwork, historical research still open, primary sources and organization link. |
| `?view=gallery&subject=translink-t-marker` | Separate T-marker source specimen and supported colourway. |
| `?view=gallery&subject=british-columbia-rapid-transit-company` | Source lead without invented artwork; organization and salary connections remain available. |
| `?view=gallery&subject=liquor-distribution-branch` | The branch identity and distinct retail/wholesale family members. |
| `?view=gallery&subject=bc-ferry-authority` | Historical specimen and valid historical atlas year. |
| `?view=gallery&subject=bc-ferry-authority-2003` | Separate modern authority. |
| `?view=gallery&coverage=1&identity-scope=institution` | The explicitly selected wider institutions. |
| `?view=government&mode=related&node=translink` | Current regional record, gallery link, operating companies and original salary records. |
| `?view=government&node=metro-vancouver-transit-police` | Both separately filed employer links and the distinction from Transit Security. |

The implementation uses the existing site navigation for cross-view links and history entries for gallery page changes. Register filter edits replace the current history entry. Back/Forward must return to the prior subject, collection or filter state.

## Build and validation

```sh
git submodule update --init --recursive
npm ci
npm run check:identity-coverage
npm run build
```

The check command verifies the artwork manifest and generated data, then runs gallery, related-body, government and browser-history regression tests. It also server-renders every subject page in light and dark themes, plus the register and overview, and checks its image URLs against local files under a project deployment base. Component rendering is not a substitute for browser interaction or visual layout review. Coverage tests exercise ownership boundaries, source-only/shared/unconfirmed states, alias handling and legacy-queue preservation. Registry tests resolve every atlas reference at its actual navigation year. Salary tests preserve both index formats and distinct employer-file identities.

Artwork can be regenerated offline with `npm run build:identity-expansion`. The acquisition README documents extraction reproduction and the image-review sheets. These are rendered artwork evidence, not screenshots of the application.

Local Linux builds use the repository's existing TeX Gyre Heros stand-in for unrelated generated Helvetica lockups when licensed Helvetica is unavailable. The newly collected logos retain their own original outlined or raster lettering. Release builds retain the repository's existing licensed-font requirements.

### Manual review checklist

1. Search **GVTA**, **BCRTC**, **Sea-Bus** and **BCLIQUOR**. Open their subjects and check their family relationships.
2. Filter transit to **Without artwork**, open BCRTC, then use the organization and salary links.
3. Open the T-marker file. Confirm the source colourway, dated specimen label, original-source/download links and absence of unsupported recolouring controls.
4. Navigate subject → artwork → subject → organization → salary, then use browser Back/Forward.
5. Compare historical and modern Ferry Authority routes. Verify the historical link selects a real 1970s atlas node while the modern authority opens its current catalogue record.
6. At a narrow viewport, check filter controls, long aliases, status labels, source links and the related-body directory. Repeat key artwork pages in dark mode, including the white Transit Police and Powerex source files.

### Validation recorded for this PR

- `npm run check:identity-coverage`: **131 tests passed**, followed by **538 successful subject-page renders** (269 subjects in each theme), register/overview rendering and local image checks at `/PofBC/`.
- Salary navigation/search/people and existing government salary regressions: **34 tests passed**.
- `python3 scripts/extract-identity-expansion.py --check`: all **14 derivatives reproduced** from their preserved sources.
- `npm run build`: passed, with the repository's local font stand-in and existing large-chunk advisory.
- All 43 added artwork renders inspected; source-file and archive checks verify all 56 retained files.
- `git diff --check`: clean.

Live browser interaction and viewport layout review could not be completed in this execution environment: the local Chromium process could not open its required socket, the browser installer did not retrieve a valid archive, and the separate review browser could not reach the local app server. The component render checks above do not claim to cover those interactions. Use the manual checklist before marking the draft ready for release.

## Research that remains open

BCRTC, SeaBus, RapidBus, B-Line, Metro Vancouver Regional Parks, BC Children's Hospital and LandSure are among the source-located subjects still awaiting accepted artwork. Other historical designs and original master files remain explicit next actions. Accepting a current file does not close those research tasks.

Adding a later acquisition requires a source, a checked local file and manifest record, regeneration, and the same ownership/provenance checks. It does not require changing a legal organization kind or adding a fictitious node to make the subject eligible.
