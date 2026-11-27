# Gallery hierarchy review (2026-11-27)

What in the gallery (`?view=gallery`) should be nested under another collection, and which collections
are former government departments or branches that could move to Departmental Logos
(`?view=internal`). Proposals only: nothing under `src/` was changed. The data is in
[`proposals.json`](proposals.json).

## Method

- Loaded the live data in Node from the working tree on 2026-11-27, including staged changes:
  `GALLERY_COLLECTIONS` and `FOLDED_UNDER` (`src/gallery/collections.js`), `IDENTITY_COVERAGE`
  (`src/gallery/identityCoverage.js`), and the government graph (`HISTORICAL_BODIES`,
  `SUB_AGENCIES` in `src/government/historyData.js`; ministry episodes in `src/ministries/history.js`).
- Basis: 626 collections, 1,252 entries, 863 register subjects; 12 existing fold groups, 41 folded
  children.
- Mapped every register relation to the collections at both ends (206 collection-to-collection
  relations, excluding `listed-by`). Then joined every collection's `graphNode` to its graph record:
  `SUB_AGENCIES.parent` edges and `HISTORICAL_BODIES.became` edges. Then read the intro of every
  candidate.
- Classification:
  - **foldUnder**: one body or brand belongs to another: `part-of`, `service-of` or `operated-by`
    (when the operator is the owner), `owned-by`, or a rename of the same continuing body
    (`renamed-to`, or a graph `became` whose source text says "renamed" or "continued").
  - **crossLinks**: distinct legal bodies that succeeded, merged or split; independent societies;
    sector leads; and sponsors. Separate Crown corporations are never folded under their ministry.
  - **High** confidence requires a register relation or a graph edge that directly states the tie.
    **Medium** means a `related-to` relation plus intro text, or a strong intro with no relation.
    **Low** is a plausible tie that the repo does not record.
- A validation pass checked every id against `GALLERY_COLLECTIONS`. It also checked that no
  proposed parent is folded, no proposed child is already folded or is an existing parent, no pair
  repeats `FOLDED_UNDER`, no child is proposed twice, and no proposed child is also a proposed
  parent. All checks pass. Evidence strings give `file:line` for the relation, graph record or intro
  text they cite.

## Counts

| Category | Total | High | Medium | Low |
|---|---|---|---|---|
| foldUnder | 41 | 24 | 13 | 4 |
| moveToDepartmental | 16 | 5 | 5 | 6 |
| crossLinks | 82 | – | – | – |
| conflicts | 9 | – | – | – |

## High-confidence folds

| Child | Parent | Relation | Evidence (register unless noted) |
|---|---|---|---|
| collected-islands-trust-conservancy | collected-islands-trust | branch | part-of ("Conservation arm of the Islands Trust federation") |
| collected-islands-2050 | collected-islands-trust | program | service-of ("Policy Statement review led by Islands Trust") |
| collected-legislative-library-bc | collected-legislative-assembly | branch | part-of |
| collected-ubc-okanagan-campus | collected-university-of-british-columbia | campus | part-of; shares-identity-with |
| collected-4tvi-stewardship | collected-4vi-group | division | part-of ("Operation within the 4VI social enterprise group") |
| collected-4ever-strategies | collected-4vi-group | division | part-of |
| collected-4good-social-impact-fund | collected-4vi-group | division | part-of |
| collected-vancouver-coast-mountains | tourism-bc-destination-bc | branch | operated-by ("Regional operation managed by Destination BC") |
| collected-lets-ride-bc | collected-bc-snowmobile-federation | program | operated-by ("Tourism program of") |
| collected-bc-farmers-market-trail | collected-bc-association-farmers-markets | program | operated-by ("Campaign operated by") |
| collected-bc-tourism-sustainability-network | collected-bc-regional-tourism-secretariat | program | operated-by |
| collected-concussion-awareness-training-tool | collected-bc-injury-research-and-prevention-unit | program | service-of ("Developed by BCIRPU") |
| collected-capilano-college | collected-capilano-university | predecessor-name | renamed-to |
| collected-emily-carr-institute-of-art-and-design | collected-emily-carr-university | predecessor-name | renamed-to |
| collected-kwantlen-university-college | collected-kwantlen-polytechnic-university | predecessor-name | renamed-to |
| collected-kwantlen-college | collected-kwantlen-polytechnic-university | predecessor-name | renamed-to (via KUC) |
| collected-university-college-of-the-cariboo | collected-thompson-rivers-university | predecessor-name | renamed-to |
| collected-cariboo-college | collected-thompson-rivers-university | predecessor-name | renamed-to (via UCC) |
| collected-university-college-of-the-fraser-valley | collected-university-of-the-fraser-valley | predecessor-name | renamed-to |
| collected-fraser-valley-college | collected-university-of-the-fraser-valley | predecessor-name | renamed-to (via UCFV) |
| collected-industry-training-authority | collected-skilledtradesbc | predecessor-name | renamed-to; graph became; "continued under the name" |
| collected-bc-safety-authority | collected-technical-safety-bc | predecessor-name | predecessor-of ("Earlier operating name"); graph became |
| collected-bc-innovation-council | collected-innovate-bc | predecessor-name | graph became; intro "renamed … Innovate BC in March 2018" |
| collected-bc-place-ltd | collected-bc-enterprise-corporation | predecessor-name | graph became ("statutory rename … 31 March 1987") |

Medium and low folds, each with a note, are in `proposals.json`:

- Science Council under Innovate BC.
- Kootenay School of the Arts under Selkirk.
- Tourism Vancouver Island under 4VI Group.
- SIFERP under FORREX.
- Three BCIRPU programs: Active & Safe Central, Cost of Injury and Prevent Shaken Baby Syndrome.
- Camping & RV in BC under BCLCA.
- RTVS under RCCbc.
- Fish & Wildlife Compensation Program under BC Hydro.
- West Vancouver Blue Bus under West Vancouver.
- BC Ambulance Service under the EHS Commission.
- Super, Natural BC and the Visitor Centre network under Destination BC.
- Chances under BCLC.
- BC Ale Trail under the Craft Brewers Guild.
- SuperHost under Tourism, Recreation and Culture.

## Departmental Logos candidates

`specimens-travel-industry` already has `shelf: 'departmental'`. `recreation-conservation` has it
through your staged, uncommitted change, which was briefly stashed during this review. Neither is
proposed again.

| Collection | Department / branch | Years | Confidence |
|---|---|---|---|
| bc-lands | BC Lands (Lands Operations Division), Crown lands ministry | 1986–88, 1994 | high |
| bc-environment | Ministry of Environment | 1988–1991 | high |
| tourism-recreation-culture | Ministry of Tourism, Recreation and Culture | 1986–1988 | high |
| collected-bc-public-health-service | Public Health Service, Department of Health Services and Hospital Insurance | c. 1961 | high |
| collected-shared-services-bc | Solutions BC / Shared Services BC, Ministry of Management Services | 2003–c. 2015 | high |
| specimens-provincial-emergency-program | Provincial Emergency Program | 1993–2003 | medium |
| superhost | Ministry of Tourism program | 1985–86 | medium |
| health-program-signatures | Ministry of Health Services (BCHealthCare, BCPharmaCare) | 2003–2005 | medium |
| specimens-ecosystems-at-risk | Conservation Data Centre, Ministry of Environment | 1993–2006 | medium |
| collected-sub-british-columbia-geological-survey | Geological Survey Branch (current) | 1895– | medium |
| specimens-environment-youth-corps, bc-parks, bcts, collected-sub-bc-online, collected-liquor-control-board, collected-alcohol-and-drug-commission | current branches/programs, or a board or commission | – | low |

## Open questions

1. **Departmental scope.** Is the view only for pre-1976 departments and defunct branches? Or does
   it also take post-1976 ministries (BC Environment, Tourism, Recreation and Culture) and current
   branches (BC Parks, BCTS, Geological Survey, LDB)? The high list assumes defunct ministries count.
   The low list is current units with public brands, which I would leave in the gallery.
2. **Predecessor names: fold or merge?** The repo sometimes merges a renamed body into one collection
   with eras (Tourism BC & Destination BC) and sometimes keeps separate collections. The 15
   predecessor-name folds (12 high, 3 medium) could instead become eras plus `aliases`.
3. **Mergers kept as crossLinks.** Following the brief, the 17 regional health boards and societies
   (1994–2001) and the 5 former school districts (1996) are crossLinks to their successors. Folding
   them as predecessors would tidy the first page, but each is a distinct, dissolved body.
4. **BC Ambulance Service.** The register's parent, BCEHS, is folded under PHSA. Choose the EHS
   Commission (proposed) or PHSA beside BCEHS.
5. **Ties the register does not record.** Super, Natural BC, the Visitor Centre network, Chances and
   SIFERP have none. Add the register relation before applying these folds, so the "ties are the
   register's" rule above `FOLDED_UNDER` still holds.
6. **Direction choices.**
   - BC Place Ltd. under BCEC follows the legal rename, though BC Place Ltd. is the better-known name.
   - Tourism Vancouver Island under 4VI Group: the register does not say whether the group or 4TVI
     Stewardship continues the society.
7. **SuperHost** is both a low fold (under Tourism, Recreation and Culture) and a medium departmental
   candidate. The fold matters only if both move.
8. **SIFERP** was split out of FORREX recently (`movedGalleryPlaces.js` redirect). Folding it back as
   a child keeps it separate but nested. Confirm that this is wanted.

## Not verified

- Nothing outside the repo was checked: no web sources and no artwork.
- Airports, municipalities and most tourism collections have no register relations to other
  collections apart from those listed. I did not infer ownership (for example, municipally owned
  airports) without one.
- `collected-bc-steamship-company` (a possible BC Ferries tie) has no relation or graph edge, so it is
  not proposed.
- The working tree was changing during the review: `collections.js`, `movedGalleryPlaces.js` and
  `InternalLogosView.jsx` were stashed, restored and staged, and `galleryModes.js` is new. All
  checks were re-run against the final state. Re-check the ids against the tree when applying.
