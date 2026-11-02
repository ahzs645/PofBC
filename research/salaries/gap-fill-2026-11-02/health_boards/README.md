# Health board history gap fill

This pass processes leads063–065 and the root-approved board components of four Providence SOFI reports recovered alongside employee schedules. All25 original board reports received complete paired native-reader comparison: **323 named observations**, comprising **266 numeric-remuneration observations** and **57 supporting observations with nonnumeric remuneration**. There are23 nonempty app candidate cohorts. Two Providence reports have no numeric remuneration and remain supporting research only.

The finite board targets are fully processed: Island Health FY2015/16–2025/26 (11 reports); PHSA FY2015/16–2023/24 (nine); and VCH FY2022/23 (one). Two broken Island links were recovered through exact official Legislative Library item→ORIGINAL→content relationships. The VCH archival file contains a catalogue cover, board schedule and continuation notes, not an employee schedule. No employee-coverage conclusion is inferred from its board scope. Four additional Providence reports cover2020/21,2021/22,2022/23,2024/25; already accepted Providence2023/24 is not reimported.

## Payment definitions and exclusions

Modern PSEC-style annual totals include expenses. Remuneration sums numeric retainers, meeting fees and separate travel per diem; meeting rates and attendance quantities are not added. Older schedules with a distinct remuneration total use that column directly. Reports without a separate expense reimbursement column have null expenses. A printed zero remains zero; a blank/dash is not invented as zero. Nonnumeric-pay rows retain their original names, expenses and cells as supporting evidence.

Island2023/24 Harold Cull has dash remuneration components and a separately printed expense-inclusive$0 total. His remuneration is not inferred from that total. Island2018/19 Diane Brennan has unknown remuneration and$657 expenses, contributing to the full board control but not the app's numeric-pay subset.

Providence2022/23 imports10 numeric-pay rows with$1,987 known expenses; six excluded observations carry$1,157, explaining the full$3,144 board control. Providence2024/25 imports nine numeric-pay rows with$4,046 expenses; the excluded seven carry$2,404, explaining the full$6,450 control. All38 Providence observations in2020/21 and2021/22 have dash remuneration and remain supporting-only; their$231/$1,372 expense controls reconcile.

Source spellings remain literal: Andrew Adams versus Andy Adams; Anne Davies versus Anne Davis; Providence's printed Keility in2021/22. Adjacent superscript footnote numbers remain separately preserved annotations. Names are not resolved identities. Notes about earlier-year meetings paid later do not move payments to another fiscal period. Island2015/16 has two appointment-footnote dates after its heading's period; that inconsistency remains explicit.

Known-field grand residuals remain unadjusted: Island2018/19+1,2019/20+1,2022/23−1,2023/24+1; PHSA2018/19−1,2020/21−2,2022/23+1 CAD. Individual row differences remain separately documented. Some sources have no printed grand control. No component is balanced and no cause inferred.

## Fidelity and review

PyMuPDF rotated words/row bands and Poppler bbox words/independent nearest-name assembly compare every named row. Raw engine output, raw cells, interpreted components, source pages, literal control cells and excluded observations are committed. Each source's provenanceFile/provenanceSha256 and evidenceFile/evidenceSha256 identify within-collection files.

Original-PDF diagnostics inspect paint type/opacity/colors, replacement characters, glyph overprints, whole-word field edges and dark ink in200dpi renders. They identify review targets, not proof of every glyph. Version1 preserved a false conflict between a pay dash and nonprinting NBSP. Version2 correctly excludes Unicode whitespace from visible-glyph conflicts and preserves37 review-region edge crossings. Those words are retained whole by center assignment rather than clipped; actual column placement is supported by separate human source views. No hidden/low-opacity/near-white/replacement text, visible-glyph overprint conflict or word without dark rendered ink was found in the25 table regions. Complete paired native comparison and bounded literal image readings remain distinct.

Repeated VCH library downloads produced different PDF bytes for the same ORIGINAL contentURL. First native evidence and raster fingerprints remain archived; the second selected download is explicitly content-hashed. All three physical pages have exactly equal word coordinates in both readers and equal full-page200dpi PNG bytes across the two observed representations. This is not a raw byte-identity claim. The first raw cache file was overwritten before freeze, disclosed in vch-2022-23-source-variant-adoption.json. Future fetches are write-once by content hash. No old receipt transfers automatically to the new hash.

## Reproduction and acceptance

- Offline replay: `python3 scripts/gap_health_boards.py --check`.
- Actual-source regressions: `python3 -m unittest discover -s scripts -p test_gap_health_boards.py -v`. Standard library and committed fixtures suffice.
- Original-source replay: `python3 scripts/gap_health_boards.py --originals`, using PyMuPDF1.26.6, Poppler and the exact pinned PDFs at source-spec paths.
- `gap_health_boards_fetch.py` refreshes issuer routes; `gap_health_boards_library.py` follows exact catalogue relationships. Newly downloaded raw representations never silently replace selected hashes.
- `gap_health_boards_visibility.py` recomputes visibility-v2 diagnostics from the exact PDFs.

Root independent acceptance is selected by review-adoption.json. Until adoption, manifest status remains candidate. Promotion verifies every reviewed PDF/data fingerprint, including two supporting-only reports. The worker freeze covers only worker-owned files; root review documents remain separately owned and referenced by explicit hash. No earlier source, compiled partition or global app output is changed by this worker.

No institution request, email, form, FOI application or fee was sent. NIC, McBride, SD8 and SD10 issuer requests remain on hold.
