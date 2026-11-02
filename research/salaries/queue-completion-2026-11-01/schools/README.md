The new `queue-completion-schools` collection contains 22 complete published employee/trustee scopes from 11 original school reports for 2024/25: SD22, 23, 27, 33, 36, 43, 44, 50, 61, 68 and 73. The 15,138 observations comprise 15,051 employee rows and 87 trustee/official rows. All compiled partitions are retained. The final manifest becomes verified only after the independent peer receipts are pinned.

Ten native reports retain independent Poppler physical-layout and MuPDF geometric readers. SD61 has one explicit image-verified name/title boundary amendment; its raw merged word remains preserved. Its employee v2 also removes separate centred footer numbers from 20 page-final positions, following a complete independent image ledger. The bounded name/title crop is 216 dpi; an additive image receipt corrects an erroneous resolution phrase in the frozen amendment description. SD50 retains two separate OCR readers, four image-verified null expense dashes, a complete independent image transcript, and an additive revision fixing the shared capital-I/l error in `Keir, Ian J.`. The unamended SD50 and SD61 employee files are revision evidence and are not registered.

The existing 398 accepted SD10/SD8 observations remain unchanged. Thirty-one public-route receipts include fresh unchanged originals, SD10's second abridged copy, later board records and public search limitations. The declaration/management conflicts, SD8 heading/aggregate differences and missing explicit SOFI adoption evidence remain issuer questions. Concrete request drafts are frozen and unsent under `../acquisition/outbox/`.

Replay the frozen text/OCR fields, amendments, payloads and source fingerprints with:

```sh
python -m unittest discover -s scripts -p test_finish_salary_schools.py -v
python scripts/finish_salary_schools_scan.py --check-amendments
python scripts/finish_salary_schools_revisions.py --check
python scripts/finish_salary_schools.py --check
python scripts/finish_salary_schools_clarifications.py --check
python scripts/finish_salary_schools_discover.py --verify-receipts
python scripts/finish_salary_schools_freeze.py --check
```

The complete original-native replay additionally requires the pinned PDFs in the paths recorded by `native-source-specs.json`, PyMuPDF and Poppler:

```sh
python scripts/finish_salary_schools_native.py --check
```

Original PDFs, full rendered pages and models remain in `/tmp`; two small corrective source crops are committed in `images/`. No global registry, generated export, old frozen source, branch or institution contact was changed by this worker. The remaining 25 current district processing gaps and earlier historical runs are outside these 22 scopes and are not reported as accepted or as procurement blockers.
