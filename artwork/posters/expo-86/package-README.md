# Expo 86 — complete vector poster reconstruction

This package recreates the photographed poster with Robert Davidson’s artwork, the Expo 86 logo, bilingual event information, the artist’s 1985 signature, and the original artist/copyright credit. It provides a charcoal-framed presentation and a clean poster print. The auction sticker, glass reflections, wall, and surrounding objects have been omitted.

## Files and editing

The deliverables are in `output/`. The `work/` folder contains the composition and validation scripts, native component assets, and source notes; `upload/` contains the supplied photographs used for this poster layout. Open the SVG or PDF directly to use the artwork. Rebuilding with the scripts requires Python, Inkscape, Poppler, Nimbus Sans, and the Python packages listed in their imports.

| Version | Main deliverables | Text-editable source |
| --- | --- | --- |
| Framed presentation | `expo86-poster-framed.svg`, `.pdf`, `.png` | `expo86-poster-framed-editable-text.svg` |
| Poster print | `expo86-poster-print.svg`, `.pdf`, `.png` | `expo86-poster-print-editable-text.svg` |

The main SVGs and PDFs contain native vector geometry with the visible type converted to outlines. They preserve the lettering’s appearance without requiring installed fonts. PNGs are rendered previews. The editable-text SVGs retain live text for wording and typography changes; the artwork, logo, and reconstructed signature remain editable vector shapes.

The live text uses **Nimbus Sans**, a close Helvetica-style substitute. The original typeface has not been verified. Use the outlined versions when consistent appearance matters; editing the live-text versions requires Nimbus Sans or a deliberate replacement font. Separate groups identify the frame, paper, artwork, signature, logo/TM, bilingual text, and bottom credit.

## Artwork, layout, and size

The composition imports the corrected **Revision 4** artwork from `expo86-recreated-expanded.svg`, preserving the recursively reviewed eyes, line joins, teeth, lattice, outer curves and continuous central geometry. One uniform placement transform applies to the complete artwork: **1.0339100 horizontally × 1.0339100 vertically**. Its target ink bounds are **(2.4, 12.16)–(1197.6, 1350.0396)** on a **1200 × 1600** paper coordinate grid.

The working print size is **600 × 800 mm**; the framed version is **618 × 818 mm**. These are adjustable reconstruction dimensions, not verified measurements of the historical print or frame. The dark bevelled frame is a reconstruction of its visible appearance.

The earlier poster introduced an extra **13.3023% vertical stretch** at the same artwork width. This revision removes it and reflows the signature, paper height and footer around the artwork's reference proportions. The page height therefore changes; the artwork itself keeps the same aspect ratio as the supplied restoration. The photographs guide the relative footer placement, but are not warped to claim an exact overlay of this reflowed page.

`expo86-poster-review.png` shows the current composition and enlarged footer. The native-coordinate artwork comparisons and correction record are included as `expo86-detail-review.png`, `expo86-overlay-50-percent.png`, `recursive-review-notes.md` and `recursive-review.json`. `poster-validation.json` records the actual uniform placement, exact copy, preserved logo geometry and PDF checks.

The palette used throughout is:

| Element | Colour |
| --- | --- |
| Paper / cream | `#FBE5C1` |
| Black | `#25282B` |
| Red | `#C9231D` |
| Blue | `#88ACB3` |

## Lettering and signature

The event copy follows the supplied close-up, including the English date **“May 2-October 13, 1986”** with its tight hyphen. The French date reads **“Du 2 mai au 13 octobre 1986”**. Both language blocks retain the photographed hierarchy of bold headings and date, with regular location lines.

The bottom credit is preserved:

> ARTIST: ROBERT DAVIDSON   © THE EXPO 86 CORPORATION   PRINTED IN CANADA

The fine credit uses 4.1 poster-coordinate units, with its deliberate spaces preserved in the editable source. The photographed **Robert Davidson 1985** signature was reconstructed manually with rounded Bézier strokes. Its principal forms and spacing are retained; tiny pen overlaps remain interpretive because the photograph is soft and reflective.

## Sources and provenance

The poster references are the supplied `46925791_1(1).jpg`, `46925791_2.jpg`, and `46925791_3.jpg`, supported by `46925791_1m.jpg` and `Restored multicolour Expo 86 artwork(1).png`.

The stacked Expo logo uses the exact imported geometry from the [user-specified PofBC gallery](https://projects.ahmadjalil.com/PofBC/?view=gallery&logos=collected-expo-86-corporation), recoloured to the poster’s black. **TM** is a separate mark. The source is pinned to [the SVG at commit `1fb9e08dbb105bd691bed0790c81365b46ebc4f0`](https://github.com/ahzs645/PofBC/blob/1fb9e08dbb105bd691bed0790c81365b46ebc4f0/public/identity-collected/expo-86-corporation/expo86-symbol.svg). Its provenance record identifies a modern SVG reconstruction credited to Mwtoews/Wikimedia Commons.

This deliverable preserves the artist and copyright attribution while distinguishing reconstructed geometry, photographed layout estimates, and substituted typography. Detailed visual and export checks are documented separately.
