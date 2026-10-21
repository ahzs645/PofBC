# Round 4, carried Round 3 evidence: integration notes

Scope: carried Round 3 evidence no other module applied (D2, D3, F6, the rest of `health/prior/`,
D4, E4-E7, H1, H2, H5, H6), checked against the four modules and the repository. Nothing under
/home/user/PofBC was written; the build ran only in a copy (`scratch/repo`).

**Source URLs.** The carried round-3 health and crowns claims have no source register in the
package. Where a claim gives a stable identifier, the URL is built from it and re-fetched on
2026-10-21: UBC Open Collections items
(`https://oc-index.library.ubc.ca/collections/bcsessional/items/<item>`, the form the repository and
the handback's own asylum file use) and OrgBook BC topics
(`https://orgbook.gov.bc.ca/api/v4/topic/<id>/credential-set`, the form the branches module's
R3F-EXT-006 uses). Every passage cited was read in the fetched text.

## D2: the Treasury Department's ministers (code fix)

The 17 years are the Treasury Department's 1899-1915. `ALIASES` maps the episode key `treasury` to
the portfolio key `finance`, but until 5 June 1916 the Executive Council styled the portfolio
"Minister of Finance and Agriculture" (key `finance agriculture`). Those terms matched only the
Department of Finance and Agriculture episode. From June 1916 ("Minister of Finance") they already
matched. The evidence is 18 Public Accounts transmittals headed "Treasury Department" and signed
"Minister of Finance", 1899-1916 (R3H-142 to -164). I re-read 1899, 1904, 1909, 1913 and 1916 in the
UBC text. The votes are headed "Department of Finance. (Treasury.)" (1898/99) and "Department of
Finance and Agriculture. (Treasury.) Minister of Finance and Agriculture" (1903/04).

- **Fix** (`code_diffs[0]`): the alias may list keys, `'treasury': ['finance', 'finance agriculture']`,
  and the match test reads the list. No term is created, stretched or bridged. Thirteen roster terms
  (Carter-Cotton 1898 to Campbell 1916) are now attached to both concurrent episodes on their own
  dates. Tested in the copy: 1,069/1,236 terms matched (unchanged); Treasury years without a
  minister went from 17 to 0 (2,229/2,229 ministry-years covered); `node --test` 421 pass.
- **Data**: each transmittal becomes `corroborating_evidence` on the one term containing its date
  (`data_changes`, 9 terms). All 18 fall inside a term held by the signer. A signature corroborates
  a term; it is not a tenure.
- **Events**: the two vote headings (`name_observed`), as the documented basis of the alias.

## D3: the 1978 Ministry of Transportation, Communications and Highways

The repository already has the plural portfolio and Fraser from 1978-12-05 (ministers-1975-1991,
record 38; LLBC errata row 17), and he was already matched. The matcher folds "communications" to
"communication". What was missing is the instrument and the title:

- **OIC 3018/1978**, approved 5 December 1978 (recommended 4 December), para (d), renames Highways
  and Public Works. It is proposed as an `executive_names_directive` event, the type used for OIC
  3199/1976.
- **OIC 3019/1978**, the same day, designates "Alexander Vaughan Fraser, Minister of Transportation,
  Communications and Highways". It is added as corroboration on record 38.
- **Optional diff** (`code_diffs[1]`): a `SPELLING` entry giving the episode the plural name. This
  changes its id to `ministry-of-transportation-communications-and-highways-1978`, so the event's
  `subject_id` must move with it. Nothing else refers to the old id. Tested: lineage unchanged,
  tests pass.

## F6: Environmental Appeal Board and Powertech (sub-agency batch and decisions)

I re-read OICs 2602, 2603 and 2604 of 1981 and both OrgBook credential sets. `sub-agency-batch.json`
(also inside proposal.json) passes `merge-research.mjs --dry-run`.

- **EAB**: established 1982-01-01 (OIC 2603/1981, under s. 11). Events: ss. 11-12 in force (2602);
  first members and chairman Hillier (2604). All three orders were approved 18 December 1981. The
  record is held as `requires_reconciliation`, so a decision (`eab-established-1982-01-01`) sets
  aside 1981 (the Act's year) and the manual's 1982. It supersedes the Round 2 recommendation. The
  merge keeps the held 2003 legal basis and adds the 1981 one as a `legal_basis_claim`.
- **Powertech**: established 1988-09-29 (incorporated as 352143 B.C. Ltd.), renamed Powertech Labs
  Inc. 1989-01-06. BC Hydro's "inception in 1979" (2020 plan) is a `function_origin_claim`. The
  decision sets aside 1989 (BC Hydro's service year) and 1979. The registry does not show BC Hydro's
  ownership from 1988; the identification rests on the name. The operating start is still open.

## Other carried files and items

Applied, beyond D2, D3 and F6 (all integrator-verified against the live source):

- **Royal BC Museum (H3)**: opened 2 December 1886 and moved in May 1889, from the curator's 1897
  report (R3H-167). These are events beside the existing year-only founding, not replacing it.
- **BC Enterprise Corporation (E6)**: it is BC Place Ltd.'s company, BC0207097 (certificate 207097,
  the one the 1980 Act names). The changes:
  - `bc-place-ltd` starts 1980-03-25 (registry registration), replacing BC Archives' 1980-05,
    which the existing event already called unverified.
  - BCEC's 1989-09-30 end gets an `endedMeaning`: a cessation and asset transfer, not a
    dissolution.
  - The registry name (20 August 1987, which conflicts with the atlas's March 1987), the 1993
    restoration and the 27 March 2023 administrative dissolution become events.
  - The body is not redrawn to 2023, as with MTOC.
- **BC Games Society (E7)**: registered 26 June 1987 as the B.C. Summer and Winter Games Society.
  Its three names are added as periods, and an `establishedMeaning` says the 1977 start is
  Wikipedia's. I did not replace the 1977 start, because the Games may predate the society as a
  program (rule 8).
- **Creative BC (E7)**: the society is the Film Development Society of BC (registered 1987),
  renamed 25 February 2013. This is an event; the April 2013 launch is kept. The Film Development
  Society is not an atlas body, so no new body is proposed.

Set aside (reasons in `not_applied`): `elections_followup_claims.json` (statutes with no atlas
subject; they need the franchise file, G5); departmental actuals, the 1889 asylum estimates and the
staffing counts (mixed scopes; `atlas/staffing.json` is FTEs from 2000/01 and no spending file
exists, H4); the Public Accounts inventory (a finding aid); the regulator crosswalks (as the health
module: no regulators layer, no URLs); `prior_package_carryforward.json` (a packaging index, its two
supersessions already handled); other E4-E7 claims (already held, without a URL, or not atlas
entities); D4, H1, H2, H5 and D3's file (round-3 files not in the package); H6 logos (the gallery's:
the 1986 BC Transit flag-lockup sighting and the BC Ferries 1983 use claim are noted for its owner).

## Open questions, rewritten

- **D4**: each deputy minister, minister of state and parliamentary secretary before 2026, with
  appointment and ending orders (Gazette Part I; BC Laws OIC archive). Return holder, office as
  styled, from/to and OIC numbers.
- **E4**: the first BC Ferries Commissioner's appointment OIC (arc_oic 2003) and first report, kept
  apart from the office's 1 April 2003 start; and whether the modern Ferry Authority is in scope.
- **E5**: the orders bringing the Public Sector Pension Plans Act's ss. 5-8 and 16-20 into force
  (arc_oic 1999-2000), and the LTSA's 2005 commencement order: order numbers and in-force days.
- **E6**: what happened to BC Enterprise Corporation in March 1987 (BC Laws hstats and arc_oic 1987),
  to settle March against the registry's 20 August.
- **E7**: whether a government program ran the BC Games before the society's 1987 registration, and
  under what 1977 instrument (arc_oic 1977-78; 1978/79 Estimates); and Creative BC's 2013 launch.
- **F6**: when BC Hydro acquired 352143 B.C. Ltd. and when Powertech began operating (BC Hydro annual
  reports 1988/89-1989/90, subsidiaries note; arc_oic 1988-89). Return both dates with meanings.
- **H1, H2, H5**: re-deliver the round-3 tables with source URLs. For H2, give a Journals page for each
  of the 140 older session ends; for H5, the Reg. 14/88 Gazette deposit and the 2005 OLA-TRU agreement.
- **H3**: which pre-1905 offices of the Provincial Secretary and Lands and Works were distinct bodies,
  and the statute or OIC creating each (not reporting letters).
- **H4**: a historical-scale file with one explicit measure per row, from the 103-item UBC Public
  Accounts inventory, visually checked.
- **H6**: masters and permissions; leads are BC Ferries FOI 23-016 and WorkSafeBC's archives (1968).
