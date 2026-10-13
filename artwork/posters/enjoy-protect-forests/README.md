# Enjoy & Protect our Forests — vector reconstruction

A clean visual remake of the image supplied in this conversation. The illustration
and headline are manually constructed vector geometry, not an automatic contour
trace. The supplied bitmap is not embedded in any SVG or in the vector PDF.

## Main files

- forest-sign-outlined.svg — preferred master. Six named layers. All lettering is
  vector outlines, so there are no font dependencies. The headline uses custom,
  reconstructed letter shapes; the footer uses outlined substitute lettering.
- forest-sign-live-text.svg — same illustration with two editable text objects.
  Uses Roboto Condensed Bold for the headline and Roboto Condensed Regular for
  the service name. These are substitute typefaces, not an identification of the
  historical lettering. Fonts are not included. Font substitution in an editor
  can change the text appearance and dimensions.
- forest-sign-vector.pdf — one-page, all-vector export of the outlined master.
- forest-illustration-isolated.svg — tree, character and flowers without the
  sign panel, lettering or emblem; transparent surrounding canvas.
- forest-service-emblem.svg — the separately editable emblem. This is the shared
  BC evergreen artwork from bc-evergreen-vector, also used in
  bc-forest-service-vector-remake.
- forest-sign-preview.png — 1122 x 1402 pixel proof of the outlined master.
- forest-sign-4x.png — 4488 x 5608 pixel PNG export.
- forest-illustration-isolated.png — transparent 1580 x 2086 pixel export.
- forest-service-emblem.png — transparent 588 x 564 pixel export.
- reference-comparison.png — supplied reference and vector remake side by side.
- palette.json — fill/stroke colour values used in the artwork.
- vector-validation.json — structural checks of the SVG and PDF deliverables.

## Editing

Each major element is grouped and individually named: sign background, smiling
tree, red-hatted character, flowers, Forest Service emblem, and lettering.
The foreground evergreen branch is in the character layer so that it overlaps
the shirt correctly. Shapes, fills, strokes and control points remain editable.
The primary master uses 78 paths, six ellipses, three rectangles and one polygon.
The PDF contains no raster images and has no font dependencies.

The outer margins of the SVG and PNG are transparent. The cream-coloured eyes,
face, boots, hands and map are intentional solid fills, not transparent holes.

## Reconstruction notes

The remake replaces source texture, irregular edge pixels and shading with flat
colour and smooth curves. The overall layout and proportions follow the supplied
image. Fine details of the small BC map, facial contours and lettering are
reconstructed approximations. This is not an authenticated historical master,
and the colours are visual approximations, not official brand specifications.
The PDF uses RGB colours and does not include printer-specific bleed or marks.

This package does not establish ownership of, or grant rights to, the underlying
historical design. No font files are included.
