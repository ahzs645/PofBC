# Pacific Coach Lines: original-source verification

**Reviewed 22 November 2026; question 4.**

The original BC Hydro 1978/79 annual report confirms **1 April 1979 as the start of operations**. Printed p. 10 (PDF p. 12) records the replacement plan announced on 5 September 1978 and the start of the new service. It does not establish incorporation or public-acquisition dates. The report describes Vancouver Island Coach Lines as provincially owned and operated; this wording does not make it identical to Vancouver Island Transit or Vancouver Island Transportation.

The 1984/85 Public Accounts confirm that operations ceased **31 March 1984**, with winding up still in progress. The later 1985/86 accounts describe disposal of remaining real estate. Keep operations ceased, winding up and legal dissolution as different event types.

## Integration

- Retain 1 April 1979 with the event meaning `operations_commenced`.
- Use 31 March 1984 for `operations_ceased`.
- Leave exact incorporation and dissolution dates unresolved unless independently sourced.
- Keep the transit company identities separate; use `TRANSIT_FINDINGS.json` for the 1978 group ownership observations.

## Primary sources

- **PC-S01:** [BC Hydro Annual Report 1978/79](https://digital.library.mcgill.ca/images/hrcorpreports/pdfs/6/632602.pdf), printed 10 / PDF 12. The original page image was inspected. [Accessible OCR](https://archive.org/stream/McGillLibrary-632602-27869/632602_djvu.txt).
- **PC-S02:** [Auditor General 1986, appendices](https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19860401a-1986reportpart2appendices.pdf), B16 note 9(i) / PDF 21, corroborated by C17 note 9(g) / PDF 80.
- **PC-S03:** [Auditor General 1987](https://www.oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-19870301-report-auditor-general-1987.pdf), appended Public Accounts A12 / PDF 160.

Source hashes and structured claims appear in `PACIFIC_COACH_FINDINGS.json` and the package source register. Source PDFs are linked, not embedded in this package.
