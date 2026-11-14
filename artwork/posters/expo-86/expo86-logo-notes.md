# Expo 86 gallery asset retrieval

## Recommended source for the poster

`expo86-logo-source.svg` is an unchanged copy of:

- Repository: https://github.com/ahzs645/PofBC
- Commit: `1fb9e08dbb105bd691bed0790c81365b46ebc4f0`
- Path: `public/identity-collected/expo-86-corporation/expo86-symbol.svg`
- Pinned source: https://raw.githubusercontent.com/ahzs645/PofBC/1fb9e08dbb105bd691bed0790c81365b46ebc4f0/public/identity-collected/expo-86-corporation/expo86-symbol.svg
- GitHub source view: https://github.com/ahzs645/PofBC/blob/1fb9e08dbb105bd691bed0790c81365b46ebc4f0/public/identity-collected/expo-86-corporation/expo86-symbol.svg
- Gallery record: https://projects.ahmadjalil.com/PofBC/?view=gallery&logos=collected-expo-86-corporation

This is the complete stacked EXPO / three-ring 86 lockup, excluding TM.
It consists of native vector line, circle and path elements, with no bitmap or font dependency.
The original viewport is 263 × 347. There is a small transparent margin around the artwork.
The repository's light display variant uses a tighter viewBox of `9.754 19.88 237.712 310.854`, but the original source supplied here is unchanged.

The EXPO letters use black (#000000); the ring symbol uses blue (#1F92CF).
The poster photograph uses a single dark ink. Recolouring an imported copy to the poster's dark ink
can preserve every original coordinate and stroke width. Keep this source file unchanged.

## Second vector variant

`expo86-wordmark-source.svg` is an unchanged copy of
`public/identity-collected/expo-86-corporation/expo86-wordmark.svg` at the same commit.
Despite the filename, this file contains **only the three-ring 86 symbol and diagonal**, in blue (#0075bd),
with no EXPO lettering and no TM. It is not the appropriate complete lockup for this poster.

Pinned source:
https://raw.githubusercontent.com/ahzs645/PofBC/1fb9e08dbb105bd691bed0790c81365b46ebc4f0/public/identity-collected/expo-86-corporation/expo86-wordmark.svg

## Match to the supplied photograph

`upload/46925791_3.jpg` is a clear 1800 × 1350 closeup of the poster's lower-left logo and footer.
It confirms the stacked EXPO / three-ring 86 arrangement, dark ink, and a small **TM** at lower right.
**Neither repository SVG contains TM.** TM needs to be a separate poster text element;
it must not be described as part of the retrieved source SVG.

The supplied photograph has perspective and glass reflections. The retrieved stacked vector is
consistent with its visible structural arrangement. This review does not establish exact original
printing-master geometry from the photograph, and no source coordinates were changed to fit it.

The footer visible in the closeup reads:

> ARTIST: ROBERT DAVIDSON   © THE EXPO 86 CORPORATION   PRINTED IN CANADA

## Provenance limitation

The gallery inventory explicitly describes both SVGs as third-party reconstructions/renditions,
not original historical production masters.

- Stacked SVG: credited to Mwtoews (English Wikipedia), from merchandise photographs.
  Upstream page: https://commons.wikimedia.org/wiki/File:Expo86logo.svg
  Upstream SVG: https://upload.wikimedia.org/wikipedia/commons/5/5e/Expo86logo.svg
- Symbol-only SVG: creator unidentified; associated with a file first uploaded to German Wikipedia in 2008.
  Upstream page: https://commons.wikimedia.org/wiki/File:Expo86logo_2.svg
  Upstream SVG: https://upload.wikimedia.org/wikipedia/commons/b/b2/Expo86logo_2.svg

These are the exact existing vectors supplied by the user-selected gallery, not newly redrawn logos.
The repository also includes a primary 1982 trademark drawing and a 1986 leaflet wordmark,
but those two assets are raster images.

## Integrity checks

Both local files were verified against their repository Git blob IDs and the SHA-256 values in
the gallery inventory. Original encoding and line endings were retained.

| Local file | Bytes | SHA-256 |
| --- | ---: | --- |
| expo86-logo-source.svg | 2500 | 3f51b5e0355222bd5399fc5e35ece3c4204c8527681d20f0385a8825bec5a1c7 |
| expo86-wordmark-source.svg | 2222 | 314fa73bbc3f835e52740f4aa675b93d663e2a32c869c04bbb5370eec4c62e97 |

Full machine-readable source metadata is in `expo86-logo-provenance.json`.
The gallery's unmodified Expo 86 inventory record is preserved in `expo86-gallery-record.json`.

