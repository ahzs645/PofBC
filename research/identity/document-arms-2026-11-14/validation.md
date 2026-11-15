# Historic identity continuation — validation

Reviewed **14 November 2026** against main
`ebd96bbb10f7eca36b53f980bd8246ef2f452202`.
PR #63 is already merged; this is a separate follow-up. Its original validation
record contains a later browser acceptance note. That prior result is not a fresh
browser test of this continuation.

## Behaviour and build

**97 focused tests passed, with no failures or skipped tests**, including six new
regressions for the colour-state and arms-only preview fixes:

```sh
node --test src/documentArms/renderDocumentArmsSvg.test.js \
  src/site/documentArmsIntegration.test.js src/site/configFormat.test.js \
  src/site/shareLink.test.js src/site/lockupReducer.test.js \
  src/site/useLockupState.test.js src/site/useAgentTools.test.js \
  src/export/exportBundle.test.js
node scripts/build-document-arms.mjs --check
```

The [actual React/JSDOM harness](../document-arms-2026-11-13/check-ui.mjs)
passes **23 interaction checks**. It exercises the real App, controls, lazy preview,
state and SVG download action, including:

- Relevant reference defaults for all four layouts, alternate specimens and the
  separate status of the small official illustration.
- Detail/Whole page switching and exact original-source page links, while the
  rendered SVG remains unchanged by reference selection.
- The Crown-grant map's unknown creation/issue dates, distinguished from the order.
- Arms alone hiding lettering controls and ignoring its saved white lettering
  when choosing a background for black arms.
- Switching identities, relinking colours elsewhere, and returning to Historic
  without losing its independent lettering colour or link preference.
- An actual SVG Blob download, compressed-link reload, readable-link collision
  handling, and links to the 1919 plate and visual guides.

```sh
npm install --prefix /tmp/pofbc-identity-review --no-save jsdom@29.1.1 esbuild@0.28.2
POFBC_TEST_DEPS=/tmp/pofbc-identity-review/package.json \
  node research/identity/document-arms-2026-11-13/check-ui.mjs
BASE_PATH=/PofBC/ node node_modules/vite/bin/vite.js build
git diff --check
```

The **complete production build passed**, including the final selected-button
hover correction. Reference assets remain in the lazy preview, outside the SVG
renderer/export path. No application dependencies or workflows were changed.
The existing Linux TeX Gyre Heros fallback builds the other identities' fonts;
Historic continues to use its unchanged committed outlines.

## Original evidence and rendering

[source-register.json](source-register.json) records the original URLs, exact
file hashes, page counts, PDF page numbers and detail-clip coordinates.

- All **14** original-file/render hashes matched their held files.
- The three PDFs contain **4, 3 and 23 pages**, respectively.
- All **10** page/detail renderings reproduce byte for byte with the recorded
  PyMuPDF version and render settings.
- All image imports and the mappings for **nine reference specimens** were checked.
- The OIC headings, complete grant-map page, supplied blackletter crop and both
  1954 engravings were visually inspected.
- Source scans are page renderings or documented rectangular clips only; they
  have not been cleaned, redrawn, recoloured or assigned invented detail.

Reproduce the five page/detail pairs with:

```sh
python3 research/identity/document-arms-2026-11-14/render-specimens.py
```

The [source comparison sheet](source-evidence-review.png) shows four held crops
without further cropping. Its SVG embeds the exact PNG bytes and uses portable
font outlines for labels. Both sheet formats reproduce byte for byte, and the
final PNG was visually inspected. Rebuild with:

```sh
node research/identity/document-arms-2026-11-14/build-evidence-review.mjs
```

## Browser boundary

This environment could not provide a fresh browser layout/codec test. Direct
Chromium failed before opening a page at its process-singleton socket. The
connected browser's localhost was a separate machine; the Cloud browser could
not connect to this workspace's Vite port. No permission or network policy was
weakened. Vite returned HTTP 200 for the index and relevant modules from its own
process, and the production build and actual React harness succeeded.

JSDOM does **not** establish desktop/mobile layout acceptance or a successful
PDF/PNG/WebP/JPEG browser download for this revision. Those remain visual review
items for this follow-up. The original merged feature's earlier browser result
is preserved as historical evidence only.

The original engraving, exact historical typefaces and period spacing rules
remain unresolved. The new source verification does not authenticate the existing
generated-master vector study. This candidate is published for review with
`[skip ci]`; validation ran locally and no workflow dispatch was requested.
