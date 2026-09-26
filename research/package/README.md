# British Columbia government atlas — research companion

Research snapshot: **2026-09-25**. Independent research material; not an official government publication.

This package contains **37 source entries, 26 starter events, 5 priority logo-acquisition records and 17 research/QA tasks**. Source statuses distinguish pages actually reviewed from catalogue links, application shells and a fetch-limited PDF.

## Open first

Open `index.html` in a browser for a searchable, offline research navigator. It contains the data inside the HTML; no server, sign-in, external JavaScript or font download is required. Source links open the original websites and require internet access.

`RESEARCH_GUIDE.md` explains the findings and priorities. `MODEL_NOTES.md` describes the proposed temporal model. `QA_CASES.md` contains acceptance tests for a future implementation, **not claims that the existing interface passed those tests**.

## Machine-readable records

- `sources.json`: official sources, retrieval status, useful fields, source locators and cautions.
- `event_seeds.json`: typed events with day/year/month precision, scheduled versus historical status, evidence and interpretation notes.
- `logo_acquisition.json`: verified routes and unresolved artwork/rights steps for ICBC, BCLC, BC Ferries, BC Transit and WorkSafeBC.
- `research_backlog.json`: prioritized research tasks and completion criteria.
- `event_seed.schema.json`: JSON Schema for the event file. `validate.py` checks its structure, IDs, date precision and source links with Python’s standard library; it also uses jsonschema when installed.
- `validation_report.json`: actual results of checking this package. `manifest.json`: checksums of the files in this package.

## Integration boundary

**This is not a replacement dataset or a ready-to-apply patch.** No local repository was modified. The `seed:` event IDs and subject keys need matching to your own organization/person/event identifiers. Your latest inventory was treated as the project baseline. The older reviewed atlas was consulted only for interface context; its older counts were not substituted for your latest numbers.

No complete historical parent-ministry intervals for BC Rail (1972–2003) or WCB (1917–1974) were established. No comprehensive deputy-minister list was found. No corporate vector masters were downloaded or compared, and no font files are distributed. Attempts to inspect original website asset bytes in the runtime failed because external DNS/network access was unavailable; official media routes were instead reviewed through the web tool.

Historical source statements are evidence, not permission to backfill every unknown year. A contemporary origin claim may describe a lineage rather than a modern name. A year-only date remains a year; it is not silently converted to January 1.

Future election milestones are recorded as scheduled/planned, with no invented results and no automatic monitoring job. Recheck the official election page before use.

## Checks performed on this package

The event file passed JSON Schema and internal ID/source/date checks. The generated HTML was rendered in Chromium at desktop and 390-pixel mobile widths; search, source dialogs, collection navigation and the planned-election filter passed smoke tests. The browser test used in-memory HTML because this environment blocks file-URL navigation. It did not test remote source availability or the user’s application. See `validation_report.json` and `browser_validation.json`.
