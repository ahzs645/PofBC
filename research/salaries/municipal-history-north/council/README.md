# Historical municipal council disclosures

225 actual council payment observations across 30 separately identified calendar-year tables, from Williams Lake, Northern Rockies Regional Municipality, Dawson Creek, Chetwynd, Hazelton and Port Clements. Sources are the council sections of originals used in the parent employee collection; this manifest has independent row/evidence hashes and controls.

These are elected municipal councillors/mayors, separate from employees. Threshold is null; completeness is `completeCouncilSchedule:true`, without claiming employee coverage. The complete published council table is retained, including partial-year payments after elections. Exact roles are printed roles, never inferred from names or other years. Expense-inclusive Totals remain evidence only.

Williams Lake 2012–2014 does not have a separate full-name column. The complete Position label, including a surname where printed, is retained as position, and name stays null. No identity is inferred from another report. Other source names/initials and Hazelton accents remain as printed. No compiled council records are deleted or relabelled.

Public warnings state exact unresolved component differences; values are not adjusted and no rounding explanation is assumed. See the parent README for residuals and the manifest for source-specific controls.

Reproduce originals with `python3 scripts/parse_history_north.py --council --fetch`; offline check is `python3 scripts/parse_history_north.py --council --check-data`. The shared regression suite includes council scope, missing names and small expense residuals.

A targeted WL2015 embedded-OCR correction changes `BonneII, I.` to the rendered `Bonnell, I.` with an exact pinned before/after cell, without global letter substitution. The unusual printed WL2011 `Natlie Lynn Montoya` spelling is retained. Both 300 dpi review crops are stored in the pass visual-corrections directory.
