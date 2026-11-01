# Sunshine Lists comparison and salary source queue

**Comparison status: incomplete-reference.** Reference captured 2026-11-01T06:11:30.217Z.

The supplied snapshot contains **3 employers** and **0 annual observations**. **It is not a complete Sunshine Lists employer inventory.** 3 employer entries contain summary evidence only.

All **1,010,644 published PofBC observations** across **239 employers** were reconciled against the actual employer files: **777,862 official-source observations** and **232,782 retained compiled observations**. 166 employers have some official records; 73 have compiled records only.

## Observed reference employers

| Sunshine Lists employer | Identity match | Reference summary | PofBC official rows | PofBC compiled rows | Comparison result |
| --- | --- | --- | ---: | ---: | --- |
| [Core Government](https://www.sunshinelists.ca/british-columbia/employers/core-government) | public-service | 179,103 records; 2007-2025 | 242,158 | 0 | summary-only |
| [Fraser Health Authority](https://www.sunshinelists.ca/british-columbia/employers/fraser-health-authority) | fraser-health | 111,202 records; 2014-2025 | 111,206 | 0 | summary-only |
| [Provincial Health Services Authority](https://www.sunshinelists.ca/british-columbia/employers/provincial-health-services-authority) | provincial-health-services-authority | 103,411 records; 2005-2025 | 27 | 24,923 | summary-only |

Reference totals span the source’s own reported years and definitions. The table deliberately does not subtract employer-wide totals: PofBC can include different years and disclosure categories. A range is not an annual series.

## Repository coverage by sector

| Sector | Employers | With official records | Compiled only | Official observations | Compiled observations |
| --- | ---: | ---: | ---: | ---: | ---: |
| Crown corporations | 43 | 12 | 31 | 105,013 | 36,315 |
| Government | 1 | 1 | 0 | 242,158 | 0 |
| Health authorities | 8 | 6 | 2 | 244,148 | 68,658 |
| Municipal police | 13 | 1 | 12 | 142 | 9,232 |
| Municipalities | 116 | 113 | 3 | 118,593 | 28,211 |
| School districts | 34 | 21 | 13 | 21,232 | 45,385 |
| Universities and colleges | 24 | 12 | 12 | 46,576 | 44,981 |

## Processing queue

The [work queue](work-queue.csv) contains **223 existing official-source tasks** and **3 reference-comparison tasks**. Existing leads are linked to their original report or archive and retain the recorded next action. They do not prove that additional records are available or that a report has passed validation.

This queue covers the published source catalog and supplied reference. The broader [six-sector processing and archive queue](../continuation-2026-11-01/work-queue.csv) remains available separately. The queues can overlap and their totals must not be added.

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

Repository input fingerprint: `c38edddbde95a7e6e9b9b13964cb985e899a4b0f7724749f7a75372e77d1a4fc`.
Reference snapshot fingerprint: `5955544e5deef4dcc72fcb201137dd943053ef78deeca303026c4a4bc19124f1`.
