# Research: how to add to the history

Everything the government atlas knows about the past comes from the files in this folder. The app
never reads them directly: three build scripts compile them into `src/government/historyData.js`,
`eventsData.js` and `atlasData.js`, which are committed. So adding to the history is always the same
three steps: **add sourced records here → rebuild → run the tests.**

What is still missing, and in what order to look for it, is in [`WANTED.md`](WANTED.md).

## The rules every record follows

These come from the atlas research package (`package/MODEL_NOTES.md`) and are checked by
`src/government/atlas.test.js`.

1. **One claim, one source.** Every date, name, parent and holder carries the URL it came from and,
   where you can, a locator (page, paragraph, clause, OIC number). Wikipedia is a lead, never the
   only source.
2. **Keep the precision the source gives.** A year stays `"1957"`, a month `"1957-03"`, a day
   `"1957-03-28"`. Never pad a year to 1 January.
3. **Unknown is not absent.** Leave a value `null` rather than guess, and say why in `note`. An
   undated body is hidden before today unless the viewer asks for undated bodies; it is not shown as
   never having existed.
4. **Say what a date dates.** An Act's Royal Assent, its coming into force, a body's legal
   establishment, its opening to the public and the first time its name appears are different
   events. Record each as its own event; choose one as the start only if a source calls it that.
5. **Stated, not inferred.** Record that a body was part of, or answered to, a ministry only where a
   source says so for that period. Funding, board appointments or a report tabled by a minister are
   other relations (`funded_by`, `appointed_by`, `reports_tabled_by`) and are not drawn as lines.
6. **A period is not an observation.** If a source shows a name or parent on one date only, record
   it with `"coverage": "observation_only"` and `observed_on`; the atlas uses it for that year alone.
7. **An end is exclusive.** `ended` is the day the successor began: the body stood until then, not
   through it.

## What each file holds

| File | Holds | Compiled by |
|---|---|---|
| `history/ministers-<era>.json` | Every cabinet appointment: `{portfolio, holder, from, to, premier, acting, party, source}` | `build:government-history` |
| `history/bodies.json` | Crown corporations and agencies since 1871: `{id, name, kind, established, ended, becameId, predecessorIds, responsible: [{ministry, from, to}], description, source}` | `build:government-history` |
| `history/responsible-*.json` | Which ministry answered for a body, by period: `{records: [{<body id>: [{ministry, from, to, source, note}]}], gaps}` | `build:government-history` |
| `history/holders.json` | Speakers, officers of the Legislature, chief justices: `{offices: [{id, title, holders: [{name, from, to, acting, source}]}]}` | `build:government-history` |
| `history/sub-divisions.json`, `sub-tribunals.json`, `sub-subsidiaries.json` | Today's sub-agencies as collected: `{id, name, shortName, parent, kind, established, description, url, source}` | `build:government-history` |
| `history/sub-agencies-researched.json` | Reviewed sub-agency history (schema `sub-agencies-research/1`): dated claims, names and parents over time, succession, and bodies that are gone | `build:government-history`, `build:government-events` |
| `history/sub-agencies-sources.json` | The catalogue of sources the review cites, by `source_id` | `build:government-events` |
| `atlas/events-*.json` | Typed, dated events: `{id, subject_id, event_type, title, date: {start, end, precision}, temporal_status, evidence: {source_url, locator}}` | `build:government-events` |
| `atlas/responsibility-rail-wcb.json` | Typed relations for BC Rail and the WCB: `{subject_id, relation, office, holder, from, to, source_url, locator}` | `build:government-history` |
| `atlas/lieutenant-governors.json` | The Legislative Library's list: commission, effective date and swearing-in kept apart | `build:government-atlas` |
| `atlas/staffing.json` | FTEs by ministry and fiscal year from the Public Accounts | `build:government-atlas` |
| `atlas/parliament-43.json` | The 43rd Parliament's 93 seats and every dated caucus change | `build:government-atlas` |
| `package/` | The atlas research package of 2026-09-25: model notes, QA cases, event seeds, logo routes | `build:government-events` |
| `decisions.json` | Editorial choices between competing claims (below) | both history and events builds |
| `sub-agencies/BRIEF.md`, `TEMPLATE.json` | What is known and missing for each sub-agency, generated | `build:research-brief` |

Ids are the atlas's own: a ministry episode is `ministry-of-forests-2022` (name and first year, from
`src/government/episodes.js`); a body is its slug (`bc-hydro`); a sub-agency is its slug without the
`sub-` prefix the build adds. Ministries may also be named as a source printed them
(`"ministry_as_printed": "Ministry of Forests"`); the build matches names to the ministry of that year.

## Adding something

**A sub-agency's history.** Add or complete its record in `history/sub-agencies-researched.json`
(the shape is the one `sub-agencies/TEMPLATE.json` gives every body, with `established`, `ended`,
`names`, `parents`, `relations`, `research_events`, `date_claims`, `legal_basis`, `evidence_status`
and `note`). A body that no longer exists goes in `gone`. Put each new source in
`history/sub-agencies-sources.json`.

**Which ministry answered for a body.** Add a period to one of the `history/responsible-*.json`
files, or start `responsible-4.json` — every `responsible-*.json` file is read.

**Events.** Add a file `atlas/events-<topic>.json` with an `events` array; every `events-*.json` file
is read. Use the event types in `src/government/events.js` where one fits, or a descriptive
snake_case type (`legislation_assented`, `operational_start`); unfamiliar types are sorted by their
words.

**A minister, a Speaker, an officer.** Add the appointment to the era's `ministers-*.json` or to
`holders.json`. A portfolio that does not match a ministry is listed in the build's output.

**A new kind of data** (MLAs, deputy ministers, committees). Add a folder or file here with its own
schema and a short note at the top of the file, and a build step to compile it — the existing
scripts in `scripts/build-government-*.mjs` show the pattern.

## Recording a decision

When sources disagree — BC Timber Sales has three candidate start dates — the research records all
of them and marks the record `requires_reconciliation`. Choosing one is an editorial decision, and
goes in `decisions.json`, never into the research file:

```json
{
  "id": "bcts-established-2003-06-20",
  "subject": "sub-agencies/bc-timber-sales",
  "field": "established",
  "value": { "date": "2003-06-20", "precision": "day", "source": "https://…", "locator": "…", "meaning": "…" },
  "status": "documented_partial",
  "reason": "Why this reading, and why not the others.",
  "set_aside": [{ "date": "2003-04-01", "why": "…" }],
  "decided": "2026-09-26"
}
```

The builds apply it after reading the research, the competing claims stay as events, and the panel
shows the reason beside the date. Decisions can currently set a sub-agency's `established` or
`ended`.

## Rebuilding and checking

```sh
npm run build:government-history   # ministers, bodies, office holders, sub-agencies
npm run build:government-events    # dated events
npm run build:government-atlas     # Lieutenant Governors, staffing, the 43rd Parliament
npm run build:research-brief       # regenerate sub-agencies/BRIEF.md and TEMPLATE.json
npm test
```

Each build prints what it could not match (a portfolio with no ministry, a staffing row with no
ministry, a duplicate whose dates disagree) — read that output. Then open the Government view at a
year the change affects, select the body, and check its **Evidence** card: every claim should show
its source.

Raw captures (PDFs, saved pages, OCR text) are not committed; keep them in `tmp/research/raw/`, and
cite the public URL in the record.

## Handing research back

If you research outside the repo (another tool, a spreadsheet), return JSON in the shapes above —
for sub-agencies, fill `sub-agencies/TEMPLATE.json` — with a note of what you checked and what you
could not resolve. The sub-agency review of 2026-09-26 is a good model: it kept every claim with its
locator, said what each date meant, and listed its limits rather than smoothing them over.
