# Institutional and public-body arms acquisition

Acquired 16 November 2026 for the PofBC Arms view. This directory supplements the broader Canadian Heraldic Authority register download; it does not duplicate the register image collection.

## Deliverables

`manifest.json` is the integration record. It contains **21 artwork files for 14 holders**, including **7 true vector SVGs**. Eighteen artworks are eligible to represent a holder or a historical entry; the Langara watermark, UFV ceremonial seal, and Saanich Police wordmark lockup are supplemental only. Twenty-nine source documents and captured pages are recorded separately with URLs, sizes and SHA-256 hashes.

The manifest distinguishes complete achievements, shields with mottoes, badges, seals and lockups. `is_vector` is based on the actual SVG contents, not the extension. `primaryEligible` describes suitability as an arms-gallery illustration; it is not a copyright permission statement.

### Verified vector artwork

| Holder | File | Illustration and source |
|---|---|---|
| University of Northern British Columbia | `derived/unbc-full-arms-monochrome-source.svg` | Full achievement, 972 paths, no images; February 2020 official standards, PDF page 17. |
| Kwantlen Polytechnic University | `derived/kpu-full-arms-colour-source.svg` | Full colour achievement, 1,391 paths, no images; official 2020 symbolism PDF, page 1. |
| University of Victoria | `derived/uvic-full-arms-colour-source.svg` | Full colour achievement, 787 paths, no images; spring 2026 convocation book, PDF page 10. |
| Simon Fraser University | `originals/sfu-full-arms-colour-existing.svg` | Current three-book shield and motto, 200 paths, no images. Recovered unchanged from an existing supplied repository source, itself extracted from the May 2015 official brand guidelines. |
| Simon Fraser University | `derived/sfu-full-arms-monochrome-source.svg` | Current three-book shield and motto, 201 paths, no images; June 2021 convocation book, PDF page 92. |
| College of the Rockies | `derived/cotr-arms-colour-source.svg` | Shield and motto, 119 paths, no images; 2022 convocation cover. Original turquoise background retained. This is a print colour treatment, not a newly established heraldic design. |
| Vancouver Police Department | `derived/vancouver-police-badge-monochrome-source.svg` | Navy badge, 264 paths, no images; 2022–2026 strategic-plan cover. The separate photographic page background was removed while retaining the badge's original paths. |

No artwork was drawn, synthesized or traced. PDF-derived SVGs retain source vector paths and the source documents are included. Crop coordinates and original PDF pages are recorded in `derived-vectors.json` and `vpd-derived-vector.json`. All seven vectors were rendered and visually checked. Off-crop image removal for the UNBC monochrome and UVic colour exports was verified to leave the cropped render pixel-identical at 2× resolution.

## Historical distinctions

**Simon Fraser University:** both designs are acquired. The one-book shield, flanked by crosses, is the 1965 university design, now used by the Office of the Chancellor. Its community rendition is `originals/Simon_Fraser_University_Achievement.png` and is associated with [CHA project 1147](https://www.gg.ca/en/heraldry/public-register/project/1147). The three-book design is the 2007 change, represented by official colour and monochrome vectors and an official PNG; it is associated with [project 1393](https://www.gg.ca/en/heraldry/public-register/project/1393). The university's [official symbols page](https://www.sfu.ca/convocation/about/symbols.html) explains the change. Colour and monochrome versions of the same design are not separate historical grants.

**Vancouver Island University / Malaspina:** the acquired community full achievement is associated with the 2018 VIU confirmation, [project 3027](https://www.gg.ca/en/heraldry/public-register/project/3027), and the 1995 Malaspina grant, [project 529](https://www.gg.ca/en/heraldry/public-register/project/529). The [university logo guide](https://adm.viu.ca/marcomm/logo-guide) says the arms were adopted on 20 May 1995. A name confirmation should not automatically be shown as a redesign.

**Kwantlen:** retain both [older project 834](https://www.gg.ca/en/heraldry/public-register/project/834) and the [2008 confirmation, project 1338](https://www.gg.ca/en/heraldry/public-register/project/1338). The acquired [official symbolism PDF](https://www.kpu.ca/sites/default/files/KPU-Coat-of-Arms.pdf) provides the full vector achievement. CHA project 834 dates the original grant to May 4, 1999. The symbolism PDF records the presentation ceremony on June 4, 1999. These are distinct dates and the presentation should not replace the letters-patent date.

**Royal Roads:** the [current official history](https://www.royalroads.ca/about/history-traditions/our-coat-arms) agrees with the CHA grant date of 24 March 1998. The earlier 1997 date appearing in a convocation account should not replace the grant date. The university identifies the motto's language as SENĆOŦEN and attributes the design to Charles Maier.

**University of Victoria:** the complete vector is a 2026 printed rendition of the registered arms. The 2001 CHA registration date, 1961 Victoria College grant, and the university's 1963 adoption/history should remain distinct rather than being treated as three presumed redesigns.

**Surrey Police:** the acquired official badge release is documentary evidence, with no badge illustration in the PDF. It reports Royal Assent on 26 March 2021 and identifies the Coast Salish eye artist as Leslie Wells of Semiahmoo First Nation. That is distinct from the October 2021 registration date. Root acquisition supplies the actual register artwork.

## Additional institution

**Douglas College** is absent from the baseline CHA-based holder list but has a documented full coat of arms and an acquired official image. The [college's official page](https://www.douglascollege.ca/about-douglas/campus-information/coat-arms) dates the unveiling to **21 January 2020**, at its 50th-anniversary celebration, and identifies **Carrielynn Victor**, Coast Salish artist from Cheam First Nation, as designer. `originals/douglas-official-art.jpg` is the official published version. The filename refers to a calligraphy update, whose date is unstated. No CHA registration number or grant date has been invented.

## Other artwork

Official original images were acquired for College of New Caledonia, UFV, Port Moody Police, SFU and Douglas. The full-colour UNBC JPEG was extracted directly from its official standards PDF at 1,192 × 1,243 pixels. UFV's 2019 convocation book also supplies an original 771 × 835 JPEG of the same granted design. These are original embedded raster files, not upscaled screenshots.

Commons originals provide additional full-achievement or shield renditions for historical SFU, UNBC, Royal Roads and VIU. Their exact asset URLs, baseline attribution and licences are retained in the manifest. Fresh Commons metadata requests were rate limited; original file downloads succeeded. The attribution metadata is explicitly identified as carried forward from the earlier collection.

## Excluded and unresolved items

`UBC_COA2.svg` contains **one embedded bitmap and no vector paths**. It is retained solely as a rejected candidate and excluded from `assets`; it is not a vector upgrade to the existing UBC shield.

The Langara policy artwork is a pale watermark and is supplemental only. UFV's seal and the Saanich Police badge-plus-wordmark lockup are also supplemental; they must not be mistaken for isolated full arms.

Public vector masters were not found for every baseline institution or public body. Some accessible PDFs contain raster arms alongside vector text, which is insufficient to call the arms vector. Langara's old graphic-standards links returned 404, Emily Carr's brand PDF and image returned 403, and an older Okanagan standards link returned 503. These attempts are preserved in `failed_acquisitions`. The root CHA acquisition supplies authoritative raster artwork for those baseline entries.

## Provenance and rights

Every usable artifact has a local path, SHA-256, source URL, format, dimensions or SVG structural check, and relevant registration identifiers. Official institutional artwork is not presumed openly licensed merely because it can be downloaded. Artist attribution is supplied where the source identifies one; otherwise the manifest names the publishing institution and records that an individual artist was not credited in the downloaded source. Commons licence statements and authors are preserved per the prior metadata.

`build_manifest.py` rebuilds the integration manifest from the acquired files and extraction records. `probe*.py` and `probes*.json` preserve source-discovery results. Captured HTML and rendered verification previews are under `evidence/`.
