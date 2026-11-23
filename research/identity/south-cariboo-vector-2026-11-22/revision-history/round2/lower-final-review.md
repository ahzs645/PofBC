# Final local lower-tree review and proposal

Principal source: `baseline/South_Cariboo_Vector/evidence/source-colour-logo.png` (315 × 141). Review began with candidate04; the isolated final render uses candidate05 as its unchanged starting model. Candidate04 and candidate05 have the same retained dark path geometry. Candidate05's pale geometry is retained without alteration.

## Outcome

There were meaningful missing lower-tree structures, not merely fringe differences. Four local regions were corrected in the proposal. The final reviewed rendering is **lower-final04/**. Earlier lower-final01–03 directories are intermediate review steps.

**Integration file:** `lower-final-proposal.json`. It has nested `dark` and `dark_voids` dictionaries. Every path is manually authored in SOURCE coordinates. Apply inverse FIT before insertion into the construction model. Include the new `dark.base_edge_bridge` key, not only replacements of existing keys.

No master geometry was modified. No raster contour extraction or automatic vectorization was used.

## Four local corrections

### 1. Inner return below the y100 lobe

The small lobe's upper and outer form is reasonable. Its return below the white bay was too open: candidate04/05 omitted substantial source ink at x20–23/y105–107. The correction changes only the first upper sweep of `left_10`, filling that return. The outer `left_09` silhouette is unchanged. A tiny unintended joining sliver in the first local trial was filled before the final render.

### 2. Hook and inner green tongue

The source has a strong green tongue at x12–15/y119–122. Candidate04/05 made most of this region white and moved the tongue's termination to around x16. Its diagonal opening also began too far right around y116–118.

The proposal restores the inner tongue through `left_11` and reshapes `branch_11_gap` as a directional cut. This preserves the source's interleaved branch structure instead of a single large clean white opening. The lower bowl itself is retained.

### 3. Diagonal base cuts, with the ink bridge retained

The source supports a thin diagonal ink bridge between the upper light chip near x29/y131 and the lower diagonal gash. It does not support indiscriminately merging those into a broad continuous opening. The source has full dark ink at x27–28/y133, with partial mixed coverage farther left near x25–26.

`base_break_01` becomes an irregular light chip with a better upper extent. `base_break_02` becomes a tapered diagonal gash, aiming toward x26.5/y133.3 and falling toward x21/y135–136. This removes the candidate's rectangular head around x24–26/y134–136 while retaining a narrow positive ink bridge between the two cuts.

### 4. Base edge, right stem and crossing near y137

The candidate's long uninterrupted white separation through x32–34/y133–140 was structurally wrong. The colour source has:

- An upper light slit around x33–34/y134–136.
- A clearly dark crossing around y137: source projected ink density is approximately .99 at x33 and .90 at x34.
- A lighter exit below that crossing.
- Substantial right-stem ink at x35–36/y131–137, including through y133–134.

The added `base_edge_bridge` restores the fuller main edge, the right stem and the crossing. `base_gap` is replaced by a compound path with a short enclosed upper slit and a separate narrow bottom break. This avoids the earlier clean continuous white split. A tiny accidental upper triangular hole caused by the first patch junction was closed and re-rendered before delivery.

## Visual review

Useful final boards:

- `lower-final04/base-review.png`
- `lower-final04/hook-review.png`
- `lower-final04/lobe-review.png`
- `lower-final04/lower-review.png`
- `lower-final-native.png` (source / candidate05 / proposal at native size and 4×)

The native-size comparison shows the restored green hook tongue and denser, connected base structure. These are perceptual changes to the arrangement of strokes and openings, not just numerical improvements at enlarged scale.

## Fixed-region check

Threshold IoU uses the unchanged .75 projected ink-density threshold. Continuous density error is mean squared error. All windows are fixed in source coordinates.

| Region | Candidate05 IoU | Final proposal IoU | Candidate05 density MSE | Proposal density MSE |
|---|---:|---:|---:|---:|
| Inner lobe return, x16–24/y102–108 | .6842 | .9231 | .10688 | .00310 |
| Hook, x8–21/y114–124 | .6400 | .8391 | .17140 | .03855 |
| Diagonal base cuts, x20–31/y129–137 | .8065 | .9326 | .05572 | .01181 |
| Base edge, x31–35/y132–139 | .3438 | .9286 | .29176 | .01297 |

Whole dark IoU: **.87528 → .89286**.

Dark lower IoU: **.81021 → .87132**.

Dark lower continuous density error: **.04349 → .02784**.

The source remains a small raster, so the exact physical width of the thinnest bridge cannot be recovered with certainty. The chosen construction preserves the visible distinction between two cuts and the well-supported dark crossing at y137. No claim of recovering original master paths is made.
