# Package validation

**22 November 2026**

## Completed checks

- All 18 original baseline files are byte-for-byte unchanged under `prior_research/`.
- Every JSON file parses successfully.
- All 33 integration actions refer to registered source IDs and, where applicable, registered claim IDs. All nine requested review questions are covered.
- The consolidated register has 59 evidence assertions/ownership observations and 31 source records. IDs are unique within each register. These counts do not represent unique companies, events or publications.
- Every claim source reference resolves to a source record.
- The Panco gross/net/gain arithmetic reconciles; the Plateau direct and indirect public holdings total 100%.
- Independent source review checked the consolidated report and the ownership recommendations. The review distinguishes source dates, name-effective dates, ownership snapshots, operations, winding up and legal dissolution.
- New package files contain no links to transient local retrieval paths. Original publications are cited by public URLs and printed/PDF page locators.
- No raw source PDFs, OCR dumps or research screenshots are included.
- The ZIP archive passes its CRC integrity test, its member set matches the staged package, and its file contents match the SHA-256 manifest.

## Scope of these checks

These are checks of the research deliverable. The user's local uncommitted repository and integration file were unavailable. The reported 1,148 passing repository tests and reproducible government build were not independently rerun. No repository edit, commit or push was performed.

Remaining evidence gaps are stated in the consolidated report and integration actions. The checks do not certify all 111 companies in the reported historical roster or all claims retained in the superseded baseline.
