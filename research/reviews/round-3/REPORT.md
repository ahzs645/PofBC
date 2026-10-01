# Government research and evidence-preservation work

Reviewed repository: `ahzs645/PofBC`, base commit
`e4adca9576b3d5b834918836133c72c7e578ed7d`. Research cutoff: 30 September 2026.

This package completes the CAWS census pilot, the Executive Council errata audit, a first
bibliographic discovery index, and the principal evidence-preservation fixes identified in the
previous review. It does **not** certify complete BC government history. Unresolved identities,
incomplete lifecycles, and source disagreements are preserved rather than converted into facts.
Changes are delivered as a patch; no GitHub branch was pushed and no site was deployed.

## What the research established

### A contemporary census instead of working backward from survivors

All entries in four CAWS report appendices were extracted and given a disposition:

| Source roster | Entries | Temporal meaning |
|---|---:|---|
| 2002/03 organization chart, Appendix C | 53 | Explicit observation on 30 May 2003, after the fiscal period |
| 2003/04 organization chart, Appendix B | 53 | Narrative associates it with the first ten months; exact observation date unresolved |
| 2002/03 agencies/boards/commissions, Appendix A | 30 | Report roster; one advisory council is printed twice |
| 2003/04 agencies/boards/commissions, Appendix A | 24 | Report roster with transfer/replacement footnotes |
| Total | 160 | Occurrences, not 160 distinct institutions |

There are 89 distinct printed labels. Neither this number nor an exact-name match is a count of
verified institutional identities. The ledger preserves each printed parent and nested unit, with
source URL and locator. Corporate boards are distinguished from their corporations; ambiguous
program headings and non-provincial scope candidates are flagged. The charts retain their printed
wording, including potential variants, without declaring them renames.

Sources:

- https://www.bcbudget.gov.bc.ca/annual_reports/2002_2003/caws/caws_appendixc.htm
- https://www.bcbudget.gov.bc.ca/annual_reports/2003_2004/caws/caws_appendixb.htm
- https://www.bcbudget.gov.bc.ca/annual_reports/2002_2003/caws/caws_appendixa.htm
- https://www.bcbudget.gov.bc.ca/annual_reports/2003_2004/caws/caws_appendixa.htm

`research/censuses/caws-2002-2004.json` contains the complete scoped census. Twelve source
reconciliations are in `research/audits/caws-reconciliation.json`; five dated ministry events are
compiled from them. They describe formation or movement of functions, not the founding of current
services inferred to be successors.

The key differences requiring caution are a branch listed in a later chart after a reported
transfer, internal regrouping reported without exact dates, and wording changes that may be editorial.
The 2002/03 narrative describes ministry formation from programs drawn from seven ministries; it
does not establish a merger of seven entire institutions. The 2004 Management Services plan explicitly
separates structural organization from functional core-business categories. These are practical
reasons not to convert report headings indiscriminately into hierarchy edges.

Narrative and model sources:

- https://www.bcbudget.gov.bc.ca/annual_reports/2002_2003/caws/caws_role.htm
- https://www.bcbudget.gov.bc.ca/annual_reports/2003_2004/caws/caws_role.htm
- https://www.bcbudget.gov.bc.ca/2004/sp/mser/mser_appendix1.htm

### Nine historical safety bodies with a supported general dissolution date

B.C. Reg. 137/2004, section 6(a)-(i), identifies nine dissolved safety boards and committees.
Its commencement is 1 April 2004. Each is now a historical research record with a typed closure
event, source and clause locator. **The exception for hearings already in progress is retained.**
No unverified founding date or continuous ministry-parent interval is supplied.

The nine records can be inspected in the source roster and research files. They are not drawn as
ordinary dated bodies throughout earlier years: their starts remain unknown. The legal dissolution
is a general institutional boundary with a residual-hearing exception, not proof that every function
ceased that day. The similarly worded electrical review body in the report remains an identity
question; the law's precise name is used for the historical record.

- https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v47n07_137-2004
- https://www.bclaws.gov.bc.ca/civix/document/id/lc/bcgaz2/v47n07_136-2004

### Executive Council errata: checked, not assumed missing

All eighteen corrected assertions were compared with stored appointments, including their
`llbc_portfolio` wording where it differs from the display title. The original volume's printed
pages 73, 109 and 110 and the two-page errata PDF were retrieved and visually inspected.

The three corrected appointment ranges already match the repository. The other fifteen corrected
portfolio-title boundary assertions also have matching stored boundaries. This is not verification
of every intervening holder or a demonstration that portfolio titles always map to administrative
ministry entities. Open ends in the printed errata remain open at that publication's cutoff; they do
not mean an office continues today.

The crosswalk records original reading, correction, matched input file/index, selected disposition,
and source locators. Corroborating evidence was added to the three appointments; their dates were
not changed. Their additional citations are retained in compilation and shown as evidence.

The spelling difference between singular/plural Communication in the atlas episode and appointment
was a compiler matching problem. Normalizing this variation repairs the previously unmatched
transportation episode without rewriting either source's printed name. Using the supplied
`llbc_portfolio` for matching also respects the source's title. All 242 ministry episodes now have at
least one matched term. This is distinct from year coverage: 1,973 of 1,990 sampled ministry-years
have a head; seventeen years remain unmatched.

- https://www.llbc.leg.bc.ca/public/pubdocs/bcdocs/47984/execouncil.pdf
- https://www.llbc.leg.bc.ca/public/pubdocs/bcdocs/47984/errata.pdf

### Bibliographic discovery with explicit limits

The Legislative Library's 1995-1999 download contains 120 members and 807 catalogue records.
Thirty-four members are empty; every member has a byte count and checksum. Forty annual-report,
directory or organizational-title candidates have a question attached for the next census work.

This is a searchable document-discovery dataset, not an organization census or verified institutional
history. The dates describe publications/cataloguing. Links have not all been followed. MARC-8 data
has a byte-preserving Latin-1 view with an explicit decoding warning; use a MARC-8 decoder before
relying on non-ASCII names. The parser rejects malformed lengths or directories instead of skipping
bad records.

- https://www.leg.bc.ca/learn/legislative-library/marc-downloads
- https://www.llbc.leg.bc.ca/public/pubdocs/bcdocsMARCBatchFiles/1990s_records/1995-1999.zip

The ministerial accountability and Public Accounts archive landing pages returned 502 errors during
this pass. No new claims were accepted from their unavailable contents. That does not invalidate
existing repository records from documents previously retrieved.

## What changed in the build and page

- Conflicting assertions sharing an event ID survive as stable variants marked conflicting.
  Corroborating copies merge source references while retaining independent locators and supplied
  review dates. Semantic similarity under different IDs is not silently deduplicated.
- Missing claim review dates stay null. A file generation date or import date cannot manufacture a
  review date. Lieutenant Governor entries without an evidence status remain unreviewed.
- Event and history source URLs retain fragments. Event sources additionally expose a document URL
  without the fragment; the evidence panel shows individual locators and review dates.
- Body predecessor sets and omitted successor targets are preserved. Existing lineage display uses
  retained predecessor IDs as well as inverse single-successor links. This is not yet a general
  function-level split/merge editor.
- Responsibility rows retain their source and locator, and differing end bounds survive projection.
  A full editorial selection workflow remains needed; raw alternatives are available in the audit.
- Month matching bounds use actual month lengths, including leap-century rules. Source date
  precision is unchanged. No existing appointment corruption count is claimed.
- Input accounting retains original input for accepted, conflicting, intentionally excluded and
  unresolved/unmapped outcomes. It also retains collection-field conflicts and unmatched offices,
  staffing and event candidates. Accounting counts measure processing, not verified history.
- The Government page's Sources section includes expandable historical rosters, matching caveats and
  import counts. Conflicting event evidence is labelled as conflicting, rather than scheduled.
- A complete government build command and a CI drift check keep committed research outputs in sync.
  The research brief has an explicit reference date; this does not generalize the app's parliamentary
  dataset or turn it into a precise-date snapshot.

Latest accounting:

| Compiler | Accepted | Unresolved/unmapped | Excluded | Conflicting |
|---|---:|---:|---:|---:|
| Events | 426 | 24 | 0 | 0 |
| History | 2,132 | 168 | 4 | 1 |
| Atlas | 791 | 75 | 0 | 0 |

Addendum on applying the patch: four sub-agency review starts (Public Guardian and Trustee 1963, BC
Cancer 1974, Environmental Assessment Office 1995, BC Timber Sales 2003) repeated an earlier event's
subject, day and kind, and would have drawn each founding twice. They now attach to that event as
further evidence, recorded as `corroborating_duplicate`. The events row is therefore 422 accepted,
24 unresolved and 4 corroborating.

These are source/claim processing rows of different granularity. Conflicting-event handling is tested
with fixtures; this dataset has no same-ID event conflict. The existing sub-collection parent conflict
is preserved and reported. Unmatched non-ministry portfolios are retained; they are not assumed to
be invalid appointments. Two month-described administrators and seventy-three staffing figures
remain unplaced, with their source input retained in the atlas audit.

## Verification and reproduction

- Government and evidence-preservation regression suite: **65 passed, zero failed**.
- Full repository suite with available generated extras: **362 passed, zero failed, 21 skipped**
  (383 discovered tests). Skips concern unavailable artwork/font assets; this is not an unqualified
  full visual-artwork validation.
- Government compilation and drift check: **byte-for-byte reproduction passed**.
- New roster component: isolated Vite production compilation and server rendering passed.
- Full production build: blocked by missing generated `src/fonts.css`; the repository's font build
  depends on a licensed Helvetica source/macOS runner. No substitute font was introduced.
- Browser visual inspection: not completed; the Playwright browser download was unavailable.
  The isolated component build is not proof of final mobile layout or full-page accessibility.

Apply this patch to the reviewed commit on a branch:

```sh
git apply --check pofbc-government-evidence.patch
git apply pofbc-government-evidence.patch
git submodule update --init --recursive
npm ci --ignore-scripts
npm run build:current-extras
npm run build:government
npm run check:government
node --test 'src/government/*.test.js' scripts/evidence-integrity.test.mjs
```

To run the complete application's checks, initialize submodules, install dependencies and provide
its existing licensed font/artwork prerequisites. Use the macOS CI job for the full asset build.
Source captures are transient and not included in the patch; `source-manifest.json` supplies public
URLs and checksums. The MARC index and extracted claims are included.

## Remaining work that must not be mistaken for completion

The accompanying `remaining-work.json` maps seventeen review themes to implemented, partially
implemented, completed-audit or pending states. The largest open work is historical coverage outside
this one ministry and period, then effective-date instruments and identity resolution within its
rosters. Existing current-sub-agency review gaps remain; no percentage of all historical government
units can be inferred from today's list.

Priorities are to adjudicate chart/narrative conflicts with effective instruments, validate the forty
source candidates, extend censuses into the 1970s-1990s, and test precise-date semantics before
introducing a snapshot mode. Broad parliamentary generalization, function-level lineage and branding
specimen-ledger work are explicitly pending. The full historical research programme is not closed.
