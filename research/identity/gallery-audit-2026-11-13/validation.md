# Gallery cleanup validation

Reviewed 13 November 2026, based on `main` at `1fb9e08dbb105bd691bed0790c81365b46ebc4f0`.

## Results

| Check | Result |
|---|---|
| All focused gallery tests | **81 passed, 0 failed**, including 9 palette-renderer tests |
| Real React interaction checks in JSDOM | **10 passed, 0 failed**, zero DOM errors |
| Production build of the actual GalleryView | Passed with `/PofBC/` base |
| Referenced source, preview, extra-download and display files in the scoped build | **503 present, 0 missing** |
| Collected source-file integrity | **208/208 SHA-256 values match** |
| Gallery identity integrity | **242 entries, 242 unique IDs** |
| Source catalogue regeneration | Reproduces the committed generated catalogue |
| Whitespace/errors in patch | `git diff --check` passed |

The gallery tests cover source checksums, collection ownership, old links, dates, timelines, vector/hybrid labels, source SVG selection, and the new palette groups. The palette tests compare Northern Health and StrongerBC output against their actual published counterpart drawings. Knowledge Network retains all 35 source paths, with exact RGB colours supported by the official source kit.

## Reproduce catalogue and gallery tests

```bash
git submodule update --init --depth 1 vendor/json-url
npm ci --ignore-scripts
node scripts/build-current-extras.mjs
node scripts/build-collected-marks.mjs
node --test src/gallery/*.test.js
git diff --exit-code -- src/gallery/collectedData.js
```

## Scoped production preview

```bash
node scripts/build-fonts.mjs
node scripts/preview-gallery.mjs --build --base /PofBC/ --out dist-gallery
```

For an interactive local preview, omit `--build`:

```bash
node scripts/preview-gallery.mjs --base /PofBC/
```

This loads the actual gallery components and styles, not a substitute gallery. The project's existing local TeX Gyre fallback was used for unrelated generator font exports because licensed Helvetica is not installed on this Linux workspace. The changed collected-logo masters already contain their original outlined lettering and do not use that substitute font. No generated fonts or build outputs are committed. The scoped bundle emits the existing large-chunk advisory; it is not the full site's deployment build.

## Interaction acceptance

[ui-validation.json](ui-validation.json) records the 10 checks, exact source hashes, results, and limitations. The real GalleryView and CollectedPaletteView were compiled with Vite, mounted with React DOM in JSDOM, and supplied the actual stored SVG bytes through a local file-backed fetch substitute. No component or palette-rendering implementation was replaced.

The checks verify:

- All four Knowledge palettes retain their original geometry and put identical SVG bytes in preview and download.
- Colour changes reuse one loaded SVG and choose the appropriate light/dark display ground.
- Old Knowledge EPS, SVG and PNG IDs, Northern Health black and both StrongerBC reverse IDs open the corresponding design and colour, including mark-only URLs.
- Failed requests disable the generated download; the original remains accessible, and retry recovers.
- Navigating from Knowledge to another design clears its colour parameter; an explicit colour survives reload.

## Browser acceptance still required

Local Chromium was attempted and failed before opening a page: `process_singleton_posix.cc:297`, `socket() failed: Operation not permitted (1)`. JSDOM does not verify physical layout, font rendering, browser image decoding or an actual file saved through a browser's download UI. Desktop/mobile visual acceptance and a real SVG download remain unverified; the pull request is a draft for that review.

The artwork comparison in `palette-proof.png` was rendered from the actual SVG palette outputs and visually inspected. It verifies the visible artwork choices, not the browser interface.

## Publishing scope

All validation ran locally. The commit includes `[skip ci]`; no workflow dispatch, production deployment or merge is part of this change.

## Browser acceptance (2026-11-13, after merging with the BC Trade addition)

Run in Chromium (Playwright) against the Vite dev server, at 1300 × 1000 desktop and an emulated
iPhone 13, plus the desktop in dark mode. `npm test` passed (906 tests) on the merged tree, and the
collected-marks, display and collecting generators reproduced the committed files unchanged.

- Old links open the right design and colour: Knowledge EPS → Full colour, Knowledge SVG → White
  lettering, Knowledge PNG → Full colour, Northern Health black → Black, StrongerBC RGB reverse →
  Reversed, StrongerBC solid reverse → White.
- Each of Knowledge Network's four choices renders (the image decodes), updates `colour=` in the
  URL, and its **Download SVG** produces a real browser download (`knowledge-network-<choice>.svg`)
  whose bytes are identical to the preview's.
- No horizontal page scroll at either width; the four choices wrap to two lines on the phone without
  overflow. Reversed choices sit on the dark preview ground in both themes.
- No page or console errors.
