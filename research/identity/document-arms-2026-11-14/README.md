# Historical document arms — source identification follow-up

Reviewed **14 November 2026**. This continues the [13 November investigation](../document-arms-2026-11-13/README.md) and resolves the provenance of two supplied headings. It does **not** recover a printer's master, identify the historical typefaces, or turn the existing vector studies into verified reproductions.

[Source comparison sheet](source-evidence-review.png) · [Portable SVG](source-evidence-review.svg) · [Checksums and page/clip coordinates](source-register.json) · [Validation](validation.md)

## Completed integration and artwork review

The [browser acceptance record](validation.md#browser-acceptance-completed---14-november-2026)
covers the complete application, all nine references, phone-width layouts, colour
state and five download formats. [PR #67](https://github.com/ahzs645/PofBC/pull/67)
integrates the source viewer and responsive fixes.

Both PRs below are merged. The [live release receipt](validation.md#merged-release-and-live-acceptance---15-november-2026-utc)
records the successful Pages deployment and focused live browser review on
15 November 2026 UTC.

The reconciled [nine-page illustrated catalogue](../arms-variants-2026-11-14/catalogue.pdf)
contains 32 specimens and 30 linked sources. Its [records and source notes](../arms-variants-2026-11-14/README.md)
now identify the two supplied headings on pages 1 and 4 of OIC 1121/1978;
[PR #64](https://github.com/ahzs645/PofBC/pull/64) contains that research integration.

The [first measured overlay and partial structural study](../historic-arms-overlay-2026-11-14/README.md)
uses the 1960 Museum report cover, printed in 1961, as a separately identified
arms target. It quantifies the existing drawing's differences without presenting
the incomplete study as a production replacement. The [source-acquisition record](../historic-arms-overlay-2026-11-14/source-acquisition.md)
states what was checked for a better scan and the exact remaining acquisition target.

## Two supplied headings come from the same official record

The complete [Order in Council 1121/1978](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1121_1978) was retrieved and inspected as a **four-page PDF**. The [held copy](reference/oic-1121-1978.pdf) provides the following matches:

| Supplied reference | Matching PDF page | Evidence |
| --- | --- | --- |
| [Government caption](../document-arms-2026-11-13/reference/government-caption.png) | **1** | Order **1121**, approval **4 May 1978**, and the arms above the government caption. |
| [Blackletter Crown-grant heading](../document-arms-2026-11-13/reference/blackletter-grant.png) | **4** | The split **British / Columbia** heading, tracing/comparison signatures and Crown Grant No. **8498**. The full sheet identifies **Kootenay District** and **Provincial Rental Housing Corporation**. |

Page 4 is a **map attachment**, rather than an entire Crown-grant instrument. Its inclusion establishes the heading's occurrence in this dated order file. The sheet's own creation date and the original grant's issue date are **not established**. Do not assign **4 May 1978** as either date.

The [separate OIC 832/1978](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0832_1978), approved **6 April 1978**, remains an independent government-caption specimen; its [held copy](reference/oic-832-1978.pdf) has three pages, with the heading on page 1.

The [split-serif reference with number 279](../document-arms-2026-11-13/reference/split-serif.png) remains unidentified and undated. It must not inherit either order's date.

## A dated publication contains two different arms drawings

The provincial Department of Mines pamphlet [*Mining in British Columbia: An Outline of the Development of the Industry*](https://cmscontent.nrs.gov.bc.ca/geoscience/publicationcatalogue/Miscellaneous/BCGS_MP-46.pdf) is held by the British Columbia Geological Survey. The [23-page scan](reference/mining-bc-1954.pdf) was downloaded and its first two pages visually inspected.

Both the cover and inner title page bear a **1954** imprint naming **Don McDiarmid**, Printer to the Queen's Most Excellent Majesty. They use visibly different arms drawings: the cover's rendering is wider, with different shield, sun and motto-scroll details from the inner title-page rendering.

This is evidence for multiple renderings **within one publication**, not evidence of a change of identity between two dates. It supports keeping specimens separate when comparing proportions or reconstructing linework. The scanned arms themselves occupy only a small part of each page; these are useful dated comparisons, not sufficiently detailed replacement masters.

## Official historical reference and its limits

The Province's [official arms history](https://www2.gov.bc.ca/gov/content/governments/celebrating-british-columbia/symbols-of-bc/coat-of-arms) links an image captioned as the arms after the **1906** modifications. The [original JPEG](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/celebrating-british-columbia/symbols-of-bc/1906-arms.jpg) is held [without enlargement](reference/1906-arms.jpg) at **200 × 186 pixels**.

That caption identifies the historical arms configuration; it does not establish the drawing's artist, engraving date or use on any particular document. Its resolution is too low to recover fine linework reliably.

The same official history distinguishes the **31 March 1906** shield-and-motto grant from the **15 October 1987** augmentation. It also states that the crest and supporters continued in use before their grant. These dates explain the heraldic distinction; they do not establish a universal end date for a printed heading or one common artwork master.

## Guides and archival leads

| Source | What was checked | What remains unknown |
| --- | --- | --- |
| [*The Emblems of British Columbia*](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/celebrating-british-columbia/symbols-of-bc/bc-emblems-set.pdf) | Current official reproduction guidance was examined in the previous investigation. | It does not establish the typefaces or spacing of these earlier headings. |
| [Dr. Whitney Smith Flag Research Center Collection finding aid](https://www.cah.utexas.edu/documents/finding_aids/smith_dr_whitney_flag_research_center_collection.pdf) | PDF page **42**, **box 2013-160/83**, lists **“British Columbia Visual Identity System.”** The catalogue entry was rechecked. | Folder contents and dates remain unexamined. The title alone does not show which identity it documents. |
| [Alan B. Beddoe fonds finding aid](https://data2.archives.ca/pdf/pdf001/p000000941.pdf), Library and Archives Canada | Search-indexed text of printed page **7**, **MG30-D252**, **container 9**, lists **“H7 (e) British Columbia,” 1904–1963**. LAC's [official fonds overview](https://thediscoverblog.com/2014/07/31/what-is-heraldry/) independently confirms the fonds. | File contents were not inspected. The indexed table repeats **file 19** for the adjacent New Brunswick and British Columbia entries; verify the file number with the archive before ordering. The date range does not establish the date of an artwork or manual. |

The Beddoe entry is a new route toward correspondence or artwork concerning the older arms, but it is **an archival lead**, not a recovered reproduction sheet. No archive or other person was contacted.

No period graphic standard for the three exact headings was verified in this follow-up. The project's **1977 Visual Identity Program** material documents a separate simplified identity and should not supply retrospective rules without direct evidence. Ahmad Jalil's *The Forgotten Crest* describes this project and is not independent corroboration.

## Consequences for the builder

The new evidence improves the **source viewer and provenance**, while the renderer remains a provisional study:

- Keep the held document scans distinct from the editable reconstructed artwork. A dated source can verify an occurrence without authenticating the vector's geometry.
- Link the government and blackletter layouts to their respective pages in the same order, and show the map sheet's date limitation.
- Keep the three lettering choices identified as modern stand-ins. The exact historical typefaces remain unidentified.
- Preserve separate specimen identities when comparing the 1954 cover, 1954 title page and 1978 document headings.
- Continue to disclose that the shared arms path comes from a generated-master conversion also used by the 1919 cardboard plate. This investigation did not replace or validate that master.

The next useful acquisition is a clear period printing block, reproduction sheet, or sufficiently detailed scan of the particular engraving being reconstructed. It should be compared against the held specimens before replacing the current path.
