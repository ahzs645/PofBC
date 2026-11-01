# Capital and Cowichan next pass

Audit date: **October 31, 2026, America/Vancouver**; baseline `5e5fe01`. The bounded search covered the twelve assigned municipalities: Colwood, Esquimalt, Highlands, Ladysmith, Lake Cowichan, Langford, Metchosin, North Saanich, Oak Bay, Sidney, Sooke and View Royal.

The [reviewed collection](../../municipal-wave-capital/README.md) adds **547 official observations in 20 employee/council cohorts across nine municipalities**. The other three municipalities have located originals awaiting source-specific processing. No compiled observations were deleted and no requests were sent.

Start with [work-queue.json](work-queue.json), a normalized list of remaining processing, archive research and clarification tasks. [findings.json](findings.json) gives accepted years/categories, original retrievals and next actions for all twelve municipalities. [retrievals.json](retrievals.json) records exact original URLs, HTTP results, hashes, page counts and text diagnostics. [index-receipts.json](index-receipts.json) and [baseline-leads.json](baseline-leads.json) preserve discovery context. Downloaded originals and rendered review pages are cached under `/tmp/wave-capital`.

These inventories distinguish accepted actual calendar years from **index labels**, document retrieval and unfinished table review. A readable text layer elsewhere in a PDF does not establish that its salary table is native text.

| Municipality | Result and remaining work |
|---|---|
| Colwood | Accepted 74 employees for 2025. Council table on physical page 9 needs OCR; older SOFI index labels extend from 2011 through 2024. Retrieved 2011 is image-only; 2024 remains unparsed. The 2025 DRAFT watermark is disclosed alongside signed approval of all schedules. |
| Esquimalt | Accepted 86 employees and seven council observations for 2025. Official index labels extend back to 2014; 2024 and image-only 2014 originals are retained for further native/OCR work. |
| Highlands | Accepted the 2024 annual-report schedule: four named employees and seven elected officials. Find other salary-bearing annual-report appendices and verify their actual years. |
| Ladysmith | Accepted 39 employees and seven council observations for 2025. Official SOFI index labels cover 2021–2025; 2021 and 2024 originals are retrieved and await complete review. |
| Lake Cowichan | Accepted 2023 employees/council, 2024 council, and 2025 employees/council. All eight 2024 employee rows are held for a material $5,000 row-total conflict despite exact aggregate controls. Earlier annual reports remain archive leads. |
| Langford | Accepted 130 employees and seven council observations for 2025. Official SOFI labels extend back to 2010; 2010 and 2024 originals are retained. The archive also indexes earlier annual reports, whose salary content is not established. |
| Metchosin | No observations accepted. The 2025 notes are native text, but the salary table on physical page 39 is an embedded image with separate remuneration/taxable-benefit columns. Complete OCR and component-definition review. Reuse existing 2024 two-pass staging rather than mistaking its discovery for acceptance. |
| North Saanich | Accepted 44 employees and seven elected officials for 2025, including two distinct published Munro, S rows with different positions/amounts. Older SOFI labels 2019–2024 remain processing work. The 2024 mixed original already has prior OCR staging. |
| Oak Bay | Official 2024 and 2021 originals retrieved. The 2024 employee table is a wide, native layout on physical pages 51–53, with separate surname, given name, department and position; council is on page 50. Full row/layout/control review remains. The 2025 annual report is an additional unverified salary-appendix lead. |
| Sidney | Accepted 53 employees and seven elected officials for 2025. Official financial-reporting page labels SOFI 2018–2025; the 2024 original is retrieved and awaits review. |
| Sooke | Official 2025 original retrieved. Native employee pages 37–38 contain wrapped titles above/below payment baselines and nearby footer numbers. Complete the source-specific layout review and controls before acceptance. |
| View Royal | Accepted 34 employees and seven elected officials from the 2025 annual-report appendix. Earlier annual reports are indexed, but their salary content/years remain unverified. A legacy link labelled 2010 points to an FIA2009 filename, demonstrating why the original schedule must establish the year. |

There is one concrete **clarification request**: Lake Cowichan 2024 employee cells and the conflicting printed total. Obtain an amended report or an explanation identifying the correct fields. No formal FOI is necessary merely to retrieve the other located originals: those are processing tasks. Deeper archive research remains appropriate for earlier periods, with an ordinary records request or formal FOI fallback considered only if public retrieval fails and the applicable access route is established.

The parser’s two readers compare every field; the independent rendered edge checks also prevent shared geometry mistakes. During final review a first-row currency marker had been assigned to a Langford job title by both readers. The column boundary was corrected; text fields now reject currency markers, and literal first/last title regressions cover every reviewed table boundary. Original monetary values and controls were unchanged.

Reproduction and thirteen regression tests are described in the collection README. Source expansion is frozen at this handoff; the queue makes the remaining work explicit.
