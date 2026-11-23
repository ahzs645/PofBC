# Statistics Canada verification — 22 November 2026

## Result

The apparent 1984/1986 and 1985/1987 date conflict is resolved: the volumes were published later and expressly carry newer appendix snapshots. The material correction is the second British Columbia page locator: **printed page 103**, not 102.

| File reference year | Publication date on title page | Appendix as-at date | British Columbia pages |
|---|---|---|---|
| 1984 | May 1987 | 31 December 1986 | Printed 143–144; PDF pages 145–146 |
| 1985 | June 1988 | 31 December 1987 | Printed 103; PDF page 105 |

The archived originals were downloaded, extracted, rendered and visually inspected. The exact dates above appear on the scanned title and appendix pages. All PDF page numbers in this report are one-based.

## Check 1: acquisitions, incorporation year and Vancouver Island Transit

**T.S. Holdings.** Retain **1975**, with the description “incorporation year reported by Statistics Canada.” The 1976 issue, printed page 22 (PDF 24), places that value in the incorporation-year column. The 1975 issue also gives it on page 22. Its page 27 describes the transport holding role; that paragraph itself does not give a start date. No day or month was verified. [S75] [S76]

**Panco.** The 1975 issue, page 27 (PDF 29), confirms the Province acquired all issued common and preferred shares in **February 1975 for CAD 4.8 million**. It describes B.C. Testing Farms, Pacific Hatching and Western Feeds as wholly owned subsidiaries. Keep month precision for this Statistics Canada assertion. For the final event, the companion identity review supplies the more precise acquisition date, **17 February 1975**, from the 1978/79 Public Accounts, F215. The enterprise table's 1974 value is a separate incorporation-year assertion; it does not contradict the 1975 provincial acquisition. [S75]

**Venture Realty.** The 1978 issue, page 26 (PDF 28), confirms a sale during the reporting year and an ongoing Housing Corporation windup. The source uses **Venture Realty**. That paragraph supplies neither an exact sale day nor a registry identifier establishing equivalence with **Ventures Realty Ltd.** The Housing fiscal-year-end column is October 31, on page 22. The direct Housing statements subsequently checked in the companion identity review supply an effective sale date of 30 November 1978 (1978/79 Public Accounts, F154). This is a subsequent event after the 31 October statement year-end. [S78; ID-S06]

**Vancouver Island Transit.** Catalogue 72-007, volume 23 number 1 covers **January–March 1981** and was published in **September 1981**. Printed page 37 (PDF 39) calls it a consolidated subsidiary. Visual inspection shows no parent named in its row. The preceding T.S. Holdings row does not establish ownership. Add a 1981-Q1 roster observation; that row alone leaves its parent unresolved and supplies no incorporation date. The separate 1978 accounts establish its T.S. Holdings parent at the earlier checkpoint; see the transit findings below. [S81Q1]

## Check 2: usable observations and limits

The two appendices list **Peace Power Constructors** at level 02 under Hydro; **Dunhill Development** and **HCBC Construction** at level 02 under Housing Corporation. These are reported ownership observations on 1986-12-31 and 1987-12-31. They do not show incorporation dates or prove uninterrupted ownership between observations. [S84] [S85]

Identity must be integrated with the separately verified Public Accounts: the later Dunhill is the renamed W.K.P. Construction; HCBC is renamed Fisher Developments. Creating separate legal-entity nodes for those renamed companies would duplicate them.

**Date verification does not certify every roster row.** The 1984 appendix marks **Surrey Farm Products Investments Ltd.**, **Western Feed Co. Ltd.** and **Pacific Hatchery Ltd.** as inactive level 01 entities. It places the Duke Point rows after an anomalous Ocean Falls/First Capital sequence across pages. The code legend distinguishes direct entities, subsidiaries and deeper subsidiaries; special-fund headings require separate attention. [S84] [S85]

A concrete staleness example is **British Columbia Cellulose Company**, still included in the roster headed 31 December 1986. The companion ownership review, **OWNERSHIP_FINDINGS.json, claim OWN-C09 and sources OWN-S05–OWN-S07**, reports a March 1986 repeal and an April 1986 accounts dissolution. That review preserves the unresolved one-day boundary between the two dates. This review verifies the later roster row; the legal and accounts dates are attributed to that separate review. Keep the raw roster and resolve legal conflicts using direct audited statements, registry records and legal instruments.

A useful earlier source: the 1981-Q1 issue, printed page 36 (PDF 38), already lists **Duke Point Terminals** as a consolidated subsidiary within the BCDC grouping and names **Discovery Park Industries**. This moves their statistical-source observation earlier than 1986, without establishing legal start dates or Discovery identity continuity. [S81Q1]

## Sources and reproducibility

The original publications site returned oversized-document errors to the web opener, while shell downloads returned HTML. Library and Archives Canada mirrors supplied the complete PDF bytes. Rendered pages were read directly; screenshot calls that returned only textual placeholders were not treated as visual verification.

### S75 — Provincial government enterprise finance, 1975

[Original PDF](https://publications.gc.ca/collections/collection_2016/statcan/61-204/CS61-204-1975.pdf) · [Working archived PDF](https://epe.lac-bac.gc.ca/100/201/301/weekly_acquisitions_list-ef/2016/16-06/publications.gc.ca/collections/collection_2016/statcan/61-204/CS61-204-1975.pdf?nodisclaimer=1)

Published 1978-05; evidence printed pages 22, 27; PDF pages 24, 29. SHA-256: `f14b14872fe517c17bd355db495860406b61420ecc242b67af5ec4e15e0209b0`.

### S76 — Provincial government enterprise finance, 1976

[Original PDF](https://publications.gc.ca/collections/collection_2016/statcan/61-204/CS61-204-1976.pdf) · [Working archived PDF](https://epe.lac-bac.gc.ca/100/201/301/weekly_acquisitions_list-ef/2016/16-06/publications.gc.ca/collections/collection_2016/statcan/61-204/CS61-204-1976.pdf?nodisclaimer=1)

Published 1979-05; evidence printed pages 22; PDF pages 24. SHA-256: `83b81498c2654d148a5792d12cd4f4d0da11fb55a7fb2ae062ec01f692975c92`.

### S78 — Provincial government enterprise finance, 1978

[Original PDF](https://publications.gc.ca/collections/collection_2016/statcan/61-204/CS61-204-1978.pdf) · [Working archived PDF](https://epe.lac-bac.gc.ca/100/201/301/weekly_acquisitions_list-ef/2016/16-06/publications.gc.ca/collections/collection_2016/statcan/61-204/CS61-204-1978.pdf?nodisclaimer=1)

Published 1981-05; evidence printed pages 22, 26; PDF pages 24, 28. SHA-256: `53a4f43452f36c56a64e5193d031b00488d8033d2bffb33f0dff27daa78f4fda`.

### S84 — Provincial government enterprise finance, 1984

[Original PDF](https://publications.gc.ca/collections/collection_2016/statcan/61-204/CS61-204-1984.pdf) · [Working archived PDF](https://epe.lac-bac.gc.ca/100/201/301/weekly_acquisitions_list-ef/2016/16-06/publications.gc.ca/collections/collection_2016/statcan/61-204/CS61-204-1984.pdf?nodisclaimer=1)

Published 1987-05; evidence printed pages 143, 144; PDF pages 145, 146. SHA-256: `1234d00fbe8d12af6b9b74c43086f811350f3816265feef87c5696f0ed90de91`.

### S85 — Provincial government enterprise finance, 1985

[Original PDF](https://publications.gc.ca/collections/collection_2016/statcan/61-204/CS61-204-1985.pdf) · [Working archived PDF](https://epe.lac-bac.gc.ca/100/201/301/weekly_acquisitions_list-ef/2016/16-06/publications.gc.ca/collections/collection_2016/statcan/61-204/CS61-204-1985.pdf?nodisclaimer=1)

Published 1988-06; evidence printed pages 103, 104; PDF pages 105, 106. SHA-256: `a73689cd59b22a686cd0ada2e719ea1487d119529abfc43f582ef5e20f4bba4a`.

### S81Q1 — Provincial government employment, 1981-Q1

[Original PDF](https://publications.gc.ca/collections/collection_2015/statcan/72-007/CS72-007-23-1.pdf) · [Working archived PDF](https://epe.lac-bac.gc.ca/100/201/301/weekly_acquisition_lists/2015/w15-50-F-E.html/collections/collection_2015/statcan/72-007/CS72-007-23-1.pdf?nodisclaimer=1)

Published 1981-09; evidence printed pages 36, 37; PDF pages 38, 39. SHA-256: `db744c98a787181dec54f07609f2ea41182d1d835b5e064a86f6674096bd8ad7`.

## Integration cautions

Use the source register to keep three dates distinct: financial reference period, actual publication date and appendix snapshot. A report about 1978 may be published in 1981; a 1984 financial volume may describe a 1986 roster. Preserve uncertainty in identity and legal status separately from certainty about what the source printed.

## Subsequent direct-statement evidence: transit subsidiaries

See **TRANSIT_FINDINGS.md** and **TRANSIT_FINDINGS.json**. The 1977/78 Public Accounts, F220, note 1(a), identify Vancouver Island Transit Ltd. as a wholly owned T. S. Holdings subsidiary at **31 March 1978**. This supplies the parent relationship that the 1981-Q1 statistical roster does not state. The same evidence also identifies Thompson-Okanagan Transit and V I T Holdings as wholly owned subsidiaries. The source-limited findings above are preserved.
