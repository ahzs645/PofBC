# Historical document arms — research and provenance

Reviewed **13 November 2026**. This evidence supports the **Historic arms** layout studies in the Identity builder. It does not establish an official reproduction master or a common standard for the three supplied document headings.

## What the examples show

| Reference | Observed heading | Date evidence |
|---|---|---|
| [Split serif heading](reference/split-serif.png) | Arms between **BRITISH** and **COLUMBIA**; number 279 below | Document undated in the supplied crop |
| [Order-in-Council heading](reference/government-caption.png) | Arms over **THE GOVERNMENT OF THE PROVINCE OF BRITISH COLUMBIA**; order 1121 | **4 May 1978** appears in the approval line; exact order not independently retrieved |
| [Crown-grant heading](reference/blackletter-grant.png) | Arms between blackletter **British** and **Columbia** | Document undated in the supplied crop |

These are three observed applications, not proof of one prescribed logo system. The source PNGs are copied without alteration. [source-register.json](source-register.json) records their original filenames, dimensions and SHA-256 hashes. Screenshot filenames date the capture, not the document.

## The historical distinction

The Province’s [official arms history](https://www2.gov.bc.ca/gov/content/governments/celebrating-british-columbia/symbols-of-bc/coat-of-arms) separates the 1895 design, the **31 March 1906** shield-and-motto grant, and the **15 October 1987** augmentation. The Province continued to use a crest and supporters before they were granted. The 1987 additions include the lion’s dogwood collar, helmet, wreath and mantling, and dogwoods around the motto scroll.

The [Provincial Secretary’s 1987/88 annual report](https://rbcm.ca/wp-content/uploads/2025/07/bca_annual_report_1987_88.pdf), printed page **vi** / PDF page **7**, supplies a contemporary account of those changes. [Robert D. Watt’s ceremony history](https://bc-yukon.heraldry.ca/archives/blazon/issues/Blazon-2021-2-Summer.pdf), reprinted with permission in *The Blazon*, Summer 2021, pages **21–23**, adds historical context.

The document crops appear to belong to the earlier arms tradition. That attribution does not identify a specific engraving or prove that one drawing or lettering arrangement served every ministry. Keep it distinct from the simplified rounded-square badge documented by the **1977 Visual Identity Program** manuals already in the project.

## What the implementation reuses

The four fixed studies—arms alone, split serif heading, government caption and blackletter heading—reuse the geometry in [the supplied Grace McCarthy arms fragment](../../../artwork/stationery/grace-mccarthy/evidence/supplied-arms-fragment.txt). The repository provenance audit matches its **1146 × 1283** master to PlateForge’s `CREST_PATH`, described there as a **vector conversion of a generated master**. The fragment itself is tagged `data-accuracy="approximate"`.

This is the same drawing lineage used by the 1919 cardboard plate rendering. That connection makes the reuse explicit; it does not verify the drawing against the three document specimens. The fragment also differs in proportions from the Grace McCarthy card reference. Treat the new output as a **provisional layout study**, with an arms drawing still requiring a reliable period master and detailed comparison.

The lettering is identified only by class: serif capitals, a condensed government caption, and blackletter. The renderer uses open-font stand-ins with outlined lettering. Neither an exact period typeface nor a universal spacing rule has been established. Recolouring is a study control, not a documented historical colourway. The output makes no claim to authorized government branding.

## Sources and their limits

- **Verified period specimen:** [OIC 832/1978, 6 April 1978](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0832_1978), first PDF page, provides an independent example of the arms-over-government-caption layout. It is a different order from the supplied **1121** crop.
- **Exact OIC still unresolved:** the [candidate 1121/1978 locator](https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1121_1978) could not be retrieved through the research browser. Its number and approval date currently come from the user’s image only.
- **Current guide, separate context:** [*The Emblems of British Columbia*](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/celebrating-british-columbia/symbols-of-bc/bc-emblems-set.pdf), page 3, discusses present arms reproduction and reverse treatment. After an initial HTTP 502, the four-page PDF was retrieved and page 3 inspected. It does not establish the older headings’ rules.
- **Archival lead:** the [Dr. Whitney Smith Flag Research Center Collection finding aid](https://www.cah.utexas.edu/documents/finding_aids/smith_dr_whitney_flag_research_center_collection.pdf), PDF page **42**, lists **box 2013-160/83, “British Columbia Visual Identity System.”** The folder’s dates and contents have not been examined.

**No independently verified period graphic standard for these exact document headings was found.** The 1977 manuals should not be applied retrospectively without evidence. Ahmad Jalil’s *The Forgotten Crest* article describes this project and was not counted as independent corroboration.

## Draft archival enquiry — not sent

Suggested recipient: [Legislative Library of British Columbia](https://www.leg.bc.ca/learn/legislative-library), `library@leg.bc.ca`, with referral to BC Archives or the King’s Printer if appropriate.

> I am documenting historical British Columbia government identity and seeking original artwork or reproduction instructions for the earlier provincial arms used on official documents. The attached examples show a split serif “British Columbia” heading, Order in Council 1121 approved 4 May 1978 with a government caption, and a blackletter Crown-grant heading. Do you hold, or know the location of, King’s/Queen’s Printer reproduction sheets, specimen books, printing-block records, stationery instructions or Crown-grant form masters for these applications? I am especially seeking dates, printer/designer attribution and clear scans that distinguish the different engravings. The 1977 Visual Identity Program manuals are already known to the project; the question concerns the earlier document forms. A full copy or authoritative identifier for OIC 1121/1978 would also help.

For the Texas lead, separately ask the Briscoe Center for the dates and item list of the **British Columbia Visual Identity System** folder before assuming it contains a relevant manual. No enquiries have been sent.
