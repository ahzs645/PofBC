# Pins: source packages

The reconstruction packages behind the **Pins** view (`?view=pins`), kept as supplied minus their
reference photographs, comparison images and raster previews.

| Folder | Pin | Used by the site as |
|---|---|---|
| `welcome-bc-pattison/` | Welcome to B.C., A Division of Jim Pattison Enterprises | `src/pins/novelty/welcome-bc-pattison.svg`: `welcome-bc-pin.svg` with its ids prefixed `wbc-` and its title's dash replaced |
| `forest-branch-campfires/` | Prevent Forest Fires: Put Your Campfires Out (Forest Branch, Lands Department) | `src/pins/forest-branch/forest-branch-campfires.svg`: `forest-fire-sign.svg` with its ids prefixed `fbc-`, its title and layer labels' dashes replaced and its metadata dropped |

The Interior University Society's pin and buttons have no folder here: the view fetches them from
`public/unbc-origins/svg/`, where the gallery serves them, and prefixes their ids on the stage
(`src/pins/prefixIds.js`). Their kit and its records are in `research/identity/unbc-origins/`.
These are reconstructions, not authenticated masters, and imply no affiliation with or rights in the historical designs.
