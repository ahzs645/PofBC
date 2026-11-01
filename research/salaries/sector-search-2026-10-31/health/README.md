# Health salary source search and historical expansion

Checked **31 October 2026, America/Vancouver**, against main `96d798e` and the 881,002-row dataset. Eight reporting employers were reviewed. **Two recovered Fraser Health employee originals provide 11,494 verified new observations**; seven Providence employee-year originals and several VCH histories were located as further candidates. Retrieval problems and incomplete scope checks remain explicit in [findings.json](findings.json).

The ready Fraser inputs are in [sector-health/sources.json](../../sector-health/sources.json), with their [collection guide](../../sector-health/README.md), locked originals, full two-engine extraction checks and six passing regression tests. They add FY2013/14 and FY2014/15 without removing compiled records. Each source carries a public warning for its unresolved printed-subtotal differences; published cells remain unchanged.

[work-queue.json](work-queue.json) provides 32 concrete remaining tasks for the combined project queue: 14 processing tasks, 15 public archive searches, two source-clarification tasks and one request for existing electronic files. Unknown historical periods remain `unknown`; a runtime download failure does not automatically become an FOI task.

## Coverage checked

| Employer | Accepted official employee periods before this pass | Current index or discovered original periods checked | Result and next action |
| --- | --- | --- | --- |
| Fraser Health | 2015/16–2024/25 | Current index: 2015/16–2024/25. Recovered originals: 2013/14 and 2014/15. | Two verified sources, 5,569 and 5,925 rows. Add after independent review. Seek 2012/13 and earlier archives. |
| Interior Health | 2014/15–2024/25 | Current index: same eleven years; 2026 board report present. | All indexed employee schedules already accepted. A guessed 2013/14 original returned 404. Search former archives for earlier years. |
| Northern Health | 2020/21–2024/25 | Current index: same five employee years; 2025/26 board report present. | Recover 2017/18 official original and earlier histories; 2018/19 and 2019/20 filename guesses returned 404. |
| Island Health | 2015/16–2021/22 and 2024/25 | Ten employee years indexed: 2015/16–2024/25; 2025/26 board report present. | 2022/23 and 2023/24 remain held for source-control disagreements. Search 2014/15 and earlier archives. |
| PHSA | None; three unverified compiled labels remain | Current index: ten scanned employee years, 2015/16–2024/25. New 2025/26 links are board reports. | Existing spreadsheet request is the best route. A fresh OCR pilot confirms shared recognition errors requiring image review. |
| BCCSS | 2016/17 and 2017/18 | Both known employee schedules indexed on PHSA; 2018/19 board link separate. | Both employee cohorts already accepted, including fully reviewed 2017/18 OCR. Establish later staff/entity transfer before treating later years as gaps. |
| Providence Health Care Society | None; 7,408 compiled rows | Official employee sources confirmed in web index for 2017/18, 2019/20–2024/25. 2018/19 SOFI found; employee section unconfirmed. | Prioritize full native-text source retrieval and extraction. Tested raw endpoints return 403 here. |
| Vancouver Coastal Health | None; 24,206 compiled rows | Official 2018/19, 2019/20 and 2020/21 employee sources confirmed; additional 2021/22 and tentative 2023/24 document leads. | Recover raw originals and verify scope/period before extraction. Web tool opens 2020/21 PDF; ordinary raw download returns 403. |

The five successful current index fetches, their SHA-256 hashes and their remuneration-related links are retained in [retrieval-receipts.json](retrieval-receipts.json). All 23 individual retrieval attempts are recorded, including 403s, 404s and an HTTP-200 HTML page-not-found response. A successful HTTP status is never treated as a successful PDF retrieval unless the content is a PDF.

Current index links do not establish complete historical availability. A guessed URL returning 404 does not establish that the report never existed. The unverified compiled labels for PHSA, Providence and VCH do not establish actual source periods. BCCSS is a separate reporting employer; its first accepted report states operations began on 1 April 2016, so pre-operation years are not listed as missing BCCSS employee cohorts.

## Confirmed primary sources to process next

The following are official source URLs discovered in indexed public content. Except for the already downloaded Fraser and PHSA sources, **their raw originals have not been hashed or approved for import**.

| Employer and fiscal period | Official original | Evidence and retrieval status |
| --- | --- | --- |
| Providence 2017/18 | [media/3706](https://www.providencehealthcare.org/en/media/3706) | Internal year ended 31 March 2018 and employee table visible in web index; raw download 403. |
| Providence 2018/19 | [media/3676](https://www.providencehealthcare.org/en/media/3676) | Internal year ended 31 March 2019 visible in supplier section; employee section still needs confirmation. |
| Providence 2019/20 | [media/3661](https://www.providencehealthcare.org/en/media/3661) | Employee table and final employee controls visible; raw download 403. |
| Providence 2020/21 | [media/3656](https://www.providencehealthcare.org/en/media/3656) | Internal fiscal heading and employee rows visible in web index. |
| Providence 2021/22 | [media/3276](https://www.providencehealthcare.org/en/media/3276) | Internal fiscal heading and employee rows visible; raw download 403. |
| Providence 2022/23 | [media/3261](https://www.providencehealthcare.org/en/media/3261) | Internal fiscal heading and employee rows visible in web index. |
| Providence 2023/24 | [original PDF](https://www.providencehealthcare.org/sites/default/files/2024-10/Schedule%20of%20Remuneration%2C%20Expenses%2C%20%26%20Supplies%20Payments%2020232024.pdf) | Combined SOFI including employee table; raw download 403. |
| Providence 2024/25 | [original PDF](https://www.providencehealthcare.org/sites/default/files/2025-11/Schedule%20of%20Remuneration%2C%20Expenses%2C%20%26%20Supplies%20Payments%2020242025.pdf) | Employee rows visible in web index; raw download 403. |
| VCH 2018/19 | [2019 original PDF](https://www.vch.ca/sites/default/files/import/documents/Schedule-of-Remuneration-and-Expenses-2019.pdf) | Employee earnings and actual April 2018–March 2019 period/definitions visible; raw download 403. |
| VCH 2019/20 | [2020 original PDF](https://www.vch.ca/Documents/Schedule-of-remuneration-and-expenses-2020.pdf) | Employee rows and a 128-page employee section visible; raw download 403. |
| VCH 2020/21 | [media/12116](https://www.vch.ca/en/media/12116) | Web tool opens a 155-page PDF: cover, board and 153 employee-section pages. Internal year ended 31 March 2021 confirmed; raw download 403. |
| VCH 2021/22 lead | [media/15051](https://www.vch.ca/en/media/15051) | Indexed board section confirms period; employee section not yet confirmed; raw download 403. |
| VCH tentative 2023/24 lead | [indexed production-careers copy](https://prod-careers.vch.ca/en/media/29876) | Title says Part F, Board and Employees. Actual internal fiscal date not yet verified; endpoint now 404. Locate the current official original. |

Providence's table splits surnames and first names into separate columns. VCH's indexed text sometimes puts the expense dash before the pay amount, so a trailing-number parser could assign the wrong monetary column. Both need complete coordinate-aware source parsing and rendered checks. Board and supplier sections must remain separate from employee observations. Aggregate wages in audited financial statements include other components and cannot supply named employee rows.

## Acquisition and clarification queue

| Priority | Material needed | Public retrieval or acquisition route | Why it remains outside the accepted app inputs |
| --- | --- | --- | --- |
| 1 | PHSA existing Excel/CSV employee schedules, FY2015/16–2024/25, plus controls and entity scope | Existing [unsent request draft](../../requests/source-requests-2026-10-30.md), [official FOI route](https://www.phsa.ca/about/accountability/freedom-of-information-requests), `foi@phsa.ca`. Ask for the existing electronic files first. | Ten official originals are scans totaling 1,764 pages. PHSA/BCEHS/BCCSS staff scope needs preserving. Full OCR remains possible but requires row review. |
| 1 | Island Health FY2022/23 and FY2023/24 existing corrected tables or explanation/amended source | Existing [unsent request draft](../../requests/source-requests-2026-10-30.md), [official access route](https://www.islandhealth.ca/about-us/accountability/information-stewardship-access-privacy/accessing-information-records), `FOI@islandhealth.ca`. | FY2022/23 extraction has 8,252 rows versus 8,264 declared; pay +$54 and expenses +$93 against controls. FY2023/24 expenses are $45,772 below printed named subtotal; pay +$41. Two readers already agree. |
| 2 | Providence and VCH raw public originals listed above | Try a working ordinary public-download/browser route and locate the current primary index. If still inaccessible, ask the issuer's financial reporting/records office for existing copies. | Source existence is established, but this runtime's 403 is a retrieval blocker. It does not establish that an FOI request is required. |
| 3 | Northern FY2017/18–2019/20 and earlier; Fraser FY2012/13 and earlier; Interior FY2013/14 and earlier; Island FY2014/15 and earlier | Former official financial-report archives first; request the existing archived employee schedules and spreadsheets if not publicly recoverable. | Current indexes start later, and tested historical filename guesses fail. No exhaustive archive search or absence claim is made. |
| 3 | PHSA/Providence/VCH earlier histories and latest FY2025/26 full employee schedules | Continue official archive/current-index research, retaining board/executive cohorts separately. | New board reports do not fill employee disclosure gaps. |
| Scope decision | BCCSS standalone employee reporting after FY2017/18 | Verify successor/staff transfer documents and identify the responsible reporting entity before a records request. | A later BCCSS board disclosure alone does not prove that a separate employee cohort should exist. |

**No requests or messages were sent to any health authority or other outside party.**

## OCR work completed

PHSA FY2024/25 was downloaded again from its [official original](https://www.phsa.ca/about-site/Documents/FY2025-Employee-Salary-and-Expenses-exceeding-75000.pdf): **54,160,556 bytes**, SHA-256 `809817f42c9e75c0ba13155cb7543e1ef5d7dea8422a51dce2ac2fe71bf7fb6c`, agreeing with the previous audit. All **284 pages have zero native text characters**.

The first and final pages were rendered at 144 dpi. Tesseract 5.5.0 modes 6 and 4 each find 49 first-page employee candidates. Strict expense-cell checks flag eight and five candidate tokens, respectively. Both modes misread the real **$771** expense for **Abia,Jo-Ann** as `™m`; the rendered source establishes the correction. They also share or disagree on dash/name-punctuation errors. Two configurations of the same OCR engine cannot establish independent correctness.

The rendered final page and OCR agree on the printed totals **$1,713,046,476 remuneration** and **$25,171,641 expenses**. These are controls for a future complete extraction, not proof that a partial or full candidate transcription is correct. [ocr-pilot.json](ocr-pilot.json) and the three adjacent raw text files retain the experiment. **No PHSA rows were accepted from this pilot.**

Reproduce the pilot from the downloaded PDF with PyMuPDF at matrix `(2,2)` for physical pages 1 and 284, then run Tesseract `-l eng --psm 6` and `--psm 4` on page 1 and mode 6 on page 284. A full extraction must review every page/name/amount, retain missing versus explicit zero/negative cells, guard correction contexts, and record exact control differences without changing published cells to make them balance.
