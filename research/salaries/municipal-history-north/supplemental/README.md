# Small-village employee supplement

Three complete named employee disclosures: Hazelton 2024 (2), Port Clements 2025 (1). Sources, exact periods, original hashes, controls and evidence are in sources.json and reviewed-layouts.json. Reproduce with `python3 scripts/parse_history_north.py --supplemental --fetch`; offline check adds `--check-data`.

Hazelton's original front cover says year ended December 31, 2024. Port Clements' financial statements say year ended December 31, 2025, and its employee schedule belongs to that 2025 SOFI. Entire rendered tables, all numeric component controls, labels and accents were reviewed. Port Clements has no employee position column; position is null. The printed expense-inclusive Total is evidence only, while the footnote explicitly says remuneration includes taxable benefits.

Employee component totals agree exactly. Hazelton's broader accounting reconciliation qualifications are visible in its source warning. Council disclosures are separate in ../council/; no compiled records are removed.
