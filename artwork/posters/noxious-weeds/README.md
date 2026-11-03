# Noxious Weeds — from the supplied PDFs

The Ministry of Forests, Forest Practices Branch's campaign against invasive plants, as three supplied
PDFs, rebuilt for the **Posters** view (`?view=posters`, series *Noxious Weeds*):

| Supplied | Piece | Made (from the file) | Size | SHA-256 |
|---|---|---|---|---|
| `P071.pdf` | **Beware These Alien Invaders**, a five-screen leaflet with links, for the screen | 25 March 1999 | 152,208 bytes | `eb8747ee3bff4f0e98f62487496949deb6d9027a0900cb751c4604ccfbbaf77f` |
| `P072.pdf` | **Shattering the Environment**, a 36 × 27 in poster | 31 March 2000 | 3,006,669 bytes | `64d67d167729389c3077fef01bca41ce297805addf13c7c4127f9e88f6d38f97` |
| `P073.pdf` | **Explosion in Slow Motion**, a 22 × 36 in poster | 31 March 2000 | 1,619,023 bytes | `3f47c3aec5a300e2fdd7075ac01b8fafce6bdcc7336bff63efcc80bc0bb7bf14` |

The dates are the PDFs' own (when Acrobat Distiller made them), not printed dates. The posters credit
copy to Susan Turner and Dwaine Brooke, art direction to Paul Nystedt and Denton Pendergast, design to
Rocket Science Design (*Shattering*) and Denton Pendergast (*Explosion*), weed photography to Dion
Manastyrski, illustration to Soren Henrich, compositing to Watermark Lithography, and the
background photograph of *Shattering* to Gunter Marx Photography.

The PDFs themselves are not kept here: everything in them that the site shows is in
`src/posters/noxious-weeds/`, their pictures byte for byte. Rebuilding needs them, checked against
the hashes above.

## How they are rebuilt

`build.py` makes each piece's drawing (`src/posters/noxious-weeds/<piece>.svg`), its pictures
(`images/`), its measured parts (`<piece>.parts.js`) and its shelf card (`<piece>.thumb.jpg`):

```sh
python3 build.py P071.pdf P072.pdf P073.pdf
```

It needs poppler-utils, lxml and Pillow, and fetches the substitute faces into `fonts/` (not kept in
git) on its first run.

- **Pictures.** Every photograph and illustration is a JPEG (one a PNG) placed in the PDF. Poppler
  passes the JPEG streams through unchanged, and the build writes each to a file the drawing names,
  so the 4.5 MB of pictures are exactly the PDFs' and are fetched by the browser only when a piece is
  opened. Nothing is recompressed. The two posters' grounds are single composites (2106 × 1592 and
  1062 × 2233 pixels), so a weed that is part of one cannot be separated from it.
- **Lettering.** The PDFs name Univers and Eurostile but do not embed them, so every viewer of these
  files has always set the copy in whatever it had. The build sets it in chosen free faces at the
  positions the PDF gives each letter, and outlines it: Univers in TeX Gyre Heros, Univers Condensed
  in TeX Gyre Heros Cn, Eurostile Condensed in Saira Condensed, Eurostile Bold Extended in Michroma.
  The full TeX Gyre Heros is used, not the site's trimmed stand-in, which has no fi and fl ligatures:
  the copy asks for them, and without them “flowers” prints as “ owers”. The faces the leaflet embeds
  (its Mekanik weed headings, Trebuchet) are its own. Letter widths follow the original, so a few
  spaces, after a W in Eurostile's place for one, look a little open.
- **Parts.** Poppler writes a page as a flat list of paths, text runs and images. `svg_bounds.py`
  measures each one; the build gives each the part whose region (in `build.py`, in points) holds its
  centre, as `data-part`, and writes out where each part was found, which the viewer uses as the
  part's frame and hotspots.
- **Highlights.** A part that is a region of a composite photograph (the four weeds in *Shattering*,
  the title, nodding thistle, marsh plume thistle and gorse in *Explosion*) gets a copy of the
  photograph masked to a soft ellipse over it. The viewer shows the copy only while the spotlight is
  on that part, so the weed stays bright as the photograph around it settles back. It is the same
  image, so it costs nothing to download, and it is left out of exports.
- **The leaflet** is five screens of 684 × 468 points, laid out one under another with a gap, and its
  links (the cover's button, the arrows and HOME under each weed) are kept as drawn.

The rebuilt pieces are not original production files, and imply no affiliation with, or rights in,
the campaign or its photographs.
