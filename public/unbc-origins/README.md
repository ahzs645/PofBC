# Interior University Society — public vector collection

This is a compact public distribution of the supplied **IUS Vector Brand Kit, version 1.2**, accompanying PofBC's account of the campaign for a northern university and the formation of UNBC.

The 26 SVG masters and their PDF/EPS exports reproduce or interpret historical campaign material. They are contemporary reconstructions, not recovered original masters or official UNBC identity files. Original fonts, exact colours, physical dimensions and the original designer have not been established.

## What is included

- `svg/`: 26 editable vector masters, retained byte-for-byte from the supplied kit.
- `pdf/`: 26 corresponding vector PDF exports, retained unchanged.
- `eps/`: 26 corresponding EPS exports, retained unchanged in the ZIP.
- `palette/`: approximate reconstruction colours; the ZIP includes JSON, CSS, ASE and GPL formats.
- `assets.json`: the public catalogue, with individual reconstruction notes.
- `manifest.json`: the exact files, sizes and SHA-256 checksums in this distribution. The web copy also identifies the downloadable ZIP.
- `SUPPLIED_README.md`, `FONT_NOTES.md`, `asset-manifest.json` and `vector-validation.json`: original documentation retained for provenance in the ZIP.
- `source/`: supplied authoring scripts and metadata, included for inspection and adaptation. These scripts were not executed during this import.

The original photographs, earlier raster reconstructions, PNG exports, photo-based comparison boards, full illustrated reports and original standalone HTML gallery are excluded. They are not required to view or edit the vector masters. The original README describes the complete supplied kit, so some of its links refer to files outside this public subset. Its full `build_all.py` workflow also expects excluded reference material and system fonts/tools; use the supplied finished masters directly or adapt individual authoring scripts.

## Reading the artwork

**Reconstructed** means that the arrangement or wording follows the supplied artifact photographs, with uncertain letterforms and colours approximated. **Interpretive** artwork includes newly drawn detail that the photographs cannot establish. **Derived adaptations** and **Components** are useful reconstruction variants or pieces; they do not demonstrate additional historical identities.

The invitation visibly dated **8 June 1988** establishes an observed use of the identity. It does not date its creation. The archival accession number **1992.2** is not a design date. Telephone numbers, addresses, donation amounts and form wording are historical documentary content; they are not current contact details, appeals or registration services. Unreadable form text and handwritten details have been omitted rather than invented.

The Northern U button includes the supplied version 1.2 capital-N correction. The precise historical typeface remains unconfirmed.

This collection does not claim authorship of the historical identity, campaign wording or original illustration, and does not grant new rights to those materials. Photographic authorship is not asserted.

## Reproducing this distribution

From the PofBC repository, run:

```sh
node scripts/build-ius-download.mjs
node scripts/build-ius-download.mjs --check
```

The packaging script uses only committed files, fixes ZIP entry timestamps and order, and does not run the supplied authoring scripts. Individual SVG and PDF files can be downloaded directly from the public collection.
