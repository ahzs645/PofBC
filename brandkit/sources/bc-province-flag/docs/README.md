# Province of British Columbia: the flag identity, about 1983–2005 (reconstruction)

**A historical reconstruction for reference and study. This is not the Province’s current
identity**, which the Government of British Columbia publishes. The years are working dates, not
confirmed adoption dates.

BC beside the waving provincial flag, with a ministry set beside or below it. Everything here is
PofBC’s flag identity, written down as brandkit data:

- **The flag** is the supplied Spirit of BC drawing, twelve shapes kept as drawn. Its white is the
  page between them, which is why, on a coloured ground, the documents set the whole lockup in one
  ink, and why this kit offers one-ink colourways beside the full-colour ones.
- **Two full-colour palettes.** *Official* is the standards page’s Pantone Blue 072C, Red 032C and
  Yellow 109C; *Modern* is the navy, red and gold the artwork was supplied in, a later recolouring.
  Neither is corrected into the other.
- **Six signatures**: the symbol alone; BC and the flag with the ministry below or beside; the
  flag above BC, with or without “Province of British Columbia”; and the flag alone. Their
  proportions come from seventeen printed references (PofBC `src/flag/flagLayout.js`, where each
  constant carries the readings it came from, including those that disagree).
- **Every ministry from 1983 to 2005** (Logos → ministries), from PofBC’s ministry history.
- **Helvetica** is set in TeX Gyre Heros, which has Helvetica’s widths, under the GUST Font License.

One approximation: PofBC grows wording set *beside* the symbol upward, so its last line sits on
the BC baseline. brandkit hangs a stack from its first line, so that signature is placed for a
two-line ministry, the commonest; a longer name runs below.

Rebuild with `npm run brandkit:build -- bc-province-flag` in PofBC.
