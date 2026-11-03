# Wildlife Trees — rebuilt vector poster

This package reassembles the corrected individual animals, the reconstructed habitat tree, the original portrait surroundings, retyped copy, clean panel rules, and the requested PofBC identity vectors in the original poster layout.

The original physical page size is **290.576 × 870.9025 mm**. The SVG coordinate system is **1000 × 2997.159090909091 units**, matching the aspect ratio of the original **4576 × 13715 pixel** source image.

## Main files

| File | Purpose |
|---|---|
| `Wildlife-Trees-editable.svg` | Layered master with selectable, editable text. Requires Nimbus Sans for the intended type appearance. |
| `Wildlife-Trees-outlined.svg` | Portable layered master with the lettering converted to vector outlines. Use this when sharing or opening on a computer without the fonts. |
| `Wildlife-Trees-vector.pdf` | Poster PDF for printing or placing in a page-layout application. Lettering is outlined. |
| `Wildlife-Trees-overlay-proof.pdf` | Registered source, reconstruction, and color-overlay comparisons for the complete poster, individual animals, tree sections, typography, and logos. |
| `Wildlife-Trees-overlay-review.html` | Self-contained offline comparison with reference, redraw, blend, wipe, and color-overlay modes; zoom and section presets are included. |
| `Wildlife-Trees-preview.png` | Convenient raster preview of the assembled poster. |

Use the outlined SVG or poster PDF for distribution. Use the editable SVG when changing the copy. In a print dialog, choose actual size or 100% to retain the supplied dimensions; fitting to a different paper size changes the scale.

The production SVGs and poster PDF were verified to contain **no embedded bitmap images**. The outlined SVG and PDF contain no live font-dependent lettering. The structural check results are recorded in `source/vector-validation.json`.

The proof PDF, HTML review, PNG preview, and files under `proof/` are visual comparison materials. They include raster views of the source and/or rendered artwork. They are separate from the editable artwork files. The HTML uses an embedded render of the vector master for responsive comparison; open the SVG itself to inspect vector geometry at arbitrary magnification.

## What was rebuilt

The artwork follows the original drawing's anatomy, branch routes, composition, and pen marks. Manually measured animal contours and tree-feature regions provide the structure. The visible source ink is reconstructed as smooth, measured-width Bézier path envelopes and organized into editable groups. Hatch marks and bark detail follow the source drawing rather than newly invented procedural textures. Small repairs to faint source-supported animal contours are documented with the animal sources.

The six corrected animals are placed using their exact native source-crop origins and dimensions. The tight cropping used for the separate animal files is undone during assembly. Their placement is therefore preserved without resizing each animal to a new visual bounding box.

The portrait branches, trunk, cavities, ground, and cast shadows are reconstructed as separate context vectors. The original frame ink is removed from those context layers and replaced with clean measured vector rules. Foreground anatomy that crosses a frame, such as the hawk's tail and the toad's left rear foot, remains outside it as in the source. Source illustrator marks are preserved in the surrounding artwork.

The habitat tree includes the source-visible crown, nest, broken branches, trunk, cavities, fungi, roots, fallen wood, vegetation, and ground details. Parts hidden by the original portrait panels remain gaps in the separate tree asset; no hidden wood or branch continuation has been invented. The full poster restores the portrait panels and their surrounding illustrations over those positions. A separate white base beneath selected solid wood is included as a removable layer.

## Separate illustration assets

`assets/wildlife-habitat-tree.svg` contains the reconstructed habitat tree and forest floor.

Each of the following animals is supplied as a separate SVG in `assets/`, together with a matching `-context.svg` for its original surroundings:

- `red-tailed-hawk.svg`
- `great-horned-owl.svg`
- `northern-flying-squirrel.svg`
- `black-capped-chickadee.svg`
- `black-bear.svg`
- `northwestern-toad.svg`

For example, `northern-flying-squirrel-context.svg` contains the surrounding branches and trunk, while `northern-flying-squirrel.svg` contains the corrected animal. The context assets use the original crop coordinate system; the assembly script supplies their exact poster placement. They are intended to be placed using the included registration data, rather than aligned to the tight outer bounds of the isolated animal SVGs.

The PofBC assets are retained separately as `assets/ministry-of-forests.svg` and `assets/forest-service-oval.svg`.

## Copy, typography, and identity marks

All wording, capitalization, punctuation, and line breaks were checked against the source. Text ink boxes, caption positions, title background, panel frames, column divider, and logo placements were remeasured against the native scan. The source wording is preserved, including its historical references.

**The original typeface has not been authenticated.** The rebuilt title, captions, and body copy use **Nimbus Sans**, fitted to the measured source line boxes. Matching those boxes does not make each letter shape identical to the printed source. The ministry support lines also use outlined Nimbus Sans. The Forest Service oval lettering uses the supplied PofBC Kabel reconstruction.

The ministry and Forest Service artwork comes from [ahzs645/PofBC](https://github.com/ahzs645/PofBC), revision `6d635f76208153909ad4a8322cd5167c15d28bbe`. Existing vector components were retained, and their whole-asset placement was fitted to the measured source ink bounds. The logo paths were not redrawn from the scan.

## Reading the overlays

Open `Wildlife-Trees-overlay-review.html` in a browser; it works offline. Select the whole poster, an animal, a tree section, the information panel, or the identity marks. Use Blend to change opacity, Wipe to move the comparison boundary, or Color overlay to distinguish source and reconstruction. Drag to pan, and use the zoom or fit controls for closer inspection.

The source is shown in magenta and the reconstruction in cyan. Aligned ink appears darker. Colored fringes can come from the scan's softness and grain, variable printed ink, fitted Bézier geometry, and replacement letter shapes. The comparison is registered to the original page coordinates; a pixel-perfect reproduction of scan noise is not claimed. The reconstructed ink is generally cleaner and stronger than the faded print, and some very faint marks are reduced.

## Editing and rebuilding

The masters contain separate layers for the paper, habitat tree, each animal and its context, captions, heading, educational copy, and identity marks. The source measurements and build scripts are under `source/`.

Key source files are:

- `source-registration.json` — exact native crop and poster-coordinate mappings.
- `panel-layout.json` — measured frames, caption exclusions, title background, divider, and logo placement.
- `poster-copy.json` — checked wording and measured text boxes.
- `tree-upper-regions.json` and `tree-lower-regions.json` — named structural regions and solid-wood bases.
- `layout-copy-audit.md` — detailed layout findings and typography limitations.

The package rebuild entry point is `source/rebuild_all.py`. Rebuilding requires Python 3, the dependencies listed in `source/requirements.txt`, Inkscape on the system path, and Nimbus Sans Regular and Bold. The supplied type builder uses the standard Linux font directory `/usr/share/fonts/opentype/urw-base35`; adjust that path in `source/build_poster.py` if your installation differs. The finished outlined SVG and PDF need none of these build dependencies. From the package folder, run:

```sh
python3 source/rebuild_all.py
```

This regenerates the tree, portrait contexts, assembled masters, PDF, previews and proofs. The proof builder also uses DejaVu Sans Regular and Bold at `/usr/share/fonts/truetype/dejavu/` and embeds them in the comparison PDF. The corrected animal SVGs and PofBC logo SVGs are supplied inputs. Their provenance and animal repair records are included under `source/pofbc/` and `source/animal-source-notes/`. To rebuild layout and exports while reusing the existing illustration assets, run `python3 source/rebuild_all.py --assemble-only`.

Keep the measured registration and crop metadata with the assets when moving or editing the package. The scripts also retain individual assembly and proof-generation entry points for targeted changes.
