# Island and coast historical search inventory

The accepted handoff is **934 observations, 74 employee/council cohorts, 37 reports, nine municipalities**. It adds 714 employee and 220 council observations and preserves every existing compiled record. The [collection guide](../../municipal-history-island/README.md) explains definitions, source residuals, the 16-row Lantzville OCR acceptance and reproduction.

This inventory covers **22 municipalities plus the distinct shíshálh Nation Government District governance case**, outside the Capital and Cowichan assignments. The audit date is October 31, 2026, America/Vancouver. It retains **131 located direct SOFI links**, **87 retrieved or reused original reports**, and **146 remaining tasks**. All 23 current official indexes were checked; Qualicum Beach and Port Alberni index retrievals failed in this environment, and their retained official leads remain useful.

* [Inventory](inventory.json): baseline accepted employee/council years; every retained and freshly located direct SOFI link; original/index URLs and hashes; label-year hints separated from accepted periods; actual salary-page text/image classification where inspected; current accepted additions and remaining coverage.
* [Remaining work queue](work-queue.json): normalized tasks with exact source/index links, explicit verified periods or `unknown`, status, route, next action and reason. A current index is not assumed exhaustive, and unverified upload/label years do not become accepted salary periods.
* [Original retrieval receipts](retrieval-receipts.json): original byte counts, SHA-256 hashes, physical page counts, retrieval/cache status and local cache paths. Reused originals retain their earlier receipt link.
* [Current index receipts](index-receipts.json): successful HTML fingerprints, extracted SOFI links and failed retrieval details. Whole-page native text is not used to certify salary tables.
* [Additional rendered source assessments](source-assessments.json): precise unaccepted page-localization findings, currently Sayward 2025.
* [Lantzville 2025 author transcription](lantzville-2025-manual-transcription.json), [fresh OCR text](lantzville-2025-fresh-ocr.txt), and [independent second full-image review](../reviews/lantzville-2025-ocr.md).
* [Qualified Tahsis 2019 council evidence](tahsis-2019-council-review-evidence.json.gzip): the original five rows, both readers and exact +$999 control conflict. The cohort is accepted with an unchanged-cell warning after independent image review; it is not held or omitted.

## Next processing work

The located older archives remain more useful than immediate FOI filings. Cumberland's 2011–2013 links, Lantzville's older and 2021–2024 reports, Tahsis 2017–2018/2024, Tofino's other indexed years, Gold River's earlier reports, and Ucluelet 2018–2022 require scan/OCR work or source-specific review. These ranges describe **archive labels** unless the inventory separately establishes the actual salary-schedule period. Earlier unindexed archives remain open research tasks for every municipality.

Campbell River 2024 is a retrieved 17-page original with no native text, SHA-256 `00952ec1a32c8e5d7ff09d2fa7492a35677e121af0519f4dd45f814b2e89a66c`; it is a processing lead, not an acquisition failure. Lantzville 2024 is likewise retrieved and scanned. Neither is silently treated as unavailable.

Sayward 2025 illustrates why classification must use the salary page: its 31-page PDF contains substantial native financial-statement text, but the named schedule is a clear scan on **physical page 4**. Rendered inspection locates one employee and five council rows and an explicit December 31, 2025 period; acceptance still requires fresh OCR, two complete human transcriptions and controls. It remains in the queue, with no six-row import implied by this inventory.

The queue also retains unresolved qualifications in accepted sources. Ucluelet 2023's malformed expense needs an existing corrected schedule or issuer explanation; the known pay is already useful. Tofino 2021 needs an approved/signed version if available and explanation of its council expense control; separately reported Benefits are explicitly excluded from the accepted council measure. Its employee and Tofino2012 below-threshold expense aggregates are n/a: named expense comparators remain unavailable, and comparisons with broader all-employee figures are explicitly labelled as different scopes. Tahsis 2019 and Port McNeill 2021 have exact named-versus-summary conflicts; the published fields remain unchanged.

Two **ordinary records acquisition options**, for unlocated Port McNeill 2022–2025 standalone schedules and Alert Bay's available-year inventory/electronic originals, follow targeted public archive research. Their absence from the checked index does not prove records do not exist. A formal FOI route is a fallback if ordinary access cannot obtain existing records; no specific report here has been labelled FOI-required without evidence. No requests or messages have been sent.

The shíshálh Nation Government District remains a separate governance/public-disclosure research task. Ordinary municipal SOFI or municipal FOI obligations are not assumed. Okanagan Falls is outside this scope and no earlier missing-year claim is made for it.

## Reproduction

```sh
python3 scripts/import_history_island.py --verify --cache /tmp/pofbc-history-island
python3 scripts/import_history_island.py --offline-verify
python3 scripts/audit_history_island.py
python3 -m unittest scripts/test_history_island.py
```

The inventory generator uses the pinned baseline, retained original/index receipts, located official leads and accepted manifests. It writes only this audit directory. Re-fetching current websites may change the discovery snapshot; source acceptance still requires the original pinned hashes and complete source-specific verification.
