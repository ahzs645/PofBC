# BC Transit × PofBC — identity research and integration package

Prepared 27 September 2026. This is an independent historical research package, not an official brand guide.

## Open the result

Open `index.html` in a browser. It is self-contained and works without a server or network; the source links are external only when followed. The timeline filters distinguish logo observations, organizational events and bus liveries.

`BCTransit-timeline.pdf` is the presentation copy with a source appendix. `BCTransit-timeline.svg` has editable explanatory text. `BCTransit-timeline-outlined.svg` converts that explanatory text to paths. Both SVG posters retain **one clearly labelled historical JPEG**; neither is falsely described as entirely vector.

## What the research establishes

The official history dates the BC Transit name to 1982. Official 2007/2008 plan covers show a flag-above-name lockup; the 2009 plan shows the loop and tagline. The latter is documented by the plan’s 17 February 2009 tabling date, not necessarily introduced then. The 2007 exterior-design milestone and 2024 green-bus rollout must not be treated as automatic logo redesign dates. BC Transit explicitly says the 2024 livery did not change the logo.

The supplied horizontal flag JPEG has no independently established dates. The navy and colour/tagline SVGs are applications of the same loop family; they are not proven successive generations. See `research/bc-transit.md` and the source-linked JSON for the evidence and unresolved questions.

## Artwork files

| File under `assets/` | What it contains |
|---|---|
| `bc-transit-loop-navy.svg` | Supplied path geometry, cropped; entirely vector, no live type. |
| `bc-transit-loop-colour-source-hybrid.svg` | Source geometry and source-font tagline outlines; retains the source’s tiny clipped shading bitmap. **Hybrid.** |
| `bc-transit-loop-colour-flat.svg` | Entirely vector, explicitly labelled **flat derivative**; exact clip boundary replaces bitmap shading. Not an official master. |
| `bc-transit-flag-horizontal-reference.jpg` | Supplied historical raster, unchanged. Not traced or presented as vector. |

Individual PDF exports and PNG previews are also included. No font programs are distributed. File colours are source values, not recovered official Pantone standards. The official stacked-flag artwork is an explicit acquisition gap.

## Install into an existing PofBC checkout

No GitHub files, branches, commits or pull requests have been created or changed by this package.

Use a clean review branch in your local checkout. Keep this package outside the checkout and run the installer from the package directory:

```sh
# Inspect the planned changes; this writes nothing.
node integration/install.mjs "/absolute/path/to/PofBC"

# Apply after reviewing the plan.
node integration/install.mjs "/absolute/path/to/PofBC" --apply

# Validate in the actual project.
cd "/absolute/path/to/PofBC"
git diff --stat
git diff
node --test src/gallery/collections.test.js src/gallery/timelines.test.js src/gallery/wanted.test.js src/gallery/renderOneOff.test.js
npm run build
```

The installer adds a collection on the **bodies** shelf using `graphNode: 'bc-transit'`. It adds a separate path catalogue and combined runtime registry rather than overwriting the generated provincial catalogue. The existing gallery renderer and colour controls are reused. Only the modern navy and flat-colour derivative have editable vector cards. Historical references retain sought-master slots; the JPEG is viewable through the first slot’s reference link.

The installer updates five existing files: the collection registry, two artwork-catalogue imports, the wanted-body list, and its expected-source test. BC Transit is removed from the body-level wanted shelf because it now has a collection; missing historical masters and permission remain documented within that collection and its research notes. Other bodies are preserved.

All transforms are planned before writes. Unexpected anchors, ambiguous records, symlinks and differing existing add-on files cause a refusal rather than an overwrite. Already-installed identical files are left alone. Original edited files are backed up under `.pofbc-bc-transit-backup/`; a manifest identifies newly added files. Do not commit that backup directory. Review the diff before committing anything.

The repository was inspected while other work may have been changing it. An anchor refusal is intentional: reconcile the registry with the newer project rather than forcing the older patch.

## Verification performed

Eight add-on tests passed: collection structure, rights/date records, null adoption endpoints, source/file integrity, native path roles, pure-vector/hybrid distinction, constrained patch transforms, and dry-run/apply/idempotency/conflict behavior on a representative repository fixture.

The standalone HTML was rendered in Chromium at desktop (1440 px) and mobile (390 px) widths. All four filters produced the expected visible counts, with no horizontal overflow or JavaScript errors. The PDF was rendered separately with Poppler and inspected.

**The full PofBC application was not built or regression-tested here.** A complete local repository could not be downloaded in this environment; the native add-on was tested independently and against a minimal installer fixture. The commands above must be run on the real checkout. This is not a claim of a passing full-repository build.

## Data and regeneration

`data/bc-transit-timeline.json` holds sources, events, families, variants, provenance, rights and unresolved work. Adoption/retirement dates are null where unknown. `data/input-inventory.json` records the original uploaded file hashes without redistributing an embedded font program.

Run the add-on tests:

```sh
node --test integration/tests/bc-transit.test.mjs
```

To regenerate from the original extracted upload (not included again here):

```sh
python scripts/prepare_assets.py /path/to/extracted/bctransit /path/to/BCTransit-PofBC
python scripts/build_package.py
python scripts/finalize_exports.py
```

Python dependencies: `lxml`, `fonttools`, `cairosvg`, `reportlab`, `pypdf`. Inkscape is used for the outlined poster. The explanatory live text uses DejaVu Sans as an installed system face; its font files are not included. The original colour SVG’s embedded tagline font is read in memory only and converted to outlines.

## Scope and rights

Not a complete history of every municipal transit brand, handyDART, RapidBus, Umo or associated operator. Missing original artwork and exact launch/retirement dates are explicitly recorded. No reproduction permission has been sought or documented. Research display and geometry preparation do not establish authorization to use BC Transit branding.
