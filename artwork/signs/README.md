# Signs: source packages

The reconstruction packages behind the **Signs** view (`?view=signs`), kept as supplied minus their
reference photographs, comparison images and raster previews.

| Folder | Sign | Used by the site as |
|---|---|---|
| `lookout/` | British Columbia Forest Service, LOOKOUT | `src/signs/forest-service/lookout.svg`: `svg/BC_Lookout_Master.svg` with the em dashes in its title replaced |
| `forest-closure/` | British Columbia Forest Service, FOREST CLOSURE BOUNDARY, Zone 3 (1960) | `src/signs/forest-service/forest-closure.svg`: `svg/forest-closure-open.svg` with the CLOSED strip of `svg/forest-closure-closed.svg` as a hidden layer, its ids prefixed `fc-` and its title replaced |
| `super-natural/` | Super, Natural British Columbia welcomes you | `src/signs/tourism/super-natural.svg`: `svg/BC_Super_Natural_Welcome_Sign.svg` with its generic ids prefixed |
| [`../recreation-conservation/park_symbols/`](../recreation-conservation/park_symbols) | Provincial Parks Branch, the 22 proposed park symbols of 1971 | `src/signs/parks/proposed-park-symbols.svg`, composed by `scripts/build-park-symbols-sign.mjs`: each file's drawing moved into a four-column grid, its title and description dropped and its clip id prefixed `pps-` |

The LOOKOUT package also keeps a softer palette sampled from the photograph, colour separations, a panel
silhouette and a construction-guide view; the site shows the master. These are reconstructions,
not authenticated masters, and imply no affiliation with or rights in the historical designs.

The Super, Natural sign is assembled from this repository's own parts (the Spirit of BC flag in
`src/assets/flagMark.js` and the Termes outlines in `src/hydro/serif.js`), so its build script
reads them from here rather than from copies.
