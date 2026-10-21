# Prior branch batch: semantic preservation review

**Head reviewed:** `0dbdb18cfebfb27e5529ce5940850e96eb9a995c`.  
**Original input:** `research/reviews/round-4-2026-10-21/branches/prior/handback-importable.json`.  
**Date:** 21 October 2026. **No repository changes.**

## Recommendation

Describe this as **a mechanically valid, substantial batch of dated observations and three additional start claims, ready for a metadata-preserving import subject to the entity-type and rendering qualifications below**. Do not describe the unmodified batch as byte-idempotent, all historical parent relationships as settled, or 144 complete histories as ready.

I prepared `prior-branch-preserving-batch.json` outside the repository. It retains all **144 records, 118 source objects and historical fields**. Only the incoming review metadata for 35 already-held records is adjusted. `prior-branch-preserving-preparation.json` records its provenance, hashes, exact adjustment list, verification and semantic gates. The original handback remains unchanged and retains all its incoming reviewer/scope metadata.

## What is mechanically and semantically sound

The input has five establishment claims. Two agree with already-applied decisions—Environmental Appeal Board on 1 January 1982 and Powertech's incorporation on 29 September 1988. The other three add starts:

| Record | Date and precision | What the retained primary source actually supports |
|---|---|---|
| Connected Services BC | 1 October 2025; day | The official “Who we are” page expressly dates the beginning of the organization to that day. It describes bringing together IM branches, IT teams, OCIO and Service BC. This is an organizational beginning. |
| Compliance and Enforcement Collaborative | 2012; year | The official terms of reference describe an inter-agency working group and community of practice, established in 2012. It is distinct from its permanent supporting C&E Secretariat. |
| B.C. Drought Information Portal | 2015; year | The official climate-and-health report states the portal was created in 2015; its timeline says spring 2015. A year preserves the available precision without inventing a month. |

I re-read the retained source passages: `round4/prior/evidence/round3/branches/raw/extras/R3F-EXT-015.txt:97–98`, `R3F-EXT-023.txt:40–41,90–91`, and `R3F-EXT-049.txt:521–527,788–792`. Public source URLs and locators remain in the batch and preparation manifest.

All **47 incoming parent rows** are `observation_only`: 41 `part_of`, six `subsidiary_of`. The batch does not turn them into continuous historical parent intervals. The 12 name rows comprise ten observations and Powertech's two registry-backed name periods. There are no new end claims, succession relations or competing date-claim entries. The two old `identity_review_required` records in the current dataset are outside this batch. None of these 144 records supplies a top-level `identity_review_required`, `import_status` or `atlas_import` flag that the merge silently drops.

The identity-qualified checks for Buy BC, the education-savings special account, DFA, Comptroller General Operations, Provincial Treasury and several budget labels remain checks with `related_label_identity_unresolved`; they are **not** promoted into first observations by this batch. The Safe Campuses BC sighting rejected during Round 4 is not reintroduced as a founding or first-sighting claim.

## Gates and qualifications

### 1. Preserve current unresolved questions before merging

The unmodified merger replaces `review.unresolved_fields` at `scripts/merge-research.mjs:151`. An in-memory merge changes that field on **35 existing records**, including material losses:

- Powertech loses `operational_start` and `relations`.
- Crown Agencies Secretariat, Internal Audit and Advisory Services, Office of the Comptroller General and Treasury Board Staff each lose `identity_continuity`, `pre_2002_history` and `relations`.
- Buy BC loses the specific contemporary-1993, 2002–2018 administration and pre-2023 parent questions.
- BC Parks loses the specific 1957 instrument and later-parent questions; COS loses its 1980 separation-instrument question.
- DFA, the education-savings program, Provincial Treasury and the Arts and Culture Endowment lose more specific Round 4 questions in favour of generic older lists.

Some incoming lists also add `established` back to records with accepted starts. This is research-status regression, even when current rendering does not consume that field. There was **no existing evidence-status change or established-date reversal** in the tested first merge; the specific question loss is the important issue.

The derived batch omits incoming `review.scope`, `review.by` and `review.unresolved_fields` for the 35 held records. It explicitly carries each held `full_history_complete` Boolean because the merger assigns that even when absent. `review.checked` and `sources_checked` remain, and new records retain the original review metadata. Existing notes and all historical facts remain intact.

### 2. Decide the C&E Collaborative's type separately from its supporting office

The date 2012 is supported for the **Collaborative**. The same official source distinguishes the working group from the **C&E Secretariat**, a permanent business unit supporting it, and identifies the Secretariat's contemporary host. The queue presently supplies `kind:"office"` and a ministry placement for the Collaborative (`research/queue/sub-agencies.json`, record `compliance-and-enforcement-collaborative`). Merge uses queue metadata for a new researched record (`merge-research.mjs:105–115`); the batch supplies no type correction.

Keep 2012 as the working group's start. Do not make it the Secretariat's founding date or use the Secretariat's hosting arrangement as proof that all member bodies answer to that ministry. A working-group/coordination type, with a separate supporting-office relationship, needs an editorial/model decision. This does not invalidate the date fact; it limits how the new node should be described and connected.

For Connected Services BC, the source also describes a 2025 restructuring of OCIO, Service BC and other teams. Adding the CSBC start alone does not apply those child-parent changes. It does not establish their dissolution either. For the Drought Information Portal, preserve the portal/program identity and avoid labelling 2015 a corporate or statutory incorporation.

### 3. The six subsidiary observations encounter the existing ownership-path defect

These records supply correctly typed ownership observations:

- `bchpa-captive-insurance`
- `tongass-power-and-light`
- `bc-lottotech-international`
- `fii-consulting-shanghai`
- `forestry-innovation-consulting-vietnam`
- `bcr-properties`

Current graph construction turns every resolved sub-agency parent into `part` (`src/government/snapshot.js:570–572`), and accountability traversal accepts `part` (`594,609`). This is the existing model-audit finding M2. Accepting ownership observations into research does not justify a political-accountability route. Preserve ownership as a separate edge and prevent that traversal. Alias resolution may also affect whether a particular parent observation matches a drawn body; a clean data merge is not proof every new relationship will render correctly.

### 4. Sightings do not complete continuous presence or parent histories

The snapshot correctly restricts a parent observation to its source year (`snapshot.js:477–478,499`). In other years it can still use today's parent or a ministry forerunner, explicitly marked inferred (`510–513`). It must not report those fallback placements as new documented periods.

For presence, `snapshot.js:493–495` draws an undated current entity in every year after its first observation. That is the existing display policy, not evidence supplied by this batch for each intermediate year. The distinction especially matters where current `identity_continuity` questions remain. Retain the “first seen” wording and uncertainty; do not describe the metric improvement as proof of full lifecycles or completion of F2.

The root's generated 251-entity simulation reports **48 established / 65 first-seen-only / 138 undated → 51 / 176 / 24**. These are display/data-coverage categories, not 114 newly discovered incorporations. Queue-only statistics have a different denominator and should not be interchanged with these figures.

### 5. Replay must preserve research bytes, not only runtime output

The original merger combines scope and reviewer as whole strings (`merge-research.mjs:152–153`). Once the held string is composite, it no longer equals the incoming component, so a second replay appends the same component again. I reproduced changes to **35 scope fields and 34 reviewer fields**, despite an empty second merge log. The root's isolated build separately observed changes in `sub-agencies-researched.json` and `history-import.json`, with runtime government output stable.

The derived batch removes the repeated older metadata components for held records. First and second **in-memory** merges now produce byte-identical serialized research and source-catalogue data, with no second merge log entries. This sub-review does not substitute for the root's fresh isolated build and test run of the derived file.

## Checks performed and limits

I inspected all incoming field shapes, all parent/name coverage classifications, the five establishment claims, identity-qualified checks, overlaps with current research decisions and current merge/compiler/snapshot behavior. I compared existing records before and after in-memory merges, verified preservation of questions/status/dates and checked replay bytes. The new-start source passages were re-read in retained primary evidence.

I did **not** re-audit every original sighting or all 134 bodies covered by the wider prior research. I did not alter the repository, publish changes, infer missing execution dates, or add undisclosed type corrections to the derived batch. The derived file is a safe additive input at the research layer; the C&E entity-type decision, ownership traversal and continuous-presence qualifications remain explicit.
