# BC TRADE - reconstruction from printed evidence

The gallery keeps this as a reconstructed vector, not original historical artwork.
The existing `bc-trade-1991-rebuilt` asset ID and gallery URL are unchanged.

## References

- **British Columbia: Software Developers 1991**, PDF page 146, back cover. Its
  original 196 x 218 pixel logo crop remains unchanged at
  `public/identity-collected/bc-trade/bc-trade-1991-scan.png`.
  Source: https://publications.gc.ca/collections/collection_2019/isde-ised/Iu44-114-1991-eng.pdf#page=146
- **Gulf Islands Driftwood, 12 July 1989**, printed page A19 / PDF page 19.
  This independent monochrome example corroborates the open separations in
  TRADE. Its smaller logo does not provide a higher-resolution shape source.
  Source: https://saltspringarchives.com/driftwood/1989/v30n28July12-1989A.pdf#page=19

The 1991 scan controls geometry. The 1989 printing checks structural details.
Restored or generated enlargements are not treated as additional source evidence.

## Shape review, 14 November 2026

The earlier reconstruction used ordinary solid italic letters and uniformly
stroked white insets around the lower flag bands. The printed mark has a more
specific structure:

- B and C remain solid; T, R, A, D and E have open component separations. Each
  letter is independently constructed. The gaps are transparent geometry,
  including the open A apex and detached D bowl, rather than white painted lines.
- Both lower flag separators have independently drawn boundaries. They widen
  above the red bands, reducing the previously oversized blue wedges.
- The diagonal red band has a wider, smoothly curved upper edge. The adjoining
  blue triangle has a shorter lower-left tip.
- The sun reaches farther left near the base, and its separator is narrower.
- The leaf's lower-left edge and two right-hand tips have small position changes.
  The flag's base and right side were also brought closer to the scan landmarks.

`review/comparison.webp` shows the original scan, former gallery master and revised
master at identical artboard scale, with enlarged lettering details. The source
is explicitly labelled as an enlargement; it contains no new image detail.

### Flag overlay follow-up

The flag was checked again with the preceding PR revision superimposed on the
same original scan. Several blue areas ended in long acute cusps beyond the
printed pigment. The follow-up shortens the upper central blue tip, eases the
small blue end beside the sun, and adds small curved caps to the left and
lower-right blue wedges. Two upper folds move slightly toward the printed
landmarks and receive curved joins. The upper-left red end and the far end of
the diagonal red band are also eased. The central white separator is slightly
wider; the flat base remains, with very small end-corner rounding. A kink on the
sun's lower-left edge is smoothed. The leaf and lettering are unchanged from the
preceding PR revision, and the pointed sun rays are retained.

`review/flag-overlay.webp` contains a source/before/after comparison, an actual
superimposition and six enlarged inspection areas. Magenta is the preceding
vector; cyan is the correction. `review/flag-overlay.html` is a self-contained
viewer with revision, outline/fill, opacity, source and crop controls. All its
images are embedded and it works offline.

Registration stays fixed: one source pixel corresponds to four SVG units, on
the unchanged 784 x 872 artboard. Visible boundaries are extracted from flattened
3x SVG renders, so hidden construction paths do not appear in the overlay.
Neither revision is fitted, rotated or warped separately. The source is enlarged
with its pixels visible. Its blur supports position comparisons but cannot
establish an exact original corner radius.

## Editable construction

The master is `public/identity-collected/bc-trade/bc-trade-1991-rebuilt.svg`.
Its named groups separate the leaf, flag, red bands, sun and seven letters.
The area outside the emblem is transparent; white inside the flag is artwork.

`source/build_bc_trade.py` contains deliberately authored control points. Inkscape
Boolean operations resolve overlaps between these vector shapes; they do not
convert reference pixels into contours. The lower white-channel boundaries are
independent paths, avoiding uniform stroke-width assumptions.

Four named blue-tip regions receive tangent-aligned cubic caps after the Boolean
operations. `svgpathtools` trims short lengths of the existing authored curves;
the cap inherits the two retained endpoint directions. This operates on vector
geometry, not scan pixels. The builder checks that each named cap is present and
that every blue subpath remains continuous and closed, including exact shared
endpoints after curve subdivision.

`source/typography-review/wordmark.svg` contains the seven letter outlines in
native scan coordinates, scaled by four into the 784 x 872 artboard. Its
`fill-rule="evenodd"` preserves the B counters. `wordmark-geometry.json` records
the same construction coordinates. No font file is needed to render the mark.

From the repository root, with Python 3, `svgpathtools` and Inkscape available:

```bash
python3 research/identity/bc-trade-vector-2026-11-13/source/build_bc_trade.py
```

This writes colour, scan-tone and symbol-only SVGs under `source/output/bc-trade/`.
Copy the colour output to the public master, update the master's SHA-256 and byte
count in `source-register.json`, then regenerate the catalogue and only this
logo's display variants:

```bash
node scripts/build-collected-marks.mjs
python3 scripts/build_collected_display.py bc-trade-1991-rebuilt
```

The scan-tone palette and symbol-only output are convenience adaptations, not
historically documented additional marks. They are not separate gallery entries.

## Verification and repeatable visual review

`validation.json` records actual SVG structure, a freshly exported vector PDF,
transparent PNG corners and a fixed-registration comparison against the scan.
The review script requires Pillow, numpy, PyMuPDF and svgpathtools in addition to
Inkscape. The overlay script additionally uses scipy:

```bash
git show ebd96bb:public/identity-collected/bc-trade/bc-trade-1991-rebuilt.svg > /tmp/bc-trade-before.svg
git show 29470d25:public/identity-collected/bc-trade/bc-trade-1991-rebuilt.svg > /tmp/bc-trade-flag-before.svg
python3 research/identity/bc-trade-vector-2026-11-13/source/review_bc_trade.py --before /tmp/bc-trade-before.svg --flag-before /tmp/bc-trade-flag-before.svg
python3 research/identity/bc-trade-vector-2026-11-13/source/overlay_bc_trade.py --before /tmp/bc-trade-flag-before.svg
```

An optional `--font /path/to/font.ttf` controls the comparison sheet's labels.
The diagnostics compare fixed colour masks at native scan resolution. They are
not an accuracy percentage or proof of historical authenticity. The gold mask
is restricted to the sun because blurred red/white edges can appear yellow.
No independent fit or warp is applied to either candidate.

The two comparisons intentionally use different baselines: the full-logo sheet
starts before the letter correction, while the flag overlay starts at PR commit
`29470d25`, after the letter correction. `validation.json` records both hashes and
checks that the flag follow-up leaves the lettering and maple leaf unchanged.
Its cap coordinates and angles describe the joins after white-channel edits and
before capping; they are construction diagnostics, not recovered historical
measurements.

Existing collection/display checks and the real GalleryView browser review cover
asset checksums, loading, light/dark display, desktop/mobile layout and downloads.
The recorded visual comparison remains the principal evidence for shape fidelity.

## Remaining uncertainty

The exact historical typeface is not identified. The different construction of
BC and TRADE does not by itself prove that two commercial fonts were used.
Small serif curves, ray tips and separator widths remain estimates because the
original colour logo is only 196 x 218 pixels and blurred by printing/scanning.

The RGB colours remain approximate display choices, not official ink or Pantone
specifications: red `#B22C20`, blue `#17447F`, gold `#EDC445`, white `#FFFFFF` and
lettering `#111111`. The softer scan-tone palette is likewise an approximation.
