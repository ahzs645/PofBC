# Recursive vector review — Revision 4

This revision works through the issues from the preceding overlay audit, then compares the corrections again in the complete assembly. The exact supplied restoration remains in its original 1191 × 1320 coordinates.

## Comparison cycles

- Preserved the Revision 3 artwork and poster exports before changing geometry; used the exact supplied 1191 × 1320 restored PNG for all native-coordinate overlays.
- Five head-region passes corrected eyes, crests, cheek fields, beaks, throat, lower panels and silhouettes; intermediate overlays caught and repaired a temporary eye-rim pinch and panel tangent kink.
- Four central-region passes plus targeted cleanup refined the small eyes, bounded teeth, lattice, arch and cuff. The final cuff taper was checked again against the source endpoint.
- Repeated side-region passes refined face, teeth, inset, ribbon, scroll and roundel; comparison and path checks removed an exposed tooth closure, a detached needle, a cream spur and two curve self-intersections.
- Five full assembled comparison snapshots checked interactions among the regions. The shared foundation was revised with the visible shapes at the upper neck, arch return, nose, scroll and lower silhouette.
- The final SVGs, PDF renders, transparent PNG, framed/print posters, detailed comparisons and eye/seam sheet were exported from the frozen sources and visually reviewed.

## Completed corrections

### Eyes and face fields

Refitted upper and lower bird eye ovoids, pupil angles, cream rims and pointed fields. Restored the small central eye surround and shared outer edge. Refined the side eye as a single black ovoid in its cream field. The six ringed pupils remain separated from their outer black shapes in the final 3× render.

### Head profiles, beaks and negative spaces

Corrected the blue-cheek boundaries and crest width, upper beak cream width and red taper, lower inlay cap/slit and separator, throat trunk and pointed arm, neck opening, arch return, lower outer curl and inner cutout. The lower blue two-cell panel has smooth shared returns and lighter borders.

### Central cuff, arm and teeth

Closed the unintended cream break below the cuff cusp, broadened the shoulder and tapered the compartment line before the cuff. Both cuff heels have uninterrupted red coverage. Repositioned bounded tooth cells and narrowed excessive dark root gaps; adjusted the continuous mouth rails.

### Lattice and tower

Replaced the repeating grid pattern with 67 explicit curved paths in coherent line families clipped to the face panel. Refined spacing, phase, bow and weight from source crossings. Adjusted the three cream tower forms to give their wings the source-like width.

### Side teeth, inset, scroll and roundel

Moved tooth divisions and returning lips, contained the lower tooth closure, removed the nostril-fork self-intersection, expanded the inset bend and aligned the blue forks with their keylines. Removed the duplicate long scroll rail and rebuilt the lower cream return with a shared boundary; the diagonal needle now joins the ribbon. Refined the roundel, petals and tail.

### Full poster proportions and footer

Removed the prior 13.3023% extra vertical stretch. The artwork now uses equal horizontal and vertical scale (1.033910034602). Reflowed the paper height, signature and footer to a 600 × 800 mm working print page; the framed page is 618 × 818 mm. The imported gallery logo geometry, English/French copy, TM and copyright credit were retained and checked.

## Export checks

- The master and expanded SVG produce identical 1191 × 1320 RGBA renders; all internal references resolve, IDs are unique, and the expanded copy has no reflected-use instances.
- All three PDFs contain native vector drawings and no embedded or inline raster images; the poster text is outlined and the PDFs require no fonts.
- The eight centre-crossing contours remain single complete paths. Inkscape SVG, MuPDF PDF and Poppler PDF checks pass; the standalone PDF is checked at native, enlarged and fractional scales.
- The final 3× transparent render has six separate ringed-pupil components and two continuous red cuff joins. The side-path report verifies closed filled shapes and no interior self-intersections in the six revised compound motifs.
- Both poster variants use uniform artwork scale, preserve all eight joined centre paths, retain the exact imported logo elements, and pass English/French/TM/credit transcription and clipping checks.
- The final artwork overlay, enlarged regional comparisons, eye/seam sheet, full poster and footer proof were inspected after export.

## Remaining limits

- Some small curve, rim-width and short tooth-edge differences of a few native pixels remain visible at high enlargement. This is a manually reconstructed master, not exact recovery of the original production file.
- The drawing keeps flat colours and exact bilateral reflection. The source PNG has texture, softened borders, shading and small left/right differences that are not reproduced.
- The central mesh reconstructs coherent line geometry rather than distressed or erased print texture. Local diagnostic measurements are not an overall accuracy percentage.
- The paper and frame dimensions are adjustable working sizes; historical physical dimensions are unverified. The signature is a manual approximation and Nimbus Sans is a Helvetica-style substitute for an unverified original typeface.

## Regional diagnostics

The table reports four-colour area disagreement and the 95th-percentile nearest-edge distance. Negative changes usually indicate a closer local match. Thin line placement, texture and blurred edges can move these values without indicating a broken shape; the enlarged visual review is necessary.

| Region | Area disagreement before → after | Edge p95 before → after |
| --- | ---: | ---: |
| upper eye | 17.173% → 10.144% | 3.606 → 2.236 px |
| upper crest | 12.031% → 7.372% | 3.606 → 2.828 px |
| upper beak | 16.109% → 8.264% | 5.385 → 2.236 px |
| upper throat | 11.752% → 5.338% | 5.385 → 2.236 px |
| lower eye | 12.737% → 9.219% | 3.000 → 2.828 px |
| lower beak inlay | 13.360% → 6.398% | 5.000 → 2.000 px |
| lower two cell panel | 14.220% → 8.442% | 2.828 → 2.000 px |
| lower outer contour | 19.548% → 8.996% | 8.544 → 3.606 px |
| central eye | 19.259% → 17.733% | 2.828 → 2.828 px |
| central teeth | 12.973% → 10.515% | 2.828 → 2.236 px |
| central lattice | 21.996% → 18.437% | 3.162 → 2.828 px |
| central hand | 4.826% → 4.367% | 2.000 → 1.414 px |
| cuff arm join | 10.341% → 5.451% | 6.403 → 2.236 px |
| side eye face | 9.873% → 4.727% | 2.828 → 1.000 px |
| side teeth mouth | 13.677% → 9.457% | 4.000 → 2.828 px |
| side blue inset | 11.562% → 7.712% | 3.162 → 2.000 px |
| side scroll roundel | 19.226% → 8.779% | 4.000 → 2.000 px |
| upper neck negative space | 20.759% → 13.205% | 5.657 → 2.828 px |
| arching brow return | 21.431% → 9.813% | 6.403 → 2.106 px |
| central tower details | 4.547% → 2.620% | 3.162 → 2.000 px |
| lower inner cutout | 11.644% → 6.184% | 5.000 → 3.162 px |

The full pass snapshots, hashes, methods and visual-review record are retained in `recursive-review.json`.
