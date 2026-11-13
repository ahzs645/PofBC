# Historical document identity — validation

Baseline: `74e9e58767856d3a4f7ea649a812fa9dc2d7aeeb` (`main`). Reviewed 13 November 2026.

The candidate was updated after PR #61 merged. Its 35 changed paths do not overlap that
update; the focused suites, React interaction checks and full production build were rerun on
this baseline before publication.

## Automated checks

**91 tests pass, 0 fail, 0 skipped** in the focused renderer, configuration, reducer, sharing,
WebMCP and export/bundle suites:

```sh
node --test src/documentArms/renderDocumentArmsSvg.test.js \
  src/site/documentArmsIntegration.test.js src/site/configFormat.test.js \
  src/site/shareLink.test.js src/site/lockupReducer.test.js \
  src/site/useAgentTools.test.js src/export/exportBundle.test.js
node scripts/build-document-arms.mjs --check
git diff --check -- . ':(exclude)src/documentArms/fonts/unifrakturmaguntia/OFL.txt'
```

The actual `json-url` compressor was built and exercised. Every new layout survives both URL
formats, including separate colours, transparency, padding and linked-colour behaviour on the
next edit. A regression covers a readable URL replacing an older compressed token. Legacy
compressed tokens keep their existing format.

The SVG export is compared byte for byte with the preview renderer, with network fetch replaced
by a throwing function. Exports contain paths and provenance metadata, with no reference image,
live text or font load. A real SVG bundle is unzipped to verify its contents and reconstruction note.
The source path, natural proportions, lettering bounds, escaped inputs and deterministic font
outlining are checked separately.

The upstream Unifraktur licence is preserved byte for byte, including its original CRLF endings
and trailing spaces. Only that third-party file is excluded from the whitespace check.

## Actual React interaction checks

**12 JSDOM checks pass** against the real `App`, hook, controls, lazy document preview and export
action. They cover all four headings, reference visibility, white-on-transparent automatic
backdrop, a manual preview backdrop, switching identities and back, downloading the actual SVG
Blob, copying and reopening a compressed link, readable-link collision handling, and the related
plate/manual links.

The harness is [check-ui.mjs](check-ui.mjs). It compiles the actual generator with esbuild and
leaves unrelated lazy views deferred; no generator component or renderer is replaced. The DOM
provides clipboard/download plumbing and a canvas capability probe. This does **not** exercise a
browser's layout, image decoder, canvas rasterization or PDF rendering.

Optional test dependencies can be kept outside the application:

```sh
npm install --prefix /tmp/pofbc-identity-review --no-save jsdom@29.1.1 esbuild@0.28.2
POFBC_TEST_DEPS=/tmp/pofbc-identity-review/package.json \
  node research/identity/document-arms-2026-11-13/check-ui.mjs
```

## Production build and visual proof

The complete Vite production build succeeds with `BASE_PATH=/PofBC/`, after initializing the
pinned submodules and building the usual generated assets. This is the full application, not a
standalone replacement of the generator. The new SVG renderer is a separate lazy chunk; the
reference PNGs resolve to fingerprinted build assets.

```sh
node scripts/build-mark.mjs
node scripts/build-fonts.mjs
node scripts/build-vendor-json-url.mjs
node scripts/build-current-extras.mjs
node scripts/build-geo-toolkit.mjs
node scripts/build-capabilities.mjs
BASE_PATH=/PofBC/ node node_modules/vite/bin/vite.js build
```

The existing Linux font fallback uses TeX Gyre Heros for the older unrelated generator identity.
The new document headings use their committed outlined geometry and are unaffected by that fallback.

All four study renderings and the [comparison sheet](review-layouts.png) were visually inspected
after rendering with resvg. The comparison uses the full original screenshots without alteration;
embedded screenshot bytes match the source hashes. It is **not a scale-matched overlay** and does
not establish engraving or typeface accuracy. Rebuild it with:

```sh
node research/identity/document-arms-2026-11-13/build-review-layouts.mjs
```

## Remaining browser acceptance

Local Chromium was attempted with Playwright and failed before opening a page:
`process_singleton_posix.cc:297 … socket() failed: Operation not permitted (1)`.
There is therefore no claim of desktop/mobile browser acceptance or successful browser
PDF/PNG/WebP/JPEG downloads. These remain review items; the existing export pipeline is used for
those formats. The historical engraving, original typefaces and exact spacing also remain
unverified, as stated in the interface and every SVG.

The candidate is published as a draft PR with `[skip ci]`. No workflow dispatch or production
deployment is part of this change.
