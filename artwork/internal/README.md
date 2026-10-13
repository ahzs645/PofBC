# Internal Logos: supplied drawings

Designs in the Internal Logos view that are supplied vector reconstructions rather than Forest Oval
recipes. Each folder is the package as supplied, minus its raster previews and reference images.

| Folder | Design | Used by the site as |
|---|---|---|
| `forest-service-lands-department/` | Forest Service, Lands Department engraved seal | `src/internal/forest-service-lands-department.svg`, a **lighter copy** (below) |
| `forest-service-green-gold/` | Forest Service, green and gold oval | `src/internal/forest-service-green-gold.svg` (the main master, unchanged) |

**The Lands Department seal is shown from a lighter copy.** Its master is 5.6 MB: 11,600 shapes
with three-decimal coordinates, ids and editor labels. `forest-service-lands-department/web_copy.py`
keeps every shape, group and transform, rounds coordinates to a tenth of a unit and writes paths as
relative moves, for a 2.4 MB copy (0.6 MB compressed) whose ink overlaps the master's by 99.4% when
both are rendered at twice their size. The master itself is not kept here; `source/build_emblem.py`
rebuilds it from the geometry data in `source/` (see that folder's README), and `web_copy.py` makes
the site's copy from it.

The Forest Service evergreen emblem's package is with the posters that carry it, in
[`../posters/forest-service-emblem/`](../posters/forest-service-emblem).

The site recolours these drawings only for display, by mapping each colour the drawing paints to a
new one; the files themselves are not changed. These are reconstructions, not authenticated
masters, and imply no affiliation with or rights in the historical designs.
