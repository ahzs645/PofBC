# BC Forest Closure Zone 3 - 1960 vector reconstruction

> **As kept in PofBC.** This folder is the supplied package minus its reference photographs and
> registered crops (`references/`), raster previews (`previews/`), the analysis PNGs and per-word
> metric fragments (`analysis/*.png`, `analysis/metrics*/` except `quantitative.json` and
> `README.md`), the interactive review HTML, the illustrated report PDF, the two single-state PDFs
> (the two-page `pdf/forest-closure-artwork.pdf` has both), and `fonts/`. The fonts are not needed
> to rebuild: `source/rebuild_fonts.py` regenerates the two reconstruction OTFs (create `fonts/`
> first) and `source/build_vectors.py` reads the closed notice from
> `source/notice_glyph_masters.json`, falling back to League Spartan (SIL OFL) only if that file is
> missing. `manifest.json` still lists every supplied file. `source/measure_overlap.py` needs the
> photographs, which are not kept. The site shows `svg/forest-closure-open.svg` with the CLOSED
> strip of `svg/forest-closure-closed.svg` added as a hidden layer, every id prefixed `fc-` and a
> new title, as `src/signs/forest-service/forest-closure.svg`; its Strip switch shows one face or
> the other.

Prepared 20 November 2026.

## Start here

- `svg/forest-closure-open.svg` - finished OPEN state, all lettering outlined.
- `svg/forest-closure-closed.svg` - finished CLOSED state, all lettering outlined.
- `svg/forest-closure-open-shared-masters.svg` and `svg/forest-closure-closed-shared-masters.svg` - one-alphabet alternatives with width/height scaling.
- `pdf/forest-closure-artwork.pdf` - two-page pure-vector artwork PDF.
- `forest-closure-interactive-review.html` - self-contained offline photo-overlay viewer, font comparisons and fit results.
- `pdf/forest-closure-reconstruction-report.pdf` - six-page illustrated review.
- `previews/reconstruction-overview.png` - both finished versions.
- `previews/photograph-overlays.png` - vectors projected over both original photographs.
- `previews/ink-difference-analysis.png` - source-only / vector-only / shared-ink differences.

The artwork SVGs in `svg/` contain no embedded raster images and require no font installation.
The triangle, rule, words, changeable panel and oval are separate named groups.
White board shapes are present; the surrounding area is transparent.

## Corrected shared-strip interpretation

Both states now use the same **1000 x 130** status-strip rectangle. This is a
normalized reconstruction convention, not a verified fabrication dimension.
The previous CLOSED panel and its layout score are superseded. It incorrectly extended to the photograph's bottom edge.
The physical board ends near source-image y1020-1028, with background and post
below it. Its revised boundary is consistent with the OPEN strip's proportions.
A reversible or interchangeable strip is a strong interpretation; the photographs
and bulletin do not prove which mechanism was used.

Letter width and height are independent parameters. Wider OPEN letters and the
narrow CLOSED notice can be modeled as settings of a common lettering style.
Local glyph-shape adjustments in the supplied fitted reconstruction improve
agreement with these scans; they do not prove that separate historical fonts were
used. The statement that OPEN necessarily required a separate font is withdrawn.
The unchanged main O scores 90.0-93.1% shape IoU across six settings. Full
shape diagnostics appear in `analysis/shared-master-benchmark.json`; the
common-alphabet assembled-layout scores are in
`analysis/metrics-shared-masters/quantitative.json`.

P and W occur only in the lower strips, so their directly observed constructions
are now also present in the common 19-glyph subset. No upper-sign glyph changed.
The corrected CLOSED layout transfers the previous placements through one board
homography. Its per-character affine representation differs from that map by at
most 0.09 canonical pixels; no independent character alignment was fitted.

## Typography finding

The source supports heavy geometric sans-serif sign lettering in the Futura/Spartan
tradition. It does **not** establish an exact historic typeface. The original bulletin
does not name a font. Historical Futura Extra Bold and Gill Sans Extra Bold specimens
were visually inspected, alongside modern open-font comparisons.

League Spartan is the strongest tested modern structural comparison. Across 50 main
letter observations, after normalizing each glyph to its own ink box:

| Construction / candidate | Main-letter mean IoU | Numeral 3 mean IoU |
| --- | ---: | ---: |
| Original reconstructed masters | 91.6% | 94.4% |
| League Spartan 825 | 88.0% | 68.3% |
| Jost 800 | 86.4% | 66.2% |
| Noto Sans 900 | 86.0% | 74.6% |

These are fitted shape similarities, not font-identification probabilities.
Individual-box normalization removes differences in character width, size and spacing.
The original main masters are constructed with straight segments, analytical ellipses
and a small number of intentional Bezier curves. No photographic contours are
autotraced. Repeated characters share masters.

The fitted OPEN setting uses locally adjusted O/P/N paths; E shares the main
construction. These are reconstruction variants, not evidence of a separate
historical font. P occurs only in OPEN, so it cannot establish a difference from
the triangle's lettering. Width/height scaling explains the major proportional
changes; residual counter, diagonal and weight differences remain uncertain.
The CLOSED notice uses original W/C/S variants and League Spartan 750 proxy outlines
for O/D/L/E/T/R/A/V. Repeated notice characters share masters; TO retains its smaller
size. The touching R/A region in TRAVEL is treated as a union in full-line comparisons.

## Assembled-layout overlap

| Region | OPEN photograph IoU | CLOSED photograph IoU |
| --- | ---: | ---: |
| FOREST | 88.0% | 89.6% |
| CLOSURE | 89.6% | 90.8% |
| BOUNDARY | 89.7% | 91.2% |
| ZONE | 86.0% | 86.6% |
| 3 | 93.3% | 93.7% |
| Main lettering pooled | 89.2% | 90.4% |
| Changeable panel, local adjustments | 93.2% | 88.3% |
| Changeable panel, shared alphabet + scaling | 89.3% | 87.1% |

IoU is shared foreground ink divided by the union of source and vector ink. Blank
paper/background does not improve the score. Pooled main-letter Dice is 94.3% / 95.0%.
Boundary F1 within two canonical pixels is 89.7% / 91.3% for OPEN / CLOSED respectively.

The main-board transformations are fitted from board geometry, and the two hinged
panels are registered separately. During evaluation, the vector retains its published
layout: no additional letter or word alignment is applied. Source foreground uses
Otsu thresholding within fixed text regions, with isolated specks excluded. Vector
alpha is rendered at four times the canonical resolution and reduced with Lanczos.
Exact thresholds, sensitivity at +/-12 gray levels, masks and input hashes appear in
`analysis/metrics/quantitative.json`.

All scores are in-sample reconstruction diagnostics. These photographs informed the
artwork; this is not independent validation or authentication of an original font.
The two source photographs themselves have registered word IoUs of 84.2-94.0%.
That is contextual evidence of photographic/printing variation, not a score ceiling.

## Geometry and uncertain details

- Main plate: equilateral convention, 1000 design units wide and 866.025404 high.
- Inferred concentric inner triangle scale: 0.556107003.
- OPEN six-landmark fit: 1.06 source-pixel RMS.
- CLOSED six-landmark fit: 5.43 source-pixel RMS, dominated by the faint outer apex
  (13.09 pixels). Its other five landmarks each fit within 1.31 pixels.
- Both panel faces share a 1000 x 130 design rectangle. Each photograph has its own
  projection; the corrected CLOSED edge is faint and carries a few pixels of
  uncertainty. These are not verified fabrication dimensions. The clean artwork
  omits the photographic supports and hinges.
- The supplied images are monochrome. Black and white is a reconstruction choice;
  original colours and finishes are not established.
- The oval wording is legible. Fine tree/landscape details are simplified, and its
  micro-lettering is condensed Nimbus Sans Bold converted to paths. It is excluded
  from the numerical typography scores. A later dense-tree emblem was not substituted.

## Editable type and font subsets

Optional `*-live-type.svg` files embed the two original OTF subsets. Some desktop
editors ignore embedded SVG fonts and require installing the OTFs from `fonts/`.
The closed notice and oval remain outlined in these files. Every character in the
main words is a separate text object inside a named word group, preserving the
measured per-character positioning. These are not continuous editable text lines.

- `ForestClosure1960-Reconstruction.otf`: space + `3ABCDEFLNOPRSTUVWYZ`
  (19 visible glyphs).
- `ForestClosure1960-Expanded.otf`: space + `ENOP` (4 visible glyphs).

These are constructed specimen subsets, not recovered historical fonts or complete
alphabets. Unrepresented digits, lower-case letters and other characters are absent.

The main/expanded geometry is original reconstruction work. League Spartan, Jost and
Noto Sans files retain their included SIL Open Font Licenses. The closed notice's
proxy-outline origins are recorded per glyph in `source/notice_glyph_masters.json`.
Only selected modern comparison instances are bundled; the full candidate result
tables retain all tested settings.

## Rebuild and measure

Requirements: Python 3 with `fonttools`, `Pillow`, `numpy`, `scipy`, `lxml`; Inkscape
for SVG rasterization and PDF export. Rebuild commands, from this folder:

```bash
python3 source/rebuild_fonts.py
python3 source/build_vectors.py
python3 source/measure_overlap.py --include-closed-panel
python3 source/measure_overlap.py --include-closed-panel --shared-masters
```

`source/layout.json` contains the board geometry, text boxes, rotations and panel
settings. `source/glyph_masters.json`, `source/expanded_glyph_masters.json` and
`source/notice_glyph_masters.json` contain reusable curves and widths. The source
photographs and registered measurement crops are retained in `references/`.

Rebuilding the vectors/metrics does not automatically rebuild the narrative PDF,
interactive HTML or composed preview boards. Those are release review artifacts
for the delivered geometry. Font file timestamps may change when rebuilding.

## Verification

- Outlined SVGs parse, contain no `<image>` elements and have no `<text>` elements.
- The two-page artwork PDF contains vector drawing operations and no raster images.
- The report was rendered and visually reviewed page by page.
- Live-type and outlined Inkscape renders agree to within antialiasing differences:
  approximately 0.07% of page pixels differ by more than four channel levels.
- The offline HTML assets, script syntax, state switching, opacity control,
  source-only toggle, SVG download links and ARIA state were checked. A live browser
  screen check was unavailable because this environment blocks Chromium process
  sockets; no browser-layout validation is claimed.

## Historical sources

1. BC Forest Service. *Protection Bulletin*, 1960 no. 3, printed page 4,
   "Forest Closure Zone Signs". This is the exact source of both photographs and
   describes twelve pilot signs with changeable OPEN/CLOSED status.
   https://a100.gov.bc.ca/pub/eirs/finishDownloadDocument.do?subdocumentId=21448
2. Doug Adderley and Rick Wells. *The BC Forest Service Oval* (2011), pages 3 and 6.
   https://bcfs100.for.gov.bc.ca/docs/pdf/6/406.pdf
3. The League of Moveable Type, League Spartan.
   https://www.theleagueofmoveabletype.com/league-spartan
4. indestructible type*, Jost.
   https://indestructibletype.com/Jost.html
5. Futura Extra Bold specimen photographed by James Puckett, CC BY 2.0.
   Inspected for morphology; the specimen's original publication date is unestablished.
   https://commons.wikimedia.org/wiki/File:Futura_Extra_Bold_Type_Specimen_(8555786350).jpg
6. Science Museum Group, Gill Sans Extra Bold series 321 specimen.
   https://collection.sciencemuseumgroup.org.uk/documents/aa110126408/specimen-sheet-for-gill-sans-extra-bold-series-number-321

The JUL 5 1960 marking on the bulletin is a library stamp, not an established exact
publication date. The user's source images are retained unchanged as references.

## Follow-up analysis records

`previews/shared-letter-widths.svg` is an analysis diagram and includes the
photographic measurement masks. It is not one of the all-vector sign artworks
in `svg/`. Older notice candidate/glyph comparison files retain their original
local sampling grid as research records. The current assembled-layout results
are `analysis/metrics/quantitative.json` and
`analysis/metrics-shared-masters/quantitative.json`; those supersede the prior
CLOSED-panel layout score. The normalized O comparison is unchanged because its
master path and source glyph masks are unchanged.
