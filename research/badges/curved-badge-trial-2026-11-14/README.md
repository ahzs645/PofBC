# Curved badge study: Medal Forge and Luster

**PofBC specimen S51-O01 — Forest Fire Prevention Officer shield**  
14 November 2026

This working comparison uses the actual Medal Forge geometry core and actual Luster 0.4.0 WebAssembly engine on the same cleaned badge artwork. Both complete objects can be bent, rotated and exported. The default demonstration is **65 mm high with a 4 mm centre-to-edge rise**. Those dimensions, the relief and the finishes are modelling assumptions, not measurements of the historical specimen.

The result supports **Medal Forge with an explicit physical profile for this metal badge**. It can give the letters, border and emblem deliberate metal relief. Luster builds an attractive complete object automatically, but its filled lettering remains enamel. That interpretation is useful for enamel objects and less appropriate to this photographed badge. This is a comparison of a tailored Medal Forge adapter against Luster's native construction rules, not a claim that both stock editors produce equivalent results.

## Open and inspect

Open **`badge-comparison.html`** in a current desktop browser with WebGL enabled. The file embeds its JavaScript, artwork, photograph and Luster model; viewing requires no installation, server or asset downloads. Source links open external pages only when clicked.

Drag to rotate both models together, scroll to zoom, or use the Front, Oblique, Top / curve, Side and Reverse presets. Compare the flat control with the cylindrical bend and shallow dome, then adjust rise from 0 to 8 mm. The top view makes the curved body particularly clear. Arrow keys rotate the focused canvas; R restores the camera. Expand the construction notes to export the current comparison PNG or either model as GLB.

## Package contents

| Path | Purpose |
|---|---|
| `badge-comparison.html` | Self-contained interactive comparison |
| `assets/S51-O01.source-crop.jpg` | Recorded reference photograph crop |
| `assets/S51-O01.original.svg` | Catalogue SVG before shared-component resolution |
| `assets/S51-O01.resolved.svg` | Complete existing vector, including the pine |
| `assets/S51-O01.prepared.svg` | Common 3D input with illustrative shadow copies removed |
| `assets/S51-O01.luster.glb` | Unbent output of the genuine Luster engine |
| `src/` | Viewer, Medal Forge adapter and shared curvature implementation |
| `vendor/luster/engine/` | Pinned Luster WASM and JavaScript bindings |
| `outputs/S51-O01-medal-forge-curved.glb` | Exported Medal Forge demonstration model |
| `outputs/S51-O01-luster-curved.glb` | Exported Luster demonstration model |
| `outputs/verification.json`, `outputs/curvature-tests.json` | Browser and mathematical verification records |
| `licenses/` | Upstream licences, notices and Medal Forge provenance |

The exported GLBs use **metres** and the demonstration's nominal 65 mm height. They include the geometry bend; curvature is not merely a viewer shader that disappears on export. Their reverse surfaces are generated display geometry, without authenticated fastening hardware or rear markings.

## Artwork and physical preparation

The catalogue SVG contains a shared-component placeholder. Resolving `historic-pine-adffb4d88d` restores the tree; extruding the unresolved file would leave the centre empty. Ten deliberately offset shadow-letter paths were removed before either engine ran. Lighting now supplies their shadows. The common prepared artwork contains 101 paths.

Medal Forge extrudes filled regions. Its adapter therefore converts SVG strokes into closed contours, respecting transforms, widths, joins and caps. It expands 45 strokes, extends the backing to the outer rim, and assigns body, rim, lettering, emblem and detail roles. The adapter also corrects reflected winding and cancels the core's artificial ordering offsets so unrelated paths do not acquire accidental physical heights. The vendored geometry algorithm itself is retained; its import aliases were rewritten for local use. See `src/medal-adapter.ts` and `licenses/Medal-Forge-UPSTREAM.json`.

The current Medal Forge body profile uses **1.8 mm thickness plus bevel**, color **`#382f20`**, roughness **0.8** and metalness **0.65**. It represents an interpreted darkened/oxidized field. Brighter raised metal uses separate profiles: lettering is **0.38 mm plus bevel**, the rim 0.42 mm, the emblem 0.32 mm and fine detail 0.23 mm. These are construction choices, not recovered die specifications. The darker field makes the raised parts easier to inspect against the reference.

Luster was minted with `metalLines: true` and `withoutHiddenFaces: false`. It produced 42,208 triangles and a 4,074,428-byte native GLB in approximately 3.02 seconds on this machine. Its stroke walls and outer edge are metallic, while filled cells are enamel. The engine's [construction documentation](https://github.com/famio/Luster/blob/371943439467c49eb9b4a8f43ac51847d6e192c7/docs/how-it-works.md) describes that distinction.

**Material metadata needs careful reading.** `assets/luster-metadata.json` records the engine's internal default pale-gold color before export. The actual GLB was exported with bronze plating, sRGB `(0.67, 0.46, 0.23)`, on both metal roles. The mesh name `gold` is an internal name. The enamel material remains nonmetallic, with its original color atlas; the reverse alone receives the generated normal-map grain. `assets/luster-report.json` records the exported material values.

## The curve belongs to the whole object

`src/curvature.ts` applies the same mapping to body, back, sidewalls and every relief layer. Long triangles are subdivided first, including the broad front and reverse surfaces. Otherwise their interiors remain straight chords even if the boundary vertices bend.

For cylindrical curvature, flat horizontal position is treated as arc length. Radius is solved from the requested rise and unbent span. Depth becomes a radial offset, preserving local thickness and relief along the curved surface normal. Normals use the inverse-transpose deformation Jacobian; tangents use its direct Jacobian. This keeps lighting consistent with the new surface. The dome uses a radial counterpart of that mapping. Returning to flat restores the original prepared coordinates rather than accumulating repeated deformations.

The two engines have slightly different generated extents. Both are normalized to 65 mm height and receive the same rise, rather than being distorted to force identical outlines. Their default cylindrical radii are approximately 129.6 mm. Projected width contracts when bent, so unbent arc width and visible chord width are different quantities.

## Findings and limits

| Question | Medal Forge adaptation | Native Luster interpretation |
|---|---|---|
| Raised metal letters? | Explicit metal solids | Filled letters remain enamel |
| Border and reverse? | Controlled physical layers | Automatic rim, plate and textured reverse |
| Curved complete body? | Shared extension | Same shared extension |
| Best fit here? | Preferred starting point | Useful comparison and enamel route |

Both retain a significant artwork limitation: the photograph has a broad, solid, tiered tree, while the existing vector uses a thinner, more open branching pine. That mismatch is inherited by both models. Improving the renderer does not authenticate or repair the tree. Letter shapes, spacing and shield proportions also remain reconstructions. The [recorded source photograph](https://drive.google.com/file/d/1Qx2P5oct-kU8_sf8XOJJvK_dU1-J6Elb/view) supports appearance comparison but does not establish radius, exact dimensions, alloy, plating, original surface finish or rear construction.

During testing, pale speckles appeared on Luster's field. They were **depth precision artifacts**, not patina: a pale engine underlay lies only 9 micrometres below the dark field. Tightening the millimetre-scaled viewer's clipping planes removed the widespread depth-buffer pattern without changing the model. The final viewer keeps its near/far planes within 55 mm of the camera-to-target distance (with a 1 mm near-plane floor). Its 32×64 face atlas contains four flat colors, no scratches. **A few fine pale seams or flecks remain visible at small viewport sizes**, including in the flat, untouched native mesh. They are a recorded native-output/rendering limitation, not authenticated patina and not introduced by our curvature. Downstream viewers need clipping appropriate to their units and camera distance.

## Verification and reproduction

The saved final browser run passed flat, cylindrical, dome and maximum-rise geometry checks, keyboard rotation, GLB export and the 390-pixel layout check, with no page errors or external asset requests. Display geometry comprises **140,388 triangles in five Medal Forge meshes** and **124,104 triangles in three Luster meshes**. This verifies this browser environment, not phone performance. Six mathematical checks cover rise, normal thickness, normal direction, preserved attributes, safe rejection and exact flat recovery. The exports are also reloaded to verify their 0.065 m height. The rise control and flat-mode disable behavior are exercised through the UI. Consult the timestamp, pass flag and material metadata in `outputs/verification.json` for the checked revision. Visual limitations above remain separate from the automated pass flag.

From the extracted package root, with Node.js and npm installed:

```sh
npm ci
npm run build
npm run verify
```

Verification uses the bundled Linux `@sparticuz/chromium` runtime. For another supported system Chromium executable, set `BADGE_CHROMIUM_EXECUTABLE` to its absolute path before running verification. The supplied HTML itself requires no Node.js.

Run the mathematical checks separately:

```sh
npx esbuild tools/test-curvature.ts --bundle --platform=node --format=esm --outfile=outputs/test-curvature.mjs
node outputs/test-curvature.mjs
```

To regenerate native Luster output using the included WASM:

```sh
node tools/mint-luster.mjs assets/S51-O01.prepared.svg outputs/luster-remint
```

## Pinned sources and integrity

| Component | Pin | Licence |
|---|---|---|
| [Medal Forge](https://github.com/CatsJuice/medal-forge/tree/a6da89fc2a9416a0651a6db113e8a2a741e6a2ae) | `a6da89fc2a9416a0651a6db113e8a2a741e6a2ae` | MIT |
| [Luster](https://github.com/famio/Luster/tree/371943439467c49eb9b4a8f43ac51847d6e192c7) | `@famio/luster@0.4.0`; `371943439467c49eb9b4a8f43ac51847d6e192c7` | MIT; bundled third-party notices |
| Three.js / Clipper | `0.184.0` / `6.4.2` | MIT / Boost Software License 1.0 |
| esbuild / Playwright / Chromium wrapper | `0.25.11` / `1.62.1` / `138.0.2` | MIT / Apache-2.0 / MIT wrapper |

SHA-256 identifiers for stable inputs and native output:

| Path | SHA-256 |
|---|---|
| `assets/S51-O01.resolved.svg` | `d53a603ffad1156f51847f4094900382d7689d1302c3b17f340d160340bccc06` |
| `assets/S51-O01.prepared.svg` | `680dea21135725a2fbac3aa2a1ef95cf3503b0d36fad05239603394752895fbb` |
| `assets/S51-O01.luster.glb` | `38e3bac1a96c66417aea3533828822f82d7bb961cd822ef6c146948a4226f78e` |
| `vendor/luster/engine/luster_wasm_bg.wasm` | `f3c03834e3c1eb35f8de0d62800d7e2b536660f7d06239735d590f7c63955477` |

Keep the supplied licences with reused engine code. These software licences do not establish rights to the historical photograph or badge artwork. The package is a reviewable rendering study, not a manufacturing model or a completed PofBC integration.
