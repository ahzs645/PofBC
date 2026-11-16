# Provincial arms and Lieutenant Governor: acquired vector supplement

Acquired 16 November 2026 against PofBC baseline `8f95bd6793e1e88e491db66ee3218148c37a17e4`.

This supplement adds **10 artwork records: nine genuine SVG files and one 3072 × 2304 photograph**. Two of the SVGs also have vector PDF excerpts. The records supplement the repository's existing 32 provincial specimens; they are not ten newly discovered official designs.

The machine-readable record is `manifest.json`. Every record includes its absolute local path, relative path, entity and holder id, element type, source page and asset URL, credit, licence as reported by the source, SHA-256, date meaning, and related Canadian Heraldic Authority register id.

## Acquired artwork

| File in `new-assets/` | What it depicts | Date interpretation | Source/credit |
| --- | --- | --- | --- |
| `bc-1895-fenn-o-manic.svg` | Full 1895 arms | Provincial adoption 19 July 1895; drawing made in 2020 | [Fenn-O-maniC, Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Coat_of_arms_of_British_Columbia_(1895).svg), CC BY-SA 4.0 |
| `bc-1987-leonid2.svg` | Full current achievement in colour | 1987 augmentation; drawing first uploaded in 2015, corrected in 2021, optimized in 2022 | [Leonid 2 and subsequent contributors](https://commons.wikimedia.org/wiki/File:Coat_of_arms_of_British_Columbia.svg), CC BY-SA 3.0; GFDL also offered |
| `bc-1906-shield-fry1989.svg` | Shield only | 1906 grant; 2010 drawing | [Fry1989](https://commons.wikimedia.org/wiki/File:Arms_of_British_Columbia.svg), source labels PD-Canada |
| `bc-1906-shield-zorlot.svg` | Alternative shield-only rendering | 1906 design; 2009 drawing | [Zorlot](https://commons.wikimedia.org/wiki/File:Blason_ca_Colombie-Britannique.svg), CC BY-SA 4.0; other licences also offered |
| `bc-1987-monochrome-official-sample.svg` | Official monochrome reproduction specimen | 1987 achievement; guide undated | Government of British Columbia, [emblems guide](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/celebrating-british-columbia/symbols-of-bc/bc-emblems-set.pdf), page 3, specimen F; SAMPLE retained |
| `bc-1987-reverse-official-sample.svg` | Official white-on-blue specimen | A reproduction treatment of the same achievement | Same guide, page 3, arms portion of specimen G; SAMPLE and blue background retained |
| `bc-lg-flag-1871-1906.svg` | Historical Lieutenant Governor flag with royal-crest badge | Historical period attributed by source; modern 2018 drawing | [TilmannR](https://commons.wikimedia.org/wiki/File:Flag_of_the_Lieutenant-Governor_of_British_Columbia_(1871%E2%80%931906).svg), CC BY-SA 4.0 |
| `bc-lg-flag-1906-1982.svg` | Historical Lieutenant Governor flag with provincial shield and motto | Historical flag period; modern 2018 drawing with 2019 correction | [TilmannR, Tcfc2349 and credited source contributors](https://commons.wikimedia.org/wiki/File:Flag_of_the_Lieutenant-Governor_of_British_Columbia_(1906%E2%80%931982).svg), CC BY-SA 4.0 |
| `bc-lg-badge-1982-fry1989.svg` | Standalone current flag emblem | Emblem approved in 1982; registered in 2005; source derivative made in 2010 | [Fry1989 and credited source contributors](https://commons.wikimedia.org/wiki/File:Badge_of_the_Lieutenant_Governor_of_British_Columbia.svg), CC BY-SA 3.0 |
| `bc-1895-window-makaristos.jpg` | Older arms in stained glass | 1895 design family; photograph dated 14 December 2007; object date not independently supplied by file page | [Makaristos](https://commons.wikimedia.org/wiki/File:BC-Arms-older.jpg), public-domain dedication |

## What belongs on the timeline

The [official provincial history](https://www2.gov.bc.ca/gov/content/governments/celebrating-british-columbia/symbols-of-bc/coat-of-arms) identifies three substantive stages: the 1895 provincial adoption, the 1906 grant of shield and motto, and the 1987 completion of the achievement. The [Canadian Heraldic Authority's 17 April 1990 record](https://www.gg.ca/en/heraldry/public-register/project/1406) registers pre-existing grants; it does not introduce a fourth design. The [Legislative Assembly](https://www.leg.bc.ca/learn/discover-your-legislature/provincial-and-parliamentary-symbols/bc-coat-of-arms) states that the arms have not changed since 1987.

The 2009, 2010, 2015 and 2020 dates on the community files are dates of digital drawings. Keep them in specimen labels while grouping them under the heraldic design they depict. A different shield shape, gradient or line weight does not establish a new grant.

The Lieutenant Governor has a separate sequence. The current flag emblem was approved **1 February 1982** and registered **15 March 2005**, according to [CHA project 456](https://www.gg.ca/en/heraldry/public-register/project/456). Keep its flags and badge under holder `lieutenant-governor`, apart from the Province's arms sequence.

## Vector verification and visual review

All nine SVGs parse as XML and contain real vector paths. None contains an embedded raster image, a script, a foreign object, an external rendering reference or an event handler. Their file hashes, path counts and checks are in `validation/svg-audit.json`. A file-by-file SHA comparison found no exact copies among existing repository SVG/JPEG/PDF assets.

All nine were rendered in Inkscape and checked together in `validation/contact-sheet.png`. The artwork is complete within its source canvas. The Zorlot shield uses a translucent radial-gradient overlay, which the preliminary MuPDF SVG renderer displayed incorrectly as solid black; Inkscape renders the original correctly. The final contact sheet uses Inkscape output. The official monochrome SAMPLE treatment also needed this renderer to reproduce transparency faithfully.

The two official SVG excerpts preserve the source geometry and SAMPLE watermark. They were made by clipping page 3 of the original PDF and exporting its vector content. Invisible raster elements from elsewhere on the page were excluded; before/after SVG renders were byte-identical. `validation/vector-extraction-validation.json` records that comparison. The original guide remains at `sources/bc-official-emblems-set.pdf`; the cropped PDF copies remain alongside the SVGs. This is vector extraction, with no tracing or reconstruction.

## Fidelity and integration notes

- **Community drawings need their credits and labels.** The 1895 and current full-colour SVGs are modern community renderings. They are not official provincial reproduction masters, and their artist-specific proportions should not be presented as original 1895 or 1987 source drawings.
- **Shields are partial emblems.** Both `bc-1906-shield-*` files omit the motto, crest, supporters and compartment. One source page loosely calls the object a crest; the manifest corrects the visible type to shield. Display the word “Shield” beside either one.
- **The official specimens remain watermarked.** They upgrade the existing `guide-monochrome` and `guide-reverse` PNG references. The guide says reproduction masters are not publicly downloadable; the extracted specimens do not remove that condition or establish a new licence.
- **The historical flags are contextual additions.** Their broad periods are supported by their source files and historical flag literature. The acquired SVGs do not prove every crown variation used within those periods.
- **Preserve separate object and image dates.** The new stained-glass photo improves reference resolution; its 2007 date belongs to the photograph. It is not an introduction date for the arms or a newly dated window.

## Remaining gap

No freely downloadable, independently sourced vector of the full **1906–1987 achievement** was located. The two shield-only SVGs do not close that gap. The repository already has dated printed and photographed specimens of those older full arms, and those remain the evidence for any future reconstruction. This supplement does not trace them or replace them with invented artwork.

## Files intended for integration or the download pack

Use `manifest.json`, this README, the files named under `new-assets/`, and the referenced source guide/metadata pages. `validation/` holds useful review evidence. `investigation/` contains intermediate downloads, including duplicates of existing sources and a government publication wrapper that did not contain the requested historical text; those are excluded from the artwork counts and should not be treated as acquired artwork.
