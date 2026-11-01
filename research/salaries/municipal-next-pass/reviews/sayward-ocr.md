# Independent full image review: Sayward 2024

Decision: **passes for all nine named observations**, with the existing unresolved council-expense warning retained. This is a separate reviewing agent’s complete reading of the rendered original image, not an independent OCR engine. No source collection or importer was edited.

Original official PDF: `https://www.sayward.ca/sites/sayward.ca/files/2026-05/2024%20SOFI%20Package%20-%20signed.pdf`. Original SHA-256: `03d0899a20d184af02094d0832a07d52294affe955737d9cdac9d6060a5475e2`. The original PDF has eight pages and no text layer. The actual reporting year is 2024, confirmed by the physical 1 management report heading **year ending December 31, 2024**, physical 3 remuneration schedule **for 2024**, and physical 7 approval signed **May 6, 2025** by CFO Lisa Clark and Mayor Mark Baker. The 2026 upload path does not change the reporting period.

## Complete independent transcription

Every name, title, remuneration and expense below was read from physical PDF page 3 and compared with both normalized cohorts and `review/sayward-2024-ocr.json`.

| Name as disclosed | Position | Remuneration | Expenses |
| --- | --- | ---: | ---: |
| Baker, Mark | Mayor |10,540|28|
| Burchett, Scott | Councillor |8,140|6,434|
| Coates, Debbie | Councillor |2,820|28|
| Gilkin, Kohen | Councillor |1,760|0|
| Johnson, Jason | Councillor |2,820|4,127|
| Poulsen, Sue | Councillor |7,920|6,259|
| Tinsley, Tom | Councillor |4,780|0|
| Gervais, Keir | Chief Administrative Officer |77,389|77|
| Read, Colin | Public Works Manager |100,279|1,239|

The first seven observations form the elected-official schedule; the final two are the complete named employee cohort headed **Employees earning more than $75,000 per year**. Council rows have no employee threshold. The two expense zeroes are visibly numeric 0, not blanks/dashes, and remain zero. There are no missing or negative monetary cells among the nine named rows. Printed below-threshold/overall aggregates are not individual salary observations.

## Controls and OCR repair review

Employee rows sum exactly to printed remuneration **177,668** and expenses **1,316**. Council remuneration sums exactly to printed **38,780**. Council expenses sum to **16,876**, while the printed subtotal is **16,877**: the −$1 row-minus-control difference is real and remains unresolved. The published council warning preserves the row values. Printed council 16,877 + employee 1,316 + below-threshold 9,963 explains the printed overall 28,156; this does not justify altering any named expense cell.

The five guarded repairs in the 250 dpi/PSM 6 reading are image-grounded: Baker’s expense 28, Coates’s expense 28, Gilkin’s expense 0, Tinsley’s expense 0 and Gervais’s expense 77. The 300 dpi/PSM 3 reading captures these cells directly. The retained two Tesseract configurations are correctly described as the **same OCR engine**. Their outputs/guards match the complete independently checked image transcription; names and amounts were not changed to balance a subtotal.

## Verified artifacts

* Reviewed OCR receipt SHA-256: `0c231b9a98b8e5811e2c1ab746713f0c75de7aec1f26572539421fd9db60b160`.
* Employee normalized gzip SHA-256: `58f5c3d7361b95bc11ad908cb562a17e6fa65acd21d80514d6925422f2de56b5`.
* Council normalized gzip SHA-256: `56c3c03b39c1fac736a0d0252c8c0b72d794f07532a78d9fabf9b475fdb9d877`.

The reviewer read the original’s rendered physical 1, 3 and 7, independently transcribed all nine rows, then called the importer’s pure `sayward_ocr` function in memory. Original/receipt/raw-reading hashes, guarded corrections, complete transcription, normalized output bytes and both cohort fingerprints all passed. Every accepted observation retains physical page 3. No compiled records are removed or relabelled.
