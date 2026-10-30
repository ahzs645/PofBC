# Columbia Hydro Constructors Ltd.

BC Hydro's Financial Information Act returns carry a separate employee schedule for its subsidiary
Columbia Hydro Constructors Ltd. (report FI308), after BC Hydro's, Powerex's and Powertech's. The
Hydro collection did not import it (`../hydro/sources.json`, `otherEmployeeSchedulesNotImported`);
this collection does, as its own employer, `sub-columbia-hydro-constructors`, the BC Hydro
subsidiary of the government atlas.

| Year | Named rows | Remuneration | Expenses | Residual (rows − printed named total) | PDF pages |
|---|---:|---:|---:|---:|---|
| 2012/13 | 190 | $19,718,574 | $1,089,407 | +$1 / $0 | 172–175 |
| 2013/14 | 226 | $23,588,724 | $1,369,304 | +$3 / −$2 | 163–167 |
| 2014/15 | 239 | $25,533,054 | $1,370,304 | −$3 / +$2 | 167–171 |
| 2015/16 | 63 | $6,651,654 | $394,765 | +$3 / −$3 | 169–170 |
| 2016/17 | 5 | $485,097 | $30,673 | −$1 / +$1 | 170–171 |
| 2017/18 | 0 | — | — | aggregate only | 175 |

The printed named total is the schedule's Total less its consolidated total of employees paid
$75,000 or less. The employer's EI and CPP line is printed below Total and is not part of it. The
residuals are left as published.

Names are published as initials then surname ("PR Adams") and are stored as BC Hydro's are
("Adams, PR"). Initials are not expanded. Positions are not published. Repeated names stay
separate rows: 2014/15 has two JW Anderson rows ($146,855 and $93,162).

In 2017/18 the schedule names no employee over $75,000: its $208,410 remuneration and $12,021
expenses are all in the below-threshold aggregate. No rows are imported for that year, and the
salary pages say so rather than suggesting the company had no employees.

## Evidence and reproduction

The rows come from the staged captures in [`../chc-recovery/`](../chc-recovery/README.md). They
were accepted on the original-PDF check in
[`../chc-recovery/pdf-verification/`](../chc-recovery/pdf-verification/review.json): matching PDF
hashes, every row found by two PDF readers, summary columns read from page coordinates, and all
19 schedule pages reviewed as rendered images.

```sh
python3 scripts/stage_chc_recovery.py          # captures to staged candidates
python3 scripts/check_chc_pdf.py --capture research/salaries/chc-recovery/captures/2014-15.json \
  --pdf /path/to/financial-information-act-return-march-31-2015.pdf --output /tmp/check.json
python3 scripts/accept-chc-salaries.py         # verified candidates to this collection
npm run build:salaries && npm run check:salaries
```

`accept-chc-salaries.py` refuses a year whose capture changed after its PDF check, or whose check
found a missing or extra row.
