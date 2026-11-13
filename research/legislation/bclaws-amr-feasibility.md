# BC Laws "Acts/Ministers' Responsibilities" (AMR): build-time importer feasibility

Research date: 2026-11-13. Every claim below was checked with a live HTTP request from this
environment unless it is marked **unverified**.
Raw downloads and the throwaway parser were working files and are not kept in the repository.

---

## 1. Network: reachable

`www.bclaws.gov.bc.ca` is **not blocked**. It works through the preconfigured proxy with TLS
verification left on:

```
$ curl -sS -o /dev/null -w "%{http_code}" "https://www.bclaws.gov.bc.ca/civix/content/amr/amr/?xsl=/templates/browse.xsl"
200
$ curl -i https://www.bclaws.gov.bc.ca/civix/content/amr/amr/
HTTP/1.1 200 Connection Established
HTTP/1.1 200 OK
Content-Type: text/xml
...<root><dir><CIVIX_DOCUMENT_TITLE>Acts - Ministers' Responsibilities</CIVIX_DOCUMENT_TITLE>
<CIVIX_DOCUMENT_ID>1487865767</CIVIX_DOCUMENT_ID>...</dir>
<dir><CIVIX_DOCUMENT_TITLE>Historical Acts - Ministers' Responsibilities</CIVIX_DOCUMENT_TITLE>
<CIVIX_DOCUMENT_ID>471408611</CIVIX_DOCUMENT_ID>...</dir></root>
```

The Content API, the Document API, OIC PDFs (up to 11.8 MB) and the TLC XML all downloaded
without errors. I did not need WebFetch or WebSearch.

## 2. How the AMR collection is organized

The Content API (`/civix/content/amr/amr/<dirId>/`) returns XML directory listings:

- **Current** (`1487865767`) has three entries: "Public Acts – Listed by Minister" (dir
  `1345862399`, 24 documents), "Public Acts – Listed by Act" (dir `1781536098`), and "Private,
  Special and Local Acts" (a single document).
- **Historical** (`471408611`) has **47 snapshot folders**, from "2015 December" to "2026 August 31".
  Each folder holds the same three parts. Snapshot folders (newest first):
  2026-08-31, 06-30, 06-16, 04-26, 03-31, 03-19; 2025-12-18, 11-24, 08-06, 07-16, 06-29, 06-19,
  05-29, 01-31; 2024-11-27, 11-18, 11-17, 07-31, 07-22, 04-02, 03-31; 2023-12-06, 10-18, 07-20,
  03-31, 01-30; 2022-12-06, 07-07, 05-26, 03-31, 02-24, 01-04; 2021-07-15; 2020-12-15, 11-25,
  02-06, 01-21; 2019-07-18, 05-31, 03-28; 2018-07-30, 07-12, 2018 June; 2017 July, 2017 April;
  2016 June; 2015 December. **Nothing earlier than December 2015 is online.**
- **Document IDs.** Most historical documents follow `amr_<code>_<YYYY-MM-DD>`, for example
  `amr_ag_2026-08-31`, `amr_hlth_2026-08-31` and `amr_hlth_2015-12-16`. The rule is not
  reliable, though:
  - Some snapshots use numeric IDs. In the 2023-03-31 folder the "by Minister" folder is
    `1161797603`.
  - The ID date can differ from the folder title. Folder "2026 March 31" holds IDs dated
    `2026-04-01`, and folder "2026 March 19" holds IDs dated `2026-03-19`, but `amr_prem_2026-03-20`
    returns 404.
  - Current documents mix numeric IDs (`658625517` is Health) with `amr_emcr`, `amr_hous` and
    similar.
  - Minister codes change with each cabinet. In 2015 the codes included `arr`, `adved`, `just`,
    `flnr`, `tics` and `ti`.

  **An importer must walk the Content API tree. It cannot build IDs from a pattern.**
- **Every older period is its own retrievable document**, for example
  `https://www.bclaws.gov.bc.ca/civix/document/id/amr/amr/amr_hlth_2015-12-16`, which returns 200.

## 3. Document format: HTML only

AMR documents are stored as `.htm` files (`CIVIX_DOCUMENT_LOC` = `.../01_Public Acts – Listed by
Minister/12_hlth.htm`). Appending `/xml`, which returns real XML for statutes, here returns the
**same HTML** (`200 text/html`, 11,090 bytes, identical to the page without `/xml`). There is no
structured XML for AMR. The pages are loose XHTML (`<td nowrap>`, unclosed `<br>`), so the
importer needs an HTML parser rather than an XML parser.

A real entry from `amr_hlth_2026-08-31`:

```html
<p class="body">This page contains information for the period November 18, 2024 to August 31, 2026.
The information is from Order in Council 596/2024, as amended by Orders in Council 613/2024, 623/2024,
43/2025, 256/2025, 290/2025, 377/2025, 399/2025, 532/2025, 601/2025, 100/2026, 162/2026, 246/2026 and 260/2026.</p>
...
<th COLSPAN="2" bgcolor="#000000"><font color="#FFFFFF">MINISTER OF HEALTH</font></th>
<tr><th>Column 1 <br/>ACT</th><th>Column 2 <br/>DETAILS</th></tr>
<tr valign="top">
<td><a href="/civix/document/id/complete/statreg/96200_01">Hospital</a></td>
<td>The Act except sections 2 (3), 42.2 (3) (c), 46 (1), (4), (4.1) and (4.2), 48, 49, 50 and 53.</td>
</tr>
<tr valign="top">
<td><a href="/civix/document/id/complete/statreg/22043">Health Professions and Occupations</a></td>
<td>The Act except the following:<br>
(a)&nbsp;&nbsp;sections 308, 309, 317, 323 and 324;<br>
(b)&nbsp;&nbsp;section 531 (d) as that provision relates to the portfolio of the Attorney General and Deputy Premier.</td>
</tr>
```

What a row contains:

- **Act short title**, without the word "Act".
- **A link to the statute's document ID** (`96200_01`, `22043`). This is a stable join key to the
  statute and to its Table of Legislative Changes.
- **A free-text "details" scope.** It can be empty (the whole Act), "Section 51.", "The Act except
  ...", Parts, or prose such as "as those provisions relate to corporate affairs." **Section
  splits are prose, not structured data.**
- **No OIC reference and no date on any row.** Each page carries one period sentence and one OIC
  list.

One page has about 38 rows. The 2025-05-29 snapshot has 24 ministers and 678 rows in total.

## 4. Effective dates: per page only, not per assignment

Your concern is confirmed. Each page gives **only a listing period and the cumulative list of
OICs**.

Since 2017 the period is **cumulative from the base reorganization OIC**. It is not the window of
one snapshot. Every snapshot from 2024-11-27 to 2026-08-31 starts "November 18, 2024 to ...". So
the period start is the date of the base OIC (596/2024), and the period end is when the snapshot
was taken. **Neither is the effective date of any single row.**

The wording and model also vary:

- 2015–2017 snapshots use true windows ("December 16, 2015 to June 22, 2016").
- The 2024-11-18 snapshot uses different text ("responsibility for Acts assigned by Constitution
  Act Order in Council 596/2024") and includes full citations ("Gaming Control, S.B.C. 2002, c. 14").
- Some lists mix two base OICs ("602/2020 ... and by Order in Council 92/2022, as amended by ...").

**Worked example: why the listing period misleads.** I parsed two consecutive snapshots,
2025-01-31 and 2025-05-29. The only OIC added between them is 43/2025. The diff shows nine
consumer-protection Acts moving from PSSG to the Attorney General:

```
- ('Minister of Public Safety and Solicitor General', 'Business Practices and Consumer Protection', '')
+ ('Attorney General and Deputy Premier', 'Business Practices and Consumer Protection', '')
... (Motor Dealer, Sale of Goods, Ticket Sales, Cremation..., Motion Picture, Parental Liability, ...)
- ('Minister of Finance', 'Budget Measures Implementation (Residential Property (Short-Term Holding) Profit Tax) Act, 2024', '')
+ ('Minister of Finance', 'Residential Property (Short-Term Holding) Profit Tax', '')   <- Act retitled, not a reassignment
```

OIC 43/2025 (`/civix/document/id/oic/oic_cur/0043_2025`, a PDF) reads: "Approved and Ordered
January 30, 2025 ... orders that, **effective February 1, 2025**, Order in Council 596/2024 is
amended". Its Schedule repeals and adds Appendix B items, which are the AMR rows.

So the real effective date is 2025-02-01. The snapshots can only bound the change to
"after 2025-01-31, by 2025-05-29". The overall listing period would give "2024-11-18". **Approval
date and effective date also differ.**

**The OICs can be retrieved.** The BC Laws OIC collection has two parts:

- `oic_cur`: 2025 and 2026, in folders by number range.
- `arc_oic`: 1872–2024 by decade and year, for example
  `arc_oic/83_2020___2029/2029_89_2024/2024_07_0500_0599/0596_2024`.

The individual OICs are **PDFs**:

- 596/2024 is a 47-page scan, 11.8 MB, with poor OCR: "ss. I 0", "pwposes", "C itizens'".
- 388/2026 is born-digital and its text is clean. It is dated "Approved and Ordered September 1,
  2026". It amends Appendix B item 280 from Finance to Jobs and Economic Growth. That change is in
  the *current* listing ("November 18, 2024 to September 30, 2026", which adds 388/2026) but in no
  historical snapshot yet.

Most years also have a **"Resumes" folder of weekly HTML digests**, for example
`/civix/document/id/oic/arc_oic/2024resume48`. Each gives the OIC number, the approval date and,
where there is one, the effective date, with an "[re: ... Act]" hint:

```
ORDER IN COUNCIL 623 Statutory Authority: Constitution, ss. 10, 13 and 14
OIC 596/2024 is amended in Appendix B by repealing and replacing Items 140, 141, 221 and 225.
[re: Employment and Assistance Act ; Gaming Control Act ] Approved and Ordered November 29, 2024
```

Resumes exist for 2000, 2015 and 2024. The 1997 folder has no Resumes subfolder. I did not check
every year (**coverage unverified**).

**Manual work per assignment.** Snapshot diffing plus the Resume index can attribute most changes
automatically when only one new OIC appears between two snapshots. That held for 2025-01-31 →
2025-05-29.

When several OICs land in one gap (01-04 → 02-24 → 03-31 2022, or the Nov 2020 and Nov 2024
rebuilds), someone has to read the OIC Schedule and match its "item N" numbers to Acts. Appendix B
item numbers do not appear in AMR, so the match is by Act name. The scanned PDFs make automatic
extraction unreliable.

Rough estimate, **unverified**: about 47 snapshot gaps since 2015, with about 70+ amending OICs
named in the period lines. Perhaps 60–75% resolve automatically to "effective = OIC effective date
or approval date" from Resumes. The remaining 20–40 OICs need about 5–15 minutes each of reading,
so roughly 1–2 person-days.

The base reorganizations (2017, 2020, 2022, 2024) are simpler. Every row takes the base OIC's date.

Before December 2015 there are no AMR listings at all. Anything earlier would mean reading base
OICs directly, which would be a separate and much larger project.

## 5. Mapping to PofBC ministries: partly direct, needs a crosswalk

- AMR is keyed by **minister title** ("Attorney General and Deputy Premier", "Premier"), not by
  ministry. PofBC's `MINISTRY_EPISODES` (`src/government/episodes.js`, built on
  `src/ministries/history.js`) is keyed by **ministry name** at **year** granularity:
  `id = slug(name)-fromYear`, with an optional `date` only on the `LATER` additions.
- A naive "Minister of X" → "Ministry of X" check against the 2025-05-29 snapshot matched 21 of 24
  titles. The misses:
  - `Premier`: there is no ministry episode.
  - `Attorney General and Deputy Premier`: the episode is "Ministry of Attorney General".
  - `Minister of Citizens' Services`: history.js spells it "Citizen's".
- Matching by name alone also picks the wrong episode where names repeat. Public Safety and
  Solicitor General matches the 2001 episode, which episodes.js closes in 2012 and replaces with a
  `LATER` 2017 episode. **Matching must be date-aware and run against the corrected
  `MINISTRY_EPISODES`, not raw `EPISODES`.**
- Older cabinets add more titles to map: 2015 has `Minister of Justice`, `Minister of Natural Gas
  Development`, `Minister of International Trade` and `Minister of Small Business and Red Tape
  Reduction`. Ministers of State may also appear (**unverified** for AMR).
- Year-level episodes cannot settle cases where two episodes stand in the same year (2024 has both
  old and new). The crosswalk should pin `{amrTitle, validFrom, validTo} -> episodeId` explicitly.
  About 60–80 distinct titles across 47 snapshots is an estimate, **unverified**. That is a small
  hand-curated table.

## 6. Licence: permits embedding derived data, with conditions

The BC Laws home page lists "Acts/Ministers' Responsibilities", "Orders In Council" and "Laws of
British Columbia" (which includes the TLCs) under **"Licensed by: King's Printer"**. The King's
Printer Licence v1.1 (https://www.bclaws.gov.bc.ca/standards/Licence.html) grants:

- **2.1**: "use, copy, publish and distribute the Information by any means, in whole or in part".
- **2.2**: "include all or any portion of the Information in Your own product or application
  (including in combination with other information)", for commercial or non-commercial use.

Its conditions:

- **3.1** due diligence that the data is accurate and current.
- **3.2** do not remove or alter its notices.
- **3.3** prominently show this statement once:

  > "These materials contain information that has been derived from information originally made
  > available by the Province of British Columbia at: http://www.bclaws.gov.bc.ca and this
  > information is being used in accordance with the King's Printer Licence – British Columbia
  > available at: https://www.bclaws.gov.bc.ca/standards/Licence.html . They have not, however,
  > been produced in affiliation with, or with the endorsement of, the Province of British
  > Columbia and THESE MATERIALS ARE NOT AN OFFICIAL VERSION."

- **5.1** no suggestion of official status. **4.1(d)** no trademarks or Provincial symbols.

These terms differ from the Open Government Licence. API responses still carry an old "Queen's
Printer License" comment, but the current licence is v1.1. **Verdict: permitted, as long as the
attribution statement is shown in the app** (for example in an about or sources panel) and the
generated data file carries a source note.

## 7. Tables of Legislative Changes: usable for Act-level timelines

- **They are real XML.** `/civix/document/id/complete/statreg/E3tlc96180/xml` returns `text/xml`
  with a TLC schema (`TLC-XSD.xsd`).
- **Row types.** `<cif>` rows are changes in force: section, change type (am, rep, en), citation
  such as `2015-18-312`, and a date such as `28 Nov 2016 (BC Reg 216/2015)`. `<cnif>` rows are
  changes not yet in force. `<cbr>` rows are changes by regulation.
- **Coverage comes in four editions per Act:**
  - 1st: `tlc96200`, Jan 1 1997 – Dec 31 2004
  - 2nd: `e2tlc96200`, 2005–2013
  - 3rd: `e3tlc96200`, 2014–2023
  - 4th: `e4tlc96200`, Jan 1 2024 – present ("November 10, 2026")
- **Finding them.** Each Act's XML names its current TLC (`<act:tlc>E4tlc96200`), and the content
  folder `.../96200/tlc96200_f/` lists all editions. AMR rows link to `statreg/96200_01`, so the
  join key is direct.
- **Fit.** This gives a good second source for "when was this Act amended or repealed". It says
  nothing about which minister administers an Act. Dates are free text inside `<cifdate>` and
  need parsing. I did not check whether Acts enacted after 1997 lack some editions
  (**unverified**).

---

## Verdict

**Feasible, with a narrower claim than the audit proposed.** A build-time importer can reliably
produce:

1. snapshot-bounded, section-scoped Act-to-minister assignments from December 2015 on;
2. snapshot-to-snapshot change events, each tied to its candidate OIC(s).

It **cannot** produce per-assignment effective dates without an OIC-dating step. That step is
mostly automatic when a gap has a single new OIC (Resume HTML gives the approval or effective
date) and manual otherwise. Pre-December-2015 history is out of scope. Do not present the listing
period as an effective date. The 2025 consumer-protection move shows that doing so would be wrong
by months.

## Minimal importer design

**Inputs** (fetched at build time and cached to a vendored `data/bclaws-amr/raw/` so builds stay
deterministic and offline):

- the AMR Content API tree (historical and current), walked recursively;
- each "Listed by Minister" HTML document;
- optionally, the OIC Resume HTML for the years involved;
- a hand-maintained `amr-crosswalk.json` (minister title + validity → PofBC episode id);
- a hand-maintained `amr-oic-dates.json` (OIC → approved date, effective date, source, reviewer note).

**Pipeline**

1. Crawl and snapshot: about 47 × 25 ≈ 1,200 polite requests once, plus about 25 per new snapshot.
2. Parse the period sentence: base OIC, amending OICs, `periodFrom`, `periodTo`.
3. Parse rows: act title, statreg id, raw details string, a `scope` flag
   (`whole` | `partial`), and a best-effort list of sections (keep the raw text as
   authoritative).
4. Normalize Acts by statreg id, not title, to absorb retitles.
5. Diff consecutive snapshots into add, remove and scope-change events. Set
   `newOics = oics(n) − oics(n−1)`.
6. Date each event:
   - one new OIC with a known date → `effectiveDate`, `confidence: "oic"`;
   - otherwise `effectiveDate: null`, with bounds kept → review queue.
7. Map titles to episodes through the crosswalk. Unmapped or ambiguous → review queue.

**Output** (`src/data/amr.json`, the shape keeps the two kinds of date apart):

```json
{
  "source": { "collection": "bclaws amr", "fetched": "2026-11-13", "licence": "King's Printer Licence v1.1", "attribution": "These materials contain information ... NOT AN OFFICIAL VERSION." },
  "listings": [
    { "id": "2025-05-29", "docIds": ["amr_hlth_2025-05-29", "..."],
      "periodFrom": "2024-11-18", "periodTo": "2025-05-29",
      "baseOic": "596/2024", "amendingOics": ["613/2024","623/2024","43/2025"],
      "periodText": "This page contains information for the period ..." }
  ],
  "assignments": [
    { "act": { "statregId": "96200_01", "title": "Hospital" },
      "ministerTitle": "Minister of Health",
      "episodeId": "ministry-of-health-2011",
      "scope": "partial",
      "detailsRaw": "The Act except sections 2 (3), ... 48, 49, 50 and 53.",
      "seenIn": { "first": "2024-11-27", "last": "2026-08-31" },
      "effectiveFrom": { "date": "2024-11-18", "basis": "oic", "oic": "596/2024", "dateKind": "approved" },
      "effectiveTo":   null }
  ],
  "changes": [
    { "act": "Business Practices and Consumer Protection", "statregId": "...",
      "from": "Minister of Public Safety and Solicitor General", "to": "Attorney General and Deputy Premier",
      "betweenListings": ["2025-01-31", "2025-05-29"],
      "candidateOics": ["43/2025"],
      "effectiveDate": "2025-02-01", "dateKind": "effective", "basis": "oic-text", "reviewed": true }
  ],
  "review": [
    { "kind": "unmapped-title", "value": "Premier" },
    { "kind": "multi-oic-gap", "between": ["2022-01-04","2022-02-24"], "candidateOics": ["2/2022"] },
    { "kind": "retitle-or-reassign", "statregId": "...", "note": "Finance: Budget Measures ... -> Residential Property ... Profit Tax" }
  ]
}
```

`listings.period*` and `assignments.effective*` are separate on purpose. In the UI,
`effectiveFrom.basis` is one of `oic` | `bounded` | `unknown`, and only `oic` should be shown as a
date.

**Review queue.** The build emits `review` and fails CI only on new, unacknowledged items, using
the same pattern as the existing corrections tables in `episodes.js`. Item kinds:

- unmapped minister titles;
- gaps with more than one new OIC;
- rows whose statreg link is missing or changed;
- scope changes, where only the details text differs;
- snapshots whose period text fails to parse (the 2024-11-18 wording).

## Effort estimate (rough)

- Crawler, parser and differ, with tests against cached fixtures: **2–3 days**.
- Crosswalk curation (about 60–80 titles; 21/24 of the current ones map trivially):
  **0.5–1 day**.
- OIC dating: Resume scraper about 0.5 day; manual reading of multi-OIC gaps and scanned PDFs
  about **1–2 days**.
- UI surfacing and attribution: depends on design, not estimated.
- **Total: about 4–7 person-days** for 2015–present. Upkeep is a few minutes per new snapshot
  (about 6–8 a year).

## Risks

- **No XML, and the HTML is irregular.** The markup is loose, the period wording varies by era,
  and the ID scheme is inconsistent (numeric IDs, date mismatches, 404s on guessed IDs). The parser
  has to be defensive and walk the tree.
- **Section scopes are prose.** Structured section parsing will be partial. Keep `detailsRaw`
  authoritative.
- **Effective-date ambiguity.** Approval and effective dates differ (43/2025). Some OICs, such as
  451/2025, appear in a later OIC's authority list but not in the AMR period line. Why is
  **unverified**, possibly because it amended only Appendix A.
- **Scanned OIC PDFs** (596/2024) have unreliable OCR. Do not automate parsing their Schedules.
- **Retitled Acts read as reassignments** unless keyed by statreg id. Some rows may have no link.
- **Historical coverage stops at December 2015**, and snapshot cadence is irregular. The 2020-12-15
  → 2021-07-15 gap is 7 months.
- **Current vs historical lag.** The current listing (to 2026-09-30, including 388/2026) is ahead
  of the newest historical snapshot. Decide whether to ingest "current" as a provisional snapshot.
- **Mapping drift.** PofBC episodes are year-granular, and repeated names (PSSG) need date-aware
  matching on the corrected `MINISTRY_EPISODES`.
- **Licence compliance.** The KP attribution statement must be displayed. Under 3.1 the data must
  be kept current, which argues for a scheduled refresh.
- **Service stability.** The Licence says supply is not guaranteed (6.2). Vendor the raw HTML.
