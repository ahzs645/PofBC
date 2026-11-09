# Salary coverage roadmap, 9 November 2026

A review of the live salary pages and the public-sector disclosure landscape, with what each
remaining gap would take to close. The review's interface findings were addressed in the same
change (page titles, threshold-aware statistics, inflation adjustment, search ranking, the Council
pay and Workforce sections, the About page, downloads). This file covers the data.

Coverage at the start of the review (from `public/salaries/coverage.json`): 1,445,458 records,
276 employers, 1999/00–2025/26; 84% from employer reports, the rest from the retained
compilation.

## Imports started in this review

| Batch | Directory | Why |
|---|---|---|
| Vancouver School District, older years | `vsb-history/` | The compiled 2017/18, 2020/21 and 2023/24 partitions have damaged names (lost hyphens and spaces, e.g. "HorsleyHoi will, Joann"); an official import replaces the compiled partition. |
| Regional districts | `regional-districts/` | Only 3 of B.C.'s 27 regional districts were covered. |
| Municipal years marked "source found" | `source-found-municipal/` | 58 employer-years had a located report that was never extracted (Nelson 2011–2024, Prince Rupert 2016–2024, and others). |

Each batch's README records what was accepted, what was held, and why.

## Gaps and where the sources are

### School district history (42 of 60 districts have only 2024/25)

gov.bc.ca now keeps only the latest school district SOFIs: `…/financial-information/sdNN-sofi-2025.pdf`
answers, and the 2023 files that search engines still index return 404. Earlier years must come
from each district's own website (most post several years) or a web archive. Districts file within
six months of the June 30 year end, so the 2025/26 files appear in December 2026–January 2027. These
are worth capturing as they are published, before the next year replaces them.

### Regional districts

All local governments must prepare an annual SOFI, but there is no central index. The ministry's
Local Government Statistics schedules hold aggregate finances only. Each regional district posts its
own PDFs, generally on a finance or "financial reports" page.

### Nicola Valley Institute of Technology

NVIT is the only public post-secondary institution with no records here. No SOFI is published on its
site or gov.bc.ca, which hosts only its audited financial statements. Its executive compensation
disclosures are published (e.g. 2012/13 at publicsectorcompensation.gov.bc.ca). The employee
schedule probably needs a request to NVIT or a freedom-of-information request.

### Executive total compensation (all Crown corporations, health authorities, universities and colleges)

The Public Sector Employers' Council publishes, every year since 2007/08, the CEO's and the next four
executives' base salary, incentive pay, benefits, pension and other pay, with a board-chair
attestation. Index: `https://www.publicsectorcompensation.gov.bc.ca/executive-compensation-disclosures/YYYY-YYYY`
(overview on gov.bc.ca under Public Sector Management → Compensation → Executive compensation
disclosures). They are per-employer PDFs with no CSV. This is the only source with pension and
benefits, which the FIA remuneration figures leave out, so it would suit a companion section like
Council pay rather than the employee records.

### Physicians' MSP payments (the "Blue Book")

The Medical Services Commission financial statement lists payments to each practitioner. It is
probably the largest public payment disclosure not covered here. CSV for 2013/14–2023/24 is in the B.C.
Data Catalogue (Payments to Medical Practitioners), and the 2024/25 PDF is at
`https://www2.gov.bc.ca/assets/gov/health/practitioner-pro/medical-services-plan/blue_book_2024-25.pdf`.
These are gross billings to practitioners and clinics, not salaries, so they need their own section
and definitions. PharmaCare publishes aggregate trends only, with no per-pharmacy payments.

### Judges and Officers of the Legislature

Statutory rates rather than named schedules: Provincial Court judge $377,116.92 and Chief Judge
$422,370.90 from April 1, 2026 (government salary lookup tool). The Judicial Compensation Commission
reports every four years (2022 report on gov.bc.ca). Officers of the Legislature are tied by statute
to the Chief Judge's salary. The same salary lookup tool publishes the pay range of every B.C. Public
Service classification, which could add "pay band" context to Public Service records.

### Bodies outside the Financial Information Act

BC Ferries and the B.C. Investment Management Corporation (BCI) are exempt from FIA compensation
disclosure. BC Ferries publishes executive pay under the Coastal Ferry Act. The Vancouver Fraser
Port Authority is federal, under the Canada Marine Act. Records for these come from other
disclosures and should be labelled as such, so their absence from an employee schedule is not read
as a gap.

### Held for review (do not override)

Several located reports fail reconciliation and are deliberately held: for example BC Hydro and
Powerex 2024/25 (printed named rows do not reconcile to the printed totals), Island Health 2022/23
(the narrative declares 12 more rows than the table holds) and 2023/24 (an expenses subtotal $45,772
off). Each needs a corrected schedule or confirmation from the issuer; no values should be inferred.

## Threshold history to confirm

The $75,000 threshold dates from B.C. Reg. 249/2002 and has not been amended since (the regulation's
last amendment is B.C. Reg. 153/2018; it has no indexing). Press reports say the earlier threshold was
$50,000, but a primary source has not been found. The 1999/00–2001/02 Public Accounts schedules would
settle it. They would also explain why the 1999/00 Public Service year has only 2,342 records, 983 of
them under $75,000.

## Comparable sites, for reference

Ontario's official Sunshine List publishes CSVs from 1996 onward. canadasunshinelist.ca has
distributions, a "where would you rank" tool, and corrections and removal pages. The Texas Tribune
salary explorer offers full CSV, per-position medians, flags for anomalous changes, and individual
pages only above the median. Transparent California offers search and spreadsheet downloads. This
site now has rankings, downloads, anomaly flags and a corrections page; per-classification pay bands
and the executive total-compensation overlay remain.
