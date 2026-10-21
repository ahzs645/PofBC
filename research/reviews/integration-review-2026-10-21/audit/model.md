# PofBC round 5: lifetime, local-body and People-path model audit

**Reviewed head:** `0dbdb18cfebfb27e5529ce5940850e96eb9a995c` (`claude/vibrant-cori-gy5e6w`).  
**Comparison baseline:** `0f1587c5e982135f155ba6660af5192509351511`.  
**Review date:** 21 October 2026.  
**Scope:** read-only review of the model, current consumers and retained original district evidence. No repository files were changed. No AGENTS.md was found in the checkout or its ancestors.

## Decision

Import the seven rural boards as historical identities with proved designation dates and explicitly untraced ends. Do not assign a fictitious dissolution, a guessed 1997 end, or an unqualified open-ended lifetime. A record should remain searchable even when the selected year's diagram cannot assert that it existed. Show evidence points and genuinely supported intervals; distinguish a missing end from evidence that the body ended on an unknown day.

Create the local-body register, but make it a reusable entity register with optional local/regional display and searchable evidence panels. The absence of a provincial ministerial responsibility chain is not a reason to suppress a local corporation's history. It is a reason to use the correct kinds of relationships and the correct electorate. Keep the current good separation between legal identity, service succession, asset transfer and ministerial responsibility.

The People node is already central in the current Government view. The remaining work is primarily the meaning and evidence of the lines leading to it. I reproduced a current case where an ownership relation becomes a political-accountability path: Powertech's `subsidiary_of` relation is converted into `part`, and therefore treated as an accountability route through BC Hydro.

## Findings

| ID | Priority | Finding | Origin |
|---|---|---|---|
| M1 | P1 | An untraced end cannot be imported without implying indefinite existence. A fix must cover search, navigation, timeline and panel as well as the snapshot predicate. | Existing model limitation; correctly identified by integration |
| M2 | P1 | Ownership evidence for Powertech is emitted as a `part` edge and produces a path to the people. | Inherited behavior, exposed by the audited data |
| M3 | P2 | The proposed local-register description overstates hospital improvement districts as bodies that never run hospitals and uniformly have elected trustees. | New proposal wording |
| M4 | P1 | A register deliberately unread by the diagram is a sound first storage step, but does not complete local-body discovery, lineage or the user's requested structural view. | New proposal scope; existing consumer limitations |
| M5 | P2 | Restricting ministers to the role of recommending minister would discard documented approval and inspection relationships. | New proposal rule |
| M6 | P2 | Date precision and event meaning remain collapsed: year-only ends become 1 January, and sub-agency ends are automatically typed as dissolution. | Inherited behavior |
| M7 | P2 | Related event subjects are discarded by the event builder, so the new Greater Vancouver transfer is not indexed to its recipient health bodies. | Existing builder limitation affecting new evidence |
| M8 | P1 | One `ended` field cannot consistently represent operating cessation, legal dissolution and name succession. The new `endedMeaning` text is useful but does not change the model. | Existing model limitation highlighted by new decisions |

### M1 — Unknown end means neither current nor proved extinct

`src/government/snapshot.js:312–315` treats any missing end as indefinite. The historical-body loop at `417–435` calls that predicate, so adding a known start and `ended:null` for the seven boards would indeed draw them in 2026. Holding them out prevented that particular error.

However, the integration note says the schema needs “ended, day unknown.” The research supports the narrower statement **end untraced**: neither the corporate ending nor the link to the 1997 society has been established. `research/reviews/round-4-2026-10-21/integration/health.json:2459–2460` expressly says not to use the 1999 repeal as their end and not to link them to the societies as `becameId`. An `ended_before` value would require its own positive evidence. Missing instruments are not evidence for a terminal date.

Adding only an end-status field or changing `stands()` is insufficient:

- `scripts/build-government-history.mjs:177–204` drops fields outside its existing projection.
- `src/government/GovernmentView.jsx:99–105` searches only historical bodies with a truthy `ended` value.
- `GovernmentView.jsx:275–281` sends the “last” navigation target to 2026 when `ended` is absent.
- `src/government/snapshot.js:634–648` returns only one start and one end to the timeline, omitting the first-seen fallback used by snapshots.
- `src/government/TimelineBar.jsx:50–51,72–73` labels endpoints “began/ended” and fills a missing end through the present.
- `src/government/GovernmentPanel.jsx:424–427` labels a missing end “Since [start]”.

These must share one lifetime/presence resolver. A search result can say “Designated 14 October 1994; later legal status untraced” without claiming existence in the current snapshot.

### M2 — Preserve ownership as ownership

The source record for Powertech has `parents[].relation:"subsidiary_of"`, including an observation on 30 September 2026 (`research/history/sub-agencies-researched.json:2150–2195`). It explicitly leaves BC Hydro's original acquisition date open (`2201`). The panel evidence recognizes the subsidiary wording (`snapshot.js:541–543`), but graph construction unconditionally calls `link(parent.id,node.id,'part')` at `570–572`. `pathToPeople` accepts `part` at `594,609`.

A direct, read-only invocation of `governmentIn(2026)` and `pathToPeople(...,'sub-powertech-labs')` returned this main route:

1. Powertech → BC Hydro, `part`, **not inferred**;
2. BC Hydro → Ministry of Energy and Climate Solutions, `responsible`;
3. Ministry → Premier, `appoints`;
4. Premier → Assembly, `confidence`;
5. Assembly → People, `elects`.

The first relationship's evidence proves a subsidiary relationship, not the separate “answers for” relationship the user's G1 rule requires. Preserve it as `subsidiary_of`/`owned_by` and exclude it from accountability traversal. Keep a separate, sourced accountability relation if one is found. Do not repurpose the existing `appoints` edge for ordinary board-appointment data: it is currently traversable too.

The existing BC Rail/WCB adapter is a useful pattern: `scripts/build-government-history.mjs:234–255` turns only `minister_responsible_for` into ministry responsibility and retains appointment, funding and report-tabling facts as separate typed relations. Apply that discipline across entity kinds.

### M3 and M5 — Correct the local-register rule without inventing provincial parenting

`integration/root.json:615` says “Neither runs a hospital” about regional hospital districts and hospital improvement districts. That categorical statement is too strong: governance provisions already in the retained primary evidence assign hospital-management roles to district trustees:

- **Fort Nelson HID:** [OIC 1373/1958](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1373_1958), PDF page 5, clauses 5–7. Clause 6 appoints the first trustees; clause 5 provides later elections. Clause 7 makes the trustees, with a Hospital Act section 5 appointee, the hospital board of management. Retained source `R4R-154`.
- **100 Mile House HID:** [OIC 2195/1960](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/2195_1960), approved **27 September 1960**, added clause 5A. It also makes the district trustees and the Hospital Act appointee the hospital board of management. Retained source `R4R-165`, claim `R4RC-193`.

The conclusion is not that every HID operated a hospital. It is that powers and management relationships must be recorded body by body. The original `hospital_improvement_districts.json` correctly says that financial-assistance objects alone do not establish hospital operation. Use that narrower language. The first appointed board and later elected board must also be distinguished.

`integration/root.json:625` goes too far in the other direction by saying ministers appear only as recommending ministers. The same proposal's held evidence at `514–519` identifies board constitution, capital-bylaw, audit and inspection provisions. `R4RC-104` identifies Hospital District Act sections 8, 17, 32 and 45 as a **2026 current-law checkpoint only**; `R4RC-072` supplies dated 1995 restrictions to minister-approved powers. Keep these as `approves_capital_bylaws`, `may_inspect`, `appoints_board_member`, or another precise type. They do not, by themselves, establish ministry responsibility. Do not backdate the current consolidation to 1967.

### M4 and M7 — Local identities should be usable without being provincial branches

The proposal's separate types and stable handback IDs are good. Its example preserves the 1967 Greater Vancouver corporation, its 1999 dissolution and multiple asset recipients. Its separation of old and new same-named Cariboo and other districts prevents false continuation. Keep these decisions.

But `integration/root.json:609` proposes a register “read by no diagram build.” This can be an initial storage milestone, not the completed local-history feature. Read the register into a shared identity lookup used by search, panel, events and lineage, and add a selectable local/regional layer. The main provincial layer need not be crowded with every local body.

Retain actual subject identities in events, even when their nodes are hidden. Currently the hospital-district events are filed under the health ministry because no local ID is registered. In `research/atlas/events-round4.json:2611` onward, `atlas:round4-gvrhd-dissolved-1999` also carries South Fraser and Vancouver/Richmond as related subjects. `scripts/build-government-events.mjs:115–138` discards `related_subject_ids`. Consequently the graph can neither resolve the local transferor nor index the event to its named recipient bodies through that field.

Minimal fix: preserve `subject`, `relatedSubjects`, and role when available. A ministry may be the recommending or administering authority; it should not substitute for the corporation that was incorporated, dissolved or transferred property. A multi-body order may remain one event, indexed to every affected identity with explicit roles.

### M6 and M8 — A date, its precision and what happened are separate facts

`startOf()` converts an end of `"1997"` to `"1997-01-01"` (`snapshot.js:41–49`). That is a documented rendering convention for the year-end view, not evidence that a transaction happened on 1 January. Preserve it only as a compatibility rule, never as a legal date or exact-day event.

The integration reconciles **42 newly dated folded councils plus the already dated Prince George council = 43** (`integration/health.json:2631`). Filtering all rows with end `1997` gives 45 because Simon Fraser and Burnaby boards are also present; that is not a missing or duplicate council count. The 43 amalgamation execution days remain open (`2499–2500`). Their existing descriptions say rescission was conditional on amalgamation. A conditional order is not the execution certificate. Preserve any supported year-level operational transition as year precision, while the legal execution date stays untraced.

`endedMeaning` is a good presentation improvement (`snapshot.js:101–108`; `build-government-history.mjs:186–188`). It is still free text alongside the same single end used by all consumers. The model now treats MTOC's operational transfer as an end while the health societies remain drawn until legal registry dissolution: `src/government/lineage.test.js:126–130` explicitly requires a society to remain present in 2001 after its services passed on, until 15 February 2002. Neither fact should be lost; the selected view should state whether it depicts active delivery or legal existence.

Additionally, `scripts/build-government-events.mjs:188` assigns event type `dissolved` to every sub-agency `ended` claim, even where the end means renamed, replaced, or cessation of a function. Preserve a structured event kind rather than infer dissolution from the presence of an end field.

## Minimal additive model

Do not require a complete schema rewrite. Retain current IDs, names, source indices and legacy dates for compatibility. Add a structured lifecycle block to the research record and generated data, and use one resolver in every consumer:

```json
{
  "lifecycle": {
    "legalEnd": { "status": "untraced" },
    "operationalEnd": { "status": "untraced" },
    "attestations": [
      {
        "on": "1994-10-14",
        "precision": "day",
        "scope": "designation in force",
        "source": "source ID or URL",
        "locator": "operative clause"
      }
    ],
    "currentConfirmation": null
  }
}
```

For each end, use one of:

- `known`: a dated fact with `eventKind`, precise source, locator and date precision;
- `occurred_date_unknown`: positive evidence that the ending happened, but no date;
- `untraced`: no established ending, which is **not** a claim of current existence;
- `not_applicable`: only where the entity/episode model makes that true.

A known date can be an exact day, month or year. A genuine bound can use `notBefore`/`before`, backed by evidence. Do not manufacture bounds from search failure. A current confirmation is a sourced observation at a date, not an infinite future interval. Preserve formation meaning separately as already done with `establishedMeaning`; a first sighting is not formation.

`attestations` can be points or explicitly supported intervals. A display window derived from them is presentation metadata and must never be exported as a dissolution. For an untraced historical body, draw evidence points/qualified observations and supported spans; leave the remainder unknown. If the strict snapshot is specifically “standing at 31 December,” a dated observation earlier in that year alone is not proof of standing on 31 December. Either show it as “documented during this year” with that distinction, or show it in an evidence view/optional uncertainty layer.

The resolver should return at least `confirmed`, `observed_during_year`, `uncertain`, `outside_known_span`, with reasons and claim references. An unknown period must not be presented as “did not exist.” Search and panels remain available in every state. A default operating structure can stop at a proved operational end while an optional legal-entity layer preserves the later shell; both dates remain visible in the panel and timeline.

### Applying the model to the immediate cases

| Case | Legal end | Operational end | Display consequence |
|---|---|---|---|
| Seven rural boards | Untraced | Untraced unless further source establishes it | Import identity and designation evidence; do not give an unrestricted 2026 lifetime or assert a society is its legal successor. |
| 43 folded councils | Execution day untraced; retain any supported year-level claim with its actual basis | Broad 1997 reorganization claim must be labelled by precision and evidence | Keep council histories; no invented 1 January legal ending. |
| MTOC | Separate from 1 June 1985 asset/staff transfer | 1 June 1985 is the asserted operational boundary | Operating view may stop then; legal history remains unresolved or separately dated. |
| Seven community health services societies | 15 February 2002 registry dissolution in current data | Service transfer is a separate 2001 event | Distinguish a legal shell from active service delivery in late 2001. |
| Regional hospital districts with powers restricted in 1995 | Not dissolved by that restriction | Restricted functions continue | Do not stop their corporate lifetimes at the restriction; store changed powers. |
| RHD transfer due by 31 December 1998 | Use actual dissolution instrument where supplied | Transfer execution may be unknown | Deadline is not an actual closing date; asset recipients need not be legal successors. |

## Local register and the People connection

Use `scope:"local"` and explicit kinds such as `regional-hospital-district` and `hospital-improvement-district`. Keep names with dates, establishment and ending claims, membership/governance rules, transfers and conflicts. A relationship should have a type, dated coverage or observation, source, locator, and any scope/conditions. Drawing a relation and traversing it as political accountability are separate operations.

Use distinct types for ownership, administration, board appointment, membership, capital funding, regulation, inspection, asset transfer and service transfer. None should become a ministry accountability edge just because its counterparty is a ministry. Set traversal eligibility from the validated relation type; ordinary board appointment must not reuse the existing traversable `appoints` type.

For local democratic routes, record the actual electorate and representative offices. Some HID instruments describe landowner-qualified voters, age and provincial-voter eligibility; the retained evidence explicitly warns against replacing this with the whole provincial population. Regional-district membership likewise does not alone prove the relevant appointment or representative route at every historical date. Populate a local accountability route only when the applicable dated governance rule supports it. Keep any uncertain or incomplete route visibly incomplete.

The current People description already distinguishes residents, children, patients and communities from eligible electors (`snapshot.js:198–205`). Preserve this. A services view can connect bodies to the populations they serve without implying electoral eligibility. Treaty First Nations governments must be peers with their own governance and treaty/partnership links, not ministry children. Current FNHA partnership handling is a useful existing guard.

Change `GovernmentPanel.jsx:342` for local bodies: “No source names a ministry” is not an adequate explanation for the absence of a local democratic route. Say which governance route is evidenced and which portion remains untraced.

## Focused implementation acceptance checks

1. A rural-board record is searchable and its designation event opens, but `ended:null` never silently creates a confirmed 2026 body.
2. “End untraced” and “proved ended, day unknown” remain distinct in generated data and panel wording.
3. A `1997` end preserves year precision; it never produces an alleged 1 January execution event.
4. Operational end and legal dissolution can differ without hiding either claim or mislabelling an end event.
5. Powertech's ownership edge remains visible as ownership and cannot, alone, create a path to the people.
6. Local districts remain distinct from similarly named health boards and from later same-named corporations.
7. A local body can be searched, selected and linked from an event without a ministry group.
8. The Greater Vancouver transfer appears for the actual district and its recipients, retaining partial scope, conditions and the residual government recipient.
9. Fort Nelson's first appointed trustees, later elected trustees and hospital-management role are all representable without overwriting one another.
10. A current-law checkpoint does not populate historical governance intervals; an unexecuted deadline does not become a transfer date.

## Verification and limits

I inspected the actual commit, compared relevant consumer changes to the exact baseline, ran direct Node snapshot/path probes, counted the council records and re-read relevant clauses from retained original PDFs `R4R-154` and `R4R-165`. The related-subject finding follows the actual builder projection and the new event input. The repo worktree was clean at the beginning; this review created only files outside it. No broad test suite was rerun by this review, and no new legal end, council execution day or transfer-closing day is claimed to have been discovered.
