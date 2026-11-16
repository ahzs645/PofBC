# Acquired identity artwork — 15 November 2026

This additive acquisition contains **40 identity subjects and 43 gallery artworks: 21 native vectors and 22 published rasters**. The gallery files and their retained source files occupy approximately 3.6 MB. A second official encoding of the TransLink Leaper is offered as an additional source download, not counted as another identity.

The complete inventory and provenance are in [assets-manifest.json](assets-manifest.json). The generated application data is `src/gallery/expandedIdentityData.js`. Original accepted collections are unchanged.

## Coverage

| Family | Added subjects |
| --- | --- |
| Transit | TransLink corporate Leaper; separate public-facing T marker; Coast Mountain Bus Company; West Coast Express; Metro Vancouver Transit Police; SkyTrain; HandyDART; Compass |
| Regional government | Metro Vancouver, with separate full-logo and wordmark examples |
| Liquor distribution | Liquor Distribution Branch; BCLIQUOR; BC Cannabis Stores; BC Cannabis Wholesale; LDB Wholesale Operations |
| Culture | Creative BC, including its provincial funding lockup; BC Arts Council funding lockup; Science World |
| Emergency communications and ferries | E-Comm 9-1-1; BC Ferry Authority; BC Ferries Commissioner |
| Regional development | Northern Development Initiative Trust; Island Coastal Economic Trust; ETSI-BC; Nechako-Kitamaat Development Fund Society |
| Administration and regulators | BC Pension Corporation; Technical Safety BC; Land Title and Survey Authority; Consumer Protection BC |
| Commercial subsidiaries and venues | Powerex; PlayNow; Vancouver Convention Centre; BC Place |
| Specialist health | BC Women's Hospital + Health Centre; BC Centre for Disease Control; BC Emergency Health Services |
| Public institutions | UBC; SFU; UVic; UNBC; BCIT |

Collection IDs are `collected-` plus the explicit body ID in the manifest. T, SkyTrain, HandyDART and Compass are separate identity shelves with `graphNode: null`; their artwork does not create an organization in the government atlas. Current Technical Safety BC artwork is not evidence for the former BC Safety Authority identity.

Subjects without acquired artwork, including BCRTC, SeaBus, RapidBus, B-Line, Metro Vancouver Regional Parks, LandSure Systems and BC Children's Hospital, remain research leads in the subject registry. They are not counted as held merely because a related organization's artwork is present. BC Cancer's existing collection was not duplicated.

## Source fidelity

- **Website files:** original SVG, PNG and WebP bytes are retained. Source page, direct file URL, resolved URL, byte size, SHA-256, dimensions and observation date are recorded. Website upload-directory dates do not establish a logo adoption date.
- **Native publication components:** the T and SkyTrain components come from page 43 of TransLink's January 2026 *Active Transportation Promotion and Education Toolkit*. HandyDART comes from the cover of the November 2025 *Customer-First Plan*. Metro Vancouver examples come from its official one-page logo guidelines. Exact selected SVG path nodes, ancestor transforms and required definitions are retained after PDF conversion. Guides, neighbouring text and other brands are excluded. These are extracted components, not purported standalone official masters.
- **Official masters:** Creative BC, BC Arts Council, Science World and UBC artwork comes from the publishers' own downloadable logo packages. Complete, unchanged selected PDF or PDF-compatible Illustrator members are retained. The manifest records both the member checksum and the entire downloaded archive's checksum. SVG previews use PyMuPDF conversion; the original files remain downloadable. Conversion from PDF colour spaces may affect screen colour; no manual recolouring is applied.
- **Embedded raster artwork:** CMBC comes from the official December 2017 route 403 map, at its original 408 × 146 pixels. Its source PDF stores the image upside down and reverses it in the placement matrix; the extraction applies that lossless row reversal. WCE's 629 × 192 image, including its original alpha mask, comes from the cover of the September 2024 performance report dated 19 December 2024. Both remain raster assets.
- **Inline SVG:** BC Place's header logo is preserved exactly. BCIT's website SVG incorrectly uses `https://www.w3.org/2000/svg` as its namespace; only the namespace is changed to the standard `http://www.w3.org/2000/svg` for a standalone SVG. Its exact original fragment is retained separately.
- **Compass:** the website's C symbol is an 81 × 80 crop defined by the official stylesheet's sprite coordinates. The separate needle symbol is an unchanged PNG from TransLink's Compass Card page. Neither is presented as vector artwork.

Complete source pages are archived under `public/identity-expanded/_sources/` for publication extracts. Their checksums are distinct from the **full original document** checksum, original byte count and original page number recorded in the manifest. A retained page is a rewritten PDF container preserving the complete page content; it is not described as the unchanged full source document.

White artwork uses a dark display plate. Source colours, geometry and transparency are otherwise retained. No artwork is traced, typeset again, generated, or silently recoloured. A raster supplied inside a PDF is not labelled a vector.

## Rebuild and verification

After the project's normal `npm ci`:

```sh
node scripts/build-identity-expansion.mjs
node scripts/build-identity-expansion.mjs --check
```

The builder runs offline and verifies the 56 preserved files against recorded byte sizes and SHA-256 values. It checks unique subject and asset IDs, explicit graph mapping, complete source attribution, format/vector consistency, PNG/WebP signatures, parsed SVG structure, the SVG namespace, usable geometry, internal reference resolution, and the absence of active content, external resources, live fonts or embedded rasters in vector artwork. Source-authored duplicate IDs on unreferenced paths are preserved; referenced definitions must be unambiguous.

To reproduce the 14 derivative files from their local archived source pages, masters and fragments:

```sh
python3 scripts/extract-identity-expansion.py --check
python3 scripts/extract-identity-expansion.py
node scripts/build-identity-expansion.mjs --check
```

The extraction helper requires PyMuPDF and Pillow. This acquisition was verified with **PyMuPDF 1.26.6**; the version is recorded in the manifest. `--check` compares regenerated bytes with the accepted artwork without writing. Rendering differences between dependency versions should be reviewed, not accepted by silently replacing checksums. No network fetch occurs during these commands.

All 43 accepted artwork renders were visually inspected. SVGs were rendered with Sharp/libvips so internal SVG styles were respected. Review found and corrected the CMBC orientation and white-logo plate metadata. The following sheets include the full source artwork with padding; they are review illustrations, not substitute downloadable masters:

- [Artwork review 1](asset-review-1.jpg): TransLink, Police, creative and liquor identities, E-Comm, ferries and trusts.
- [Artwork review 2](asset-review-2.jpg): remaining trusts, regulators, subsidiaries, health, institutions and T marker.
- [Artwork review 3](asset-review-3.jpg): native transit/Metro components, CMBC/WCE rasters, official kit masters, BC Place, BCIT and Compass.

Only explicitly dated publications are given specimen dates. The capture date is not a logo adoption date, and a held current specimen does not establish complete historical coverage.
