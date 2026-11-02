# Municipal lead processing

This worker covers the eight assigned municipal leads 026–033. The accepted set contains **411 observations across 52 source cohorts from 28 original PDFs**: 212 employee and 199 council observations. Every observation received complete independent original-image review. Root separately reviewed and adopted the four qualified pay definitions. No global salary registry or public build has been changed by this worker.

[Final lead dispositions](lead-dispositions.json) distinguish already covered originals, new literal row candidates and remaining issuer questions. The [accepted manifest](../../gap-fill-municipal/sources.json), [accepted reconciliation](accepted-summary.json) and [values-withheld source packet](independent-review-packet.json) provide data and review boundaries.

## Sources processed

- **Rossland:** Remaining located 2010–2023 histories, excluding already accepted 2015, 2021, 2022, 2024 and 2025 cohorts. Archive links labelled 2013 and 2014 retrieve the same 2013 PDF. A distinct 2014 employee schedule was recovered from physical page 57 of the official June 22, 2015 council agenda. That agenda does not supply a named 2014 council schedule. The located 2011 SOFI extract and its containing 128-page June 25, 2012 agenda omit the named employee schedule; council records are staged separately.
- **Clearwater:** All twelve located 2011–2022 originals, covering employee and elected-official schedules. Already accepted 2023–2025 sources remain untouched. Partial-year, emergency-response, donated-wage and RRSP footnotes remain explicit; payments are not annualized.
- **Barriere:** 2020 council and 2024 employee/council schedules. The 2020 staff section contains no named observations. [Aggregate-only evidence](aggregate-only-barriere-2020.json) preserves that scope without inventing an employee record. Prior 2023 sources are already accepted.
- **100 Mile House:** 2023 employee and council schedules. All eight printed employee rows remain included. Their sums exceed the printed named subtotal by amounts equal to the first row's figures. This coincidence does not establish a cause or authorize dropping that row or balancing values.
- **Lantzville:** Supplied original 7293 is the already accepted 2025 report. The distinct 2024 original 7134 supplies nine employee and five council observations. Its signed approval is dated June 25, 2025.
- **Port Moody:** Supplied original 584992 matches an already accepted source byte for byte. Official sources covering 2019–2025 already exist; no repeated import is made.
- **Trail:** All three located 2022–2024 originals match already accepted sources and scopes; no repeated import is made.
- **Abbotsford:** The 2023 original and finance page were refreshed. The page says SOFI is available on request; no public taxable-benefit dash legend was located. At root's direction, an **eleven-row known-column supplement is accepted with an explicit partial-compensation definition**. It uses literal Remuneration & Payouts, excludes the separately unknown benefit and preserves the original 449 numeric-composite observations and metadata byte for byte. The [bounded supplement proof](abbotsford-known-column-supplement.json) pins the held-row list, original 449-row payload, exact disjoint source identities and eleven actual original image crops. It neither claims complete compensation nor infers zero benefits.

## Literal fields and compensation definitions

The ordinary candidate pages were personally transcribed from actual, whole, PDF-painted salary-page images. Independent Tesseract and Paddle/RapidOCR outputs remain separate in `ocr/`. Tesseract loses many ruled-table cells; these raw readers are corroborating evidence, not a claim that both engines read every cell successfully. Final acceptance requires complete independent source-image review of every literal field.

The Abbotsford supplement uses fresh, independently positioned PyMuPDF and Poppler readers on five whole page parts, exact row comparisons and personal source-image review of the eleven selected row crops. That bounded personal review does not claim a new personal transcription of all 460 original rows.

A blank or dash expense remains null. An explicit numeric zero stays zero. Rossland's 2013 council schedule prints `Nil`, retained as explicit no expense. A subtotal match cannot establish an unknown cell's value. Names, source title spellings, repeated observations and meaningful footnotes remain intact. An explicitly defined trailing footnote marker may be removed from the displayed name/title while remaining in provenance.

Rossland's 2016–2018 council schedules each have one blank separate benefit. The adopted representation uses the numeric **Remuneration column only for every council row in each cohort**, excluding separately printed benefits throughout. No zero benefit is inferred. Employee sources with two known pay components use remuneration plus benefits, with their different definition stated. Expense-inclusive totals remain supporting evidence and are never substituted for pay. The exact seven, seven and twelve council observations and the eleven Abbotsford row crops received explicit root definition adoption.

Source residuals remain unchanged and qualified. They include Rossland's three-cent 2010 remuneration difference, a 1,000-dollar inconsistency in a 2013 employee's separate expense-inclusive Total, small later component residuals and 100 Mile House's 2023 employee subtotal difference. No cause is inferred. Some Rossland 2023 council Total cells have visibly missing digit strokes; these are preserved as incomplete source evidence instead of reconstructed by arithmetic.

Every existing compiled observation remains retained with an explicit overlap warning. This worker establishes no calendar mapping and deletes no compiled copy.

## Remaining existing-record questions

1. **Rossland 2011:** Obtain a complete named employee remuneration schedule, absent from the located SOFI and its containing agenda.
2. **Rossland 2014:** Obtain a named council schedule, absent from the distinct SOFI agenda and the 89-page 2014 Annual Report. The direct archive's 2014 link supplies the 2013 PDF. Search receipts preserve all 64 metadata results for the bounded Council Remuneration query; this is not a claim that every related agenda was personally read.
3. **Abbotsford 2023:** An existing spreadsheet or explicit taxable-benefit dash/blank definition is still needed to establish complete composite compensation for the eleven known-column observations.

These questions are documented only. **No email, municipal form, statutory request, FOI application, message or fee has been sent.** The user's four existing issuer requests remain on hold.

## Reproduction and acceptance

Original PDFs and rendered-page caches are under `/workspace/gap-municipal-cache`, outside the repository. Public URLs and exact hashes are retained. The offline build uses committed normalized payloads and evidence rather than downloading changing originals. Full PDFs, OCR models and page caches are not committed.

- `python3 scripts/gap_municipal_emit.py --check` replays selected literal transcripts and reader pins. It validates candidate bytes until an explicit `acceptance.json` is supplied, then validates accepted bytes and the pinned decision.
- `python3 -m unittest discover -s scripts -p test_gap_municipal.py -v` runs 13 missing-cell, literal-source, disjoint-supplement and acceptance-guard tests.
- The acquisition, public search, agenda recovery and OCR helpers use the `gap_municipal_` prefix. Refreshing source bytes never automatically adopts them.
- `scripts/gap_municipal_ocr.py` runs the preserved Tesseract/Paddle pair on selected exact originals. The existing RapidOCR environment is `/tmp/held-health-ocr/venv/bin/python`; models and originals are needed for new extraction, not the offline salary build.

The independent school-native reviewer completed the [earliest twelve originals](independent-review-packet-earliest-12.json), containing 22 cohorts and 149 rows. The health employee reviewer completed the [remaining sixteen originals](independent-review-packet-remaining-16.json), containing 30 cohorts and 262 rows. Both transcribed actual original pages before opening candidate values, froze their first transcripts and compared every literal field afterward. Original drafts and first visual-reading mistakes remain separate from additive corrections.

`python3 scripts/gap_municipal_finalize.py --template` creates an **unapproved** acceptance template; it never marks a source verified. Finalization fails unless the root-approved decision pins the current candidate manifest, every current candidate data/provenance hash, a nonempty unchanged independent receipt for every cohort, full literal review and period confirmation. Rossland's three known-column council cohorts and Abbotsford's eleven-row supplement require separate explicit definition adoption. Changed source values or changed peer receipts invalidate the prior decision. The [root acceptance decision](acceptance.json) now pins all 52 cohorts and both complete independent receipts. The accepted manifest and evidence replay exactly through the finalizer.

The [publication qualifications](source-publication-qualifications.json) retain unsigned or partly dated approval forms, unaudited labels and source date conflicts for 17 cohorts. [Certified-correct final Rossland minutes](rossland-2014-adoption-source-receipt.json) record approval of the 2014 SOFI package with the council remuneration table added. That missing attachment is specifically listed in [held acquisition notes](acquisition-notes.json); no council amounts are inferred. The [qualification replay](source-approval-qualification-replay.json) proves that every salary payload and literal source field remains byte-identical to the independently reviewed candidates.

`python3 scripts/gap_municipal_freeze.py --check` validates the accepted producer inputs after the final freeze. The independent review work this worker performs for other source owners under `municipal/reviews/` is deliberately outside that producer freeze and remains separately pinned in its own receipts.
