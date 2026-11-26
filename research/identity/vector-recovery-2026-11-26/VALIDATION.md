# Recovery validation — 26 November 2026

## Source and model checks

- 48 targeted tests passed across `vectorRecovery`, `identityCoverage`, `collectedCollections` and `postsecondarySubjects`.
- All 130 source files match their recorded SHA256 values. All 109 newly accepted SVGs contain native geometry without embedded raster images, live text, scripts, foreignObject or external href dependencies.
- All 1,083 baseline design IDs remain. Independent integration review also confirmed preservation of all 697 prior body records, 1,432 prior asset records and every existing display record, apart from the declared preferred-vector/additional-sighting patches.
- Review identified and corrected the human-readable VIU locators so each colourway cites its own original PDF ZIP member.
- Code and metadata pass the whitespace check. The complete staged check reports six trailing-whitespace lines inherited from the byte-original Selkirk SVG and its two generated display copies; those official source bytes are retained without normalization. No other staged whitespace issue was found.

## Actual gallery UI

The actual gallery was served through the repository preview with Chromium. The full pass inspected 60 affected subject pages and 130 selected artwork versions in **both light and dark themes**: 120 subject renders and 260 detail renders. Checks covered image loading, subject headings, format labels, selected source download links and all 130 downloaded files against their recorded SHA256 values.

The first run found two **pre-existing** dark preview files absent from the sparse local checkout: Colwood's annual-report reverse and Nanaimo's current reverse signature. Both were restored byte-for-byte from baseline commit `279cba21ce0afd2a6d21e082019f2a736932d0cb`, with their Git blob hashes verified. A focused second pass checked both subject pages, all ten recovered versions belonging to those subjects, and their downloads in both themes: **4 subject renders, 20 detail renders, 10 downloads, zero failures**. No source or app change was needed to resolve these checkout omissions.

Representative cards and detail screenshots were inspected for NVIT, CNC, UBC Okanagan, Nanaimo Airport, Sooke, OUC, Sparwood and BCTC. Screenshots are internal verification material and are not bundled as deliverables.

## Offline download bundle

All 130 artwork images decoded, all 269 local file links resolved, and the format/name filters returned the expected counts. The remaining-gap filters returned 453 subject records, 550 design records and 88 raster matching follow-ups. The index also passed a 390-pixel mobile-width check without horizontal overflow.

## Reproduction and limits

Run the targeted tests:

```sh
node --test src/gallery/vectorRecovery.test.js src/gallery/identityCoverage.test.js src/gallery/collectedCollections.test.js src/gallery/postsecondarySubjects.test.js
```

Run the real-gallery browser check with Playwright available (set `NODE_PATH` if needed):

```sh
CHROMIUM_EXECUTABLE_PATH=/path/to/chromium node scripts/check-vector-recovery-render.mjs
```

The script starts its own preview server. `RECOVERY_QA_DIR` selects the output directory. `RECOVERY_QA_SUBJECTS=municipality-colwood,airport-cycd` limits a follow-up to named affected subjects; omit it for the full recovery batch.

[Machine-readable summary](validation/summary.json), [initial full pass](validation/gallery-full-pass.json), and [restored-file follow-up](validation/gallery-restored-followup.json) retain the results and resolved checkout issues. The full application production build and unrelated repository test suites were not run. Source-native flags for legacy artwork are inherited from existing repository evidence and were not all revalidated.
