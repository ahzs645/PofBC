# FireSmart BC

The supplied July 2025 guide and the [publisher’s PDF](https://firesmartbc.ca/wp-content/uploads/2023/04/07.22.25_FSBC_BrandGuidelines.pdf) have the same SHA-256, `bd922d1a28dab4c23091b338d690b26f0cc092eda4dcaf931781b48d4564c9bf`. A complete copy is held in [the public collection](../../../public/initiatives/firesmart-bc/brand-guidelines.pdf).

## Program relationships and dates

Page 16 diagrams four sub-brands. The [provincial directory](https://firesmartbc.ca/what-is-firesmart/) also lists the Education and Farm and Ranch programs. The [2022 annual report, page 10](https://firesmartbc.ca/wp-content/uploads/2023/03/FireSmart-BC-2022-Annual-Report.pdf#page=10) documents the Library Program’s launch. These seven entries link to the provincial initiative. Funding streams, awards, professional roles, research collaborations, publications and campaigns have their relationships explained in the entry. Each child’s source library follows its own records.

The 2022 strategic plan dates early B.C. activity to the late 1990s. May 2017 dates the formation of the BC FireSmart Committee. The 2024 annual report records Home Partners becoming the provincially managed Wildfire Mitigation Program. The July 2025 guide already illustrates the Local FireSmart Collective Program, which was still in development that year. The public introduction is documented in April 2026.

## Artwork

| PDF page | Published artwork |
| --- | --- |
| 5 | Provincial signature, positive and reverse |
| 13 | Ember, front profile, side profile, sitting and standing |
| 17 | Wildfire Mitigation Program, positive and reverse |
| 19 | Local FireSmart Collective Program, positive and reverse |
| 20 | Plant Program, positive and reverse |
| 22 | Wildfire Resiliency and Training Summit, positive and reverse |

For each specimen, isolate its InDesign `/PlacedGraphic` marked-content block from the page stream. Retain the PDF colour space, graphic state and resources. Remove the surrounding layout and the preceding example’s closing graphics-state restore, then crop to the transparent artwork bounds. Convert the cropped single-page PDF with Poppler’s `pdftocairo -svg`. This preserves the clipped gradient fills in the plant shield, summit symbol and full-body foxes. Verify that each output has path geometry and no image elements. Rendering the isolated PDF over the sampled guide background at 4× scale reproduced each source panel to within antialiasing differences. Per-file checksums and locators are in [the gallery dataset](../../../src/gallery/fireSmart.js).

The parent and sub-brand designs each have an independently extracted reverse. The [gallery display builder](../../../scripts/build_collected_display.py) makes the display copies. Native SVGs remain available as downloads. The guide describes monochrome signatures on page 5 but illustrates only two full-colour versions. FireSmart BC’s brand asset request is an open lead for the monochrome originals. The “FireSmart Purple” swatches on pages 20 and 22 are visibly purple but carry the same printed RGB and hex specifications as Charcoal. Preserve both the printed values and the source artwork.

Page examples on the initiative are WebP renders of complete guide pages 9, 14, 18, 21 and 23. The Farm and Ranch and Library images are first-page renders of the linked example assessment and readers’ catalogue. The Education image is a WebP display copy of the illustration on the program website. Each of these links to its source through the relevant initiative record.
