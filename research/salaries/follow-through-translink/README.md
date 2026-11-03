# TransLink official source reconstruction, calendar 2020–2025

Six official FIA/remuneration PDFs were downloaded afresh from the supplied official URLs. All six match the supplied byte counts and SHA-256 digests. The cover years and every employee schedule heading establish years ending December 31; these are calendar periods, regardless of compiled fiscal edition labels.

The collection accepts **29 distinct employer/year cohorts and 27,402 individual observations**: 26,421 published names and 981 individually disclosed withheld-name payments. CMBC 2024 remains held with 3,896 candidate observations (3,894 named, two withheld). Every assigned PDF and all five employee entities per PDF have a disposition. None of the source PDFs or employer/cohort combinations appeared in an existing accepted official salary manifest when reconstruction began; existing compiled editions are preserved.

| Calendar year | Authority | BCRTC | CMBC | Security Management | West Coast Express | Accepted rows |
|---|---:|---:|---:|---:|---:|---:|
| 2020 | 557 | 847 | 2,635 | 210 | 6 | 4,255 |
| 2021 | 604 | 857 | 2,496 | 229 | 7 | 4,193 |
| 2022 | 578 | 893 | 2,874 | 238 | 7 | 4,590 |
| 2023 | 654 | 1,029 | 3,504 | 233 | 6 | 5,426 |
| 2024 | 799 | 1,129 | **3,896 held** | 264 | 6 | 2,198 |
| 2025 | 906 | 1,222 | 4,340 | 266 | 6 | 6,740 |

## Entity and observation scope

The authority uses `translink`; operating-company schedules use `british-columbia-rapid-transit-company`, `coast-mountain-bus-company`, `transit-police`, and `west-coast-express`. Only the BCRTC, CMBC and WCE slugs require new employer registry entries. Subsidiary employees are never rolled into the authority.

The parent task verified the primary employer bridge for the source's legal heading **TransLink Security Management Ltd.**: [TSML Policy 029](https://transitpolice.ca/wp-content/uploads/_pda/2023/07/TSML-Policy-No.-029-Psychological-Health-and-Safety-Management-System-PHSMS.2022-01-27.WebsiteRedacted.pdf), definitions on physical page 2, identifies TSML as the entity employing Transit Police personnel and defines Transit Police as also Metro Vancouver Transit Police. The 2025 TransLink accountability organization chart corroborates the employer bridge. These six official employee cohorts therefore use the existing `transit-police` slug, sector **Municipal police**, and display name **Transit Police (TransLink Security Management Ltd.)**. The actual legal report title and `reportedEmployerName` remain unchanged. Root retains the pinned bridge evidence.

The legacy compiled `metro-vancouver-transit-police` alias remains distinct pending separate observation-level review. No compiled rows are reassigned or deleted. Compiled `translink` observations may mix parent and subsidiary attribution; these official entity-specific cohorts do not justify automatically moving compiled observations or declaring complete compiled-group equivalence.

Only complete individually disclosed employee schedules over $75,000 are accepted. Each rank-number Security Management row and each separate FOIPP-withheld CMBC payment is one individual observation with `name=null`. Their source labels, amounts, physical pages and occurrence order remain in evidence. No anonymous rows are merged. Names are retained as printed, with layout line breaks joined by a space; no identities or titles are inferred. There is no dedicated employee position column, so `position=null` throughout.

Board directors, Mayors’ Council, executive component/total-compensation disclosures, suppliers, below-threshold employee aggregates and employer EI/CPP aggregates are excluded from individual data. Published duplicate names with different source occurrences remain separate.

## Monetary definitions and missing values

The imported remuneration is **Total Remuneration**, never Salary Payments alone or a sum substituted for the published total. The reports define remuneration as salary, wages, overtime, retroactive pay, vacation, banked time payout and other taxable benefits paid during the year. They exclude non-taxable benefits and amounts payable under severance agreements; report page 4 also excludes pension benefits. Expenses include vehicle operating, travel, membership, tuition, relocation, registration and similar payments to employees or third parties on their behalf, outside remuneration.

Salary Payments and Other are retained as separate evidence columns. Blank cells and dashes, including PDF soft-hyphen dash glyphs, become `null`, while literal numeric zero remains `0`. Parenthesized negative amounts remain negative. In 2025 WCE, three expense cells are visibly blank. In 2025 CMBC, Lutz, Joe has a salary-component dash, Other $91,987 and published remuneration $91,987; the component dash remains unknown and the total remains $91,987.

## Extraction and controls

PyMuPDF positioned words and independent Poppler `pdftotext -layout` extraction agree on every individual employee label, all four monetary cells and physical page for **all 31,298 candidate rows**, including the held cohort. Printed control monetary cells also agree between both readers. Every source entity, schedule heading, calendar period and complete row census is checked, with fail-closed expected counts and residuals. Row sums cover Salary Payments, Other, Total Remuneration and Expenses. Printed over-threshold, below-threshold and grand totals remain unchanged in evidence.

Source pixels were reviewed for every employee subtotal, all 31 wrapped-name cases, withheld individual payments, the negative Security expense, blank/dash columns and the small control differences. Thirty-one wrapped-name crops are retained in four contact sheets; two names whose surnames are printed above the monetary row receive dedicated parser regressions. The six annual control contact sheets identify physical PDF pages. These are focused visual checks; they are not a claim that every ordinary row was manually transcribed or individually viewed.

Twenty-five accepted cohorts reconcile exactly in all four columns. Four accepted cohorts retain small, proven source arithmetic differences. Values below are **displayed individual row sums minus the printed over-$75,000 subtotal**, in CAD:

| Cohort | Salary Payments | Other | Remuneration | Expenses | Decision |
|---|---:|---:|---:|---:|---|
| BCRTC 2022 | +3 | +7 | +7 | −1 | Accepted with public warning |
| BCRTC 2023 | −1 | −5 | +17 | +4 | Accepted with public warning |
| BCRTC 2025 | 0 | 0 | 0 | +9 | Accepted with public warning |
| WCE 2025 | 0 | 0 | 0 | −1 | Accepted with public warning |
| CMBC 2024 | +3,859 | −3,212 | +647 | −12 | Held |

BCRTC 2022 and 2023 also contain many displayed component-vs-remuneration differences of $1; each is recorded in row evidence, without changing any source cell or asserting an undocumented rounding rule. For WCE 2025, the visible expenses are $1,105 + $44 + $2,187 = $3,336, but the report prints $3,337. All three blank expenses remain null. No balancing amount or fabricated total is introduced.

CMBC 2024’s 3,896 candidate row components add exactly, and its two individual FOIPP rows are included in candidate sums. Its printed over-threshold, below-threshold and grand totals are internally additive. The last-page footnotes only define Salary Payments, Other and FOIPP; they do not explain the larger differences from the complete individual schedule. The candidate schedule stays held pending a publicly issued corrected/revised report or an official row-level explanation resolving those four differences. The held array is under `held/`; the manifest intentionally uses `candidateFile`, with no accepted `file` key.

## Files and reproducibility

- `sources.json`: accepted source schema, 29 accepted cohorts, and one explicit `unparsedSources` held cohort.
- `dispositions.json`: all six assigned report IDs, with five entity decisions each and specific held next action.
- `reports/2020.json` through `reports/2025.json`: per-report periods, definitions, complete counts, pages and four-column controls.
- `evidence/*.json.gzip`: complete per-row four-column/raw-cell evidence, printed controls and every row component difference, including the held schedule.
- `held/coast-mountain-bus-company-2024.json.gzip`: complete six-field candidate array; excluded from accepted sources.
- `fixtures/native-page-regressions.json.gzip`: fingerprinted original positioned words and independent layout text for actual problematic pages.
- `visual-review/`: reviewed source pixel crops and annual employee-control contact sheets.
- `originals.json`: official URLs and independently checked original fingerprints.

Normalized arrays have schema `[employerSlug, name, position, remuneration, expenses, pdfPage]`. Gzip uses `mtime=0`; `dataSha256` hashes compressed bytes and `normalizedSha256` hashes compact UTF-8 JSON. Original PDFs and full Poppler text are cached outside the repository at `/workspace/salary-source-follow-through/cache-translink/`.

From the checkout root:

```sh
python scripts/follow_through_translink.py --write
python -m unittest scripts/test_follow_through_translink.py
```

The rebuild fingerprints the cached official originals, runs both readers over all six years, and refuses new counts, field disagreements or unreviewed residual changes. It writes only this collection. Shared employer registry, export and source-backlog integration belongs to the parent task.
