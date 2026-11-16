# Municipal arms acquisitions

Retrieved 16 November 2026 for PofBC's arms collection, compared with baseline commit `8f95bd6793e1e88e491db66ee3218148c37a17e4`.

## Acquired artwork

`manifest.json` is the stable machine-readable handoff: **14 artwork files: 9 SVG vectors and 5 raster drawings**, plus five supporting official PDFs. Source URLs, exact source licenses, authors, SHA-256 checksums, register matches, design/registration/drawing dates, and dating caveats accompany every artwork. Files were downloaded or extracted from source PDFs; none were newly traced or generated.

| Municipality | Artwork | Meaning for the collection |
|---|---|---|
| Abbotsford | SVG shield | Arms of the City (1995), not the former District's separate 1993 record; shield only. |
| Burnaby | SVG full achievement | Independent 2012 drawing of the 1991 arms; 2005 City registration is a separate event. |
| Delta | SVG full achievement | Independent 2026 drawing; arms recorded in Scotland in 1988, Canadian records in 2005 and 2018. |
| Kamloops | SVG full achievement | Independent 2026 drawing; College of Arms record 1981, Canadian registration 1992. |
| Parksville | SVG full achievement | Independent 2026 drawing of the 2010 arms, plus two official grant reproduction PDFs. |
| Kelowna | SVG full achievement | Independent 2023 drawing of the 1954 arms; Canadian registration 2001. |
| Vancouver | SVG full achievement and SVG shield | Independent drawings of the 1969 arms; Canadian registration in 2025 is not their design date. |
| Langley (City) | SVG full achievement | Independent 2022 drawing of the City's 1995 arms. It is not the Township's arms. |
| Victoria | Two PNG drawings | Two renderings of the 1962 arms. A new heraldic design in 2005 is not established. |
| Vancouver history | Three PNG drawings | Official 2006 council report reproductions of the 1886–1903 seal, 1903–1969 arms, and 1969 arms. |

All nine SVGs have real vector geometry and no embedded `<image>` elements or scripts. They render successfully in Inkscape; an overview is in `municipal-acquisition-contact-sheet.png`. A generic PDF SVG renderer initially rendered some CSS-based fills incorrectly, so the final overview uses Inkscape output. Original SVG files were preserved unchanged.

## Timeline evidence

The [City's 2006 visual identity report](https://council.vancouver.ca/20060718/documents/a15.pdf), PDF page 20, explicitly illustrates three Vancouver design stages. Original embedded bitmaps were extracted losslessly with image XRefs 516, 517 and 518. Their low source resolution is retained and documented. The report identifies the 1969 grant date as 31 March 1969; the [2025 CHA record](https://www.gg.ca/en/heraldry/public-register/project/3711) is a registration of those earlier arms.

The first seal's start date needs a caveat. The council report labels it 1886–1903, while [Early Vancouver, volume 4](https://archives.vancouver.ca/projects/EarlyVan/SearchEarlyVan/Vol4pdf/MatthewsEarlyVancouverVol4_TheFirstCoatOfArms.pdf) says about 1888–1903. [Volume 7](https://archives.vancouver.ca/projects/EarlyVan/SearchEarlyVan/Vol7pdf/MatthewsEarlyVancouverVol7_TheFirstCoatOfArms.pdf) gives last use of the old seal on bylaws as 16 February 1903 and first use of the replacement as 23 February 1903. The manifest preserves this discrepancy.

For Victoria, [CHA project 502](https://www.gg.ca/en/heraldry/public-register/project/502) describes the 2005 action as registration and identifies the original College of Arms record as 10 May 1962. The Commons image filename `1962–2005` is not enough to assert a formal redesign in 2005.

Parksville's [official explanation](https://www.parksville.ca/cms.asp?wpID=348) says the shield builds on an emblem used since 1977, while the grant is dated 15 April 2010. A verified original 1977 drawing was not acquired in this pass.

## Credits and source status

The SVGs are independent Wikimedia Commons emblazonments, not municipal vector masters. Credits are Ssire (Abbotsford), Mathieu Chaine (Burnaby), ConfidentBobcat and credited component authors (Delta, Kamloops, Parksville), ProfAuthor and credited component authors (Kelowna), Jack Ryan Morris (Vancouver full achievement), Zorlot (Vancouver shield), and IndysNotHere (Langley). The exact selected Creative Commons license and component credits are retained per file. Commons file-description wikitext was retained where the API lacked a machine-readable author.

Official PDF illustrations are labelled documentary references with no open license established; they are not mislabeled CC-licensed. The acquired Commons Victoria PNGs retain the Commons public-domain claim without treating that as an independent legal determination.

## Exclusions and limits

- A Commons file titled “Unofficial seal of the City of Vancouver, BC, Canada” is a modern circular composition incorporating current arms. Visual inspection rejected it as an 1886 historical seal; it is not in the deliverable artwork set.
- Victoria, Australia SVGs and Richmond, Quebec SVGs were excluded as different places.
- Broad Commons place-name searches hit rate limits. `municipal-vector-search.json` retains successes and failures; this is not a claim that every possible municipal vector has been exhausted.
- No additional municipal arms vectors were found among the existing repository's `public/identity-collected` and `public/identity-expanded` files using place-name/arms/crest filename searches. Health-region identity files and Metro Vancouver logos are different assets and were excluded.
- Root's separate CHA acquisition covers current official registry images; this folder supplements that coverage with vectors and historical drawings.

## Supplements

`port-moody-manifest.json` adds three official Port Moody images from its annual report and meeting minutes, filling the absence of a published image in CHA project 169. The complete achievement is distinct from the simplified city arrangement without the pigeon and motto; these are not treated as successive grants.

`historical-manifest.json` adds five dated documentary extracts from Robert D. Watt, *Coats of Arms and Logos: Visual Identity for Communities in the New Millennium*, published in 2000, printed pp. 681–711 of [the official Italian State Archives proceedings](https://dgagaeta.cultura.gov.it/public/uploads/documents/Saggi/5508125695520.pdf). These are Burnaby's early seal, Surrey's early seal, Vancouver's circa 1889 seal specimen, the Township of Langley's 1912–1989 emblem, and Karen Bailey's commissioned 1988 Port Moody drawing. The original source volume is retained. Each extraction records PDF and printed pages, figure number, image XRef, native pixel crop, and checksums. No scaling or cleanup was applied.

Together the three stable manifests contain **22 artworks: 9 vectors and 13 raster specimens**, plus **9 distinct supporting PDFs**. Only manifest-listed artworks are deliverable acquisitions; other downloaded files and previews are working evidence. The Port Moody 1988 scan is a more detailed documentary specimen but has weak tonal reproduction, so the colour annual-report example remains useful alongside it.
