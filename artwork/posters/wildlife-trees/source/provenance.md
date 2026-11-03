# Source provenance

## PofBC identity components

Repository: [https://github.com/ahzs645/PofBC](https://github.com/ahzs645/PofBC)  
Recorded revision: [`6d635f76208153909ad4a8322cd5167c15d28bbe`](https://github.com/ahzs645/PofBC/tree/6d635f76208153909ad4a8322cd5167c15d28bbe)

The seven files in `pofbc/` are unchanged copies of the source components retained during the earlier logo assembly. This is a component snapshot, not a complete PofBC application checkout. No new upstream fetch was made for the full-poster rebuild.

| Retained file | Role in the supplied logo artwork |
| --- | --- |
| `crestMark.js` | Exact `ARMS` and outlined `WORDMARK` paths for the ministry mark. Upstream: `src/assets/crestMark.js`. |
| `forest-oval-art.json` | Retained art data; the Forest Service oval uses `treeFrame` and `treeInner`. Upstream: `vendor/forestoval/bc-ministry-primitives-v5/data/art.json`. Other fields remain in the snapshot but are not used by this poster's logo assembly. |
| `mountain-ridge.svg`, `mountain-base.svg` | Supplied mountain contours used in the oval. |
| `primitives.js` | `KABEL_LETTERING` cap heights, ellipse radii, offsets, tracking and word spacing, plus separator measurements. |
| `engine.js` | Reference for the repository's curve placement and arc-length centring behavior. |
| `Kabel-Black.otf` | Supplied face used to construct the oval lettering as vector outlines. |

The retained ministry asset uses the PofBC crest and wordmark geometry. Its two supporting lines, “Ministry of Forests” and “Forest Practices Branch”, are outlined Nimbus Sans substitutions. The Forest Service oval retains the supplied frame, tree and mountain geometry, measured diamond separators, and Kabel lettering constructed from the retained font and placement parameters. The earlier assembly adapted the marks to one green ink, `#326c59`, and the poster layout.

The current rebuild imports `assets/ministry-of-forests.svg` and `assets/forest-service-oval.svg` unchanged. It adjusts their whole-asset placement using `panel-layout.json`; it does not regenerate or redraw their internal artwork. Both SVGs remain byte-identical to the previous logo assets. Their outlined lettering needs no installed font to display.

## Animal reconstruction records

`animal-source-notes/` retains the nine v2 anatomical/context mask, measured restoration, solid-repair and vector-manifest JSON files. Its README explains their scope. The corrected animal SVGs in `assets/` are prebuilt inputs to this poster rebuild; the historical animal-generation pipeline is not duplicated here.

`provenance-inputs.json` records SHA-256 hashes for the copied components, the nine animal JSON records, seven prebuilt animal SVGs, and two prebuilt logo SVGs. The copied files and SVG inputs were checked against their previous-stage originals.

## Rebuild dependencies

The current entry point is `rebuild_all.py`. It requires Inkscape on `PATH`, the Python packages in `requirements.txt`, and Nimbus Sans Regular/Bold at `/usr/share/fonts/opentype/urw-base35/`. The font files are supplied by the `fonts-urw-base35` package on Debian-based systems. The comparison proof additionally embeds DejaVu Sans Regular and Bold from `/usr/share/fonts/truetype/dejavu/`. These executables, imports and font files were present when this package was assembled.

The copied PofBC JavaScript and Kabel font are provenance inputs, not runtime dependencies of the current rebuild. The JavaScript files alone do not constitute a runnable copy of the upstream browser application. The v3 build reads the prebuilt SVGs, `reference/reference-native.jpg`, and the current registration, mask, copy and layout JSON files.
