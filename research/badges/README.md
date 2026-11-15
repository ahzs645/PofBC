# Badges in 3D (preliminary)

The Badges view (`?view=badges`) opens a badge as a solid model you can turn, bend and export,
instead of the embroidery simulation the Patches view uses. It is a first version: the shapes come
from the library's drawings, and every depth, size, finish and curve is a modelling choice.

## Where it comes from

`curved-badge-trial-2026-11-14/` is the study it follows: its report (`README.md`), comparison board,
verification records and the upstream licences. On one specimen, S51-O01 (Forest Fire Prevention
Officer shield), it built the same cleaned artwork with the
[Medal Forge](https://github.com/CatsJuice/medal-forge/tree/a6da89fc2a9416a0651a6db113e8a2a741e6a2ae)
geometry core and with Luster 0.4.0, bent both with one curvature routine, and found Medal Forge the
better starting point for metal badges: it can give letters, rim and emblem real metal relief,
where Luster's filled lettering stays enamel.

So the site uses Medal Forge and the trial's curvature. Luster, its 2.4 MB WebAssembly engine and
the trial's GLB outputs are not brought in.

## What was carried over, and what was generalized

| Trial | Here |
|---|---|
| Medal Forge core, `src/vendor/medal-forge/lib/*.ts` | `src/badges/vendor/medal-forge/`, unchanged, with its MIT licence and `UPSTREAM.json` |
| `src/curvature.ts` | `src/badges/curvature.js`: the same mathematics in plain JavaScript, with its checks in `curvature.test.js` (the trial's Luster GLB check is left out with Luster) |
| `src/medal-adapter.ts`, tuned to S51-O01 | `src/badges/medalBadge.js` and `badgeParts.js`, for any library badge (below) |
| `src/main.ts`, a two-model comparison page | `src/badges/badgeScene.js` and `BadgeViewer.jsx`, one model in the site's viewer layout |

The trial's adapter took the first fill as the body and gave every other shape one of five roles.
The library's 14 badges include silver ranger shields with green enamel insets, cap badges made of a
scroll and a separate plaque, and a leather badge, so:

- **The body is the outline of the whole drawing** (the union of every painted region, solid), so
  each piece of a multi-piece badge has a back.
- **Parts come from what the drawing records**: `data-caption` is lettering, `data-role="border"`
  strokes are the rim, a fill covering more than a third of the badge is its ground, a gradient is a
  plate of the badge's metal, a saturated colour off the metal's hue is enamel, a near-black is a
  darkened field, and the rest is raised metal. Lighter metal stands above darker, so a lit face
  sits on its drawn shading.
- **Struck relief, as in the reference photographs.** The atlas snapshot holds a photograph of every
  badge (`dist/assets/sources/`). On most, the lettering, rim and emblem are struck up from the same
  metal as the field: polished high points with sloped shoulders over a darker, satin or oxidized
  field. So raised parts stand 0.5–0.65 mm (lettering about 0.6 mm), each outline is inset by its
  bevel so the shoulder slopes from the drawn edge to a narrower top (thinner strokes get a smaller
  shoulder), fields are satin and darker than the polished relief, and the key light comes low from
  the upper left and casts shadows. On a silver badge the shadows and the finish are what show a
  raised letter at all.
- **Embossed emblems.** In the photographs the provincial arms (and the Parks Branch dogwood)
  stand up as one sculpted mass, with their detail modelled on it, not as line work on the field.
  The drawings mark these (`data-component` …`-arms`, `five-petal-dogwood`), so each gets a boss:
  its outline with the gaps between its parts closed and everything inside filled, raised about
  0.8 mm with a sloped shoulder, in a darker satin of the metal. The emblem's own pieces stand on
  it in drawing order, and an "engraved" emblem's plates (S18, S19) become its polished high points
  over the darker boss.
- **Struck field textures.** The drawings leave texture out, but the photographs show it: the early
  Park Ranger shields (S11, S12, S17, S20) have a pebbled field of close-set, irregular bumps about
  0.6–1.3 mm across, and the green-enamel ones (S14, S18) a fine frosted grain. Both leave a smooth
  band just inside the badge's edge and stop short of the raised parts. `stipple.js` makes each
  badge its own field texture, following common practice for procedural hammered and peened metal
  (irregular packed dents with flattened crowns, as Blender's Voronoi "hammered" texture and Modo's
  peened texture make) and for variable-density stippling (Poisson-disk sampling with a sizing
  field): the field and the relief are rasterized, distances to the edge and to the relief
  measured, bumps placed by dart throwing with a gap that widens near the relief and none in the
  edge band or the relief's halo, each bump an irregular blob of random size and height, and the
  height field turned into a normal map (which the GLB keeps). Other badges' fields are smooth, as
  their photographs are.
- **The metal is read from the badge**: leather by its medium; otherwise a gradient's name (`silver`)
  or the lit paints' hue, gold against grey, by area.
- The longer side is set to a nominal **65 mm** (the trial's height for S51-O01), and the default
  shape is the trial's **4 mm centre-to-edge rise across the width**. Flat and dome are a click away;
  the rise is held below a 90° turn at the badge's edge.

Shadows the atlas drew into the artwork (`data-intentional-shadow`) are left out, as in the trial;
the lighting makes its own.

## Limits

- Not measured: size, body thickness, relief, finish and radius are illustrative, and the reverse
  is generated, without pins, clutches or maker's marks. The GLB records this in its extras.
- The drawing is the reconstruction, not the die. The trial's note stands: S51-O01's photograph shows
  a broad, solid, tiered tree; the vector's thinner pine is what gets built.
- Fine heraldic detail (the provincial arms on the ranger and cap badges) becomes hundreds of small
  pieces; the larger badges take a few seconds to build, on the page's main thread.
- WebGL is required for the 3D view; without it the Vector tab still works.

## Checks

`node --test src/badges/*.test.js` runs the curvature checks and the part rules. Every library badge
was built and rendered in headless Chromium (SwiftShader) without errors when this was added.
