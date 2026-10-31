# Forest Renewal BC and ferry contract: targeted handoff audit

Reviewed commit: `0dbdb18cfebfb27e5529ce5940850e96eb9a995c`. This review made no repository changes.

## Forest Renewal BC: close the statutory end-date question

**Forest Renewal BC was dissolved on 27 June 2002.** The current body record already has that exact date. The reopened “14 or 27 June” item in `research/WANTED.md` is a handoff/status regression, not an unresolved statutory question.

| Date | Meaning | Evidence |
|---|---|---|
| 28 March 2002 | Assent to the Budget Measures Implementation Act, 2002 | R3E-001, assent heading |
| 26 June 2002 | OIC 517 approved and ordered | R3E-128, original stamped order; R3E-002 Gazette recital |
| 27 June 2002 | B.C. Reg. 158/2002 deposited | R3E-002, opening paragraph |
| 27 June 2002 | Repeal and statutory dissolution effective | Act ss 8, 28, 32; OIC operative provisions; deposit rule |
| 2 July 2002 | Gazette issue published | R3E-002 masthead |

The original Act supplies the substantive legal effects. Section 8 repeals the Forest Renewal Act. Section 28 dissolves the corporation and its statutory committees upon repeal, ends the appointments, transfers rights/property/assets to government, and makes government assume the obligations and liabilities. Section 32 defers these provisions to regulation. Original OIC 517 brings sections 7–11 and 28 into force. The regulation was deposited 27 June and specifies no different commencement day. The Regulations Act, RSBC 1996 c. 402, s 4(1), supplies the deposit-date default; the official repeal table independently reports 27 June 2002.

The one-page original order was visually checked. It shows the **26 June** approval stamp. It does **not** supply a competing 14 June dissolution or make approval equivalent to commencement. Deposit is documented by the separate Gazette record. Nothing here determines whether 14 June referred to an operational or administrative milestone; such a claim would require its own evidence and must not replace the statutory end.

### Source chain

- **R3E-001:** [Budget Measures Implementation Act, 2002, SBC 2002 c. 7](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/1944924325), PDF pp. 1, 2, 5; ss 8, 28, 32.
- **R3E-128:** [Original OIC 517/2002](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0517_2002), entire one-page original.
- **R3E-002:** [B.C. Reg. 158/2002, Gazette Part II vol. 45 no. 12](https://www.bclaws.gov.bc.ca/civix/document/id/bcgaz2/bcgaz2/v45n12_158-2002), opening paragraph and operative paragraphs (a), (c).
- Supplemental: [Regulations Act, RSBC 1996 c. 402](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/2015542934), printed/PDF p. 2, ss 3–4. The original was opened through the web tool.
- Supplemental: [official repeal table](https://www.bclaws.gov.bc.ca/civix/document/id/consol45/consol45/tlc96160) and [repeal notice](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/96160rep_01). Search-index text explicitly corroborated 27 June 2002; direct web opens of these two pages failed. The conclusion does not depend on those pages.

### What the repository should do

`research/history/bodies.json` lines 1084–1096 already records `ended: "2002-06-27"`. Keep it. Close the Forest Renewal statutory-end subquestion at `research/WANTED.md` lines 234–237 and reconnect **R3E-C048** to its full source catalogue. Other E11 questions can remain open independently.

## Ferry contract: the original start and term are already recovered

**R3E-C073 already establishes commencement on 1 April 2003 and a 60-year initial term.** Reading the preserved original confirms both: the commencement definition is in s 1.01 (PDF p. 5/printed p. 2) and the term is in s 3.01 (PDF p. 9/printed p. 6). The initial contractual end calculates to **31 March 2063**, subject to the agreement’s provisions. It is a calculated contractual boundary, not a forecast of actual termination.

The original first performance term lasts **five years**, 1 April 2003–31 March 2008. Subsequent performance terms last **four years**. Accordingly:

| Performance term | Start | Last day | Basis |
|---|---|---|---|
| 1 | 1 April 2003 | 31 March 2008 | First Performance Term definition, 5 years |
| 2 | 1 April 2008 | 31 March 2012 | Subsequent 4-year term definition |
| 3 | 1 April 2012 | 31 March 2016 | Same definition |
| 4 | 1 April 2016 | 31 March 2020 | Same definition |
| 5 | 1 April 2020 | 31 March 2024 | Same definition |
| 6 | 1 April 2024 | 31 March 2028 | Same definition; 2024 consolidation and amendment 17 corroborate |

These period endpoints are calculated from the contract’s definitions. They describe performance cycles inside the continuing contract. They are **not renewals of the entire 60-year agreement**. Actual whole-contract renewal provisions are ss 3.02–3.04: discussions begin in 2058, with a 2060 decision/notice mechanism and conditional extension rights. The performance-term documents do not establish that such a renewal has occurred.

### What the 18-instrument ledger does and does not supply

The full handoff preserves the original contract, the 2024 unofficial consolidation, and **18 published amending instruments**. The source catalogue retains their URLs and hashes. The ledger primarily records reference dates, and its `effective_date` fields are all null. This is deliberate restraint: a reference date, execution date and operative effective date may differ. Amendment 1 has separately verified operator/province signature dates of 21 and 22 January 2004 and no invented reference date.

This targeted follow-up inspected two further operative clauses:

| Instrument | Reference date | Express operative date | Locator |
|---|---|---|---|
| Amendment 17 / Performance Term Six Agreement, R3E-164 | 30 June 2023 | 1 April 2024 | PDF p. 7, clause 3.11 |
| Amendment 18 / PT Six Amending Agreement No. 2, R3E-165 | 31 March 2024 | 1 April 2024 | PDF p. 6, clause 3.11 |

Both clauses expressly apply regardless of execution or delivery date. Those two effective dates can now be proposed for the ledger, with locators. This review has not inspected every operative clause of all 18 amendments.

### Ferry sources

- **R3E-146:** [Original Coastal Ferry Services Contract](https://www2.gov.bc.ca/assets/gov/driving-and-transportation/passenger/coastal-ferries/coastal_ferry_services_contract.pdf), original recital; s 1.01; ss 3.01–3.04. Original term page visually reviewed.
- **R3E-147:** [Unofficial consolidated contract effective 1 April 2024](https://www2.gov.bc.ca/assets/gov/driving-and-transportation/passenger/coastal-ferries/unofficial-consolidated-contract-effective-2024-04-01.pdf), cover lists 18 amendments; s 3.01 retains the initial term; this is a convenience consolidation, not a substitute for individual executed amendments.
- **R3E-130:** [Government contract and amendment index](https://www2.gov.bc.ca/gov/content/transportation/passenger-travel/water-travel/coastal-ferry-services-contract).
- **R3E-164:** [Amendment 17](https://www2.gov.bc.ca/assets/gov/driving-and-transportation/passenger/coastal-ferries/cfs_contract_amend_agreement_no-17.pdf), PDF p. 1 and 7.
- **R3E-165:** [Amendment 18](https://www2.gov.bc.ca/assets/gov/driving-and-transportation/passenger/coastal-ferries/cfs_contract_amend_agreement_no-18.pdf), PDF p. 1 and 6.

### What remains open in E4

The supplied handoff leaves these specific matters open:

1. The **executed 2 April 2003 amended memorandum and original share redemption/subscription records**. Audited statements already identify their date and described effect; the corporate originals remain desirable.
2. The **first Commissioner’s personal appointment order and first report**, distinguished from establishment of the statutory office.
3. **Clause-specific commencement for requested route/service/payment changes** not yet checked. The amending documents already exist in the package. Their reference dates should not be imported as universal effective dates.

The original contract’s existence, start, initial duration and performance-term distinction should not remain a blanket missing-contract request. Suggested E4 wording: “Original contract recovered: 1 April 2003 commencement, 60-year initial term, first performance term 5 years then 4-year terms; 18 published amendments catalogued. Open: requested clause-level effective dates, executed 2 April 2003 corporate instruments, and first Commissioner appointment/report.”

## Demonstrated source handoff gap

The current imported `crowns/prior-claims.json` contains **R3E-C048** and **R3E-C073**, and the imported amendment ledger contains 18 rows. However, current `crowns/sources.json` has only 48 Round 4 records and contains neither **R3E-128** nor **R3E-146**. Their original URLs/checksums exist in the full consolidated catalogue and preserved Round 3 sources.

That mismatch can make a settled subquestion appear undocumented when the claim actually lost access to its source record. Restore/map the carried source catalogue before regenerating WANTED. Keep completion status at subquestion level: E4 and E11 need not be entirely closed to stop requesting their already settled parts.

The accompanying JSON retains the original claim objects, source URLs and verified file checksums, the received 18-row ledger, the two newly checked effective clauses, and exact repository locations. This report is an audit handback; it does not automatically import anything.
