# Posters — source packages

The reconstruction packages behind the **Posters** view (`?view=posters`), kept as supplied: each
folder's own README says how the drawing was made, what was interpreted, and how to rebuild it. The
reference photographs and raster exports were left out; the vector masters, rebuild scripts,
palettes and validation records are here.

| Folder | Poster | Used by the site as |
|---|---|---|
| `dont-drop-it/` | DON’T DROP IT! — B. C. Forest Service | `src/posters/forest-service/dont-drop-it.svg`, unchanged |
| `dont-gamble-with-fire/` | Don’t gamble with FIRE — B. C. Forest Service | `src/posters/forest-service/dont-gamble-with-fire.svg`, **recoloured** (below) |
| `reward-living-forest/` | REWARD — A Living Forest | `src/posters/forest-service/reward-living-forest.svg`, unchanged |
| `enjoy-protect-forests/` | Enjoy & Protect our Forests | `src/posters/forest-service/enjoy-protect-forests.svg` (the outlined master), unchanged |
| `be-careful/` | Be Careful: Prevent Forest Fires (1960 decal) | `src/posters/forest-service/be-careful.svg`, the master with **ids prefixed** (below) |
| `coons-age/` | A Coon’s Age (1971 newspaper advertisement) | `src/posters/forest-service/coons-age.svg` and `coons-age-raccoon.webp`, the outlined master with **its photograph moved out** (below) |
| `prevent-forest-fires/` | Prevent Forest Fires: Fire Destroys Timber and Payrolls, British Columbia Forest Service | `src/posters/forest-service/prevent-forest-fires.svg`, the master **minified, ids prefixed** (below) |
| `matches-not-for-children/` | MATCHES ARE NOT FOR CHILDREN!! British Columbia Forest Service, F. P. 19 | `src/posters/forest-service/matches-not-for-children.svg`, a **lighter copy**, ids prefixed (below) |
| `forest-service-emblem/` | The Forest Service evergreen emblem | `src/internal/forest-service-emblem.svg`, unchanged; also drawn into the two posters above |
| `go-bc-ferries/` | GO B.C. FERRIES — car decal | `src/posters/bc-ferries/go-bc-ferries.svg`, unchanged |
| `queen-of-sidney/` | Queen of Sidney — car decal | `src/posters/bc-ferries/queen-of-sidney.svg`, **layer ids renamed** (below) |
| `wildlife-trees/` | Wildlife Trees — Ministry of Forests, Forest Practices Branch | `src/posters/wildlife-trees/wildlife-trees.svg`, a **lighter copy** (below) |
| `noxious-weeds/` | Beware These Alien Invaders, Shattering the Environment, Explosion in Slow Motion — the Noxious Weeds campaign | `src/posters/noxious-weeds/`, **rebuilt from the PDFs** by `noxious-weeds/build.py` (below) |
| `expo-86-fiorucci/` | Expo 86, art poster by Vittorio Fiorucci | `src/posters/expo-86/expo-86-fiorucci.svg`, the master with **ids prefixed** (below) |
| `our-british-columbia/` | Our British Columbia, the British Columbia Pavilion's film poster for Expo 86 | `src/posters/expo-86/our-british-columbia.svg`, the master with **ids prefixed and two layers split** (below) |

**The gamble badge is green on the site.** The one supplied photograph shows it deep blue
(`#01375D`), and the master here was drawn to that photograph. The blue is the photograph's, not the
badge's — a colour cast from the camera, or sun fading — so the site sets every use of it (the field,
the pips, the dice outlines and the knockout stroke on “with”) in DON’T DROP IT!’s forest green
(`#003E2D`). The cream (`#F1D8AC`) is the badge’s own. The Posters view offers an “As photographed”
comparison that shows the blue, labelled as the photograph's colour and not a printing; the swap is
made on the stage (`src/posters/stage/useColourSwap.js`). To regenerate the green master, change
`BLUE` in `dont-gamble-with-fire/source/rebuild_badge.py` or replace the colour in the SVG.

**The Queen of Sidney decal's layers are renamed on the site.** The master names its ten layers with
a leading number (`02-flag-and-pole`), which a CSS selector cannot name, and the Posters view finds a
part's layer by selector. The site copy drops the numbers: `sticker-and-field`, `flag-and-pole`,
`sky-forest-and-birds`, `helm`, `dogwood-flowers`, `helm-above-bow`, `sea` and `ribbon` (`ferry` and
`lettering` already had none). Nothing else changes. The two decals' packages also came with reference
pictures, raster proofs, a PDF and an offline comparison page, which are left out like the others'.

**Wildlife Trees is shown from a lighter copy.** Its outlined master is 45 MB and 104,787 paths, far
more than a browser should be asked to build for one poster. `wildlife-trees/web_copy.py` rounds it
to a tenth of a unit, writes its paths as relative moves, drops the editor's ids and notes, and joins
like paths, for a 14.8 MB copy of 1,960 paths (about 4.5 MB served compressed) that renders the same
ink: [`wildlife-trees/README.md`](wildlife-trees/README.md) has the method and the comparison. The
masters, the separate animal and tree assets and the 120 MB of scans and proofs are left out; the
package's measurements, copy, animal records and scripts are kept.

**The Noxious Weeds pieces are rebuilt from their PDFs.** They are photographs placed in PDFs with
their copy in fonts the files do not carry; `noxious-weeds/build.py` keeps every picture byte for byte
as a file of its own, sets the copy in chosen free substitutes and outlines it, tags each element with
its part, and gives the weeds inside the composite photographs a highlight for the spotlight:
[`noxious-weeds/README.md`](noxious-weeds/README.md). The PDFs are not kept; their hashes are.

**The 1960 decal and the 1971 advertisement are lightly adapted.** The Be Careful decal's site copy
prefixes every id with `bcc-` and re-words its `<title>`; nothing else changes. The raccoon
advertisement's site copy names its photograph by file (`coons-age-raccoon.webp`, WebP quality 82 at
the supplied 1040 × 1513, about 450 KB in place of the 5.5 MB inline PNG), writes its nested emblem
`<svg>` without the `ns0:` prefixes an HTML parser will not draw, prefixes its ids with `coon-` (the
emblem layer keeps `forest-service-emblem`, as on REWARD and the sign), and replaces the em dash in
its title. Rendered in Chromium, it matches the supplied master exactly outside the photograph. In
`coons-age/` the two SVG masters also link `assets/raccoon-supplied.png` (kept, byte for byte)
instead of embedding it; `build_ad.py` embeds it again. Their scans, comparison images, raster and
PDF exports, review pages and the copy of this repo's emblem are left out; see each README's last
section.

**Prevent Forest Fires is minified without changing a number.** Its site copy prefixes every id with
`pff-`, rewords its `<title>` and `<desc>`, keeps the Inkscape layer labels as `data-label`, and drops
whitespace between tags and inside path data and fills a parent already sets: 1.56 MB in place of
1.67 MB, with no pixel changed in a Chromium render at three times its size. It is fetched only when
opened, and the shelf shows a JPEG of it. The supplied photograph, the PNG renders and boards, the
masks, the superseded revision-5 drawing, the review page and the per-pass history are left out; see
[`prevent-forest-fires/README.md`](prevent-forest-fires/README.md).

**MATCHES ARE NOT FOR CHILDREN!! is shown from a lighter copy.** Its master is 11.3 MB, nearly all
of it the paint: 780,000 outline points in absolute two-decimal coordinates. `web_copy.py` simplifies
those outlines within a fifth of a unit, rounds them to a tenth and writes them as relative moves,
and prefixes every id `mnc-`; nothing outside the paint changes. The copy is 4.2 MB (0.9 MB
compressed), fetched only when opened, and differs from the master in 0.03% of pixels at 2000 × 2800.
Its seal is also an Internal Logo. The photograph, PNGs, PDF, review page, history and the separate
11 MB paint files are left out; see [`matches-not-for-children/README.md`](matches-not-for-children/README.md).

**Coastal Forest** comes from its own repository,
[ahzs645/coastal-forest-poster](https://github.com/ahzs645/coastal-forest-poster), whose
`build/build_assets.py` splits the reconstruction package into the drawing and its photograph. The
site carries those two files (`src/posters/coastal-forest/poster.svg` and `forest.jpg`) and the
panel images beside them; rebuild them there and copy them across.

None of these is an original production master, and none implies affiliation with, or rights in,
the historical designs.

**The two Expo 86 additions are lightly adapted, and unlisted like the Davidson poster.** Both
masters reuse the Davidson poster's Expo mark and event text, ids and all, so each site copy
prefixes its ids (`fio-`, `obc-`), drops the Inkscape markup and JSON metadata, and rewords its
title and description. The Fiorucci copy is otherwise unchanged, pixel for pixel. Our British
Columbia's master writes its three emblems with `ns0:` prefixes, which an HTML parser will not draw,
so its copy writes them in the drawing's own namespace; it also takes the white paper out of the
first layer and the fine print out of the billing layer, each into a layer of its own in the same
place, so the Posters view dims a layer as one group. Lighting the fine print inside the billing
layer dimmed every credit line separately, and with the sheet tilted, Chrome left most of the poster
undrawn. The three Expo 86 posters are off the shelf, open from their addresses, and step among
themselves. The photographs, PNGs, PDFs, comparison page, the fonts (Six Caps and Oswald, both open)
and the copies of this repo's own files are left out; see
[`expo-86-fiorucci/README.md`](expo-86-fiorucci/README.md) and
[`our-british-columbia/README.md`](our-british-columbia/README.md).
