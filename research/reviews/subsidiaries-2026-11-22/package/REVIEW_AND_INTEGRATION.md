# Integration brief for PofBC

## Recommended data model

Represent `legal_entity` independently of each public-facing label, and preserve:

- `jurisdiction`, `registry_number`, `incorporation_date`, `continuance_date`, `dissolution_or_amalgamation_event`;
- `legal_names[]` with effective dates and primary registry evidence;
- `relationships[]` with directed, typed ownership/control/funding edges; `percentage`, `share_class`, `source_id`, `period` or **observation_as_of**;
- `events[]` with `event_type` distinct from source's **date_kind** (`incorporated`, `acquired`, `sold_assets`, `sold_shares`, `renamed`, `amalgamated`, `wound_up_observed`, `dissolved`, `loan`, `financial_provision`);
- `confidence` and `verification_state` distinct from a date's precision.

## Guardrails and suggested treatment

- Province→company equity holding for **Swan Valley Foods**; ownership is percentage/dated, then a December 1, 1977 disposal. Do NOT classify Creston Valley as a Swan Valley renamed legal entity.
- **Dunhill** must be mapped by registered company number; no string-based merge on the recurring Dunhill name. Keep 1974 ownership as a **point-in-time** statement rather than 1974–1990 interval.
- **T.S. Holdings** directly provincially owned; its exact fleet subsidiaries require 1977 audits before linking.
- **Vancouver Island Transit** explicitly described as a consolidated subsidiary, but parent unresolved; `owns` edge should remain null.
- **Thompson-Okanagan Transit** funded, not proven owned.
- **Chef Ready**, **Kootenay Dehydrators**, **South Peace Dehy** are other equity investments. Their share-class and accounting issues need separate tracking.
- For **I.O.K. Poultry**, display historical dissolution as occurring **on or before 1980-03-31**, not exactly 1980-03-31.
- For **Venture Realty**, preserve spelling conflict with the existing `Ventures Realty Ltd.` until registry documentation.

## Steps to integrate (not performed)

1. Match each new company against **company numbers** in `research/history/` and `src/government/` rather than only labels. Keep unresolved cases in a `held` queue.
2. Implement typed ownership/financial relationship graph for user-selected historical years. Financial observations require as-of-date semantics; they should not be extended indefinitely.
3. Link immutable evidence citations to each event and relationship; display source-page and confidence.
4. Add focused regression tests: same-name different entity; different-name same entity; sale of shares vs assets; equity provision vs disposal; missing parent relationship.
5. Start with legal name events for Dunhill, exact ownership exit for Swan Valley, and I.O.K. dissolution-bound event; hold minority holdings until the equity overlay can distinguish them from Crown corporations.
6. Review chronology/graphic output, then prepare an ordinary PR. Do not deploy or merge without review.

## Evidence-quality notes

The source register distinguishes contemporary financial statements, court judgments, statutory instruments, company registries and the internal research. The source PDFs are not embedded. Several are old scanned documents and some large PDF screenshot fetches fail; the package records the page as published and does not claim to have reconstructed missing registry file numbers. All 53 inventory records are research observations/candidates, NOT a deduplicated count of provincial Crown subsidiaries.
