# Nine earlier PHSA employee schedules

This is a finite continuation of lead 034: nine explicitly catalogued PHSA ORIGINAL salary assets for fiscal 2006/07 through 2014/15. The title “Salaries Over $75,000” was outside the earlier discovery selector. Existing accepted PHSA employee schedules begin in 2015/16. No issuer was contacted, no form was submitted, and no request or fee was authorized.

## Original documents and periods

`original-locators.json` preserves official Legislative Library item/bundle metadata. `source-inventory.json` records each actual delivered PDF's SHA-256, byte count, physical pages, and both format probes. The Library download adds a catalogue cover and repacks the asset; advertised stored MD5/length and delivered MD5/length are deliberately recorded separately. They are not claimed to describe identical bytes. Physical PDF citations include the added cover at page 1.

The nine delivered copies have 602 physical pages. Three originals have native painted text (121 pages). Six have scanned salary schedules (481 pages including six Library covers). All 475 non-cover scan pages were captured through both original-raster OCR engines: 468 salary pages, six definition pages, and one actual blank final page in 2012/13. The native reports contain 115 salary pages. Page and payment censuses are independent of a comma-only name or shared OCR row predicate.

Periods come from actual original salary headings, not file paths or catalogue issues. The 2009/10 definition narrative says March 31, 2009, while its own heading and repeated salary-table headings say March 31, 2010. The contradictory narrative is retained; the salary period follows the repeated actual schedule headings. Its narrative count of 1,800 belongs to that contradictory period text and is not adopted as a 2010 table count control. No cause for the contradiction is invented. April 1 is the conventional start of the twelve-month fiscal year ending on the printed March 31.

## Compensation and unknown values

These are named payment disclosures above a reporting threshold, not workforce censuses or annual base salary rates. The original definition includes physical payments to or on behalf of an employee, salary/wages, taxable benefits, bonuses, stipends and applicable on-call or sessional payments. Expenses may be direct or through third parties. These salary tables have no job-title column; position remains null.

Every printed observation remains in source order, including repeated observations. Native explicit `(0)` cells are numeric zero. A dash is an unknown expense, never an invented zero. An OCR omission, absent cell, narrative count or subtotal cannot supply a missing individual amount. Literal named sums and printed controls are recorded separately, with unexplained residuals retained. In particular, the 2006/07 narrative counts 1,280 above-threshold employees, while complete independent table censuses find 1,267 observations. No thirteen employees or payments are fabricated.

## Readers, source images and bounded acceptance

The three native originals have independent Poppler physical-layout and MuPDF word-geometry readers, broad monetary-anchor censuses, original raster pins and an independent bounded image review. The initial native v1 grouping omitted one source row with a 2.88-point name/pay baseline offset. Its v2 grouping recovered the actual row; both initial and corrected snapshots remain available. A source superscript footnote marker is separate from the disclosed person name.

The six scans use separately preserved full Tesseract TSV and RapidOCR/Paddle bounding boxes from the actual 300 dpi RGB original raster. Captures use isolated processes and one OCR thread per process; PyMuPDF rendering is sequential within a process. Engine/model/dictionary hashes are retained. One initially empty RapidOCR result on the genuinely blank final 2012/13 page stopped the first capture. That failure was preserved; the resumed capture handles an empty OCR result without making it a payroll row or a zero amount.

Initial v1–v3 parsing exposed slanted-name baselines, adjacent descenders, footer rows and a printed total underneath a rule. Those superseded snapshots remain unchanged. The v4 census starts with painted remuneration-column bands across the original salary page, independently of OCR name recognition. Each original has its own header, spacing, footer, control-rule and expense-cell calibration.

Every true field or geometry flag, deterministic held-out row, score-minimum/range challenge and additional known-confusable challenge is personally read from an unaltered original-pixel crop. Independent reviewers preserve their first readings before comparing producer values. Additive source rereads retain mistakes made by either reviewer instead of silently rewriting the first transcript. For example, a primary wide-sheet reading mistook Moosa's printed 271 expense for a dash; a fresh original 600 dpi row confirmed 271. Its correction is tied to that cell, rather than to a desired total.

Remaining rows use explicit finite guards: both independently parsed readers must agree, their scores must lie within actual source-personally-corroborated ranges, and every null expense must have complete-cell original ink within that source's personally checked dash geometry. All initial generic confidence flags remain in the evidence. These finite checks reduce known failure modes; agreement or confidence does not prove infallible recognition or a statistical accuracy rate. No all-row manual-transcription claim is made.

Capital-I/l and similar name choices follow the printed mixed-case typography and same-source calibration. A rendered glyph does not establish the original Unicode character or a person's real-world identity. Name spellings, punctuation and case remain literal; no employer-directory or expected-spelling enrichment is used.

## Reproduction and retained compiled observations

The capture, reader, packet, primary-reading, selection and normalized-build scripts are separate. All raw reader alternatives, complete page locators, source-only packets, first manual readings, explicit corrections and superseded candidate snapshots are retained. `gap_phsa_history_select.py` can replay a selection offline from committed evidence without OCR models, caches, live requests, Pillow or NumPy. Original-pixel replay is a processing check against the pinned delivered PDF and separately retained raster fingerprints.

The final normalized candidate is reconstructed from pinned source selections, independent acceptance receipts and source-context decisions. It explicitly sets `retainCompiledPartition: true` together with matching complete-schedule validation and a public overlap warning. No complete-copy comparison proves that these official observations replace the retained compiled partitions. All compiled observations therefore remain available, with possible overlap disclosed.
