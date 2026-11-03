# Wildlife Trees — source package

The reconstruction package behind **Wildlife Trees** in the Posters view
(`?view=posters&poster=wildlife-trees`): a Ministry of Forests, Forest Practices Branch poster of a
single wildlife tree and six animals, about 2001 from the artist's mark “d.g.01”. The package's own
README, as supplied, is [`PACKAGE-README.md`](PACKAGE-README.md); `source/` holds its measurements,
copy, registration, animal records, validation records and build scripts, unchanged.

## What is kept, and what is not

The supplied package is 215 MB. Kept here (400 KB):

| Kept | What it is |
|---|---|
| `PACKAGE-README.md` | The package's README, unchanged |
| `source/*.json`, `source/*.md` | Registration, panel layout, checked copy, tree regions, animal records, provenance, validation |
| `source/*.py`, `source/requirements.txt` | The package's rebuild and proof scripts |
| `web_copy.py` | Makes the site's copy from the outlined master (below) |
| `render_preview.mjs`, `preview.py` | Make the preview the viewer opens on (below) |

Left out, like the other posters' packages: the reference scan and its proofs (`reference/`,
`proof/`, the overlay PDF and review page, the preview PNG), and the 45 MB masters, poster PDF and
separate animal and tree assets, which are build outputs. `source/pofbc/` is left out too: it is a
snapshot of this repository's own files (`src/assets/crestMark.js` and the Forest Oval artwork and
Kabel face under `vendor/forestoval/`) at revision `6d635f76`. `source/package-manifest.json` keeps
every left-out file's size and SHA-256; the outlined master the site copy is made from is
`Wildlife-Trees-outlined.svg`, 45,444,719 bytes, SHA-256
`107a69eb41fa24671e3bc7dcbb2a30ce23cb7e8ff38b91ba6840627121a7cb7d`.

## The site's copy

`src/posters/wildlife-trees/wildlife-trees.svg` is a **lighter copy** of the outlined master:

| | Master | Site copy |
|---|---|---|
| Size | 45.4 MB | 14.8 MB (about 4.5 MB served compressed) |
| Path elements | 104,787 | 1,960 |
| Coordinates | absolute, three decimals | relative, on a grid of a tenth of a poster unit (a hundredth for the two identity marks) |
| Editor notes | an id on every path, titles, descriptions and JSON metadata in every group | none, except the poster's own title and the lettering's aria-labels |

Every group that names a part of the drawing keeps its id and transform, and every colour, clip and
glyph is kept. The large saving in elements comes from joining runs of sibling paths that paint the
same way into one path. Under the non-zero fill rule, that paints the union of what the separate
paths painted as long as each part winds the same way. So each joined path is first turned to
match, and a path that crosses itself (36,103 of them, whose loops wind both ways) is joined only
with others whose bounds it cannot touch.

Rendered in Chromium against the master, the copy's ink overlaps the master's by 97–99.9% across
the hawk, the trunk, the crown, the toad and the logos at 7–20 pixels per poster unit. Pixels that
differ by more than a quarter of the tonal range are under 0.25% in every crop; what differs is
anti-aliasing along edges. At twenty pixels to the unit the two cannot be told apart by eye.

To make it again, with lxml and numpy:

```sh
python3 web_copy.py Wildlife-Trees-outlined.svg ../../../src/posters/wildlife-trees/wildlife-trees.svg
```

The card image, `src/posters/wildlife-trees/thumbnail.jpg`, is the package's preview PNG at 160
pixels wide, so the shelf does not fetch the drawing to show a card. The viewer fetches the drawing
as a file, not inside a script, and does not fetch it ahead when a neighbouring poster is open.

## The preview it opens on

Opened, the poster does not wait for 4.5 MB: it shows `src/posters/wildlife-trees/preview.png` at once,
on a stand-in drawing of the same size, and swaps in the vector drawing when it arrives, keeping
whatever view is on screen. Zoom, hotspots, panels and the story all work on the preview; only the
spotlight (which lights the drawing's own layers) and export wait for the drawing, and a small notice
says it is a preview until then (with a Retry if the download fails).

The preview is 1000 × 2997 pixels and 198 KB. The poster is one ink on white, so it stores only how
much ink each pixel holds, in four tones (paper, two tints, full ink), as a 2-bit PNG; a JPEG of the
same picture is over 400 KB, because fine hatching is the hardest thing for JPEG to compress. At the
size the whole poster first appears it cannot be told from the drawing; zoomed in before the drawing
arrives, it is soft. It is made from a render of the site's copy, so the two are in register:

```sh
node render_preview.mjs ../../../src/posters/wildlife-trees/wildlife-trees.svg /tmp/wildlife-trees-2000.png
python3 preview.py /tmp/wildlife-trees-2000.png ../../../src/posters/wildlife-trees/preview.png
```

## How smoothly it zooms

Add `&frames=1` to the address and every zoom reports, in the corner, how many frames it drew and
how long they took (`src/posters/stage/frameMeter.js`). In headless Chromium, which draws without a
graphics card, Wildlife Trees' zooms that keep much of the tree on screen ran at 9–33 frames a second
at desktop size against REWARD's 29–40, and zooms onto a single animal near REWARD's. That machine
is not a phone, so the number that matters is the one a real device shows.

## What the poster's panels rely on

- **Part boxes** are measured, not guessed: the animals' from their frames and captions, the tree's
  from the region masks in `source/tree-upper-regions.json` and `source/tree-lower-regions.json`
  (the tree is drawn in clipped tiles whose paths overrun them, so the groups' own bounds are too
  large).
- **Repairs** named in the animal panels are those recorded in `source/animal-source-notes/`.
- **The date** is the artist's mark, in the grass at the foot of the tree, recorded by the package as
  “approximately d.g.01” (`original-illustrator-mark` in `source/tree-lower-regions.json`). It is not a
  printed date.

The two identity marks are this site's own vectors placed where the printed ones are, not tracings
of the scan: the arms and wordmark from the Arms identity, and the Forest Service tree oval from
Forest Oval. The support lines and all the copy are a substitute face (Nimbus Sans), fitted to the
measured lines of the print. None of this is an original production master, and none of it implies
affiliation with, or rights in, the historical design.
