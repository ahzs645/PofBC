# South Cariboo — one shared tree master

Current revision: **shared-master-soft-crown-v2**, 22 November 2026. This version implements the user's explicit assumption that the two trees reuse exactly the same illustration.

## Start here

| File | Purpose |
| --- | --- |
| South_Cariboo_Reconstructed.svg | Main editable logo: visible dark master and one linked pale SVG use. Editing the master updates both. |
| South_Cariboo_Expanded.svg | Visually identical compatibility SVG with the clone expanded. Its copies are no longer linked. |
| South_Cariboo_Tree_Master.svg | Standalone tree artwork. |
| South_Cariboo_Vector.pdf | Path-based logo export. |
| South_Cariboo_Transparent.png | 2520 × 1128 PNG with transparency. |
| South_Cariboo_Preview.png | 1890 × 846 white-background preview. |
| South_Cariboo_Interactive_Comparison.html | Offline source / previous / current comparison with wipe, opacity, density and actual SVG zoom. |
| South_Cariboo_Overlay_Analysis.png | Source / previous crown / softened crown comparison. |
| South_Cariboo_Crown_Comparison.png | The same focused treetop comparison under a descriptive filename. |
| South_Cariboo_Refinement_Report.pdf | Current assumption, visible differences, linked construction and validation. |
| South_Cariboo_Research_and_Analysis.pdf | Historical research with current artwork and overlay analysis. |

## How the link works

The dark tree contains the single `tree-master` element. The pale tree references it with SVG `<use>`. It uses the exact same filled paths, openings and detached brush marks. Its only changes are pale green fill, uniform 5/6 scale and translation of approximately (53.2773, 23.0667) source units after scaling. There is no pale-specific canopy, masking exception, or separate fleck.

In an SVG editor that supports linked clones, edit the dark master to update both trees. `construction/South_Cariboo_Branch_Model.svg` exposes named component branches and negative-space cuts while retaining the same linked relationship. The expanded export is provided for applications that flatten or do not preserve SVG clone relationships.

The main tree body is connected. A source-supported narrow lower stroke was restored to join a previously detached twig. Eight intentional detached brush flecks remain in the master artwork and are reused identically; they are not joined with invented connecting lines.

## Build from the authored components

```sh
python3 construction/assemble_logo.py
```

Python3 and Inkscape are required. `construction/shared-tree-model.json` contains one master only. The build reads no source raster and uses no automatic tracing or contour extraction. Lettering remains outlined, with no installed-font dependency.

## Comparison and limits

| Source comparison window | Previous version | Exact shared-tree version |
| --- | ---: | ---: |
| All | 91.51% | 79.41% |
| Dark | 89.19% | 89.33% |
| Pale | 94.43% | 65.86% |
| Type | 89.53% | 89.53% |

The complete-copy assumption reduces agreement in the pale right-hand area, which looks more solid in the source. This is the expected visible tradeoff of exact shared geometry. Matching repeated branch features supports the common underlying illustration, but does not prove that the historical pale silhouette was an untouched duplicate of every dark contour.

Eleven manually selected source features fit the simple 5/6 scale and translation with approximately 0.40 px RMS error, within their reading uncertainty. No relative skew or rotation is used.

The previous, closer source-fitted version is preserved under `revision-history/Before_Exact_Shared_Master/`. The historical sources and attribution limits remain in Research_and_Method.md and Source_Search_Followup.md. These files do not claim recovery of an original vector master.

## Verification

The linked and expanded SVGs render pixel-identically. A temporary edit to the dark master changed both tree instances, with no changes outside the expected tree areas; that test edit is absent from the deliverable. The logo PDF contains vector drawing objects, no bitmap and no font dependency. The HTML passed syntax and embedded-asset checks; browser execution was not visually tested here.


## Treetop cleanup

The shared crown has a softly rounded apex, fewer small staircase corners, and smoother unequal shoulders. Its lean and main branch proportions are retained. Only master.ink.crown changed; the live pale copy updates automatically. The former crown is preserved in revision-history/Before_Crown_Cleanup/.
