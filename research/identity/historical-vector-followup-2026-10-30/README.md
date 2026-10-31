# Historical Crown and health logo follow-up

This collection brings the verified historical follow-up into the gallery and records a fourth, targeted search pass. It is integrated with `main` at `64599abab1d2198e00bb289ab013b2a539a29b04`, including the gallery tile-sharing changes from PR #15. The initial comparison used `766087b6f07eead08c32e1426696efa38ac42d81`; both revisions already contain the earlier 35-SVG vector-search batch.

**Added here: 8 original-path SVGs for 7 organizations, 11 additional raster specimens, and one source-page PNG used only as a display preview.** The fourth search pass contributed two of those raster specimens, both for Simon Fraser Health Region. It produced no further verified vector.

The original research scope was **21 former Crown organizations and 112 former health organizations without a verified vector**. The eight SVG files close seven organization-level gaps: four Crown bodies and three health bodies. **17 Crown and 109 health vector gaps remain, 126 in total.** These counts concern that historical checklist, not every organization or asset in the gallery.

## Verified vector additions

Each SVG contains original PDF path geometry, including outlined lettering. There are no embedded images, live text elements, external resources, newly traced contours or substituted fonts. The [source register](source-register.json) records the source URL, document checksum, page, path selection, crop coordinates, output checksum and visual comparison. Small rendered source crops are retained in [evidence](evidence/) for review.

| Organization | Specimen and source | SVG |
|---|---|---|
| BC Buildings Corporation | 2005 financial statements, PDF p. 1; emblem, name and tagline | [Artwork](../../../public/identity-collected/bc-buildings-corporation/bc-buildings-corporation-2005.svg) |
| BC Heritage Trust | 2001/02 annual report, published 2002, PDF p. 1; complete boxed mark | [Artwork](../../../public/identity-collected/bc-heritage-trust/bc-heritage-trust-2002.svg) |
| BC Assets and Land Corporation | 1998/99 annual report, back cover, PDF p. 21; emblem, full name and agency tagline | [Artwork](../../../public/identity-collected/bc-assets-and-land-corporation/bc-assets-and-land-corporation-1999.svg) |
| Land and Water BC | 2001/02 service plan report, published 2002, PDF p. 1; visible emblem and full name | [Artwork](../../../public/identity-collected/land-and-water-bc/land-and-water-bc-2002.svg) |
| Capital Health Region | June 2000 sewage-disposal brochure, PDF p. 1; dark/grey version | [Artwork](../../../public/identity-collected/capital-health-region/capital-health-region-2000-dark-grey.svg) |
| Capital Health Region | Spring 2000 regional services plan, back cover, PDF p. 12; dark/white version | [Artwork](../../../public/identity-collected/capital-health-region/capital-health-region-2000-dark-white.svg) |
| South Fraser Health Region | April–May 2001 newsletter, PDF p. 1; stacked black mark and “Healthy Individuals / Healthy Communities” tagline | [Artwork](../../../public/identity-collected/south-fraser-health-region/south-fraser-health-region-stacked-tagline-2001.svg) |
| Northern Interior Regional Health Board | July 2001 annual report, PDF p. 8; blue emblem and full outlined name | [Artwork](../../../public/identity-collected/northern-interior-regional-health-board/northern-interior-regional-health-board-blue-2001.svg) |

The Land and Water BC extraction omits an invisible white-on-white tagline and a separate page rule. Its description therefore claims only the visible emblem and name. The Capital dark/white SVG retains its original dark lettering and white bands. Its gallery preview is a crop of the source page with the original orange texture, because a uniformly dark backdrop obscures the dark lettering. The transparent SVG download contains no background image. This preview has its own checksum and is not counted as another recovered logo.

## Additional raster specimens

These remain identified as raster in both the register and gallery. Original pixel dimensions, compression artefacts, scan damage and source clipping are preserved. Decoding a PDF image mask, restoring its original soft mask or applying its original placement orientation does not make it vector artwork.

| Organization | Additional specimens | Files |
|---|---|---:|
| Capital Health Region | January 1999 newspaper advertisement; October 1999 letterhead; January 2000 original colour image; September 2000 original greyscale image | 4 |
| Vancouver/Richmond Health Board | October 2001 official-mark journal specimen; Fall/Winter 2001 *Visions* specimen; April 2001 original colour image | 3 |
| South Fraser Health Region | July 2001 original horizontal colour logo with tagline | 1 |
| North Shore Health Region | Reversed image and original soft mask preserved in a later trail donor-panel PDF | 1 |
| Simon Fraser Health Region | Original website colour JPEG and January 2001 newsletter monochrome bitmap, recovered in the fourth pass | 2 |

### Newly recovered in the fourth pass: Simon Fraser

- **[Original website JPEG](../../../public/identity-collected/simon-fraser-health-region/simon-fraser-health-region-original-web-colour-2001.jpg): 435 × 219 pixels.** The historical About page links the original file. Its archive capture is August 25, 2001; the JPEG is retained byte for byte. That date is a capture date, not a publication or adoption date. [Archived original](https://web.archive.org/web/20010825010851id_/http://sfhr.com/inter_ccaboutsfhr/images/sfhr_logo2co.jpg).
- **[Original monochrome bitmap](../../../public/identity-collected/simon-fraser-health-region/simon-fraser-health-region-continuum-2001-monochrome.png): 1,943 × 990 pixels.** This is image object 256 from PDF p. 12 of the January 2001 *Continuum*. Its one-bit mask was decoded and mapped to the document’s black ink on white without resampling. The printed issue date takes precedence over a stale April 2000 PDF template-title field. [Archived newsletter](https://web.archive.org/web/20030527161646id_/http://www.sfhr.com/ccregionalnews/Newsletters/January%202001%20Continuum.pdf).

Both are additional specimens for an already represented body. Neither closes its vector gap. The newsletter extraction has a [pixel and placement proof](evidence/simon-fraser-continuum-raster-proof.json) and a [rendered source header](evidence/simon-fraser-continuum-jan2001-page12-header.png).

## Continued search and unresolved leads

The fourth pass actually revisited **21 distinct bodies: 8 Crown bodies and 13 health bodies**. The health work covered nine councils and four regions. The [full checklist](CHECKLIST.md) retains all 133 original rows, with explicit revisit flags; carried-forward results are not represented as fresh searches. [Detailed outcomes and queries](search-pass-4.json) distinguish inspected source pages, indexed text, unavailable downloads and duplicate material.

The most useful remaining routes are:

- **BC Development Corporation, BC Enterprise Corporation and BC Place Ltd.:** the [BCEC records schedule](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/services-policies-for-government/information-management-technology/records-management/orcs/bcec_orcs_170469.pdf), PDF pp. 9–10, identifies creator subject/file indexes in accession **93-4720, boxes 1–4**, and **90-1769, box 24**, under classification **20000-02**. These are index locations, not confirmed boxes of logo art. They could locate final corporate-marketing files under **20000-20**; item-level records and the artwork remain unavailable.
- **BC Harbours Board:** a [Library and Archives Canada finding aid](https://data2.archives.ca/pdf/pdf002/66-11_43861_open.pdf), PDF p. 7, identifies **Ports Canada, RG 66, accession V-85-86/395, volume 14 (499999)**, “British Columbia Harbours Board,” 1967–1970. The finding aid was inspected; the underlying correspondence was not. The separately inspected Cuthbert correspondence uses provincial ministry letterhead.
- **Metro Transit Operating Company:** [UBC’s additional-map holdings](https://ubc-lib-geo.github.io/development-of-vancouver-maps/additional-maps.html) identify its **1981 Transit Guide for Vancouver**, call **624.9gm Vancouver 1981 B**, and **1982 downtown guide**, call **624.9gm 1982 M**. These catalogue records do not supply inspectable artwork.
- **Central Cariboo Chilcotin Health Council:** an indexed *Patients First* appendix identifies **submission 33**, Tracy MacDonald for the council, October 19, 2001. The original brief remains uncollected.

Several plausible routes were narrowed or rejected. The Toll Authority hit in the 267-page TRA-2018-88109 packet is ordinary table lettering on PDF p. 185, and every page is a flattened bitmap. Quesnel’s grounded historical `qdchc.com` route yielded only an archived generic server “Under Construction” page. The WLC seal-field document is an alternate-access duplicate of previously inspected material. Simon Fraser’s recovered 205-page health profile and 12-page newsletter both use bitmap corporate art; other linked report URLs remained unavailable. No inaccessible document is counted as visually inspected.

## Relationship to open PR #9

[PR #9](https://github.com/ahzs645/PofBC/pull/9) already proposes a North Shore November 1999 recruitment-ad crop from the same journal page as one file in the earlier standalone research package. That duplicate crop is **excluded** here and recorded under `excludedDuplicateSpecimens` in the source register. Its Toll Authority, Ferry Authority, Urban Transit Authority and Simon Fraser letterhead specimens are also not recounted as new discoveries.

This follow-up is independently based on current `main`. It leaves the original acquisition inventory and earlier 35-vector register intact. If both PRs are merged, retain both source inventories and regenerate `src/gallery/collectedData.js` with `npm run build:collected-marks`; this incorporates both sets without choosing one generated file over the other.

## Gallery integration and verification

`scripts/build-collected-marks.mjs` reads this additional register, verifies files against their checksums, rejects unknown body IDs and duplicate asset IDs/file paths, and keeps detailed extraction evidence outside the gallery bundle. Adding an actual specimen changes a formerly unresolved body to `asset-collected`; it does not imply that a vector was found. The Capital source preview has a separately verified checksum.

Validation commands:

```sh
npm run build:collected-marks
node --test src/gallery/collectedCollections.test.js src/gallery/collections.test.js src/gallery/collecting.test.js src/gallery/wanted.test.js
npm run build
git diff --check
```

The gallery-index build, four listed test files, asset/proof checks and whitespace check pass. After integrating PR #15, the new government-panel logo cards were also checked: all eight vectors appear for the seven upgraded bodies, Capital uses its source-page preview, and Simon Fraser and North Shore remain excluded from the vector-only cards. The public dependency submodules were initialized and the `json-url` dependency built successfully. The full `npm run build` was attempted but stops at the existing Helvetica prerequisite: this Linux workspace has no licensed `/System/Library/Fonts/Helvetica.ttc`. No substitute font or build bypass was introduced. The repository’s existing Pages workflow uses macOS and checks for that font before building. Full production-build success is therefore not claimed by this local validation.

All document dates and archive captures are specimen sightings. They do not establish first use, adoption dates or complete usage periods. Research observation dates use October 30, 2026 in America/Creston; older supporting artifacts may retain their original UTC timestamps. Full publications are linked and checksummed rather than copied into this repository.
