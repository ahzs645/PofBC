# Second review: original tree evidence

## Main finding
The two colour trees share distinctive left-side branch forms and internal openings. They are not mirrored. Eleven manually selected source feature pairs fit a near-5/6 affine reduction plus about (54, 23) pixels translation, with 0.279-pixel RMS residual. This supports a common reconstructed brush skeleton. It does not establish that the complete pale tree is simply a transformed dark tree: the pale right-side mass is broader, and several dark right-side openings are absent.

`manual-landmark-fit.json` records the eleven approximate point pairs, matrix, uncertainty and residuals. Points are selected visually from named features; no contour extraction or image optimization was used. Their manual uncertainty is approximately 0.5–1 source pixel, so the matrix decimals are computation precision, not evidence of subpixel design precision.

## Why pass07 feels different
The source has irregular tapered strokes, hooked branch ends, chipped interruptions and inconsistent spacing. Pass07 regularizes several of those into smooth broad lobes and nearly round holes. The left edges broadly align, but silhouette overlap alone misses this brush character. Both the negative openings and the asymmetric direction of the strokes need visual judgment. `source-versus-pass07-trees.png` compares both at the native 315×141 measurement scale, enlarged five times.

## Retained specimens
- `source-colour-logo.png`, 315×141, remains the best verified colour source. Retained provenance: 1999 Health Plan, archived PDF capture 2000-09-15. Earlier PDF inspection found an embedded raster logo, not recoverable vector paths. See baseline `evidence/source-map.json`.
- `south-cariboo-original-black.gif`, 239×258, is a sharp but substantially solid silhouette variant. It does not preserve the colour illustration’s white brush interruptions and cannot establish those fine edges.
- `south-cariboo-monochrome-lockup.jpg`, 200×100, preserves the ragged/brushy full lockup but adds no detail beyond the colour source. Its archived payload dates to 2004; earlier page references do not date this exact payload.

## Additional research
Exact council-name, designer-name and pine/stock searches produced no verified matching stock illustration, vector original or logo authorship credit. A contributor listing for Cynthia Gardner Design is not proof of logo authorship.

A possible modern lead was checked in Interior Health’s official 2019-02-12 board agenda package, PDF page58 (printed magazine page24). Its South Cariboo Health Foundation logo has three smooth conifers with different branch structure. It is not a sharper specimen of the historical two-tree drawing. Local verification: `foundation-2019-page58.png`; source PDF: https://www.interiorhealth.ca/sites/default/files/PDFS/2019-02-12-board-regular-meeting-agenda-package.pdf

The useful advance is structural evidence from the original image, rather than a newly discovered master. Historical stock origin and designer remain unverified.

## Diagnostic image limits
The normalization and affine image comparisons in this folder are source-analysis aids only. Raster data is not embedded in or used to generate SVG boundaries. The colour normalization makes white gaps easier to compare but includes overlapping dark artwork in some pale crops; interpret those regions with the original colour image. Final reconstruction should remain manually authored vector geometry.
