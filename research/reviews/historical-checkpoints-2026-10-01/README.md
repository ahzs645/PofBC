# PofBC historical research — finalized release 1.0

**1 October 2026.** Six specified budget checkpoints, with targeted lifecycle follow-up and earlier research retained.

Open **index.html** for the self-contained searchable review. **PofBC_Historical_Research.xlsx** provides filterable research tables. **REPORT.md** explains findings, scope and source coverage. The `data` directory has canonical JSON and matching UTF-8 CSV exports.

## What is delivered

120 ministry checkpoint scopes; 590 observation rows; 26 typed event records; 61 source entries for this pass; a candidate crosswalk to the inherited 238-record baseline; a 1,428-cell body/year evidence lookup; and 19 specific open research issues.

These are observations, not 590 different agencies. All ministry rosters were covered and selected supporting passages were reviewed, but this is not an exhaustive census of every internal unit, every Crown subsidiary or every health-authority program.

## Use and validate

```sh
python tools/validate.py
# Optional download to a separate source archive from a network-enabled machine:
python tools/fetch_sources.py --out downloaded_sources
```

No repository files were changed, no production build was run, and no site was deployed. Do not overwrite the production history dataset with these separate research tables. Follow **docs/INTEGRATION.md** first.

The previous 39-claim first batch is retained unchanged in `prior/first-batch`. The Finance 72-check table is in `data`; the CAWS census, reconciliation and prior report/patch are in `prior/finance-and-caws`. The inherited patch is provenance only; do not apply it automatically to a current branch.

## Reading rules

Unknown is not absent. A first observation is not a founding date. Budget support is not structural parentage. Planned changes are not completed events. A rename is not necessarily a new institution. An exact-name match is still an identity candidate. Different labels may refer to institutions, programs, accounts or functions.

Complete remote source documents are not archived in this release; sources retain official URLs and exact passage locators. The interrupted working directory was reconstructed from the retained source-reviewed extraction notes; all six per-year row totals were recovered and release validation was rerun. See `data/recovery_log.json`.

## Release checks

70 internal data/package checks passed; 12 HTML browser smoke checks passed; the seven-sheet workbook passed archive and cell-error checks and its overview was visually inspected. The original first-batch files were verified byte-for-byte against the supplied ZIP. These are package checks, not independent historical verification or production application tests.
