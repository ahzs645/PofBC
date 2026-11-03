# Community Living BC salary source follow-through

All 20 supplied official reports were downloaded from Community Living BC, matched to the supplied SHA256 fingerprints, and accepted as complete **named employee cohorts above $75,000**. The collection contains **3,218 employee rows**, including 147 rows in the two scanned reports. No reports remain held.

`dispositions.json` covers every input report ID. `sources.json` is the salary build collection manifest. Deterministic gzip files contain `[employerSlug, name, position|null, remuneration, expenses|null, physicalPdfPage]`. `inventory.json` preserves the supplied discovery metadata as input; its discovery statuses are superseded by the dispositions.

The 2005/06 schedule says “For the nine months ended March 31, 2006”; its actual period is **July 1, 2005–March 31, 2006**. The other reports disclose years/twelve months ended March 31. Periods were read from original schedule headings or rendered covers, never inferred from URL filenames.

Remuneration is the source's separate remuneration column. The combined Total column in early schedules is a check only. Employer CPP/EI, other benefits, under-threshold aggregates, reconciliation entries, board members and suppliers are excluded from employee rows. Positions are undisclosed and remain null. Original names and punctuation are retained, including initials and literal spelling. Dashes/blank expense cells remain null; numeric zero remains zero. Disclosed payments are not annual salary rates.

Every native employee row was independently extracted with **PyMuPDF positioned words** and **Poppler pdftotext -layout**. All 3,071 native rows agree in name, remuneration, expenses, optional combined total and physical page. All remuneration and expense controls reconcile exactly. Original rendered control/header regions were inspected for all 18 native reports; the 2005/06 schedule and 2009/10 scanned cover received additional visual review. Modern source wording distinguishes remuneration from separately reconciled employer benefits; the 2024/25 remuneration definition on physical page 36 was also inspected.

For 2008/09 and 2010/11, **every original employee name and monetary cell, every combined row total, the schedule boundary, reporting-period cover and named control was independently read from unmodified source pixels**. Tesseract psm4 and a grid-cleaned psm6 reading are diagnostic evidence; they share an OCR engine and are not represented as independent engines. The independent source-pixel reading resolves OCR errors such as `Grant,Paula NL` → `Grant,Paula N L`, `Scott,R lan` → `Scott,R Ian`, `luvancigh` → `Iuvancigh`, and Junvik's misread expense punctuation. All 147 individual combined totals and both complete cohort controls agree exactly, without monetary adjustment.

`proof/YYYY-YY.json` records reporting period evidence, controls, row counts per physical page, missing/zero distinctions and duplicate checks. `evidence/YYYY-YY-rows.json.gzip` preserves each independent native line pair, or the scanned-row source-pixel transcription and OCR variants. Scanned original/cleaned OCR text and the editable reviewed scan transcriptions are retained in this collection. Original PDFs and rendered review images are cached outside the repository at `/workspace/salary-source-follow-through/cache-clbc/`.

The duplicate check covers every registered source collection: no existing source fingerprint or normalized Community Living BC employee group matches these reports. Normalized groups compare sorted `[employerSlug, name, position, remuneration, expenses]` tuples, excluding page and row order. The 20 incoming groups also differ from one another. No compiled identities or edition labels were used to infer a reporting period, link people or replace compiled partitions.

| Period | Named employee rows | Remuneration | Known expenses | Employee physical pages |
| --- | ---: | ---: | ---: | --- |
| 2005/06 | 4 | $341,437.28 | $16,646.36 | 2 |
| 2006/07 | 40 | $3,650,059.74 | $356,301.70 | 2, 3 |
| 2007/08 | 53 | $4,946,102.36 | $569,721.12 | 2, 3 |
| 2008/09 | 64 | $6,041,134.62 | $484,861.09 | 2, 3 |
| 2009/10 | 68 | $6,512,147.10 | $566,910.85 | 2, 3, 4 |
| 2010/11 | 83 | $7,829,583.96 | $519,665.13 | 2, 3, 4 |
| 2011/12 | 81 | $7,563,653.00 | $471,464.00 | 21, 22 |
| 2012/13 | 91 | $8,440,053.00 | $523,503.00 | 19, 20, 21 |
| 2013/14 | 93 | $8,420,937.00 | $579,366.00 | 20, 21, 22 |
| 2014/15 | 108 | $9,755,595.00 | $564,162.00 | 20, 21, 22 |
| 2015/16 | 93 | $8,475,911.00 | $573,246.00 | 20, 21, 22 |
| 2016/17 | 108 | $9,790,202.00 | $615,904.00 | 21, 22, 23 |
| 2017/18 | 139 | $12,905,632.00 | $774,060.00 | 20, 21, 22, 23 |
| 2018/19 | 137 | $12,526,457.00 | $811,794.00 | 22, 23, 24, 25 |
| 2019/20 | 175 | $16,181,519.00 | $808,654.00 | 22, 23, 24, 25 |
| 2020/21 | 306 | $27,063,316.00 | $188,783.00 | 23, 24, 25, 26, 27, 28, 29 |
| 2021/22 | 302 | $27,078,682.00 | $289,769.00 | 23, 24, 25, 26, 27, 28, 29 |
| 2022/23 | 299 | $27,012,351.00 | $576,419.00 | 22, 23, 24, 25, 26, 27, 28 |
| 2023/24 | 453 | $44,948,675.00 | $993,667.00 | 22, 23, 24, 25, 26, 27, 28, 29, 30, 31 |
| 2024/25 | 521 | $51,053,923.00 | $1,094,031.00 | 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35 |

All row-sum residuals against the printed named remuneration and expense controls are zero.

Reproduce with Python 3, PyMuPDF, Pillow, NumPy, SciPy, Poppler `pdftotext`, and Tesseract:

```sh
python scripts/follow_through_clbc.py --cache /workspace/salary-source-follow-through/cache-clbc
python scripts/test_follow_through_clbc.py
```

The importer fetches only public PDFs, validates the immutable fingerprints, reuses cached OCR, and writes only this collection. On an empty cache it renders scan pages and runs OCR sequentially with `OMP_THREAD_LIMIT=1` and `OMP_NUM_THREADS=1`; reviewed source-pixel transcriptions remain required audit inputs. No contact forms, requests, fees, messages or outreach were used.
