# Postsecondary recovery wave — 2026-11-01

Four official original employee schedules,9,987 named rows: UBC FY2025/26 (9,633) and Coast Mountain College FY2022/23–2024/25 (91,124,139). Prior sources and global/generated files are untouched. This is a frozen candidate collection for parent peer review and registration.

| Original | Physical employee pages | Row remuneration | Row expenses | Row sums minus printed named control (pay / expenses) |
|---|---|---:|---:|---:|
| UBC2025/26 |42–189|$1,401,982,434|$35,281,528|$0 /$0|
| Coast Mountain2024/25 |34–38|$15,195,816|$546,451|+$2 /−$1|
| Coast Mountain2023/24 |33–36|$13,225,819|$468,420|−$1 /+$6|
| Coast Mountain2022/23 |34–36|$9,399,254|$338,937|−$3 /+$1|

Every ordered name, component cell, row/page boundary and multiplicity is compared by independently implemented PyMuPDF positioned-word and Poppler physical-layout readers. Evidence retains both complete inputs and per-row source tokens. All original expense-inclusive Total cells at Coast Mountain are independently compared as separate evidence. Published values are never balanced. The small control differences remain explicit public warnings; their causes are unresolved. FY2023/24 printed named-plus-below-threshold pay is also$1 above the printed grand total. All controls, cumulative carry comparisons and individual source Total/component differences are in the manifest and control-review receipt.

All are fiscal April1–March31 periods confirmed from actual schedule headings. UBC reports cash payments; expenses are gross, unadjusted for external recoveries. President/faculty/staff/student employment amounts for Board members are expressly in the employee schedule. Separate Board activity expenses, supplier payments, employer CPP/EI and below-threshold aggregates are excluded. Coast Mountain remuneration is literally Salary Plus Benefits; its separate Total includes expenses, and its reconciliation separately identifies employer benefits. Titles are unpublished and stay null. Missing/dash expenses stay null, literal zero would stay0, and all11 UBC negative expense amounts remain negative. UBC's27 duplicate-name groups retain source multiplicity.

Coast Mountain FY2023/24 and FY2024/25 approval pages show autograph signatures. FY2022/23 has Board approval wording but an unsigned line, typed Acting Chair and date; this genuine official original is qualified explicitly, without claiming independent adoption. Its Helfensteller dos, Vito surname field is visibly clipped and retains the common native-reader text without completion. UBC's consolidated management page displays literal[signed] labels dated June24,2026; its employee schedule is unaudited and no separate autograph approval was identified.

Full native reader comparison covers every table page. Rendered review is sampled and recorded exactly in `../recovery-wave-2026-11-01/education/visual-review.json`: UBC full pages3,40,41,42,49,189,190 plus all11 negative-expense cell crops; each Coast Mountain report approval, first/last employee, separate Board and reconciliation pages. No full rendered review of all UBC employee cells or independent OCR is claimed. Original PDFs and rendered images remain under/tmp; hashes and reproducible render tooling are included.

UBC has no same-label compiled partition. Coast Mountain FY2023/24 has124 compiled rows. The compressed full comparison contains raw rows, exact multisets and every one-to-one link. Differences are12 source missing expenses versus compiled0, and3 lost-hyphen spellings. The separate Board schedule and complete employee scope were reviewed. No compiled row remains unmatched after those documented presentation differences. Root decides any replacement; this collection does not alter a compiled partition.

North Island College FY2019/20 remains held: the nine-page scan includes only employee printed pages2of5 and4of5. Printed employee pages1,3,5 are missing, so OCR alone cannot close the lead. A source/printed-page crosswalk, image hashes, OCR discovery text and an ordinary existing-record request draft are retained. CNC FY2020/21 remains held because hidden versus rendered surname text disagrees; no row was accepted. The existing SFU material-control holds remain unchanged.

Reproduce with Python3, PyMuPDF1.26.6, Poppler25.03.0 (`pdftotext`). From repository root:

```sh
python scripts/recover_wave_education.py
python scripts/recover_wave_education.py --originals
python -m unittest discover -s scripts -p 'test_recover_wave_education.py'
python scripts/recover_wave_education_review.py --originals --render-review
```

The first command replays the compressed evidence without PDFs. `--originals` rereads all source PDF tables. `--build` regenerates this new collection from the four pinned/tmp originals, and should be used only before freeze or in an isolated copied output directory. Review tooling is read-only by default; rendering recreates review images without claiming new human inspection. Original URLs, cache paths and SHA256s are in sources.json and the handoff. Re-download exact URLs to the stated cache paths if caches are absent, and require matching SHA256s; do not substitute changed documents silently.
