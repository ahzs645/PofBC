# BC Environment vector reconstruction

## Files

- `BC_Environment_Logo.svg`: upright logo, dark monochrome, transparent background.
- `BC_Environment_Cream.svg`: upright logo in approximate cream ink, transparent background.
- `BC_Environment_Diagonal_Banner.svg`: the supplied diagonal cover arrangement. The two narrow knockout bands and the area outside the green panel are transparent, ready to place over a photograph.
- `BC_Environment_Vector.pdf`: two vector pages: the upright monochrome logo and diagonal green banner.
- `BC_Environment_Preview.png`: large upright colour preview.
- `BC_Environment_Comparison.png`: source, reconstruction, and registered overlay.
- `BC_Environment_Geometry.json`: editable path data and source provenance.
- `BC_Environment_Validation.json`: vector-content checks and comparison diagnostics.
- `BC_Environment_Source.png`: the supplied raster reference, included only for comparison.

## Reconstruction

The main SVG contains 25 editable paths: 13 letter paths (B, C, and 11 letters in Environment) and the emblem's 12 paths. The SVGs contain no embedded bitmap and no live text; the artwork does not require fonts to be installed. Groups label the upper text, lower text, and emblem. The banner adds one path with three green subpaths.

The existing flag artwork was reused from PofBC and transformed as a single unit. Its original Bezier curves were preserved, including the transparent separations. The lettering was rebuilt using PofBC's Helvetica Bold outlines, then fitted by letter to the supplied scan. The lower line is tightly spaced; its compact appearance should not be reproduced simply by uniformly squeezing an ordinarily spaced word.

The diagonal version is registered to the 594 x 446 supplied image and uses a 45-degree rotation. The underlying photograph and printing noise are not part of the reconstructed artwork. Transparent areas allow the banner to be reused over another image.

## Colour

- Green: `#5EBD7E`
- Cream: `#F7F3D6`

These are visual approximations from a textured scan, not verified government spot-colour or CMYK standards. The SVG fill colours can be edited directly.

## Provenance and limitations

- User-supplied screenshot is the layout reference.
- Website: https://projects.ahmadjalil.com/PofBC/
- Existing flag paths: https://github.com/ahzs645/PofBC/blob/a8d35e4afcdf67447a6234ca0ace68689350ec82/src/assets/flagMark.js
- Original PofBC flag asset: https://github.com/ahzs645/PofBC/blob/a8d35e4afcdf67447a6234ca0ace68689350ec82/artwork/flag/spirit-of-bc-flag.svg
- Helvetica outlines used by the site: https://projects.ahmadjalil.com/PofBC/assets/bold-DhMx883U.ttf

This is a reconstruction from the supplied image and existing PofBC artwork. It is not a newly authenticated original government master. The scan supports Helvetica-family bold lettering, but it cannot establish a particular historical font release. The font files are not redistributed.

The reconstructed geometry was reprojected over the source and inspected. Overall foreground intersection-over-union in the saved threshold-based comparison is 82.6%; the emblem alone is 69.2%. These are pixel-mask diagnostics, not an accuracy guarantee. The fine emblem gaps and top details retain visible differences at the source's small scale.

## Validation

- SVGs: all paths; no embedded images or text elements.
- PDF: two pages; zero embedded raster images; zero font dependencies.
- SVG and PDF exports rendered and visually checked.
