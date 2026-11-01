# NIC FY2019/20 complete employee schedule recovery

Two separate official fiscal scopes: **136 employee rows**, remuneration **$13,045,792**, expenses **$543,386**; and **15 Board rows**, remuneration **$16,375**, expenses **$12,727**. Total **151 observations**. The exact archived October 22, 2020 NIC Board agenda contains every salary schedule page, printed 1–5, at recovered package physical pages 26–30. This fills the gap in the separate signed nine-page scan, which has only employee pages 2 and 4. No other NIC year or compiled partition is imported or replaced.

The archived board package is genuinely truncated: 1,048,576 bytes were preserved, versus its archival header's original length of 3,739,511 bytes, with `Warning: 299 wayback content truncated by "length"`. The original lacks its trailer; MuPDF repairs it. Independently, Ghostscript recovers the five salary pages and Poppler reads their layout. Every ordered visible name, pay, expense, page and row boundary agrees. Every position is null because embedded job-title strings are painted white and are invisible on the source page. Hidden native strings are not treated as published titles. Source images for all five salary pages were reviewed; exact coverage and source hashes are recorded separately.

Named employee controls reconcile exactly. The separate Board table has 15 people and controls of $16,375 remuneration / $12,727 expenses; it is accepted separately as Board remuneration and is not part of the employee cohort. All 15 visible Board records match an independent source-image transcript, with every position null. Its Board page is absent from the signed scan, so no individual Board crossmatch to that scan is claimed. Adding those controls and below-threshold aggregates of $15,484,088 / $454,520 gives the printed overall $28,546,255 / $1,010,633. Both overall figures match the separate signed original. Its 72 surviving named rows also match the recovered salary pages exactly, using independent signed-scan OCR plus manual original-image checks. Tesseract is one supplementary OCR engine; it is not represented as two independent engines.

Remuneration is the source Remuneration column, without adding expenses or employer costs. All source expense dashes stay null; explicit zero would stay zero. No negative expense amount occurs. The salary headings explicitly say year ended March 31, 2020, so the fiscal period is April 1, 2019 through March 31, 2020. Current index labeling is not used to change that period. All five printed salary pages are complete; **the overall Board package is not complete**.

The agenda attachment has unsigned approval lines. Separate complete official October 22, 2020 minutes, physical/printed page 4, item 4.2.1, record a carried motion approving Financial Information Act information for the year ended March 31, 2020. The signed management scan dated October 27, 2020 provides further corroboration. A clear public warning preserves the archive/repair limitation.

The bounded search receipts cover current/legacy NIC links, dated official Board indices and attachments, Ministry originals, Legislative Library public holdings, Arca navigation and search discovery. A later archived Board index changed the October attachment from `agendacover.pdf` to `agenda.pdf`; following that exact published link recovered the missing salary pages. The complete nine-page PDF was rechecked for page boxes, raw images, orphan objects, duplex/combined pages and embedded files. No hidden back pages exist there. The new crosswalk also corrects one old nonemployee footer: physical page 3 is guarantee page 1 of 2, not 2 of 2. Earlier frozen receipts remain unchanged.

Reproduce from repository root (Python, PyMuPDF 1.26.6, Ghostscript 10.05.1, Poppler 25.03.0; PDFMiner is used for the nine-page structure check):

```sh
python scripts/resolve_held_education.py
python scripts/resolve_held_education.py --originals
python -m unittest discover -s scripts -p 'test_resolve_held_education.py'
python scripts/resolve_held_education_review.py --originals
```

Default replay uses compressed row/evidence inputs. Original replay requires the hash-pinned PDFs under `/tmp/nic-held-resolution`, independently runs Ghostscript, and recreates only `/tmp` rendered images. `--build` is for pre-freeze reproduction or an isolated copied output location. PDFs and image binaries are not stored in the repository. Exact archival URLs, hashes, index chain, request receipts and image coverage are in `../held-resolution-2026-11-01/education/`. The complete-copy request is concrete and unsent; obtaining a complete preservable original remains useful even though the employee schedule is recovered.
