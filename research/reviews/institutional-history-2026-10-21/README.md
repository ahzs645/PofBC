# PofBC institutional-history research package

Prepared 20–21 October 2026. Repository reviewed read-only at commit
`112b352ebbd032c28e35b12036d5199ec97584e2`.

Start with **REPORT.md**. The three domain appendices retain more detailed findings,
source qualifications and earlier names than the executive report.

## Contents

- `REPORT.md`: integrated findings and recommended expansion.
- `health_lineage.md`: all five regional authorities, Northern deep history, societies and territorial changes.
- `phsa_ministry.md`: PHSA constituent institutions, ministry functions and direct programs.
- `crowns_branches.md`: corporate structure,20-entry exempt-body queue and other branch histories.
- `SOURCE-CATALOGUE.md`: readable source index.
- `source-register.json`: 161 distinct URLs from 170 records, retaining every citation alias and review note.
- `health_lineage_map.json`: 44 statutory constituents, 7 societies, 43 earlier council-to-board links and other events.
- `proposed-relationship-examples.json`: 24 additional sourced event/relationship examples, including full regulator merger lists.
- `repository_audit.json`: commit, current-data reference date, counts and connectivity snapshots.
- `research_backlog.md`: precise remaining questions and the evidence needed to resolve them.

## How to use the evidence

Source IDs resolve through the `aliases` list in the combined register. Identical URLs
are deduplicated; original research records remain under `review_records`.
The status counts are `{"read": 121, "official-index-only": 33, "local-code-read": 4, "lead": 3}`.
An indexed lead is not equivalent to a fully reviewed document. Even a reviewed source
can leave a specific date, legal identity or transaction unresolved.

These JSON files are research interchange data, not migration scripts. Match names to
existing repository IDs, preserve event type/date precision, and use the canonical
research files and normal build checks during implementation. Unknown start dates
must not become 1 January. A ministerial responsibility, funding or service relationship
must not be silently converted into ownership.

No application source files were changed, no PR was created, and no site was deployed.
The audit imports committed data and examines graph snapshots; it is not a rendered
browser usability test. External source documents are linked, not redistributed here.
