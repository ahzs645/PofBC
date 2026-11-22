# Handbook branding components

## Three category emblems

The `svg/` folder contains 1000-square editable geometric reconstructions:

- `Ram_Head.svg`: manually constructed cubic curves for the head, spiral horn, horn divisions, eye and neck.
- `Crab.svg`: a central carapace plus mirrored claw/arm and leg components.
- `Flower.svg`: five repeated petal arcs, radial boundaries and paired veins.

No bitmap trace is embedded or used to generate these three symbols. The outer frames share a consistent rounded-square construction. The source photographs are small, so tiny line positions, claw detail and flower veins are approximate. Symmetry in the crab and radial repetition in the flower are reconstruction decisions.

`Handbook_Subject_Emblems_Review.png` shows each photographed source, reconstruction and overlay. Registration crops the frame and normalizes it to a square; it does not locally warp the source artwork. The observed printed frame corners are a little less uniform than the geometric masters.

### Photographed sources

- Ram: [The Birds: Diving Birds and Tube-nosed Swimmers, no.29](https://www.abebooks.com/Birds-British-Columbia-Diving-Tube-nosed-Swimmers/32246743715/bd).
- Crab: [Some Common Marine Fishes, no.23](https://www.abebooks.com/Common-Marine-Fishes-British-Columbia-Handbook/32246733201/bd).
- Flower: [The Orchids, no.16](https://www.abebooks.com/Orchids-British-Columbia-Handbook-No-16/32246744624/bd), cross-checked against the photographed edible-plants cover.

The source photographs document the artwork. Seller dates are not treated as verified printing dates. Photograph colours are not official calibrated ink specifications.

## Fixed typography for the handbook frames

`labels/` contains 62 fully outlined labels: the museum name, Victoria, Canada, all required title and bird-volume topic lines, and the 23 photographed handbook numbers. These use the closest inspected public modern specimen, **Neue Helvetica Pro43ExtendedLight**. The exact historical handbook typeface is not established.

The fixed wording was reconstructed from official public raster specimens by fitting straight segments and cubic curves. No font binary is included. `label_sources.json` records each exact preview URL and its bounds. These are modern comparison lettering components, not recovered historical typesetting.

```python
from label_engine import label_group, measure_label

group = label_group('British Columbia Provincial Museum',
                    x=60, y=900, width=780, color='#52675e')
```

`width` alone preserves the source proportions. Supplying both `width` and `height` explicitly fits a measured reference rectangle. Text or the filename slug may identify the fixed label. The returned SVG group contains paths only and requires no installed font.

The branding-frame templates built elsewhere use these components. Full natural-history illustrations are separate artwork, not part of these symbol and typography reconstructions.

## Source-derived handbook branding panels

`templates/all24/manifest.json` is the canonical 24-record manifest, with SVG/PNG paths relative to that directory. It maps one-to-one to the research inventory: 23 distinct handbook numbers and two separately photographed copies of no.20. `templates/all24/All_24_Handbook_Branding_Templates.png` previews the collection; six `Source_Comparison_XX.jpg` sheets compare all photographs with the templates. Each record also has source header and footer crops.

The production SVGs have only vector paths and shapes. The central illustration fields are open, with no placeholder captions. Author names, illustrations, paper wear and incidental handwriting are outside this branding-panel reconstruction. Visible title and bird-volume topic lines, handbook numbers, subject-emblem presence, and the museum footer treatment are retained. In particular, nos.36 and37 omit BCPM, and symbols are not added to covers where none is visible. No.23’s pictured header contains “Some Common / Marine Fishes”; its metadata’s longer title is not substituted.

These are normalized source-derived templates, not exact complete-cover facsimiles. Four source-specific representative layouts are additionally retained in `templates/` for edible plants20, marine fishes23, birds29 and dragonflies35. The other templates reuse the series’ panel geometry. Smooth colours approximate photographic samples; they do not establish official ink formulas.

`build_handbook_labels.py`, `build_templates.py` and `build_all_templates.py` rebuild the outlined labels and layouts. `label_sources.json` includes all public comparison-specimen URLs; no font binary or distributable font is supplied.
