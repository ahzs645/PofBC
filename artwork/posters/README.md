# Posters — source packages

The reconstruction packages behind the **Posters** view (`?view=posters`), kept as supplied: each
folder's own README says how the drawing was made, what was interpreted, and how to rebuild it. The
reference photographs and raster exports were left out; the vector masters, rebuild scripts,
palettes and validation records are here.

| Folder | Poster | Used by the site as |
|---|---|---|
| `dont-drop-it/` | DON’T DROP IT! — B. C. Forest Service | `src/posters/forest-service/dont-drop-it.svg`, unchanged |
| `dont-gamble-with-fire/` | Don’t gamble with FIRE — B. C. Forest Service | `src/posters/forest-service/dont-gamble-with-fire.svg`, **recoloured** (below) |
| `reward-living-forest/` | REWARD — A Living Forest | `src/posters/forest-service/reward-living-forest.svg`, unchanged |
| `enjoy-protect-forests/` | Enjoy & Protect our Forests | `src/posters/forest-service/enjoy-protect-forests.svg` (the outlined master), unchanged |
| `forest-service-emblem/` | The Forest Service evergreen emblem | `src/internal/forest-service-emblem.svg`, unchanged; also drawn into the two posters above |

**The gamble badge is recoloured on the site.** The supplied badge, like the photograph it was
rebuilt from, is deep blue (`#01375D`). The site sets every use of that blue — the field, the pips,
the dice outlines and the knockout stroke on “with” — in DON’T DROP IT!’s forest green (`#003E2D`), so
the two fire-prevention badges read as one series. The cream (`#F1D8AC`) is the badge’s own. The
master here is left blue; to regenerate the green one, change `BLUE` in
`dont-gamble-with-fire/source/rebuild_badge.py` or replace the colour in the SVG.

**Coastal Forest** comes from its own repository,
[ahzs645/coastal-forest-poster](https://github.com/ahzs645/coastal-forest-poster), whose
`build/build_assets.py` splits the reconstruction package into the drawing and its photograph. The
site carries those two files (`src/posters/coastal-forest/poster.svg` and `forest.jpg`) and the
panel images beside them; rebuild them there and copy them across.

None of these is an original production master, and none implies affiliation with, or rights in,
the historical designs.
