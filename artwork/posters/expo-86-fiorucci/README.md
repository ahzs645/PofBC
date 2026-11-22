# Expo 86 — Vittorio Fiorucci vector reconstruction

Reconstructed on 21 November 2026 from the supplied framed-poster photograph,
with reusable vector elements from the user's PofBC gallery.

## Open these files first

- `Expo86_Vittorio_Reconstructed.svg`: main layered vector; all lettering is outlined, with no font dependency.
- `Expo86_Vittorio_Print.pdf`: one-page vector PDF, nominally 635 × 920 mm. It contains zero raster images and zero font resources; lettering is vector outlines.
- `Expo86_Vittorio_Reconstructed-unsigned.svg`: the same reconstruction without the signature facsimile.
- `Expo86_Vittorio_Reconstructed-editable-text.svg`: a text-editable alternative. Uses Nimbus Sans, with Helvetica/Arial fallbacks. A font substitution can change appearance. Use the outlined main SVG for faithful exchange.
- `Expo86_Vittorio_Preview.png`: 2200 px wide raster preview.
- `Expo86_Vittorio_Comparison.png`: corrected photograph, vector reconstruction, and contour comparison side by side.
- `Expo86_Vittorio_Overlay.png`: enlarged outline comparison, cyan for the photograph and magenta for the reconstructed shapes.

## What was reconstructed

The four coloured silhouettes are independent, deliberately authored cubic
Bézier shapes, with 24, 22, 23 and 23 curve segments respectively. The artwork
was not produced by an automatic bitmap tracing operation. Sharp tips, concave
fin roots, asymmetric tails, and the spaces between forms were rebuilt as
controlled geometry. The 21 window objects preserve the visible irregularities:
4 pale-yellow rounded forms, 6 mint quadrilaterals, 7 orange quadrilaterals, and
4 pink rounded forms. No one silhouette was mirrored or repeated to make another.

The main SVG has eight named Inkscape layers: paper; red motif; blue motif;
yellow motif; green motif; bilingual footer; Expo mark; signature facsimile.
Every motif and window is separately selectable. The footer is outlined per
line in the main SVG. The alternative text-editable SVG has ten live text lines.

## What was reused from PofBC

The Expo logo and its small TM mark reuse `poster-expo-logo` from the
Davidson-poster SVG. The English and French event copy reuse `english-copy`
and `french-copy`. Their paths were retained and repositioned to the supplied
Fiorucci photograph. The bold footer lines received small horizontal placement
scales, because their original PofBC widths did not exactly match this printing.

The gallery identifies its lettering as Nimbus Sans, a Helvetica-style
substitute. This reconstruction does not establish the original printer's
typeface. The gallery describes its Expo symbol as a modern Wikimedia Commons
reconstruction from merchandise photographs; it is not recovered official
printer artwork. The historical artwork remains attributed to Vittorio Fiorucci.

## Identification and nominal size

The dealer's photograph visually matches the supplied design. Its listing
identifies Vittorio Fiorucci, screenprinting, The Expo 86 Corporation, printing
in Canada, and dimensions of 92 × 63.5 cm:
https://librairieseksik.fr/livre/1538

The export uses that listed size, 635 × 920 mm, and the corresponding page
ratio. This is a dealer's catalogue measurement, not a measurement of the user's
physical print. The photograph shows paper under a frame; any hidden perimeter
is unrecoverable from this image. The black frame, wall, photographic shading,
and paper surface texture are not part of the clean vector edition.

## Registration and two manual refinement passes

The supplied image is 1365 × 2048 px. The paper corners used for a perspective
transform, clockwise from the upper left, were:

`(178,311), (1271,302), (1281,1869), (204,1895)`.

The comparison uses a normalized 1100 × 1600 px analytical canvas. The
exported SVG applies a vertical scale of 0.996062992126 to recover the
catalogued physical page proportion, 1100 × 1593.700787402 vector units.

After the first authored drawing, the photo/vector contour overlay guided two
manual adjustments of the existing curve handles. These refined the red upper
fin and lower edge; blue upper and lower contours; yellow belly and upper tail;
and green lower tail, hooked fin, and left edge. A separate visual review
checked the window counts, letter placement, and signature.

| Silhouette | Initial overlap | Final overlap | Mean boundary distance | 95th percentile |
|---|---:|---:|---:|---:|
| Red | 98.19% | 98.53% | 0.92 px | 2.00 px |
| Blue | 98.13% | 98.81% | 0.86 px | 2.24 px |
| Yellow | 97.73% | 98.87% | 0.84 px | 2.24 px |
| Green | 96.96% | 98.44% | 0.92 px | 2.00 px |

Overlap is intersection divided by union of the two silhouette masks. Coloured
windows are treated as holes filled for this silhouette comparison. Boundary
distance is measured symmetrically between the two one-pixel mask boundaries.
Colour thresholds and largest-component selection identify the photographed
silhouettes for measurement only; these raster masks are never converted into
SVG paths and do not generate the vector artwork. Values are calculated from
the corrected photo and normalized vector render. They do not measure original
ink colour, the logo, text, signature, print texture, or overall artistic fidelity.
Photographic blur, frame occlusion, lens distortion and the chosen registration
also limit the precision of these numbers.

## Remaining interpretive details

- **Colour:** the flat palette is an estimated clean interpretation. The source photo is not colour calibrated. Paper is represented as warm off-white. These are RGB colours, not authenticated Pantone or CMYK ink specifications.
- **Signature:** a five-path, hand-drawn visual facsimile based on the supplied photo and a corroborating postcard image. It is approximate, separately editable and removable. The unsigned edition omits it.
- **Typography:** the source gallery's outlined Nimbus Sans is reused, with spacing adjustments. The original printing font is unconfirmed.
- **Edges:** the artwork follows the visible paper area. A small amount may continue beneath the frame in the physical original.

## Palette

| Role | RGB hex |
|---|---|
| Paper | `#F7F5EF` |
| Red | `#B70F18` |
| Blue | `#24558F` |
| Yellow | `#FFDA0A` |
| Green | `#0C602E` |
| Lemon | `#F6E579` |
| Mint | `#62C5AF` |
| Orange | `#EC5006` |
| Pink | `#EC477D` |
| Ink | `#171716` |

## Included source and audit materials

`upload/` contains the untouched supplied photograph. `research-assets/`
contains the downloaded donor SVG, extracted logo/footer groups, and the
visually matched dealer photograph. `work/` contains the authored build script,
signature group, registration parameters, corrected reference, geometric
comparison script, and before/after measurement JSON.

To rebuild in a compatible Python environment, install lxml and Inkscape and
run `python work/build_poster.py` from this folder. This writes SVG editions to
`output/expo-86-vector/`. To repeat geometry QA, also install Pillow, NumPy and
SciPy, then run `python work/compare_poster.py`. The corrected reference used
for the comparison is included. The scripts do not need internet access.

## Source URLs and provenance

- User's PofBC page: https://projects.ahmadjalil.com/PofBC/?view=posters&poster=expo-86-davidson
- PofBC explanatory module: https://projects.ahmadjalil.com/PofBC/assets/expo-86-CUU4K1K5.js
- PofBC vector module: https://projects.ahmadjalil.com/PofBC/assets/expo-86-davidson-DQhS5w5L.js
- Matched original-poster listing: https://librairieseksik.fr/livre/1538
- Dealer image: https://static.livre-rare-book.com/pictures/KSI/1538_1.jpg
- Corroborating 2002 postcard listing: https://www.artsy.net/artwork/vittorio-fiorucci-2002-canadian-exhibition-postcard-expo-86-from-1986-canadian-exposition-poster-vittorio-fiorucci

The postcard image corroborated the design and signature; its colours were not
used as a measured standard. All sources were inspected on 21 November 2026.

## In this repository

Kept, each byte for byte as supplied except this README, which has this section added: the three
SVG editions (outlined, unsigned, editable text), `palette.json`, `MANIFEST.json`, and `work/` less
its corrected reference photograph (the build and comparison scripts, the signature group, the
registration parameters and the before-and-after measurements).

Left out: the supplied photograph (`upload/`), `research-assets/` (the dealer's photograph, and the
copies of this repo's own Davidson drawing, its logo and footer groups and a built module), the
corrected reference `work/reference-rectified.png`, the PDF and every PNG (the preview, comparison
and overlay, all of which carry or are measured against the photograph). Without them,
`work/build_poster.py` and `work/compare_poster.py` will not run here; they are kept as the record of
how the drawing was made. `MANIFEST.json` still lists the files left out.

The Posters view (`?view=posters&poster=expo-86-fiorucci`) shows
`src/posters/expo-86/expo-86-fiorucci.svg`, made from `Expo86_Vittorio_Reconstructed.svg` by
`web_copy.py`: every id prefixed `fio-`, the Inkscape layer labels kept as `data-label`, the
metadata dropped, the size given in user units, and the title and description reworded. Rendered in
Chromium at 1500 wide, it does not differ from the master by a pixel. The shelf card is
`expo-86-fiorucci.thumb.jpg`, 480 × 696, made from that render. The poster is unlisted, with the
other Expo 86 posters.
