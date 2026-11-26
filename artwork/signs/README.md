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

The [Cheakamus River notice](cheakamus/polished.svg) is the supplied polished reconstruction
from `cheakamus-refinement/artwork/cheakamus-notice-to-anglers.svg`. The Signs viewer pairs the
rectified photograph with a typeset edition. Run
`uv run --with fonttools scripts/build_cheakamus_sign.py` to rebuild it. The script takes the
headline, river name, mile marker, barred J, end date and footer outlines from the supplied SVG.
It sets the main notice in the repository’s TeX Gyre Heros Regular, using a common baseline grid,
and groups each line and word for editing. The build fits the
[gallery’s F&W reconstruction](../../public/identity-recreation-conservation/drc-fw-oval-1973.svg)
to the supplied sign’s gold backing and uses the sign’s dark ink.

The five [Entering British Columbia signs](../../src/signs/entering-bc) come from the
B.C. Ministry of Transportation and Highways’ [September 2000 manual, printed page 6.12 (PDF page 162)](https://www2.gov.bc.ca/assets/gov/driving-and-transportation/transportation-infrastructure/engineering-standards-and-guidelines/traffic-engineering-and-safety/traffic-engineering/traffic-signs-and-pavement-markings/manual_signs_pavement_marking.pdf#page=162).
Each SVG retains the individual plate’s native vector paths, colours and illustrated proportions.
The I-180X and I-180B greetings use the PDF’s named Times New Roman Bold Italic face, supplied
locally during Poppler SVG conversion and outlined at the PDF’s glyph positions. The white page
behind the I-180 panels is included in each drawing. The catalogue reports the printed sign
dimensions separately from the proportions of the illustrations, particularly for I-180B.
The [lettering editions](entering-bc/) pair re-typeset outlines with editable SVGs. Each sign’s
About panel offers both downloads and cites the published illustration.

The [blue-bordered Super, Natural welcome sign](super-natural-bordered/) uses the supplied
297 × 224 screenshot. Its date, location and physical dimensions are unknown. Four board
corners, estimated by extending the visible edges, anchor one projective transform.
The 814 × 440 front view uses an approximate 1.85 board aspect ratio, consistent with
the two vanishing points assuming a centred camera with square pixels. A cropped image
or different corner estimates could give other proportions.

The three lines are typeset in [TeX Gyre Termes Bold](https://ctan.org/pkg/tex-gyre)
at 99 drawing units, with the font’s standard advances, kerning and word spaces.
Each complete line is centred on the board at its photographed baseline before its
glyphs are exported as outlines. The original typeface is unidentified. The bundled
font carries the [GUST Font License](super-natural-bordered/GUST-FONT-LICENSE.txt).

Run `node artwork/signs/super-natural-bordered/build.mjs` and then
`python3 artwork/signs/super-natural-bordered/measure.py` (Pillow and NumPy). The latter
projects the delivered SVG back into the camera frame, averages coverage over each original
pixel, and measures lettering intersection over union and centre-spacing error there.
The About panel lets the reader fade the pink projected lettering over the original scene.
