# The Province's identities, as brandkit brands

Every visual identity the Province of British Columbia has had, oldest first, each written as a
[brandkit](https://github.com/ahzs645/brandkit) brand and packed as a brand pack: one zip per era
that brandkit opens by drag and drop, by link (`?url=`) or from a catalog. The brands are made
here, from PofBC's own reconstructions, so they cannot drift from what the generator draws.

```sh
npm run brandkit:build                     # write every era's brand folder
npm run brandkit:pack                      # build, then pack every era
npm run brandkit:pack -- bc-province-flag  # one era (or several), by id
npm run brandkit:release                   # build, pack, and zip the packs for a release
```

**Releases.** `npm run brandkit:release` writes one zip,
`brandkit/out/release/pofbc-brandkit-<date>-<commit>.zip` (`-- --name 2026.11` names it), holding
every era's pack, its menu logo, `catalog.json` and a README listing the eras. The same commit
gives the same zip byte for byte. To publish it, run the **Release brandkit packs** workflow
(Actions → Run workflow, or `gh workflow run brandkit-release.yml`): it builds the zip on a clean
checkout, tests it, and attaches it to a GitHub Release tagged `brandkit-<version>`, replacing the
zip if that release already exists.

`brandkit:pack` writes to `brandkit/out/packs/`:

| File | What it is |
| --- | --- |
| `<id>.zip` | The era's pack. Drop it on brandkit, choose it with **⋯ → Open a brand…**, or link to it with `?url=`. |
| `<id>.logo.svg` | Its logo for brandkit's brand menu. |
| `catalog.json` | All five packs, for `?catalog=<address>` or a site built with `VITE_BRANDKIT_CATALOGS`. Pass `--base-url https://host/path/` to write absolute addresses. |
| `bc-province.bundle.zip` | Every pack in one file: dropped or linked, it adds all five eras at once. |

The brand folders themselves are in `brandkit/out/brands/<id>/` (or `BRANDKIT_OUT`); `brandkit
build <folder>/brand.json` turns one into a complete kit of files. Packing is brandkit's own
(`vendor/brandkit/src/pack`), so the packs are exactly what brandkit reads, and come out byte for
byte the same from the same sources.

## The eras

| Id | Era | Years | Made from |
| --- | --- | --- | --- |
| `bc-province-engraved-arms` | Engraved arms | before 1977 | The Grace M. McCarthy calling-card reconstruction: the supplied arms engraving and three PlateForge Card Script study fonts (`artwork/stationery/grace-mccarthy/`) |
| `bc-province-1977` | Visual Identity Program (crest and ring) | 1977 – about 1983 | The four 1977 manuals as rebuilt in brandkit's BC manual pack, and PofBC's Provincial Symbol and ministry history |
| `bc-province-flag` | The flag logo | about 1983 – 2005 | PofBC's flag drawing and its layout from seventeen printed references (`src/flag/`) |
| `bc-province-arms` | Coat of arms and BRITISH COLUMBIA wordmark | after the flag (unconfirmed) | PofBC's arms and wordmark and their layout from twelve documents (`src/crest/`) |
| `bc-province-current` | The BC mark | 2011 – present | The mark lifted from the Province's published ministry-marks PDF, every published ministry mark drawn by PofBC, and its line rules (`src/current/`) |

The order, ids and labels are in [`eras.mjs`](eras.mjs). Each brand records its place in the
sequence (`brand.era`) and a one-line `description` the catalog shows.

**Engraved arms** is new, and starts with one piece: Grace M. McCarthy's calling card (Deputy
Premier, Provincial Secretary, Minister of Recreation & Travel Industry), rebuilt from a
photograph as an editable template whose seven lines are fields, with the photograph as the
studio's reference overlay and the reconstruction's offline editor, report and evidence carried in
the pack. Its typeface, ink colours, printed size and date are not established, and the supplied
arms are a different engraving from the card's; the brand says so wherever the card is shown. Add
the era's next pieces (a letterhead, an envelope, another card) as templates in
[`scripts/eras/engraved-arms.mjs`](scripts/eras/engraved-arms.mjs).

Like every other era's source artwork, the card's reconstruction package lives in PofBC's
`artwork/` ([`artwork/stationery/grace-mccarthy/`](../artwork/stationery/grace-mccarthy)): the
editable and outlined SVGs, fonts, offline editor, report and evidence, as supplied (less its
`model.json`, which repeats the font files at 5 MB). The script reads the arms path, its
placement and every line's text, position, size and cut from the editable SVG, so a revised
package rebuilds the brand with no numbers to copy.

**1977** is the generator brandkit used to ship (`scripts/brands/bc-province-1977*.mjs` and its
helpers, before brands moved out of brandkit), moved here with its paths retargeted. It now reads
the Provincial Symbol and the ministries straight from `src/` instead of a copied `artwork.json`,
and writes the same definition brandkit had (checked key by key), plus its place in the era
sequence.

**Flag** and **arms and wordmark** run PofBC's own layout functions and write the result down as
brandkit signatures, set for every ministry of their years. **The BC mark** carries every
published ministry mark exactly (English and French, four colourways each, in
`artwork/ministry-marks/`) and an editable mark for unlisted names, set in EB Garamond because the
Province's Garamond is licensed.

## Layout

```
brandkit/
  eras.mjs                 the eras, oldest first
  sources/<id>/            what an era starts from: artwork, fonts, references, its README (committed)
  shared/fonts/            TeX Gyre Heros and Cursor (GUST licence), copied into every era
  scripts/
    build.mjs              sources → brandkit/out/brands/<id>/, validated by brandkit
    pack.mjs               brand folders → packs, catalog and bundle
    eras/<era>.mjs         one generator per era: writes its brand.json
    lib/                   shared helpers; the 1977 brand's applications, illustrations, motion
                           and pattern studies
```

For each era, `build.mjs` empties its folder, copies in `sources/<id>/` and `shared/`, runs the
era's script, then checks the result the way brandkit will: `validateBrand`, every font loads,
every listed file exists. It writes `USE.md` and `logo-menu.svg` from the brand.json.
`scripts/brandkit-eras.test.mjs` builds and packs every era into a temporary folder and reads the
packs back.

Needs `vendor/brandkit` checked out (`git submodule update --init vendor/brandkit`). No licensed
font is used: Helvetica is TeX Gyre Heros throughout, as the 1977 brand always did.

## Fonts and rights

- TeX Gyre Heros and Cursor: GUST Font License (`shared/fonts/`).
- PlateForge Card Script studies: SIL Open Font License, derived from Pinyon Script, each with its
  provenance (`artwork/stationery/grace-mccarthy/fonts/`).
- EB Garamond: SIL Open Font License, from Fontsource (`sources/bc-province-current/fonts/`).

Every brand is labelled as a reconstruction or reference kit, not the Province's current identity
or a source of approved marks. The photograph and supplied arms engraving are user-provided
evidence; font licences do not cover them.
