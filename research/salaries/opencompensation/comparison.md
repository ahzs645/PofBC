# OpenCompensation comparison

Observed 2026-11-04T20:33:23Z. Status: **filtered-directory-compared-periods-unverified**.

The [published employer directory](https://www.opencompensation.org/british-columbia/employer) contains **158 published names** selected by its minimum of 15 positive compensation records and latest period per name. **158 names map to 119 PofBC employer IDs**; 0 are unmatched and 0 are ambiguous. Employer IDs are the repository's identities, not an independent legal-entity census.

The comparison reconciles **1,445,458 PofBC disclosure observations**, including **1,217,094 official-source observations** and **228,364 compiled observations**, across **276 employers** and **1240 populated employer/periods**. These totals span different years and scopes from the external table and are not subtracted.

The saved site coverage statement reports **171,863 B.C. salary records** under **2023-2024**. Its national record total also includes other provinces and physician-payment datasets. The B.C. latest snapshot does not imply continuous annual coverage.

## What the arithmetic comparison establishes

For **154 of 158 entries**, the record count, rounded mean and rounded maximum can be reproduced from PofBC's immutable historical compilation. **152** reproduce those three values only after reported expenses are added to remuneration. This is evidence of aggregate similarity and a measure-definition problem; it does **not** prove row-level equality or common provenance.

For **5** of those entries, reproduction also requires selecting positive-remuneration rows before adding expenses. Expense-only rows change the denominator under the other diagnostic. These are tested arithmetic interpretations, not verified site-wide selection rules.

The immutable compilation contains retained original input, including data later replaced or held. Its period labels remain unverified. A matching signature never restores those historical rows or elevates them to official evidence.

## Examples requiring source and period review

| Published name | External label | External records | Candidate PofBC source counts | Historical compilation diagnostic |
| --- | --- | ---: | --- | --- |
| [Provincial government](https://www.opencompensation.org/british-columbia/employer/provincial-government) | 2023-2024 | 20,515 | 2023/24: 938 appointee-remuneration (official) + 48 deputy-minister-remuneration (official) + 20373 employee-remuneration (official) | No matching compilation signature |
| [B.C. Hydro](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 6,066 | 2023/24: 6405 employee-remuneration (official) | Remuneration + expenses reproduces the three aggregates |
| [Northern Health](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 3,285 | 2023/24: 10 board-remuneration (official) + 3645 employee-remuneration (official) | Remuneration + expenses reproduces the three aggregates |
| [Vancouver Police](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 1,672 | 2023: 13 executive-only (official); 2023/24: 1672 compiled-unverified; 2024: 13 executive-only (official) | Remuneration + expenses reproduces the three aggregates |
| [B.C. Financial Services Authority](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 257 | 2023/24: 257 employee-remuneration (official) + 257 compiled-unverified | Remuneration + expenses reproduces the three aggregates |
| [B.C. Infrastructure Benefits](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 805 | 2023/24: 805 employee-remuneration (official) + 805 compiled-unverified | Remuneration + expenses reproduces the three aggregates |

Candidate counts preserve official employee, board, appointee and compiled scopes separately. An official schedule plus a retained compiled copy can represent overlapping evidence. A directory label alone cannot establish that either corresponds to the external rows. The JSON contains each original source URL, actual dates, threshold rule, source warnings and monetary diagnostics.

## All observed directory entries

| Published employer name | External period label | External positive records | PofBC employer ID | Compilation aggregate match |
| --- | --- | ---: | --- | --- |
| [Provincial government](https://www.opencompensation.org/british-columbia/employer/provincial-government) | 2023-2024 | 20,515 | public-service | No matching compilation signature |
| [Fraser Health](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 14,908 | fraser-health | Remuneration + expenses reproduces the three aggregates |
| [Provincial Health Services Authority (PHSA)](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 11,908 | provincial-health-services-authority | Remuneration + expenses reproduces the three aggregates |
| [Vancouver Coastal Health](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 11,260 | vancouver-coastal-health | Remuneration + expenses reproduces the three aggregates |
| [Island Health](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 10,400 | island-health | Remuneration + expenses reproduces the three aggregates |
| [Interior Health](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 8,896 | interior-health | Remuneration + expenses reproduces the three aggregates |
| [University of B.C. (UBC)](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 7,861 | university-of-bc | Remuneration + expenses reproduces the three aggregates |
| [B.C. Hydro](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 6,066 | bc-hydro | Remuneration + expenses reproduces the three aggregates |
| [TransLink](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 5,184 | translink | Remuneration + expenses reproduces the three aggregates |
| [Surrey school district](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 4,534 | surrey-school-district | Remuneration + expenses reproduces the three aggregates |
| [City of Vancouver](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 4,094 | city-of-vancouver | Remuneration + expenses reproduces the three aggregates |
| [Providence Health Care](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 3,289 | providence-health-care | Remuneration + expenses reproduces the three aggregates |
| [Northern Health](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 3,285 | northern-health | Remuneration + expenses reproduces the three aggregates |
| [Vancouver school district](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 3,187 | vancouver-school-district | Remuneration + expenses reproduces the three aggregates |
| [ICBC](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 3,133 | icbc | Remuneration + expenses reproduces the three aggregates |
| [Simon Fraser University (SFU)](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 2,831 | simon-fraser-university | Remuneration + expenses reproduces the three aggregates |
| [Worksafe B.C.](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 2,768 | workers-compensation-board | Remuneration + expenses reproduces the three aggregates |
| [B.C. Ferries](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 2,111 | bc-ferries | Both measures reproduce the three aggregates |
| [University of Victoria](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 2,072 | university-of-victoria | Remuneration + expenses reproduces the three aggregates |
| [Coquitlam school district](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 2,054 | coquitlam-school-district | Remuneration + expenses reproduces the three aggregates |
| [Vancouver Police](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 1,672 | vancouver-police | Remuneration + expenses reproduces the three aggregates |
| [Metro Vancouver](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 1,639 | metro-vancouver | Remuneration + expenses reproduces the three aggregates |
| [Burnaby school district](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 1,449 | burnaby-school-district | Remuneration + expenses reproduces the three aggregates |
| [Langley school district](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 1,439 | langley-school-district | Remuneration + expenses reproduces the three aggregates |
| [BCIT](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 1,435 | bcit | Remuneration + expenses reproduces the three aggregates |
| [Richmond school district](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 1,428 | richmond-school-district | Remuneration + expenses reproduces the three aggregates |
| [City of Burnaby](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 1,417 | city-of-burnaby | Remuneration + expenses reproduces the three aggregates |
| [City of Surrey](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 1,384 | city-of-surrey | Remuneration + expenses reproduces the three aggregates |
| [City of Richmond](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 1,080 | city-of-richmond | Remuneration + expenses reproduces the three aggregates |
| [Ridge-Meadows school district](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 1,030 | maple-ridge-pitt-meadows-school-district | Remuneration + expenses reproduces the three aggregates |
| [Delta school district](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 1,013 | delta-school-district | Remuneration + expenses reproduces the three aggregates |
| [Abbotsford school district](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 992 | abbotsford-school-district | Remuneration + expenses reproduces the three aggregates |
| [B.C. Lottery Corporation](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 970 | bclc | Remuneration + expenses reproduces the three aggregates |
| [North Vancouver school district](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 929 | north-vancouver-school-district | Remuneration + expenses reproduces the three aggregates |
| [Kwantlen Polytechnic University](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 914 | kwantlen-polytechnic-university | Remuneration + expenses reproduces the three aggregates |
| [Chilliwack school district](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 910 | chilliwack-school-district | Remuneration + expenses reproduces the three aggregates |
| [B.C. Transit](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 909 | bc-transit | Remuneration + expenses reproduces the three aggregates |
| [Langara College](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 891 | langara-college | Remuneration + expenses reproduces the three aggregates |
| [B.C. Infrastructure Benefits](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 805 | bc-infrastructure-benefits | Remuneration + expenses reproduces the three aggregates |
| [Thompson Rivers University](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 795 | thompson-rivers-university | Remuneration + expenses reproduces the three aggregates |
| [Douglas College](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 678 | douglas-college | Remuneration + expenses reproduces the three aggregates |
| [University of the Fraser Valley](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 673 | university-of-the-fraser-valley | Remuneration + expenses reproduces the three aggregates |
| [City of Coquitlam](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 670 | city-of-coquitlam | Remuneration + expenses reproduces the three aggregates |
| [Vancouver Island University](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 667 | vancouver-island-university | Remuneration + expenses reproduces the three aggregates |
| [B.C. Liquor Distribution Branch](https://www.opencompensation.org/british-columbia/employer/b-c-liquor-distribution-branch) | 2023-2024 | 666 | liquor-distribution-branch | Remuneration + expenses reproduces the three aggregates |
| [City of Delta](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 575 | city-of-delta | Remuneration + expenses reproduces the three aggregates |
| [Vancouver Community College (VCC)](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 540 | vancouver-community-college | Remuneration + expenses reproduces the three aggregates |
| [District of Saanich](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 537 | district-of-saanich | Remuneration + expenses reproduces the three aggregates |
| [Okanagan College](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 536 | okanagan-college | Remuneration + expenses reproduces the three aggregates |
| [District of North Vancouver](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 535 | district-of-north-vancouver | Remuneration + expenses reproduces the three aggregates |
| [Camosun College](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 515 | camosun-college | Remuneration + expenses reproduces the three aggregates |
| [B.C. Housing](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 490 | bc-housing | Remuneration + expenses reproduces the three aggregates |
| [Langley Township](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 487 | langley-township | Remuneration + expenses reproduces the three aggregates |
| [District of West Vancouver](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 486 | district-of-west-vancouver | Remuneration + expenses reproduces the three aggregates |
| [City of Victoria](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 471 | city-of-victoria | Remuneration + expenses reproduces the three aggregates |
| [New Westminster school district](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 463 | new-westminster-school-district | Remuneration + expenses reproduces the three aggregates |
| [Community Living B.C.](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 453 | community-living-bc | Remuneration + expenses reproduces the three aggregates |
| [Capilano University](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 436 | capilano-university | Remuneration + expenses reproduces the three aggregates |
| [Mission school district](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 423 | mission-school-district | Remuneration + expenses reproduces the three aggregates |
| [University of Northern B.C.](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 420 | university-of-northern-bc | Remuneration + expenses reproduces the three aggregates |
| [B.C. Assessment](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 394 | bc-assessment | Remuneration + expenses reproduces the three aggregates |
| [West Vancouver school district](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 389 | west-vancouver-school-district | Remuneration + expenses reproduces the three aggregates |
| [Technical Safety B.C.](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 359 | technical-safety-bc | Remuneration + expenses reproduces the three aggregates |
| [Surrey Police (SPS)](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 348 | surrey-police | Remuneration + expenses reproduces the three aggregates |
| [City of North Vancouver](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 337 | city-of-north-vancouver | Remuneration + expenses reproduces the three aggregates |
| [City of New Westminster](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 331 | city-of-new-westminster | Remuneration + expenses reproduces the three aggregates |
| [College of New Caledonia](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 312 | college-of-new-caledonia | Remuneration + expenses reproduces the three aggregates |
| [Abbotsford Police](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 268 | abbotsford-police | Remuneration + expenses reproduces the three aggregates |
| [City of Maple Ridge](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 267 | city-of-maple-ridge | Remuneration + expenses reproduces the three aggregates |
| [B.C. Financial Services Authority](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 257 | bc-financial-services-authority | Remuneration + expenses reproduces the three aggregates |
| [Selkirk College](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 254 | selkirk-college | Remuneration + expenses reproduces the three aggregates |
| [B.C. Energy Regulator](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 249 | bc-energy-regulator | Remuneration + expenses reproduces the three aggregates |
| [Delta Police](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 234 | delta-police | Remuneration + expenses reproduces the three aggregates |
| [Transit Police](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 233 | transit-police | Remuneration + expenses reproduces the three aggregates |
| [Victoria Police](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 232 | victoria-police | Remuneration + expenses reproduces the three aggregates |
| [City of Port Coquitlam](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 226 | city-of-port-coquitlam | Remuneration + expenses reproduces the three aggregates |
| [Saanich Police](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 194 | saanich-police | Remuneration + expenses reproduces the three aggregates |
| [Powerex](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 184 | sub-powerex | Remuneration + expenses reproduces the three aggregates |
| [North Island College](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 181 | north-island-college | Remuneration + expenses reproduces the three aggregates |
| [PowerTech](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 175 | sub-powertech-labs | Remuneration + expenses reproduces the three aggregates |
| [Emily Carr University](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 170 | emily-carr-university | Remuneration + expenses reproduces the three aggregates |
| [City of Port Moody](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 165 | city-of-port-moody | Remuneration + expenses reproduces the three aggregates |
| [Transportation Investment Corporation](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 160 | transportation-investment-corporation | Remuneration + expenses reproduces the three aggregates |
| [College of the Rockies](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 154 | college-of-the-rockies | Remuneration + expenses reproduces the three aggregates |
| [Justice Institute of B.C.](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 152 | justice-institute-of-bc | Remuneration + expenses reproduces the three aggregates |
| [B.C. Pavilion Corporation](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 137 | bc-pavilion-corporation | Remuneration + expenses reproduces the three aggregates |
| [Northern Lights College](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 126 | northern-lights-college | Remuneration + expenses reproduces the three aggregates |
| [Coast Mountain College](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 124 | coast-mountain-college | Remuneration + expenses reproduces the three aggregates |
| [Skilled Trades B.C.](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 98 | skilledtradesbc | Remuneration + expenses reproduces the three aggregates |
| [B.C. Securities Commission](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 89 | bc-securities-commission | Remuneration + expenses reproduces the three aggregates |
| [District of Oak Bay](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 89 | district-of-oak-bay | Remuneration + expenses reproduces the three aggregates |
| [City of White Rock](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 82 | city-of-white-rock | Remuneration + expenses reproduces the three aggregates |
| [Langley City](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 79 | city-of-langley | Remuneration + expenses reproduces the three aggregates |
| [City of Pitt Meadows](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 76 | city-of-pitt-meadows | Remuneration + expenses reproduces the three aggregates |
| [Destination B.C.](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 68 | destination-bc | Remuneration + expenses reproduces the three aggregates |
| [Legal Aid B.C.](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 68 | legal-aid-bc | Remuneration + expenses reproduces the three aggregates |
| [Columbia Basin Trust](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 62 | columbia-basin-trust | Remuneration + expenses reproduces the three aggregates |
| [Port Moody Police](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 59 | port-moody-police | Remuneration + expenses reproduces the three aggregates |
| [Infrastructure B.C.](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 42 | infrastructure-bc | Remuneration + expenses reproduces the three aggregates |
| [Royal B.C. Museum](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 33 | royal-bc-museum | Remuneration + expenses reproduces the three aggregates |
| [Central Saanich Police](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 29 | central-saanich-police | Remuneration + expenses reproduces the three aggregates |
| [First Peoples' Cultural Council](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 28 | first-peoples-cultural-council | Remuneration + expenses reproduces the three aggregates |
| [Forestry Innovation Investment](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 28 | forestry-innovation-investment | Remuneration + expenses reproduces the three aggregates |
| [Knowledge Network](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 28 | knowledge-network | Remuneration + expenses reproduces the three aggregates |
| [Oak Bay Police](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 23 | oak-bay-police | Remuneration + expenses reproduces the three aggregates |
| [Bowen Island](https://www.opencompensation.org/british-columbia/employer) | 2023-2024 | 22 | bowen-island | Remuneration + expenses reproduces the three aggregates |
| [Vancouver Island Health](https://www.opencompensation.org/british-columbia/employer) | 2020-2021 | 7,280 | island-health | Remuneration + expenses reproduces the three aggregates |
| [University of British Columbia (UBC)](https://www.opencompensation.org/british-columbia/employer) | 2020-2021 | 6,955 | university-of-bc | Remuneration + expenses reproduces the three aggregates |
| [Vancouver police (VPD)](https://www.opencompensation.org/british-columbia/employer) | 2020-2021 | 1,604 | vancouver-police | Remuneration + expenses reproduces the three aggregates |
| [Maple Ridge/Pitt Meadows school district](https://www.opencompensation.org/british-columbia/employer) | 2020-2021 | 755 | maple-ridge-pitt-meadows-school-district | Remuneration + expenses reproduces the three aggregates |
| [B.C. Lottery Corporation (BCLC)](https://www.opencompensation.org/british-columbia/employer) | 2020-2021 | 657 | bclc | Remuneration + expenses reproduces the three aggregates |
| [District of Delta](https://www.opencompensation.org/british-columbia/employer) | 2020-2021 | 462 | city-of-delta | Remuneration + expenses reproduces the three aggregates |
| [City of Abbotsford](https://www.opencompensation.org/british-columbia/employer) | 2020-2021 | 351 | city-of-abbotsford | Remuneration + expenses reproduces the three aggregates |
| [New Westminster school board](https://www.opencompensation.org/british-columbia/employer) | 2020-2021 | 328 | new-westminster-school-district | Remuneration + expenses reproduces the three aggregates |
| [Liquor Distribution Branch](https://www.opencompensation.org/british-columbia/employer) | 2020-2021 | 321 | liquor-distribution-branch | Remuneration + expenses reproduces the three aggregates |
| [Royal Roads University](https://www.opencompensation.org/british-columbia/employer) | 2020-2021 | 223 | royal-roads-university | Remuneration + expenses reproduces the three aggregates |
| [B.C. Oil and Gas Commission](https://www.opencompensation.org/british-columbia/employer) | 2020-2021 | 207 | oil-and-gas-commission | Remuneration + expenses reproduces the three aggregates |
| [B.C. Pension Corp.](https://www.opencompensation.org/british-columbia/employer) | 2020-2021 | 182 | bc-pension-corporation | Remuneration + expenses reproduces the three aggregates |
| [City of Chilliwack](https://www.opencompensation.org/british-columbia/employer) | 2020-2021 | 166 | city-of-chilliwack | Remuneration + expenses reproduces the three aggregates |
| [New West Police](https://www.opencompensation.org/british-columbia/employer) | 2020-2021 | 130 | new-west-police | Remuneration + expenses reproduces the three aggregates |
| [Powerex Corporation](https://www.opencompensation.org/british-columbia/employer) | 2020-2021 | 127 | sub-powerex | No matching compilation signature |
| [Emily Carr](https://www.opencompensation.org/british-columbia/employer) | 2020-2021 | 120 | emily-carr-university | Remuneration + expenses reproduces the three aggregates |
| [City of Mission](https://www.opencompensation.org/british-columbia/employer) | 2020-2021 | 108 | city-of-mission | Remuneration + expenses reproduces the three aggregates |
| [Powertech Labs. Inc.](https://www.opencompensation.org/british-columbia/employer) | 2020-2021 | 106 | sub-powertech-labs | No matching compilation signature |
| [City of Langley](https://www.opencompensation.org/british-columbia/employer) | 2020-2021 | 70 | city-of-langley | Remuneration + expenses reproduces the three aggregates |
| [Legal Services Society](https://www.opencompensation.org/british-columbia/employer) | 2020-2021 | 63 | legal-aid-bc | Remuneration + expenses reproduces the three aggregates |
| [Industry Training Authority of B.C.](https://www.opencompensation.org/british-columbia/employer/industry-training-authority-of-b-c) | 2020-2021 | 60 | industry-training-authority | Remuneration + expenses reproduces the three aggregates |
| [University of British Columbia](https://www.opencompensation.org/british-columbia/employer) | 2017-2018 | 5,130 | university-of-bc | Positive remuneration rows + expenses reproduce the three aggregates |
| [PHSA](https://www.opencompensation.org/british-columbia/employer) | 2017-2018 | 5,072 | provincial-health-services-authority | Remuneration + expenses reproduces the three aggregates |
| [BC Hydro and Power Authority](https://www.opencompensation.org/british-columbia/employer) | 2017-2018 | 4,892 | bc-hydro | No matching compilation signature |
| [Surrey School Board](https://www.opencompensation.org/british-columbia/employer) | 2017-2018 | 2,628 | surrey-school-district | Remuneration + expenses reproduces the three aggregates |
| [Vancouver School Board](https://www.opencompensation.org/british-columbia/employer) | 2017-2018 | 2,312 | vancouver-school-district | Remuneration + expenses reproduces the three aggregates |
| [Providence Health](https://www.opencompensation.org/british-columbia/employer) | 2017-2018 | 1,705 | providence-health-care | Positive remuneration rows + expenses reproduce the three aggregates |
| [Simon Fraser University](https://www.opencompensation.org/british-columbia/employer) | 2017-2018 | 1,617 | simon-fraser-university | Remuneration + expenses reproduces the three aggregates |
| [Burnaby School Board](https://www.opencompensation.org/british-columbia/employer) | 2017-2018 | 1,038 | burnaby-school-district | Remuneration + expenses reproduces the three aggregates |
| [Richmond School Board](https://www.opencompensation.org/british-columbia/employer/richmond-school-board) | 2017-2018 | 889 | richmond-school-district | Remuneration + expenses reproduces the three aggregates |
| [Coquitlam School Board](https://www.opencompensation.org/british-columbia/employer) | 2017-2018 | 887 | coquitlam-school-district | Remuneration + expenses reproduces the three aggregates |
| [Abbotsford School Board](https://www.opencompensation.org/british-columbia/employer) | 2017-2018 | 767 | abbotsford-school-district | Remuneration + expenses reproduces the three aggregates |
| [Langley School Board](https://www.opencompensation.org/british-columbia/employer) | 2017-2018 | 723 | langley-school-district | Remuneration + expenses reproduces the three aggregates |
| [Maple Ridge/Pitt Meadows School Board](https://www.opencompensation.org/british-columbia/employer) | 2017-2018 | 635 | maple-ridge-pitt-meadows-school-district | Remuneration + expenses reproduces the three aggregates |
| [North Vancouver School Board](https://www.opencompensation.org/british-columbia/employer) | 2017-2018 | 610 | north-vancouver-school-district | Remuneration + expenses reproduces the three aggregates |
| [Chilliwack School Board](https://www.opencompensation.org/british-columbia/employer) | 2017-2018 | 538 | chilliwack-school-district | Remuneration + expenses reproduces the three aggregates |
| [Oakanagan College](https://www.opencompensation.org/british-columbia/employer) | 2017-2018 | 387 | okanagan-college | Positive remuneration rows + expenses reproduce the three aggregates |
| [Township of Langley](https://www.opencompensation.org/british-columbia/employer) | 2017-2018 | 364 | langley-township | Remuneration + expenses reproduces the three aggregates |
| [B.C. Investment Management Corporation](https://www.opencompensation.org/british-columbia/employer) | 2017-2018 | 363 | bc-investment-management-corporation | Remuneration + expenses reproduces the three aggregates |
| [Vancouver Community College](https://www.opencompensation.org/british-columbia/employer) | 2017-2018 | 361 | vancouver-community-college | Positive remuneration rows + expenses reproduce the three aggregates |
| [City of Kamloops](https://www.opencompensation.org/british-columbia/employer) | 2017-2018 | 340 | city-of-kamloops | Remuneration + expenses reproduces the three aggregates |
| [West Vancouver School Board](https://www.opencompensation.org/british-columbia/employer) | 2017-2018 | 282 | west-vancouver-school-district | Remuneration + expenses reproduces the three aggregates |
| [Mission School Board](https://www.opencompensation.org/british-columbia/employer/mission-school-board) | 2017-2018 | 263 | mission-school-district | Remuneration + expenses reproduces the three aggregates |
| [University of Northern British Columbia](https://www.opencompensation.org/british-columbia/employer) | 2017-2018 | 258 | university-of-northern-bc | Remuneration + expenses reproduces the three aggregates |
| [Metro Vancouver Transit Police](https://www.opencompensation.org/british-columbia/employer) | 2017-2018 | 182 | metro-vancouver-transit-police | Remuneration + expenses reproduces the three aggregates |
| [Justice Institute of British Columbia](https://www.opencompensation.org/british-columbia/employer/justice-institute-of-british-columbia) | 2017-2018 | 111 | justice-institute-of-bc | Remuneration + expenses reproduces the three aggregates |
| [District of Mission](https://www.opencompensation.org/british-columbia/employer) | 2017-2018 | 99 | city-of-mission | Remuneration + expenses reproduces the three aggregates |
| [EmilyCarr](https://www.opencompensation.org/british-columbia/employer) | 2017-2018 | 93 | emily-carr-university | Positive remuneration rows + expenses reproduce the three aggregates |
| [Delta School Board](https://www.opencompensation.org/british-columbia/employer) | 2017-2018 | 78 | delta-school-district | Remuneration + expenses reproduces the three aggregates |
| [City of Nelson](https://www.opencompensation.org/british-columbia/employer) | 2017-2018 | 51 | city-of-nelson | Remuneration + expenses reproduces the three aggregates |
| [Forestry Innovation Investsment](https://www.opencompensation.org/british-columbia/employer) | 2017-2018 | 26 | forestry-innovation-investment | Remuneration + expenses reproduces the three aggregates |
| [Nelson Police](https://www.opencompensation.org/british-columbia/employer) | 2017-2018 | 24 | nelson-police | Positive remuneration rows + expenses reproduce the three aggregates |

## Interpretation and follow-up

- The full captured table is a filtered directory: at least 15 positive compensation records in the latest period for each published employer name. It is not the complete employer roster, annual history or workforce.
- Published names can be historical aliases. Mapping to repository employer IDs does not independently establish legal-entity equivalence.
- Hyphenated edition labels are normalized only to find candidate reports. Calendar years, fiscal dates and compilation labels are not interchangeable.
- Source cohorts remain separate. Official schedules and retained compiled copies can overlap; their combined row count is not an employee count.
- Compensation averages and maxima are tested against remuneration and remuneration plus known expenses. A matching count and rounded mean/maximum is an aggregate arithmetic signature, not row equality or independent validation.
- A separate diagnostic selects positive-remuneration rows before adding known expenses. This can differ from selecting all rows with a positive combined amount; source selection rules are not inferred from a matching signature.
- Missing expense cells remain unknown, even when known numeric expenses reproduce a displayed aggregate.
- The immutable compilation is historical evidence only. Previously rejected, replaced or misdated records are not restored.
- No salary records are imported, removed, relabelled or merged by this comparison.

For a discrepancy, obtain the exact originating employer report, verify its reporting dates and compensation definition, then reconcile individual rows and source controls. The existing source queue remains the route for accepting salary additions. A count difference, matching name or matching mean is insufficient.

The separate [PSA-2024-42006 workforce companion](../workforce/README.md) adds the all-employee and Victoria-office aggregate series. It is excluded from employee-record totals and from the Public Accounts FTE series.

## Reproduce

```sh
npm run audit:opencompensation
npm run check:opencompensation
```

[Detailed comparison](comparison.json) · [Directory comparison CSV](comparison.csv) · [Observed input](observed-snapshot.json) · [Methods and source findings](README.md)

Repository salary input SHA-256: `b40f0060e51af0e11506291ab1db5eebf6b0fc2f9bb797af218e2593d17ecd4f`.
Saved directory input SHA-256: `3c3a0fb9ef04e42aa58d4ea5f5d20084dc92fbdc6fe3162fc9eb336d6dec7f24`.
