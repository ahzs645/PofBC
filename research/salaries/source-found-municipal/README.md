# Source-found municipal SOFI imports

Official Statement of Financial Information (SOFI) remuneration schedules for municipal employer-years that the coverage file listed as `source-found` (a report had been located but never extracted). Manifest: `sources.json`; data rows `[employerSlug, name, position_or_null, remuneration, expenses_or_null, physicalPdfPage]` in `<employer>-<year>-<scope>.json.gzip`; per-row evidence (printed cells, both engines' text, skipped lines, validation) in `evidence/`.

## Method

- Each PDF was downloaded from the lead URL in `public/salaries/coverage.json` and hashed (SHA-256 below).
- Schedules were extracted only from a native text layer, independently with poppler `pdftotext -layout` and with pdfplumber/pdfminer character boxes (own word and column builder). Rows were accepted only when both engines agreed row-for-row on name, position text, every printed amount cell and physical page.
- Named rows were reconciled to the printed schedule total; only whole-dollar rounding (0.5 x rows) is accepted. Nothing was adjusted to force a match.
- Scope `employee-remuneration` is the printed list of employees over $75,000 (`threshold` 75000, `>`, `completeEmployeeSchedule` true); `elected-officials` has `threshold` null and `completeEmployeeSchedule` false. Calendar years, sector "Municipalities".
- Conventions: a printed dash or a blank expense cell is recorded as null (the repository convention); a printed zero stays zero. Names, positions and amounts are as printed (including capitalisation and missing commas). Multi-column remuneration is documented per source (e.g. Prince Rupert pay is the printed total remuneration; Quesnel 2024 pay is the printed Total Income = remuneration + taxable benefits); components are kept in the evidence file.
- PDFs with no text layer, or with a scanned image plus third-party OCR text, were held: tesseract is not installed, so no independent reading could be verified against printed totals.
- This directory is not yet listed in `research/salaries/collections.json`; the build only reads collections listed there.

## Employer-years

### City of Nelson 2011

- URL: https://www.nelson.ca/Archive.aspx?ADID=49
- PDF SHA-256: `0e7d46dc6c77ee78e1ca3b40cd5c88af1c33e7b3b9619d78fa809963ef32a37d`
- all schedules: **held** - image-only PDF; OCR not attempted (34 pages, 0 extractable text characters; tesseract is not installed).

### City of Nelson 2012

- URL: https://www.nelson.ca/Archive.aspx?ADID=50
- PDF SHA-256: `40aacb431e66cd1257f21c6a8e668d447b5f77b080437c88b469ee263d84723c`
- all schedules: **held** - image-only PDF; OCR not attempted (35 pages, 0 extractable text characters; tesseract is not installed).

### City of Nelson 2013

- URL: https://www.nelson.ca/Archive.aspx?ADID=51
- PDF SHA-256: `420e13738ebb377adbd40867f8671b61c5abe4e9734a1b042a428d4d12d6faa5`
- all schedules: **held** - image-only PDF; OCR not attempted (35 pages, 0 extractable text characters; tesseract is not installed).

### City of Nelson 2014

- URL: https://www.nelson.ca/Archive.aspx?ADID=52
- PDF SHA-256: `82e5a73bc676af984c5e71bce0090b37193b37700e6ec09c4a94023ed408e966`
- all schedules: **held** - image-only PDF; OCR not attempted (35 pages, 0 extractable text characters; tesseract is not installed).

### City of Nelson 2015

- URL: https://www.nelson.ca/Archive.aspx?ADID=53
- PDF SHA-256: `2b3c0358842c544f7b20ab20e67b3a861d5a1430b8dbab43e324e14d095a4dd6`
- all schedules: **held** - image-only PDF; OCR not attempted (35 pages, 0 extractable text characters; tesseract is not installed).

### City of Nelson 2016

- URL: https://www.nelson.ca/Archive.aspx?ADID=148
- PDF SHA-256: `bb924c4f0f2db55a6710fd04281baadf67822d8e1ac65b1648f54d15bcda0578`
- all schedules: **held** - image-only PDF; OCR not attempted (34 pages, 0 extractable text characters; tesseract is not installed).

### City of Nelson 2017

- URL: https://www.nelson.ca/Archive.aspx?ADID=151
- PDF SHA-256: `c1832eec17d60b99f5f619e037c954896d41b2533cff8d9d4776c785b3a552a4`
- all schedules: **held** - image-only PDF; OCR not attempted (35 pages, 0 extractable text characters; tesseract is not installed).

### City of Nelson 2018

- URL: https://www.nelson.ca/Archive.aspx?ADID=162
- PDF SHA-256: `08aa01f0d35a2876b460270720781308d141614020529cb8b7dfa2e50036924c`
- all schedules: **held** - image-only PDF; OCR not attempted (40 pages, 0 extractable text characters; tesseract is not installed).

### City of Nelson 2019

- URL: https://www.nelson.ca/Archive.aspx?ADID=165
- PDF SHA-256: `7bc4d323c858f3111dc7d1b3b7af54e108638196c3f74e09d54240d85aa2d32f`
- `elected-officials`: **accepted** - 7 rows, pages 36; remuneration $232,715 (printed $232,714, residual +1), expenses $53,722 (printed $53,722, residual +0); tolerance 3.5.
- `employee-remuneration`: **accepted** - 54 rows, pages 36, 37; remuneration $5,794,825 (printed $5,794,823, residual +2), expenses $128,029 (printed $128,029, residual +0); tolerance 27.

### City of Nelson 2020

- URL: https://www.nelson.ca/Archive.aspx?ADID=167
- PDF SHA-256: `d684e542ad8ff17691c79eb912ffefdcaa47e904ee1373f3cea559e9be987f17`
- `elected-officials`: **accepted** - 7 rows, pages 9; remuneration $208,170 (printed $208,169, residual +1), expenses $248 (printed $248, residual +0); tolerance 3.5.
- `employee-remuneration`: **accepted** - 62 rows, pages 9, 10; remuneration $6,532,555 (printed $6,532,554, residual +1), expenses $53,078 (printed $53,078, residual +0); tolerance 31.

### City of Nelson 2021

- URL: https://www.nelson.ca/Archive.aspx?ADID=172
- PDF SHA-256: `6ed4b24857a69a929cfde577bbe5239a134ff491ab71b2af7af42f823b587670`
- `elected-officials`: **accepted** - 7 rows, pages 8; remuneration $205,470 (printed $205,469, residual +1), expenses $4,596 (printed $4,596, residual +0); tolerance 3.5.
- `employee-remuneration`: **accepted** - 63 rows, pages 8, 9; remuneration $6,709,316 (printed $6,709,317, residual -1), expenses $45,801 (printed $45,801, residual +0); tolerance 31.5.

### City of Nelson 2022

- URL: https://www.nelson.ca/Archive.aspx?ADID=174
- PDF SHA-256: `70bfa9b6400e693fd3fbbb248df1281a7a9dbff253967c358e7f20a65e6357f5`
- `elected-officials`: **accepted** - 10 rows, pages 35; remuneration $233,167 (printed $233,166, residual +1), expenses $36,167 (printed $36,166, residual +1); tolerance 5.
- `employee-remuneration`: **accepted** - 74 rows, pages 35, 36; remuneration $7,598,762 (printed $7,598,763, residual -1), expenses $143,403 (printed $143,399, residual +4); tolerance 37.

### City of Nelson 2023

- URL: https://www.nelson.ca/Archive.aspx?ADID=178
- PDF SHA-256: `60708e00ea7ad54ad2ee9f0688ac7f5752babc8484e316a0bcca69fa16d972b8`
- `elected-officials`: **accepted** - 7 rows, pages 36; remuneration $235,117 (printed $235,117, residual +0), expenses $34,852 (printed $34,852, residual +0); tolerance 3.5.
- `employee-remuneration`: **accepted** - 91 rows, pages 36, 37; remuneration $9,587,732 (printed $9,587,732, residual +0), expenses $168,375 (printed $168,375, residual +0); tolerance 45.5.

### City of Nelson 2024

- URL: https://www.nelson.ca/Archive.aspx?ADID=179
- PDF SHA-256: `2a5aea31442018babba6f48bb6b024d825354cbcf218dc328ae52936a34d5281`
- `elected-officials`: **accepted** - 7 rows, pages 38; remuneration $241,622 (printed $241,622, residual +0), expenses $39,096 (printed $39,096, residual +0); tolerance 3.5.
- `employee-remuneration`: **accepted** - 112 rows, pages 38, 39, 40; remuneration $12,294,176 (printed $12,294,176, residual +0), expenses $237,009 (printed $237,009, residual +0); tolerance 56.

### City of Prince Rupert 2016

- URL: https://www.princerupert.ca/sites/7/files/2023-06/2016%20Statement%20of%20Financial%20Information_0.pdf
- PDF SHA-256: `ba134b222959dbb00c1dfa6326a1fc7629df4ef93167152d9f309c0071e810ac`
- `elected-officials`: **accepted** - 7 rows, pages 5; remuneration $143,968 (printed $143,967, residual +1), expenses $31,261 (printed $31,261, residual +0); tolerance 3.5.
- `employee-remuneration`: **accepted** - 65 rows, pages 6, 7, 8; remuneration $6,570,715 (printed $6,570,714, residual +1), expenses $177,099 (printed $177,093, residual +6); tolerance 32.5.

### City of Prince Rupert 2017

- URL: https://www.princerupert.ca/sites/7/files/2023-06/2018-06-11%202017%20SOFI%20Report.pdf
- PDF SHA-256: `f64ff49007d116e9314eb901f91307fb9d66b6c7dac1e23ba784ebef19719e6b`
- `elected-officials`: **accepted** - 7 rows, pages 5; remuneration $141,886 (printed $141,886, residual +0), expenses $35,674 (printed $35,674, residual +0); tolerance 3.5.
- `employee-remuneration`: **accepted** - 69 rows, pages 6, 7; remuneration $7,022,635 (printed $7,022,637, residual -2), expenses $133,842 (printed $133,845, residual -3); tolerance 34.5.

### City of Prince Rupert 2018

- URL: https://www.princerupert.ca/sites/7/files/2023-06/2018%20SOFI.pdf
- PDF SHA-256: `253dc7312ccf86e4e7db41e89780dcb9727e38f9b9051b7525b9ed2250f50632`
- all schedules: **held** - image-only PDF; OCR not attempted (43 pages, 0 extractable text characters; tesseract is not installed).

### City of Prince Rupert 2019

- URL: https://www.princerupert.ca/sites/7/files/2023-06/2019%20SOFI%20Submission%20set.pdf
- PDF SHA-256: `7645c7921ee7c1e22906fb7eaf46742d066c160fe8571c9be2807ff8efb29489`
- `elected-officials`: **accepted** - 7 rows, pages 5; remuneration $188,836 (printed $188,836, residual +0), expenses $47,020 (printed $47,020, residual +0); tolerance 3.5.
- `employee-remuneration`: **accepted** - 77 rows, pages 6, 7; remuneration $8,320,190 (printed $8,320,192, residual -2), expenses $326,357 (printed $326,357, residual +0); tolerance 38.5.

### City of Prince Rupert 2020

- URL: https://www.princerupert.ca/sites/7/files/2023-06/2020%20Statement%20of%20Financial%20Information.pdf
- PDF SHA-256: `e7829d5f5935b5805ae37928d303004b789218df4cdeda7454b71ddebde0f734`
- `elected-officials`: **accepted** - 7 rows, pages 5; remuneration $187,940 (printed $187,940, residual +0), expenses $7,735 (printed $7,735, residual +0); tolerance 3.5.
- `employee-remuneration`: **accepted** - 88 rows, pages 6, 7, 8; remuneration $9,059,188 (printed $9,059,185, residual +3), expenses $209,056 (printed $209,056, residual +0); tolerance 44.

### City of Prince Rupert 2021

- URL: https://www.princerupert.ca/sites/7/files/2023-06/SOFI%20June%2013%202022.pdf
- PDF SHA-256: `744ad866e07a05a1e69f7edf0335b799b8e215221513f6aaa560c7bd862c5599`
- `elected-officials`: **accepted** - 7 rows, pages 5; remuneration $215,181 (printed $215,181, residual +0), expenses $801 (printed $801, residual +0); tolerance 3.5.
- `employee-remuneration`: **accepted** - 84 rows, pages 6, 7, 8; remuneration $9,829,196 (printed $9,829,190, residual +6), expenses $220,444 (printed $220,439, residual +5); tolerance 42.

### City of Prince Rupert 2022

- URL: https://www.princerupert.ca/sites/7/files/2023-07/2022%20SOFI%20-%2015Jun2023.pdf
- PDF SHA-256: `b66ef4ad53f8c46f6257ed34a3cd430f6abc15eea6c41e79d2f55e90c0d272d1`
- `elected-officials`: **accepted** - 9 rows, pages 5; remuneration $218,170 (printed $218,170, residual +0), expenses $18,597 (printed $18,597, residual +0); tolerance 4.5.
- `employee-remuneration`: **accepted** - 85 rows, pages 6, 7, 8; remuneration $10,074,588 (printed $10,074,588, residual +0), expenses $219,768 (printed $219,767, residual +1); tolerance 42.5.

### City of Prince Rupert 2023

- URL: https://www.princerupert.ca/sites/7/files/2024-06/2023%20SOFI%20and%20Financial%20Statements.pdf
- PDF SHA-256: `c63daf951525b7c079caac47a6d8f3916b86deb91d8dc3bc0d90642e5e540297`
- `elected-officials`: **accepted** - 7 rows, pages 5; remuneration $225,089 (printed $225,089, residual +0), expenses $69,460 (printed $69,460, residual +0); tolerance 3.5.
- `employee-remuneration`: **accepted** - 129 rows, pages 6, 7, 8, 9; remuneration $14,189,911 (printed $14,189,906, residual +5), expenses $513,209 (printed $513,194, residual +15); tolerance 64.5.

### City of Prince Rupert 2024

- URL: https://www.princerupert.ca/sites/7/files/2025-06/2024%20SOFI.pdf
- PDF SHA-256: `4247ca4967220ae3e21aaa2d7c518285f030ab0f2cbc6646e2c03e41164727db`
- `elected-officials`: **accepted** - 7 rows, pages 5; remuneration $234,530 (printed $234,530, residual +0), expenses $71,354 (printed $71,354, residual +0); tolerance 3.5.
- `employee-remuneration`: **accepted** - 134 rows, pages 6, 7, 8, 9; remuneration $14,550,536 (printed $14,550,529, residual +7), expenses $501,180 (printed $501,176, residual +4); tolerance 67.

### City of Quesnel 2018

- URL: https://www.quesnel.ca/media/file/2018-statement-financial-information-city-quesnel
- PDF SHA-256: `d3557bfa5946ccfb03951ad4ddc5646e13f62510e61bc04598c560c8820de583`
- all schedules: **held** - image-only PDF; OCR not attempted (14 pages, 0 extractable text characters; tesseract is not installed).

### City of Quesnel 2019

- URL: https://www.quesnel.ca/media/file/city-quesnel-2019-sofi
- PDF SHA-256: `c5fecb2384863ab6c39a222ee7daa83c9c58b156c002d3b31b1f3f1de563a996`
- all schedules: **held** - image-only PDF; OCR not attempted (14 pages, 0 extractable text characters; tesseract is not installed).

### City of Quesnel 2020

- URL: https://www.quesnel.ca/media/file/city-quesnel-2020-sofi
- PDF SHA-256: `9342db01ff8c6c72488815d9c71069023f02d4528be54bcc491e24db9bffd9f4`
- all schedules: **held** - image-only PDF; OCR not attempted (14 pages, 0 extractable text characters; tesseract is not installed).

### City of Quesnel 2021

- URL: https://www.quesnel.ca/media/file/2021-sofi
- PDF SHA-256: `9a555be7fe2c8a15d0dc16309743bc46fce707445f6f6d3a8f11283002cb8eba`
- `elected-officials`: **accepted** - 7 rows, pages 3; remuneration $182,936.96 (printed $182,936.96, residual +0), expenses $3,227.95 (printed $3,227.95, residual +0); tolerance 3.5.
- `employee-remuneration`: **held** (42 rows extracted) - Named rows do not reconcile to the printed total within whole-dollar rounding (0.5 x 42 rows = 21): remuneration row sum 4016499.15 vs printed 4016499.15 (residual 0); expenses row sum 26688.11 vs printed 28330.8 (residual -1642.69). Both extraction engines agree row-for-row, so the difference is in the printed schedule; held rather than adjusted.

### City of Quesnel 2022

- URL: https://www.quesnel.ca/media/file/2022-sofi
- PDF SHA-256: `d14f10a478cb3b620bb70e3ca98bee12a960b13f4dea1834cc49a969344babdf`
- `elected-officials`: **accepted** - 8 rows, pages 3; remuneration $189,049.76 (printed $189,049.76, residual +0), expenses $9,533.41 (printed $9,533.41, residual +0); tolerance 4.
- `employee-remuneration`: **held** (38 rows extracted) - Named rows do not reconcile to the printed total within whole-dollar rounding (0.5 x 38 rows = 19): remuneration row sum 3851893.05 vs printed 3851893.05 (residual 0); expenses row sum 55814 vs printed 56014.0 (residual -200). Both extraction engines agree row-for-row, so the difference is in the printed schedule; held rather than adjusted.

### City of Quesnel 2024

- URL: https://www.quesnel.ca/media/file/2024-sofisignedpdf
- PDF SHA-256: `7578426f64644bfcf577ddd658318b7782dd622a62743b14a875de1438e8abfd`
- `elected-officials`: **accepted** - 7 rows, pages 5; remuneration $202,635 (printed $202,633, residual +2), expenses $29,227 (printed $29,227, residual +0); tolerance 3.5.
- `employee-remuneration`: **accepted** - 60 rows, pages 6, 7, 8; remuneration $5,733,463 (printed $5,733,463, residual +0), expenses $99,193 (printed $99,193, residual +0); tolerance 30.

### City of Penticton 2021

- URL: https://www.penticton.ca/sites/default/files/docs/city-hall/financial-statements/2021%20SOFI%20Report.pdf
- PDF SHA-256: `0a846e9f6c48d162a1774c532b85f6301dd88c850d1d39b5126f210db2e5e02a`
- all schedules: **held** - image-only PDF; OCR not attempted (13 pages, 0 extractable text characters; tesseract is not installed).

### City of Penticton 2022

- URL: https://www.penticton.ca/sites/default/files/docs/city-hall/annual-reports/SOFIs/2022%20Statement%20of%20Financial%20Information%20(SOFI).pdf
- PDF SHA-256: `e51ff5f165c61c1d5456f88395ac9f217cff192d0f2772f3effc098d64445669`
- all schedules: **held** - image-only PDF; OCR not attempted (13 pages, 0 extractable text characters; tesseract is not installed).

### City of Penticton 2023

- URL: https://www.penticton.ca/sites/default/files/docs/city-hall/annual-reports/SOFIs/2023%20Statement%20of%20Financial%20Information%20(SOFI).pdf
- PDF SHA-256: `9f5aad228bf2634fbcf3ac1702f2cd1b0fe0f3db6c2f571401f2e58470af9bcc`
- `elected-officials`: **accepted** - 7 rows, pages 3; remuneration $248,523 (printed $248,526, residual -3), expenses $56,492 (printed $56,493, residual -1); tolerance 3.5.
- `employee-remuneration`: **accepted** - 187 rows, pages 4, 5, 6; remuneration $19,427,720.24 (printed $19,427,720, residual +0.24), expenses $504,645.66 (printed $504,646, residual -0.34); tolerance 93.5.

### City of Penticton 2024

- URL: https://www.penticton.ca/sites/default/files/docs/city-hall/financial-statements/Attachment%20A%20%E2%80%93%202024%20Statement%20of%20Financial%20Information%20(SOFI).pdf
- PDF SHA-256: `3862928dcf707279d34a3b34d9b2d541f6a96bbb2889a5721618477baae727c5`
- `elected-officials`: **accepted** - 7 rows, pages 4; remuneration $251,176.26 (printed $251,176.26, residual +0), expenses $60,535.41 (printed $60,535.41, residual +0); tolerance 3.5.
- `employee-remuneration`: **accepted** - 224 rows, pages 5, 6, 7; remuneration $24,666,712.41 (printed $24,666,712.41, residual +0), expenses $531,256.65 (printed $531,256.65, residual +0); tolerance 112.

### City of Castlegar 2021

- URL: https://castlegar.ca/wp-content/uploads/2023/05/2021-Statement-of-Financial-Information-amended-FINAL.pdf
- PDF SHA-256: `68e501196526175979faff294619759fa348dcf7b909d0ee03adac9fbc95b9e6`
- `elected-officials`: **accepted** - 9 rows, pages 3; remuneration $122,400 (printed $122,400, residual +0), expenses $5,587 (printed $5,587, residual +0); tolerance 4.5.
- `employee-remuneration`: **held** (29 rows extracted) - Named rows do not reconcile to the printed total within whole-dollar rounding (0.5 x 29 rows = 14.5): remuneration row sum 2927914 vs printed 2811337 (residual 116577); expenses row sum 45346 vs printed 45235 (residual 111). Both extraction engines agree row-for-row, so the difference is in the printed schedule; held rather than adjusted.

### City of Castlegar 2022

- URL: https://castlegar.ca/wp-content/uploads/2023/11/2022-Statement-of-Financial-Information.pdf
- PDF SHA-256: `f345f56896d2244b77f5ff8244adc239010f7247fe87ba0ac0097ca9c42d2460`
- `elected-officials`: **accepted** - 10 rows, pages 3; remuneration $132,803 (printed $132,802, residual +1), expenses $18,218 (printed $18,217, residual +1); tolerance 5.
- `employee-remuneration`: **held** (34 rows extracted) - Named rows do not reconcile to the printed total within whole-dollar rounding (0.5 x 34 rows = 17): remuneration row sum 3489451 vs printed 3368807 (residual 120644); expenses row sum 81006 vs printed 79887 (residual 1119). Both extraction engines agree row-for-row, so the difference is in the printed schedule; held rather than adjusted.

### City of Cranbrook 2023

- URL: https://docs.cranbrook.ca/downloads/finance/2023_Statement_of_Financial_Information.pdf
- PDF SHA-256: `b3065ca41de8494809f74b1d7fad35f64ced3f0362e7817d3ffc44793909e09a`
- `elected-officials`: **accepted** - 7 rows, pages 4; remuneration $233,576 (printed $233,577, residual -1), expenses $39,058 (printed $39,058, residual +0); tolerance 3.5.
- `employee-remuneration`: **accepted** - 90 rows, pages 5, 6; remuneration $10,000,180 (printed $10,000,177, residual +3), expenses $200,510 (printed $200,510, residual +0); tolerance 45.

### City of Cranbrook 2024

- URL: https://docs.cranbrook.ca/downloads/finance/SOFI-2024.pdf
- PDF SHA-256: `60175ddc92b06cdebeb1941cd12b05a36ef87c75d0425286bfc8a13385eba672`
- `elected-officials`: **accepted** - 7 rows, pages 4; remuneration $242,275 (printed $242,275, residual +0), expenses $33,696 (printed $33,696, residual +0); tolerance 3.5.
- `employee-remuneration`: **accepted** - 128 rows, pages 5, 6, 7; remuneration $13,760,961 (printed $13,760,964, residual -3), expenses $250,378 (printed $250,379, residual -1); tolerance 64.

### City of Dawson Creek 2015

- URL: https://dawsoncreek.civicweb.net/document/135363
- PDF SHA-256: `ec9cdc2722c67c9af7d051f9ac588be2ba243e3b5bbd56b6b70f9ab3e64e83a0`
- `elected-officials`: **accepted** - 7 rows, pages 4; remuneration $165,013.45 (printed $165,013.45, residual +0), expenses $72,262.27 (printed $72,262.27, residual +0); tolerance 3.5.
- `employee-remuneration`: **accepted** - 51 rows, pages 4; remuneration $5,196,460.51 (printed $5,196,460.51, residual +0), expenses $99,377.98 (printed $99,377.98, residual +0); tolerance 25.5.

### City of Dawson Creek 2016

- URL: https://dawsoncreek.civicweb.net/document/135364
- PDF SHA-256: `4902afa4e6dd3ee5536eca266c6d3770c03b845a2e33b092cca966bd7533af64`
- all schedules: **held** - Scanned page images with an embedded third-party OCR text layer that is largely unreadable (e.g. "Stiturlent at Financiallnlomlithn", "Burnxtei?, Dale", "TOTALFOR ELECFED 16 .07 .80"). OCR not attempted (tesseract is not installed), so no independent reading can be verified against the printed totals.

### City of Dawson Creek 2018

- URL: https://dawsoncreek.civicweb.net/document/135366
- PDF SHA-256: `f4dc86df329806d8a25c4a3ecccf730d62e697077870de02c17a15a2a69f7e14`
- all schedules: **held** - Scanned page images (Times-Roman OCR text layer over 1688x2198 images) with recognition errors in the schedule (e.g. "$" read as "5"/"S", "28,521-51", "10.34018", "Of?cials"). OCR not attempted (tesseract is not installed), so no independent reading can be verified against the printed totals.

### City of Dawson Creek 2025

- URL: https://dawsoncreek.civicweb.net/document/163514
- PDF SHA-256: `1b98d04eaea6a076f81e7c81dcdee406069cdf3ae9f667e21099f3ebf895affe`
- all schedules: **held** - Scanned page images with an embedded OCR text layer showing recognition errors in names and amounts (e.g. "Gillingham,.l", "218,317.2 JS", "TOTALFORELECTEDOFFICIALS: $ 24931226"). OCR not attempted (tesseract is not installed), so no independent reading can be verified against the printed totals.

### City of Salmon Arm 2021

- URL: https://www.salmonarm.ca/Archive.aspx?ADID=1131
- PDF SHA-256: `14d2475cf444db4a2fc0ea151f38cf77eac4baec2126eb343140831f68f9debb`
- all schedules: **held** - Scanned page images (Century OCR text layer over 2200x1700 images) with recognition errors in the schedule (e.g. "82.918", "1.531", "Bannister. Carl", "Wjlson", "Utility Person 111", "SAIMONARM"). OCR not attempted (tesseract is not installed), so no independent reading can be verified against the printed totals.

### City of Salmon Arm 2023

- URL: https://www.salmonarm.ca/Archive.aspx?ADID=1219
- PDF SHA-256: `cd73f7ecfc6b1125f16f7a50d937491819e7a0f2189614760737c803f8e24414`
- all schedules: **held** - Scanned page images (Century OCR text layer over 3300x2550 images) with recognition errors in the schedule (e.g. "$ 20 iP 83,860", "I_Name", "SAIMOMARM"). OCR not attempted (tesseract is not installed), so no independent reading can be verified against the printed totals.

### Town of Smithers 2023

- URL: https://www.smithers.ca/sites/default/files/2024-06/2023%20Smithers%20Approved%20SOFI%20Report%2C%2005-28-24.pdf
- PDF SHA-256: `cbd1e97f690cb6ada5a5bbdebad192bbd97234e11da314fe3e987db162d2f1fd`
- all schedules: **held** - Schedule pages 9-10 are scanned images with a non-embedded OCR text layer showing recognition errors (e.g. "Planner Ill", "Building Inspector Ill", an expense printed as "."), so the native-text dual-engine check cannot establish the printed values. OCR not attempted (tesseract is not installed), so no independent reading can be verified against the printed totals.

### Town of Smithers 2024

- URL: https://www.smithers.ca/sites/default/files/2025-07/FIN%2025-012%20Attach.%201%202024%20SOFI%20Filing.pdf
- PDF SHA-256: `71fb598f011df445388cf95e8f7bf790267ef17df1413809e547d7e9acc7409d`
- `elected-officials`: **accepted** - 7 rows, pages 8; remuneration $159,465 (printed $159,465, residual +0), expenses $60,968 (printed $60,968, residual +0); tolerance 3.5.
- `employee-remuneration`: **accepted** - 38 rows, pages 9; remuneration $3,686,811 (printed $3,686,813, residual -2), expenses $106,104 (printed $106,106, residual -2); tolerance 19.

Totals: 46 accepted schedules, 24 held entries.
