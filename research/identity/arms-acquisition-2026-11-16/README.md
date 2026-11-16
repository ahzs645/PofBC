# Arms acquisition, 16 November 2026

**422 artwork records for 99 holders, retrieved 16 November 2026.** This is the artwork behind the
Coats of Arms view (`?view=arms`): every rendering of the arms, flags, badges, seals and letters
patent of the bodies in [`../arms-register-2026-11-16`](../arms-register-2026-11-16/README.md), plus
Douglas College, whose arms are documented by the College itself.

It was acquired against commit `8f95bd67` and covers all 108 register entries in that baseline, seven
earlier register records linked to them (a body's grant under a former name, or a same-day
registration), and supplemental artwork from the holders' own publications and Wikimedia Commons.

| Folder | Files | What |
| --- | --- | --- |
| `assets/registry/` | 367 | The Canadian Heraldic Authority's published images: arms, flags, badges and letters patent |
| `assets/provincial/` | 10 (+2 PDFs) | The Province's and the Lieutenant Governor's arms, shields, flags and badge, community SVGs and the official SAMPLE-marked vectors |
| `assets/institutions/` | 21 | Universities', colleges' and police services' own artwork, and four Commons files |
| `assets/municipal/` | 24 | Municipal SVGs from Commons, official municipal artwork and historical seals |

Every file is unchanged from its source and matches the SHA-256 in [`catalogue.json`](catalogue.json).
Nothing was traced, synthesised or upscaled. SAMPLE markings and source backgrounds remain.

## Files

- [`catalogue.json`](catalogue.json): the normalised catalogue. `records` has one entry per register
  record, `assets` one per artwork file, with its artist, licence, rights, source page and URL,
  dates, dimensions and hash. `unresolved` lists what could not be found.
- [`holders.json`](holders.json): the 99 holders with their artwork, as the acquisition grouped them.
- [`inventory.csv`](inventory.csv): one row per artwork record, for spreadsheets (UTF-8 with BOM).
- [`source-documents.csv`](source-documents.csv): the supporting source PDFs, with URLs and hashes.
- [`provenance/`](provenance/): the acquisition manifests and notes for each group. Their local paths
  are the acquisition machine's; the catalogue's `file` paths resolve against `assets/`.
- [`SHA256SUMS.txt`](SHA256SUMS.txt): the delivered package's checksums.

## Not kept here

The package also held 24 supporting PDFs (convocation programmes, brand standards, council minutes and
a 15.6 MB heraldry congress volume, 62 MB in all), its own previews, a 17-page PDF catalogue and an
offline `index.html`. They are not arms artwork and are mostly third-party publications, so they are
left out; each source PDF's URL and hash is in `source-documents.csv`, and `SHA256SUMS.txt` still
lists them. The two provincial SAMPLE PDFs, which are alternate forms of artwork records, are kept.

## In the site

[`scripts/build-arms-artwork.py`](../../../scripts/build-arms-artwork.py) makes a WebP display copy of
each record in `src/arms/artwork/` (long edge 720 px, 1100 px for letters patent; SVGs rendered in
Chromium) and writes `src/arms/artwork.json`, the index the view reads. Run it again after changing
this folder:

```bash
python3 scripts/build-arms-artwork.py
```

Each holder's page leads with the picture the acquisition chose (`holders.json` → `image`), except the
Province (the site's own vector) and the Lieutenant Governor (the Commons flag already in
`src/arms/images/`). Every record is shown in the page's Artwork section with its artist, licence,
source and a link to the original file here.

## Dates and rights

Design, registration, artwork and publication dates are separate fields, and the date a rendering was
made is not the date of the design. A modern community drawing of historical arms is labelled as such.

The register's paintings and the holders' own artwork keep their owners' rights: being downloadable is
not a licence. Open licences (Commons) are recorded per file with their authors. Credit each image as
its record says.

## Open points

- **Town of Kinnaird** has no illustration: the register's published image is the text of the
  registration, not the arms. Its emblems were recorded at the Court of the Lord Lyon on 20 March 1969.
- **The 1906–1987 full achievement** has no independently sourced vector; the dated specimens in
  [`../arms-variants-2026-11-14`](../arms-variants-2026-11-14/README.md) remain the references.
- **Official provincial masters** are not public; only SAMPLE-marked excerpts of the official guide
  were extracted.
- **Register entries 169 and 491** (City of Port Moody's 2000 registration and City of Chilliwack's 2005
  confirmation) have no published images in the register; both places have artwork from their other
  entries or other sources.
