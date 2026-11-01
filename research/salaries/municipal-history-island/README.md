# Island and coast municipal histories

This collection adds **934 official disclosure observations in 74 separately defined employee or council cohorts**, from **37 reports across nine municipalities**. There are **714 employee** and **220 elected-official** observations. Three jurisdictions had no accepted official records in the frozen baseline: Lantzville, Port McNeill and Tofino. No compiled observation is deleted, relabelled or matched to a calendar year.

| Municipality | Newly accepted calendar years | Employees | Council |
| --- | --- | ---: | ---: |
| Courtenay | 2020–2024 | 439 | 36 |
| Cumberland | 2014–2024 | 115 | 61 |
| Gibsons | 2021–2024 | 64 | 22 |
| Tahsis | 2019–2023 | 9 | 27 |
| Ucluelet | 2023–2024 | 33 | 10 |
| Sayward | 2021–2022 | 5 | 12 |
| Port McNeill | 2021 | 3 | 5 |
| Lantzville | 2018–2020, 2025 | 25 | 25 |
| Tofino | 2012–2013, 2021 | 21 | 22 |
| **Total** | | **714** | **220** |

The baseline is recorded in [the history-pass baseline](../municipal-history-pass/baseline.json), commit `67d5cff`, with 919,955 dataset records. Existing accepted years and categories are rejected by the importer. Each source's printed calendar period is retained in `validation.periodProof`; later upload paths are not used as salary years.

## Source qualifications

Names, initials, roles, source spellings, abbreviations and adjacent name-column order remain as printed. No departments, identities, annual base rates or zero expense cells are inferred. Threshold comparators appear only when the original explicitly supplies them. Aggregates and suppliers are evidence controls, never individual salary records.

* **Ucluelet 2023:** Abigail Fortune's expense is literally printed `3,3463.64`. Her unambiguous $104,649.90 remuneration remains; the unusable expense is `null`. The literal and its positioned cell are preserved with a source/name/token guard. All 15 named employees remain represented, `completeEmployeeSchedule` is true, and `expensesComplete` is false in both source and validation. No comma removal or balancing inference supplies an expense. Known numeric expenses total $23,514.08 against the printed $26,977.72 named control; full expense reconciliation is unresolved.
* **Tahsis 2019 council:** all five individual rows were independently verified from the rendered original. Their pay sums to $29,124 against the printed $28,125, a **+$999** source residual; expenses match $16,175 exactly. Every individual cell remains unchanged, and the cause is unresolved. The public warning preserves this qualification. Signed approval is visible on physical page 28, dated August 18, 2020.
* **Tofino 2021 council:** remuneration uses the explicit **Remuneration column only**. Separately reported Benefits, totalling $15,560.49, remain in evidence and are excluded; inclusive total compensation is not established. Eight expense rows total $5,159.88 against the printed $5,165.88, a −$6 residual. The official posted report is not marked draft, but its physical-page-10 approval is an unsigned, undated template with highlighted names. Both accepted cohorts disclose that signed approval or adoption has not been established. The employee below-threshold expense aggregate is `n/a`, so a named-employee expense comparator is unavailable. Known named expenses $16,773.81 versus printed all-employee expenses $16,773.82 are a comparison of different scopes; the −$0.01 difference is not a named expense reconciliation. The same unavailable-comparator rule applies to Tofino 2012: known named and printed all-employee expenses both equal $39,581.30, but that equality does not establish a named control or convert below-threshold `n/a` to zero.
* **Port McNeill 2021:** separate expense-inclusive Total columns remain evidence only. Sinclair, Koel and Mitchell have blank expenses, retained as missing even when their printed Total equals pay. Council pay sums $62,699 against $62,698. The employee-page summary reports council expenses $2,426 versus $1,378 on the named council schedule; the unexplained $1,048 cross-schedule difference is visible in its public warning.
* **Lantzville 2025:** the actual salary page is scanned with embedded OCR. Every field in all 16 rows was transcribed from the image and independently compared with a second full human transcription. Jones's printed `(256)` expense remains −$256, without an inferred cause. Council named pay and subtotal agree at $93,290; the lower reconciliation instead says $93,289, an unresolved $1 difference. Both embedded and fresh OCR misread `Savage, Ian` as `Savage, lan`; the image establishes the capital I. Roman III/II and `Long, Aria` were checked directly. See the [independent full-image review](../municipal-history-pass/reviews/lantzville-2025-ocr.md).
* **Courtenay titles:** rendered cells clip Berard, A. in 2022 at `Perfo`, Wyka, R. in 2023 at `Busine`, and Wyka, R. in 2024 at `Performa`. Source/year/name/token guards remove Poppler-only hidden suffix glyphs and retain the visible PyMuPDF prefix. The full titles are not inferred. Wrapped titles that begin above a bottom-aligned name are assigned by native PDF cell order and independently checked against the source layout and rendered row boundaries. Legitimate `A.` initials are retained.
* **Courtenay 2020:** the original explicitly states that the calendar year includes an additional pay period beyond its usual 26. This affects comparisons with other years.

Other source-faithful residuals are itemized in each source's `publicWarning`, `printedControls`, `expectedNamedControl` and `rowSumMinusNamedControl`. No residual is assumed to be rounding, and no published amount is adjusted to make controls agree. Gibsons's expense-inclusive Total is never remuneration. Ucluelet explicitly labels its schedules unaudited and cash-based; other source-specific definitions remain in notes.

## Verification and reproduction

All **918 native observations** agree in independent PyMuPDF positioned-word and Poppler layout parsers after the three guarded visible-title corrections. Rendered inspection covered each native salary page, first and last named rows, wrapped edges, controls and source periods. The **16 additional OCR observations** use two complete human image transcriptions; two readers of one OCR overlay are not treated as independent native extraction. The [independent native review](../municipal-history-pass/reviews/island-native.md) covers the malformed expense, Benefits exclusion, visible clips, Cumberland wraps and qualified Tahsis residual.

The manifest pins original PDF, normalized JSON and compressed-data SHA-256 fingerprints. `extraction-evidence.json.gzip` retains complete native word pages, raw independent Poppler layout, individual cells, additional Total/Benefits values and printed controls. Original URLs, official indexes and retrieval receipts appear in the manifest and [audit inventory](../municipal-history-pass/island/inventory.json). Original binaries are cached outside the repository under `/tmp/pofbc-history-island`.

From the repository root, with Python, PyMuPDF and Poppler installed:

```sh
python3 -m unittest scripts/test_history_island.py
python3 scripts/import_history_island.py --offline-verify
python3 scripts/import_history_island.py --verify --cache /tmp/pofbc-history-island
```

The 15 tests exercise full offline two-reader evidence replay, initials, bottom-aligned roles, visible title clips, the malformed expense, Benefits exclusion, blank versus zero/negative amounts, expense-inclusive totals, actual periods, scan rejection, qualified residuals, unavailable-versus-zero aggregate controls and queue semantics. Offline replay reproduces all rows and controls from pinned extraction evidence; it does not replace checking an original PDF's fingerprint. For an empty cache, add `--download-missing` to the original verification command. Each downloaded original must match the pinned hash. `--write` regenerates this owned collection, and a second `--verify` checks identical normalized and compressed results. Gzip headers are fixed for portable reproduction.

This is a bounded historical expansion, not complete municipal history. [Remaining work](../municipal-history-pass/island/work-queue.json) distinguishes public originals needing processing/OCR, deeper public archive research, ordinary acquisition options and exact source clarification. No records request or external message was sent.
