# Historical B.C. health logos: vector findings

Research and extraction completed 22 November 2026.

## Result

**Original Vancouver/Richmond Health Board vector artwork was recovered from two historical publications.** South Cariboo and Greater Trail remain without a verified original vector in the sources inspected.

| Organization | Result | Useful files |
| --- | --- | --- |
| Vancouver/Richmond Health Board | Original two-colour and single-colour vectors recovered | Three SVGs, three vector PDFs, PNG previews, source crops and original publications |
| South Cariboo Community Health Council | No original vector found after inspecting 26 unique archived PDFs | Existing green logo, existing black emblem, newly recovered black-and-gray complete logo, research evidence |
| Greater Trail Community Health Council | No original vector found in the surviving website files inspected | Unchanged transparent 205 x 105 GIF and archive research evidence |

## 1. Vancouver/Richmond: recovered vectors

The files are in `Vancouver-Richmond/recovered-vectors/`.

| Base filename | Artwork | Formats |
| --- | --- | --- |
| `VRHB-original-colour-lockup` | Original red-and-purple emblem, full name and tagline | SVG, PDF, PNG |
| `VRHB-original-colour-emblem` | Original red-and-purple emblem by itself | SVG, PDF, PNG |
| `VRHB-original-purple-lockup` | Original single-colour purple emblem, full name and tagline | SVG, PDF, PNG |

### Original sources and dates

**Colour artwork:** [Take Care, archived original PDF](https://web.archive.org/web/20030426095928id_/http://www.vcn.bc.ca:80/vrhb/Down_Loads/CaregiverSupport/TakeCareHandBook.pdf), PDF page 1. Page 2 states that the handbook was revised in 2000; the back cover has form code HED2050 00/08. Its PDF creation metadata is 28 September 2000. The 26 April 2003 archive capture is a preservation date, not the publication or logo-adoption date.

**Purple artwork:** [Directional Plan 2000-2003, archived original PDF](https://web.archive.org/web/20040107163909id_/http://www.vcn.bc.ca:80/vrhb/Down_Loads/VRHB_Health_Plans/Directional_Plan/VHRB_Directional_Plan.pdf), PDF page 1, upper-left header. Its PDF creation metadata is 29 February 2000, with a later modification in July 2001. The 7 January 2004 archive capture is a preservation date.

Both complete source PDFs are preserved in `Vancouver-Richmond/archive-candidates/`. The source-crop PDFs and PNGs retain the original page appearance for comparison.

### Why these qualify as original vectors

The logo regions contain original PDF drawing operations for the emblem, fine brush details, lettering and tagline. The lettering was already outlined in the publications. The extraction isolates those operations while preserving their coordinates, curve control points, fills, strokes and colour resources.

All three exported SVGs contain paths, with **zero embedded images, zero live text elements and no external resource dependencies**. The extracted vector PDFs likewise have no image objects or font dependencies. The files are not bitmap wrappers or reconstructed lettering.

An independent review found no missing details or clipping. At an 8x comparison render, the isolated colour logo and colour emblem PDFs were pixel-identical to crops rendered directly from the original source. SVG rendering differs slightly because of colour conversion and antialiasing. Detailed checks, file hashes and crop coordinates are in `vector-provenance.json` and `Vancouver-Richmond/independent-review.json`.

### Original colours and backgrounds

The two-colour source explicitly names **PANTONE 1797 CVC** for red and **PANTONE 2627 CVC** for purple. Those names and source colour definitions remain in the extracted PDFs. The SVGs use RGB conversions for screen display; their RGB values are not a newly established print colour standard.

The colour artwork retains the source's white knockout shapes in the brush details. Its PDF and SVG have no added page-sized background, but those white shapes remain white. The single-colour purple version has an open heart through which the background shows; its original pale cream publication background is retained only in the source crop. These are two distinct source treatments.

`Vancouver-Richmond/extract_vrhb_vectors.py` reproduces the extraction from the two included source PDFs using PyMuPDF. Run it from that folder with Python and PyMuPDF installed. It regenerates the vector files and basic provenance; the independent review is supplied separately.

## 2. South Cariboo: broader search and a new raster specimen

The two historical website locations yielded 27 successful PDF URL entries. Download checksums identify **26 unique PDFs, containing 149 unique pages**. Graphics were inspected across every page, every cover was visually checked, and pages with complex drawing objects were reviewed separately.

The [1999 health plan](https://web.archive.org/web/20000915110312id_/http://www2.bcinternet.net:80/~100mile/health/healthplan99.pdf) contains the green full logo as a **315 x 141 JPEG**, image object 8 on PDF page 1. The document has no vector drawing paths. The other inspected documents contain text, rules, tables, outlined headings or a DRAFT watermark, with no vector tree emblem.

**Additional original specimen recovered:** `South-Cariboo/South-Cariboo-original-monochrome.jpg`, a **200 x 100 JPEG** containing the black-and-gray trees and complete stacked name. It appears in an opening-ceremonies thank-you advertisement.

- [Recovered original JPEG](https://web.archive.org/web/20040916225305id_/http://www.100mile.com:80/health/thankyou/image11.jpg)
- [Supporting 2001 page](https://web.archive.org/web/20010718201751id_/http://www.100mile.com:80/health/thankyou/)
- [Matching earlier 2000 HTML](https://web.archive.org/web/20000915110316id_/http://www2.bcinternet.net:80/~100mile/health/thankyou.html)

The image payload is verified from a September 2004 capture. The earlier HTML references the same filename, but that does not independently date the recovered image bytes. This is an additional monochrome specimen, with lower native resolution than the green logo.

The original 239 x 258 black website emblem and the green full logo already preserved by PofBC are also included unchanged. The linked `nominations2001.pdf` could not be recovered and was not inspected. Archive indexes, download manifest and graphics inspection results are in `South-Cariboo/evidence/`.

## 3. Greater Trail: original GIF remains the best recovered source

The [original website logo](https://web.archive.org/web/20010606033527id_/http://www.trailnet.bc.ca:80/~trh/GTCHC_logo.gif) is a **205 x 105 GIF**, preserved unchanged as `Greater-Trail/Greater-Trail-original-2001.gif`.

The archive inventory returned **72 successful distinct URL keys**: 57 HTML pages, 13 raster images and two Dreamweaver templates. Links from 34 archived HTML pages and the templates were inspected. No vector master or logo-bearing vector PDF was recovered.

Two later pages reference alternative logo filenames, but those image targets were unavailable. The original annual chair's report is HTML and does not link drawing files. These limits are recorded in the supporting archive files.

The GIF has a transparent background. Its transparent palette entry is gray, which can look like a gray background if transparency is discarded during conversion. The unchanged GIF is therefore preferable to a flattened RGB copy.

## Interpretation for the gallery

Vancouver/Richmond can now be classified as having verified original vector artwork, with two documented full-logo treatments and a separate emblem extraction. South Cariboo and Greater Trail should retain their raster/original-source status and their unresolved vector status. This package does not change the website or repository.

The unsuccessful searches are bounded findings about the material inspected. They do not establish that original print or design masters never existed. `findings.json` records the resulting organization-level status, and `SHA256SUMS.txt` checksums the supplied package contents.
