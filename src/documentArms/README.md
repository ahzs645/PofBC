# Historical document-arms studies

These four layouts make the earlier document-heading tradition available beside the
other identities. They are **source-informed studies**, not recovered official lockups.

## What is reused

The arms use the exact `1146 × 1283` path already held in
`artwork/stationery/grace-mccarthy/evidence/supplied-arms-fragment.txt` and used by
PlateForge's `1919-cardboard` template. PlateForge describes this as a vector conversion
of a generated master, **not a verified historical or official drawing**. The supplied
document photographs show different engravings. Reusing the path connects the two
tools; it does not establish an authentic historical master.

The renderer preserves the natural proportions with a uniform scale. Every exported
SVG carries the caveat, source paths, source checksums and font choices in its
`desc` and `metadata`. Nothing is auto-traced from the supplied screenshots.

## Layouts and lettering

| Key | Wording | Modern font used for this study |
| --- | --- | --- |
| `emblem` | Arms only | None |
| `split-serif` | BRITISH / COLUMBIA | Noto Serif Bold |
| `government` | THE GOVERNMENT OF / THE PROVINCE OF BRITISH COLUMBIA | Barlow Condensed Bold |
| `split-blackletter` | British / Columbia | UnifrakturMaguntia Book |

The historical typefaces have **not** been identified. The fonts are modern open-font
stand-ins. The last layout follows the supplied crown-grant heading, whose date has
not been established. Its blackletter face is a deliberate study choice, not a claim
that that face appeared in the source.

Noto Serif and Barlow Condensed are the existing pinned `@fontsource` dependencies.
The unmodified UnifrakturMaguntia source font is held under `fonts/unifrakturmaguntia/`
with the SIL Open Font License and upstream Git blob identifiers. Only the two outlined
words enter the renderer; no font file is requested at runtime.

## Rendering and rebuilding

`layouts.js` holds the lightweight layout list and caveats. The detailed geometry is
separate, so callers can load `renderDocumentArmsSvg.js` on demand.

```js
const { svg, box } = renderDocumentArmsSvg({
  layout: 'split-serif',
  markColor: '#000000',
  textColor: '#000000',
  background: 'transparent',
  clearSpaceFactor: 0.05,
  pixelWidth: 2048
})
```

The result is self-contained SVG path artwork. Preview, SVG, PDF and raster exports
can use the same bytes. There are no external paint references, font loads, embedded
images or live text. `documentArmsSize()` returns the size before clear space, matching
the other identity renderers. `layoutDocumentArms()` also exposes the positioned
lettering and the uniformly scaled arms for bounds checks.

```sh
node scripts/build-document-arms.mjs
node scripts/build-document-arms.mjs --check
node --test src/documentArms/renderDocumentArmsSvg.test.js
```

The build script hashes its held source and font bytes and outlines the complete
shaped words, including kerning. The generated output is deterministic. It deliberately
does not attempt to infer a historical typeface or impose the later visual-identity
manual's spacing rules on these earlier document examples.
