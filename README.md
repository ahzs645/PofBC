# Province of British Columbia — logo generator

A Vite app that builds the Province's lockups — four identities' worth, spanning the crest era to
the marks in use today — for any ministry, in any colourway, and exports them as SVG, PDF, PNG,
WebP or JPEG. The rendering core underneath it is plain JavaScript with no framework dependency, so
it can be reused from another app, a build script or a server.

```
git clone --recurse-submodules <this repo>
npm install
npm run dev
```

Already cloned without `--recurse-submodules`? `git submodule update --init --recursive`.

---

## Four identities

An **Identity** switch at the top of the controls chooses between them. They have almost nothing in
common, so most of the panel changes with it.

| | Crest | Flag | Arms | Current |
|---|---|---|---|---|
| What it is | The crest lockups, from the supplied artwork | BC beside the waving provincial flag | The coat of arms with the BRITISH COLUMBIA wordmark | The Province's published ministry marks |
| Wording | Any ministry, any second line, any wrapping | Any, plus an optional province line and a third line | Any, plus a trailing line | Any, typeset in the marks' own alphabet |
| Lockups | Four | Three symbols × two placements | Three arrangements × two placements | One per ministry |
| Colour | Anything, mark and type independently | Three flag palettes, plus ink | Anything | Four official colourways |
| Language | — | — | — | English and French |
| How it is made | Drawn from parts on every render | Drawn from parts | Drawn from parts | Published mark, typeset wording |

Every era keeps its **own background and ink**, because their palettes have nothing to do with each
other. Switching identity leaves each side as you had it. Sharing them was a bug twice over: the
crest era's forest green showed through the flag's gaps, and the arms' white type once landed on a
white ground.

A **Gallery** button opens the one-off marks — BC Parks and its like — which follow no pattern the
generator can offer and so have nothing to be loaded into. Each still opens for recolouring, and
each draws itself from the same renderer as everything else, so a card cannot drift from what it
gives you.

Most of the gallery is the **Best Place on Earth years**: WelcomeBC, WorkBC, BC Stats,
Environmental Reporting BC, the BC Public Service's "Where ideas work", Canada's Pacific Gateway,
and the stacked BC mark with its tagline. Each is the BC mark with a shaded sun, a gold divider, and
a name in large Garamond. `scripts/build-one-offs.mjs` lifts them from the published files in
[`artwork/one-offs/`](artwork/one-offs) and labels every shape with its part (sun, rays, mountains,
wordmark, tagline, name, the gold accent), so any part can be recoloured.

**StrongerBC** (2021) is lifted the same way but belongs to a later generation: a flat sun, gold
rays over a light disc, with no shading to sample; a grey divider; and a heavy sans in place of the
Garamond. The build tells the two kinds of sun apart by what the file contains. It finds the divider
by its shape rather than its colour, so a grey one counts.

- **The glow is sampled, not guessed.** The print files shade the sun, and the converter wrote each
  shading as a small bitmap clipped to its shape. Those bitmaps are read back into radial gradients
  about the sun's centre, as a mix from the core's light to the sun's gold. The glow recolours
  with everything else and stays vector. One ink draws the sun flat instead, with the rays and core
  cut out of it.
- **The wordmarks are the ministry marks' alphabet, tracked tighter.** WelcomeBC and WorkBC fit
  the same kerned Adobe Garamond at −20/1000 em instead of −10. WelcomeBC is where the capital `B`
  was lifted from. WorkBC's `rk` pair was opened by hand: its `k` sits 5/1000 em right on both
  sides.
- **One thing the lifting turned up:** the committed `W` sits 14/1000 em lower than the `W` drawn
  in both WelcomeBC and WorkBC, exactly where the licensed font puts it. It was recovered from the
  one corrupt file that has a `W`, and its height looks to have come from the font. The other
  capitals the Province drew (`B`, `N`, `O`) also sit 11–14/1000 em from the font's, so the
  artwork's Garamond is a slightly different cut. The committed `W` is left as it is until that is
  looked into properly.

### The current era: a published mark, typeset wording

**The mark itself is never recreated.** Both of the Province's guideline documents say in bold that
the marks must be used *exactly as provided*, so `scripts/extract_current_marks.py` lifts the drawn
vectors out of the published PDF and packages them unchanged.

The *wording* is a different matter, and it is now set rather than stored. The published artwork
draws each ministry name as outlines, which meant a ministry that had been renamed — or one that
never had a mark published — had nothing to use. So the serif was identified, and the alphabet
recovered from the artwork itself:

- **It is Adobe Garamond Pro.** Confirmed by overlaying outlines glyph for glyph: 1.3% worst case,
  0.5% median. BC Sans, the Province's screen face, is not the serif on these marks.
- **The marks are kerned, and tracked at −10/1000 em.** Kerned rather than merely letter-spaced:
  fitting with the pairs gives a residual of 0.005 pt against 0.150 without them.
- **Letterforms are combined by coordinate-wise median, not mean.** Forty-six published marks
  contain many copies of each letter, and a handful of the files are off-standard; the mean was
  pulled 70/1000 em by them, the median 7.8.
- **`W` appears in only one file, and that file is corrupt.** It was recovered by rasterising
  candidate outlines and matching on overlap — an index-based resampling scored 0.44, rasterising
  scored 0.054.
- **Four English files are unusable**: three merge two lockups into one, and a fourth holds French
  text. Typesetting sidesteps all four.
- **The PDF has a text layer.** Finding it removed every remaining guess about line breaks, which
  had until then been inferred from a baseline grid — heads break on commas and feet break on
  apostrophes, so neither alone clusters the lines correctly, but a grid survives both.

What is committed is the alphabet the published marks are *themselves* drawn with, plus advance
widths and kerning pairs. The rest of the alphabet is built from a licensed font and gitignored —
see [Requirements](#requirements).

**Forty-six marks have no capital N or O.** No current ministry name starts a word with either, so
until the list offered historical ministries nobody noticed. Then "Forests, Lands, Natural Resource
Operations and Rural Development" was drawn as "atural Resource perations". The fix is the
Province's own drawing again, not a font: older marks were drawn in the same alphabet, and
`scripts/lift-current-letters.mjs` takes the letters the alphabet lacks out of any mark listed in
[`artwork/current/lifted/`](artwork/current/lifted).

- **It fits before it lifts.** Each line's size and origin are fitted against the letters the
  alphabet already has. On the FLNRORD mark every known letter lands within 0.6/1000 em of where the
  metrics put it, and a file that misses by more than 0.02 pt is refused.
- **It also settled a line-break rule.** The rules below used to cap a mark at three lines,
  because no current mark has four. FLNRORD has four: an even two-line split of its name would make
  a line 13579 wide, where the widest any current mark sets is 12296. So above 13000 the ministry
  proper takes three lines, evened the same way, and the published mark comes out exactly.
- **An English name with a comma is a list, and breaks between its items**: after a comma, or on
  either side of the closing "and". The even split alone set "Jobs, Economic / Development and
  Innovation" and "Energy, Mines and Low / Carbon Innovation", where the Province's marks read
  "Jobs, Economic Development / and Innovation" and "Energy, Mines and / Low Carbon Innovation".
  Width cannot tell these apart from "Children and Family / Development", which *is* the even split
  and is published that way: both miss the evenest break by about 100/1000 em. The comma can, since
  without one the "and" may sit inside a single item. None of the 46 current marks moves.
- **Still missing: `U`, `V` and the full stop**, which 6 historical names use. (`B` came later, from
  the WelcomeBC wordmark: see the gallery above.) A published mark containing them, added to the
  lifted folder's `index.json` with the tracking it was set at, closes that gap.
- **A typewriter `'` is set as `’`**, which is what the marks use, so "Women's Equality" needs no
  letter the marks never drew.

The current era's ministry list is the published marks first, then every other name the other three
identities offer, including every ministry since 1976. Those have no official wording, so they are
set by the rules.

The four colourways are the Province's own, from its colour-accessibility guidance: **Colour**,
**Reverse**, **Solid black**, **Solid white**. Reverse is the interesting one — the mountains
lighten to BC Blue at 60% while the wordmark turns white, and both are the same blue in the source
artwork. That is why the extraction labels every shape with a `data-role` rather than recolouring by
fill. The solid colourways drop the sun's rays entirely so the background shows through them;
painting them white would ring the mark with a halo on anything but a white page.

In the current era the background swatches are the BC identity colours, and choosing one moves the
colourway to the one the guidance pairs with it: BC Blue and black get Reverse, the golds and the
60% tints get Solid black. Choose a colourway by hand and it stops following, as the wordmark and
the alignment do.

Each mark is also a plain file — `current-marks/for-en.svg` and so on, listed in
[`current-marks/index.json`](https://ahzs645.github.io/PofBC/current-marks/index.json) — so current-era
artwork can be fetched directly without running the page.

Two things worth knowing about the source PDF: it draws the marks in CMYK-native `#053673` and
`#fdb913`, while the Province's colour-accessibility guidance specifies `#234075` and `#e3a82b` for
screen. The extracted files carry the screen values and record the print ones. And three rows of the
PDF are inconsistent — one has its divider drawn twice, and two use a different vector export of the
same logo — all handled by the extraction rather than papered over.

---

## The four lockups

These are the **Crest** identity's, the first of the four. The first three are reconstructed from
the supplied Illustrator exports in [`artwork/`](artwork),
and each keeps that file's own type size, leading and tracking — they were set individually and do
not agree with each other, so the differences are preserved rather than averaged away.

| | Layout | Set from | Notes |
|---|---|---|---|
| **Stacked** | Mark above a left-aligned text column | `artwork/lockup-stacked.svg` | 122.2 units, 1.2 em leading |
| **Centred** | Mark centred above centred text | `artwork/lockup-centred.svg` | 121 units, 1.04 em leading, tracked −0.02 em |
| **Horizontal** | Mark left, text right, vertically centred | `artwork/lockup-horizontal.svg` | 121.64 units, 1.2 em leading |
| **Side by side** | Mark, wordmark and ministry as three columns | *no vector original* | 121.64 units, 1.2 em leading |

**Side by side is the one without a source file.** It was reconstructed from a photograph of
signage, so it borrows its type size and leading from the horizontal lockup — its closest relative,
and the only other one that sets the mark beside the type. Its two original numbers are the gap
from the mark (shared with the horizontal lockup) and the gutter between the columns, set to half
the mark's width. Those are the only invented constants in `src/logo/layouts.js`; everything else
there was measured. `npm run compare` covers the three that have originals.

The lockups disagree about the province wordmark: the centred one is drawn without it, so that
lockup is just the ministry and its second line under the mark. Picking a lockup therefore adopts
what its artwork does — until you set the wordmark yourself, after which it is your decision and
switching lockup leaves it alone. A restored share link counts as having set it.

All three take a ministry from a list or typed in free-hand, an optional second line, separate
colours for the mark and the type, a background colour or transparency, and a clear-space margin.
Explicit line breaks are honoured.

---

## The flag identity

BC beside the waving provincial flag, from [`artwork/flag/spirit-of-bc-flag.svg`](artwork/flag) —
twelve shapes, kept as drawn. Three symbols (the letters beside the flag, the flag above them, the
flag alone) each take the wording below or beside them.

**There are three palettes, and the supplied file is not the official one.** The standards page
specifies Pantone Blue 072C, Red 032C and Yellow 109C — `#10069f`, `#ef3340`, `#ffd100`. The SVG
supplied for this project carries `#013366`, `#ad0000`, `#fcba19`, a later recolouring. Both are
offered rather than one being corrected into the other, alongside a third that sets the whole
symbol in a single ink.

That third one exists because **the flag's white is the page showing through it**, not a white
shape. Full colour on a green ground therefore shows green through every gap in the flag, which is
what the printed documents avoid by setting the whole lockup in one ink. The palette picker
recommends it whenever the background is dark enough to matter.

The proportions come from seventeen printed references, because the standards page gives the symbol
and its colours but never shows a ministry name against it. All seventeen reproduce. The documents
disagree with each other, and where they do the reading is kept rather than averaged.

The measure the wording wraps to was wrong for a while, and wrong in a way worth recording: it had
been arrived at by dividing a flag's *width* by its height ratio, which is not a quantity. It broke
"Province of British Columbia" in two — a line nearly every document keeps whole, which is what
made it visible. There is now a test that pins exactly that.

The **BC Parks badge** is built from this flag and its frame, but it belongs to the gallery rather
than to the generator: both of its words are the wordmark, set alike, rather than a ministry name
under a symbol. The frame is the real artwork and not a shape fitted to it — it was a superellipse
until the drawing turned up, and the drawing is not symmetrical, running 30.3 units of wall on the
left against 30.5 on the right and 29.6 at the top against 30.7 at the bottom. It was drawn by
hand, and no fitted curve was going to find that.

---

## The coat of arms

The full achievement of arms with the BRITISH COLUMBIA wordmark, and a ministry set against it.
Both pieces are artwork — the arms as drawn, the wordmark as outlines rather than as text — so the
ministry is the only thing typeset. `scripts/build_crest.py` does the extraction in Python rather
than in this project's own path reader, because the source uses relative arcs and the reader does
not implement them.

Everything else here was measured off twelve printed documents, and the measuring taught more than
the numbers did.

### Check the aspect before believing the reading

Every proportion below was taken by finding the arms and the wordmark in a rasterised reference and
reading their heights. The check that makes those readings trustworthy is to compute each drawing's
own aspect first: across all twelve the arms come out at 0.818–0.833 against this project's 0.831,
and the wordmark at 2.483–2.511 against its 2.523. That is what rules out having measured something
rescaled, cropped or simply misidentified — and it caught two documents that had been read as side
by side when they in fact stack.

### The documents disagree, so several constants are choices

Three of them draw the arms and the wordmark at much the same height (0.878, 0.899, 0.891); three
draw the arms about twice as large (0.493, 0.493, 0.433). Both are printed, so both exist:
**Stacked** and **Stacked, large arms**. A single averaged value would have matched neither.

The same is true of the ministry's size, which runs from 0.212 to 0.294 of the wordmark, and of
where the ministry's lines break, and of whether a trailing line is set smaller than the ministry
above it. Each became a control rather than a number.

### Band height is not cap height

Reading type size off a rasterised reference means reading the height of a band of ink, which
includes any descender in the line. In Helvetica the ascenders reach 0.718 em against the cap
line's 0.717, so a line with ascenders and no descenders bands at exactly its cap height, and one
with descenders bands at cap plus 0.208. Converting each reading that way turned a spread that
looked continuous into three clean settings.

### The unit is usually the bug

Two constants were wrong not in value but in what they were a share of.

The gap from the mark to a ministry set beneath it was measured against the arms, where the twelve
documents spread 0.125 to 0.397 and no constant fits. Against the wordmark the stacked ones land on
0.453, 0.427 and 0.448. The wordmark is the one drawing whose size holds across the arrangements,
so a share of it means the same thing in all three; a share of the arms does not. The ministry's
size moved to the same unit for the same reason.

The measure the ministry wraps to was in arms heights, which was fine until the ministry's size
became a choice — then the largest setting overran a backstop that could not grow with it. It is
now in cap heights of the ministry's own type, pinned just above the widest line these documents
print whole ("Ministry of Employment and Investment", 25.1 caps in its document and 26.2 as this
project sets it).

### A typed break wins over the measure

The documents were set line by line and disagree about where to break, so there is no rule to
infer. The measure is a backstop for text nobody has broken yet; a line broken by hand is set as
typed. This is the rule the current era already followed.

### What still differs

`selection-1 (2)` reads 0.433 for wordmark-to-arms where the large-arms form uses 0.49, the median
of its three readings — it is the smallest, lowest-resolution image of the set. `selection-1 (5)`
cannot be compared at all: its arms are an embedded raster in the source file. And `selection-1
(7)`'s vertical rule is a page margin, not part of the lockup.

---

## Requirements

**Node 20.19+ or 22.12+**, **a copy of Helvetica**, and one git submodule. A copy of **Adobe
Garamond Pro** is optional and widens the current era's alphabet.

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

### Adobe Garamond Pro, optionally

The current era's wording is set in the serif its marks are drawn with, which is Adobe Garamond Pro.
The letters the published artwork *itself* contains were recovered from that artwork and are
committed, so every official ministry name works out of the box, as do the capitals lifted from
older marks. The rest of the alphabet — the letters that appear in none of them — has to come from
the font:

```sh
GARAMOND_SOURCE=/path/to/adobe-garamond-pro npm run build:current-extras
```

**`GARAMOND_SOURCE` has no default, deliberately.** Picking a licensed font up off the machine
automatically would mean an ordinary `npm run build` quietly bundled it, and a deploy published it.
Without the variable the build simply produces a smaller alphabet, and the app names any letters it
cannot set rather than dropping them silently.

---

## How it fits together

```
artwork/                     the supplied artwork — the source of truth for every era
  crest/, current/, flag/    the arms' wordmark, the ministry-marks PDF (and older marks, in
                             current/lifted/), the flag SVG
  one-offs/                  the gallery's marks, as published, and what each is
scripts/
  build-mark.mjs             extracts the mark, proves all three copies are identical
  build-fonts.mjs            subsets Helvetica, emits the metrics table and the glyph outlines
  build_crest.py             extracts the arms and their wordmark (relative arcs, hence Python)
  extract_current_marks.py   lifts the published ministry marks out of the PDF, unchanged
  recover_current_names.py   reads their wording back, from the outlines and the PDF's text layer
  build-current-glyphs.mjs   the alphabet and metrics the current era typesets from
  lift-current-letters.mjs   the capitals that alphabet lacks, from older published marks
  build-one-offs.mjs         the gallery's one-off marks, lifted from their artwork
  letterFit.mjs              finds the letters in drawn type, and the line they were set on
  build-vendor-json-url.mjs  builds the share-link submodule
  sfnt.mjs, svgPath.mjs,     the font and path surgery those need
  svgAbsolute.mjs
  compare-artwork.mjs        re-renders each lockup over its original and diffs them
vendor/json-url/             submodule — compresses a configuration into a share link
src/
  assets/                    generated artwork: the mark, the flag, the arms, the Parks frame
  logo/                      the framework-free core: layouts, measurement, colour, rendering
  flag/                      the flag identity, its palettes, and the BC Parks badge
  crest/                     the coat-of-arms identity
  current/                   the published marks, and the alphabet their wording is set in
  gallery/                   the one-off marks, which follow no pattern the generator offers
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

### The other three eras

They have no Illustrator source to diff against, so they are checked against printed references
instead — seventeen documents for the flag identity and twelve for the arms, rasterised and
measured rather than eyeballed. All of them reproduce.

The method that matters is measuring each drawing's **own aspect** before trusting any reading
taken from it. A height read off a reference is only meaningful once you know you have found the
right drawing at its true scale, and that check caught both a misidentified arrangement and a
proportion that turned out to have two printed values rather than one. Every constant in
`src/flag/flagLayout.js` and `src/crest/crestLayout.js` carries the readings it came from in a
comment, including the ones that disagree.

Where the documents genuinely disagree the readings are kept as choices rather than averaged into a
value that matches none of them. Averaging was the failure mode throughout this project: a mean
across off-standard published marks, a single stacked proportion standing in for two, one ministry
size standing in for three.

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
  stacked/       …-stacked-ffffff.svg  .pdf  -1024.png  -2048.png
  centred/       …
  horizontal/    …
  columns/       …
  README.txt     what is in the box, and which file to hand a printer
```

Everything goes through the same `renderLogoBlob()` as a single download, so a bundled asset is
byte-for-byte the one you would have got on your own. The default selection is 16 files; ticking
everything is 56, and the button says so before you commit to the work. Already-compressed formats
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

## For agents

Two things here are aimed at software rather than people.

### Handing over a configuration

An agent that has read the manifest can describe exactly the lockup it wants — and then needs a way
to hand it over. `capabilities.json` describes the generator's *browser* exports; it is not itself
an export, so without this the only route was writing the settings out as instructions for a person
to re-enter by hand.

So the configuration is a documented object, in the same vocabulary as the manifest and the tools:

```json
{ "lockup": "columns", "ministry": "Ministry of\nEnvironment", "markAlignment": "top",
  "markColor": "#eee3c0", "background": "transparent", "clearSpace": "none" }
```

Pass it URL-encoded as `?c=…` and the generator opens with those settings already applied, ready to
export — or paste it into the **Configuration** box on the page. Absent fields keep their current
value, so a partial object changes only what it names. **Copy readable link** goes the other way.

### capabilities.json

[`/capabilities.json`](https://ahzs645.github.io/PofBC/capabilities.json) states the whole option
space in one fetch: every lockup with the artwork it was derived from, every format and whether it
holds transparency, the palette, the clear-space presets as both a rule and a number, the ministry
list with the date it was last checked, and how share links are formed. It is generated by
`scripts/build-capabilities.mjs` from the same constants the application imports, so it cannot
drift from what it describes — adding a lockup updates it for free, and a test asserts the two
agree.

It is written in the vocabulary the URL and the tools below accept, so a value read out of it can
be passed straight back in.

### WebMCP

Where the browser implements [`navigator.modelContext`](https://webmachinelearning.github.io/webmcp/docs/proposal.html),
the page registers six typed tools, so an agent calls them instead of hunting for the right button:

| Tool | |
|---|---|
| `get_lockup_state` | The current lockup, wording, colours, the size it would export at, and its contrast |
| `set_lockup` | Lockup, ministry, second line, wordmark, alignment, clear space — any subset |
| `set_colours` | Mark, type and background, independently |
| `export_lockup` | Downloads in any supported format, optionally with the type outlined |
| `get_share_link` | A URL reproducing the current lockup exactly |
| `find_ministry` | Searches the listed ministries, ignoring case and punctuation |

Their JSON Schemas enumerate their options from `LAYOUT_ORDER`, `EXPORT_FORMAT_ORDER` and the rest,
so a tool can never offer something that does not exist.

WebMCP is a W3C draft and currently a Chrome preview, so this is written as pure progressive
enhancement: where the API is absent nothing runs, and the page behaves exactly as it always did.
Nothing else in the app depends on it.

**What was deliberately not done.** An `llms.txt` was considered and skipped — no major provider
documents reading one at inference time, and an analysis of 300,000 domains found no measurable
effect, so it would have been decoration. The accessibility tree is what browser agents actually
read today, and that is served by the ordinary ARIA and labelling the UI already uses.

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

The marks are provincial symbols reproduced from the supplied artwork; their use is governed by the
Government of British Columbia. The Province's guideline documents say in bold that the current
ministry marks must not be altered and must be used exactly as provided, which is why that era
serves them unchanged.

Helvetica and Adobe Garamond Pro are licensed typefaces. The build subsets each from a copy already
on the machine and commits neither — only advance widths and kerning, which are not letterforms.
Distributing a built site distributes the embedded subsets, which is your call to make under
whatever licence covers your copies. `GARAMOND_SOURCE` has no default path so that this cannot
happen by accident.
