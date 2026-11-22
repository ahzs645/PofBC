# 1984 disc logo, rebuilt as vectors (21 November 2026)

`public/identity-collected/bc-place-ltd/bc-place-1984-disc-rebuilt.svg`, recorded in
`source-register.json` as `bc-place-1984-disc-rebuilt`, with the newsletter masthead
(`bc-place-1984-disc`) kept as its version.

## What it is made from

Only the outlines of this collection's 1983 reconstruction (`bc-place-1983-rebuilt.svg`), unchanged,
placed after the masthead of *BC Place Update*, Spring Issue 1984 (Museum of Vancouver H2025.7.1,
`bc-place-1984-update-header.png`). Nothing is traced from the scan.

- The symbol is the 1983 `interlocking-b-c-p` path without its fine parallel outline, filled white
  and clipped to a disc, as the newsletter prints it.
- The lettering is the 1983 lettering, set flush left on three lines. The 1983 path
  `shared-british-h-columbia-l` (one stem for the h of british and the l of columbia, where the 1983
  lines stagger to meet) is split into an h that stops at the british baseline and an l of the
  1983 ascender height.

## How it was placed

Each part was fitted to the scan by overlap, in the scan's pixel coordinates (the SVG's own):

- Disc: the bounding box of the scan's blue, centre (71, 73), radius 60.
- Symbol: scale and offset maximizing its overlap with the white inside the disc (87%):
  matrix(0.461 0 0 0.461 18.021 1.592).
- Lettering: one scale for all three lines, fitted to the black lettering of the first line; each
  line's height fitted as a whole; every line's left edge at the scan's left edge.

| Line | Scale | x offset | y offset |
| --- | --- | --- | --- |
| british | 0.421 | 46.595 | -1.691 |
| columbia | 0.421 | 4.074 | 1.408 |
| place | 0.421 | 35.06 | 5.102 |

## What differs from the newsletter

Letter by letter the newsletter's round letters are a little wider than the 1983 outlines, most
the c of columbia and the e of place: measured at the scan's x-height, the following letter sits
about 7 to 8 px (of a 695 px crop) further right. The rebuild keeps the 1983 letters and their
spacing rather than redrawing them, so its second and third lines end a little short of the
scan's. The blue (#2D50CB) is the median of the scan's disc pixels, from a museum photograph; it is
not an original specification.
