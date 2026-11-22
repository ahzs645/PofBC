# Department of Recreation and Conservation: reconstruction package (21 November 2026)

A supplied reconstruction of the department's branding from its 1970–1973 annual reports and the
Provincial Museum's handbook series. The package's own account is
[`package-README.md`](package-README.md); `overview.png` is its one-page overview. Its 176
production SVGs are in [`artwork/recreation-conservation/`](../../../artwork/recreation-conservation/README.md),
and `manifest.json` / `asset_index.csv` give each one's source report, PDF page, status and checksum
(their `vectors/` paths are that folder).

## What is kept here

- `package-README.md`, `manifest.json`, `asset_index.csv`, `checksums.json`, `validation.json`,
  `pdf_validation.json` — as supplied.
- `notes/` — the package's notes on each group.
- `construction/` — the build scripts and their data, kept as a record. They name the package
  author's workspace paths and need the full report PDFs and locally installed fonts, neither of
  which is here; they are not run by this repository.
- `sources/` — crops of the official annual reports for the report dividers, related emblems and
  park symbols.
- `review/` — source/reconstruction overlays for the core symbols, report dividers (converted from
  PNG to WebP), park symbols and type.
- `reference/` — the report-variant findings and matrix, the handbook and typeface inventories, and
  the Corporatus spacing notes (CSS, JSON, README).

## What is left out, and why

- **The PDF and PNG exports** of each SVG (`pdf/`, `previews/`): copies of the vectors.
- **Photographs of the handbooks**: `sources/handbook_covers/`, `sources/handbook_panels/`,
  `sources/handbooks/`, `review/handbooks/`, `review/handbook_templates/` and
  `reference/BC_Handbook_Variants_Contact_Sheet.jpg` are booksellers' listing photographs. Their
  URLs are in `reference/BC_Handbook_Variants_Inventory.csv`.
- **Type specimens**: `reference/BC_Typeface_and_Variants_Atlas.pdf` and
  `reference/BC_Corporatus_Spacing_Study.pdf` render licensed typefaces; no font software is
  committed (the repository is public).
- **The illustrated catalogue PDF and `index.html`**, which embed the above.

## In the site

`scripts/build-crown-marks.mjs` packages the five symbols (black, report green, report pale, white)
and the four related emblems. The gallery's `recreation-conservation` collection
(`src/gallery/collections.js`) has three eras (`src/gallery/timelines.js`): the 1970 oval, the
1971–1973 square symbols, and the 1973 emblems. BC Parks' collection begins with the Parks Branch's
spirals and 1973 shield, and the Royal BC Museum's (now a researched collection, `royal-bc-museum`,
which keeps `collected-royal-bc-museum` as an alias) with the Provincial Museum's square.
`scripts/build-park-symbols-sign.mjs` composes the 22 proposed park symbols into the Signs view's
*Proposed park symbols, 1971* (`src/signs/parks/`), from the individual SVGs rather than the package's
contact sheet, whose outlined subtitle lost its word spaces. The register subject is `department-of-recreation-and-conservation`
(`src/gallery/reconciledSubjects.js`); the department is a ministry in the atlas
(`department-of-recreation-and-conservation-1957`), not an agency, so the collection has no atlas link.

## Open questions

- Who designed the square symbols, and whether an identity manual exists.
- The Parks Branch logo proposal mentioned in the 1973 report (PDF page 106), which is not pictured.
- What the branches used after 1973. The package found that the 1974 and 1975/76 reports' chapter
  openings no longer use the square symbols, which is a change in those reports, not evidence that
  the marks stopped being used elsewhere.
- The handbook lettering's actual typeface (Neue Helvetica 43 Extended Light is the closest
  comparison, not an identification).
