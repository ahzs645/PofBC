# Province of British Columbia — logo generator

A Vite app that builds the three provincial lockups for any ministry, in any colourway, and
exports them as SVG, PDF, PNG, WebP or JPEG. The rendering core underneath it is plain JavaScript
with no framework dependency, so it can be reused from another app, a build script or a server.

```
git clone --recurse-submodules <this repo>
npm install
npm run dev
```

Already cloned without `--recurse-submodules`? `git submodule update --init --recursive`.

---

## The three lockups

Each one is reconstructed from a supplied Illustrator export in [`artwork/`](artwork), and keeps
that file's own type size, leading and tracking — the three were set individually and they do not
agree with each other, so the differences are preserved rather than averaged away.

| | Layout | Set from | Notes |
|---|---|---|---|
| **Stacked** | Mark above a left-aligned text column | `artwork/lockup-stacked.svg` | 122.2 units, 1.2 em leading |
| **Centred** | Mark centred above centred text | `artwork/lockup-centred.svg` | 121 units, 1.04 em leading, tracked −0.02 em |
| **Horizontal** | Mark left, text right, vertically centred | `artwork/lockup-horizontal.svg` | 121.64 units, 1.2 em leading |

The three artworks disagree about the province wordmark: the centred one is drawn without it, so
that lockup is just the ministry and its second line under the mark. Picking a lockup therefore
adopts what its artwork does — until you set the wordmark yourself, after which it is your decision
and switching lockup leaves it alone. A restored share link counts as having set it.

All three take a ministry from a list or typed in free-hand, an optional second line, separate
colours for the mark and the type, a background colour or transparency, and a clear-space margin.
Explicit line breaks are honoured.

---

## Requirements

**Node 20.19+ or 22.12+**, **a copy of Helvetica**, and one git submodule.

### The submodule

[`vendor/json-url`](https://github.com/ahzs645/json-url) compresses a lockup configuration into a
share link. It gitignores its own `dist/`, and every entry in its package `exports` points there,
so it has to be built before Vite can resolve the import. `npm run vendor:build` does that, and
`prepare`, `dev` and `build` all run it for you. It is a no-op once built, so the dev loop pays
nothing for it.

### Helvetica

The artwork is set in real Helvetica — verified, not assumed: the advance widths in the source
files match Helvetica's to five decimal places, and no other face on the machine comes close. macOS
ships it at `/System/Library/Fonts/Helvetica.ttc`, which is where the build looks by default.

```sh
FONT_SOURCE=/path/to/Helvetica.ttc npm run build:fonts   # elsewhere, or another licensed copy
```

Helvetica is licensed, so the subset faces the build produces are **not committed** —
`src/fonts/generated/` and the `src/fonts.css` that points at it are both gitignored and rebuilt on
each machine. `npm run dev` and `npm run build` do that for you.

`src/logo/fontMetrics.js` *is* committed. It holds advance widths and side bearings, not outlines,
and it is what lets the layout engine measure text in Node — including in CI, on a machine with no
Helvetica at all.

---

## How it fits together

```
artwork/                     the three supplied Illustrator exports — the source of truth
scripts/
  build-mark.mjs             extracts the mark, proves all three copies are identical
  build-fonts.mjs            subsets Helvetica, emits the metrics table and the glyph outlines
  build-vendor-json-url.mjs  builds the share-link submodule
  sfnt.mjs, svgPath.mjs      the font and path surgery those two need
  compare-artwork.mjs        re-renders each lockup over its original and diffs them
vendor/json-url/             submodule — compresses a configuration into a share link
src/
  assets/markup.js           generated — the mark, once
  logo/                      the framework-free core: layouts, measurement, colour, rendering
  export/                    SVG/PDF/PNG/WebP/JPEG, single files or a zipped bundle
  ministries/                the ministry list and its search
  site/                      the React generator UI
```

### Reusing the core

The package has no framework dependency below `src/logo/BcLockup.jsx`. `renderLockupSvg()` returns
a complete SVG document as a string and runs anywhere:

```js
import { renderLockupSvg } from './src/logo/renderLogoSvg.js'

renderLockupSvg({
  layout: 'horizontal',
  ministry: 'Ministry of Water, Land and Resource Stewardship',
  color: 'white',          // sets both halves at once…
  markColor: 'gold',       // …unless one of them says otherwise
  background: 'green',
  padding: clearSpacePadding('snug')
})
```

`resolveLockup()` returns the resolved geometry — box, mark position, per-line baselines — without
drawing anything, for callers placing the lockup inside a larger drawing. In React:

```jsx
import { BcLockup } from './src/logo/BcLockup.jsx'

<BcLockup layout="stacked" ministry="Ministry of Forests" color="white" background="green" />
```

The component renders the markup that the exporter produces, rather than rebuilding it as React
elements, so the preview cannot drift away from the download.

---

## The mark is stored once

The three source files are three exports of one Illustrator artboard, and each carries a full copy
of the provincial mark — about 21 KB of path data, three times over, at three different positions
on the board.

`npm run build:mark` normalises all three to a common origin, compares them coordinate by
coordinate, and writes the drawing out once:

```
mark verified identical across 3 lockups (largest coordinate delta 0.010)
497.02 × 497.19, 26 shapes, 21.4 KB
→ src/assets/markup.js (42.8 KB of duplicated path data dropped)
```

The comparison is numeric with a 0.011-unit tolerance, because Illustrator wrote two decimal places
against three different artboard offsets and the same point can land either side of a rounding
boundary. The shapes carry no `fill` of their own — colour inherits from the wrapping `<g>` — so one
copy serves every colourway with no markup rewriting at render time.

The check matters more than the saving: if a future artwork drop changes one lockup's mark and not
the others, the build fails loudly instead of silently blessing whichever file was read first.

---

## Checking the reconstruction

`npm run compare` re-renders each lockup through the generator, crops the original to the same
frame — aligned on the mark, the one element guaranteed to be shared — and writes a difference
sheet to `tmp/compare/comparison.png`. It needs `python3 -m pip install cairosvg pillow`.

Measured against the source artwork, per text line:

| Lockup | Line widths | Position |
|---|---|---|
| Stacked | exact | 0.78 units |
| Horizontal | exact | 0.00 horizontal, 7.83 vertical |
| Centred | exact | 19.1 and 28.0 units |

Every line's width matches the original exactly. The position differences are deliberate, and all
three come from the same decision: the reconstruction is built on a rule, and the originals were
placed by hand.

- **Stacked** aligns the mark to the leftmost ink in the whole text block; the original aligns it
  to the `P` of *Province* specifically. 0.78 units apart, and the rule does not depend on which
  letter happens to come first.
- **Horizontal** centres the mark on the text's cap band. The original sits it 7.83 units higher —
  1.6% of the mark's height.
- **Centred** actually centres. The original's two lines are 19 and 28 units off centre, and
  disagree with *each other* by 9, so there is no single offset that could have been copied.

These numbers are pinned by the tests in `src/logo/renderLogoSvg.test.js`, so they cannot drift
without a test failing.

---

## Exports

| Format | Notes |
|---|---|
| **SVG** | Both faces inlined as base64 `@font-face`, so the file is self-contained |
| **PDF** | Real vector, page sized to the lockup, type still live and selectable |
| **PNG / WebP** | Transparency preserved; 512–4096 px wide |
| **JPEG** | No alpha channel, so it is composited onto white |

### Live text or outlines

Vector exports keep their type live by default, with both faces embedded — the file stays
editable, selectable and searchable. **Convert text to outlines** turns each letter into a path
instead, which is what a printer usually means by "supply it with the text outlined": nothing in
the file refers to a font any more, so nothing can substitute one.

Outlining is not an approximation. The pen arithmetic in `src/logo/textOutline.js` mirrors
`measureLine()` exactly, and the tests measure the emitted path data back and compare all four ink
edges against the layout model — they agree to within 0.01 of a unit, without involving a
rasteriser at all.

It usually makes the file *smaller*, because the embedded font goes away with it:

| | Live text | Outlined |
|---|---|---|
| SVG | 172 KB | **36 KB** |
| PDF | 122 KB | 140 KB |

The glyph table is about 200 KB and loads on demand, so it costs nothing until someone asks for it.
The accessible `<title>` is kept either way — outlining removes the text from the document, and
that title is then all a screen reader has.

The viewBox hugs the ink — actual glyph extents, not the font's full ascender and descender — so a
lockup with no descenders carries no empty band beneath it. **Clear space** then adds a margin on
top of that, measured as a fraction of the mark's width so the proportion holds at any size. Where
the lockup has a background colour, the colour fills the margin too, so clear space also decides how
much of a coloured panel the export is. `None` is available for a logo being dropped into someone
else's layout, but it is not the default — type set hard against the edge of a coloured panel reads
as a mistake.

Formats the browser cannot encode are detected and disabled rather than offered and then quietly
substituted.

### Colour, and the transparent case

The mark and the type take their colours independently; `color` is a shorthand that sets both, and
the UI keeps them linked until you say otherwise.

A transparent export has no background of its own, so the generator reports contrast twice — against
white and against black — and names whichever of the mark or the type is the weaker of the two. A
white lockup is 1:1 on white and 21:1 on black, and both numbers are worth knowing before you hand
the file over.

The preview surface follows from the same reasoning. On **Auto** it turns dark when the artwork
would otherwise be invisible against a light page, which is the one case where a preview actively
misleads. It is a preview control only and is never part of the export; the checkerboard appears
only when the export really is transparent, so the pattern always means the same thing.

---

## Bundles

**Bundle** in the download panel renders the cross-product of the lockups, formats and pixel widths
you tick, and zips it:

```
bc-ministry-of-forests/
  stacked/     …-stacked-ffffff.svg  .pdf  -1024.png  -2048.png
  centred/     …
  horizontal/  …
  README.txt   what is in the box, and which file to hand a printer
```

Everything goes through the same `renderLogoBlob()` as a single download, so a bundled asset is
byte-for-byte the one you would have got on your own. The default selection is 12 files; ticking
everything is 42, and the button says so before you commit to the work. Already-compressed formats
are stored rather than deflated, which costs nothing and saves the time.

---

## Share links

**Copy link** puts the whole configuration in the URL — there is nothing to upload and nothing
stored anywhere. [`@firstform/json-url`](https://github.com/ahzs645/json-url) does the compression,
with two of its transforms doing the work on length: defaults are stripped, so a link carries only
what was changed, and the survivors are renamed to single letters.

| Configuration | Token |
|---|---|
| Untouched | 10 characters |
| One change | 36 characters |
| A typical lockup | ~145 characters |
| Everything changed | ~195 characters |

The engine is pinned to json-url's `lz` codec, and a test asserts that across the whole size range.
That pin started as a workaround: json-url's `raw` codec (plain base64) is the natural pick for the
smallest payloads, but its base64 helper reached for Node's `Buffer` global, so a raw token
compressed happily in a browser and then threw on the way back. The asymmetry made it a problem for
whoever *opened* a link rather than whoever made one, and it only appeared on payloads small enough
for the engine to choose raw — which is the common case of a nearly-default lockup.

That is now fixed upstream in json-url (base64url is implemented locally against the `buffer`
package, as the rest of that library already does). The pin stays anyway: one codec that works at
every size is simpler than two, and the few characters raw would save on a short link are not worth
the branch.

A decoded link is treated as hostile, because it is: it arrives from whoever wrote the URL, not
from whoever opens it. `sanitizeShare()` coerces every field back into something the app could have
produced — enumerated values must be in their enum, booleans must be booleans, text is capped and
stripped of control characters, and a colour must match a pattern that cannot contain a quote or an
angle bracket. The renderer escapes what it interpolates as well; the two are independent.

The engine is loaded on demand, so a visit that neither arrives with a link nor makes one never
downloads it.

---

## Updating the ministry list

Ministries are renamed at every cabinet shuffle. The list lives in
[`src/ministries/ministries.js`](src/ministries/ministries.js) with a `MINISTRY_LIST_REVIEWED`
date that the UI displays, and the generator always accepts a typed-in name — a stale list should
never be the reason someone cannot make the logo they need.

---

## Deploying

[`.github/workflows/pages.yml`](.github/workflows/pages.yml) builds and publishes to GitHub Pages on
every push to `main`, and can be run by hand from the Actions tab. Enable it once under
**Settings → Pages → Build and deployment → Source: GitHub Actions**.

Two things make this workflow unusual:

- **It runs on `macos-latest`, not Ubuntu.** The build subsets the real Helvetica the artwork is set
  in, and the only copy it can legally reach is the one macOS itself ships — the font is not
  committed here. A Linux runner has nothing to subset. A step checks for the font up front and
  fails with an explanation rather than part-way through the build. macOS minutes are free on public
  repositories; on a private one they bill at ten times the Linux rate, so if that matters, the
  alternative is to commit a metric-compatible libre face (Arimo or Liberation Sans have identical
  advance widths, so none of the layout constants would change) and move the job to Ubuntu.
- **It checks out submodules.** `vendor/json-url` builds its own `dist/`, so `submodules: recursive`
  is required or `npm ci` cannot resolve the dependency.

The base path comes from the repository's own name via `BASE_PATH`, so renaming the repository
cannot leave every asset URL pointing at a path that no longer exists. Locally, `npm run deploy`
still works for a one-off publish from your own machine.

---

## Licence and use

The mark is a provincial symbol reproduced from the supplied artwork; its use is governed by the
Government of British Columbia. Helvetica is a licensed typeface — the build subsets it from a copy
already on the machine and never commits the result, but distributing a built site distributes the
embedded subset, which is your call to make under whatever licence covers your copy.
