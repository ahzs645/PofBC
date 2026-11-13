# BC TRADE — vector reconstruction

Created from the two supplied raster references. This is a newly reconstructed
vector, not an original historical artwork file and not an automatic image trace.

## Files

- BC-Trade-recreated.svg — full colour editable master, including outlined lettering.
- BC-Trade-recreated.pdf — one-page vector print/export copy; 588 x 654 points.
- BC-Trade-recreated.eps — EPS vector exchange copy.
- BC-Trade-symbol.svg — emblem without lettering, with a compact artboard.
- BC-Trade-scan-tones.svg — same geometry with softer colours approximating the scan.
- BC-Trade-transparent.png — 2352 x 2616 raster convenience export.
- BC-Trade-preview.png — white-background preview.
- BC-Trade-comparison.png — original, reconstruction and registered edge comparison.
- palette.json — both approximate RGB palettes.
- validation.json — checks on the final master and exported PDF.
- source/ — editable construction program and independent letter geometry.
- references/ — the two supplied reference images.

## Construction and reference decisions

The small 1991-named scan controls the overall proportions and structural
landmarks. The larger restored image was used to inspect the intended parts;
its texture, stray pixels, softened leaf tips and broken A were not transferred.

The leaf is one deliberately asymmetric outline. The flag has its own sloping
sides and flat base, with a blue field, five individual red components, a swept
rising sun and white separators of different widths. Seven heavy italic serif
letters were constructed individually, including a closed A counter. There is
an explicit space between BC and TRADE. All seven letters remain separately
editable and do not require a font file.

The finished SVG has 20 closed paths, including its vector clipping boundary.
Every visible contour is a filled vector shape. There are no embedded images,
live text elements, strokes, filters, gradients or external dependencies.
Named groups separate the leaf, flag and wordmark; individual components also
have stable descriptive IDs. White is intentional artwork within the flag;
the area outside the logo is transparent.

White channel extents were subtracted from underlying colours with vector
Boolean operations. This prevents the fine coloured fringe that can otherwise
appear where multiple painted shapes meet a PDF clipping edge. These operations
act on the manually authored Bezier paths, not on pixels from either reference.

## Colour and lettering limitations

The references do not establish an original font name or an official spot-colour
specification. The lettering is a stylistic reconstruction, not a claim of an
identified historical typeface. Tiny ray tips and separator widths are informed
estimates because the original scan is blurred.

Primary flat RGB palette:

| Part | Colour |
| --- | --- |
| Red | #B22C20 |
| Blue | #17447F |
| Gold | #EDC445 |
| White | #FFFFFF |
| Lettering | #111111 |

The scan-tones version uses #B3614E, #46698A, #DDC679, #FFFFFF and #242A28.
Both palettes are approximations, not official ink or Pantone specifications.

## Rebuilding the SVG files

The source folder is self-contained. It requires Python 3 and Inkscape on PATH.
Run `python build_bc_trade.py` from that folder. This recreates the three SVG
variants in `output/bc-trade/`. The script lists the intended control points,
then uses Inkscape only for vector Boolean operations. The existing
`typography-review/wordmark.svg` contains the independent letter paths;
`wordmark-geometry.json` preserves their original construction coordinates.

The comparison sheet uses equal artboard scales. Its teal contours are a visual
alignment aid, not a quantitative accuracy or historical-authentication claim.
