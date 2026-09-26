# Proposed data model and temporal rules

These are design recommendations for integration, not a description of the current implementation.

## Separate objects

| Object | Purpose | Important fields |
|---|---|---|
| Organization | Stable legal or administrative subject | id; type; jurisdiction; existence claims |
| Organization episode | A meaningful bounded organizational state | organization_id; label; temporal extent; source claims |
| Name use | Legal, operating, historical or display name | organization_id; name_type; literal_name; dates |
| Office/role | A post, independently of whoever holds it | id; title; hosted_by; authority |
| Role holding | One person holding one role | person_id; role_id; capacity; start/end; evidence |
| Function | Responsibility that can move without a whole organization | id; description; period assignments |
| Relationship | Typed, dated connection | source_entity; target_entity; type; bounds; claims |
| Event | Change or milestone | event_type; participants; effective/announced dates; source |
| Measure | A dated fiscal or staffing observation | value; unit; period; budget/actual; reporting scope |
| Identity asset | A mark or generated variant | organization; variant; provenance; dates; rights; fidelity |
| Evidence/claim | Why a field or edge is shown | source_id; locator; assertion; uncertainty; review status |
| Parliament/session | Legislative time context | ids; dates; dissolution; session records |
| District version | One boundary/name version | persistent district lineage; geometry version; valid dates |
| Electoral candidacy/result | A person contesting/obtaining a seat | election_id; district_version; party_at_election; votes; status |
| Caucus membership | Later affiliation over time | person_id; caucus_id; temporal extent; source |

## Relationship vocabulary

`administrative_part_of`, `minister_responsible_for`, `report_tabled_by`, `owned_by`, `funded_by`, `regulated_by`, `appoints_to`, `partner_of`, `succeeded_by`, `merged_into`, `split_into`, `renamed_as`, `functions_transferred_to`.

The direction and endpoint types must be documented. For example, `minister_responsible_for` should originate at a ministerial office, not become an all-purpose ownership arrow. A minister may hold multiple portfolios; a person may serve multiple roles concurrently. Do not require exactly one parent for every entity. Do not infer responsibility from a budget heading or topical similarity alone.

## Time

Use separate real-world validity and research-observation dates. A web page observed in 2026 saying who holds a role does not prove that person held it in 2025.

Preserve date precision: `day`, `month`, `year`, `day_range`, `month_range`, `year_range`, or `unknown`. Keep exact effective dates where known; retain intervals or estimates otherwise. Year-only dates should not be stored as exact January 1 dates.

For exact organization/role intervals, a half-open convention [start, end) simplifies simultaneous changes. Convert from an original source’s inclusive wording only with an explicit rule and preserved original value. For the event seeds, multi-day event ranges instead explicitly mark `range_end_inclusive: true`. Do not mix these conventions silently.

A record can be `known_active`, `known_inactive`, `observed_active`, or `unknown_for_date`. An open end from a 2024 source is not proof of active status in 2026. An organization without a founding date can be shown at dates with direct attestations and shown as uncertain outside them; do not invent a continuous history to make a slider look complete.

Different event dates can coexist: announced, legislated, assented, effective, operational, sworn-in, first observed, last observed, retired. A logo observed on a report proves use for that application, not universal adoption or exclusive use.

## Evidence

Each claim should have a source reference, exact locator, publication/revision date where available, observation date, source wording or brief permissible excerpt, normalized interpretation and reviewer status. Keep conflicting claims instead of overwriting the earlier one invisibly.

Use categorical states rather than unsupported numeric probabilities: `documented`, `bounded`, `estimated`, `conflicting`, `unknown`. Source type and date precision are separate dimensions. An official page may be retrospective, outdated or imprecise.

Do not store a source-file checksum unless the bytes were actually obtained. The checksums in this package apply only to the generated package files.

## Identity assets

Recommended independent classifications:

- Provenance: `original_supplied`, `extracted_from_official_vector`, `archival_raster`, `reconstructed`, `synthetic_name_variant`.
- Format: SVG, PDF-vector, PNG, etc.; test actual contents rather than the extension alone.
- Fidelity: source compared, partially compared, font substitution, no comparison.
- Historical applicability: documented adoption; first observation; last observation; estimated era; unknown.
- Rights: exact source terms; permission request; permitted use and attribution; unresolved.

A reconstruction can have accurate dates but imperfect lettering. An original vector can have uncertain dates. A high-fidelity image can still require permission. A modern mark generated with a historical name is not an authentic historical mark.

## Measures and coverage

Keep fiscal periods distinct from calendar dates. Preserve headcount versus FTE versus funded positions, permanent versus seasonal staff, budget versus actual, gross versus net, nominal currency and consolidated scope. A reorganization can break comparability even when a table row keeps the same name.

Coverage metrics require explicit denominators. Count organizations separately from episodes and people separately from terms. Prefer duration-weighted coverage where precise intervals exist; label sampled-year metrics honestly. Unknown ministers, unknown parents and unknown identity dates are separate measures. Approximate subcategory counts may overlap, so total unique IDs rather than adding them blindly.

## Example API/view projection

A view request could specify `date`, `scope`, `relationship_types`, `include_uncertain`, `identity_mode` and `source_cutoff`. A shareable route should encode these values with the selected entity. The output should include both records and coverage/missingness, not silently remove uncertainty.

A modern table fallback and historical identity view should use the same canonical records. Do not let visual presets change the historical facts.
