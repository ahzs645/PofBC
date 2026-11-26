# CleanBC program marks

The atlas already recorded the CleanBC plan and its December 5, 2018 launch. The April 2024 guide supplies a later visual record for that program. The gallery now connects the atlas node `sub-cleanbc` to one collection with 14 designs and 54 selectable files. April 2024 dates the illustrated specimens. The artwork kits also contain versions for which the guide gives no dated example. [Plan launch](https://news.gov.bc.ca/releases/2018PREM0088-002338) · [Provincial guide](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/services-policies-for-government/policies-procedures-standards/web-content-development-guides/corporate-identity-assets/visid-pdfs/guidelines_cleanbc-programmarks_april2024.pdf) · [Artwork kits](https://www2.gov.bc.ca/gov/content/governments/services-for-government/policies-procedures/bc-visual-identity/download-marks#clean-bc-marks)

## Family and versions

| Name or treatment | BC-endorsed mark | Standalone wordmark | Connection |
| --- | --- | --- | --- |
| CleanBC | 4 files | 5 files | Base signature. The wordmark kit includes a second positive labelled CMYK. |
| CleanBC with tagline | 4 | 4 | Adds “our nature. our power. our future.” beneath the same name. |
| Better Homes | 4 | 4 | Program descriptor below CleanBC. |
| Active Transportation | 4 | 4 | Program descriptor below CleanBC. |
| Better Buildings | 4 | 4 | Also appears in the Financeit lockup. |
| Go Electric | 4 | 4 | Program descriptor below CleanBC. |

Each group contains colour positive, colour reverse, solid black and solid white. Pages 2 and 3 illustrate the paired colour forms. Page 4 illustrates both solid treatments for the tagline wordmark. The seven provincial ZIP files establish the wider monochrome selection. The source register records the actual archive member, including differences such as “BCID” versus “BC” and spaces within “Better Buildings.” [Source register](../../../src/gallery/cleanbcSources.json)

Two distinct arrangements complete the 14 designs on page 1.

- **Supported by the Province** combines the horizontal provincial signature and its support acknowledgement with the CleanBC tagline. Its kit supplies four treatments. The ordinary endorsed layout uses the stacked provincial signature and a gold divider in the positive version.
- **Better Buildings and Financeit** extends the endorsed Better Buildings mark with a second divider and the partner's logo. The guide supplies one colour specimen. Financeit separately describes administering a **Better Homes** financing program. These sources document different relationships. The guide identifies which program name appears in this particular artwork. [Financeit’s program announcement](https://www.financeit.io/financeit-x-cleanbc-extension/)

The atlas also records the CleanBC Industry Fund. The five-page guide identifies no dedicated Industry Fund mark. Its name is evidence of a program relationship, and a separate artwork holding would need its own specimen. For rebates and offers, page 1 gives a reusable copy pattern that places the CleanBC offer or subprogram name before a “for” phrase identifying the type of offer. [Industry Fund](https://www2.gov.bc.ca/gov/content/environment/climate-change/industry/clean-industry-fund)

## What can share a template

| Reusable field or behaviour | CleanBC example | Where the evidence belongs |
| --- | --- | --- |
| Family, descriptor, layout | CleanBC → Better Buildings → endorsed or standalone | Each layout gets its own stable design ID. Special lockups add a named partner or acknowledgement. |
| Edition, treatment, intended ground | April 2024 colour reverse on dark | Each verified file belongs to one design. A theme default can select its published reverse. Explicit version selection retains that file and its colours. |
| Publisher and source | Provincial kit → exact ZIP member, or guide → page and bounds | Record the method and SHA-256 per file. Retain a separate edition or colour-space export when the source distinguishes it. |
| Application rules | Minimum height, clear space, proportional scaling, BC mark elsewhere | Attach the rule to the illustrated layout and use context. A future proof sheet can select an approved asset, scale it and measure the surrounding space. |
| Unverified or restricted form | Tiny endorsed mark for HTML5 ads and social platforms | Record the lead and allowed context. A missing file remains an open inventory item. |

The gallery implements the layout and version template with a list of actual source files for each design. The same approach fits the project's StrongerBC family, whose guide also distinguishes endorsed and standalone marks and calls for a visible provincial signature elsewhere when using the wordmark. Artwork, spacing and minimum dimensions belong to each family's own guide. The CleanBC guide asks users to use the supplied program lettering. The program-name slot in this template selects finished artwork. [CleanBC collection model](../../../src/gallery/cleanbc.js) · [StrongerBC guide, p. 5](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/services-policies-for-government/policies-procedures-standards/web-content-development-guides/corporate-identity-assets/visid-pdfs/strongerbc_guidelinesforuse.pdf#page=5)

The base white wordmark and all eight Better Buildings versions share one set of outlines in [artwork/cleanbc](../../../artwork/cleanbc). Each layout records its exact source coordinates. The templates preserve the publisher's layer order, blend modes and special white symbol cutout. `npm run build:cleanbc-artwork` generates the nine standalone SVGs at their existing download URLs after verifying each file against the source register's SHA-256. The site build, gallery preview and display-copy build run this step automatically.

## Specifications from the guide

Page 3 allows the standalone wordmark at a different scale when the BC mark remains visible elsewhere. Page 5 measures **height**, including the tagline where present. It gives three illustrated minima.

| Illustrated layout | Print height | Web height |
| --- | ---: | ---: |
| Plain standalone wordmark | 0.40 in | 45 px |
| Standalone wordmark with tagline | 0.46 in | 50 px |
| BC-endorsed plain CleanBC | 0.46 in | 50 px |

The protective margin equals the height of the lowercase “c” in “clean.” Scale both axes equally. The guide supplies no separate numeric minimum for the four named program descriptors or the Financeit lockup. For contractor applications, the Better Homes Energy Savings Program has more specific requirements, including joint use with the BC and BC Hydro marks. This is a separate application context. [Program terms, Schedule D](https://betterhomesbc.ca/wp-content/uploads/2026/03/Contractor_TsCs_ESP_1April2026.pdf)

| Page 4 palette | Web | RGB | CMYK |
| --- | --- | --- | --- |
| BCID Gold | #E3A82B | 227, 168, 43 | 0, 30, 100, 0 |
| BCID Blue | #234075 | 35, 64, 117 | 100, 80, 6, 32 |
| BCID Blue (60%), reverse | #606C9C | 96, 108, 156 | 60, 48, 4, 19 |
| Sky Blue | #008FB4 | 0, 143, 180 | 100, 5, 14, 17 |
| Douglas Fir Green | #5FA544 | 95, 165, 68 | 68, 12, 100, 1 |
| Leaf Green | #8BC043 | 139, 192, 67 | 48, 0, 95, 4 |
| River Blue, additional | #005C97 | 0, 92, 151 | 100, 53, 4, 19 |
| Deep Blue, additional | #002A4E | 0, 42, 78 | 100, 57, 12, 66 |

## Source findings and open leads

The supplied PDF matches the provincial download byte for byte (SHA-256 `3de406a4a53637829bee1ffe64853a88ee309b317f1ead26cca1be025b5a2cef`). It contains vector drawings and no image objects. Of the 54 gallery files, 48 are unchanged kit SVGs, two isolate source artwork from kit SVGs, two convert kit EPS paths and two extract paths from the guide.

| Source finding | Gallery treatment |
| --- | --- |
| The base wordmark ZIP includes RGB-positive and CMYK-labelled positive SVGs, both with coloured lettering. There is no RGB-reverse member. | Retain both positive files. Isolate the printed reverse on page 3, row 2, right column. |
| The Better Homes and Better Buildings endorsed solid-white SVGs each have a full-artboard white rectangle covering the logo. The corresponding EPS and PNG also render as white rectangles. | Remove only the full-size white rectangle from each SVG. Preserve the native white lettering, divider, emblem, and their positions. The per-file record identifies the source treatment and links the original kit. |
| The Go Electric endorsed solid-white SVG also draws a white rectangle. The file named solid white for its standalone wordmark draws dark lettering. | Both same-kit white EPS files render the intended marks, corroborated by the transparent PNGs. Convert the EPS with Ghostscript PDF output and pdftocairo SVG output. Both PDF intermediates contain vector drawing commands and no bitmap images. |
| The download page lists seven CleanBC kits. None contains the Financeit lockup. | Isolate the whole published lockup on page 1, lower right. An independent master and any additional documented colourways remain open leads. Its dark gallery copy is a display adaptation. |
| Page 5 mentions a restricted tiny alternative to the endorsed mark. | No matching tiny master was identified among the seven kits. The print/web minima above apply to the pictured regular marks. The tiny version's geometry and size threshold remain unverified. |

For the two guide extracts, coordinates in the source register are PDF points from the top left. PyMuPDF removed graphics outside each specimen and the test ground, then exported the remaining drawings as SVG. The Financeit lockup retains 62 painted paths and the standalone reverse retains 12. Gallery crops and theme copies are generated separately with `scripts/build_collected_display.py`. Downloads distinguish the kit originals from source extractions and conversions.
