# Continued name-connection review — 2 November 2026

This pass adds **43 source-spelling corrections** to the application: 13 retained
compiled spellings and 30 parsed official spellings. The reviewer personally read
112 original row crops on 12 contact sheets from 13 exact-hash PDFs. Fourteen of
the 57 proposed corrections remain held after reading the originals.

The entire previous **3,268-pair held queue** is reconciled in
[review-results.csv](review-results.csv) and [review-results.json](review-results.json):

| Outcome | Candidate pairs |
| --- | ---: |
| Connected by verified evidence | 35 |
| Kept apart: separate named rows in an original schedule | 60 |
| Still held | 3,173 |
| Starting held queue | 3,268 |

Of the 35 verified pairs, 34 acquire their verified connection in this pass; one
was already connected through earlier verified aliases. Ten other pairs already
share an application history through a **likely** link. They remain in the held
count and are not upgraded. Source-spelling corrections, resolved candidate pairs
and newly discovered people are different measures.

Examples of accepted corrections:

| Retained spelling | Original preferred spelling | Source |
| --- | --- | --- |
| Salvatinova, Ramona | Salvarinova, Ramona | PHSA 2019/20, PDF p.94 |
| Grenman, Jonathan Troy | Grennan, Jonathan Troy | PHSA 2019/20, PDF p.40 |
| Symnes, Anne R. | Synnes, Anne R. | PHSA 2021/22, PDF p.162 |
| Cheny, Shalman | Cherry, Sharman | PHSA 2023/24, PDF p.43 |
| Mackey, Jolm | Mackey, John | PHSA 2023/24, PDF p.158 |

Each accepted spelling has its actual source URL and physical PDF page in the
[review plan](review-plan.json), pinned row and PDF hashes in
[continuation-reviewed.json](../continuation-reviewed.json), and unretouched
source pixels in [renders](renders). Application histories expose the evidence
links. All original observations and their disclosed spellings remain available.

Finding the correct third name does not establish the original proposed pair.
For example, the original corrects “Munay, Melanie” to “Murray, Melanie”; it also
lists “Munday, Melanie” separately. Those candidate names stay apart. “MacKay,
Jolm Alan” is not joined to the corrected “Mackey, John” without further evidence.

## What remains held

| Reason | Pairs |
| --- | ---: |
| Two primary spellings still need affirmative identity evidence | 2,562 |
| A complete unique financial row has not been established | 366 |
| Primary-source observations are still needed | 218 |
| Direct original-row review found a printed variant or incomplete compiled witness | 14 |
| Related spelling corrected, but the original pair is not established | 2 |
| Already connected by a likely path, still unverified | 10 |
| Pittman: identity supported; currency handling still required | 1 |
| Total | 3,173 |

The older originals really print Bailey, Katherine; recent ones print Bayley,
Katherine. The originals also print both Smith/Smyth, Sharon and Neilsen/Nielsen,
Murray in different years. These are not accepted as extraction corrections.
Names, employer and a plausible payment history alone do not establish a
verified identity. The individual reasons are in [visual-review.json](visual-review.json).

Unknown expenses stay unknown. A printed McIvor/McIver/MacIsaac spelling does
not authorize connecting every compiled observation when complete financial
witnesses are missing. No unknown expense is substituted with zero.

Pittman remains held from a new join. The official BCI review identifies the later
amount as USD executive total compensation. Every record surface and derived
comparison needs consistent currency handling before that join: explicit USD
display; exclusion from CAD rankings, averages, raises and charts; continued
access to the original row; and evidence for any conversion. No exchange rate,
payment definition or reporting label is assumed. See the earlier
[BCI findings](../connection-review-2026-11-02/case-findings.json).

Other employers remain represented in the queue. This pass concentrates personal
original-row review on PHSA extraction errors; it does not claim that all held
pairs received a new biography search or that all historical identities are known.
The full queue was checked against current verified source relationships. A likely
edge cannot supply another name's primary rows or close a case as verified.

## Safeguards and preservation

The new payload is separate from the previous 251 source-reviewed decisions and
four earlier manual decisions. Those files and the old review results remain
unchanged. Every prior group and relationship is checked against the
[frozen baseline graph](baseline-links.json.gzip).

Every adopted official alias observation requires its own original-row review,
plus an existing preferred spelling. Every compiled alias observation requires
an exact remuneration-and-expense witness unique to one official name at the
same employer and year-label prefix. The prefix locates a comparison; it does not
relabel a compiled edition as an independently established calendar year.

The build rechecks all alias observations, witness rows, source hashes and PDF
pages. The review gate additionally rechecks the crops, contact sheets and
source-row locator files. Added observations or changed originals require a new
review. A regression check preserves an older extraction-split connection when
a new reviewed preferred spelling changes its canonical name.

[preservation-check.json](preservation-check.json) records 483 unchanged input
files, all 1,379,680 published named observations, all 22,403 previous name groups
and all 24,240 previous relationships. The complete dataset remains 1,385,021
salary observations, including 5,341 unnamed observations. This pass does not
change the accepted source definitions, salary amounts or reporting labels.

No requests, forms or messages were sent. The existing four acquisition requests
remain on hold as instructed.

## Reproduction

From the repository root:

```sh
python3 scripts/review_name_connection_continuation.py --write-reviewed --check
npm run build:name-links
python3 scripts/review_name_connection_continuation.py --check
node --test scripts/reviewed-name-connections.test.mjs src/salaries/nameLinks.test.js
python3 -m unittest discover -s scripts -p 'test_name_connection_continuation.py'
```

To reproduce the original pixels, download each unique `sourceUrl` in the review
plan to a cache file named `<sourceId>.pdf`, and verify its `pdfSha256`. The
render manifest specifies physical pages and clipping rectangles in PDF points.
Using PyMuPDF 1.26.6, Pillow and DejaVu Sans:

```sh
python3 scripts/render_name_connection_continuation.py \
  --cache /path/to/exact-hash-pdfs --out /tmp/name-review-reproduction
```

The renderer verifies byte-identical PNG crops and contact sheets. It writes to
a separate folder and cannot overwrite the reviewed evidence. The original
112 row crops are the review evidence; labels above them are annotations.

The ordinary salary CI rebuild and reconciliation also run this review gate.
The generated [summary](summary.json) and full CSV include the resolved cases and
every remaining blocker, without overwriting the previous review snapshot.
