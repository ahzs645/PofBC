# Province of British Columbia arms: supplied vector reconstructions, 27 November 2026

Three vector redraws of the Province's arms with the crest, supporters and motto as they were drawn
before the 1987 grant (the 1906 shield, the lion crest, the stag and ram, no dogwood compartment).
Each was supplied as a reconstruction of a raster picture. None is original artwork or an official
vector master, and none dates the design; they are catalogued in the Coats of Arms view as section
08, "Vector reconstructions", of `research/identity/arms-variants-2026-11-14/catalogue.json`, each
pointing to the dated specimen it follows.

| Catalogue entry | File | Follows | Supplied as |
| --- | --- | --- | --- |
| `reconstruction-colour-ornate` | `reference/reconstruction-colour-ornate.svg` (SHA-256 `664e20fa…f908895`) | No. 17, the government history illustration (same drawing, cleaner print) | `historical-bc-coat-of-arms-vector-package.zip`, revision 2: 104 paths, 20 ellipses, 10 circles; no images or live text |
| `reconstruction-monochrome-engraved` | `reference/reconstruction-monochrome-engraved.svg` (`318360e6…c8266e4967`) | No. 11, the 1935 museum report's fine engraving (printed 1936) | `BC-Historical-Coat-of-Arms-Package.zip`: 40 filled paths in 14 named groups; no images or live text |
| `reconstruction-monochrome-line` | `reference/reconstruction-monochrome-line.svg` (`e99ce07b…c2bd5ed2`) | No dated specimen in the catalogue | `historic-bc-coat-of-arms.svg` alone; its source cutout was not supplied |

The match to a catalogue specimen is by visual comparison of the supplied reference with the
catalogue's image (pose of the supporters, crown, scroll layout), not a claim that the reference is a
scan of that specimen.

## What is kept here

- `colour-ornate/`: the package README (reconstruction decisions, revision 2 corrections, palette),
  `vector-validation.json`, the supplied reference raster (`supplied-reference.png`), and the
  rebuild sources (`rebuild/`: component SVGs and the Python that fitted and assembled them). The
  package's PDF, 4000 px PNG and comparison previews are not kept: they are exports of the SVG.
- `monochrome-engraved/`: `RECONSTRUCTION-NOTES.txt` and the supplied reference
  (`Original-reference.png`). Its PDF and PNG exports are not kept.
- The line reconstruction carries its own description in the SVG's `<title>` and `<desc>`.
