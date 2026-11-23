# South Cariboo Community Health Council — refined vector reconstruction

Prepared 22 November 2026. Selected reconstruction: pass07, following seven combined revision passes and separate pale-tree and lettering reviews.

## Start here

| File | Purpose |
| --- | --- |
| South_Cariboo_Reconstructed.svg | Main colour logo: 36 vector paths, transparent openings, no embedded bitmap and no installed font required. |
| South_Cariboo_Vector.pdf | One-page vector logo for print and design software. |
| South_Cariboo_Transparent.png | 2520 × 1128 transparent raster export. |
| South_Cariboo_Preview.png | 1890 × 846 white-background preview. |
| South_Cariboo_Refinement_Comparison.png | Original / earlier reconstruction / refined reconstruction, with before-and-after overlays and measurements. |
| South_Cariboo_Overlay_Analysis.png | The same current comparison board under the existing deliverable filename. |
| South_Cariboo_Tree_Detail.png | Enlarged original, refined tree geometry and continuous red/cyan overlay. |
| South_Cariboo_Interactive_Comparison.html | Self-contained browser comparison with revision toggle, opacity, wipe, source, vector, density overlay and zoom. |
| South_Cariboo_Refinement_Report.pdf | Three-page illustrated account of the changes, measurements and stopping judgment. |
| South_Cariboo_Research_and_Analysis.pdf | Updated four-page historical research and analysis report. |
| Research_and_Method.md | Research, source URLs, dates, reconstruction method and limitations. |
| Refinement_Log.md | Seven-pass revision sequence, decisions, measurement definitions and stopping rationale. |

Open the HTML locally in a modern browser. Its images and vectors are embedded; it has no network dependencies. The source raster is shown with its original pixels when enlarged, while the vector uses actual scalable SVG. Browser execution could not be visually tested in this environment; JavaScript syntax, embedded assets, measurements and element references were checked.

## What changed

The dark tree's diagonal openings, lower trunk, terminal branch, lower loop and base were rebuilt as intentional curved shapes. Pale branches and the lower hook received a separate refinement. The lettering retains native Souvenir contours, with a modest optical weight correction and small placement corrections to the three large initial capitals. Extra whole-tree translations were tested and rejected.

| Comparison window | Before foreground IoU | Refined foreground IoU |
| --- | ---: | ---: |
| Whole logo | 86.37% | 88.66% |
| Dark tree | 78.37% | 82.93% |
| Pale tree, visible window | 89.37% | 90.93% |
| Lettering on clear background | 87.19% | 89.53% |

The average whole-logo boundary distance fell from 0.50 to 0.42 source pixels. Continuous ink-density error fell 26.6% overall and 30.2% in the dark-tree window. These measure agreement with the small reference image; they are not an authenticity score. The comparison retains the original 315 × 141 coordinate frame with no additional overlay alignment. See the report and log for thresholds and window definitions.

## Editable construction and reproducible build

`construction/South_Cariboo_Branch_Model.svg` retains named branch tiers, deliberate detached twigs and negative-space masks. The portable master has two flattened tree paths plus 34 outlined glyph paths.

`construction/tree-geometry.json` contains the authored tree construction. `lettering-outlined.svg` contains the final glyphs. `lettering-optical-editable.svg` records the small optical stroke and capital offsets before expansion into fills. No font binaries are included.

From the package folder, run:

```sh
python3 construction/assemble_logo.py --export
```

This requires Python 3 and Inkscape on the command path. The current build uses the Python standard library and Inkscape; it does not read the source bitmap. It regenerates the tree paths and main SVG, then exports the white PNG, transparent PNG and vector PDF. Rebuilding in a separate folder reproduced the delivered preview pixel for pixel in the checked environment.

The construction folder also contains the alignment, typography evidence and refinement notes, measured before/after data, diagnostic overlays, export verification, viewer verification and a file manifest.

## Revision history and evidence

`revision-history/` preserves the previous master, preview, overlay board and live-text fitting reference, as well as the geometry and measurements for pass00 through pass07. The archived live-text file requires a compatible ITC Souvenir Demi font and is not the current portable master.

`evidence/` retains the colour reference, black web emblem, monochrome lockup, health-plan cover, historical orders and a source map with URLs and hashes. Source-document dates and archive captures are distinguished from design or adoption dates.

## Status and limits

This is a new historical reconstruction, not a recovered original vector master. No automatic tracing, raster-contour extraction or pixel-to-path conversion was used. Tree geometry comes from deliberate branch and negative-space construction; lettering comes from native typeface outlines.

The 315 × 141 source cannot uniquely establish every brush tip or concealed pale-tree branch. Some remaining differences are geometric interpretation, and some reflect raster edge softness and compression. Fine details have not been given unsupported extra islands merely to improve one pixel metric.

ITC Souvenir Demi remains the strongest tested typeface match; the historical vendor and exact cut are unverified. The two sampled RGB estimates, #417A3A and #9BBC95, are not official print specifications. No verified designer attribution, adoption date or official symbolism was found. Full evidence and citations are in the research report and Research_and_Method.md.

For historical display, label the asset “Reconstructed vector — colour health-plan logo” and retain the original raster alongside it.
