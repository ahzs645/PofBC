# Heraldic emblem — vector reconstruction

This package reconstructs the artwork supplied as “Lion and stag heraldic emblem(1).png”. The source canvas is 1470 × 1070 pixels. The master SVG preserves that coordinate system and can scale to any size.

## Files

- **heraldic-emblem.svg** — main editable vector artwork; transparent background.
- **heraldic-emblem.pdf** — one-page vector export for placing in documents or printing.
- **heraldic-emblem.png** — transparent PNG, 4000 pixels wide.
- **heraldic-emblem-preview.png** — white-background preview at the source size.
- **source-comparison.png** — supplied image and rebuilt artwork at equal scale.
- **detail-comparison.png** — enlarged comparisons of the faces, antlers, horns, and crown.
- **components/** — separate SVG elements, all in the same original coordinate system.

## Reconstruction

The shield, sun, waves, Union flag, and ribbon forms were rebuilt with clean vector geometry. The original arrangement and its asymmetries were retained. Animal and crown linework was isolated from the source and fitted with smooth Bézier curves. A reduced palette replaces most fine print grain while retaining the directional engraved markings.

The motto remains **SPLENDOR / SINE / OCCASU**. Its 18 original letterforms were individually isolated and converted to outline paths, preserving placement, rotation, counters, and spacing. They do not require a font installation and are not live editable text.

The facial details received a separate pass to preserve the lion’s eye highlights, the stag’s iris and mouth, and the ram’s iris and nose. The 17 larger crown pearls were rebuilt as native ellipses with restrained shading.

## Editing

The master has named groups/layers for the scroll and motto, shield, stag, ram, lion, crown, and small facial details. The crown includes its separate pearl group. Colour planes and engraved linework are separate within the animal groups.

For a flatter ribbon, hide the **scroll-engraving** group. The animal engraving is also separately grouped. Some filled paths contain several subpaths; an editor’s break-apart operation can expose individual marks if needed. The standalone components share the master coordinate system, so they overlay without manual positioning.

## Verification and limits

The SVG contains only vector shapes and clipping paths, with no embedded raster image, external asset, or live text. The PDF export contains no raster image objects. Both exports were rendered and visually checked. Close checks covered the antler openings, ram’s horn opening, facial features, paws and hooves, scroll folds, lettering, and crown.

This is a reconstruction of the supplied raster artwork. Smooth fills and reduced paper texture are intentional; the file is not an untouched original production vector.
