# New and strengthened evidence — PofBC historical subsidiaries

**Research date:** 2026-11-22. The source IDs used below are resolved in `data/source_register.csv` and `data/source_register.json`.

## A. Swan Valley Foods: two ownership changes and a corporate legal-history sequence

- **1977-03-31 (historical comparison):** The provincial Public Accounts presented a **40% provincial interest** in Swan Valley Foods. The Court of Appeal separately describes the government owning *over 40% at one point*. These are statements at different times; do not force a single static ownership percentage. `[SRC01; SRC05]`
- **1977-04-15:** A distinct entity, **Creston Valley Foods Ltd.**, acquired Swan Valley's Creston plant, equipment, buildings and technology for a **$1.5m debenture**. The Court of Appeal also describes a buyer-side corporate relationship involving Hardee Farms International and Federal Diversiplex Ltd. This was an **asset transaction**, not the incorporation of Swan Valley or its rename. `[SRC05]`
- **1977-12-01:** The purchaser's 1977 annual report, **Standard Brands Limited, financial statement Note 6**, gives the exact transaction date and says it acquired **100% of Swan Valley's outstanding shares and certain debentures** from the B.C. government for **$2.2m**. This is much stronger timing evidence than the 1977/78 Public Accounts reporting period alone. `[SRC03]`
- **1977/78 Public Accounts B8:** Provincial accounts independently list the **$8,307,751** book value of the shareholding sold, a **$2.0m** promissory note, and cash subject to claim settlement. Also records extra shares acquired during FY1977/78, which helps explain why one earlier schedule lists 40% but the buyer later reports acquisition of 100%. `[SRC01]`
- **1978-01-06:** **Swan Valley Foods Ltd.**, federal corporation No. **026524-1**, continued from BC to the CBCA. This is a **continuance**, not a new company incorporation or dissolution. `[SRC04]`
- **1978-04-28:** The federal register records Swan Valley Foods was **amalgamated** into a resulting corporation shown under the later registered name **Nabisco Brands Canada Ltd.** The *name immediately on amalgamation* should be independently checked through the resulting corporation's historical name table. `[SRC04; SRC18]`

**Atlas decision:** Swan Valley should have a separately identified provincial stake and dated exit. Creston Valley should be recorded only as a private counterparty / asset buyer, unless the application visualizes broader corporate transactions.

## B. T.S. Holdings: transit subsidiary family is larger than the current graph

- **1975:** Statistics Canada says B.C. acquired bus transportation companies through **T.S. Holdings Limited** and that this company held shares in firms operating scheduled bus routes, sightseeing/charter service and regional transit. 1976 federal roster prints **1975** as its establishment year (year precision only). `[SRC06; SRC19]`
- **1977-01-25:** BC Hansard confirms that a report administering the *Transit Services Act* and an auditor's report concerning **T.S. Holdings Ltd. and subsidiary companies** was tabled. This is a high-value document-retrieval lead for the missing subsidiary names. `[SRC08]`
- **Government-enterprise list:** Statistics Canada explicitly lists **Vancouver Island Transit Ltd. (subsidiary consolidated)**, but its parent is not shown in that exact roster passage. `[SRC07]`
- **1980-03-31:** Public Accounts B4 records **one government-owned common share of T.S. Holdings**, and separately **two shares of Pacific Coach Lines Ltd.** Do not present Pacific Coach as an operating subsidiary based solely on both being provincial holdings. `[SRC02]`
- **1980-03-31:** **Thompson-Okanagan Transit Ltd.** has a **$50,000 provincial advance**. This demonstrates a funding relationship, not ownership. `[SRC02]`
- **1978/79 Auditor General** says T.S. Holdings had a material receivable from Pacific Coach Lines and operating losses. A debtor-creditor relationship is not parentage. `[SRC09]`

**Atlas decision:** Create a candidate T.S. Holdings legal node; hold edges to Vancouver Island Transit, Pacific Coach and Thompson-Okanagan until corporate statements or registry records establish share ownership.

## C. Direct provincial holdings and subsidiary wind-ups

- **Crown Development Corporation:** 1977/78 Public Accounts B8 records the corporation was **wound up** with a **$1,000 share write-off**. **By 1978-03-31** is supportable; the exact dissolution day is not. `[SRC01]`
- **I.O.K. Poultry Ltd.:** 1979/80 Public Accounts B4 shows prior 100%-owned 600-share holding no longer carried as of 1980; B8 explicitly calls the $600 credit **proceeds on dissolution**. This strengthens the prior research record with a dissolution event occurring by **1980-03-31**; don't invent the registry dissolution day. `[SRC02]`
- **Surrey Farm Products Investments Ltd., formerly Panco Poultry:** 1979/80 B4 shows the legal company still had **$1** recorded in provincial equity after $4,799,999 had been returned on sale of operating assets. **Do not** equate an operating-asset sale with company disappearance. `[SRC02]`

## D. Equity investees that are **not** proven subsidiaries

The 1979/80 Public Accounts B5 lists these as *Investments, Other*, not under the direct Crown corporations share schedule:

| Company | Evidence at 1979/80 checkpoint | Required atlas handling |
|---|---|---|
| Chef Ready Foods Ltd. | **33.33%** in 10,000 common shares; **$85,000 doubtful-recovery provision** recorded FY1980 | Minority investment; zero book value does **not** establish divestiture |
| Kootenay Dehydrators Ltd. | **35.9%** for 2,000 Class A common shares, plus the **entire issue of 98,000 Class B common shares**; earlier 1977/78 schedule says 33.33% | Multi-class equity; don't infer effective voting control; investigate discrepancy |
| South Peace Dehy-Products Ltd. | **27.7%** for 277 nonvoting common and 277 voting preferred; **$554 provision** | Minority investment; no evidence shares were sold or entity dissolved |

Source: `[SRC01; SRC02]`. Page locator: 1979/80 Public Accounts **printed B5** (PDF index 172).

## E. Housing Corporation: new end-of-ownership lead

Statistics Canada (1978 report, printed p.26) says the Housing Corporation of British Columbia had been directed to wind up operations and that its real-estate sales subsidiary **Venture Realty** was sold during the reporting year. The 1974 Dunhill consolidated list uses **Ventures Realty Ltd.** (plural). These **must not** be normalized into one legal entity unless a matching incorporation number or contemporaneous corporate record confirms identity. `[SRC10; SRC20]`

The dual-Dunhill identity remains unchanged: parent **No.73385** renamed Housing Corporation on **1976-11-18** and dissolved **1990-06-18**; subsidiary **No.91003**, formerly W.K.P., adopted Dunhill on **1976-11-26** and dissolved **1989-06-12**. The **1976-11-09 OIC** is a name-resolution authorization, not the name-change effective date. `[SRC12; SRC13; SRC14; SRC15; SRC16]`

## F. Limitations and provenance

The new eight corporate candidates were checked against exact names in the current `src/government/historyData.js`; absence as a name string was observed, but it does not prove zero mentions in notes, branches or other databases. Some company names already appear in the November 14 audit and elsewhere in the repository. The research is not equivalent to a verified official master registry. Sources link to primary PDFs, registries and company statements, with publication/report year distinguished from transaction date.
