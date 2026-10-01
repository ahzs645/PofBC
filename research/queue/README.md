# Researching B.C.'s sub-agencies: a guide for researchers and AI assistants

This folder is the work list for the history of the Government of British Columbia below the
ministry level, and the instructions for doing that work. It is written so that a person or an AI
assistant with no other context can pick up one batch, research it, and hand back results that merge
cleanly.

**If you are handing work to an AI:** give it this file and one file from [`batches/`](batches/).
The prompt at the end of this file (§9) works as-is.

**If you are an AI given a batch:** read §1–§6, then work through the batch. Return JSON in the
shape of §6. Section 7 is the checklist to run before you answer.

The list of batches and what is left is [INDEX.md](INDEX.md). Every body's questions, in
machine-readable form, are in [sub-agencies.json](sub-agencies.json). Both are regenerated from the
data, so they are always current; this README is written by hand.

---

## 1. The project

**PofBC** is a website about the visual identity of the Province of British Columbia. One of its
views, **Government**, draws the whole provincial government as a diagram for any year from 1871 to
today: the Legislature, the courts, the Premier and cabinet, every ministry, and the Crown
corporations and agencies. Move the timeline and the diagram shows the government of that year.

Around each ministry and Crown corporation the diagram draws its **sub-agencies**: divisions,
offices, programs, boards, tribunals and Crown subsidiaries. Examples are the Residential Tenancy
Branch, the Civil Resolution Tribunal, BC Cancer and the Gender Equity Office.

Everything the diagram knows comes from sourced research files in `research/`. Build scripts
compile them into the data the site reads. Every date, name and parent on screen links to the source
that states it. That is the point of the project: nothing is drawn that a source does not support.

## 2. The problem you are solving

The sub-agencies were collected from **2026** sources: the 2026/27 Estimates, service plans, and
ministry and Crown websites. Those sources say what exists now. Most of them do not say when a body
began.

The site draws a body in a past year only if a source shows it existed by then. So a body with no
start date is drawn in 2026 and **disappears the moment the timeline moves back even one year**. On
30 September 2026, 238 sub-agencies were drawn in 2026 and only 38 in 2025.

Two examples:

- **Child Care Resource and Referral Centres** has no start date on file. It is drawn in 2026 and
  gone in 2025, although it certainly existed then.
- **Energy Resource Appeal Tribunal** is dated: its Act came into force on 4 October 2010. It is drawn
  back to 2010, as it should be.

The site does not guess, because a guess would be wrong in both directions. The Liquor and Cannabis
Regulation Branch did not exist in 1990 under that name. Many branches were created, renamed, split
or moved between ministries at cabinet shuffles. The fix is evidence.

## 3. What we are looking for

There are three tracks for each body, in priority order, then two broader ones.

### A. First sighting: "known to exist by"

**The most valuable work per hour.** A body does not need a founding date to be drawn in the past.
If the 2010 Estimates list it, it existed in 2010. For each body, check the budget documents at each
**checkpoint year**: 2025, 2020, 2015, 2010, 2005 and 2002. For each check, record:

- whether the body is **listed** (`true` or `false`);
- the **name as printed**, which may be an earlier name;
- the **ministry it is printed under**, as printed;
- the URL and the **page** (PDF page and printed page if they differ).

**A "not found" result is a finding about the search, not about the body.** Record it, with the
pages or sections you read and the names you searched for. Budget books omit small units, fold them
into a larger line, print them under another ministry or use an older name, so a non-match never
dates a start or an end. It tells the next researcher what has already been read.

What counts as listed:

- A **sub-vote, program or line** in the Estimates that names the body.
- A branch, division or office named in a service plan's **organization chart, core business areas
  or program list**.
- The body named on an **archived gov.bc.ca page** (Wayback Machine). The capture date is the
  observation date.
- The body named in a **news release** as existing on that date.

What does not count as listed:

- A description of the body's **function** without its name ("tenancy disputes are resolved…").
- A **retrospective statement** such as "since 2010, the office has…", written later. It is not a
  sighting in 2010. Record it as a `research_event` (type `retrospective_claim`) with the date it
  speaks of and the date of the document that says it. It is a start for track B only if it says the
  body was *created* then.
- A **similar but different name**. Record it as a possible earlier name and say why you think it is
  the same body. Do not treat it as proof.

If a body is found at a checkpoint, check the checkpoints before it too, and do not stop at the
first non-match: look under the predecessor names, under other ministries of the time, and in the
year's annual reports. 2002 is where the online budget documents begin, not where history begins;
follow earlier evidence wherever it leads.

Give every check an **outcome**:

| `outcome` | `listed` | Meaning |
|---|---|---|
| `found_name` | `true` | The body is named, as itself. |
| `found_contextual_name` | `true` | Named in passing, inside another unit's description. |
| `related_label_identity_unresolved` | `null` | A similar or predecessor-looking name; whether it is the same body is open. |
| `function_only` | `null` | Its work is described, but not the body by name. |
| `not_found_in_scope` | `false` | Not in the pages or sections read. Says nothing about the rest of government. |

### B. Start: when this body began

The date the body began **as this body**: under this name or an earlier one. It is recorded with the
precision the source gives. Good evidence, strongest first:

1. The **Act** or regulation that created it, and its coming into force (BC Laws; point-in-time
   versions show when a section took effect).
2. The **order in council** that established, named or transferred it.
3. A government **news release** announcing its creation or launch.
4. The body's own **annual report** or the ministry's annual service plan report.
5. The body's own **official "about" or history page**.
6. A secondary source (a book, a society's history). Record it only as a lead, marked `secondary`.

**Say what the date dates.** Royal Assent, coming into force, legal establishment, first members
appointed, opening to the public and first use of the name are different events. Record each one you
find as a `research_event` with its own type. Use `established` only for the one a source calls the
body's creation. If sources disagree, record every claim; do not choose one (see §4).

### C. Names and parents over time

- **Names:** each earlier name, with dates or observation years. A rename keeps the same body. The
  Oil and Gas Appeal Tribunal became the Energy Resource Appeal Tribunal; that is one record with two
  names.
- **Parents:** which ministry, Crown corporation or agency the body sat under, by period, **with the
  ministry named as the source prints it**. Ministries were renamed often. The build matches printed
  names to the right ministry of that year, so do not translate "Ministry of Justice" into "Ministry
  of Attorney General".

The cabinet shuffles of 2001, 2005, 2017, 2020, 2022 and 2024 moved many branches between
ministries. Each batch has a table of the ministry that *most likely* held its bodies in each
checkpoint year, following the ministry lineage the atlas holds. It is a lead, and it is wrong for
some bodies: in 2010 the Climate Action Secretariat was printed under Environment, not the energy
ministry the lineage suggests, and in 2002 the Office of the Fire Commissioner was under Community,
Aboriginal and Women's Services. If the body is not there, search the whole volume.

**A budget heading is not always a parent.** The Estimates group spending for appropriation; an
independent tribunal or a commission can be funded through a ministry's vote without being part of
it (the BC Ferry Commission states that it is independent of the Province). Record the ministry a
budget prints the body under in `review.sources_checked` (`ministry_as_printed`). Add it to `parents`
only where a source places the body inside the ministry: an organization chart, an Act, or the
body's own description. Earlier-year columns in an Estimates volume are restated to the current
structure, so read placement from the volume of that year, not from a later volume's comparison
column.

### D. Bodies that are gone (discovery)

Twelve sub-agencies that no longer exist are recorded. A body is **gone** only where a source says
it was abolished, dissolved or wound up. A new name is not an end: a rename keeps one body, under the
same id, with the old name in `names`. Nor is a body gone because it now sits inside a larger one.
Two cautionary examples:

- The **Industry Training Appeal Board** was continued as the Skilled Trades BC Appeal Board
  (*Skilled Trades BC Act*, s. 42(1); renamed 1 December 2022). One body, already in the queue.
- **BC Ambulance Service** still operates, as part of BC Emergency Health Services.

Leads to test, each needing cessation evidence: Gaming Policy and Enforcement Branch (its functions
passed to the Independent Gambling Control Office on 13 April 2026), Emergency Management BC,
the Liquor Control and Licensing Branch, the Provincial Game Commissioner, the old Forest Service
divisions.
- Tribunals and boards abolished in the 2002–03 core review. The 2002/03 and 2003/04 annual reports
  of each ministry list its boards and commissions; `research/censuses/caws-2002-2004.json` shows the
  method for one ministry.
- Crown subsidiaries of BC Hydro, BC Rail, BC Ferries, BC Transit, ICBC and BCLC that were wound up.
  The notes to each Crown's financial statements list its subsidiaries by year.

Return a body in `gone` only with a sourced `ended`. Add a `replaced_by` or `merged_into` relation
where a source states one. Do not take the end from the date a successor began: bodies can overlap,
and a transfer of functions does not by itself abolish the old body. A lead you could not settle goes
in `note`, not in `gone`.

Following today's bodies backwards cannot find every body that has disappeared. That needs rosters of
the government at a given date: the boards and commissions lists in annual reports, and the
Estimates of that year read in full. `research/censuses/` holds the first of these.

### E. Other open research

Outside the sub-agency batches, the open items are in [`../WANTED.md`](../WANTED.md) (which ministry
answered for a Crown or agency in each year; ministers; staffing) and
[`../reviews/round-3/remaining-work.json`](../reviews/round-3/remaining-work.json) (historical
rosters for other ministries and eras; forty catalogue records in
`../discovery/roster-source-queue.json` waiting to be checked).

## 4. Rules of evidence

The build and its tests enforce these. The merge script (§8) refuses a batch that breaks them.

| Rule | Right | Wrong |
|---|---|---|
| **One claim, one source.** Every date, name and parent has a URL and a locator. | `"locator": "PDF p. 84 / printed p. 76, Vote 12 sub-votes"` | A claim with no page; "various sources" |
| **Keep the precision.** | `"date": "2004", "precision": "year"` | `"date": "2004-01-01"` for a year |
| **Unknown is not absent.** | `"established": null`, and `note` says what was searched | A guessed or rounded date |
| **A sighting is not a start.** | `first_observed: 2010`, `established: null` | `established: 2010` because the 2010 Estimates list it |
| **Stated, not inferred.** A parent only where a source places the body in that ministry. | `"relation": "part_of"` from an org chart | Parent inferred from who funds it, appoints its members or tables its report |
| **A function is not a body.** | "Fire protection began in 1874" as a `function_origin` event | That date as the Wildfire Service's `established` |
| **Disagreement is kept.** | Both dates, each with its source, and `evidence_status: "requires_reconciliation"` | Choosing one and dropping the other |
| **Wikipedia is a lead only.** | Follow its citation to the primary source and cite that | Wikipedia as the only source |

**For AI assistants in particular:**

- **Cite only what you opened.** Do not cite a document you did not read in this session. Do not
  reconstruct a page number, OIC number or date from memory. If you could not open a source, say so
  in `note` and leave the claim out.
- **Quote the words that support a claim** in `locator`, where they are short. For example: `"p. 12:
  'The Gender Equity Office was established in 2021'"`.
- **Distinguish** "not found" (you read the pages and it is not there) from "not checked" (you
  could not open it). Only the first goes in `sources_checked`, with the pages you read.
- **Do not fill a field to look complete.** An empty field with a reason is correct.

## 5. Where to look

Checked on 30 September 2026:

| Source | URL pattern | Notes |
|---|---|---|
| Estimates, 2020 onward | `https://www.bcbudget.gov.bc.ca/<year>/pdf/<year>_Estimates.pdf` | One PDF. Each ministry's vote lists its sub-votes and programs. |
| Estimates, 2010–2019 | `https://www.bcbudget.gov.bc.ca/<year>/estimates/<year>_Estimates.pdf` | Same structure. |
| Budget, 2002–2009 | `https://www.bcbudget.gov.bc.ca/<year>/default.htm` | Links to each ministry's service plan (`<year>/sp/<abbr>/<abbr>.pdf`) and the Estimates (`<year>/est/toc.htm`). |
| Service plans, 2010 onward | `https://www.bcbudget.gov.bc.ca/<year>/sp/pdf/ministry/<abbr>.pdf` | The abbreviation changes with the ministry's name. Find it from the year's `default.htm`; the directory listing is refused (403). |
| Annual reports, 2002 onward | `https://www.bcbudget.gov.bc.ca/annual_reports/<yyyy_yyyy>/...` | Ministry annual service plan reports, including lists of agencies, boards and commissions. |
| Laws and orders in council | `https://www.bclaws.gov.bc.ca/` | Acts, point-in-time versions, regulations, and the OIC search (`/civix/content/oic/`). |
| News releases, 2001 onward | `https://news.gov.bc.ca/` | Creation, launch, rename and transfer announcements. Older releases are in the archive. |
| Archived government pages | `https://web.archive.org/web/<year>*/<gov.bc.ca URL>` | For bodies whose pages have changed. The capture date is the observation date. |
| BC Archives | `https://search-bcarchives.royalbcmuseum.bc.ca/` | Authority records give administrative histories for older branches. It did not respond from our checker on 30 September 2026; try it in a browser. |
| Legislative Library | `https://www.llbc.leg.bc.ca/` | Ministry annual reports, Estimates and Public Accounts before 2002. Budget pages for 2000–2001 are not on bcbudget.gov.bc.ca. |

Also:

- **Crown corporations:** their annual reports and service plans, and the notes to their
  consolidated financial statements, which list subsidiaries each year.
- **Tribunals:** their own annual reports (most state their founding Act), and the Attorney General's
  tribunal-sector page.
- **Not usable:** the BC Government Directory (`dir.gov.bc.ca`) now requires a government login.
  Archived copies on the Wayback Machine still work.

## 6. What to hand back

Return one JSON object for the whole batch, with one record per body inside it:

```json
{
  "batch": "03",
  "records": [ { "...": "one object per body; the batch file has a skeleton to fill" } ],
  "gone": [ { "...": "bodies that no longer exist (track D), same shape plus ended" } ],
  "sources": [ { "id": "est-2020", "url": "https://…", "title": "2020/21 Estimates", "evidence": "estimates" } ]
}
```

### The fields of a record

| Field | Holds | Shape |
|---|---|---|
| `id` | The body's id from the batch. Do not invent ids for bodies in `records`. | `"gender-equity-office"` |
| `established` | The start (track B), or `null` | a **dated claim** |
| `first_observed` | The earliest sighting (track A), or `null` | a **dated claim**, with `meaning` saying it is a sighting |
| `ended` | Only for bodies that no longer exist | a **dated claim** from a source that states the abolition or dissolution; the date is the first day the body no longer existed |
| `names` | Each name, by period or observation | a **period row** with `name` |
| `parents` | Each parent, by period or observation | a **period row** with `ministry_as_printed` and `relation` (`part_of` or `subsidiary_of`) |
| `relations` | Predecessors and successors | `{type, body, date, precision, evidence, source, locator}`; `type` is `formed_from`, `split_from`, `merged_into`, `replaced_by` or `absorbed`; `body` is the other body's id |
| `research_events` | Other dated events: Act assented or in force, first members appointed, launch, rename | a **dated claim** plus `type` (snake_case, such as `legislation_in_force`) and `summary` |
| `date_claims` | Competing start dates | a **dated claim** plus `type: "establishment_claim"` and `summary` |
| `legal_basis` | The Act or OIC that creates or continues it | `{citation, source, locator}` |
| `evidence_status` | `documented_partial` for most results; `requires_reconciliation` where sources disagree | string |
| `note` | What you searched, what you could not open, and why a field is empty | string |
| `review` | `{checked, by, scope, sources_checked, unresolved_fields, full_history_complete}` | see below |

A **dated claim** is:

```json
{ "date": "2010-10-04", "precision": "day", "meaning": "What this date is the date of",
  "evidence": "statute", "source": "https://…", "source_id": "optional id from sources",
  "locator": "Page, section or paragraph", "checked": "2026-10-01" }
```

`precision` is `day` (`YYYY-MM-DD`), `month` (`YYYY-MM`), `year` (`YYYY`), `decade` (`1970s`) or
`circa` (`YYYY`). `evidence` is one of `statute`, `order_in_council`, `regulation`, `news_release`,
`annual_report`, `service_plan`, `estimates`, `public_accounts`, `official_webpage`,
`archival_description`, `financial_statements`, `gazette` or `secondary`.

A **period row** is either an observation or a period:

```json
{ "name": "…", "observed_on": "2010", "coverage": "observation_only", "evidence": "estimates", "source": "https://…", "locator": "…" }
{ "name": "…", "from": "2005", "to": "2017", "from_precision": "year", "to_precision": "year", "coverage": "documented_period", "source": "https://…", "locator": "…" }
```

Use `observation_only` when a source shows the name or parent on one date. Use a period only when a
source states the span. Other coverage values are `start_documented_end_unknown` and
`continuing_as_of_source`.

`review.sources_checked` lists every document you actually read for track A, **whatever the
outcome**, with the part you read in `scope`:

```json
{ "source": "https://www.bcbudget.gov.bc.ca/2015/estimates/2015_Estimates.pdf", "year": "2015",
  "listed": false, "outcome": "not_found_in_scope", "ministry_as_printed": "Ministry of Finance",
  "scope": "Finance vote descriptions, PDF pp. 119–121", "searched_for": ["Gender Equity Office", "gender equity"] }
```

`review.checked` is the day you did the research. `review.by` names the researcher or model.
`unresolved_fields` lists what is still open. `full_history_complete` is `true` only if the whole
lifecycle is documented, which is rare.

### A real example

The Court Services Branch, from the second research round (`../history/sub-agencies-researched.json`):
a sighting in the 2003 service plan, recorded as a name and a parent observation, with no start.

```json
{
  "id": "court-services-branch",
  "established": null,
  "first_observed": {
    "date": "2003", "precision": "year", "evidence": "service_plan",
    "source": "https://www.bcbudget.gov.bc.ca/2003/sp/ag/ag.pdf", "source_id": "r2-ag-plan-2003",
    "locator": "PDF page 17 / printed page 11, Judiciary paragraph", "checked": "2026-09-26",
    "meaning": "Court Services Branch named in the 2003 plan; not a founding claim"
  },
  "names": [{
    "name": "Court Services Branch", "observed_on": "2003", "coverage": "observation_only",
    "evidence": "service_plan", "source": "https://www.bcbudget.gov.bc.ca/2003/sp/ag/ag.pdf",
    "locator": "PDF page 17 / printed page 11, Judiciary"
  }],
  "parents": [{
    "ministry_as_printed": "Ministry of Attorney General", "relation": "part_of",
    "observed_on": "2003", "coverage": "observation_only", "evidence": "service_plan",
    "source": "https://www.bcbudget.gov.bc.ca/2003/sp/ag/ag.pdf",
    "locator": "PDF pages 16–17 / printed pages 10–11, Core Business Areas and Judiciary"
  }],
  "evidence_status": "documented_partial",
  "note": "The 2003 service plan names the branch and places it in the Ministry of Attorney General. This is an observation, not the founding year or proof of continuous placement.",
  "review": { "checked": "2026-09-26", "unresolved_fields": ["established", "complete_name_history", "complete_parent_history", "relations", "legal_basis"], "full_history_complete": false }
}
```

## 7. Before you hand back

- [ ] Every date has `precision`, `source` and `locator`, and its shape matches its precision.
- [ ] No sighting is recorded as `established`.
- [ ] Every parent is named as printed and placed inside that ministry by a source; a budget heading
  alone is recorded in `sources_checked`, not `parents`.
- [ ] Every checkpoint you read is in `review.sources_checked` with an `outcome` and a `scope`,
  including the non-matches. No start or end is taken from a non-match.
- [ ] Nothing is in `gone` without a source stating it ended; renames stay in `names`.
- [ ] Nothing is cited that you did not open; what you could not open is in `note`.
- [ ] Disagreements are kept as competing claims, not resolved.
- [ ] `review.checked` is today's date.
- [ ] New sources are in `sources`, with ids the records use in `source_id`.

## 8. For maintainers: merging results

```sh
npm run research:merge -- path/to/results.json --dry-run   # check, and show what would change
npm run research:merge -- path/to/results.json             # write into research/history/
npm run build:government                                   # recompile, and regenerate this queue
npm test
```

The merge script checks the batch against §4 and §6 and writes nothing if any record fails. It adds
to the existing research and never overwrites it. A start that competes with one already held goes in
`date_claims`, and the record is marked `requires_reconciliation`. The earliest sighting wins
`first_observed`. Every check, whatever its outcome, is kept in `review.sources_checked`. Choosing between
competing claims is an editorial decision, recorded in `../decisions.json` (see `../README.md`).

After rebuilding, open the Government view at a year the change affects, select the body, and check
its Evidence card.

**Not yet in the site.** The build compiles `first_observed`, but the diagram does not yet use it
to draw a body before its start date. Until it does, a sighting shows in the body's evidence, not
on the timeline. Recording sightings now is still the right order of work. The display rule, which
draws a body from its earliest sighting and marks its start as unknown, needs the evidence first.

## 9. A prompt for an AI assistant

Paste this, followed by this README and one batch file:

> You are helping research the history of the Government of British Columbia for PofBC, a site that
> draws the provincial government in any year since 1871 and cites a source for every claim. Below
> are a research guide and one batch of sub-agencies. For each body in the batch, do tracks A (first
> sighting at each checkpoint year), B (start) and C (names and parents over time), as the guide
> describes. Use only sources you can open in this session, cite the page for every claim, record
> every check with its outcome and the pages you read, and leave unknown fields null with the reason in `note`. Do not choose
> between conflicting sources; record both. When you finish, return one JSON object in the shape of
> the guide's §6, using the batch's skeleton, then a short plain-language summary of what you found,
> what you could not access, and what should be checked next.
