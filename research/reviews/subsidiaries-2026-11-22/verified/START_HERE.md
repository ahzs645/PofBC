# PofBC subsidiary research: verified continuation

**Review date: 22 November 2026**

Read `VERIFICATION_AND_CORRECTIONS.md` first. It answers the nine questions raised after the earlier package was integrated and identifies changes to make before committing that integration.

## Package contents

- `VERIFICATION_AND_CORRECTIONS.md`: the consolidated review and graph decisions.
- `data/review_actions.json`: concrete integration actions, date meanings and evidence references; `data/claim_register.json` consolidates the supporting assertions.
- `data/source_register.json` and `SOURCE_INDEX.md`: primary-source URLs, locators, verification methods, and available download hashes. Statistics Canada records include working Library and Archives Canada mirrors.
- `review_workstreams/`: detailed authored findings from the Statistics Canada, transit ownership, legal identity, public ownership and Pacific Coach checks.
- `prior_research/`: the earlier 18-file package, preserved unchanged as the research baseline. Its claims are superseded wherever the new review supplies a correction.
- `PROVENANCE.json`: baseline archive hash and review scope.
- `PACKAGE_VALIDATION.md`: checks performed on this deliverable.
- `SHA256SUMS.txt`: checksums of the packaged files.

## Scope and integration status

This is a source review and correction package. The user's uncommitted local integration was not accessible in this workspace. The report of 1,148 passing tests and a reproducible government build is the user's verification; those checks were not independently rerun here. No repository files were changed, committed or pushed in this review.

The earlier 53-item inventory and the reported 111-company roster are not deduplicated counts of legal subsidiaries. In particular, HCBC Construction is the renamed Fisher Developments, and the later Dunhill is the renamed W.K.P. Construction. Preserve legal identities when applying names and dated observations.

Full source PDFs and raw OCR are retrieval intermediates rather than package members. The source register provides primary links, archived mirrors where useful, and exact printed/PDF page locators. All PDF page locators in this package are one-based unless expressly stated otherwise.

## Evidence conventions

An incorporation date, public acquisition, operational start, legal rename, share sale, asset sale, winding-up observation and legal dissolution are separate events. A roster date describes what the source reported as of that date; it does not establish incorporation or continuous ownership. Unknown endpoints remain unknown. The review preserves a real March/April 1986 day-boundary disagreement for BC Cellulose and unresolved legal rename dates for Panco's later names.
