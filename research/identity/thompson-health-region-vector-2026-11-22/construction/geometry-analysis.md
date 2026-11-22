# Thompson Health Region symbol: independent geometry findings

This is reconstruction analysis from surviving raster specimens, not a recovered master drawing. Coordinates below use a nominal 1000 by 1000 symbol box, with the origin at the upper-left.

## References and reliability

- 9 September 1999 letter: decoded full-page image 5100 by 6600; symbol component bounds 336 by 336. Most pixels repeat in 3 by 3 blocks, so effective independent detail is approximately 112 by 112. This is the cleanest winding-path reference. The upper-left upright edge is badly clipped; that diagonal is contradicted by the other specimens and the colour reference.
- 9 June 2000 letter: symbol bounds 110 by 108 after page rotation. Strong white dropout distorts some upper cutout tips, especially the central and inner-right tips.
- 1 November 2001 letter: symbol bounds 110 by 109. Its upper component provides useful corroboration of the five cutouts. White speckles across the cross are scan defects.
- Colour image recovered from the 2003 workshop report: 59 by 56. Good evidence for the two-colour division; its slight width-to-height distortion should not govern the reconstructed outline.

## Outer geometry

A nominal square cross with a central stem and horizontal bar each approximately one third of the overall width is supported. Small softened external corners are consistent with the sources; a radius near 16 units is reasonable, though the surviving resolution cannot establish an exact original radius.

The horizontal bar lies approximately from y=330 to y=665. Raw later scans put it 1–2% higher, which is consistent with reproduction distortions. Fitted arm edge slopes indicate about -0.4 degrees in the 1999 scan and +0.6 degrees in the later scans. Outer edges should therefore be reconstructed as horizontal and vertical. There is no persuasive evidence of intended asymmetry in the cross or upper cutouts.

## Five white cutouts

There are five white upward-pointing cutouts. Their nominal tips are:

| Cutout, from left | x | y |
|---|---:|---:|
| Outer left | 359 | 200 |
| Inner left | 412 | 135 |
| Central | 500 | 100 |
| Inner right | 590 | 135 |
| Outer right | 644 | 200 |

The side cutouts lean outward. The central one is nearly vertical. They join a white separator band at the gold/teal junction. Do not reduce them to five vertical triangular notches: the ordered outline folds left and right around leaning forms.

A compact left-to-right sequence for the gold component's lower boundary is:

(333,270), (366,320), (359,200), (418,286), (412,135), (475,278), (500,100), (529,280), (590,135), (580,295), (644,200), (630,318), (667,270).

Alternate high points in this sequence are the white cutout tips. The lower points are the gold fingers. Use gentle curves between the major anchors and slight rounding at the gold finger ends. The raw pixel zigzags, especially in the 2000 scan, should not be reproduced as intended detail.

## Teal crown and separator

The 1999 teal component has a nearly flat arm top at y=330, with the following upper-edge extrema in the middle:

- Downward white valleys near (367,366), (447,357), (559,357), and (635,366).
- Upward teal peaks near (408,330), (505,313), and (595,330).

Within approximately one source pixel, symmetry around x=500 is supported. The gold finger ends typically sit 45–60 units above the nearby teal crown, giving the connecting white band a consistent visual thickness. The winding white path starts separately below this band with a teal gap.

## Winding path checkpoints

These left and right boundaries were measured from the cleanest 1999 specimen. They are useful checks on a manually smoothed Bezier outline; they are not exact master-art coordinates.

| y | Left x | Right x |
|---:|---:|---:|
| 400 | 473 | 491 |
| 460 | 571 | 616 |
| 600 | 357 | 411 |
| 740 | 536 | 625 |
| 780 | 536 | 634 |
| 900 | 473 | 598 |
| 980 | 375 | 527 |

The lower opening extrapolates to approximately x=340 through x=515 at y=1000. The path is a widening ribbon, with a small upper right turn, a sharp but smooth middle left turn, and a broad lower right turn. Avoid using a constant-width stroke: the silhouette widens substantially toward the base.

## Supporting files

- *-full-original.png: decoded source page images.
- *-symbol-native.png: analysis crops retaining original image pixels.
- *-symbol-tight.png: large connected components isolated for measurement.
- gold-boundary-contours.json and gold-boundary-contours-1999.json: ordered raster contour measurements.
- *-gold-contour-analysis.png: contour diagrams, not proposed artwork.
- path-row-bounds-normalized-1000.json: path checkpoint measurements from all three years.
- proportions-measurements.json and bar-edge-slopes.json: outline proportions and scan slopes.
