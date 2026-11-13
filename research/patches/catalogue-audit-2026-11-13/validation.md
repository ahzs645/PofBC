# Validation — patch catalogue review

Reviewed 13 November 2026 against PofBC baseline [`1fb9e08`](https://github.com/ahzs645/PofBC/commit/1fb9e08dbb105bd691bed0790c81365b46ebc4f0) plus the accompanying gallery changes. Patcher's published implementation is [`da92d58`](https://github.com/ahzs645/patcher/commit/da92d583addc66b62d3f243a9684eccb3f9a73ec); its tree `420a5d723c7c41409ee3a36b5aa822dc0ade2747` matches the tested local implementation. No full-site acceptance is implied by these checks.

## Reproducible commands

Run from the PofBC root with its submodules initialized and development dependencies installed. Patcher's own `typecheck` script requires its TypeScript/Vite development dependencies. The session used Node 24.22.1 and TypeScript **5.9.3**; the repository permits TypeScript 5.x through `^5.6.0`.

```sh
node --test \
  src/patches/patches.test.js \
  src/patches/patchCatalogue.test.js \
  vendor/patcher/src/library-cache.test.js \
  vendor/patcher/src/template-families.test.js

npm --prefix vendor/patcher run typecheck

node vendor/patcher/scripts/verify-library.mjs

node vendor/patcher/scripts/audit-library.mjs > \
  research/patches/catalogue-audit-2026-11-13/storage-audit.json

node scripts/check-patch-viewer-build.mjs
```

These commands do not start GitHub Actions. The storage audit uses local files and has no network dependency. `library:verify` here compares the reconstructed artwork with the saved manifest and supplied drawings; `--source` was not used to re-download and compare the entire original atlas snapshot in this final pass.

## Final focused results

| Check | Result and scope |
| --- | --- |
| Existing PofBC patch tests | **8 passed**: catalogue ownership, collection boundaries, source aliases, reconstruction and history behavior |
| PofBC browsing-helper tests | **8 passed**: family grouping, secondary variants, exact-ID precedence, intersecting filters, generated-colourway/source counting and URL state |
| Patcher cache tests | **8 passed**: in-flight sharing, failure retry, UTF-8 byte bound, eviction, oversized values and stale completion/rejection races |
| Patcher family tests | **5 passed**: real catalogue membership, variant references, invalid members/groups, collection boundaries and numbered badge specimens |
| **Combined focused tests** | **29 passed, 0 failed, 0 skipped** |
| Patcher typecheck | **Passed** using TypeScript 5.9.3 |
| Reconstructed artwork | **168 of 168** match saved SHA-256 and byte lengths; **28,903,909** reconstructed bytes from **8,333,874** stored bytes |
| Storage audit | **No** missing files, summary mismatches or unreferenced generated files; [report](storage-audit.json) includes input hashes |
| Targeted production build | **Passed** with production base **`/PofBC/`**, **455 emitted assets**, real gallery/viewer CSS, library assets and digitizing worker |
| Source-crop packaging | **154 patch records**, **191 local source-crop references** checked for existence in the targeted output |

The build uses [check-patch-viewer-build.mjs](../../../scripts/check-patch-viewer-build.mjs). It exercises the actual patch view and dependencies without running the unrelated full-site asset pipeline. The 191 figure counts references, not necessarily 191 unique photographs.

## DOM integration evidence

A session harness using **jsdom 29.1.1**, the real React gallery, real Patcher manifest/helpers and real template catalogue passed seven scenarios. The detail viewer was replaced only at its lazy import boundary with a test double, so this verifies state and DOM behavior rather than canvas output or visual layout. These checks are separate from the 29 tests above; the session harness is not a committed browser automation suite.

| Scenario | Observed result |
| --- | --- |
| Initial gallery and lazy detail boundary | **126 cards / 154 variants**; detail module evaluated **0** times before opening |
| Cross-organization ministry-shield family | **15 cards** across **5 organizations**: Parks, Environment, Corrections, Attorney General, Highways |
| Organization/family intersection and clearing | **5** scoped cards, **126** after clearing; selected grouping retained |
| Exact secondary-variant search | `FO-green-gold-black` selected its own preview/link, with the explicit generated-colourway notice |
| Open, Back, Forward and Close | Grouping, family and query preserved; detail module evaluated **once** after first opening |
| Historical aliases | `R22-O01` opened `FO-forest-service`; `S56-O53` opened `S29-O01` |
| Invalid URL filters | Safe fallback to **126 cards**, with invalid filters clearable |

The real `loadPatchSvg()` was also exercised with file-backed fetch responses from emitted production assets. For `FO-green-gold-black`, the first load made **3** fetches and the second made **0 additional** fetches. Its resulting SHA-256 was:

```text
d31e5f8416f5918032e6b20772e25d65c2d8caac6764a68990f588411db25e53
```

This confirms cache behavior through the actual loader and production asset references. It is not a measurement of browser network requests or a browser rendering check.

## Browser and full-site limits

Actual browser acceptance was attempted and remained blocked:

- Chromium exited **before loading the application**, reporting `process_singleton_posix.cc:297 socket() failed: Operation not permitted (1)`.
- The configured automatic approval policy rejected the execution escalation (`sandbox_approval=false`).
- The advertised cloud browser could not reach the local preview (`net::ERR_CONNECTION_REFUSED`).

Consequently, **desktop visual layout, mobile layout and horizontal overflow, browser network request counts, cache behavior in a real browser, and actual embroidery preview rendering are not verified**. No desktop/mobile screenshots are claimed. DOM execution does not resolve these omissions.

The **full site build and full site test suite were not run** as part of this focused review. Before visual acceptance, use the targeted build or a fully configured site preview in a working browser and repeat the seven scenarios above at desktop and mobile widths, then check the real embroidery viewer and exports.
