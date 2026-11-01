# Municipal historical follow-up

As of **31 October 2026, America/Vancouver**, this pass checked **24 priority
municipal archives**, retrieved and fingerprinted **29 original PDFs**, and
prepared **411 reviewed observations** from Pitt Meadows, Revelstoke and Parksville.
These are 360 employee disclosures and 51 council disclosures across seven calendar
municipality-years and 14 cohorts. All three municipalities lacked accepted
official records at baseline `96d798e`.

Start with [findings.json](findings.json). Each employer has its exact official
index, baseline accepted years and compiled labels, archive receipt, retrieved
originals, inspected periods, schedule/text status and concrete next action.
[work-queue.json](work-queue.json) provides normalized next tasks with processing,
archive research and routine/clarification request routes. An empty reporting
period list means the schedule period is unverified or the task seeks a historical
index; any index label is stated in the task's reason. No automatic FOI filing is
queued for a report already available publicly.
[document-receipts.json](document-receipts.json) preserves all 29 PDF URLs, hashes,
byte/page counts and text screening results.
[archive-receipts.json](archive-receipts.json) records the index checks and link
labels. Label years and upload-path year tokens are distinguished: neither alone
establishes a schedule period. Encoded spaces and punctuation are normalized when
checking whether a lead was already known; they are not counted as new sources.

| Work | Result | Next action |
|---|---|---|
| Pitt Meadows 2013, 2019–2022 | 223 employees, 37 council ready; every rendered row checked | Register the reviewed collection and expose its exact source residual warnings |
| Parksville 2025 | 72 employees, 7 council; exact monetary controls | Register with the retained council adoption evidence |
| Revelstoke 2025 | 65 employees, 7 council; small visible issuer residuals disclosed | Register with the retained source warnings |
| Revelstoke 2021–2024 | Named employee and council schedules located; exact schedule years inspected | Review all fields, scope and controls; 2022 has an imperfect OCR-like text layer |
| Pitt Meadows 2011–2012, 2014–2018, 2023–2025 | Originals already retrieved; mostly scanned/mixed salary pages | Locate and review salary tables; run bounded OCR where needed |
| Mission 2023–2025 | All three originals retrieved, without embedded text | Locate schedules and OCR; verify actual schedule years, complete rows and controls |
| Port Moody 2021–2025 | Original text tables available with held layouts | Resolve wrapped titles, separate pay/tax-benefits-and-payouts/expense definitions and full controls |

The [reviewed collection guide](../../sector-municipal/README.md) explains the exact
pay definitions, five rendered-source corrections in the Pitt Meadows 2013 text
layer, all residuals and reproduction commands. Agreement of PDF readers is one
check; it does not replace visual name/title/row/period review. No individual value
was adjusted to balance a subtotal. No compiled records were removed or aliases
changed. [compiled-overlap.json](compiled-overlap.json) preserves the partial
Pitt Meadows 2020 versus compiled `2020/21` comparison for central review.

Revelstoke's previous audit route was its homepage. Its
[Financial Documents](https://revelstoke.ca/86/Financial-Documents) archive links
the 2021–2025 SOFI originals; all five are now fingerprinted. This provides a clear
historical processing sequence. Parksville's 2025 PDF was already an unvalidated
audit lead. This pass added extraction, reconciliation and the official
[June 15, 2026 minutes](https://parksville.civicweb.net/document/82769/), resolution
26-129, approving the SOFI as presented despite the agenda copy's unsigned form.
The new Powell River
[financial statements/SOFI folder](https://powellriver.civicweb.net/filepro/documents/280/)
remains an archive lead; no individual schedules or periods are inferred from the
folder alone.

The other checked archives are Central Saanich, Chilliwack, Clearwater, Coldstream,
Colwood, Courtenay, Dawson Creek, Esquimalt, Langley Township, Nanaimo, Oak Bay,
Port Alberni, Powell River, Rossland, Salmon Arm, Sidney, Summerland, West Kelowna
and Williams Lake. A 200 response with no detected salary link is a deeper archive
research task, not proof that a report must be requested. Port Alberni's old audit
target returned 404 and needs a replacement archive route. Existing 98-report OCR
artifacts remain indexed in `municipal-ocr`; this pass does not redo that completed
batch. Newly retrieved Mission/Pitt Meadows/Port Moody/Revelstoke/Parksville PDFs
were outside that batch.

The inherited procurement list is preserved separately inside `findings.json`,
with its audit provenance and **not-sent** status. It contains these specific
blocking requests:

| Municipality / year | Material to obtain or resolve |
|---|---|
| Abbotsford | Public adopted SOFI, existing spreadsheet and index of historical years; finance page says available on request |
| West Kelowna 2025 | Final/adopted SOFI or adoption evidence for the draft-linked tables |
| Salmon Arm 2025 | Actual named employee and council schedules; current SOFI-labelled attachment lacks them |
| New Hazelton 2022/2023 | Separate adopted schedules and confirmation of their periods; attachment and schedule years conflict |
| Surrey 2025 | Explanation or amendment for $473 named expense-control difference |
| North Vancouver City 2022 | Explanation or amendment for $143 expense difference |
| Montrose 2023 employees | Explanation or amendment for $36 expense difference; council already accepted |
| Creston 2024 employees | Existing spreadsheet or clearer original to resolve glyph/control ambiguities |
| Terrace 2022 | Clarification of printed expense-inclusive grand total; accepted remuneration/expenses reconcile |
| Clinton 2024 / Salmo 2024 | Clarification of small printed remuneration subtotal differences already disclosed |

Use a routine request to Finance/Corporate Services for existing public SOFI
schedules and electronic tables first. If routine access does not resolve a gap,
verify the municipality's official FOI process, recipient and any fee before filing.
No municipal requests or messages were sent. Readily available scanned reports
belong to the processing queue; they are not automatically FOI work.

The existing [province-wide coverage table](../../municipal-audit/coverage.md)
remains the full 161-jurisdiction roster. This follow-up covers 24 priority archive
checks and does not claim that every historical document has been found. Police
and regional district work are tracked by the other sector agents.
