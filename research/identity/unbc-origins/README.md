# IUS vector collection — import and evidence record

The user supplied `IUS_Vector_Brand_Kit(1).zip`, identifying its contents as version 1.2 of an Interior University Society reconstruction. `provenance.json` records the source archive's SHA-256 and byte count. The original archive is not published here.

## Preserved material

The 26 production SVGs and PDFs are retained byte-for-byte under `public/unbc-origins/`; the matching 26 EPS files are retained here in `eps/`. `source/` and `palette/` preserve the supplied authoring files and palette formats. `supplied/` preserves the original inventory, validation records, README, font notes and text/JSON audit evidence. Its original `SHA256SUMS.txt` describes the full supplied kit, including files intentionally omitted from this repository. The public distribution has its own checksum manifest.

`assets.json` adds concise gallery labels and captions without changing artwork bytes. It distinguishes reconstruction, interpretation, reproduction adaptation and construction components. In particular, compact/extended alternatives are derived from prior raster clean-ups and are not independent historical evidence; monochrome/reversed exports are not treated as proof of historical colourways.

## Source and date limits

The supplied source inventory identifies six original photographs (P01–P06) and four earlier raster reconstructions (R01–R04). Do not combine these as ten independent historical sources. The photographed 8 June 1988 invitation establishes an observed use, not the identity's creation date. The display's accession number 1992.2 must not be used as a design date. No photographer identity, original designer, measured colour target or rights grant is asserted.

The source photographs, raster comparison boards and image-bearing guides are excluded from the public distribution. A source JPEG contains location/device metadata, while wider display photographs include contextual people, donor lists and handwriting. Importing the vectors avoids publishing those unrelated details. The production SVGs independently passed checks for matching supplied hashes and absence of embedded images, live text, scripts and external references.

## Version interpretation

The current supplied production Northern U SVG is version 1.2, with the separately drawn capital N. `supplied/font-audit/northern-n/FINDINGS.md` is an earlier review-stage record: its final statement that no production assets were edited is superseded by the supplied version 1.2 README and manifest. It is retained as review history, not a statement about the current asset.

All supplied authoring scripts remain unexecuted during import. Some regenerate report pages that depend on excluded photographs and separately installed fonts/tools. The repository's packaging script does not depend on those scripts or the original upload location:

```sh
node scripts/build-ius-download.mjs
node scripts/build-ius-download.mjs --check
```

The generated public `assets.json` is an exact copy of the canonical research array. Each record has `{ id, label, category, status, note, svg, pdf, svgSha256, width, height }`. Asset paths are relative to `public/unbc-origins/`; width and height are nominal vector viewBox dimensions, not physical measurements. The downloadable ZIP includes all 26 SVG/PDF/EPS sets and compact documentation, source and palette files; generated previews and original photographs are not duplicated.
