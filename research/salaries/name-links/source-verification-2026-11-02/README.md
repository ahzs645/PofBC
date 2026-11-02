# Source verification of the 4,445 surname candidates

**251 source-spelling connections are individually reviewed and adopted.** Every
one of the original 4,445 candidates has a recorded source-comparison result.
The 251 adopted connections were checked against **252 rendered original rows**
from six hash-verified PDFs. This pass changes name links, without changing any
salary observation, amount, source definition, reporting label or record count.

Start with [dispositions.csv](dispositions.csv) for every candidate and its
primary-source links. [review-results.json](review-results.json) includes the
underlying original rows, exact row hashes and the reason for each decision.
The original candidate queue remains frozen in
[the preceding review](../connection-review-2026-11-02/README.md).

## Accepted connections

| Employer | Reviewed spelling connections |
| --- | ---: |
| Provincial Health Services Authority | 215 |
| Burnaby | 24 |
| Port Coquitlam | 10 |
| Pitt Meadows | 1 |
| Vancouver Coastal Health | 1 |
| **Total** | **251** |

Examples include Getmain/Germain, Murtby/Murthy, Lefi"esne/Lefresne and the
lowercase-L rendering lonescu versus Ionescu. These are source-spelling
corrections: the rendered original names, full remuneration-and-expense tuples,
employer and reporting context support the decision. They are not inferred from
name resemblance or salary similarity alone.

For each adopted connection:

1. One normalized spelling occurs only in the retained compilation.
2. **Every** observation under that spelling matches remuneration and disclosed
   expenses, to the exact cent, for the proposed official name. Unknown expense
   fields are not equated with zero; amounts are not rounded to force a match.
3. Among all official observations at that employer and corresponding year-label
   prefix, the monetary tuple is unique to that official normalized name.
4. The original PDF bytes agree with the accepted SHA-256. Its physical page and
   rendered source row were inspected for the literal name and both monetary
   fields. Municipality remuneration follows the already accepted component
   definition; expense-inclusive totals are not used as pay.
5. The compiled observations remain unchanged and separately accessible. A name
   connection does not prove duplicate payments, verify a compiled reporting
   period, or establish a complete lifetime identity or employment history.

Case 1082 has two compiled observations and was checked in two different original
reports. The review therefore covers 252 original rows for 251 connections.
Pre-existing one-dollar expense-inclusive residuals in Port Coquitlam cases 285
and 2506 remain unchanged; see [visual-review.json](visual-review.json).

[source-reviewed.json](../source-reviewed.json) is the application input. It
records the exact spellings, preferred original spelling, evidence pages and
hashes of all compiled observations and official witnesses. During every rebuild,
`validateReviewedNameConnections` rechecks completeness, monetary uniqueness,
row multiplicity, source hashes and physical pages. A later source or row change
cannot silently inherit an outdated review.
Record guards use employer slugs and reporting labels instead of temporary
index offsets, so adding unrelated employers or historical periods does not
invalidate unchanged source evidence.

## Decisions for the other candidates

| Result | Candidates | Treatment |
| --- | ---: | --- |
| Both names occur as separate rows in the same original schedule | 926 | Keep apart; there is no affirmative identity evidence for joining them |
| Both spellings occur in official disclosures, without a common original schedule | 2,607 | Hold for dated biographies, original-row review or an explicit employer correction |
| A complete unique remuneration-and-expense match is not established | 436 | Hold; inspect source layout, components, dates and possible homonyms |
| Neither spelling has accepted primary salary observations in the dataset | 224 | Locate original schedules; professional biographies can corroborate identity separately |
| Pittman at BCI | 1 | Identity supported, application join held for USD compensation treatment |
| **Still unconnected pending sufficient evidence** | **3,268** | |

The 926 same-schedule cases are not declarations that the people are necessarily
different: they are explicit reasons to avoid joining two disclosed names without
support. The 2,607 other official pairs also remain ambiguous; an official source
can faithfully disclose two real surnames or an original spelling variation.
They cannot be treated as vendor transcription errors merely because the names
look similar.

The full scan is a computational comparison of current original-source
observations for every candidate. **It is not a claim that 4,445 people received
independent biography checks.** The 251 adopted source corrections received the
rendered-row review described above. The held cases state the evidence still
needed. No requests, messages or paid searches were sent.

Additional original-document leads were located for Northern Lights College's
Jonathan Todd Bondaroff and Forestry Innovation Investment's Sonya
Zeitler-Fletcher; see [external-source-leads.json](external-source-leads.json).
Those documents corroborate full names and roles, but this pass does not
silently accept them as employee salary cohorts or treat their component totals
as equivalent to the retained compiled observations. Public professional
profiles, including LinkedIn, can support later identity review; matching a
profile name is insufficient to join ambiguous salary records.

## Application behavior

Automatic name rules stay surname-bound. Only explicitly reviewed pairs can
connect different surnames. Each adopted connection has a clickable source-page
link on the person detail page. Both original names and amounts remain visible,
including compiled-period caveats.

A reviewed correction can change the two-letter surname slice, such as lonescu
(`lo`) to Ionescu (`io`). Link groups are published under both slices, and the
canonical person page loads all required record slices before showing the
history. A failed slice gives a retry message instead of a partial history. Old
misspelled links still offer navigation to the reviewed name. Existing likely
name variants retain their uncertainty; source verification of one typo does
not upgrade an entire name family to a verified identity.

BCI's Pittman link remains held. The original report explicitly labels the later
3,902,330 as USD executive total compensation, and the earlier compiled amount
differs from the annual report total. Currency-aware display and comparison
treatment are still required before joining that history in the app.

## Reproduce

From the repository root:

```sh
python3 -m unittest discover -s scripts -p 'test_name_connection*.py' -v
python3 scripts/review_name_connection_evidence.py --write-reviewed --check
node --test scripts/reviewed-name-connections.test.mjs src/salaries/nameLinks.test.js
npm run build:name-links
```

The check regenerates every computational disposition and validates the manual
review's hashed crops and contact sheets, without fetching live sources or
overwriting reviewed files. To regenerate the initial candidate snapshot, use
the committed publication ref documented in the preceding review.

To reproduce rendered crops, download the six original PDFs referenced in
[render-manifest.json](render-manifest.json), verify each accepted hash, and name
each file `<sourceId>.pdf` in a cache directory. With PyMuPDF 1.26.6, Pillow and
DejaVu Sans installed:

```sh
python3 scripts/render_name_connection_evidence.py --cache /path/to/source-cache
```

The renderer uses the pinned original PDF and either frozen PHSA source-band
coordinates or native PDF word coordinates. Full row pixels are retained in
[renders](renders); contact sheets add explanatory labels above those pixels.
Re-rendering can change review hashes and requires reading the resulting sheets
before updating the manual review. It does not constitute automatic approval.

[inputs.json](inputs.json) pins every publication shard used by the evidence
comparison. [visual-review.json](visual-review.json) records all 26 contact
sheets personally inspected by the root reviewer, with no unresolved rendered
row discrepancies in the adopted set. Salary values and source metadata are
byte-identical to the previous published release.
