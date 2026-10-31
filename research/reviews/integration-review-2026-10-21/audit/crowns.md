# Crown integration audit

**Reviewed commit:** `0dbdb18cfebfb27e5529ce5940850e96eb9a995c` on `claude/vibrant-cori-gy5e6w`.

**Result:** The central historical date corrections are mostly supported. Four integration corrections remain: preserve the meaning of MTOC’s transfer boundary, attach primary sources to corrected lifespan facts, retain the inferred basis of LDB’s 1986 cap, and handle Harbours’ first-seen date in search. Two further wording/model qualifications are recorded below.

This was a read-only review of the checkout, retained originals, and focused runtime outputs. No repository files were changed. No full test suite was rerun by this reviewer. The checkout was clean at completion.

## Supported decisions to keep

| Subject | Assessment | Claims |
|---|---|---|
| MTOC | Keep 18 January 1980 statutory commencement and 1 June 1985 transfer events; legal dissolution remains unproved. | R4E-C013, R4E-C019, R4E-C020, R4E-C021 |
| Hydro | Keep 30 March 1962 original scheme commencement, 23 March 1964 reconstitution, and 20 August 1965 amalgamation; distinguish their date kinds and identities. | R4E-C030, R4E-C035, R4E-C039 |
| BC Electric and Power Commission | Keep 20 August 1965 separate-corporate-existence ends. Retain BC Electric formal dissolution on 23 August as a different event. | R4E-C039, R4E-C040 |
| Harbours Board | Keep established=null, firstSeen=23 September 1983 and legal dissolution=30 May 1985. Do not describe 1983 as its foundation. Earlier legal start remains a separate research task. | R4E-C046 |
| LDB | Keep the 31 December 1976 statutory-branch event distinct from 1973 administrative lineage; keep the explicit 1976 responsible-minister assignment, with its period inference exposed. | R4E-C023, R4E-C026 |

## CROWN-AUDIT-01: MTOC operational withdrawal is displayed as closure of the body

**Severity: medium. Confidence: high.**

**Locations**

- `research/reviews/round-4-2026-10-21/integration/crowns.json` lines 979-1004.
- `research/history/bodies.json` lines 826-845.
- `src/government/snapshot.js` lines 312-316, 417-433.
- `src/government/compare.js` lines 86-91.
- `src/government/AtlasCards.jsx` lines 217-219.

**Observed behavior.** The integration deliberately stores the 1 June 1985 transfer in ended, while correctly saying in endedMeaning that legal dissolution is unknown. The snapshot filters existence using ended and drops endedMeaning from node fields; the year comparison calls every disappearance a closure. MTOC is consequently in Bodies that closed when comparing 1984 and 1985.

**Source assessment.** R4E-C019 and C020 prove the asset, obligation and employee transfer. R4E-C021 records a new MTOC board appointed effective 1 June 1985, affirmative evidence against legal dissolution that day. R4E-C022 is only a later statutory-edition observation, not proof of operating continuity.

**Correction.** Preserve the transfer as an operational/display boundary and retain an explicit unknown legal end. Carry an end kind or separate operationsEnded/legalEnded/visibleUntil fields through the snapshot and comparison, labeling the change operations transferred rather than body dissolved/closed. Do not replace this with an unqualified null that depicts continuing operation through 2026. Ensure the legal entity remains discoverable in the record even if not drawn after transfer.

**Verification**

```json
{
  "governmentIn_1984_contains_mtoc": true,
  "governmentIn_1985_contains_mtoc": false,
  "compareYears_1984_1985_bodies_closed_includes": "metro-transit-operating-company",
  "comparison_node_endedMeaning": "undefined"
}
```

**Claim references:** R4E-C013, R4E-C019, R4E-C020, R4E-C021, R4E-C022.

**Original sources:** [R4E-006: Metro Transit Operating Company Act, SBC 1979, c 18](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/1632786748); [R4E-007: Order in Council 29/1980](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0029_1980); [R4E-012: British Columbia Transit Amendment Act (No. 2), SBC 1985, c 35](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/123385008); [R4E-013: Order in Council 1093/1985](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1093_1985); [R4E-014: Order in Council 1094/1985](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1094_1985); [R4E-015: Order in Council 1095/1985](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1095_1985); [R4E-016: Order in Council 1096/1985](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1096_1985); [R4E-017: Auditor General 1986 report, Part 2 appendices, reproducing 1984/85 Public Accounts](https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19860401a-1986reportpart2appendices.pdf); [R4E-019: Metro Transit Operating Company Act, 1991 consolidation](https://www.bclaws.gov.bc.ca/civix/document/id/91consol15/91consol15/79257).

## CROWN-AUDIT-02: Changed lifespan facts inherit an old general source instead of the new field-level evidence

**Severity: medium. Confidence: high.**

**Locations**

- `research/reviews/round-4-2026-10-21/integration/crowns.json` lines 1007-1030.
- `research/history/bodies.json` lines 395-420, 826-845.
- `scripts/build-government-history.mjs` lines 181-202.
- `src/government/snapshot.js` lines 378-386.

**Observed behavior.** Hydro is displayed from 1962-03-30 but that lifespan claim links to the BC Archives authority record which the same record explicitly says gives 1962-03-31. MTOC new exact dates similarly retain the old Archives source. Primary orders appear as event evidence or textual mentions rather than the source of the changed lifespan fact.

**Source assessment.** R4E-C030 uses the 1962 Act and OIC 839 for 30 March. The integration records the conflicting Archives date separately, so its own evidence proves that the current lifespan source cannot substantiate the exact new start.

**Correction.** Preserve provenance for established, ended and firstSeen individually, including source IDs/URLs, locators, date kind and qualification. Build separate sourced assertions for original commencement, reconstitution, amalgamation and operational transfer. Keep the Archives record as background/conflicting evidence; do not use it as the sole link on a primary-source-corrected date.

**Verification**

```json
{
  "body": "bc-hydro",
  "year": 1962,
  "claim": "British Columbia Hydro and Power Authority, from 1962-03-30",
  "linked_source": "https://search-bcarchives.royalbcmuseum.bc.ca/british-columbia-hydro-and-power-authority-2",
  "note_acknowledges_conflicting_date": "BC Archives gives 31 March 1962"
}
```

**Claim references:** R4E-C013, R4E-C019, R4E-C020, R4E-C030, R4E-C035, R4E-C039.

**Original sources:** [R4E-006: Metro Transit Operating Company Act, SBC 1979, c 18](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/1632786748); [R4E-007: Order in Council 29/1980](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0029_1980); [R4E-012: British Columbia Transit Amendment Act (No. 2), SBC 1985, c 35](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/123385008); [R4E-013: Order in Council 1093/1985](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1093_1985); [R4E-030: British Columbia Hydro and Power Authority Act, SBC 1962, c 8](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/744546168); [R4E-031: Order in Council 839/1962](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0839_1962); [R4E-035: British Columbia Hydro and Power Authority Act, SBC 1964, c 7](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/511440219); [R4E-036: Order in Council 773/1964](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0773_1964); [R4E-037: Order in Council 2519/1964](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/2519_1964); [R4E-039: Order in Council 2386/1965](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/2386_1965); [R4E-040: Power Measures Act, SBC 1966, c 38](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/815001869).

## CROWN-AUDIT-03: LDB inferred 1986 endpoint is presented as part of a source-stated ministry period

**Severity: medium. Confidence: high.**

**Locations**

- `research/reviews/round-4-2026-10-21/integration/crowns.json` lines 1070-1096.
- `research/history/bodies.json` lines 164-182.
- `scripts/build-government-history.mjs` lines 198, 223-225.
- `src/government/snapshot.js` lines 327-330, 354-367, 386.

**Observed behavior.** The source JSON explains that the responsible period is capped at 1986 because the ministry episode ends then. The build only retains ministry/from/to/source/locator, discarding that note; the snapshot also omits the retained locator. The 1985 panel therefore says Answered to the Ministry of Consumer and Corporate Affairs from 1976-12-31 to 1986 with only the 1976 appointment order as source.

**Source assessment.** R4E-C026 dates the administration assignment order to 2 December 1976, before statutory commencement on 31 December. OIC 3495/1976 contains no 1986 end or proof that no intervening transfer occurred. The cap is a modeling inference from ministry lifespan, not an established legal reassignment date.

**Correction.** Carry the qualification and both endpoint bases into generated responsible periods and evidence. Cite the ministry-episode source for the cap; label continuation/capping as inferred. Preserve an unknown later responsible ministry until a source establishes the transfer. Keep order approval and operative commencement distinct.

**Verification**

```json
{
  "body": "liquor-distribution-branch",
  "year": 1985,
  "claim": "Answered to the Ministry of Consumer and Corporate Affairs from 1976-12-31 to 1986",
  "source": "https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/3495_1976",
  "rendered_evidence_has_note": false
}
```

**Claim references:** R4E-C023, R4E-C026.

**Original sources:** [R4E-020: Liquor Distribution Act, SBC 1975, c 39](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/706478044); [R4E-025: Order in Council 3494/1976](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/3494_1976); [R4E-026: Order in Council 3495/1976](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/3495_1976).

## CROWN-AUDIT-04: The new Harbours first-seen record generates a null start label in search

**Severity: medium. Confidence: high.**

**Locations**

- `research/reviews/round-4-2026-10-21/integration/crowns.json` lines 1117-1144.
- `research/history/bodies-round4.json` lines 5-14.
- `src/government/GovernmentView.jsx` lines 99-105.

**Observed behavior.** Harbours correctly has established=null and firstSeen=1983-09-23. The search index derives its year and date label solely from established, yielding NaN and null–1985. This is a new valid data shape exposing an incomplete consumer.

**Source assessment.** The 1983 source is an observation of an existing board in the repeal Act, not its creating instrument. Moving 1983 into established would repair the label by corrupting the historical assertion.

**Correction.** Use established or firstSeen[0] for navigation, and explicitly label a first-seen lower bound as known by 1983 / start unknown. Keep established null. Check other lifespan consumers for the same assumption, without changing the correct firstSeen semantics.

**Verification**

```json
{
  "search_year": "NaN",
  "search_detail": "null–1985",
  "established": null,
  "firstSeen": "1983-09-23"
}
```

**Claim references:** R4E-C046.

**Original sources:** [R4E-047: Harbour Board Repeal Act, SBC 1983, c 5](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/881646216); [R4E-048: Order in Council 1061/1985](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1061_1985); [R4E-017: Auditor General 1986 report, Part 2 appendices, reproducing 1984/85 Public Accounts](https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19860401a-1986reportpart2appendices.pdf).

## Identity and relationship qualifications

### CROWN-AUDIT-N01: Keep the Hydro operating lineage distinct from the 1964 corporation

The 30 March 1962 original commencement is well supported, and the 20 August 1965 ends of BC Electric and the Power Commission are well supported by the agreement ratified in the 1966 Act. It is reasonable to keep one public-facing Hydro lineage if the dates are typed. A continuous lineage from 1962 is not a finding that the modern legal corporation was constituted in 1962. R4E-C035 identifies its new 1964 constitution, effective 23 March 1964. The event for the 1963 judgment already correctly preserves contemporary annual-report attribution and the fact that the judgment and any appellate outcome were not recovered.

**Recommended wording:** BC Hydro’s operating lineage begins under the 1962 scheme on 30 March 1962. Following the judicial invalidity reported in Hydro’s contemporary annual report, a new corporation was constituted under the 1964 Act on 23 March 1964. BC Electric and the Power Commission ceased separate corporate existence under the amalgamation effective 20 August 1965.

**Limits:** Do not summarize the whole display as the settled legal identity from 1962, or imply the full 1963 judgment was inspected. Do not undo the 1965 ends merely because the full judgment is unavailable: the later ratified agreement directly establishes those ends.


**Claim references:** R4E-C030, R4E-C032, R4E-C035, R4E-C039, R4E-C040, R4E-C041.

**Original sources:** [R4E-030: British Columbia Hydro and Power Authority Act, SBC 1962, c 8](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/744546168); [R4E-031: Order in Council 839/1962](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0839_1962); [R4E-033: British Columbia Hydro and Power Authority second annual report, year ended 31 March 1964](https://digital.library.mcgill.ca/images/hrcorpreports/pdfs/6/632603.pdf); [R4E-035: British Columbia Hydro and Power Authority Act, SBC 1964, c 7](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/511440219); [R4E-036: Order in Council 773/1964](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0773_1964); [R4E-037: Order in Council 2519/1964](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/2519_1964); [R4E-039: Order in Council 2386/1965](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/2386_1965); [R4E-040: Power Measures Act, SBC 1966, c 38](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/815001869); [R4E-041: Order in Council 2387/1965](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/2387_1965).

### CROWN-AUDIT-N02: Harbours transfer provisions should retain their conditions and relationship type

Dissolution on 30 May 1985 is secure. The 1983 Act authorizes specified asset/liability transfers to BC Development Corporation and BC Railway on separately fixed transfer dates. R4E-C046 expressly leaves those orders/dates unresolved. The body text converts this into a completed division of assets, and serviceSuccessorIds makes the relation a service lineage. The cited Public Accounts independently proves a railway-asset exchange in fiscal 1983/84, but that does not supply every executed transfer or convert all asset transfers into service succession.

**Correction:** State that the Act provided for the transfers; record separately the railway-asset exchange reported for the year ended 31 March 1984. Use asset-transfer relationships until service succession is independently established. Recover the actual transfer orders for complete dated edges.

- The Harbours Board had no assets, liabilities or operations during fiscal 1984/85. Source R4E-017, Public Accounts 1984/85, list of transportation companies and commercial enterprises recorded on equity basis, footnote 3; raw text lines 4635-4665.
- During the year ended 31 March 1984 the Province acquired 111,156 Railway shares in exchange for the Harbours Board net railway assets. Source R4E-017, Public Accounts 1984/85, railway note, raw text lines 891-906.

**Model consequence:** Harbours is retained through legal dissolution despite the documented empty period; MTOC is removed at its emptying. An explicit common legal/operational convention is needed.

**Claim references:** R4E-C046.

**Original sources:** [R4E-047: Harbour Board Repeal Act, SBC 1983, c 5](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/881646216); [R4E-048: Order in Council 1061/1985](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1061_1985); [R4E-017: Auditor General 1986 report, Part 2 appendices, reproducing 1984/85 Public Accounts](https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19860401a-1986reportpart2appendices.pdf).

## What this audit does not settle

- MTOC’s eventual legal end.
- The complete 1963 Hydro judgment or any appellate disposition. The annual-report attribution remains the source for that judgment claim.
- LDB’s later administrative transfers and the exact 1986 change.
- Harbours Board’s original creation/commencement or all executed asset-transfer orders.

These are evidence gaps. They do not justify undoing directly supported commencement, transfer or dissolution dates. The immediate implementation work is to prevent an operational or inferred boundary from becoming an unqualified legal fact when it reaches the diagram.

## Evidence record

`crowns.json` contains the structured findings, exact reviewed commit, reproducible output values, original Round 4 claim objects, and source URLs/checksums/local evidence paths. Source originals remain in `round4/crowns/`; their existing source identifiers are preserved.
