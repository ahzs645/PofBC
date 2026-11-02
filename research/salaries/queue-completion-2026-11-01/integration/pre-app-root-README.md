# Salary queue completion and further gap research

This pass works through the nine entries left by [PR36’s held-source release](../held-resolution-2026-11-01/release.md), and investigates additional school and municipal gaps with separate agents. The [release reconciliation](release.md) gives the accepted counts and sources. The [original-task disposition ledger](original-queue-dispositions.json) distinguishes completed public processing from issuer-dependent records. Earlier frozen work queues overlap; their entries must not be added together as unique missing reports.

## What qualifies for import

Use the reporting year printed in the remuneration schedule, its actual disclosed payment definition, every published named observation, and literal source values. An upload date, a fiscal-looking compiled label, a familiar name, or a matching financial subtotal cannot establish another reporting period or an employee’s identity.

The new native-text sources have independently implemented readers, actual rendered-source visibility checks, and independent row comparisons. PHSA scans use Tesseract and Paddle/RapidOCR with source-specific layouts and independently image-transcribed benchmarks. Raw reader outputs and all initial flags are preserved separately from source-image corrections.

PHSA’s additional guarded agreement policy can resolve a confidence-only flag when both readers recognize exactly the same literal field and all source geometry and name-quality guards pass. Confidence scores are model scores, not accuracy probabilities. Actual disagreements, missing or unparsed detections, ambiguous name glyphs, source-layout exceptions and unsupported monetary types remain image-review targets. The policy also requires independent implementation review and ten deterministic, previously unreviewed rows from each report, spread across early, middle and late pages. The first report’s original flagged packets remain fully reserved for manual review; its additional ten rows provide separate layout coverage. Finite benchmark and holdout success does not prove that every later machine agreement is correct. Validation distinguishes personal image review from automated corroboration.

Some PHSA scan fonts draw capital `I` and lowercase `l` identically. Exact cases may use the source’s initial-capital convention or surname order as an explicitly qualified reading after two source-image reviews and root adoption. Alternatives remain in the evidence and the source warning. In-word capitalization is not inferred from a dictionary. Other reports have visibly distinct serif glyphs and are checked using their own source images.

Some low-resolution serif scans also merge `rn` or other upright strokes. Finite `rn`/`m` alternatives require two original-image readings, exact case adoption and a public source warning. Other compressed-stroke ambiguities require a separate, closed list of individually adopted source hashes, rows, crops, preferred transcriptions and complete alternative sets. That list grants no general spelling or identity authority. Contextual ordering is an explicit assumption, not proof of a unique glyph. All first transcripts, reviewer mistakes, source rereads and superseded overlays remain preserved with additive corrections.

Every manual monetary reading that matches neither independently parsed reader requires a fresh second source-image reading before release. The comparison uses literal amounts and exact source fields. A subtotal difference cannot supply a correction. Revised overlays retain their predecessors and require a hash-pinned supersession with identical source, rows and requested field scope.

Final source-view review uses the original native 300 dpi page and integer crops of a complete page rendered at 600 dpi. A partial PDF clip can render fine strokes differently, so it cannot settle a disputed letter by itself. Source-pixel reproduction verifies the view and row geometry; it does not prove a reviewer read the glyph correctly. The earlier eight histories received an additional check of 365 qualified names, 43 selected direct manual names and 138 positive monetary fields. This is a bounded review, not a new personal transcript of every payment. For example, the current source supports `Mundi,Jacqueline` and `Bell,Ritteshni`; the earlier `Mundl` and missing-`t` decisions are preserved as superseded errors. The older Mundi view already contained the dot: that correction fixes a reading error, not a renderer defect. Corrections and expanded finite sets use new immutable revisions. The root acceptance selects each exact candidate revision and source-review receipt, with no automatic fallback to an older or newest file.

A source expense dash or visibly blank field stays null. A printed zero stays zero. A missed OCR detection establishes neither. Expense-inclusive totals, aggregate payroll, supplier payments, employer contributions and amounts paid to entities do not become individual remuneration unless the source defines them that way. Board observations with nonnumeric remuneration remain supporting research, without invented zero pay.

## Specific source decisions

- The nine historical PHSA cohorts require all original pages and complete named scopes. FY2018/19’s literal row count and printed headcounts do not all agree; no invented observation closes that difference. A source footnote about an earlier unpaid-leave adjustment does not move a payment into another disclosure period.
- PHSA 2019/20’s final second reading corrected three monetary cells from the original images. The complete literal rows still exceed the printed remuneration control by $5,220; expenses reconcile exactly. The cause remains unestablished, and the published standalone schedule does not establish board approval. These qualifications accompany the accepted records; no amount was changed to close the remaining difference.
- Providence FY2023/24 and Vancouver Coastal Health FY2020/21 were recovered through official Legislative Library downloads. Those representations include an added catalogue cover; page references and hashes identify the downloaded versions. No byte-identity claim is made against an inaccessible issuer download or differing catalogue checksum.
- Providence’s Board has 15 printed observations, of which ten have numeric remuneration. Their known expenses are $5,455; the excluded five nonnumeric-pay observations carry $1,111, making the full Board control $6,566. This is an explicit subset difference, not a financial error or permission to infer zero remuneration.
- VCH’s complete literal employee rows exceed printed named controls by $39 remuneration and $22 expenses. These residuals remain visible. Its separate Part F download contains no approval page; that absence does not establish either adoption or an unsigned draft.
- Mission 2023’s independently corrected literal pay is $3 below its printed employee control; the affected row’s inclusive total also disagrees. Mission’s named selection wording uses remuneration **and expenses**, so it is not treated as a pay-only threshold. City-paid work for its Bridgehead corporation stays in the employer and rows printed by the source.
- Vernon 2025’s literal employee expenses are $1,007 below its printed named control. Creston 2024’s literal employee rows are $12 remuneration and $10 expenses below the corresponding controls, with separately described aggregate differences. Complete independent source-row reviews support qualified import; no amount is balanced, allocated or given an inferred explanation.
- The school review preserves literal clipped text, negative expenses, low-paid trustees, source-footnoted employees and repeated observations. Twenty SD61 positions initially included separate page-footer numbers in both readers; an independently image-confirmed additive correction removes only those footer numbers. Earlier candidate and raw-reader bytes remain available.

## Compiled-copy replacement

Only Providence’s complete 3,289-row compiled employee cohort is selected for removal by the new [comparison](integration/compiled-comparison.json). A separate implementation verifies the whole multiset, every literal pairing, exact cents, row multiplicity and the original selected-row order. Comparison permits case, whitespace and punctuation differences while retaining every Unicode letter and digit. Its 588 official expense dashes compare to compiled zeros only for identifying the copied cohort; the official expenses remain null.

VCH’s large partial overlap includes unmatched executive observations with different compensation. Its entire compiled partition stays retained. No partial overlap, apparent name similarity or duplicate-looking observation authorizes deletion.

The replacement pins the original PDF, normalized data and exact compiled rows. The builder rejects later source changes even when extracted data happens to stay the same. Existing official records and their metadata remain exact.

The acquisition worker’s original 105-file handoff is frozen. The active `queue-completion-acquisition-release` manifest uses byte-identical local copies of its payloads and applies only the [reviewed retention-description amendment](integration/acquisition-metadata-adoption.json). Local copies preserve the builder’s collection-path boundary. This prevents the two Providence warnings from falsely claiming that the removed employee copy still coexists. VCH qualifications, all observations, source hashes, years, scopes and definitions stay unchanged.

## Records that still require an issuer

The [four-request outbox](acquisition/outbox/outbox.json) contains verified recipients and concrete ordinary existing-record drafts for NIC, McBride, SD8 and SD10. On 1 November 2026, the user [instructed that all four requests be held and noted in the repository](acquisition/outbox/user-direction-2026-11-01.json). No institution message, web form, statutory application or fee has been submitted. The drafts and unresolved source issues remain recorded; no sending step is authorized.

NIC’s salary scope is already accepted; the request seeks a complete preservable original for the truncated archive package. SD8 and SD10’s existing qualified observations stay published while their conflicting headings, declaration/adoption evidence and aggregate figures require clarification. McBride’s five ambiguous council observations remain excluded because the actual table says 2024 inside later packages; generic package approval cannot relabel those rows.

Additional gaps located by agents appear in the [gap inventory](additional-gap-inventory.md). A public scan needing extraction is processing work, not automatically a procurement or FOI gap. No claim is made that every historical salary report in British Columbia has been located.

## Reproduction

The salary build is offline and uses committed normalized payloads, manifests, raw extraction evidence and hash-pinned reviews. Original PDF downloads, OCR models, caches and temporary page images are not required by the build. Source-specific scripts and guides under `acquisition`, `schools`, `municipal` and `phsa` describe downloading and replaying their originals. Every independently resolved field retains its source/page/row mapping and review evidence.

```sh
python3 scripts/finish_salary_queue_overlap.py --check
python3 scripts/finish_salary_queue_release_inputs.py --check
npm run compare:municipal-periods
npm run build:salaries
npm run check:salaries
npm run audit:municipal-salaries
npm run follow-up:municipal-salaries
npm run review:sector-salaries
npm run review:municipal-wave
npm run review:municipal-history
npm run review:salary-continuation
npm run review:salary-recovery
npm run review:salary-held-resolution
npm run review:salary-queue-completion
npm run preview:salaries -- --build
```

Run the Python parser regression suite and salary Node tests used by `.github/workflows/salaries.yml`. The new release gate requires all nine historical PHSA years, every final worker and root input freeze, exact source qualifications, explicit independent review coverage, the original-queue dispositions, and complete reconciliation of earlier and newly published records. A second build must produce the same generated files.
