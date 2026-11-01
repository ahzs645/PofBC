# Independent review of the PR27 text repairs

The root reviewer inspected rendered original Sparwood 2024 and 2025 physical page 3 and Princeton 2023 physical page 9. All eight restored initials are visibly printed in the originals: LEBLANC, A; LUCAS, A; PINCHAK, A; STRASSER, A in 2025; CARDOZO, A in both Sparwood years; STRASSER, A in 2024; and WILLIS, TYLER A in Princeton. No initial was expanded into an inferred given name.

The archived normalized inputs are checked against the exact data hashes recorded by PR27 and their original Git blobs at `67d5cff`. Current and archived rows retain the same order, employer, monetary cells, missing-expense values and physical pages. The only eight normalized differences restore printed name text. Counts, periods and original PDF fingerprints are unchanged.

The repair also confines artifact filtering to monetary fields. Two supporting layout corrections move currency signs out of text-column geometry without changing normalized observations. The complete prior source manifest, parser/configuration and affected data/evidence bytes remain archived; the historical release is not rewritten to claim that the corrected names were always present.

The central release-amendment ledger pins each old/new normalized hash and exact before/after row. The frozen PR27 validator accepts these reviewed text-only amendments by validating the archived original bytes and enforcing unchanged monetary cells, row multiplicity and pages. Other input changes continue to fail validation.
