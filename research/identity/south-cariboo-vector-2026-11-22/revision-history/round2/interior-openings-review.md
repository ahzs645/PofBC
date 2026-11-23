# Local curve cleanup of five interior openings

## Assessment

Localized curve cleanup is warranted. At export enlargement, candidate06's `branch_06_gap`, `branch_07_gap`, `branch_09_gap`, `branch_12_gap`, and `crown_eye` appear as deliberately constructed hexagons, diamonds or clipped polygons. The small source raster suggests short uneven light brush cuts. It does not establish exact corner radii, so this proposal is a restrained reconstruction rather than a claim to recover original curves.

## Proposal

`opening-curves-proposal.json` contains only a `dark_voids` dictionary with those five keys. All paths are manually authored in source coordinates. Apply inverse FIT when inserting them into the construction model.

The changes preserve the approximate location, size and direction of each cut. Short quadratic curves soften the polygon shoulders while keeping uneven widths and different shapes. This is confined to the five openings; no global smoothing, contour roughening, position change or other geometry edit is applied.

`opening-curves/compare.png` shows source / candidate06 / local curves at the same enlargement. `opening-curves/preview.png` is the isolated full render. The source comes from `baseline/South_Cariboo_Vector/evidence/source-colour-logo.png`.

## Review result

I prefer the local curves for enlargement/export. At native size, the tree's character stays consistent. The five openings no longer read as geometric chips.

The curves were not optimized for pixel overlap. Overall dark IoU changes slightly from .89338 to .89187; continuous density MSE is essentially unchanged (.018661 to .018691). This small numerical tradeoff is acceptable for the requested contour cleanup. There is no need to reopen the surrounding branch geometry to recover those few threshold pixels.

No master or pale-tree geometry was changed.
