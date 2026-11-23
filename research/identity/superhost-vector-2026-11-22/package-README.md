# SuperHost — refined vector reconstruction, revision 2

Reconstructed 22 November 2026 from the supplied newspaper image, the CIPO
SUPERHOST & DESIGN specimen, and the existing vector material in PofBC.

## Changes in this revision

This is a new refinement of the previously delivered vector, with the earlier
geometry retained in `source/previous/` for comparison.

The serif masters were refined through bounded construction landmarks while
keeping their original Bézier segment structure and the shared S design. The
P was narrowed from roughly 66 to 54.7 CIPO reference units, its gap to E was
restored, the U and E were narrowed, the R return was smoothed, and the H/O
stems and counters were realigned. Letter placement was also refitted.

The script was rebuilt with tighter, more angular pen motions. Its h ascender
was restored toward the source height; the m became more diagonal; the o was
constrained to its own compact oval; and the s and final t were repositioned.
The s/t join and h exit remain interpretations. Font identification remains
unresolved.

The newspaper placement of both components was fitted again against the
supplied image. The twelve flag paths, both star arrangements, and their
placements are unchanged from the previous delivery.

`proof/SuperHost_Lettering_Before_After.png` shows the same CIPO crop and scale
for source, previous vector, and refined vector.
`proof/SuperHost_Newspaper_Before_After.png` shows the full supplied layout.
The four-page comparison PDF includes both sets of registration overlays.

The same-coordinate overlap checks improved at all three tested thresholds.
They are diagnostics of these particular printed scans, not historical
accuracy percentages. Full definitions and results are in
`source/refinement-metrics.json`.

| Source and region | Previous IoU | Refined IoU |
|---|---:|---:|
| CIPO wordmark | 0.598 | 0.830 |
| CIPO script | 0.371 | 0.642 |
| Newspaper wordmark | 0.573 | 0.697 |
| Newspaper script | 0.405 | 0.578 |

The table uses the same fixed masks and a 0.5 threshold on both versions.
The individual component studies use slightly different masks and are saved
separately in `source/construction/`.

The slogan can additionally be regenerated from its reusable pen skeletons:

```bash
python3 source/brush/build_slogan_refined.py --output source/components/Slogan.svg
```

This optional geometry generator requires `svgpathtools`. It reads no raster
image and reproduces the final slogan component from its saved skeletons and
placements. The main assembly script still requires only the Python standard
library.

## Start here

**`svg/SuperHost_Newspaper_Black_Refined.svg` is the closest version to the supplied
newspaper image.** Its taller star spray and narrower flag/lettering follow that
reference. `SuperHost_Newspaper_Colour_Refined.svg` uses the same arrangement in colour.

The CIPO pair preserves the broader arrangement visible in the trademark
specimen. The two references have different star positions; they are treated as
separate layouts, rather than forcing one entire logo through a stretch.

| Layout | Black SVG | Colour SVG |
|---|---|---|
| Supplied newspaper | `SuperHost_Newspaper_Black_Refined.svg` | `SuperHost_Newspaper_Colour_Refined.svg` |
| CIPO specimen | `SuperHost_CIPO_Black_Refined.svg` | `SuperHost_CIPO_Colour_Refined.svg` |

Matching **vector PDFs** are in `pdf/`. Transparent PNG previews are in
`preview/`. `SuperHost_Refined_Preview.png` shows the newspaper versions together.
`proof/SuperHost_Refinement_Comparison.pdf` compares both layouts with their
source images and includes coloured registration overlays.

## How the artwork was constructed

### Flag: reuse of existing vector geometry

All **12 path strings** in PofBC's `src/assets/flagMark.js` are preserved exactly.
Those paths describe the waving provincial flag with its Union Jack, setting
sun and wave bands. They are also the flag component used in the linked
Super, Natural sign artwork. The roadside sign's additional long stripes are
not part of this logo.

The existing paths were positioned and scaled against each reference; no flag
outline was generated from the newspaper pixels. The CIPO fit uses uniform
scaling. The newspaper fit has different horizontal and vertical scales to
match that specific printed appearance. This is a placement decision, not a
claim that the original scan is distorted.

The source snapshot is pinned to commit
`46a0b38f2784f41c84a717ee5b7c835ec92ac172`.

### Stars: geometric primitives

Each star is an editable ten-vertex, five-point shape with an inner/outer radius
ratio of **0.445**. Star centres and rotations were fitted to visible landmarks.
The two arrangements were reconstructed separately:

- Newspaper: **145 star shapes**.
- CIPO: **128 star shapes**.

These are counts in the reconstruction, not asserted historical production
counts. At the dense base, the printed stars merge. Some overlapping placements
are therefore inferred using the same regular shape. The construction JSON
records which positions are measured, separated from touching marks, or inferred.

### Wordmark: structural lettering

The serif wordmark uses eight custom reusable letter masters: S, U, P, E, R, H,
O and T. It retains the enlarged initial S, larger H, smaller capitals, close
spacing, and curved R leg. Repeated S forms share the same construction at
different scales.

PofBC's TeX Gyre Termes substitute was inspected, along with other serif
specimens, but its contrast and R shape did not match closely enough to reuse
unchanged. **The historical font has not been identified.** These are deliberate
letterform reconstructions, not an authenticated recovery of the original type.

### Slogan: brush-stroke construction

“Expect the most” was rebuilt from ten shared letter skeletons. A mathematical
brush-nib sweep supplies the stroke width, then cubic curves describe the
resulting contours. This produces editable filled paths rather than a raster
trace or a live-font substitution. The cubic fitting tolerance is 0.075 unit in
the CIPO reference coordinate system.

The script is smoother than the printed source. Some joins and terminal shapes
remain interpreted, particularly where print spread obscures the original.

## Colour

The colour versions reuse the PofBC flag palette:

| Element | sRGB hex |
|---|---|
| Blue flag areas | `#013366` |
| Red flag areas | `#AD0000` |
| Yellow sun | `#FCBA19` |
| Stars and lettering | `#000000` |

These are **colour interpretations**, not verified SuperHost ink specifications.
The historical red/blue/yellow colour family is supported by the contemporary
advertisement and the surviving enamel-pin example. Neither establishes exact
printed colour values. The SVGs contain no Pantone, spot-colour or CMYK claim.

The background is transparent. The unfilled spaces between flag shapes are
transparent as in the reusable component; these versions are intended for a
white or light background.

## Editing and rebuilding

All four SVGs are self-contained, with four named top-level layers:

1. Star spray
2. PofBC flag
3. Expect the most
4. SuperHost

There are **no embedded images, live text objects, external fonts, external
resources, scripts, filters, or clipping masks**. Individual stars and letters
remain separate objects. The four logo PDFs contain vector drawing commands,
with no raster images or font resources. The comparison PDF intentionally
contains reference raster images.

`source/components/` contains the ready-to-edit vector components.
`source/construction/` contains the star positions, serif masters and brush
skeletons. `source/construction.json` stores placements, view boxes, palette and
provenance. `source/pofbc/` contains the unchanged flag component and extracted
path data.

To reassemble all four SVGs after editing the component files:

```bash
python3 source/rebuild.py
```

To also produce the transparent PNGs and vector PDFs, with Inkscape installed:

```bash
python3 source/rebuild.py --export
```

SVG assembly uses only the Python standard library. All finished SVGs can also
be edited directly without running any code.

## Scope and verification

The deliverable is the core SuperHost logo. The surrounding newspaper text,
minister credit and separate Tourism British Columbia endorsement below the
CIPO specimen are not part of the core artwork.

Both layouts were compared with enlarged source images and coloured overlays.
The final renders were inspected for clipping, missing letters, path artefacts
and spacing. All twelve reused flag path strings were compared with the source
and confirmed unchanged. The exact original fonts, individual merged stars,
and historic ink specifications remain unresolved.

This package is a documented reconstruction, not a recovered original master.

## Sources

- [PofBC project](https://projects.ahmadjalil.com/PofBC/)
- [Super, Natural sign](https://projects.ahmadjalil.com/PofBC/?view=signs&sign=super-natural)
- [Unchanged flag component at the pinned commit](https://github.com/ahzs645/PofBC/blob/46a0b38f2784f41c84a717ee5b7c835ec92ac172/src/assets/flagMark.js)
- [Super, Natural source notes](https://github.com/ahzs645/PofBC/blob/46a0b38f2784f41c84a717ee5b7c835ec92ac172/artwork/signs/super-natural/README.md)
- [CIPO record 0904301](https://ised-isde.canada.ca/cipo/trademark-search/0904301?lang=eng)
- [CIPO artwork](https://ised-isde.canada.ca/cipo/trademark-search/media/904301.png)
- Supplied newspaper screenshot, included in `source/reference/`.
- [Surviving enamel-pin example](https://www.etsy.com/listing/1796083498/superhost-beautiful-vintage-british)
- [Squamish Times, 29 April 1986, page 19](https://squamishlibrary.digitalcollections.ca/uploads/r/squamish-public-library/1/9/19028/19860429_Squamish_Times.pdf)

Existing flag geometry is credited to its PofBC source. This reconstruction does
not supply a separate licence for that source material or the historical mark.
