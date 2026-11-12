# British Columbia Steamship Company (1975) Ltd.

## Finalized round logo

The primary circular logo has been corrected against the latest supplied reference and checked with a fresh overlay. Use `bc-steamship-round-logo.svg` as the editable master.

This is a constructed vector reconstruction. The C, S, lowercase s, y, 5 and 7 use explicit, sparse Bezier masters. Other lettering starts with native Roman serif outlines, optically scaled and placed around the circle. Repeated letters share one master shape. The full mark contains 54 filled vector paths, with no embedded raster, live text, mask, filter or external font dependency.

### Corrections completed

- Fuller C bowl and inward terminal; rounded upper/lower S terminals and broader S body.
- Rounded lowercase s/y details and corrected 5/7 numeral forms.
- Individual optical size, width, rotation and spacing adjustments throughout the inscription.
- Correct company wording: **British Columbia Steamship Company (1975) Ltd.** The extra d and punctuation in the reference are omitted.
- Heavier outer border and inner emblem ring, corrected inner-to-outer proportion, and corrected separator dot.
- Refined stem, bar, facets and waves in the central emblem using symmetric analytic geometry.

### Main files

| File | Use |
| --- | --- |
| bc-steamship-round-logo.svg | Editable black vector master; transparent background. |
| bc-steamship-round-logo-white.svg | White vector for a dark background. |
| bc-steamship-round-logo.pdf | Vector PDF for print and interchange; no embedded image or font. |
| bc-steamship-round-logo.eps | Vector EPS interchange export. |
| bc-steamship-round-logo-3200.png | Transparent 3200 x 3200 PNG. |
| bc-steamship-round-logo-preview.png | Preview on white. |
| bc-steamship-round-comparison.png | Supplied reference, preceding revision, final vector and final overlay. |
| bc-steamship-final-overlay.png | Unannotated full-logo overlay. |
| bc-steamship-final-lettering-overlay.png | Lettering-only overlay with the intended wording. |
| validation.json | Export, structure, reproducibility and overlay checks. |

The earlier standalone `bc-steamship-emblem.*` and `bc-steamship-wordmark.*` assets remain separate token/name-strip-based reconstructions. Their earlier evidence and notes are retained in `references/README-before-finalization.md`. The finalized full round logo follows the newer supplied circular reference and has its own corrected central geometry.

## Editing and regeneration

Open the SVG in Inkscape, Illustrator, Affinity Designer or another vector editor. All lettering is outlined, so the artwork does not depend on installed fonts. Change the main groups' fill to recolour it. The viewBox is 1500 x 1500.

`source/round-inscription-parameters.json` contains the explicit glyph masters and per-character placements. `source/rebuild_round_inscription.py` reconstructs the inscription from that data with FontTools. It reads no bitmap and needs no installed font. `source/rebuild_round_geometry.py` contains the sparse analytic circle, facet and wave parameters. `source/assemble_round.py` combines these sources.

```sh
python3 source/rebuild_round_inscription.py
python3 source/assemble_round.py
inkscape bc-steamship-round-logo.svg --export-filename=bc-steamship-round-logo.pdf
inkscape bc-steamship-round-logo.svg --export-filename=bc-steamship-round-logo.eps
inkscape bc-steamship-round-logo.svg --export-filename=bc-steamship-round-logo-3200.png --export-width=3200
```

The included recipe was run and verified to reproduce the final SVG exactly. `source/rebuild_all.py` also refreshes the earlier separate emblem/name-strip/provisional assets and therefore needs the older fonts documented in its source; those fonts are not needed to regenerate this finalized circular logo.

## Overlay and evidence

Cyan indicates reference-only ink, magenta vector-only ink, and dark areas overlap. The final artwork uses one uniform reference-to-vector transform. The outer and inner rings are clean, concentric circles; the supplied image's small ovality and asymmetries are not copied. Both geometry and lettering are checked separately so the large centre emblem cannot hide letter differences.

The common-wording overlap measure stops after the complete closing parenthesis in (1975), excluding the final ending in both versions because the source contains extra characters. Measurements are fit-to-reference diagnostics, not font-identification confidence or historical-authenticity percentages.

The original historical font remains unconfirmed. Native Nimbus Roman Bold and Liberation Serif Bold curves were used as construction starting points for the ordinary letters, alongside the six explicitly redrawn characters. No bitmap contour was automatically traced. Black and white are neutral exports; the supplied images do not establish historical corporate ink colours.

Supplied references and preceding revisions are retained under `references/`. The previous token study under `studies/` is historical working material and is not the finalized logo.
