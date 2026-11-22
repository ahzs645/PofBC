# BC health logo vector findings, 22 November 2026

A supplied search for original vector artwork of three historical BC health identities. The
search's own report is `search-README.md`, its summary `findings.json`.

## Vancouver/Richmond Health Board: original vectors found

`proposed-assets.json`, read by `scripts/build-collected-marks.mjs` (VECTOR_SEARCHES). The board's
logo is drawn as vector paths in two of its own publications. The isolated drawing is in
`public/identity-collected/vancouver-richmond-health-board/`:

- `…-original-colour-lockup.svg`: the red-and-purple logo with its name and tagline, from the cover
  of "Take Care", revised 2000 (Internet Archive, 26 April 2003). It now leads the board's colour
  card. The November 2000 and April 2001 images of the same logo become its versions.
- `…-original-colour-emblem.svg`: the apple-heart emblem alone, from the same cover.
- `…-original-purple-lockup.svg`: the one-colour purple logo with an open heart, from the cover of
  the Directional Plan 2000–2003 (Internet Archive, 7 January 2004).

Each comes with the isolated PDF, which keeps the publication's named inks (PANTONE 1797 CVC red,
PANTONE 2627 CVC purple); the SVG colours are RGB conversions. The supplier's SVGs were written
with an `ns0:` namespace prefix; the copies here use the default SVG namespace, with the drawing
unchanged. `vancouver-richmond/` holds the provenance and the second review (`vector-provenance.json`,
`independent-review.json`), PNG previews, the source crops, and `extract_vrhb_vectors.py`, which
reproduces the extraction from the two publications (not kept here; their archive URLs are in
the register).

## South Cariboo Community Health Council: no vector; one more image

`source-register.json`, read as a history (HISTORIES). No original vector was found in the 26
archived PDFs (149 pages) under the council's two web addresses. Its black-and-grey logo, a 200 × 100
JPEG from the opening-ceremonies thank-you page, captured on 16 September 2004, is added as a version
of the green 1999 logo. Archive indexes and the per-PDF inspection are in `south-cariboo/`.

## Greater Trail Community Health Council: no change

No vector was found among the 72 archived URLs of its site. The gallery's 2001 GIF is byte for byte
the archived original and stays as it is. The archive index and link survey are in `greater-trail/`.

These are bounded searches of what the archive kept. They do not show that no master ever existed.
