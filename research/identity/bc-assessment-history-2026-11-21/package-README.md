# BC Assessment: historical identity research

Reviewed 21 November 2026 (Vancouver). Repository audited: `ahzs645/PofBC`, `main` at `bb468bc78bbc81d214477293934e0a8e3d4977d7`.

## Finding

The supplied geometric British Columbia outline is an authentic historical British Columbia Assessment Authority identity. Both supplied screenshots have been matched to the original public government disclosure PDF. PofBC already represents the organization but currently holds only the modern full-colour media-kit logo. Its own research register explicitly records that further BC Assessment research was skipped once a current vector was held.

This package records the research and source artwork. It does not represent a repository commit or a completed reconstruction of the historical map symbol.

## Why PofBC missed it

The October 2026 vector-search inventory records BC Assessment as:

| Field | Recorded value |
| --- | --- |
| Organization | British Columbia Assessment Authority |
| Short name | BC Assessment |
| Baseline category | `has-vector` |
| This pass | `baseline-vector-retained-not-researched` |
| Individually searched | `no` |
| Research scope | `Outside missing-vector research; baseline retained` |

The collection originally held JPG and EPS files of the same current design. Those two files were not two historical identities. The current gallery record contains one design entry, with SVG display artwork converted from the official EPS and the EPS retained as a download. The coverage logic counts an organization as holding vector artwork when at least one source vector exists. It explicitly says that this does not establish every era or an adoption date.

Thus the recorded gap is historical design coverage. The organization and its longer name are already present. No deliberate rejection of the historical map design was found in the current catalogue or relevant recorded work. This audit was not an exhaustive examination of every old branch.

Repository evidence:

- [Vector-search inventory](https://github.com/ahzs645/PofBC/blob/bb468bc78bbc81d214477293934e0a8e3d4977d7/research/identity/vector-search-2026-10-30/organization-inventory-records.json)
- [Current gallery data](https://github.com/ahzs645/PofBC/blob/bb468bc78bbc81d214477293934e0a8e3d4977d7/src/gallery/collectedData.js)
- [Coverage definitions and logic](https://github.com/ahzs645/PofBC/blob/bb468bc78bbc81d214477293934e0a8e3d4977d7/src/gallery/identityCoverage.js)
- [Original acquisition report](https://github.com/ahzs645/PofBC/blob/bb468bc78bbc81d214477293934e0a8e3d4977d7/research/identity/collection-2026-10-22/README.md)
- [Existing gallery collection](https://projects.ahmadjalil.com/PofBC/?view=gallery&logos=collected-bc-assessment)

## Original documents behind the screenshots

Both appear in the public [FIN-2016-64551 disclosure package](https://docs.openinfo.gov.bc.ca/Response_Package_FIN-2016-64551.pdf). The downloaded file has 171 PDF pages; its reproduced release pagination runs out of 176 and carries the earlier identifier FNR-2016-62793.

| Evidence | Actual PDF page | Printed release page | What it establishes |
| --- | ---: | --- | --- |
| Cowichan Valley office letterhead, May 1982 | 129 | 134 of 176 | The geographic symbol between the two uppercase halves of the organization's name was in use by May 1982. The day is damaged and remains unresolved. |
| 1989 & 1990 assessment notice | 10 | 10 of 176 | The same emblem appears behind the stacked uppercase name and the notice heading. The two years are the notice's assessment years. |

The included crops isolate the organizational artwork; full property records are not reproduced in this package.

## Cleaner historical references

### Official paper associated with the 1992 annual seminar

[Evolution of Real Property Taxation and the Assessment Function in British Columbia](https://info.bcassessment.ca/about/Shared%20Documents/Evolution%20of%20Real%20Property%20Taxation%20in%20BC%20-%201992.pdf), by John Collins, Area Assessor, Nelson, shows the same symbol on its cover and in its footers. The cover explicitly associates the paper with the 1992 annual seminar. An independent printing date is not stated on the inspected cover. The PDF's 2004 scan metadata records digitization, not logo adoption.

This is a scanned, raster-only document. `BC_Assessment_1992_Seminar_Logo_Crop.png` is an unretouched cover crop.

### BC Assessment presentation to AVICC, 2019

Page 12 of the [2019 AVICC presentation](https://avicc.ca/wp-content/uploads/2019/05/April-13-BC-Assessment-Fair-Taxation-and-the-Fundamentals-of-Property-Assessment.pdf) contains a cleaner grey horizontal reproduction with mixed-case lettering. `BC_Assessment_Historical_Logo_2019.png` is the embedded 1042 x 279 pixel image extracted directly from that PDF. It has not been traced, retouched, or enlarged.

It is a later official reproduction, not a newly found original vector master. Its grey treatment does not establish an original historic corporate colour, and its mixed-case lettering must not replace the uppercase lettering in the 1982 and 1989/1990 applications.

### Official visual sequence

Page 4 of BC Assessment's [8 March 2021 Rossland presentation](https://rossland.civicweb.net/document/10599/City%20of%20Rossland%20March%208%202021.pdf?handle=A4CE874F241C4CB38A88D6462C92F4D6) places the map identity, an italic 40th-anniversary wordmark, and the modern geometric identity together. `BC_Assessment_Official_History_Row_2021.png` reproduces that logo row. The middle item is an anniversary application, not a date label for the entire wordmark generation.

## Documented changes

The current [Corporate History](https://info.bcassessment.ca/about/Shared%20Documents/BCA-Corporate-History.pdf) records the board's endorsement of the shortened public name in 1994 (p40), a logo change in 1996 (p43), and a major rebrand in 2015 (p78). These events do not supply the map logo's introduction date or an exact retirement day.

## Another missing generation: the italic wordmark

The [3 May 2000 Trade-marks Journal](https://publications.gc.ca/collections/Collection/RG42-2-47-2375.pdf), printed p187 / PDF p190, official mark 911,901, identifies Arrus as the typeface. It describes the underline as a left-to-right comet expressing action and progress. The specified full-colour treatment combines PMS 072 blue lettering with PMS 109 yellow and PMS 032 red in the underline, with five degrees of colour mixing. The record also recognizes monochrome variants. The publication date is not the logo's introduction date.

The [2010-2012 Service Plan](https://www.bcbudget.gov.bc.ca/2010/sp/pdf/agency/bcaa.pdf), PDF p34, contains a blue wordmark and the slogan We Value BC as genuine vector paths. The SVG and PDF included here were extracted from that page, retaining the existing paths. They are source extractions, not Illustrator masters, redrawn lettering, or raster wrappers. They document the blue treatment visible in this particular publication.

Extraction verification: the resulting PDF has 22 vector drawing objects and no embedded images. The SVG contains no image elements, and was separately rendered for visual inspection. Colours follow the PDF renderer's conversion of the published source; they are not a new official RGB specification.

## Proposed catalogue treatment

Keep the existing `bc-assessment` organization and modern media-kit artwork. Add historical design records beneath it:

1. **British Columbia Assessment Authority - outline-map identity.** Record the verified May 1982 and 1989/1990 applications, the seminar-related cover, and the later official reproduction. Preserve the different arrangements as applications of the same emblem unless more exact geometric comparisons establish distinct masters.
2. **BC Assessment - italic wordmark.** Link the source vector from the 2010 publication and the specification in the 2000 official-mark record. Keep colour and monochrome treatments explicit.
3. **Anniversary applications.** Keep anniversary wording separate from the underlying wordmark and its period of use.

Track organization-level artwork availability separately from historical-design completeness. A useful research queue should allow an organization with a current vector to remain flagged for missing historic identities.

Suggested historical caption:

> British Columbia Assessment Authority: geometric outline-map identity. Documented on May 1982 letterhead and 1989-1990 assessment notices. Also appears in an official paper associated with the 1992 annual seminar and in later corporate-history presentations. Designer, introduction date and original vector master remain unconfirmed.

## Remaining limits

- No verified designer or original standards sheet was located for the map identity.
- No original vector master of the map identity was recovered. Its supplied source evidence remains raster.
- Formation of the organization in 1974 does not prove the logo was introduced in 1974.
- The historic uppercase typeface and original colour specifications remain unconfirmed.
- Later reproductions should be retained as later evidence, with their publication dates, rather than used to invent an earlier adoption date.

## Package contents

- This report and `source-register.json`, including URLs, page locators, extraction notes, and file hashes.
- Both original screenshot matches as focused source crops.
- The seminar-cover logo crop and directly extracted 2019 historical image.
- The 2021 official three-logo comparison row.
- The 2010 italic wordmark as an extracted SVG, cropped vector PDF, and PNG preview.

No full third-party publications are redistributed in the package. The source links above identify the originals.

## In this repository

Kept as supplied: this report (with this section added), its register as
`source/package-source-register.json`, the full 2021 logo row and the 2010 wordmark's PNG preview
in `source/`. The gallery's files are in `public/identity-collected/bc-assessment/`, each byte for
byte as supplied and renamed, except `bc-assessment-40-years-2021.png`, a crop of the middle logo of
the 2021 row (pixels 566–1002 across, 104–208 down, not retouched or enlarged).

`source-register.json` is this package in the gallery's own record format, which
`scripts/build-collected-marks.mjs` reads (as a history register: dated images beside verified
vectors). It holds the six files as two designs of the British Columbia Assessment Authority /
BC Assessment collection, beside the 2015 media-kit mark it already had:

- **The outline map**, from the May 1982 letterhead, with the 1989 & 1990 notice, the 1992
  seminar cover and the 2019 reproduction as its versions. The 2019 picture is a later
  reproduction, so it carries no date of use; the design is shown as seen 1982–1992.
- **The italic wordmark**, from the 2010 service plan's own vector paths (the cropped vector PDF
  is its download), with the official-mark publication of May 2000 as a further sighting and the
  40th-anniversary application as a version, undated, as the package advises.

The gallery shows the collection at `?view=gallery&logos=collected-bc-assessment`.
