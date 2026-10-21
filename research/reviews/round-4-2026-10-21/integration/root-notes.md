# Round 4, root module: integration notes

Hospital districts, the 1988 franchise, FOIPPA classes and the 1977 titles: 199 claims. 98 applied
through 11 events; 101 under `not_applied` with reasons. Generator (outside the repository):
`scratchpad/r4-work/root/build.py`; it checks ids, URLs, and that every claim is used or set aside.

## The main decision: hospital districts are not drawn as bodies

Regional hospital districts (RHDs, from 1967) and hospital improvement districts (HIDs, 1951-1972)
are **local corporations** created under provincial statute. They are not provincial government
bodies:

- An RHD's board is made up of the directors of the matching municipal regional district (OIC
  527/1972 recitals; Hospital District Act s.8). It raises hospital capital by requisitions on its
  members. The minister approves its capital spending and can inspect it (s.45).
- An HID was an improvement district under the Water Act. Its trustees were elected by landowners,
  and it filed its statements with the Comptroller of Water Rights.
- No source in the module says a ministry *answered for* any of them. The report says outright that
  they are "not simply ministry branches". Rule 4 therefore gives them no `responsible[]`.

`health-authority` does not fit: those bodies govern or deliver health services and answer to the
Ministry of Health; these districts fund capital and run nothing. 68 local corporations in the
provincial lanes would misdescribe them, as school districts or municipalities would.

What I propose instead:

1. **Events on the ministry that recommended each order** (9 events). Each OIC names the
   recommending minister: Health Services and Hospital Insurance in 1967-72, Health in 1995-98. The
   event records something the department did under the statute. It does not claim the districts
   were its bodies.
2. **A local register, not drawn** (`local_register_proposal`): a proposed
   `research/history/local-hospital-districts.json` with two new kinds, `regional-hospital-district`
   and `hospital-improvement-district`. Each record carries names by period, an established date
   with its meaning, an ended date or `not_traced`, typed transfers (deadline kept apart from the
   actual transfer day), board and membership rules, and conflicts. It has no `responsible[]`. The
   proposal includes two examples, Greater Vancouver RHD and Creston Valley HID, built only from the
   sources. Same-named corporations keep separate ids (Cariboo 1968 and 1996; East Kootenay and
   North Okanagan 1967 and 1996).
3. Once G1's typed relations exist, the register supplies `funds` and `assets_transferred_to`
   lines (e.g. Greater Vancouver RHD to South Fraser HR and Vancouver/Richmond HB).

## Events applied (all `documented`, day precision)

| Date | Subject | What it dates |
|---|---|---|
| 1967-04-13 | Dept of Health Services and Hospital Insurance | OIC 1222/1967 approved: 27 areas defined. Not a common incorporation date |
| 1969-09-25 | same | OIC 3082/1969: 23 HIDs dissolved, all their assets and liabilities passed to paired RHDs |
| 1972-02-08 | same | OIC 527/1972 approved: 28 RHDs aligned to regional-district membership. Not new incorporations |
| 1995-12-12 | Ministry of Health 1976 | Fraser Valley RHD in force, amalgamating three (approved 7 Dec). Not the Fraser Valley Health Region |
| 1995-12-31 | same | OIC 1549/1995 restriction effective (approved 14 Dec). A restriction, not a dissolution |
| 1996-01-01 | same | 12 new RHDs in force (OICs 1550-1561/1995, approved 14 Dec). Not the health boards of the same names |
| 1998-11-19 | same | OIC 1429/1998: 13 RHDs' powers restored, two renamed, five dissolutions ordered |
| 1998-12-31 | same | The five 1996 RHDs dissolved. Also the transfer deadline; the actual closing days are not known |
| 1999-01-01 | same, related: South Fraser HR, Vancouver/Richmond HB | Greater Vancouver RHD dissolved; four groups of recipients, with the reversion conditions stated |
| 1977-10-21 | Ministry of Health 1976 | OIC 3240/1977 orders the titles proclamation, with exceptions. Not the proclamation itself |
| 1977-10-21 | same | 1994 Table of Statutes: c.75 amendments to the Hospital Corporations Act in force that day. Corroborates only those sections |

Duplicates: none held. The existing `primary-evidence-health-act-title-1977` event is the assent
(27 Sept 1977); its note mentions the authorization, but no event records it. It stays as it is.

## Set aside (see `not_applied`)

- 28 original RHD incorporations; Fort Nelson-Liard 1987 and Stuart-Nechako 1998; RHD renames;
  dissolutions 2000-2025; OIC 524/1996; all 25 HID letters patent and the 1972 HID endings. These
  are register material: their subjects are not atlas nodes.
- The hospital societies' 1971 incorporations come only from recitals in the 1972 orders, and the
  1972 transfers rest on certified board resolutions rather than conveyances (peer review
  BR-PR-03). The societies are not provincial bodies.
- R4RC-184 is `context_only_use_per_entity_dated_rules`: not applied; per-district rules go to the
  register. R4RC-104 (current Hospital District Act) is a checkpoint for G1/G3, never backdated.
- Franchise, R4RC-105 to 109: the atlas has no subject for them. The franchise lives in
  `franchiseIn` (src/government/snapshot.js) and models only exclusions before 1949.
  **Supersession R3G-F027 -> R4RC-106:** R3G-F027 does not appear anywhere in the repository
  outside the round-4 folder, so there is nothing to correct. The 28 March 1988 date should be used
  when the franchise becomes dated data, with order approval (25 March) kept apart from
  commencement (28 March).
- FOIPPA classes, R4RC-110 to 112: the atlas has no FOIPPA or Information and Privacy Commissioner
  subject, and a class rule needs a matching body. These are input for G2.
- Alberni-Clayoquot treaty membership, R4RC-198 and 199: neither the district nor the First
  Nations governments are nodes. These are input for G7.

## Corrections to existing data

None. The eight original-versus-recital conflicts concern undrawn bodies: register `conflicts`.

## Open questions, rewritten

- **A8 (narrowed).** (1) When was the *original 1968* Cariboo RHD (OIC 2236/1968) dissolved? Search
  the BC Laws OIC archive (arc_oic, 1996-2026) for "Cariboo Regional Hospital District" rescission
  orders, and check the Cariboo Regional District's hospital-district records. Hand back the OIC
  number, approval date, effective date and any transfer recipient. (2) On what day did the
  Peace River RHD (1967) take the name Peace River-Liard? Look for supplementary letters patent
  from 1970-72 recommended by the Minister of Health Services and Hospital Insurance. The 1970
  municipal rename (OIC 3028/1970) does not count. (3) Were there HIDs outside the 25? Check the
  Comptroller of Water Rights' improvement-district register and BC Gazette Part I, 1946-72, and
  hand back each name, letters-patent OIC and dissolution order. (4) For the repository: approve or
  reject the register and its two kinds.
- **C2 (narrowed).** Find the issued proclamation under the Ministerial Titles Amendment Act, 1977.
  It should be in BC Gazette Part I between late October and November 1977 (Legislative Library;
  archive.org Gazette scans). Hand back the proclamation's date and effective date, and whether it
  names the Department of Health Act. Failing that, the 1978 or 1979 Table of Statutes entry for
  the Ministry of Health Act would serve.
- **G2 (narrowed).** For each drawn body, on what date did FOIPPA first apply to it? Answer by
  matching the body to a 1994 or 1995 class or to its Schedule 2 entry, using point-in-time FOIPPA
  Schedule 2. The Ombudsperson Act schedule history comes from the BC Laws historical tables.
- **G5 (narrowed).** Create a dated franchise file: one row per qualification change, each with its
  Act, assent, commencement and conditions. The remaining gaps are the colonial voting
  ordinances (1859-71) and the 2003 Election Amendment Act's commencement (2003-04 Table of
  Statutes), which separates the statutory repeal of the prisoner disqualification from the
  earlier Charter rulings.
- **G1, G3, G4, G7 (unchanged).** Worked examples only (funding and transfer lines, local board
  rules, capital funders are not service providers, treaty-Nation RHD membership); model work.

## Summary

11 events (9 on the hospital-district framework, 2 on the 1977 titles), 0 body changes, 0 new
bodies (a separate, undrawn local register is proposed with two new kinds), 101 claims not applied
in 12 groups, and no corrections to existing data. Blocker: none for the events. The register
needs the maintainers to agree to a new file and kinds that the diagram builds do not read.
