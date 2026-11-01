# Southern Interior follow-up inventory

This bounded pass follows the earlier province-wide audit for Thompson–Nicola, the Okanagan, Columbia–Shuswap, the Kootenays and Squamish–Lillooet. It prioritizes new municipal employee coverage and preserves historical sources for continued processing.

The [accepted collection](../../municipal-wave-interior/README.md) contains **299 official observations**: **233 employees and 66 elected officials**, across nine municipalities and 11 calendar municipality-years. Existing compiled data and aliases were not changed by the Interior importer.

Start with:

- [`findings.json`](findings.json): municipality coverage, accepted years, located originals, prior audit leads and limitations.
- [`source-inventory.json`](source-inventory.json): exact report URLs, hashes, archive labels, text status and candidate physical pages. Located/indexed years remain distinct from verified accepted periods.
- [`discovery-receipts.json`](discovery-receipts.json): 91 retrieval receipts, including 68 original PDF URL receipts representing 67 distinct PDF hashes.
- [`work-queue.json`](work-queue.json): normalized processing, public archive research and clarification tasks. OCR and parsing are processing work, not procurement.
- [`edge-review.json`](edge-review.json): first/last row and wrapped-title boundary checks against rendered accepted pages.
- [`held-cohorts.json`](held-cohorts.json) and `held-evidence/`: the original held Princeton/Coldstream review packages. Their current status is **accepted with qualification after independent review**; their clarification work remains open. No source amounts or missing cells changed.

## Recovered archives

Official source links yielded substantial histories alongside the accepted cohorts:

| Municipality | Located report labels / periods awaiting individual verification |
| --- | --- |
| Clearwater | 2012–2025, plus an earlier scanned file; 2023 and 2025 cohorts accepted |
| Rossland | 2010–2025 with gaps/duplicate links requiring original review; 2025 accepted |
| Sparwood | 2012–2025; 2024 and 2025 accepted |
| Lytton | 2015, 2017–2018, 2020–2025; scans and recognition errors need source review |
| Barriere | 2020, 2023–2024; 2023 accepted, other retrieved copies are scans |
| Trail | 2022–2024 originals retrieved; complete table/column review remains |
| Princeton | 2022–2023; 2023 accepted with explicit employee expense qualification |
| Summerland, New Denver, Sun Peaks, Coldstream | Accepted originals plus retained official archive routes |
| Radium Hot Springs | 2021 scanned original retrieved |

These are discovery ranges, not claims that every report or employee row is accepted. A later upload date is not a salary year. CivicWeb duplicate document URLs sometimes return identical PDFs; hashes prevent those links from becoming duplicate imports. OCR layers may contain corrupt names or titles even when monetary totals match, so source glyphs and row boundaries still need checking.

The queue retains source-discovery work for other priority municipalities, including Armstrong, Ashcroft, Enderby, Fernie, Grand Forks, Invermere, Kimberley, Lake Country, Oliver, Osoyoos and Spallumcheen. Those existing audit leads were not treated as proof of unavailable records or a completed exhaustive historical search. Pending Okanagan Falls incorporation is excluded from current-municipality missing-year tasks.

## Remaining issues and procurement routes

**Merritt 2025 remains held.** Its named remuneration subtotal **$4,779,040.10** plus under-threshold **$2,876,685.82** totals **$7,655,725.92**. The printed `Total Employees (B)` **$7,842,227.42** is **$186,501.50 higher**, exactly the separately printed council remuneration. Ordinary and grant-funded expense columns require complete component/scope review before an import. The original is already retrieved; this is processing and definition review before any possible clarification request.

**Princeton 2023 and Coldstream 2021 are accepted with visible qualifications**, after every employee field was independently reread and rendered originals checked. Their known expense control differences are **−$44.78** and **−$300**, respectively. No value was imputed or rescaled. The queue retains clarification tasks for an explanation or amended original, without making publication of faithful qualified rows depend on an answer.

Other already downloaded reports need complete row extraction, OCR where necessary, actual calendar-period verification and full available component controls. Earlier unlocated histories require deeper public finance/council archive research first. An ordinary request for an existing original PDF or spreadsheet is the next route if those public retrieval routes fail; formal FOI is a fallback, not a synonym for unread or scanned documents. No municipality was contacted, no request was filed and no fee was committed.

## Reproduction

Accepted source reproduction and tests are described in the collection README. Current cache: `/tmp/wave-interior`.

```sh
python3 scripts/wave_interior.py --cache-dir /tmp/wave-interior
python3 scripts/wave_interior_inventory.py --cache-dir /tmp/wave-interior
python3 -m unittest discover -s scripts -p 'test_wave_interior.py'
```

Both scripts support `--fetch` for missing pinned PDFs. Originals are downloaded from exact retained public URLs and fingerprints are checked; PDFs are not copied into Git. Inventory regeneration reads the retained index/document receipts and inspects originals; it does not convert candidate text or located documents into accepted rows.
