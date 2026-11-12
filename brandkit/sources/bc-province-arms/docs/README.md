# Province of British Columbia: arms and wordmark (reconstruction)

**A historical reconstruction for reference and study. This is not the Province’s current
identity**, which the Government of British Columbia publishes.

The identity that followed the flag one: the full achievement of arms with the BRITISH COLUMBIA
wordmark, and a ministry set against it. Its years are not yet confirmed.

- **The arms and the wordmark are artwork**: both were lifted from a page extraction (PofBC
  `scripts/build_crest.py`) and are drawn as paths, so the wordmark needs no font and cannot be set
  in the wrong one. Only the ministry is typeset, in Helvetica (TeX Gyre Heros here, with the same
  widths).
- **Seven signatures**: side by side and stacked, alone; and with the ministry beside, below,
  centred under the stack, flush with the wordmark, or under the large-arms stack. Every proportion
  is PofBC’s (`src/crest/crestLayout.js`), read off twelve printed documents, with the disagreements
  between documents kept as choices rather than averaged.
- **Every ministry from 1983 to 2011** (Logos → ministries): since the identity’s own years are not
  confirmed, the list spans the flag identity to the BC mark.
- **One ink.** Every document measured sets the lockup dark on light in a single ink; black, BC
  Blue and white are offered.

Wording set beside the mark is centred on it in PofBC, so the block moves as it gains lines; here
that signature is placed for a two-line ministry. Wording set below hangs from the mark exactly as
PofBC sets it.

Rebuild with `npm run brandkit:build -- bc-province-arms` in PofBC.
