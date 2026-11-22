# Thompson Health Region, vector reconstruction, 22 November 2026

A supplied vector reconstruction of the Thompson Health Region's logo. The original production
vector has not been found. Read by `scripts/build-collected-marks.mjs`: the reconstructions from
`proposed-assets.json` (VECTOR_SEARCHES), the dated images from `source-register.json` (HISTORIES).

## In the gallery

The black reconstruction leads the region's card, in place of the 1999 letterhead image, which
becomes one of its versions. The other versions:

- **Colour symbol, black lettering (composite):** with a vector PDF and EPS. The 2003 colour image
  shows the symbol alone, so the colours of the name and tagline are not known; they are black here
  by assumption.
- **Symbol alone, colour:** with a vector PDF, plus the symbol in black as an SVG download.
- **Images:** the letterheads of 9 September 1999 (already held), 9 June 2000 and 1 November 2001,
  from the City of Merritt's council agendas, and the 2003 colour image of the symbol (59 × 56 px),
  from Environment Canada's *Proceedings of the Risk Assessment Workshop*, PDF page 71.

## How it was made

The symbol is redrawn as smooth curves over the three letterheads, whose scans hold about 112 px of
real detail. The damaged upper-left edge of the 1999 copy is restored from the later two. The teal
#00687A and ochre #C47900 are sampled from the 2003 image; they are not print specifications.

The name is outlined EB Garamond (weight 500, SIL Open Font License, `font-notices/`). The tagline is
outlined Nimbus Roman Italic (URW base 35, AGPL-3 with the font exception,
https://github.com/ArtifexSoftware/urw-base35-fonts). Both are substitutes fitted to the letterheads'
ink; the original typefaces are not identified, and these set slightly heavier than the letters'
thin print. No font file is included.

## In this folder

- `package-README.md`, `reconstruction-manifest.json`: the supplier's own notes and checksums.
- `construction/`: geometry and typography analysis, and the overlays.
- `references/`:
  - the 1999 header crop;
  - the four-page extract of the 2003 publication;
  - source manifests and colour research.

  The complete Merritt agendas are not copied; their URLs are in the register.
- `review/`: the reconstruction review PDF and a preview.
