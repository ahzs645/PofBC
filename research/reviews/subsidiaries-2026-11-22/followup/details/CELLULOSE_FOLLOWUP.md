# Cellulose follow-up: legal endpoint, identities and ownership

Research date: 22 November 2026. This is a research addendum, not a repository patch. Page numbers below distinguish printed pages from one-based PDF pages.

## Findings ready to apply

1. **British Columbia Cellulose Company: use 31 March 1986 as the legal endpoint.** The original **OIC 631/1986**, approved **19 March 1986**, expressly brings the Repeal Act into force effective **31 March 1986**. The official consolidation identifies **B.C. Reg. 49/86**; section 2 dissolves the company upon repeal. Keep the Accounts' separately printed 1 April assertion. [CELL-S08–S11]
2. **Kootenay Forest Products Ltd.: add a wholly owned subsidiary from 1 March 1974.** That is the effective purchase of all its shares by BC Cellulose, not its incorporation date. [CELL-S01, F128]
3. **Canadian Cellulose Company, Limited: create a distinct majority-controlled entity record if that category is supported.** BC Cellulose acquired 79% on 29 June 1973. A strict wholly-provincially-owned graph must retain the qualification: the company was not 100% publicly owned during that stage. [CELL-S01, F9]
4. **Use 9 March 1978 for the transfer to BCRIC**, supported by the Finance Minister's subsequent account of the completed transaction, alongside the order and agreement. Record the intervening dividend to the Province separately. [CELL-S02–S04]
5. **Separate the end of public control from the 31 December 1980 amalgamation.** The former belongs to the 1979 share-distribution sequence at year precision; the latter is an exact successor event involving three predecessor corporations. [CELL-S05–S07]

## 1. BC Cellulose: legal date and accounting statement

The original commencement order is now recovered: **OIC 631/1986**, approved **19 March 1986**. Its operative text brings the British Columbia Cellulose Company Repeal Act into force effective **31 March 1986**. The one-page official scan was visually checked. It does not specify 1 April or a time of day. [CELL-S11]

The archived Repeal Act, consolidated on 3 June 1986 and preserved in the 5 December 1994 consolidation, identifies **B.C. Reg. 49/86** and the same effective date. Section 2(1) makes dissolution, termination of directors, and transfer of assets and liabilities consequences of repeal. The original order plus this clause support the recommended legal endpoint of **1986-03-31**. [CELL-S08–S09, CELL-S11]

The 1985/86 Public Accounts say the Act came into force on 31 March but describe dissolution and transfer as effective **1 April 1986**. Preserve that assertion in the evidence record. The source does not explain the one-day difference, and this review does not label it a typographical error or presume an accounting convention. The original order resolves the legal commencement question; the reason for the Accounts' next-day wording remains unexplained. The **23 September 1983 assent** is neither commencement nor dissolution. [CELL-S08, CELL-S10]

## 2. Canadian Cellulose and Kootenay: distinct corporations

| Entity | Public acquisition | Immediate parent / interest | Boundary on the evidence |
|---|---|---|---|
| Canadian Cellulose Company, Limited | 29 June 1973 | BC Cellulose, 79% | Acquisition date, not incorporation; majority ownership |
| Kootenay Forest Products Ltd. | 1 March 1974 | BC Cellulose, 100% | Acquisition date, not incorporation; previously an Eddy Match subsidiary |

These are separate from **British Columbia Cellulose Company**, the Crown holding company. Canadian Cellulose's own note 10 describes the 29 June 1973 combination of certain assets and liabilities of **Columbia Cellulose Company, Limited** with Canadian Cellulose; Columbia then ceased to be a shareholder. This is evidence of a reorganization between separately identified corporations, not a simple Columbia-to-Canadian rename. [CELL-S01, F9 and F94]

Kootenay's own note 1 specifies the share purchase effective **1 March 1974** and a separate purchase of the assets and third-party liabilities of the **Kootenay Forest Products** and **Stafford Mills** divisions of Eddy Match. Do not turn a division label into a duplicate corporate node. The parent statement's 28 February 1974 acquisition-value reference should not override the subsidiary's explicit effective date. [CELL-S01, F7 and F128]

## 3. Preserve the intermediate Province ownership

The 1977/78 Accounts describe securities distributed by BC Cellulose to the Province before their transfer to BCRIC. This stage is real even though the precise dividend date is unresolved. The fiscal-year transaction and the completed 9 March transfer bound the dividend to **1 April 1977–9 March 1978**, inclusive; that is an inferred interval, not a printed date. [CELL-S02–S04]

For Canadian Cellulose the Province combined the BC Cellulose dividend—**9,570,353 common and 39,750 non-voting shares**—with **278,100 common shares held separately as a temporary investment**. The transferred combined interest was reported as **81%**. Consequently, do not change BC Cellulose's earlier 79% holding into 81%. Kootenay's entire holding and BC Cellulose's 225 Plateau shares also passed through the Province. [CELL-S02, B5]

OIC 530/1978 approved the agreement on 9 March 1978. More decisively for completion, Finance Minister Wolfe's budget address on **10 April 1978, printed page 264**, says the Province transferred the holdings on **9 March 1978**: Canadian Cellulose 81%, Kootenay 100%, and Plateau 100%. These are dated observations of the respective interests, not permission to carry a percentage unchanged across all later years. [CELL-S03–S04]

## 4. Public-control endpoint and later amalgamation

The 1978/79 Accounts' subsequent-events note describes the Crown receiving 15 million BCRIC shares on **19 April 1979**, the free-share scheme, and a further 81.2 million treasury shares subscribed by the public. It reports the government interest reduced from 100% to below 5%. BCRIC's audited 1980 report independently places the cash share issue and note conversion in its **calendar-1979 comparative cash-flow column**. Together these support a **1979 year-precision loss of wholly/majority provincial ownership**, with the exact crossing day unresolved. The Province retained **4.65% at 31 March 1980**; this is not a claim that every public financial interest ended. [CELL-S05, p.21; CELL-S06, A9iv; CELL-S07, B5]

BCRIC increased its Canadian Cellulose holding from 81% to 100% **during 1980**. That later full ownership by BCRIC does not turn Canadian Cellulose into a wholly provincially owned company. [CELL-S05, pp.2 and 23]

On **31 December 1980**, Canadian Cellulose, Kootenay and Plateau amalgamated into a **new Canadian Cellulose Company, Limited**. Note 14 gives the exact date and calls the result a new company. Preserve a successor distinction even though the successor reused Canadian Cellulose's name. This is an amalgamation event, not evidence that Kootenay's operations stopped or that the provincial holding company changed its name. [CELL-S05, p.25 / PDF 27]

## Implementation boundaries

- For Kootenay, a wholly owned subsidiary node is supported from the exact 1974 acquisition; its parent sequence must allow the bounded Province interval and the BCRIC transfer.
- For Canadian Cellulose, use a majority-controlled classification. If the graph only admits wholly owned companies, retain its record and evidence outside that category until the schema supports it.
- Keep public-control dates, immediate-parent dates and legal predecessor/successor dates in separate fields. A 1980 legal endpoint does not justify a public-control edge through 1980.
- No original incorporation dates were established for Canadian Cellulose or Kootenay in this pass. Do not use their acquisition dates as incorporation dates.
- The main draft's sections 6–7 passed substantive QA; the only recommended addition was the explicit majority-versus-wholly-owned distinction for Canadian Cellulose.

## Sources

| ID | Primary source and URL | Locator |
|---|---|---|
| CELL-S01 | [BC Public Accounts 1975/76, full volume](https://archive.org/download/publicaccountsof00mini_4/publicaccountsof00mini_4.pdf) | F7–F9 / PDF 393–395; F94 / PDF 480; F128 / PDF 514. F9, F94 and F128 visually checked. |
| CELL-S02 | [Auditor General report for year ended 31 March 1978, reproducing 1977/78 Accounts](https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19780301-report-auditor-general-1978.pdf) | Accounts B5 / PDF 73 and B8 / PDF 76; transmitted 30 March 1979. |
| CELL-S03 | [OIC 530/1978 and sale agreement](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0530_1978) | PDF 1 approval; PDF 3 agreement; PDF 4 shares. |
| CELL-S04 | [Hansard, 10 April 1978, afternoon](https://lims.leg.bc.ca/hdms/file/Debates/31st3rd/31p_03s_780410p.htm) | Finance Minister Wolfe's budget address, p.264, transfer paragraph. |
| CELL-S05 | [BCRIC Annual Report 1980](https://digital.library.mcgill.ca/images/hrcorpreports/pdfs/6/637355.pdf) | p.2 / PDF 4; p.21 / PDF 23; p.23 / PDF 25; p.25 note 14 / PDF 27. PDF 23 and PDF 27 visually checked. |
| CELL-S06 | [Auditor General report for year ended 31 March 1979, reproducing 1978/79 Accounts](https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19790301-report-auditor-general-1979.pdf) | Accounts A9iv, note 7B / PDF 85, visually checked; report transmitted 13 March 1980. |
| CELL-S07 | [Auditor General report 1980, reproducing 1979/80 Accounts](https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19800301-report-auditor-general-1980.pdf) | Accounts B5 / PDF 173, visually checked. |
| CELL-S08 | [British Columbia Cellulose Company Repeal Act, SBC1983 c.2](https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/1157935215) | Sections 1–3, one-page original statute. |
| CELL-S09 | [Official archived consolidation of the Repeal Act](https://www.bclaws.gov.bc.ca/civix/document/id/94consol18/94consol18/83002) | Section 2 and final editorial note: B.C. Reg. 49/86, effective 31 March 1986. Direct official HTML retrieved successfully. |
| CELL-S10 | [Auditor General report 1987, reproducing 1985/86 Accounts](https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19870301-report-auditor-general-1987.pdf) | Accounts A11 / PDF 159, note 5(b); C12 / PDF 194. |
| CELL-S11 | [Original OIC 631/1986, BC Cellulose commencement](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0631_1986) | One-page original order, approved 19 March 1986, effective 31 March 1986; visually checked. |

The companion JSON supplies dates, bounds, source links and proposed graph treatment. Local OCR and page images are working evidence, not independent sources. The McGill catalogue's corporate-history metadata was not used to merge companies or assert name changes.
