# BCCSS 2017/18: scanned employee schedule verified

Reviewed 30 October 2026. This import contains **346 named employee records** for
the **BC Clinical and Support Services Society**, mapped to
`bc-clinical-and-support-services-society`. The original report is hosted on PHSA's
website, but it explicitly names BCCSS as the employer. It is a separate cohort.

The source reports remuneration **strictly over $75,000** for the fiscal year ended
31 March 2018. Its cover describes a cash-receipts basis, including salaries/wages,
taxable benefits, bonuses and stipends. The normalized rows sum exactly to the
printed **$33,202,601 remuneration** and **$1,352,527 expenses**. All **59 expense
dashes remain null**. No job titles are published. The adjacent 2016/17 report's
inclusive threshold is not applied to this year.

## Evidence and review

- Original PDF SHA-256:
  `8c74494d2b3fb201f48fa8243af20dd92070fb5cab5750728f86d77976522140`.
- Eleven physical pages: one cover and ten employee pages. Pages 2–10 have 35 rows
  each; page 11 has 31 rows and the named totals.
- Two OCR passes use Tesseract 5.3.4 at 250 dpi / segmentation mode 6 and 300 dpi / mode 4.
  Raw text, text hashes and rendered-PNG hashes for both passes are preserved in
  [review/2017-18-ocr-passes.json.gzip](review/2017-18-ocr-passes.json.gzip).
- The cover and every employee page were visually inspected. This is essential:
  the two configurations use the same engine and can share errors.
- [review/2017-18-review.json](review/2017-18-review.json) contains 21 guarded
  before/after correction occurrences covering 17 distinct rows. The corrected
  passes agree exactly on every name, remuneration, expense and physical page,
  in source order. Both independently reproduce the printed count and totals.

Shared OCR mistakes included `Ahmad,Waqar` (q misread as g), `Krcmar,Norm`
(c misread as e), and `Cozma,Iacob` (capital I misread as lowercase l).
One pass misread `Ahsan,Muhammad` remuneration as 71,154; the image clearly shows
77,754. Both passes read `Zanatta,Marco Antonio`'s 747 expense as `TAT`; the image
establishes 747. These are image-grounded corrections, not adjustments chosen to
balance totals. Ordinary comma spacing is normalized without expanding names.

The final employee, **Van Gogh, Justin**, appears after the Z names and is retained.
Alphabetical ordering is not used as a rule to discard records. No duplicate
payment rows were found. Disclosure names do not establish unique identities.

## Reproduction

```sh
python3 scripts/import-bccss-ocr-salaries.py --pdf /path/to/bccss-2017-18.pdf --offline
```

The command verifies the original PDF fingerprint, checks the saved raw OCR
hashes, applies only complete matching correction contexts, validates every page,
compares both corrected passes and checks all controls before writing normalized
outputs. Without `--offline`, it downloads a missing source from the exact URL in
[sources.json](sources.json).

This is a reproducible rebuild from the locked reviewed OCR evidence, not a claim
that fresh OCR will always emit the same text. Different OCR software or changed
source bytes require another review. Rebuilding does not certify a new visual
inspection or publish the output by itself.
