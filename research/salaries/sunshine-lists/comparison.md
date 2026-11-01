# Sunshine Lists comparison and salary source queue

**Comparison status: incomplete-reference.** Reference captured 2026-11-01T06:11:30.217Z.

The supplied snapshot contains **3 employers** and **0 annual observations**. **It is not a complete Sunshine Lists employer inventory.** 3 employer entries contain summary evidence only.

All **926,855 published PofBC observations** across **206 employers** were reconciled against the actual employer files: **683,243 official-source observations** and **243,612 retained compiled observations**. 119 employers have some official records; 87 have compiled records only.

## Observed reference employers

| Sunshine Lists employer | Identity match | Reference summary | PofBC official rows | PofBC compiled rows | Comparison result |
| --- | --- | --- | ---: | ---: | --- |
| [Core Government](https://www.sunshinelists.ca/british-columbia/employers/core-government) | public-service | 179,103 records; 2007-2025 | 220,106 | 0 | summary-only |
| [Fraser Health Authority](https://www.sunshinelists.ca/british-columbia/employers/fraser-health-authority) | fraser-health | 111,202 records; 2014-2025 | 111,206 | 0 | summary-only |
| [Provincial Health Services Authority](https://www.sunshinelists.ca/british-columbia/employers/provincial-health-services-authority) | provincial-health-services-authority | 103,411 records; 2005-2025 | 0 | 24,923 | compiled-only-summary |

Reference totals span the source’s own reported years and definitions. The table deliberately does not subtract employer-wide totals: PofBC can include different years and disclosure categories. A range is not an annual series.

## Repository coverage by sector

| Sector | Employers | With official records | Compiled only | Official observations | Compiled observations |
| --- | ---: | ---: | ---: | ---: | ---: |
| Crown corporations | 41 | 6 | 35 | 65,950 | 43,992 |
| Government | 1 | 1 | 0 | 220,106 | 0 |
| Health authorities | 8 | 5 | 3 | 243,958 | 68,658 |
| Municipal police | 13 | 0 | 13 | 0 | 9,232 |
| Municipalities | 105 | 102 | 3 | 117,100 | 28,211 |
| School districts | 14 | 1 | 13 | 10,568 | 45,385 |
| Universities and colleges | 24 | 4 | 20 | 25,561 | 48,134 |

## Processing queue

The [work queue](work-queue.csv) contains **225 existing official-source tasks** and **3 reference-comparison tasks**. Existing leads are linked to their original report or archive and retain the recorded next action. They do not prove that additional records are available or that a report has passed validation.

Priority 1 covers missing official employer/period coverage, held partial employee disclosures, or a smaller comparable count. Priority 2 requires scope, period or source review. The priority is an action order, not a count of missing employees.

## How coverage is judged

- The comparison covers only employers and annual observations present in the supplied snapshot. Partial input is never a complete directory audit.
- A displayed employer-wide year range is preserved as a range, not expanded into assumed annual observations.
- Calendar, fiscal and compiled edition labels are distinct. Only verified reporting dates establish an exact fiscal period match.
- Employer identity matches and equal aggregate counts do not establish record-level equality, unique people, or complete employee coverage.
- Directory completeness concerns employer enumeration only. It does not establish a complete annual series for each employer.
- Existing source leads are a processing queue, not accepted salary records or proved missing observations.

## Files and reproducibility

- [Machine-readable comparison](comparison.json) contains every observed employer, annual decision, source task and SHA-256 input fingerprint.
- [All PofBC employers](repository-employers.csv) lists accepted official employee periods and compiled edition labels separately.
- [Work queue](work-queue.csv) is suitable for filtering by employer, period, source status and priority.
- [Usage and snapshot format](README.md) explains importing a saved snapshot and rerunning the audit.

Repository input fingerprint: `29d8eb75db2236ecc05bbafd72f7be6e12a986040ead1a8552d82737848a9d7d`.
Reference snapshot fingerprint: `5955544e5deef4dcc72fcb201137dd943053ef78deeca303026c4a4bc19124f1`.
