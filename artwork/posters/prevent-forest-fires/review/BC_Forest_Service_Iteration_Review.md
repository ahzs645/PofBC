# Recursive overlap review — revision 6

Revision 6 uses the delivered revision 5 as its frozen baseline. The work repeatedly followed the same loop: inspect a fixed colour comparison and missing/extra ink, change an authored shape, render the complete candidate, measure again, then accept or reject after visual review. Independent combined reviews supplied a final set of targeted corrections.

The aim is a closer visual reconstruction. None of the numbers below is a 0–10 artistic rating, and no overall “90% accurate” claim is made.

## Accepted changes

### Upper conifers

Unequal bough tiers, returning hooks, staggered pendant foliage, thinner trunk toes, connected twig tips and restrained wood scars replace repeated generic sprays. Two closing reviews deepen the small right crown and open the yellow collar beside the central flame apex.

**Selected state:** cycle16, following 19 recorded render/review cycles.
**Review record:** history/upper/README.md and ledger.json.

### Lower trunks and fallen timber

The leaning shaft is narrower, its root turns earlier, stump faces are quieter and better placed, and the main log has a more coherent exposed face and curved pendant branch. The snag shoulder and right log bend were revised after a partial rejection. Dense invented face grain was rejected.

**Selected state:** pass9_branch_bend, with the accepted isolated pale-gold material trial.
**Review record:** history/lower/LEDGER.md.

### Ground openings and fragments

Broad orange blobs become grouped directional cuts. Stepped gaps and the right fork are rejoined continuously; a central orange club becomes a short exposed end face. A root colour-only pass uses the same pale gold as the foreground wood; no additional ground geometry changed.

**Selected state:** ground pass7 geometry, then root material-colour alignment.
**Review record:** history/ground/README.md, ledger.json and root_colour/.

### Flame crest and Prevent script

Unequal curved tongues, shallower splits, left folds and a narrower right neck replace incorrect crest shapes. The central orange tip is lowered to retain its yellow collar. Five detached ribbons remain unchanged. Prevent uses individually fitted existing lowercase masters plus a new continuous capital-P outline, with a final narrower lower downstroke.

**Selected state:** root pass10, following ten recorded cycles.
**Review record:** history/root/iterations.json.

### FOREST / FIRES headline

Shared constructed letter masters receive fuller E/F/S/T forms and revised O/R contours. Occurrence-specific fitting corrects proportions and placement. A uniform six-unit ivory keyline is selected after colour review; a wider alternative with higher ivory IoU is rejected for excess visible outline weight.

**Selected state:** headline pass6.
**Review record:** history/headline/README.md, ledger.json and selected_state.json.

### TIMBER / PAYROLLS footer

Two closing cycles correct internal letter spacing, width and cap heights using bounded transformations of the existing masters. All other footer paths and both glyph master functions remain unchanged. The final frozen word boxes contain every changed rendered pixel.

**Selected state:** footer pass2_cap_heights.
**Review record:** history/footer/LEDGER.md.

## Final combined result versus the previous delivery

These measurements use the exact delivered PNG render, including all accepted modules together. Isolated iteration results may differ because adjacent layers can reveal or cover each other.

| Fixed dark-ink area | Revision 5 | Revision 6 | Change |
|---|---:|---:|---:|
| Upper trees | 74.04% | 76.08% | +2.04 percentage points |
| Lower woodland | 78.66% | 80.60% | +1.94 percentage points |
| Lower trunks and logs | 70.73% | 73.02% | +2.29 percentage points |
| Roots and ground | 88.83% | 90.28% | +1.45 percentage points |

Dark ink uses the same max-RGB < 140 rule, with the original tree regions and FIRES exclusion unchanged. The main overlap report also gives raw counts, precision, recall, sensitivity at 120/160, light cleanup, and guarded ink-edge distances. The ground has its own row so its large dark area does not conceal the remaining log and trunk differences.

### Constructed script

| Ivory script area | Revision 5 | Revision 6 | Mean edge distance, before → after |
|---|---:|---:|---:|
| Prevent | 75.48% | 83.84% | 1.91 → 1.31 px |

The script has 4,252 → 1,901 missing ivory pixels and 1,897 → 2,200 extra ivory pixels. Both changes are disclosed: increased brush coverage is useful only when the colour review still supports the letter form.

### Display headline: fill and outline measured separately

| Word | Dark fill, before → after | Ivory outline, before → after |
|---|---:|---:|
| FOREST | 84.76% → 91.41% | 39.62% → 58.46% |
| FIRES | 86.53% → 90.86% | 43.36% → 56.10% |

The headline boxes and both classifiers were frozen before headline edits. A thin outline is especially sensitive to small position and width differences; its score must be read alongside the natural-colour review. Fill and outline scores are not averaged.

### Flame crest: local orange-field checks

| Fixed local colour area | Revision 5 | Revision 6 | Mean edge distance, before → after |
|---|---:|---:|---:|
| Left flame crest | 87.27% | 89.12% | 5.16 → 4.41 px |
| Middle-left flame crest | 86.15% | 90.67% | 4.27 → 3.36 px |
| Middle-right flame crest | 87.16% | 88.52% | 2.85 → 2.67 px |
| Right flame crest | 88.10% | 90.95% | 3.85 → 3.39 px |
| Right outer flame arc | 95.91% | 96.18% | 1.09 → 1.05 px |

These are local orange-field measurements. Their rectangles also contain some lettering or bark, so they are not isolated-flame silhouette scores. The separate five yellow side-ribbon paths are retained from revision 5 and checked using the previously frozen yellow-mask scope. Nearby crest or lettering changes can affect their local colour counts even when a ribbon path is unchanged. No combined flame rating is calculated.

## How the recursion affected the decisions

- A first redraw of the lowercase script and a later uniform shift/weight treatment both made the match worse. Those results are retained, but the delivered lowercase uses the original constructed masters with individually bounded placement and brush-weight changes.
- The capital P was rebuilt as one continuous outline after the combined review exposed an angular bowl/downstroke join. A final pass narrows the bottom of its downstroke while retaining its left edge.
- A left-flame experiment made a narrow finger and adjacent tongue less convincing. It was revised before acceptance; the final folds use unequal curved tongues.
- The headline O experiment was corrected after its full render reduced agreement. The outline was then reviewed for visible weight independently of the dark fill.
- Canopy review favoured connected twig ends over a slightly higher intermediate raw score. Remaining right-crown weight and the central flame collar were reviewed after integration.
- Exposed wood received a separate pale-gold colour after the colour review showed the sky yellow made it too vivid. That colour-only stage was checked independently of geometry, so anti-aliasing changes are not described as a construction gain.

## Construction method and fixed evidence

Tree structure, flame contours, bark cuts, ground fragments and lettering are authored vector geometry. Masks never become path contours. For the script, headline and selected footer letters, bounded position, proportion and constant stroke-width parameters are fitted to already constructed letter masters, followed by exact SVG render and visual review. This is parameter calibration of editable design elements; it is not automatic bitmap tracing. Final parameter values are recorded in the source modules.

The source photograph is rectified once to 1000 × 1440 using corners (248,27), (1183,29), (1207,1423), (216,1427). Every vector is rendered at 3000 × 4320 and reduced once using Lanczos. Neither the reference nor individual trees are independently warped to improve agreement. Primary regions, exclusions and thresholds stay fixed; additional local scopes were recorded before edits in their respective areas. Qualitative detail windows may differ from measurement rectangles and are not scored as though they were frozen measurement regions.

The actual artwork contains no photograph, live text or external font dependency. The source image, masks, overlays and colour comparison boards appear only in review/analysis materials. The artwork builder itself never reads a raster reference.

## Remaining interpretation

The supplied photograph contains blur, aged ink, uneven lighting, print wear and very small broken marks. Individual needles, torn grain and tiny bark gaps remain interpreted rather than copied pixel for pixel. Some lettering contours and small spacing still differ. The separate colour/edge diagnostics and source comparison make those limits visible; the package does not claim an archival facsimile or certify a subjective 9/10.

## Files and reproducibility

`BC_Forest_Service_Refinement_Overview.png` places the fixed source, delivered revision 5 and final revision 6 side by side. Tree detail, flame detail, colour blends and missing/extra-ink maps provide larger crops. `BC_Forest_Service_Iteration_Metrics.json` contains the exact measurements used here, together with the selected source states.

The ZIP includes the editable artwork, independent vector PDF, all construction modules, final diagnostics and fixed scopes, the baseline render, source reference, per-area ledgers and source/metric checkpoints. Rejected cycles are retained as history, clearly separate from the delivered artwork. Large intermediate PNG renders are omitted where the complete source snapshot can regenerate them. Final analysis commands are in the reconstruction notes and individual reports. `SHA256SUMS.txt` records the packaged files.

## Footer word fitting

The footer record uses word areas and classifiers frozen before the closing edits. Only bounded transformations of existing glyphs were used. The ivory rule is recorded separately in the footer scope; these local word measurements are separate from the tree analysis.

| Word | Ivory overlap, before → after | Mean ivory edge distance, before → after |
|---|---:|---:|
| TIMBER | 55.18% → 83.34% | 3.00 → 1.08 px |
| PAYROLLS | 49.47% → 76.66% | 3.02 → 1.45 px |

The corresponding dark-space checks and complete pixel counts are retained in the JSON. Background agreement is not used as a substitute for ivory letter agreement.
