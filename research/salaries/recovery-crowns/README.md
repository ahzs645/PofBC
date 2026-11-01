# BC Assessment and BC Energy Regulator employee originals

Eight complete official employee schedules add **2,691 observations**: BC Assessment calendar 2020 and FY2021/22–2024/25 (1,908), and BCER FY2023/24–2025/26 (783). Three independent readers compare every literal name, pay, expense, physical page and row boundary, preserving duplicate multiplicity. Approval and source-control pages are rendered and independently reviewed. Full evidence and exact cache paths are in [source-specs.json](../recovery-wave-2026-11-01/crowns/source-specs.json).

| Employer / period | Rows | Remuneration | Known expenses | Named control residual pay / expenses |
| --- | ---: | ---: | ---: | ---: |
| BC Assessment 2020 | 362 | 34,830,265 | 532,750 | 0 / 0 |
| BC Assessment 2021/22, fifteen months | 359 | 43,024,330 | 714,013 | 0 / 0 |
| BC Assessment 2022/23 | 382 | 39,153,289 | 1,056,265 | −1 / +7 |
| BC Assessment 2023/24 | 394 | 41,844,959 | 1,231,964 | −3 / +13 |
| BC Assessment 2024/25 | 411 | 44,664,847 | 1,405,463 | +7 / +21 |
| BCER 2023/24 | 249 | 28,973,613 | 1,405,173 | 0 / 0 |
| BCER 2024/25 | 257 | 30,683,576 | 1,167,816 | +3 / +2 |
| BCER 2025/26 | 277 | 32,865,486 | 900,606 | 0 / 0 |

## Source definitions and controls

BC Assessment 2020 and 2021/22 define remuneration using salaries paid in **T4 Box 14**, including wages, vacation payouts and taxable benefits. FY2022/23 uses FIR remuneration whether or not income-tax reported; FY2023/24–2024/25 explicitly add bonuses, gratuities, trust/deferred-income payments and exclude anything payable under a severance agreement. These changing definitions must accompany comparisons; figures are not base annual salary rates.

The **2021/22 transition is fifteen months, January 1, 2021–March 31, 2022**. Its published total remuneration is used without annualization. Calendar2021 and January–March2022 components remain in provenance, including eleven unknown quarter components. Their missing values are not inferred as 0. The schedule separately consolidates employees above $75,000 in fifteen months but below $75,000 in twelve; that group is excluded from named observations. Known negative expense amounts remain literal, with no inferred cause.

Calendar2020's named controls are derived from explicitly numeric all-employee totals minus the under-threshold aggregate. The transition subtracts both explicitly numeric consolidated groups. Later BC Assessment and all BCER sources print named-over-threshold controls directly. Employer CPP/EI, under-threshold payroll, board schedules, suppliers and accrued/secondment aggregate adjustments are excluded from individual remuneration/expenses.

Exact source-control residuals remain public warnings and unsent clarification tasks. Broader source subtotal/grand-total arithmetic differences are independently retained in [the peer controls receipt](../recovery-wave-2026-11-01/reviews/independent-crowns-pdfminer-comparison-and-controls.json); they are not asserted to explain named-row residuals. No printed amount is changed to make a total match. Initials in 2020 remain initials; later full names are not substituted. These employee schedules publish no job titles.

## Compiled copies

All 362 BC Assessment compiled observations labelled 2020/21 match the actual calendar 2020 complete employee schedule. A hash-pinned [calendar replacement rule](../recovery-wave-2026-11-01/crowns/calendar-replacement.json) removes that whole proved copy. BC Assessment 2023/24 (394) and BCER 2023/24 (249) also match their same-fiscal originals completely. Only documented case/punctuation and compiler 0/source-null expense presentation are set aside for comparison; the published original retains null expenses. No unmatched board observations or earlier compiled 2017/18 records are deleted. All 1,005 Crown replacements are [independently reviewed](../recovery-wave-2026-11-01/reviews/independent-crowns-compiled-overlap-decision.json).

BCER's predecessor Oil and Gas Commission identity and unprocessed older originals remain a separate task; this wave does not create a canonical alias or guess older reporting dates.

## Reproduce

```sh
python3 scripts/recover_wave_crowns.py --fetch --verify
python3 scripts/recover_wave_crowns.py --offline --verify
python3 -m unittest discover -s scripts -p test_recover_wave_crowns.py
```

Original-backed replay requires Poppler and PyMuPDF; `--fetch` retrieves only missing pinned PDFs and rejects changed hashes. Offline replay uses committed positioned-word and independent Poppler evidence. A third PDFMiner original-only transcription, every component vector, signed approval/date, source-definition and control comparison are retained in the new peer receipts. See [the wave review](../recovery-wave-2026-11-01/README.md) for exact baseline preservation and updated source-copy tasks. No institution was contacted and no FOI or fee incurred.
