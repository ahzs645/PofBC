# Evidence reconciliation — 12 November 2026

This is the first bounded response to the audit of PofBC at baseline commit
`620294eec90dba2e69d94b4dde8551108f61fe37`. It corrects several historical claims, preserves the
evidence behind date choices, repairs links between existing records, and records concrete source
leads for the next research pass. It does not close the full historical, salary or artwork backlog.

The checkpoint date is **12 November 2026**. Each source retains its own publication, event and
review dates. The current backlog and older measurements are preserved in
[`research/WANTED.md`](../../WANTED.md). Final local validation and its limits are recorded below and in
[`validation.json`](validation.json).

## Research method and evidence registers

For each contested claim, identify the kind of fact being asserted before looking for a date:
incorporation, statutory rename, business-name registration, asset transfer, operating cessation,
legal dissolution, registry observation or public identity announcement. Check an operative passage
in the original statute, order, contemporaneous announcement or audited statement. A report title,
upload path or later description cannot supply a different event's date.

Record the public URL and an exact section or page locator, the retrieval method, what the passage
supports, and what it leaves open. PDF evidence includes fingerprints where originals were
downloaded; page images were checked where typography, signatures or scanned approval stamps
matter. Record blocked retrievals as such. Preserve a conflicting or less precise assertion with
its provenance rather than inventing an additional event to explain it.

Change source records first, then project the reviewed result into generated data and the interface.
Keep legal identity, ministerial responsibility, property ownership, operational control, gallery
placement and disclosure-employer identity separate. A newly located document is a research lead
until its relevant evidence has been checked; a salary source needs the complete employee cohort
and reconciliation before it becomes accepted coverage.

| Register | Contents |
|---|---|
| [history-sources.json](history-sources.json) | Fourteen sources, exact locators, access limitations and decisions for BC Place/BCEC/PavCo, BC Rail, BC Cancer and specimen dates. |
| [prhc-sources.json](prhc-sources.json) | Three recovered event citations, the unretrieved 1976 source, two responsibility orders and contemporary corroboration. |
| [collection-priorities.json](collection-priorities.json) | Five retrieved and fingerprinted official salary documents, approval evidence, schedule pages, printed controls and acceptance work still required. |
| [link-check.json](link-check.json) | Structural links in materialized events, plus separately listed unmatched organizations and events with no source URL. |
| [election-2026-final-count.json](../../atlas/election-2026-final-count.json) | The declared election result, all 93 candidate rows, recount flags, source locator, fingerprint and review date. |

## Reviewed historical decisions

The [history source register](history-sources.json) gives the complete support and limits for the
following changes. The principal instruments are linked here to make the decisions reviewable.

| Question | Reviewed result | Evidence and retained limit |
|---|---|---|
| Did BCEC become PavCo? | BC Place Ltd. was renamed BCEC with effect from **31 March 1987**. BCEC ceased operations and transferred certain assets and liabilities to the Province and PavCo on **30 September 1989**. The BCEC-to-PavCo continuation and predecessor claims are removed. | [BCEC Act s. 1.1 and historical note; s. 2](https://www.bclaws.gov.bc.ca/civix/document/id/93consol17/93consol17/80002); [BCEC 2002/03 statements, notes 1 and 4](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2002-03/sup-e/bc-enterprise-corporation-fs-2002-03.pdf). An asset transfer does not establish a corporate rename or an exclusive predecessor lineage. |
| Which PavCo establishment date applies? | Former PavCo's incorporation is **3 May 1984**; registration of the PavCo business name is **23 September 1999**. The present corporation was formed by amalgamation on **1 April 2008**. These remain separate milestones. | [PavCo 2004/05–2006/07 Service Plan, printed p. 4](https://www.bcbudget.gov.bc.ca/2004/sp/crownagency/bcpc.pdf); [2024/25 audited statements, note 1](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2024-25/sup-e/bc-pavilion-corporation-fs-2024-25.pdf). The 1984 date belongs to former PavCo, distinct from the BC Place company recorded in 1980. |
| When did BCEC legally end? | Preserve the **1989 operating cessation**, add statutory dissolution on **13 March 2023**, and retain **27 March 2023** as the separate registry-status observation. | [B.C. Pavilion Corporation Act, ss. 4–6 and 10](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/22033), read with [OIC 171/2023 / B.C. Reg. 71/2023](https://free.bcpublications.ca/civix/document/id/lc/bcgaz2/v66n04_71-2023). The timing reason for the later registry entry is unestablished. |
| Did the BC Rail transaction close on July 14 or July 15? | Use **14 July 2004** for the transaction closing. Preserve the previous Wikipedia assertion in `superseded_assertion`; retain the TSB's **15 July** statement as an attributed retrospective date claim. | [Provincial Public Accounts 2004/05, printed p. 66, note 33](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2004-05/public-accounts-2004-05.pdf), [CN's contemporary release](https://www.sec.gov/Archives/edgar/data/16868/000095010304000988/jul1504_6k.htm) and audited accounts agree on July 14. No separate next-day handover is inferred. The operating business, statutory Crown parent and publicly retained railway infrastructure are kept distinct. |
| Do the BC Cancer 2017 records conflict? | One explicit reviewed decision selects the **15 November 2017** joint identity announcement and retains the compatible **2017** history entry as corroboration. The event describes a public-name simplification and aligned identity. | [BC Cancer history, 2017 entry](https://www.bccancer.bc.ca/about/history) and [the Foundation's dated announcement](https://bccancerfoundation.com/news-and-media/blog/bc-cancer-and-bc-cancer-foundation-strengthen-partnership-break-down-cancer/). The Foundation announcement was available as official indexed text; direct retrieval returned 403. These sources do not establish a legal corporate rename or merger. |

The BC Cancer choice is recorded in [`research/decisions.json`](../../decisions.json) as
`bccancer-identity-date-refinement-2017-11-15`. The compiler checks the selected origins, pinned
input digests, subject, type, status and compatible date bounds before applying it. Every original
input and its precision remain in the [event import ledger](../../audit/events-import.json), and
the event panel exposes the decision and evidence dates. Similar dates alone do not merge events.

The 1987 registry name entry remains alongside the statutory date. This review did not establish
why the two dates differ, did not independently refetch BC Place's previously recorded 25 March
1980 registration, and did not resolve the TSB discrepancy. Those limits are recorded in
`history-sources.json`.

## PRHC: recover citations and bound one responsibility period

Three event citations now point to retrieved official documents:

- **2000/01 BC Housing annual report:** printed p. 59 / PDF p. 61 shows PRHC's financial-statement
  heading. Its typography is described as a heading. The retained 2001 year is the reporting-period
  end; the document does not establish a distinct logo or an adoption date.
- **PRHC 2023 financial statements:** note 9(b), p. 18 explicitly dates the Riverview land and
  buildings transfer to **2 February 2015**, separate from the report date.
- **6 November 2025 PRHC letter:** the District of 100 Mile House's 12 November agenda, PDF p. 7,
  shows BC Housing's emblem and wordmark on this letter. The observation is confined to that document.

The original **1976 ministry annual report was not retrieved**. Searches reached a blocked library
catalogue and an unavailable publications portal. The event keeps a `null` URL and explicitly
unverified reported page locator, and its review date is cleared. Three recovered URLs out of four
is the result of this pass. The [PRHC register](prhc-sources.json) records the evidence, hashes and
attempts without treating an unretrieved source as reviewed.

[OIC 177/1998, appendix s. 15](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0177_1998)
and [OIC 897/1999, appendix s. 23](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0897_1999)
bound a ministerial-responsibility period under Employment and Investment from **18 February 1998
to 21 July 1999**. Both orders print “Commission”; the contemporary
[Auditor General's Social Housing report, printed pp. 53 and 35](https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19990901-social-housing-governance.pdf)
identifies PRHC and corroborates both dates. The source wording discrepancy is preserved in the
[new responsibility record](../../history/responsible-evidence-reconciliation-2026-11-12.json).
No earlier or later interval is filled by inference. The existing 1999 transfer event is reused.

## Event links and source gaps

Related organization IDs, related event IDs and legal references now have separate fields. Repairs
cover the Parks, Wildfire, BCTS, Coroners, Corrections and Public Guardian and Trustee references,
along with the Columbia Power subject ID. Event-to-event references open event anchors; legal
references carry their own URL and locator; unmatched organization mentions remain visible with
their reason.

[`scripts/check-record-links.mjs`](../../../scripts/check-record-links.mjs) checks the materialized
organization and event IDs, source indices and legal-reference shape. The current
[recorded output](link-check.json) covers **970 events**, **812 entities**, **315 related-entity
links**, **2 related-event links** and **1 legal reference**, with **zero structural issues**. It
separately reports:

- The **2007 Emergency Management B.C.** reference in the Coroners event. The service-plan mention
  is retained, but no matching dated entity is in the register. Health Emergency Management BC is
  a different body and is not substituted.
- The **1976 PRHC event without a retrieved source URL**, described above.

The [event import ledger](../../audit/events-import.json) also retains **26 unresolved/unmapped
inputs**. A clean link audit of materialized records does not establish complete input integration,
historical correctness of every claim or retrieval of every citation.

## Salary links and collection follow-through

Three reviewed employer-to-body mappings expose already held observations on the matching
government panels. Employer slugs continue to identify the disclosure URLs, even where the graph
uses a different ID.

| Employer slug | Government body ID | Existing observations | Existing source scope |
|---|---|---:|---|
| `bc-railway-company` | `bc-railway-company` | 146 | Employee remuneration |
| `bc-family-maintenance-agency` | `bc-family-maintenance-agency` | 22 | Board remuneration |
| `justice-institute-of-bc` | `justice-institute` | 392 | Compiled, unverified disclosure |

These **560 observations** were already in the dataset. The current
[employer index](../../../public/salaries/employers/index.json) has **280 employers and 48 mapped
bodies**; [coverage metadata](../../../public/salaries/coverage.json) still reports **1,460,511
observations**. The projection updates body links and derived body-period exports. It does not
convert board records into employee records or upgrade the JIBC compilation to official-source
coverage. The JIBC panel visibly labels compiled records as awaiting source review, distinguishes
edition labels from verified reporting periods and describes the sum as a recorded total. The
relinking script checks preservation of row, source, period and coverage totals and the original
compressed employer data.

The [collection-priorities register](collection-priorities.json) makes the next source work concrete:

| Lead | Evidence recovered | Remaining acceptance work |
|---|---|---|
| UNBC 2021/22 | Original SOFI package and approved board motion of 16 September 2022. | Extract the complete employee schedule, independently check it and reconcile both printed controls. |
| UNBC 2025/26 | Original package and employee schedule. | Final approval is unverified: the agenda proposes approval. Obtain approved minutes or a signed final report, then extract and reconcile. |
| SD57 Prince George 2023/24 | Official report and signed declaration dated 14 November 2024. | Separate trustees from employees; check every employee row and reconcile remuneration and expenses. |
| SD57 Prince George 2022/23 | Official scanned report and signed declaration. | Extract the scans, independently review every cell and reconcile the employee controls. |
| Fort St. James 2024 | Official report and signed approval dated 10 June 2025. | Independently transcribe and reconcile the employee schedule, preserving the report's stated scope. |

All **five original binaries were retrieved and fingerprinted**; **four have verified approval
evidence**. This source-discovery pass added **zero accepted employee rows and zero accepted source
manifests**. The register carries employee/board page boundaries, printed controls, approval
locators and the exact next action. Working PDF copies are not committed. The old Kitimat 2024
agenda link returned 404; a replacement original remains to be recovered.

## Gallery ownership, reverse links and specimen dates

Gallery shelf placement is now separate from organization identity. Reverse lookup includes a
body's own designs on shared shelves, including the provincial-mark shelf, and each thumbnail
links to its actual collection. HealthLink BC is explicitly mapped; Knowledge Network can use an
available SVG version even when the default download is EPS. Existing shared-shelf records for
WorkBC, BC Stats, BC Wildfire, the Coroners Service, BC Bid and the Public Service Agency can be
found through their organization links. The two BC Cancer Foundation designs retain Foundation
ownership while remaining in the same visual family as BC Cancer.

BC Place, BCEC and PavCo remain separate collections. BC Development also contributes to BCEC's
history, so the reviewed statutory rename and asset transfers do not justify an exclusive
one-to-one gallery lineage. Shared Services BC still lacks a resolved graph identity.

The specimen-date parser accepts complete supported date strings: ISO dates, explicit years and
ranges, fiscal years, named months or seasons, and explicit approximations. It does not extract a
year from arbitrary prose. Reviewed `specimenDate` metadata can express the date separately from
descriptive `sourceDate` text, and retrieval dates stay separate. The two BC Housing records whose
undated report mentions April 2019 now display an unknown specimen date. Other narrative-only
source dates remain visible as context until a reviewed date is supplied. Neither a specimen
sighting nor a report period establishes logo adoption.

## Election result and officeholder snapshot

The [election source register](../../atlas/election-2026-final-count.json) records Elections BC's
**9 November 2026 final count** for the **24 October election**, checked on **12 November**:
**93 declared elected candidates**, comprising **64 Conservative Party**, **27 BC NDP** and
**2 BC Green Party** candidates. **Kelowna Centre** and **Ladysmith-Oceanside** retain judicial-recount
flags. The interface shows the totals and recount districts, with the full candidate table
expandable and linked to the official source.

The register also records the Assembly's statement that 44th Parliament member information would
be available on receipt of certified results on **18 November 2026**. The result does not establish
swearing-in, current caucus affiliation, the Speaker or cabinet appointments. The existing
officeholder snapshot retains its own older review date and is labelled as predating the election.
Future updates must review those separate facts against their own sources.

## Measured checkpoint and remaining priorities

The current branch's 1871–2026 annual-snapshot measurements are carried into
[`WANTED.md`](../../WANTED.md), alongside the preserved older checkpoints:

| Measure | 12 November 2026 |
|---|---:|
| Ministry-years without a matched minister | 0 of 2,015 |
| Body-years with a stated responsible ministry | 2,755 |
| Body-years placed beside a ministry by inference | 106 |
| Body-years with no ministry, excluding sub-agencies, partnerships and courts | 551 |
| Sub-agencies with an established start / a dated sighting / neither | 52 / 175 / 24 of 251 |
| Historical sub-agency-years whose parent is inferred from today's | 2,956 of 3,073 |
| Bodies with Wikipedia as their main source | 22 |
| Bodies with a year-only start | 58 |
| Historical bodies with no start, shown in lineage only | 5 |

Zero missing ministry-year matches is an annual-snapshot result, not a day-by-day tenure audit.
**96.2%** of historical sub-agency-years still infer a parent from today's relationship. Further
responsibility work should recover and resolve dated reorganization schedules and annual-report
charts before adding historical edges. The earlier handoff's **657 clauses from 17 orders** still
require entity and relation review; those clauses are not ready-made parent edges.

The next work remains concrete: retrieve the 1976 PRHC source; investigate the legal/registry date
differences and the TSB discrepancy; establish the unmatched 2007 Emergency Management entity;
complete and independently validate the five salary cohorts; review more employer-to-body
mappings; recover explicit specimen dates and artwork; and update officeholders after the relevant
official records are available. This pass does not imply completion of historical health-body
coverage, sub-agency lineage, the wider salary archive or the artwork collection.

## Validation

Final local verification passed on **12 November 2026** (13 November UTC). The exact results and
preserved employer-file fingerprints are recorded in [validation.json](validation.json).

| Check | Result |
|---|---|
| Consolidated government, gallery and affected script tests | **232 unique tests passed**, zero failed or skipped |
| Actual component output through Vite SSR and ReactDOMServer | **11 checks passed**, covering election dates/counts/recounts, overview and Assembly labels, both BC Housing headers, Knowledge SVG assets, and JIBC/BCFMA disclosure labels and links |
| `npm run check:government` | Generated outputs reproduce **byte for byte**, with `GOVERNMENT_AS_OF=2026-09-30` |
| `node scripts/relink-salary-bodies.mjs --check` | All **20** projected/index files match; **15** body-period routes |
| `npm run check:record-links` | Zero structural issues; the unmatched entity and missing source remain in the report |
| Employer export preservation | All three original gzip files have exactly the baseline SHA-256 values |
| Focused production Vite build | **107 modules** compiled, including the actual affected React components and application CSS |
| `git diff --check` | Passed |

The consolidated regression command is:

```sh
node --test --test-reporter=tap \
  'src/government/*.test.js' 'src/gallery/*.test.js' \
  scripts/event-decisions.test.mjs scripts/record-links.test.mjs \
  scripts/evidence-reconciliation-history.test.mjs scripts/salary-body-links.test.mjs \
  scripts/evidence-integrity.test.mjs scripts/salary-data.test.mjs \
  scripts/merge-research.test.mjs
```

The rendered-output check found and prompted a fix for JIBC's previously hidden compiled-source
qualification. It now shows the pending source review, the edition-label limitation and a
“Recorded total” label. BCFMA continues to identify board remuneration. The checks also confirmed
that the employer URLs retain their original slugs and that the selected public data and artwork
paths exist locally.

**Verification limits:** these were server-rendered HTML checks, not visual browser tests. They do
not exercise React effects, asynchronous row loading, click interactions, responsive CSS or
deployed HTTP routes. Standalone Chromium could not launch under the platform's socket
restrictions, and both connected browser environments could not reach the workspace preview.
No visual screenshots are claimed. The full application build was not verified because this
checkout does not initialize the unrelated vendor submodules; a temporary harness compiled the
actual affected components. Its combined bundle emits a size warning and is not a measurement of
the normal application's bundle splitting.

The commit uses `[skip ci]` to avoid unnecessary GitHub Actions usage. These results are local
checks; no hosted CI pass, deployment or merge is claimed.
