# V2 animal reconstruction records

These nine JSON files are unchanged records from the corrected, isolated-animal reconstruction stage. They document how the source-visible anatomy was separated, which small source-supported features were repaired, and how the resulting SVGs were registered.

| Files | Recorded purpose |
| --- | --- |
| `raptors-masks.json` | Hawk and owl silhouettes, anatomical regions, and source occlusions. |
| `small-animals-masks.json` | Flying squirrel and chickadee silhouettes and anatomical regions. |
| `bear-toad-masks.json` | Bear and expanded-crop toad masks, measured regions and crop notes. |
| `hawk-context-mask.json` | Observed perch and supporting context for the separate hawk-with-perch variant. |
| `raptor-restorations.json` | Two faint, source-measured hawk head/cere contour restorations. |
| `small-animal-restorations.json` | A short, source-measured squirrel rear-ear rim restoration. |
| `bear-ear-repair.json` | Narrow reconstruction of the bear's near-ear ink core and its observed white flecks. |
| `toad-eye-repair.json` | Measured toad pupil and one observed highlight. |
| `vector-manifest.json` | V2 artwork metadata, registration and reconstruction/repair records. |

The current full-poster build uses the corrected **prebuilt SVGs** in `../../assets/`: red-tailed hawk, great horned owl, northern flying squirrel, black-capped chickadee, black bear and northwestern toad. It restores their original positions from SVG registration metadata and the current `../source-registration.json`. It rebuilds each portrait's surrounding scenery separately. The prebuilt hawk-with-perch SVG is also retained as an alternate asset.

This directory is a documentation snapshot, not a second animal-regeneration pipeline. The v2 reconstruction scripts and their separate crop/proof package are not duplicated here, and `../rebuild_all.py` does not reapply these repair JSONs. Their repairs are already present in the supplied animal SVG inputs. Reapplying them independently could duplicate artwork.

Paths to v2 `reference/` crops, diagnostic grids or proof images inside these records describe the historical evidence locations. They are not additional dependencies of the current poster build. The current source scan is `../../reference/reference-native.jpg`; the current registration data records the original native crop coordinates, including the toad's expanded left edge.

All nine copied JSON files and the seven prebuilt animal SVGs were checked for byte identity with the v2 originals. Their hashes are recorded in `../provenance-inputs.json`. Current build dependencies are documented in `../provenance.md` and `../requirements.txt`.
