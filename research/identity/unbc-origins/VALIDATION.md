# UNBC origins implementation review

Reviewed 19 November 2026 against `main` at
`00cf5d68d7574897a52414f8b0744c1a4c0e508d`.

## What changed

The UNBC identity subject now has a formation feature with narrative, ten
milestones, source links and eight featured campaign objects. The Interior
University Society has its own searchable subject and 26-design collection.
The `campaigned-for` relationship resolves in both directions. UNBC's logo and
each campaign design link to the same origin story.

The public download retains the supplied version 1.2 vector exports and font
corrections. Its compact distribution and evidence limits are documented in
the adjacent README and public reconstruction notes.

## Completed checks

- 44 existing focused tests passed across the gallery collection, identity
  subjects, coverage, search, gallery URL handling and related-body suites.
- `node scripts/check-identity-render.mjs` rendered 910 subject/theme
  combinations, the register and the overview. Image paths resolved beneath
  `/PofBC/` and referenced existing local files.
- `node scripts/preview-gallery.mjs --build --base /PofBC/ --out dist-gallery`
  built the actual gallery components successfully, including the new public
  assets. This is the gallery production preview, not a full-site build.
- Targeted assertions verified IUS's 26 reconstructed entries, UNBC's separate
  original-vector entry, relationship direction, search aliases, and clearing
  all four origin-story fragments when navigating to another subject.
- The download packaging check reproduces the archive. Import checks verified
  all 78 supplied SVG/PDF/EPS exports and all ZIP payload checksums.
- The staged whitespace check passed for application code, documentation and
  metadata. The supplied EPS exports retain their original trailing spaces so
  that the imported artwork remains byte-for-byte identical to the supplied kit.

The preview uses the repository's supported TeX Gyre font stand-in for unrelated
generator components. The supplied IUS artwork already contains outlined type
and was retained byte-for-byte.

## Visual verification still needed

A live browser check could not be completed in this workspace. The installed
headless Chromium process was blocked by the command sandbox's socket policy;
both connected browsers could not reach the local preview. The automatic
approval gate rejected an attempt to run the local preview/browser outside
that sandbox. No successful desktop or mobile screenshot is claimed.

For browser acceptance, open
`?view=gallery&subject=university-of-northern-bc#unbc-origins` in the gallery
preview. Check the narrow layout, light/dark themes, section jumps, IUS/UNBC
record links, all-designs navigation, individual SVG/PDF downloads, the ZIP,
and Back/Forward. The fragment-aware origin story is also reachable from the
UNBC logo and IUS artwork pages.
