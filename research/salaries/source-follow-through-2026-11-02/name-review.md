# Individually reviewed source-copy spellings

The new guarded receipts adopt18 source-copy spelling connections:12 Royal Roads and6 CNC. Root inspected every individual source crop. This work preserves every disclosed name, payment, expense, source and period label; it does not establish lifetime identity or authorize replacing compiled observations.

Fifteen connections concern the original3173-pair queue:11 RRU cases and CNC IDs1797,1899,2022,3601. Funk, Scot→Scott, Comelis→Cornelis and Thome→Thorne are three additional leads outside that denominator. CNC IDs1973 and1974 remain held because113,947 remuneration occurs45times in each complete cohort and unknown expenses cannot be equated to0.

The current original-queue overlay is **145 verified,25 likely,3003 unconnected**, starting from the immutable original130/25/3018 review. [held-pair-outcomes.csv](held-pair-outcomes.csv) and [review-results.json](review-results.json) account for all3173 original IDs. [name-review-overlay.json](name-review-overlay.json) pins the original review and actual published link graph, preserves every prior confidence level and lists the three extra leads separately. Uploaded outcome labels supply candidate membership only; they are not adopted as identity evidence.

[name-review-rru.json](name-review-rru.json) pins both complete223-row cohorts, exact compiled/original witness rows, all live alias and current target histories, every associated source definition, the original normalized data, compiled snapshot, individual crop registry and crop/full-page hashes. The original report explicitly covers2021/22 while the related compilation retains2020/21; twelve financial occurrences differ on each side. Each accepted witness is individually unique in both complete cohorts. No blanket cohort equivalence, replacement or redating is inferred.

[name-review-cnc.json](name-review-cnc.json) applies the same guards to the complete312-row2023/24 cohorts. The compiled edition label remains independently unverified even where its characters match the original fiscal label. Five CNC connections use exact remuneration plus numeric expenses. Stuart-Clarke uses113,369 remuneration alone, unique once in each cohort; source expenses remain unknown and the compiled numeric0 remains0. Cornelis and Thorne additionally require the earlier native2020/21 original rows/crops to distinguish compressed r+n glyphs. That requirement derives from the pinned individual registry and cannot be removed by deleting mutable proof fields.

The validator returns existing reviewed-link decision objects for the name builder, while refusing stale observations, new alias/target rows, changed source definitions/currency, ambiguous financial witnesses, altered years/pages/data or changed pixels. Missing expenses never equal zero. `reviewedLiveIndexSha256` records the initial review index as an informational trace; current complete name/cohort/source fingerprints are recomputed independently, so unrelated index metadata does not invalidate unchanged evidence.

Reproduce the receipts or validate every committed output:

```sh
python3 scripts/review_follow_through_names.py --check
node --test scripts/follow-through-name-connections.test.mjs
```

`--check` is fully read-only and compares all seven receipt/snapshot/CSV output bytes, plus all four queue-overlay outputs when present. It works without upload scratchfiles by reading the frozen candidate-membership snapshot. To regenerate the overlay after an approved final name build, use `python3 scripts/review_follow_through_names.py --overlay`. Default regeneration is for an explicitly reviewed receipt update; changed name histories or source evidence require renewed individual review.

The26 focused Node tests exercise all18 real decisions, bilateral uniqueness, full-history staleness, missing versus0, source/page/year/currency/data/pixel changes, required native support, original candidate membership, the full3173 overlay and read-only operation across all11 outputs.
