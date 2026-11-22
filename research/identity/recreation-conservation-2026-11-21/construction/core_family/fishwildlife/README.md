# Fish and Wildlife Branch reconstruction

## Delivered files

- `fishwildlife.svg`: normalized 1000 x 1000 editable vector; transparent background, black geometry.
- `fishwildlife.png`: transparent raster preview of the same geometry.
- `fishwildlife_white.png`: white-background review preview.
- `reference.png`: tightly cropped and independently scaled x/y reference from the official 1971 report scan.
- `comparison.png`: source / vector / overlap review board.
- `fishwildlife_overlay.png`: cyan source ink, orange vector ink, charcoal common ink.
- `build_fishwildlife.py`: reproducible manual geometric construction.
- `compare_fishwildlife.py`: renders the vectors and computes transparent comparison metrics.

## Source and identification

British Columbia Department of Recreation and Conservation annual report for 1971, Fish and Wildlife Branch divider, printed DD15 / PDF page 16. Report published in 1972. Source file `sources/forgov_1971.pdf` is a higher-resolution monochrome official scan: its raster page is 1698 x 2197. The review crop is the region x1293, y297, width229, height226 in a 3x rendering of PDF page16. This small printed mark is still only about 210 native scan pixels wide; enlarging it does not supply original-artwork detail.

The accompanying submitted general-administration screenshot and reverse-cover screenshot were used to cross-check the interpretation of the fish, antlers and overlapping deer neck. The comparison deliberately omits the horizontal scanner/registration rule through the animal at y485..501 in the normalized image when computing scores. It is not part of the mark.

## Construction

The vector is assembled from a rounded-square frame, a fish-body outline, a finer gill, eyes, deer face/neck and ear/cheek curves, and a branched antler structure. These are deliberately selected cubic Bézier and line segments, with named editable groups. There is no embedded image, no text/font dependency, and no automated outline extraction or traced pixel contour. The fish tail joins the neck and border; the outer frame hides intended line endpoints.

## Iterative comparison

Three constructions were inspected in registered overlays. The main improvements were moving the fish flank to the right, raising the antler fork and ear, correcting muzzle height and neck alignment, closing the tail/neck junction, placing the eyes, and matching the relative weight of main lines versus the fine gill. Tight-bounds scaling is independent in x/y to remove small scan aspect differences. It does not claim to recover a photographic camera model.

See `metrics.json` for exact figures. Whole-mark intersection-over-union improved from about 0.662 to 0.804 and then about 0.87. Interior overlap improved from about 0.345 to 0.647 and about 0.80. These are diagnostic raster-mask comparisons to one imperfect scan, not percentages of historical accuracy. The corner frame contributes much of the whole-mark score.

## Remaining limitations

This is a reconstruction, not recovered original artwork. The native scan is small, with visible thresholding, ink spread, scan-line defects and local edge noise. The SVG regularizes these defects into clean linework. Fine eye and antler-join details remain interpretations at this source resolution. No species identification or official symbolic meaning is asserted. Black is supplied as a neutral editable ink, not as a verified historical colour specification.
