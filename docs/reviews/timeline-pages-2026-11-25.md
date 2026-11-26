# Timeline page review

25 November 2026

## What to carry forward

**Use the card to choose a period. Use the destination to explain what changed.** On SIFERP, “2002–2015 · FORREX · Next name” gives a reader enough information to open the next collection. The first FORREX era can then distinguish the operating name in the June report from the registered name change on 29 July and cite the Gazette. Keep the same hit area and visible keyboard focus for cards that open another page and cards that jump down the current one. [SIFERP](http://localhost:5173/dev/data?view=gallery&logos=collected-siferp) · [FORREX](http://localhost:5173/dev/data?view=gallery&logos=collected-forrex)

| History the reader is following | Example | What the example teaches |
| --- | --- | --- |
| One organization changes its name | [Technical Safety BC](http://localhost:5173/dev/data?view=gallery&logos=collected-technical-safety-bc) | This is the next candidate for a compact linked card. Its predecessor section already records the BC Safety Authority’s 20 September 2017 operating-name change. Keep “operating name” in the detail. |
| Several organizations merge or divide responsibilities | [BC Innovation Council](http://localhost:5173/dev/data?view=gallery&logos=collected-bc-innovation-council) · [Southeast Kootenay](http://localhost:5173/dev/data?view=school-districts&district=school-district-5) | Show each contributing organization at the event. The council identifies two merger partners. The school district names Fernie and Cranbrook, dates both connections to 2 December 1996 and links each district and the order. A sequence of three name cards would obscure who merged with whom. |
| One organization funds another | [Forest Renewal BC](http://localhost:5173/dev/data?view=gallery&logos=collected-forest-renewal-bc) · [Forestry Innovation Investment](http://localhost:5173/dev/data?view=gallery&logos=collected-forestry-innovation-investment) | Put the period, role and counterparty on both records. “Funded” and “Delivered under contract” describe different contributions. Reserve “Previous name” and “Next name” for continuity of identity. |
| An organization has a long sequence of designs | [BC Rail](http://localhost:5173/dev/data?view=gallery&logos=collected-bc-railway-company) | Lead with a scannable era index. Keep the distinct designs, qualified dates and evidence in each era. On a phone, offer an expandable index or jump-to-era control when showing the full index would push the first design off screen. |
| The reader wants to know what existed in a year | [Licence plates](http://localhost:5173/dev/data?view=plates&year=2000) · [Government](http://localhost:5173/dev/data?view=government&year=2001) | Align concurrent periods on a shared year axis. Both views supported stepping the year with the keyboard. The selected year is visible while the records change. |
| The history is the material the reader came for | [UNBC’s origins](http://localhost:5173/dev/data?view=gallery&subject=university-of-northern-bc#unbc-origins-timeline) · [FireSmart BC](http://localhost:5173/dev/data?view=initiatives&initiative=firesmart-bc&section=timeline) | Keep dates, explanations and citations together in the event list. UNBC has ten milestones and a link directly to the section. FireSmart’s 27 events occupied roughly 8,800 pixels at phone width. Year-group links would let a reader skip to the relevant period. |

## Two changes with the broadest gallery benefit

1. **Make an era addressable and focus its heading on selection.** Activating BC Rail’s fifth era by keyboard scrolled to the right content but left focus on the index button and the URL without a fragment. On the same page, “Company connections” updates the fragment and moves focus to its section. UNBC also supports opening its timeline directly. The existing section-link behaviour is a model for gallery eras. [BC Rail company connections](http://localhost:5173/dev/data?view=gallery&logos=collected-bc-railway-company#railway-connections)
2. **Scale the index to the number and length of its entries.** At a 390-pixel viewport, BC Rail’s 13 entries occupied 932 pixels before the era details. Temporarily allowing each row its natural height brought that to 724 pixels. At 1,360 pixels, the index extended 637 pixels beyond its own visible width. It was the only one of the 23 collection era indexes to overflow horizontally at that desktop width. A compact index for long histories would preserve the equal hover areas that work well on SIFERP. [BC Rail](http://localhost:5173/dev/data?view=gallery&logos=collected-bc-railway-company)

## Other layout finding

At a 390-pixel viewport, two party detail pages were wider than the screen. The Provincial Party page measured 447 pixels and the BC Conservative page measured 432 pixels. The artwork and file-detail area extended past the viewport on both. Repairing that area would let readers scroll vertically from artwork to history without sideways movement. [Provincial Party](http://localhost:5173/dev/data?view=parties&party=provincial-party) · [BC Conservative](http://localhost:5173/dev/data?view=parties&party=bc-conservative)

## Coverage

I enumerated routes from the local catalogues and loaded them in Chromium at a 390-pixel phone width. I checked all gallery collection layouts and initiative timeline sections at 1,360 pixels as well, plus representative desktop records for the other views. Targeted interaction checks used the running app with its normal assets.

| Area | Coverage |
| --- | --- |
| Logo gallery | 27 collection pages, including all 23 with an era index, 152 mark routes and six organization-register routes. Two older mark URLs open their Pacific Gateway initiative records. The UNBC and Interior University Society origin stories open through their section links. |
| Initiatives | All 20 sections declared as event timelines, including sections labelled “History.” |
| School districts | All 91 current and historical district histories. |
| Political parties | The lineage index and all 19 party pages with dated events. |
| Government | 833 distinct organization or ministry selections from annual snapshots, using one available year per record. The common year control appeared throughout the list selections. I also checked the graph, comparison and selected-record lineage layouts. |
| Licence plates | The by-year overview, 16 family timelines and 447 individual design strips. |

The review covered timeline layouts and distinct records. Repeated year settings, artwork variants and colour themes were sampled. Historical claims and external sources were outside this design review.
