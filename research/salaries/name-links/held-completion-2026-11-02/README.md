# Completion review of the 3,173 held name pairs

All **3,173** pairs received a reproducible assessment of the records already published. **130 are connected with verified evidence and 25 with qualified likely evidence**, including 10 likely connections present before this pass. This pass therefore connects **145 additional original candidate pairs**. The remaining **3,018 pairs** stay unconfirmed and separate. Their salary records were already in the application and remain there.

The assessment checks full given names (not just a first initial), all compatible alternative names at that employer, primary reporting-year/date overlap, disclosure scope, roles, reporting gaps and pay continuity. It uses a frozen starting graph so new connections cannot supply proof for their own acceptance. This is an assessment of every pair from available dataset evidence, **not a claim that every person received an individual internet or biography search**. Targeted professional checks and original-image reviews are identified separately.

Start with [every pair and its outcome](review-results.csv), the [summary](summary.json), or the [remaining evidence by employer](remaining-evidence.md). The [source follow-up list](original-source-follow-up.csv) groups names lacking a primary observation by employer and unverified compiled label, with located original schedules as leads. It distinguishes missing identity evidence from a missing report. No messages, requests, FOI applications or fees were sent.

## Adopted decisions

The [167 new decisions](../held-completion-reviewed.json) are distinct from the number of original candidate pairs connected: some repair a proposed name toward a third, correct spelling instead of accepting the originally suggested pair.

| Review method | Verified | Likely |
| --- | ---: | ---: |
| Personally read name and unique official remuneration row | 130 | 4 |
| Same ordered surname/initial letters, separator only | 17 | 0 |
| Official executive disclosures, biographies and appointment records | 4 | 3 |
| Restricted continuity assumption from primary observations | 0 | 9 |
| Total | 151 | 16 |

The unique-remuneration checks retain a compiled zero expense and a primary undisclosed expense as different values. They establish a reviewed name spelling, **not a complete financial match, verified compiled year, or permission to delete a row**. Nonzero unexplained expense discrepancies are blocked. The four North Vancouver City cases with conflicting initials are explicitly likely source-copy assumptions and require the same published position.

The ICBC separator decisions insert a comma between an otherwise identical printed surname and initials. No initial is expanded into a full given name. Multiple same-initial rows remain separate observations and may represent different people.

The nine continuity assumptions require an uncommon identifying feature beyond a common first name: complete multiple given names, a long distinctive full name, or a rare shared position. Primary periods must not overlap; compatible competing names, conflicting roles/scopes, long gaps and excessive pay changes block adoption. These connections are labelled likely in the app. Similar pay is supporting context, never proof of identity.

[Professional review](professional-review.json) covers Jim Pittman, Jessica McDonald, Jonathan Todd Bondaroff, Matthias Görges/Goerges and three qualified cases. It also records SFU exclusions: R. Dancy and R. D’Arcy are separate original rows, and O’Brian, M cannot be expanded to Mary Grantham O’Brien from an initial and similar surname. No identities are joined across employers.

## Pittman's currency and reviewed name

BCI's [2023/24 report, physical page 67](https://www.bci.ca/wp-content/uploads/2018/01/2023-2024-corporate-annual-report_financial-statements-1.pdf#page=67) identifies **Jim Pittman** and **USD 3,902,330** as executive total compensation. Its [physical page 92](https://www.bci.ca/wp-content/uploads/2018/01/2023-2024-corporate-annual-report_financial-statements-1.pdf#page=92) explicitly states that his 2023/24 compensation is in US dollars. A frozen [exact-observation annotation](../../record-annotations.json) identifies that compiled row by employer, period, name, position, remuneration, expense value, source and page.

The app connects both disclosed spellings under the reviewed name **Jim Pittman**, retaining every original spelling and value. It displays **US$3,902,330** with source evidence. That observation is excluded from CAD rankings, employer and position averages/medians, charts, raises and growth, including the Government salary panel. It remains accessible as an unranked observation. No exchange rate is assumed. The compiled expense's currency stays unverified. The 2017/18 compiled amount is different from the primary executive total and is not silently replaced.

The public root salary index points to `record-annotations.json`; consumers of the raw employer/people arrays must apply those exact-observation annotations before aggregating amounts. The raw array schemas and observations are preserved.

## Evidence and preservation

The primary agent personally read **153 original row crops on 16 sheets**, plus **six professional/currency PDF crops**. [The visual receipt](pay-visual-review.json), [pay manifest](pay-render-manifest.json), [professional manifest](professional-render-manifest.json) and source digests retain what was checked. Crops contain unretouched source pixels; the original PDFs remain the authority.

[Preservation checks](preservation-check.json) retain all **22,439 previous groups**, **24,283 existing relationships** and **1,430 verified local edges**. A local spelling correction does not make an uncertain path to a different canonical history verified. Historical review outputs are replayed against their frozen graph, while preservation checks use the live graph.

All **1,385,021 salary observations** remain: **1,156,657 official** and **228,364 compiled**. No amount, expense, reporting label, source definition or raw source row is rewritten. Derived CAD comparisons change for the single USD annotation. The BCI Trends crash when every payment exceeds the final pay-band boundary is also fixed and covered by a regression test.

## Reproduce

```sh
npm run build:salaries
npm run check:salaries
python3 scripts/assess_salary_name_queue.py --check
python3 scripts/review_name_connection_continuation.py --check
node --test scripts/held-name-connections.test.mjs src/salaries/recordAnnotations.test.js src/salaries/nameLinks.test.js
```

The build revalidates every adopted decision's complete observation fingerprints, source hashes, pages, unique remuneration witness and pinned review receipt. Changed evidence requires another review.

To reproduce images with PyMuPDF 1.26.6 and Pillow, place exact-hash PDFs in a separate cache as `<sourceId>.pdf` for pay crops and `<key>.pdf` for the six professional manifest entries, then run:

```sh
python3 scripts/render_held_name_evidence.py --cache /path/to/originals --out /tmp/held-review-reproduced
```

The renderer verifies every crop and contact-sheet hash and will not overwrite this reviewed evidence folder. The [validation receipt](validation.json) records 824 Python tests, 115 salary Node tests, all 15 reconciliation checks and 37 mobile/desktop browser checks. The PR records publication status.
