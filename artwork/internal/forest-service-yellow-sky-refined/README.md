# Forest Service - British Columbia

## Refined vector reconstruction

This updated package recreates the supplied emblem as editable vector artwork. The master SVG has a transparent exterior, outlined lettering, flat fills, named layers, and individually editable illustration shapes. The PDF contains the same vector artwork for scalable placement and printing. PNG files are previews and comparison aids.

## Main files

- `Forest_Service_BC_Reconstructed.svg` - editable vector master.
- `Forest_Service_BC_Reconstructed.pdf` - vector export, with a 200 mm wide page.
- `Forest_Service_BC_Transparent.png` - transparent preview, 3000 pixels wide.
- `Forest_Service_BC_Preview.png` - smaller preview on white.
- `Forest_Service_BC_Comparison.png` - supplied image and refined vector at matched scale.
- `Forest_Service_BC_Overlay.png` - registered 50/50 source/vector blend.
- `Forest_Service_BC_Refinement_Comparison.png` - reference, previous vector, and refined vector.
- `Forest_Service_BC_Refinement_Details.png` - before/after illustration close-ups.
- `Forest_Service_BC_Palette.gpl` - the flat RGB palette.
- `review/` - measured overlap report, exact pixel counts, and color-coded diagnostics.
- `source/` - final vector components, border controls, portable assembly code, and construction notes.

## What was refined

The weaker C, R, S, M, B and A letterforms were reconstructed with dimensioned typographic curves. Existing letters retain their individual position, rotation and proportions. Both outside borders were recalibrated as four-arc oval centerlines with consistent-width strokes. The interior window was also recalibrated.

The central evergreen's bough shapes, hanging tips, green openings and dark cuts were refined. The mountains received revised cliff columns, snow cuts and ridge marks. The small shore trees now have distinct irregular silhouettes. The foreground saplings, long terrain loop, root fan and small marks were redrawn and calibrated; lake ripples were adjusted to the reference.

The geometry was designed as recognizable drawing elements and refined against the image. No bitmap contour-to-path tracing was used. The SVG contains no embedded raster images, live text, linked fonts, filters, or external assets.

## Measured before / after comparison

| Selected region | Previous vector | Refined vector |
| --- | ---: | ---: |
| Lettering | 92.8% | 95.3% |
| Two outer border strokes | 82.5% | 93.2% |
| Central canopy silhouette | 88.7% | 95.7% |
| Central canopy dark details | 50.0% | 77.7% |
| Lower scene dark details | 40.6% | 68.0% |
| All dark marks | 75.8% | 87.7% |

These are intersection-over-union (IoU) measurements of selected masks, not an overall percentage of visual fidelity. IoU counts matching occupied pixels divided by pixels occupied by either mask; blank canvas does not increase it. Both versions were rendered in the original 1709 x 2048 source coordinates without an additional registration warp. The lower-scene region is held fixed between versions. See `review/Forest_Service_BC_Overlap_Report.md` for method and limitations, and the JSON for exact counts and threshold sensitivity.

## Editing

The seven top-level layers are:

1. Outer oval, cream trim and olive band
2. Golden sky
3. Mountains, shore, lake and foreground
4. Central evergreen and trunk
5. Interior oval boundary
6. Outlined lettering
7. Side separator dots

The landscape and central tree are clipped to the interior window. If the window changes, update both the clip path and visible interior outline. Each letter is an independent outlined path; no font installation is required. Fills and strokes are ordinary SVG attributes. The outside of the emblem is transparent.

## Rebuilding the exact vector composition

Use Python 3.9 or newer:

```sh
python source/rebuild.py
```

This reads the three final SVG components and the border/window control data, then writes the master SVG in the package directory. It uses only the Python standard library and needs no font files or reference image. The final component SVGs are the canonical editable construction sources; the previous revision's drawing scripts have been superseded by these refined components.

## Reference and remaining differences

The reference is a supplied generated image (Gemini), 1709 x 2048 pixels: a restoration-style picture of the emblem, not a photograph of it. This recreates that image. No separate archival master, confirmed historical typeface or official color specification was supplied. Soft raster edges and surface color variation are represented by crisp vector curves and flat fills. Some fine branch, mountain and terrain details still differ; the comparison images make those differences visible.

Updated 2026-11-20.

## In this repository

The site shows `Forest_Service_BC_Reconstructed.svg` as `src/internal/forest-service-yellow-sky.svg`, with its title and description reworded. Its reference is a generated image, not a photograph, so the page says so. The earlier redraw from the two photographs is no longer shown; its package stays in `../forest-service-yellow-sky/`.

Left out, as from every source package here: the PNG previews and comparisons (`Forest_Service_BC_Comparison.png`, `_Overlay.png`, `_Refinement_Comparison.png`, `_Refinement_Details.png`, `_Transparent.png`, `_Preview.png`, and the PNGs in `review/`), which show the generated reference or are raster previews.
