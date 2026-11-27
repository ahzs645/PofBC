# So many of our visitors return in Spring.

Updated 26 November 2026 for PofBC's Super, Natural BC campaign reconstruction.

## What changed

The lettering is composed from native TeX Gyre Termes outlines, using measured
per-letter boxes for the headline. The original's cap height, shorter lowercase,
tight spacing and line breaks are fitted separately. The composition is levelled;
scan tilt is not built into the recreated typography. The small print uses a dark
ink colour and the correct per-ad arrangement.

Two supplied modern whale scenes remain selectable. The 1462 x 1021 reference clips both headline endpoints and part of the right header. The headline is reconstructed fully within a 10 px safe inset; that crop does not establish the original full-page aspect ratio. The tiny unreadable department code remains a source facsimile.

This is **mixed artwork: vector typography over raster photography**. It is a
modern reconstruction, not a recovered production master or original photograph.
The exact historic typeface remains unconfirmed.

## Date and credits

1984 publication, supported by the creator interview; 1985 ADCC award.

Client: Tourism B.C. Agency: McKim Advertising (Vancouver). Writing and creative
direction: Alvin Wasserman. Design and art direction: Bill Cozens. The campaign
record collectively lists Peter Thomas, Ed Gifford and Bob Herger. The individual
Spring ad record credits Peter Thomas. No individual photographer is assigned to
the ferry or lake photograph without further evidence. These historical credits
do not apply to the supplied modern recreation photos.

## Files

- `spring-visitors.svg`: self-contained master with native outlined lettering.
- `spring-visitors-editable-text.svg`: individually positioned editable text. Install the
  bundled TeX Gyre Termes Regular and Italic fonts for the same rendering.
- `spring-visitors.pdf`: page-sized vector lettering with embedded raster photography.
- `spring-visitors-alternate.svg`, `spring-visitors-alternate-editable-text.svg` and
  `spring-visitors-alternate.pdf`: the same layouts using the alternate whale scene.
- `source/design.json`: complete copy, geometry, photo placement and uncertainties.
- `photos/`: unmodified supplied scene bytes.
- `reference/`: historical scans retained as reference evidence.
- `review/comparison.jpg`: whole composition comparison.
- `review/headline-overlay.png`: green native lettering over the straightened
  historical headline crop. Remaining white edges show contour/placement differences.
- `review/validation.json`: current export checks and limitations.

Working canvas: **1462 x 1021** units; export size **14.62 x 10.21 inches**.
These are working dimensions; the original printed size is not established.

## Rebuild

The shared builder and font tables are in the Spring folder. Retain the three
sibling artwork folders together, then run from the package/repository root:

```bash
python3 artwork/posters/super-natural-spring/source/build.py --exports
```

Without `--exports`, SVG construction uses only Python's standard library. PDF,
PNG and thumbnail rendering requires Inkscape and Pillow. `--only spring`,
`--only ferries`, or `--only lake` builds one advertisement. The gallery copy is
written under `src/posters/` and the standalone exports stay in `artwork/posters/`.

The included OTF fonts were obtained from the official CTAN TeX Gyre distribution.
Their licence is `../super-natural-spring/source/GUST-FONT-LICENSE.txt`. All glyph
bounding boxes in the committed tables match those OTF files. Editable and outlined
versions rendered to identical pixels at the working canvas dimensions with these
fonts installed. This verifies the editing files; it does not identify the historical font.

## Review

The poster catalogue's **34 checks pass**, including drawings, references, layer
selectors, panel bounds, stories, reciprocal links and export page proportions.
Each PDF has one page and retains vector drawing objects for the letters. The
outlined SVGs contain no font-dependent text nodes; all photographs are embedded.

Source tilt, crop, scanning noise, unknown original type cut, and different modern
scene detail remain visible limitations. Old 620 x 418 Spring metrics are superseded;
no previous IoU/Dice score is claimed for this revision. The legacy Spring
`source/design-initial.json` is retained only as an earlier composition record.

## Sources

- https://theadcc.ca/archive/so-many-of-our-visitors-our-good-ferries-take-away-our-great-hotels_1985_gold_consumer-magazine
- https://theadcc.ca/archive/so-many-of-our-visitors_1985_gold_consumer-magazine-ad
- https://bcbusiness.ca/lifestyle/tourism/the-bcbusiness-2018-tourism-status-report-branding/
- https://ctan.org/pkg/tex-gyre-termes?lang=en
