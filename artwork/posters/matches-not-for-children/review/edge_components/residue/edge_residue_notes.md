# Optional edge residue

`edge_residue.svg` and its generator, `edge_residue.py`, contain six manually drawn paths. Four describe the pale film and short pigment deposits above the child’s right match head; two describe a faint fringe below the upright foot. The corresponding features are visible in the supplied photograph. The shapes retain only the clearest local deposits, without adding general grain or simulated aging.

**Placement:** clip `optional-edge-residue-v3` to the union of the final white reserve paths. Insert it after the reserve fill and before the black illustration. All colours are opaque and already pale; there are no opacity attributes, raster images, filters, or noise. The reserve geometry and its alpha-mask measurements remain unchanged.

The leg ridge provides the clearer case for inclusion. The upright-foot effect is intentionally slight. A stronger initial foot patch was reduced because it read as a new stain rather than a thin pigment fringe. Keeping the foot pair as an optional subgroup is reasonable if the desired final treatment is cleaner.

`edge-residue-decision-board.png` shows the photograph, the clean V3 geometry, and the same geometry with the clipped layer. The comparison uses the final child paths and the available V3 upright path, retaining the existing paint and black drawing. `review_edge_residue.py` regenerates this review without modifying those source files.

The pale colours were informed by small representative photographic samples and judged visually. They are not a calibration of the original print. The layer suggests observed paint residue; it does not reproduce every diffuse pigment deposit or the photograph’s grain.
