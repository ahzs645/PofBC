# Validation — missing identity recovery

Validated on 20 November 2026 (America/Cambridge_Bay), against baseline
`882261bb27ce7a2d5c83c967aaa76a4a3f266147`.

## Recorded results

| Check | Result |
|---|---|
| `node scripts/build-identity-expansion.mjs --check` | Passed. All three acquisition batches: 231 bodies, 243 artwork records and 303 unique source/artwork files verified. |
| `python scripts/extract-recovered-identities.py --check` | Passed. All 27 new derivatives reproduce byte-identically from preserved, hash-checked source files. |
| `python scripts/extract-identity-expansion.py --check` | Passed. All 14 earlier derivatives still reproduce after the PDF alpha-channel correction. |
| `node scripts/report-identity-recovery.mjs` | Passed. Same 455 subjects; all 168 previously held subjects remain held; exactly 170 new owners now hold artwork; 117 remain unresolved. |
| `npm run check:identity-coverage` | Passed: 137 tests, 0 failures. |
| React source/register rendering | Passed: 910 subject-page renders (455 subjects in both themes), plus register and overview; local image URLs checked at `/PofBC/`. |
| `npm run build` | Passed. Vite transformed 4,303 modules and produced the client bundle. |
| Source-artwork proof rendering | Passed. All 177 artwork files rendered across nine sheets and visually inspected. |
| Acquired-file inventory | All 222 files in `public/identity-recovered/` are referenced by the acquisition manifest; no exploratory downloads or orphan files remain. |
| `git diff --check` | Passed for code, metadata and authored documentation. Verbatim acquired evidence preserves its published whitespace through scoped Git attributes. |

The new batch holds 177 artwork files and 183 source records, with overlap where an unchanged
website original is both artwork and source. Its 222 unique retained files total 24,872,858 bytes.
The 303-file integrity result includes the two earlier acquisition batches as well.
Git attributes disable line-ending normalization for acquired evidence; staged Git blobs were also
checked against the recorded hashes, so a checkout preserves the same bytes.

## Concrete fidelity corrections verified

- RCY and the reversed Power Smart wordmark now use the gallery’s existing dark-plate flag;
  original white lettering is visible without recolouring the SVGs.
- COIBC extraction retains five outlined initials as well as the office-name glyphs. Its rendering
  matches an independently recovered full signature.
- BC Safety Authority’s original PDF contains an opaque decoded alpha channel and a separate soft
  mask. The empty alpha channel is removed before applying that mask; the black rectangle disappears.
  Replacing the PDF’s source image with the corrected PNG and comparing source-bound renders produced
  only rounding-level differences (mean channel error below 0.013 on a 0–255 scale).
- Kitimat’s literal static JSX component retains all 37 original path strings. No downloaded
  JavaScript is executed. Port McNeill’s embedded JPEG is decoded byte-for-byte and remains raster.
- Logan Lake’s unresolved gradient appears only in an unused simple `.st1` rule. Applied `.st0`
  and `.st2` styles are intact; the original SVG remains unchanged.
- Supplementary Transit Security, AirCare and Power Smart source paths resolve to retained files;
  the builder now verifies these references in addition to the principal source.
- Historical Film/Film + Media, Film Commission, ITA/ITAC, and BCAS/EHSC ownership and dates remain
  separate. Blue Bus’s magenta production-proof limitation and AirCare’s archive-capture context
  survive the generated data normalization.

## Runtime and limits

Extraction used PyMuPDF 1.26.6 and Pillow 13.0.0. Original artwork has not been substituted with
generated imagery, traced outlines or replacement type.

The repository’s existing Linux build uses TeX Gyre Heros when licensed Helvetica is unavailable;
this affects unrelated generated provincial lockups, not the collected originals. The production
build reports its existing large-chunk advisory. The server-render check reports the existing
`useLayoutEffect` warning for custom select controls; all asserted render checks pass.

**Live browser/viewport interaction was not validated.** The local Chromium process could not
create its required socket (`Operation not permitted`). Source proof sheets are not application
screenshots, and the 910 server renders do not claim to exercise browser interaction.

Validation ran locally. The commit uses `[skip ci]`; no GitHub Actions run was requested for this
data-acquisition branch. The pull request is a draft for review, with no deployment or main-branch merge.
