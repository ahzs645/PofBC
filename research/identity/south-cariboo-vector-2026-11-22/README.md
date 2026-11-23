# South Cariboo Community Health Council, vector reconstruction, 22 November 2026

This is a supplied vector reconstruction of the council's green two-tree logo (revision
`shared-master-soft-crown-v2`). The original artwork has not been found.
`scripts/build-collected-marks.mjs` reads `proposed-assets.json` (VECTOR_SEARCHES). The package's
own README is [`package-README.md`](package-README.md).

## In the gallery

The reconstruction leads the council's card. The 1999 Health Plan image
(`historical-south-cariboo-1999-health-plan`) becomes its "Published image" version. The black-and-
grey thank-you lockup, which was a version of that image, moves with it to the vector. The black
2000 website emblem is a different drawing and keeps its own card.

The main SVG keeps the package's live link: the pale tree is an SVG `<use>` of the dark one. These
extra downloads are offered:
- the vector PDF;
- the expanded SVG, for editors that flatten clones;
- the tree alone.

## What it rests on

The target is the Health Plan's single 315 × 141 logo image. The plan, approved 1 November 1999,
has no drawing paths. The trees are redrawn by hand. Copying one tree is a construction assumption:
the source's pale tree is fuller on the right, so the pale area scores lower than the earlier,
closer-fitted drawing, which is kept in `revision-history/Before_Exact_Shared_Master/`. The lettering
is outlined after ITC Souvenir Demi, the closest typeface tested, and no font file is included. The
greens are sampled from the image.

The history, sources and limits are in `Research_and_Method.md` and `Source_Search_Followup.md`.
`evidence/` repeats three images the gallery already holds, identical byte for byte, alongside the
1994 and 1997 ministerial orders. `construction/` holds the package's build scripts, kept as
supplied and not run here.
