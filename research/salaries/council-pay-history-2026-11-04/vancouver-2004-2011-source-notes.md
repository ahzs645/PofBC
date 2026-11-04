# Vancouver council payments, 2004–2011

Retrieved on 2026-11-04. The companion JSON contains 104 annual payment rows across eight years, with four components per row: remuneration, local expenses, transportation allowance, and travel/conferences. The source reports actual payments; the data must not be interpreted as an annual base salary schedule.

## Primary tables and coverage

| Year | Rows | Primary source | Physical PDF page | Printed column controls |
| --- | ---: | --- | ---: | --- |
| 2004 | 11 | [2004 SOFI](https://vancouver.ca/files/cov/FI2004.pdf) | 40 (printed SOFI page 6) | All four exact, to the cent |
| 2005 | 18 | [Annual report](https://council.vancouver.ca/20060516/documents/a6.pdf) | 2 | Two exact; remuneration −$2, transport +$3 |
| 2006 | 11 | [Annual report](https://council.vancouver.ca/20070503/documents/cs1.pdf) | 2 | Remuneration +$1, local −$1, transport +$1, travel −$1 |
| 2007 | 11 | [Annual report](https://council.vancouver.ca/20080429/documents/a7.pdf) | 2 | All four exact |
| 2008 | 16 | [Annual report](https://council.vancouver.ca/20090324/documents/a3.pdf) | 2 | All four exact |
| 2009 | 11 | [Annual report](https://council.vancouver.ca/20100323/documents/a3.pdf) | 2 | All four exact |
| 2010 | 11 | [Replacement annual report](https://council.vancouver.ca/20110405/documents/a2.pdf) | 2 | Remuneration +$2, local −$1, transport −$1, travel −$2 |
| 2011 | 15 | [Annual report](https://council.vancouver.ca/20120327/documents/a3.pdf) | 2 | Two exact; local −$1, transport −$1 |

Differences are **sum of disclosed cells minus printed total**. All 416 primary numeric cells are retained as reported. There are 20 exact column controls and 12 small differences at whole-dollar precision. Every difference, source total, calculated sum, and nearest-dollar rounding bound is explicit in the JSON. Cells were never altered to force equality.

## Source verification and precision

The [2005 SOFI](https://vancouver.ca/files/cov/FI2005.pdf), physical page 44, reproduces the 2005 table's values and totals. The [2010 SOFI](https://vancouver.ca/files/cov/FI2010.pdf), physical page 46, and [amended 2011 SOFI](https://vancouver.ca/files/cov/2011-statement-of-financial-information.pdf), physical page 46, likewise corroborate their annual tables. The city's [financial-report index](https://vancouver.ca/your-government/financial-reports-and-information.aspx) identifies the 2011 SOFI as amended.

For 2006, every annual-report cell and printed total was checked again against the official PDF's indexed table. The separate SOFI's text extraction was not usable. The explanation that individual figures and the aggregate were rounded independently is therefore an **inference**, not a claim of a recovered cent-level reconciliation. The same qualification applies to other unmatched columns whose underlying cents are unavailable.

The 2010 report supplies stronger evidence for the travel column. Its Appendix A, physical pages 3–4, gives exact-cent person totals summing to **$73,089.62**. Each rounds to the annual table's corresponding travel amount, and the aggregate rounds to its printed **$73,090**. Summing the rounded person amounts yields **$73,088**. Both representations are retained. The 2011 appendix similarly sums to **$55,988.82**, which rounds to **$55,989**; all eleven corresponding person totals were checked. Appendix amounts are verification evidence, not additional payment rows.

The 2004 SOFI supplies all four columns to the cent and reconciles exactly. Its corresponding [whole-dollar annual report](https://council.vancouver.ca/20050524/documents/a4.pdf), physical page 2, is preserved in `sourceComparisons`. All 44 person-level cells match nearest-dollar rounding. However, that annual report prints a travel total of **$47,666**, whereas the SOFI total **$47,666.66** rounds to **$47,667**. This source-edition discrepancy remains explicit. The cent-precision SOFI is the primary 2004 table.

The transcription was made from the official PDFs' retrievable text. Direct PDF downloads returned HTTP 403; no local visual inspection is claimed.

## Roles, terms, and component treatment

The 2005 report prints **Sullivan, S.** in two distinct groups: mayor for the 2005–2008 term and councillor for 2002–2005. Both rows survive, with distinct `sourceRowKey` values and the printed term labels. The 2005 and 2008 tables each include two mayors because office changed during the reporting year. Election-year figures are not annualized.

Asterisks denote membership in the 2005–2008, 2008–2011, or 2011–2014 council. They do not mean every payment covers an entire new term. Original row labels and notes preserve this distinction. The 2011 table uses explicit dashes for zero amounts; these remain visible in the raw rows. No empty cell was converted into zero.

Expense totals include all three reported expense components, including the separate transportation allowance. Councillor remuneration includes deputy-mayor work. The source's expense caps and allowance definitions are paraphrased in `sourceFootnotes`; travel/conferences are net of recoveries. The 2010 source is expressly a replacement report.

## Validation

An independent Decimal-based check recomputed all 32 primary column totals and differences, verified all 104 row identities and roles, checked both Sullivan groups, verified all 44 rounded 2004 comparison cells, and reconciled the 22 exact-cent appendix person totals for 2010 and 2011. No requested year was omitted. No existing repository table, generated export, builder, or identity index was changed by this extraction.
