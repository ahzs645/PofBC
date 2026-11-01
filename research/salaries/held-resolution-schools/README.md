# Qualified school period resolutions

Three complete scopes add **398 observations**: Arrow Lakes FY2024/25 employees (53) and trustees (5), and Kootenay Lake FY2025/26 employees (340). Existing trustee sources, older held evidence, source collections, queues and global/generated files are unchanged.

Arrow Lakes' complete remuneration tables on original physical pages 47–48 explicitly print fiscal year ended June 30, 2025. Those headings establish the observed payment period. The declaration body on page 3 certifies June 30, 2024 despite its 2024–2025 year field and visible signatures dated December 18, 2025. Management page 5 prints December 18, 2024 under a June 30, 2025 header. These contradictions remain unresolved: the warning does not infer a typo or establish 2025 SOFI approval/adoption. The actual 2024 SOFI has its own 2024 salary headings and different amounts; the district and Ministry 2025 salary pages are pixel-identical. Complete package contextual OCR, relevant original images, separate financial statements and adjacent adopted board records were checked. The financial statements' September 2025 approval is not treated as SOFI adoption.

Kootenay Lake uses the separately posted SOFI as the payment-source original, physical pages 51–59. Its page 52 says June 30, 2025; the other employee pages say June 30, 2026. The September 8, 2026 public board agenda supplies specifically dated period corroboration: all nine salary pages 185–193 say 2026 and every one of the 340 names, remuneration/expense components, row order and multiplicity agrees with the posted original under page mapping +134. The memorandum on agenda page 134 explicitly describes the attached remuneration schedule as for year ended June 30, 2026. This is complete dated row corroboration, not upload-filename inference or a silent repair of page 52. The resulting data hash equals the old held payload exactly; no payment or page was changed.

The agenda contains unsigned forms and DRAFT/Not Finalized marks within its embedded financial-statement subsection; its remuneration pages are unmarked. The whole agenda is not promoted to a final payment original. The posted SOFI has no native draft marks; approval date fields read September 8, 2026 with signature areas redacted, and management dates read August 28, 2026. The adopted board minutes record SOFI presentation, with no explicit SOFI adoption motion. These limits remain public.

All named component controls reconcile exactly:

| Scope | Rows | Remuneration | Expenses |
|---|---:|---:|---:|
| Arrow Lakes trustees | 5 | $69,248.51 | $12,525.55 |
| Arrow Lakes employees | 53 | $6,036,402.68 | $89,295.97 |
| Kootenay Lake employees | 340 | $37,683,809 | $414,506 |

Kootenay Lake has an additional unresolved aggregate control difference: posted SOFI reconciliation page 64 prints $56,431,182 remuneration and $594,827 expenses; consolidated schedule page 59 prints $56,431,196 and $594,437. Reconciliation minus schedule is −$14/+ $390. Both remain literal, with no balancing adjustment or inferred cause. This qualification does not change the exact complete employee schedule.

Arrow Lakes has a complete original-image manual transcript, two independent OCR engines (Tesseract LSTM and Paddle PP-OCR through RapidOCR/ONNX), and full independent peer image review. Raw OCR text, boxes/confidence and 64 explicit text-only image corrections are retained; no monetary correction was required. Names and clipped titles remain literal, including `Momeyer, Erika C.`, `McLellan, Michael` and `TEACHERS, TEACH ON`. Kootenay Lake has independently implemented Poppler lexical and PyMuPDF geometric readers over all 340 rows in both originals, plus the separate independent peer reader receipt described in the handoff. No full manual reading of all 340 rows is claimed.

The six fields are `[employerSlug, name, position, remuneration, expenses, pdfPage]`. Blank/dash expenses remain null, explicit zero stays zero, and missing positions remain null. Remuneration and expenses are separate cash-basis reported payments, not annual base salary. Under-threshold aggregates, employer CPP/EI, suppliers and financial-statement totals are excluded. Kootenay Lake expense footnote markers are retained in evidence without becoming money or inferred titles.

Offline replay and tests require only the committed evidence:

```sh
python3 scripts/resolve_held_schools.py
python3 -m unittest discover -s scripts -p 'test_resolve_held_schools.py'
```

Pinned original replay reruns Arrow Lakes Tesseract and both native readers in both Kootenay Lake originals:

```sh
python3 scripts/resolve_held_schools.py --originals
```

To rerun the independent Paddle engine as well, add `--rerun-rapid`. It uses the research-only read-only environment `/tmp/held-health-ocr/venv`; model hashes, versions, acquisition URLs and licenses are pinned in the research engine receipt. Originals, images and models stay in `/tmp`.

Rebuild an unfrozen candidate in order with `python3 scripts/resolve_held_schools.py --build`, then `python3 scripts/resolve_held_schools_sd08.py --build`. Do not run build against a frozen release; later changes require a new receipt/version. See [the handoff](../held-resolution-2026-11-01/schools/handoff.json) and [research README](../held-resolution-2026-11-01/schools/README.md) for exact assumptions, review coverage, sources/hashes and changed queue. No contact, request, fee, branch action, commit, push or publication occurred in this worker task.
