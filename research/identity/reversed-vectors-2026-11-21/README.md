# Reversed and variant vectors, 21 November 2026

Vector versions of marks the gallery held only as images, made from vector artwork already in the
collection rather than traced from the images. Each is listed in `proposed-assets.json` and read by
`scripts/build-collected-marks.mjs` (VECTOR_SEARCHES), which checks that it is pure vector and makes
the image it stands for a version of it, so the image stays beside it as evidence.

## North Shore Health Region, reversed

`public/identity-collected/north-shore-health-region/north-shore-health-region-reversed-rebuilt.svg`

The gallery held the reversed (white) logo only as a 118×124 px raster restored from a later Trans
Canada Trail donor-panel PDF (`historical-north-shore-health-region-trail-reversed-raster`). Its
design is the green boxed logo of the 1999/2000 Annual Report, held as native PDF vector paths
(`north-shore-health-region-annual-report-2000.svg`).

The rebuild uses those paths unchanged. They are drawn into a mask, green as white (shown) and
white as black (open), and the mask cuts a white rectangle: so everything green on the report is
white here, everything white there is left open, and lettering the report draws in white over the
green mountain (Health Region) is cut out of the white rather than painted over it. Compared at the
raster's size, frame, mountain, lettering and tagline box agree; the raster is too small to show
whether the reversed original differed in fine detail, and the record says so.

The BC Place 1984 disc rebuild of the same day is recorded with that body's history, in
`../bc-place-history-2026-11-21/source-register.json`.
