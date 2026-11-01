# PR27 Interior standalone-initial correction

The old Interior parser applied a currency/artifact ignore list to every field. A standalone `A` in a published name was therefore removed even though both PDF readers retained the letter. The repair preserves text tokens and confines explicitly reviewed currency tokens to monetary fields. Currency signs crossing into a text column now fail extraction.

Before any old parser or dataset edit, `pr27-original/` retained the exact original source manifest, reviewed layouts, parser/tests, original verification, every affected normalized/evidence file and the original edge review. `snapshot.json` records SHA256 and byte length for every archived original. These files preserve the PR27 evidence that existed before this amendment; they are not regenerated from repaired inputs.

All **21 cohorts / 299 observations** were audited against both retained positioned-reader word sets. The repair restores **eight published initials in five normalized cohorts**:

| Source | Restored published names |
| --- | --- |
| Sparwood 2025 employees, physical page3 | LEBLANC, A; LUCAS, A; PINCHAK, A; STRASSER, A |
| Sparwood 2025 council, physical page3 | CARDOZO, A |
| Sparwood 2024 employees, physical page3 | STRASSER, A |
| Sparwood 2024 council, physical page3 | CARDOZO, A |
| Princeton 2023 council, physical page9 | WILLIS, TYLER A |

All affected names were checked against rendered originals. The audit also showed that dollar signs sat inside text-column geometry in Rossland 2025 council and the first Sun Peaks 2024 employee row. Their column boundaries were corrected to place the signs in monetary columns. Their normalized rows do not change; provenance/layout evidence changes. In total seven cohort provenance files change.

No row count, amount, expense missingness, physical page, calendar period, control subtotal or original PDF fingerprint changes. No compiled row is deleted. `corrections.json` records every source ID, prior/current data and evidence hashes, exact before/after rows and geometry amendments. `pre-repair-audit.json` records the initial all-cohort review, including the currency signs that the boundary correction resolves.

Validation: nine old Interior regression tests pass, including all restored initials and exclusion of currency from text fields. A fresh second build reproduces all 44 generated files exactly. The root audit ledger must validate the archived PR27 originals plus these explicit amendments; it must not silently reinterpret PR27 as if the repaired names had always been present.
