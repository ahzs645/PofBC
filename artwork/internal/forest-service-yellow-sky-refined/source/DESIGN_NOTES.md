# Construction sources

The files in `components/` contain the final editable paths. `rebuild.py` combines them with the four-cubic border models and the four-cubic interior window. Its output is the same visible vector composition as the delivered master.

`landscape.svg` combines the refined mountain and shore illustration with the independently refined lake, saplings and ground paths. `central-tree.svg` combines the refined canopy with the coordinated lower root flare. `lettering.svg` contains all 28 outlined characters. These are geometry sources, not raster embeddings.

The original drawing was composed from semantic vector forms: oval arcs, individual glyphs, a tree leader and bough whorls, mountain ridges and snow cuts, distinct small conifers, water ripples, roots and terrain marks. Refinement used bounded edits to those authored shapes, including positions, sizes and curve controls. Pixel-mask comparison was used to evaluate the reconstruction; source image contours were not converted into output paths.

Lettering construction notes and placement metadata are included alongside the components. The exact original typeface is not identified. The geometry is already outlined, so font availability cannot change the delivered composition.

The old revision's standalone drawing scripts are omitted because they do not recreate the refined result. Use the current components and `rebuild.py` for an exact reconstruction of this revision.
