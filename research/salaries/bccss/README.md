# BCCSS employee disclosure

**Employer decision:** BC Clinical and Support Services Society is a separate
reporting employer (`bc-clinical-and-support-services-society`). Its 2016/17
financial statement describes the society and the April 1, 2016 start of
operations after a transfer of services from PHSA (physical PDF page 16). Hosting
the report on PHSA's website does not turn it into PHSA's employee schedule.

The 2016/17 import contains **306 named employee records**, on physical PDF pages
48–53. Both Poppler layout extraction and independent PyMuPDF positioned-word
extraction agree for every name, amount and page, in the original order. All six
employee pages and the reporting-entity note were visually reviewed. Remuneration
reconciles exactly to **$28,855,034**, and numeric expenses to **$958,981**.

The source's sixty expense dashes remain `null`; they are not invented zero
payments. Page 47 board remuneration and the below-threshold/overall summary rows
are excluded. The employee subtotal explicitly says **equal to or greater than
$75,000**, so this source's threshold is inclusive. The next year's different
heading must retain its own comparison rule.

Source: [2016/17 BCCSS SOFI](https://www.phsa.ca/about-site/Documents/BCCSS%20Statement%20of%20Financial%20Information%202016-17.pdf).
Exact source and normalized hashes, row counts, totals, page boundaries and the
employer decision are in `sources.json`.

Reproduce with the original PDF:

```bash
python3 scripts/import-bccss-salaries.py --pdf /path/to/bccss-2016-17.pdf
```

The importer requires PyMuPDF and Poppler. The report-specific source hash, row
boundaries and controls fail closed. Any new report version needs review first.
The separate 2017/18 scanned report is handled in the `bccss-ocr` collection.
