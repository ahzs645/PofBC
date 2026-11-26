# BC endorsed marks · June 2019 setup audit

The CleanBC and StrongerBC galleries already pair an endorsed layout with a standalone wordmark and let each layout carry its own source files. The largest gap is at placement time. The generator can add padding and choose an export width, but an endorsed-mark template needs to measure the visible artwork, apply the spacing rule for that layout, and account for a provincial signature placed elsewhere on the page.

The source is the Province’s four-page *BC ID Guidelines for Use of Endorsed Marks*, supplied as `bcid_use_of_endorsedmarks_2019.pdf` (SHA-256 `e57abca3018bc824b1b12f281d542ae548f1276012e9fcca457c7d1e58226810`). “BCProgram” is the example lettering. The page references below refer to this edition. The setup proposals are project recommendations.

## Which versions the guide actually shows

| Treatment | BCProgram endorsed lockup, p. 1 | Provincial mark on its own, p. 2 | Expected background |
| --- | --- | --- | --- |
| Full colour positive | Shown | `cmyk_pos` | Light |
| Full colour reverse | Shown, with white lettering and lighter blue mountains | `cmyk_rev` | Dark |
| Greyscale positive | Shown, with distinct light and dark values | `gry_pos` | Light |
| Greyscale reverse | No illustrated lockup | `gry_rev` | Dark |
| Single-colour positive | Shown in blue | `solid_pos`, shown in blue | Light |
| Single-colour reverse | No illustrated lockup | `solid_rev`, shown in white | Dark |

The current ministry generator offers Colour, Reverse, Black and White. The shared program version helper recognizes positive, reverse, black, white and a CMYK-labelled positive. To describe this source it would also need greyscale positive, greyscale reverse and solid blue positive, with light or dark ground attached to each source file. The two greyscale versions and solid blue belong only on designs with evidence for them. The separate BCProgram wordmark is illustrated in full colour on page 1. [Current generator colourways](../../../src/current/currentVariants.js) · [Program version helper](../../../src/gallery/programMarkVersions.js)

## Placement and export options

| Setup option | What the project already does | What the 2019 guide adds |
| --- | --- | --- |
| Arrangement | Galleries group endorsed marks and standalone wordmarks. The current ministry generator accepts editable wording. | Select the finished program artwork. For the joined version, preserve lettering, divider and proportions together. For separate placement, use the standalone wordmark without a divider and allow the BC mark a different scale elsewhere in the same communication (p. 1). |
| Protective margin | None, Snug, Standard and Generous add 0%, 12.5%, 25% and 50% of total mark width. | A **Guide clear space** option would measure one X on every side. For the example, X is the height of the program lettering indicated by the diagram. Store X in source artwork coordinates so a longer name doesn't acquire a larger margin just because it is wider (p. 1). |
| Minimum visible height | Raster exports specify canvas width, from 512 to 4096 px. Vector export preserves proportions. | Let a proof report the placed artwork height before padding. For this endorsed example, compare it with **30 px on screen** or **10 mm in print**. Treat those as separate thresholds. A large download can still be placed too small (p. 1). |
| Background proof | The current picker pairs colourways with BC palette backgrounds. Gallery variants can carry their own intended ground. | Preview the chosen positive or reverse on the intended placement colour. Page 2 shows both wrong pairings. Inspect lettering and mountain detail as well as the sun, which should read as the brightest part. The guide gives a visual test and specifies no numeric contrast ratio (p. 2). |
| Output purpose | The generator exports SVG, PDF, PNG, WebP and JPEG. Gallery versions can already carry additional publisher downloads, including StrongerBC CMYK PDFs. | Reuse the additional-download slot for verified source files. Label the medium and colour process independently of the extension. The 2019 examples pair web logos with RGB SVG, Word/PowerPoint with RGB WMF/EMF, posters and banners with CMYK EPS, and newspaper ads with CMYK WMF/EMF/EPS. The guide also describes single-ink GREY print artwork. The browser PDF export has no process-colour selector (pp. 3–4). |

A practical proof would show, for example, **29 px artwork · 30 px minimum** even if the canvas is 64 px high. A page template could identify the other visible BC mark when a standalone program wordmark is selected. A single-logo download can show the placement note, while validation of the second mark requires the surrounding composition. [Current mark sizing](../../../src/current/currentMarks.js) · [Clear-space presets](../../../src/logo/layouts.js) · [Export sizes and formats](../../../src/export/exportLogo.js) · [Gallery downloads](../../../src/gallery/CollectedMarkView.jsx)

## What can share the CleanBC template

- **Share** the family and layout picker, selection of a verified source version, intended background, source locator and original-file downloads. For a placement proof, share the fields for spacing reference, print and screen minimum heights, and companion-mark placement.
- **Set the values per layout and source edition.** CleanBC measures clear space with the lowercase “c” in “clean.” Its plain standalone wordmark has a 45 px minimum and its plain endorsed mark has a 50 px minimum. StrongerBC's A–D arrangements have screen minima of 50, 25, 50 and 40 px respectively. Keep the 2019 example’s 30 px attached to that example. [CleanBC rules](../cleanbc/README.md) · [StrongerBC rules](../stronger-bc/README.md)
- **Retain the published palette by edition.** Page 1 lists reverse blue as `#65799E`. The current generator uses `#7B8CAC`. The same page gives gold as RGB 227/168/43 (which converts to `#E3A82B`) and separately prints HEX `#FDB913`. Record both source values and identify the source file used for each reproduction. [Current palette](../../../src/current/currentVariants.js)
- **Keep typography with the publication template.** Page 2 describes Myriad Pro for supporting type, prefers its Light weight for body text, and offers Adobe Garamond Pro for formal work. Page 1 preserves the supplied program lettering. A surrounding document can expose text styles while the mark selector uses finished artwork.

Implementation priority would be the guide-based sizing and spacing proof first, followed by a companion-mark placement option for page layouts. Extend the version selector when attaching the corresponding source artwork. The existing download mechanism can carry Office and print masters as they are verified. The Province's download catalogue also identifies name, orientation, colour space, positive/reverse and format as separate parts of a source filename. [Provincial download catalogue](https://www2.gov.bc.ca/gov/content/governments/services-for-government/policies-procedures/bc-visual-identity/download-marks)

## Implemented placement checks

The **Check placement** panel on a gallery mark accepts the visible height in px for screen, inches for the 2024 print guides, or mm for the 2019 print guide. It can apply the illustrated clearance or compare it with the smallest measured margin in a composition. The 2019 standalone wordmark and separate provincial mark have no independent numerical limits in this guide. Standalone wordmarks provide a place to record where the accompanying provincial mark appears. Print mode links to the verified CMYK EPS member of an artwork kit when available.

Spacing is calibrated from the source geometry. CleanBC uses the lowercase “c” relative to visible artwork height, including the descriptor or tagline. StrongerBC uses the upper corner square in each page 4 diagram, divided by the height of the visible ink in that diagram. Those square/height measurements in PDF points are A 13.17/42.799, B 12.595/26.658, C 13.17/39.165 and D 12.595/39.05. The 2019 joined example uses the height of the program capital letters. These ratios are measurements of the illustrations. The numerical minimum heights are printed specifications. The panel rounds the calculated clearance up for entry at the displayed precision.

**Download placed SVG** adds the selected margin and background to the vector artwork and sets the chosen physical or screen dimensions. It measures from the ink bounds recorded by the gallery build, excluding its rendering border. Source downloads still supply the individual artwork. The 2019 collection registers the four lockup treatments and separate wordmark from page 1, and the six provincial-mark treatments from page 2. The extraction register records page coordinates and file digests. [Shared rules](../../../src/gallery/programPlacement.js) · [2019 specimen register](../../../src/gallery/endorsed2019Sources.json)
