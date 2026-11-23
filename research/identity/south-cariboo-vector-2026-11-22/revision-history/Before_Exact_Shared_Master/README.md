# South Cariboo Community Health Council — rebuilt vector trees

Prepared 22 November 2026. Current revision: **round2-candidate07**. The earlier delivered pass07 was reopened after the user correctly identified weaknesses in the trees.

## Files

| File | Purpose |
| --- | --- |
| South_Cariboo_Reconstructed.svg | Portable colour logo with two tree paths and 34 outlined glyph paths; transparent openings and no installed font dependency. |
| South_Cariboo_Vector.pdf | Vector logo for printing and design software. |
| South_Cariboo_Transparent.png | 2520 × 1128 transparent PNG. |
| South_Cariboo_Preview.png | 1890 × 846 white-background preview. |
| South_Cariboo_Overlay_Analysis.png | Equal-scale source / rejected pass07 / current tree comparison and measured changes. |
| South_Cariboo_Tree_Detail.png | Original trees, sharp current vector and continuous red/cyan overlay. |
| South_Cariboo_Native_Comparison.png | Full lockups compared at the original 315 × 141 size. |
| South_Cariboo_Interactive_Comparison.html | Offline viewer with previous/current revisions, opacity overlay, wipe, source/vector views, density overlay and direct SVG zoom. |
| South_Cariboo_Refinement_Report.pdf | Three illustrated pages describing the rebuilt trees and comparison method. |
| South_Cariboo_Research_and_Analysis.pdf | Four-page historical research report with current artwork and analysis. |
| Research_and_Method.md | Historical sources, method and uncertainties. |
| Source_Search_Followup.md | Focused additional archive search and its limits. |
| Refinement_Log.md | This round's construction decisions, progression and measurements. |

Open the HTML locally in a modern browser. All assets are embedded. The source retains its native pixels when enlarged; the vector view scales the actual SVG. Browser execution was not visually tested in this environment; embedded assets, JavaScript syntax and control references were checked.

## What was rebuilt

The previous trees were too regular, with broad rounded shelves and weak lower connections. This round rebuilt the crown, directional left sweeps, thin interrupted right tips, inner openings, hooked lower stroke and root crossings. Unsupported detached marks were removed. A final local cleanup gave the small interior openings uneven curved shoulders instead of mechanical polygon corners.

Eleven manually paired features support a shared branch pattern at approximately five-sixths scale. The pale tree now derives from that authored structure, with separate right-side completion and a small independent basal fleck. This is a reconstruction hypothesis; the original vector master has not been recovered. The lettering remains the previously fitted Souvenir outline construction.

| Comparison window | Previous pass07 overlap | Current overlap | Mean boundary distance |
| --- | ---: | ---: | ---: |
| All | 88.66% | 91.51% | 0.418 → 0.322 px |
| Dark | 82.93% | 89.19% | 0.689 → 0.443 px |
| Pale | 90.93% | 94.43% | 0.696 → 0.463 px |
| Dark lower | 77.47% | 87.23% | 0.671 → 0.397 px |

These values support the visual comparisons. They do not establish that every reconstructed brush mark is exact. Detailed definitions are in the log and report.

## Editable construction

`construction/South_Cariboo_Branch_Model.svg` retains named branch shapes, deliberate detached marks and negative-space masks. `construction/tree-geometry.json` is the component source. The main SVG flattens the two trees for reliable application use while keeping their openings transparent. The lettering is outlined and contains no font binary.

To rebuild the delivered artwork:

```sh
python3 construction/assemble_logo.py --export
```

This uses Python 3 and Inkscape. It reads only the authored JSON/SVG construction, not the reference bitmap. An isolated rebuild was checked against the delivered preview. The optional `regenerate_shared_pale.py` helper updates the shared pale branches after edits to the dark master; it requires NumPy and svgpathtools. Its preserved `completion_*` and `instance_*` components remain independently editable.

## Evidence, history and limits

`revision-history/Previous_Pass07_Deliverable/` preserves the user-rejected prior deliverable. `revision-history/round2/` records this round's candidate geometry and measurements. Earlier optimistic review notes are explicitly superseded. The evidence folder retains the source raster and corroborating historical material.

No automatic tracing, raster contour extraction or pixel-to-path conversion was used. The trees are deliberate vector constructions based on observed branch forms and voids. Exact fine brush ends and hidden pale-tree structure remain interpretive. Some remaining differences are geometry, and some reflect raster edge softness; they should not all be attributed to compression.

ITC Souvenir Demi is the strongest tested typeface match; the historical vendor and exact cut are unverified. The sampled RGB estimates #417A3A and #9BBC95 are not official print specifications. No verified original vector, designer attribution, adoption date or official tree symbolism was found. Full sources and qualifications are in the research files.
