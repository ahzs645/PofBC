# Political parties

B.C.'s provincial parties, their logos and their organizational history, for the Parties view
(`?view=parties`).

- [`bc-political-party-logos-2026-11-22/`](bc-political-party-logos-2026-11-22/README.md): the
  22 November 2026 recovery package. It has 65 source-artwork records across 12 identities, 27
  party and label coverage records, 85 events and 86 sources. The package's `data/`,
  `research-notes/`, PDF catalogue, contact sheet and `SHA256SUMS.txt` are kept here as supplied.
  - Its `assets/` folder is at [`public/parties/assets/`](../../public/parties/assets), with the same
    layout, so `SHA256SUMS.txt` still checks those files by their `assets/…` paths.
  - Its `previews/catalogue/` folder is at [`public/parties/previews/`](../../public/parties/previews).
  - Its offline `index.html` gallery was not filed, because the view replaces it.

`scripts/build-parties.mjs` compiles `data/catalogue.json` into `src/parties/partyData.js` and
copies it to `public/parties/catalogue.json` for download. To add a party, a design or an event,
extend the catalogue records with sources and rebuild. Keep three kinds of date apart: dated use,
file observations and political events. Leave a gap as a gap.
