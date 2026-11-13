# Super, Natural British Columbia welcomes you

> **As kept in PofBC.** This folder is the supplied package minus its reference photograph,
> comparison image, raster preview and PDF, and minus `rebuild/sources/` (byte-for-byte copies of
> `src/assets/flagMark.js`, `src/hydro/serif.js` and `src/hydro/hydroType.js`, which the scripts in
> `source/` now read from this repository directly; `node source/build-sign.mjs` reproduces
> `svg/BC_Super_Natural_Welcome_Sign.svg` exactly). `rebuild/` is `source/` and the SVGs are in
> `svg/`. The site shows the master as `src/signs/tourism/super-natural.svg`, with its generic ids
> (`title`, `desc`, the two baseline clips) prefixed so they cannot collide on the page.
> `source/compare.py` needs the photograph, which is not kept here.

Editable vector reconstruction assembled from the existing elements in
[ahzs645/PofBC](https://github.com/ahzs645/PofBC), using the supplied
`Bennett-06(1).jpg` photograph as the layout reference. Prepared 12 November 2026.

## Open these files

| File | Purpose |
| --- | --- |
| `BC_Super_Natural_Welcome_Sign.svg` | Main vector: white sign face, interpreted flag backing, flag, three stripes and all three text lines. |
| `BC_Super_Natural_Welcome_Sign.pdf` | Vector PDF of the same master. Contains no embedded raster images or font resources. |
| `BC_Super_Natural_Artwork_Only.svg` | The coloured artwork on a transparent canvas, with the white sign panel omitted. The negative space inside the flag is transparent. |
| `BC_Super_Natural_Preview.png` | Presentation preview on grey, making the panel edge visible. The grey background is not part of the master. |
| `BC_Super_Natural_Comparison.png` | Supplied photo, vector projected into the same camera view, and 45% overlay. |
| `components/` | Separate flag/stripe header, lettering and panel silhouette SVGs. |
| `construction.json` | Explicit composition parameters and type metrics. |
| `validation.json` | Source identity and vector-only checks. |
| `rebuild/` | Generator, layout settings, exact reused source files, reference image and verification tools. |

The SVG has labelled groups for the panel, header and three text lines. Individual
letters are editable vector paths. There is no embedded photograph, image trace,
remote dependency or installed-font requirement in the finished artwork. The
lettering is outlined rather than editable as a live text string; edit the wording
in `rebuild/design.json` and rerun the generator to typeset it again.

## Existing components reused

The source snapshot is commit
[`620294eec90dba2e69d94b4dde8551108f61fe37`](https://github.com/ahzs645/PofBC/tree/620294eec90dba2e69d94b4dde8551108f61fe37).

1. **Spirit of BC flag:** the twelve paths from `src/assets/flagMark.js`, derived
   in PofBC from `artwork/flag/spirit-of-bc-flag.svg`. All twelve path strings and
   fills are unchanged. One uniform scale and one translation place the flag.
2. **Serif lettering:** the committed TeX Gyre Termes Regular glyphs and kerning
   in `src/hydro/serif.js`, with layout measurements from `src/hydro/hydroType.js`.
   All visible letter path strings match those source glyphs.
3. **Palette:** the supplied artwork's navy `#013366`, red `#AD0000` and gold
   `#FCBA19`, with a white sign face. PofBC separately records a historical-standard
   palette; the supplied palette is used here for consistency with the existing
   element. It is not a verified paint specification for this particular sign.

The exact upstream source files are included. Their Git blob hashes are checked in
`validation.json`. The serif copyright attribution remains in the source files;
the supplied GUST Font License is included with them.

## New construction and documented adjustments

- Three straight stripe extensions meet the original flag at its existing left
  edges. A small overlap prevents antialiasing seams. These extensions are simple
  geometric shapes; the source flag is not reshaped.
- A white rectangle forms the board face. The small white backing around the
  flag is an interpretation of the raised upper panel edge, derived from the
  existing flag silhouette. The pale sky makes that edge uncertain in the photo.
- Three lines reproduce the observed wording and punctuation exactly:
  `Super, Natural` / `British Columbia` / `welcomes you`.
- The existing serif is condensed and placed line by line. A reversible vector
  stroke of 16 source-font units adds optical weight. Reused `p`, comma and `y`
  paths have clipped below-baseline copies scaled to 0.5, 0.7 and 0.65 respectively,
  to approach the shorter descenders visible in the photograph. The original
  path data is retained; the adjustment is entirely in groups and clipping.
- The full artwork uses a normalized 1200 by 1150 viewBox. The rectangular face
  begins at y=190 and is 1200 by 960 units. These are construction units, not
  measured dimensions of the roadside sign.

This is a reconstruction, not an authenticated original master. The photograph
does not establish the original typeface, exact panel cutting profile, real-world
size, or sign-specific paint colours. Termes is an existing reconstruction font
from the repository, not a claimed identification of the sign's historical font.

## Comparison and checks

For comparison only, the finished vector is projected into the supplied photo
using the four estimated board corners `(115,31)`, `(244,30)`, `(241,135)` and
`(111,134)` in the original 364 by 161 image. The geometry overlay is included so
that proportions and spacing can be reviewed. Enlarging the small photograph
does not recover missing detail. No photographic tracing or raster-to-vector
conversion was used to create the master.

Verification checks that:

- The twelve flag paths and fills are identical to the repository source.
- All 39 visible letter instances use the committed glyph paths.
- The SVG has no image, live-text, foreign-object or external-href elements.
- The PDF has one page, no embedded raster images and no font resources.
- The source files match their recorded Git blob hashes.

## Rebuild

The SVG generator requires Node.js and uses no npm packages:

```sh
node source/build-sign.mjs
```

New results appear in `source/output/`. The reference photo in
`rebuild/reference/Bennett-06.jpg` is supplied for comparison only.

To reproduce the PNG, PDF, comparison and validation outputs as well, install
Inkscape and Python with Pillow, NumPy and PyMuPDF, then run:

```sh
python source/export_all.py
```

The source SVG, not a raster preview, is the editable master. The PDF's page size
is derived from the normalized SVG units; scale it as appropriate when printing.
