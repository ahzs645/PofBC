# Patch source review — 8 November 2026

The review covers **all 154 patch variants**, presented as **126 gallery cards in
21 organizations**. It excludes the separate 14-item badge collection. The
machine-readable findings are in `review-2026-11-08.json`; every patch has an
explicit status, priority, findings, next action, evidence limitations and the
SHA-256 of the drawing actually reviewed.

## Review result

| Status | Variants | Meaning |
| --- | ---: | --- |
| Reconstruct | 42 | A major scene, emblem or layout needs rebuilding. |
| Refine | 71 | The composition is recognizable; lettering, proportions or selected components need work. |
| Source limited | 15 | The available reference cannot resolve important detail or provenance. |
| Retain | 14 | Keep the present construction at this review level. This is not authentication. |
| Interpretation | 12 | A generated colourway without a linked specimen in that colour. |

These are visual triage judgments, not measured fidelity scores. The five partial
corrections below retain their review status because other issues remain.

### Work that should lead the next drawing pass

1. **Give the historical Forestry scenes their own masters.** Fire Control,
   Wildfire Management, the green/gold light-band edition and the yellow-sky
   edition differ in landscape, trees, water and service-band construction.
   Recolouring a modern snowy-mountain master does not reproduce those editions.
2. **Rebuild the most schematic pictorial elements.** The Parks hikers triangle
   (S29-O03), the Forest Service map/deer design (S45-O01), scenic Parks arches,
   and several tiny-board crests need stronger silhouettes and component
   relationships. Exact microdetail may require a better reference.
3. **Review lettering and crest scale by specimen.** Conservation Officer
   shields, Fish & Wildlife Branch captions, Parks ministry shields and Sheriff
   headings share broadly plausible parts but diverge in alphabet, arc, spacing,
   hierarchy and embroidered treatment. The good narrow Warden alphabet is a
   useful control, not a universal replacement.
4. **Resolve evidence gaps before inventing detail.** Most of the small-agency
   references are tiny crops of the 480 × 640 S56 collector board. They establish
   broad structure more reliably than exact letters or heraldic contours. The
   Ministry of Environment shield also has a better MC26 source, now exposed in
   the viewer. The supplied SPCA photograph is retained with its own provenance.

## Five partial artwork corrections

The actual SVG changes live upstream in `ahzs645/patcher`, with authored source
files and regenerated previews. PofBC consumes that revision through its existing
submodule.

| Design | Prepared correction | Still unresolved |
| --- | --- | --- |
| MC27-O01 | Restore the curved heading divider and put British Columbia on a wider, lower arc. | Alphabet, footer, outer cut and embroidered crest. |
| MC28-O01 | Same heading correction, preserving its distinct ministry caption. | Caption spacing and historic crest treatment. |
| MC29-O01 | Same heading correction for the narrow-footer edition. | The lower block particularly needs its own lettering/layout pass. |
| FO-wildfire-management-black | Restore two existing mountain-line primitives omitted by the monochrome capture. | Band shape, title weight, tree and tonal treatment. |
| S48-O01 | Replace the bowed printed-emblem border with a separate near-square cloth border. | Internal map/tree contours, spacing and colour interpretation. |

Each record preserves `baselineFindings` and `baselineSvgSha256`, then records the
new `reviewedSvgSha256` and `candidateChanges`. The report shows source, previous
drawing and partial correction separately; it never presents a changed image
with findings silently inherited from a different drawing.

Only those five complete drawings change. The stored fragment for
FO-forest-service-black also changes during shared-part extraction, but its
fully joined bytes and hash remain unchanged.

## Source evidence and limits

There are **191 source crops covering 141 variants**. Thirteen variants have no
available individual crop: twelve generated colourways and FSP-bright-gold.
Five linked occurrences are explicitly unavailable: four PDF occurrences lack
individual crop rectangles and the S32 source image was not supplied. The
builder does not attempt to recover unavailable material.

Sources include cloth photographs, printed depictions, digital artwork and a
document page. Native dimensions and the reference medium are displayed. Images
keep their aspect ratio and are uniformly fitted to their panels. Enlarging a
small crop supplies no extra evidence. There is no photograph registration,
pixel-overlap score, calibrated colour claim or production-size inference.

**Predator Branch (MC03-O01):** the 157 × 173 historical reference is a printed
depiction with a 128 × 134 crop. The catalogue says its page owner has not seen a
physical example. The existing supplied package's 95.1% foreground / 98.9% animal
overlap figures compare a separate clean illustration with the reconstruction.
They do not authenticate a historical cloth specimen. Its artwork is retained;
its metadata and limitations are corrected.

The ledger records which occurrences informed each judgment. All variants were
triaged; alternate sources were examined where recorded, rather than claiming
an exhaustive independent historical investigation of every linked publication.

## Gallery behavior

The selected source is placed beside the vector drawing, with an occurrence
selector, source type, native dimensions and its own original-source link.
Embroidery output is labelled as a simulation. Findings and partial corrections
remain visible alongside the comparison.

Source loading failures and absent crops have explicit states. A review is
labelled stale when the current drawing hash differs from the reviewed drawing.
The source link never falls back to a different occurrence while an occurrence
is selected.

Variant changes cannot reuse another patch's SVG, sew-out or downloads. The
canvas is hidden until its matching sew-out is ready and is painted in a layout
effect before it becomes visible. Export readiness is keyed to the selected
patch, drawing and machine settings.

## Reproduce the evidence

Baseline PofBC: `280b5015ddd2a092acf26b242b3aec2dd220b690`
Baseline Patcher: `1e41f5e01a517d2232197ff57ba5b4f1c9d0636e`

Use the existing [BC Forestry Patch Atlas snapshot](https://drive.google.com/file/d/1FttYbiCfmrQW4TbvcDD7lpVG9Y-gRzs4/view).
Its archive SHA-256 is
`a5d174b9ba815bbcc34c4f7ea6e9c0e4cc125235f692f81222c69580d076f001`,
and its `CODEBASE_SNAPSHOT.json` identifies snapshot
`02f524d650e28b12a9600bfcd220e492d0fcb2b7cdce039d97e6655ab231c563`.

Extract it to a directory containing `CODEBASE_SNAPSHOT.json` and `dist/`. The
builder needs Python with Pillow, Node, and PofBC's installed `@resvg/resvg-js`
for the few native vector references. It does not download source material.

```sh
python3 scripts/build-patch-review.py --atlas /path/to/extracted-atlas
python3 scripts/build-patch-review-report.py \
  --patcher vendor/patcher \
  --output /path/to/PofBC_Patch_Source_Review_2026-11-08.html
```

The first command builds `public/patch-review/index.json` and its WebP crops.
It verifies each source against the snapshot's file hashes and checks crop
bounds and native dimensions. Rectangles use **[x0, y0, x1, y1]**, not x/y/width/
height. Per-source URLs, coordinates, source-file hashes and crop hashes are
retained in the index. Original URLs come from the sighting or source catalogue;
missing manifest URLs do not erase catalogue provenance.

The report embeds the source crops and previews, so it can be read offline.
It requires the baseline Patcher commit to remain available in the repository
in order to retrieve the original previews. It preserves all entries when
JavaScript is disabled; search and selection enhance the page when enabled.

`reviewedSvgSha256` belongs to the human review and is never silently updated
by the builder. `currentSvgSha256` records the imported library revision.
Changing a drawing requires a new review or an explicit stale-review state.

## Verification

```sh
node --test src/patches/patches.test.js
node scripts/check-patch-viewer-build.mjs
node vendor/patcher/scripts/verify-library.mjs --zip /path/to/atlas.zip
```

- Independent checks covered all 191 source crops: source hashes, crop bounds,
  dimensions, URLs, output hashes and one entry for each of the 154 variants.
- Patcher's source-integrity verifier passes for all 168 library drawings,
  including the separate badge collection. Exactly five joined drawings differ
  from the baseline. Its TypeScript check and Vite production build pass.
- PofBC's eight patch tests pass, and the changed JSX components transform. A
  focused Vite production build of the actual patch viewer, CSS, Patcher library
  and digitizing worker passes against the candidate submodule revision (454
  emitted assets). This does not run the unrelated full-site asset pipeline.
- Interactive browser acceptance of the new viewer has not been completed in
  this workspace: the connected browser cannot reach the executor loopback and
  local Chromium startup was blocked by its process socket policy.

The work is prepared for review. Review statuses are not publication or
manufacturing approval, and no broad redraw is represented as completed.
