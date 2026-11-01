# Government, police and regional-district continuation

As of 2026-11-01: **32 verified cohorts / 22,471 observations**; **0 held cohorts / 0 candidate observations**. The collection contains 32 cohorts from 25 distinct official originals. `sources.json` is the acceptance boundary; held sources are excluded from ingestion.

| Scope | Periods | Rows |
|---|---|---:|
| BC Public Accounts Other Employees | 1999/00, 2000/01, 2001/02, 2002/03, 2003/04, 2004/05, 2005/06 | 13450 |
| BC Public Accounts OIC/appointees | 1999/00, 2000/01, 2001/02, 2002/03, 2003/04, 2004/05, 2005/06 | 8602 |
| Vancouver Police executives only | 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024 | 142 |
| Alberni-Clayoquot employee schedules | 2019, 2020, 2023, 2024, 2025 | 122 |
| East Kootenay surname-only employees | 2023, 2024, 2025 | 155 |

The seven Other Employees histories 1999/00–2005/06 extend existing official core-government employee coverage continuously back to 1999/00. Published same-row travel is retained in the first four years; 2003/04 onward is salary-only, so expenses remain null. OIC/appointees are a distinct scope, with no cross-schedule travel join. Four literal negative OIC salary cells and wrapped/no-comma surname anomalies are preserved and warned. Deputy, minister and MLA compensation remain separate processing tasks.

Vancouver Police 2015–2024 is executive-only. Every one-page original was rendered and reviewed completely. Expense dashes remain null and the three explicit zero cells in 2022 remain zero. The 2014 executive release lacks a full reporting-period statement and is held outside this normalized collection; 2025 is an image-only processing lead. Existing staff FOI releases preserve redactions and require separate processing. The newly located Victoria Police 2024 original publishes title/pay/expense with no name field; direct download returned 503 and its public retrieval is still a processing task.

ACRD 2019, 2020, 2023, 2024, 2025 named employee pages and every control/reconciliation page were rendered completely. Its index 2022 link returns the identical 2023 original; no 2022 cohort is inferred. 2021 has corrupt native character mapping and needs decoding/OCR. Source-control residuals are exposed exactly, with no balancing or explanation invented. East Kootenay 2023–2025 contains surnames only; every employee/control page was rendered completely. Gross earnings exclude the separate employer-paid benefit aggregates, and dashes remain unknown.

Every named row, title where published, money cell, physical page and multiplicity agrees across independent native readers. Employee/ACRD/East Kootenay/VPD tables use PyMuPDF and Poppler; OIC tables use PyMuPDF and PDFMiner because Poppler fixed-pitch output collapses initials on a wrapped surname. Complete extracted word/text evidence permits both readers to be replayed offline. The independent Crown worker additionally reviewed all 13,450 early employee rows,122 ACRD rows and 155 East Kootenay rows. The education worker independently reproduced all 8,602 OIC rows with a third engine. Source/control disagreements remain visible; the parent accepted the literal values after original-scope/control review, and source metadata links the independent receipts.

Reproduce without changing any payload:

```sh
python scripts/continue_government_police.py --verify-originals --cache /tmp/continuation-government-police
python scripts/continue_government_police.py --check-data
python scripts/test_continue_government_police.py
```

Use `--fetch` with the ordinary build command to retrieve missing pinned originals; an original hash change stops extraction. `--refresh-metadata` replays existing evidence and changes only the manifest after an explicit documented review decision. All gzip payloads use deterministic mtime=0.

Exact original/data/evidence hashes, cache paths, pages, row counts and source-specific warnings are in [the handoff](../continuation-2026-11-01/government-police/handoff.json). Original PDFs stay in `/tmp/continuation-government-police`. Payload/evidence hashes are frozen in `frozen-batch-1.json`. No old collection, aliases, shared registry, compiled data, app/public outputs or external messages were changed by this worker.
