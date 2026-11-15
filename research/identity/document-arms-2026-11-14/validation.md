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
renderer/export path. No application dependencies were changed.
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

## Browser acceptance completed - 14 November 2026

The earlier browser limitation is resolved. The installed Chromium headless shell
from `@sparticuz/chromium` runs in this environment without the desktop browser's
process-singleton socket. No environment permissions or network policy were changed.

The [reproducible browser harness](check-browser.mjs) runs the **complete Vite
production build**, with no substituted application components. Its
[recorded result](browser-acceptance/browser-check.json) includes the tested source
file hashes, production index hash, browser version and actual download hashes.

**57 browser checks passed** in Chromium **138.0.7204.0**:

- All four layouts at **1440 x 1000**, **390 x 844** and **320 x 568**, in both
  light and dark themes: 24 layout/theme/viewport cases, with decoded references,
  no document overflow, and segmented buttons contained inside their tracks.
- All **nine** reference specimens at all three widths: decoded images, correct
  source links/page fragments, alt text, and Detail / Whole page switching for
  the five document specimens. Switching a reference leaves exported SVG unchanged.
- Historic's independent text colour and link preference survive linking another
  identity's colours. Black Arms alone ignores saved white lettering for the Auto
  backdrop and 21:1 contrast; restoring a heading restores that lettering.
- Manual preview backgrounds leave transparent export artwork unchanged.
- Actual **SVG, PDF, PNG, WebP and JPEG** download actions succeed with the correct
  file signatures. SVG contains outlines and the reconstruction qualification,
  with no reference images or live text. All three raster files decode at
  **2048 x 684 pixels**. The one-page PDF was opened and visually inspected using
  Poppler's rendering: [download review](browser-acceptance/download-pdf.png).
- A compressed share link reopens the complete application; copying a readable
  link removes a previous compressed token.

No page/console errors, missing local assets or unintended external requests were
observed. The script checks external link destinations; the retained original
PDFs/images are separately verified by their recorded hashes. These are Chromium
viewport checks, **not physical iPhone or Safari testing**.

### Small-phone fix found by this review

The first 320-pixel run exposed a 357-pixel-wide page. The implicit grid column and
unbreakable Historic labels imposed their minimum content width on the page. The
layout now uses a shrinkable grid column and children, long heading labels can
wrap, and the clear-space and download-format choices can wrap inside their tracks.
The full browser acceptance was rerun successfully after the fix.

| Viewport | Light | Dark |
| --- | --- | --- |
| Desktop | [Screenshot](browser-acceptance/desktop-light.png) | [Screenshot](browser-acceptance/desktop-dark.png) |
| Phone | [Screenshot](browser-acceptance/phone-light.png) | [Screenshot](browser-acceptance/phone-dark.png) |
| Small phone | [Screenshot](browser-acceptance/small-phone-light.png) | [Screenshot](browser-acceptance/small-phone-dark.png) |

Reproduce with an installed Playwright and compatible Chromium executable:

```sh
npm run build:assets
BASE_PATH=/PofBC/ node node_modules/vite/bin/vite.js build
POFBC_BROWSER_DEPS=/path/to/browser-dependencies/package.json \
POFBC_CHROMIUM_EXECUTABLE=/path/to/chromium \
  node research/identity/document-arms-2026-11-14/check-browser.mjs
```

Both environment variables are optional when Playwright and its browser are
available through the project's normal module resolution. Output goes to
`tmp/historic-browser` unless `POFBC_BROWSER_OUTPUT` is set.

## Fresh local validation and release

- **97 focused tests pass**, zero failures/skips; document-arms geometry reproduces.
- **23 actual React/JSDOM interaction checks pass** after the responsive fix.
- Full project suite: **966 pass, zero failures, eight explicitly skipped**, out
  of 974 checks. Six skips concern optional extracted current-ministry SVG files;
  two concern exact Helvetica geometry when the documented TeX Gyre Heros fallback
  is used. Historic's committed outlines do not depend on that fallback.
- The complete production asset build and Vite build pass.
- All **14** source/render hashes were freshly rechecked and matched.
- Independent review of the state, evidence controls and responsive CSS found no
  blocking defect. `git diff --check` passes.

The complete suite initially lacked research/brandkit files because the inherited
checkout was sparse. Those tracked inputs were materialized and the full suite
rerun to the result above; no application change was needed for that setup issue.

The Pages workflow now offers an optional manual `run_tests` input, defaulting to
false, so a locally reviewed release can build and deploy without repeating its
full test suite. Main-push deployments retain their existing test behavior. This
uses the established macOS build and Pages deployment jobs; it does not claim a
runner-free deployment. Publication and merge commits use `[skip ci]` to avoid
unrelated workflows before the intentional manual release.

The original engraving, exact historical typefaces and period spacing still need
better primary artwork. The separate measured overlay study does not authenticate
or replace the generated-master renderer.
