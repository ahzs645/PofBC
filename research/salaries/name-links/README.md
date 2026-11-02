# Name links

The [2 November 2026 connection review](connection-review-2026-11-02/README.md)
adds a repeatable scan of every published named observation, a queue of possible
surname variants, and original-source findings for BCI. It distinguishes the
existing heuristic `verified` status from independent source review. The Pittman
connection is supported by primary evidence but held from new application joins
pending treatment of the later USD executive-compensation amount. This research
pass does not change the links applied by the site.

Employers write the same person's name differently from year to year ("Garant, D." in 2017/18,
"Garant, Daniel" in 2023/24), sources disagree, and extraction splits letters off ("Nevill, T homas").
This list says which spellings **at one employer** are one person, how sure that is, and why. The
site joins exactly what it lists: on the People browse ("Also disclosed as D. Garant · likely the same
person") and on a name's page, where each record under another spelling says how it was disclosed.

Run `npm run build:name-links` (also run by `npm run build:salaries`). The rules are in
`src/salaries/nameLinks.js`, with tests in `nameLinks.test.js`.

## Files

- `decisions.csv` — every decision, highest pay first: `verified`, `likely` or `apart`, the spelling,
  what it was joined to, and the reason. Read this to check the joins.
- `summary.json` — counts by decision and by reason.
- `reviewed.json` — decisions made by reading the records. They override the rules either way: add
  `"decision": "verified"` to join two spellings the rules miss, or `"reject"` to keep apart two the
  rules join.
- `public/salaries/links/` — the joins the site loads, sliced by surname like the people index, plus
  `top.json.gzip` for the highest-paid browse.

## Verified: the records establish it

- **Extraction split** — joining the first two parts of the given name gives the other spelling
  exactly: "T homas" is "Thomas".
- **Same position** — a title held by three or fewer names at that employer appears under both
  spellings: "Fyfe, G." and "Fyfe, Gordon" are both CEO/CIO of BCI.
- **Same payment twice** — both spellings in one period with the identical payment: one record
  disclosed twice.
- **Position in the name** — the same name with the job title run into it ("Glickman, Eva
  Director, HR Payroll Services", in West Vancouver's disclosures).
- **Reviewed** — `reviewed.json`.

## Likely: the assumption

A spelling joins a fuller one when **all** of these hold:

1. Same employer and surname. Nothing is joined across employers.
2. The names agree: each given name equal, an initial of the other, or (first name only) the start of
   the other of three or more letters ("Jeff" and "Jeffrey"). A middle name one spelling leaves out
   does not disagree.
3. It is the **only** fuller name at the employer that agrees. "Jones, D" at Surrey, with both David J
   and Donna L. there, is kept apart.
4. The two never appear in the same period. Two records in one period are two people ("Canning, S" and
   "Canning, SE" at BC Hydro, every year 2012/13–2023/24).
5. They are within 6 years of each other.
6. Between neighbouring years (a year or less apart), pay does not change more than 3×. Over longer
   gaps a jump is as often a promotion as a different person — "Rayes, R.", a director at $406,722 in
   2017/18, is likely "Rayes, Ramy", an executive vice president at $2.6 million in 2023/24 — so it is not
   weighed.

Most likely joins are a whole employer changing how it writes names: SFU used initials through
2018/19, UBC added middle names in 2025/26, Surrey switched to initials in 2022, and the public service's earliest
records (1999/00–2002/03) often give initials only.

## Kept apart

Several fuller names fit; both spellings in one period; more than 6 years apart; a pay jump between
neighbouring years; a spelling that disagrees with a name already joined; or a reviewed rejection.
Where the names agree, these still appear on a name's page under "Possible matches", as before.

## Reviewed so far

The highest-paid decisions in each group were read by hand. That review added four joins
(`reviewed.json`): Daniel Garant at BCI (confirmed by the site owner); "Wong, Jason Lany" and
"Wong, Jason Larry" at PHSA (one misread); and "J G", "J GRAY" and "J GARY" Cohen in the public
service (the same $160,698 appointee payment). It also confirmed some rules: "Galbraith, David" stays
apart from the deputy minister "GALBRAITH, DAVID L" because a probation officer shares the spelling,
and "Johnson, J" at SFU stays apart because Joanne and Joy both fit.
