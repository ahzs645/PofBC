# Welcome to B.C. pin: vector reconstruction

Recreated from a supplied photograph on 20 November 2026.

## Files

- `welcome-bc-pin.svg`: primary vector artwork with a pale warm face.
- `welcome-bc-pin-white.svg`: the same artwork on a pure white circular face.
- `welcome-bc-lettering.svg`: lettering and underline only, on transparency.
- `welcome-bc-pin.pdf`: vector PDF on a 100 × 100 mm square page. This is a convenient export size, not a measurement of the original button.

## Editing and scaling

The SVG files use a 1000 × 1000 coordinate system. The circular face is a separate layer. Every text line is grouped and every character is an editable outline. The underline is an independent rounded rectangle. Scale the entire artwork uniformly to the required button or print size.

All lettering is already converted into vector geometry. No fonts need to be installed to open the finished SVGs or PDF. The wording is stored in accessible labels for identification, but the visible letters are paths rather than live text. Changing the wording therefore requires editing or replacing the letter shapes.

The files contain no embedded raster images, linked artwork, filters, scripts, or external resources. The photographed wear, lighting, reflections, curved face shading, and surrounding table are not part of the reconstructed design.

## Reconstruction choices

The design preserves the photographed line breaks, widely expanded headline letters, tight typewriter-style lower text, separate underline, and slight placement to the right of the circle's centre.

The photograph was rotated approximately 6.7 degrees and its slightly elliptical outline was normalized for comparison. This is a practical visual rectification, not a calibrated recovery of the camera or the curved button surface.

The distinctive uppercase W and M were drawn as custom closed Bézier shapes. Uppercase L and the smaller A, i, v, n, m, f, J, t, and r were rebuilt with clean curves and strokes. Other letters use adjusted Latin Modern Mono or Nimbus Mono PS outlines. Their proportions and weight were matched to the reference individually. This is not an identification of the original typeface.

The main face colour is an interpretation: pale warm `#F1F2E9`, with near-black lettering `#141614`. Use the pure-white version when the material or final printing process supplies the background colour.

## Verification

The complete reconstruction was compared visually with the straightened photograph and with an ink overlap image. The exported PDF was rendered and inspected. The SVGs were checked for embedded raster content and live text, and the PDF was checked for raster images and font dependencies.

The photograph's blur, physical curvature, ink irregularity, lighting and age limit an exact match. The SVGs are clean visual reconstructions, not recovered original production artwork.

## In this repository

Kept as supplied, minus `welcome-bc-preview.png` (a raster preview), `reference-comparison.png` and
`overlap-check.png` (both carry the photograph). The site shows `welcome-bc-pin.svg` as
`src/pins/novelty/welcome-bc-pattison.svg`, its ids prefixed `wbc-` and the dash in its title
replaced; the white-face version is the same drawing with one colour changed, offered on the site as a switch.
