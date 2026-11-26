# So many of our visitors return in Spring.

Reconstruction of the 1984 Super, Natural British Columbia magazine advertisement,
prepared on 25 November 2026 for PofBC's Posters collection.

## What this is

This is a modern reconstruction composed from the two clean scene images supplied
with the request, a 620 × 418 pixel reference, and reusable serif outlines. It is
mixed artwork: native vector lettering and a raster photograph. The small unreadable
mailing response code after “Dept.” is retained as an 18 × 8 pixel facsimile from the
reference. It has not been replaced with guessed characters.

The default scene is `photos/vintage-orcas.png`, supplied as “Vintage Orcas in British
Columbia Waters.png” (1635 × 962). It fits the original photo window at x = 0, y = 53,
width = 620, height = 365. The alternative, supplied as
“Gemini_Generated_Image_6ia0526ia0526ia0.jpeg” (2516 × 1696), has extra sky above the
same crop. Both scene files are preserved byte for byte. They contain reconstructed
detail and are not presented as Peter Thomas's recovered original photograph.

## Historical identification

The ADCC's own award record identifies the client as **Tourism B.C.**, the agency as
**McKim Advertising**, **Alvin Wasserman** as writer and creative director,
**Bill Cozens** as designer and art director, and **Peter Thomas** as photographer.
It records a **1985 Gold award for Consumer Magazine Ad**. BCBusiness's interview with
Wasserman dates the ad's appearance to **1984**. The award year and appearance year
are deliberately separate in the catalogue.

Sources:

- [ADCC: So Many Of Our Visitors](https://theadcc.ca/archive/so-many-of-our-visitors_1985_gold_consumer-magazine-ad)
- [ADCC: the three-ad campaign](https://theadcc.ca/archive/so-many-of-our-visitors-our-good-ferries-take-away-our-great-hotels_1985_gold_consumer-magazine)
- [BCBusiness, 2 August 2018](https://bcbusiness.ca/lifestyle/tourism/the-bcbusiness-2018-tourism-status-report-branding/)
- [Concordia University, 3 December 2021](https://www.concordia.ca/cunews/offices/advancement/2021/12/02/-concordia-very-formative--in-lives-of-ad-agency-founder-and-chi.html)
- [Larger ADCC reference image](https://theadcc.ca/wp-content/uploads/2022/10/adcc_38306_OBJ.jpg)

The supplied filename `1638469586611(1).png` corresponds to the reproduction on the
Concordia page. The larger ADCC reproduction was used to check the small copy: it
supports plural “mountains” and a comma after “mountain trekking”. The credit reads
“Hon. Claude Richmond, Minister, Tourism/Expo 86.”; its tiny punctuation is less
certain than its wording. The reply code remains unresolved.

## Typography: the historical font is still unconfirmed

The headline, body and wordmark use **TeX Gyre Termes Regular** native glyph outlines,
already held in PofBC's `src/hydro/serif.js`. The small ministerial credit uses
**TeX Gyre Termes Italic**, from the open GUST distribution. The headline is fitted
letter by letter for width, height, baseline and spacing; the short t and the
descenders are intentionally fitted individually. This is a typeset reconstruction
with optical fitting, not an automatic trace of the scanned headline.

The font comparison included EB Garamond, Nimbus Roman, Liberation Serif, Noto Serif
Display, and official raster specimens of ITC Garamond Light and Light Condensed.
The ITC candidates differ in the y ending, the g connection, the f/capital height
relationship and the relative widths of letters. A fitted Times-family design is
the strongest practical match from the available evidence. No source has been
found that establishes the original phototypesetting cut. Do not relabel this
reconstruction “the original font” or “verified source vector”.

Comparison references:

- [ITC Garamond Std Condensed Light](https://www.myfonts.com/products/std-light-condensed-garamond-370364)
- [ITC Garamond Std Light](https://www.myfonts.com/products/std-light-garamond-370326)
- [Klingspor Museum: Garamond specimens, page 4](https://www.klingspor-museum.de/KlingsporKuenstler/Schriftdesigner/Garamond/CGaramond.pdf)
- [TeX Gyre Termes distribution](https://ctan.org/pkg/tex-gyre)

The regular table is reused under the GUST Font License, retained in
`source/GUST-FONT-LICENSE.txt`. The italic table contains only the characters used
in the credit. No proprietary font files or extracted proprietary font programs
are included.

## Files and rebuilding

| File | Purpose |
| --- | --- |
| `spring-visitors.svg` | Self-contained outlined master, default supplied scene |
| `spring-visitors-alternate.svg` | Self-contained outlined master, alternate supplied scene |
| `spring-visitors-editable-text.svg` | Text-editable version; install TeX Gyre Termes for consistent type |
| `source/design.json` | Copy, typography positions and measured layout |
| `source/design-initial.json` | Initial headline placement before two refinement passes |
| `source/type-glyphs.json` | Reusable regular serif contours, advances and kerning |
| `source/type-glyphs-italic.json` | Credit's italic glyph contours |
| `source/build.py` | Dependency-free Python composition script |
| `photos/` | Original supplied scenes and the unresolved code fragment |
| `review/comparison.jpg` | Original and reconstruction at the same scale |
| `review/headline-overlay.png` | Reference/outline overlap with a colour key |
| `review/headline-metrics.json` | Reproducible definition of the measured headline mask |

Run from any directory:

```bash
python3 artwork/posters/super-natural-spring/source/build.py --proof
```

For a standalone copy of this package, run `python3 source/build.py --proof`.
The script writes the two outlined SVGs, the text-editable SVG and a combined gallery
master. It uses only Python's standard library and the committed glyph tables.
All outlined outputs render without fonts installed. The editable-text version is
an editing convenience: a fallback font can change its contours.

The gallery master is `src/posters/super-natural-spring/spring-visitors.svg`. It
contains both photographs as separately named layers; the existing viewer chooses
one, and keeps Original and Overlay comparisons available. Gallery images are lazy
loaded. The route is `?view=posters&poster=super-natural-spring`.

The chosen print export is **12.4 × 8.36 inches**, preserving the supplied reference
ratio. This is not a measurement of the historical magazine placement. A 2480 × 1672
PNG samples the composition at 200 ppi at this size; the default photograph itself
contains 1635 × 962 source pixels, so export size does not create more photographic
detail. PDF text is outlined vector geometry.

## Review and limitations

The composition preserves the 53-pixel header, two copy columns, right-hand wordmark,
and bottom headline. Photo alignment was checked at the main mountain and dorsal
fins. The supplied clean image differs in fine detail, colour and shoreline position;
global image shifting would worsen the main landmarks, so its natural crop is kept.

Two local fitting passes improved the headline alignment. The final binary mask
comparison gives approximately **0.731 IoU / 0.845 Dice** against the supplied scan,
using the threshold and region recorded in the metrics file. This is a
threshold-dependent alignment diagnostic, not an authenticity percentage or proof
of font identification. Remaining contour differences are visible in the overlay.

The existing poster catalogue checks cover the entry, series, layer IDs, hotspots,
links, stories and export dimensions. The SVG and PDF renderings are inspected
separately. Browser access to this workspace's development server was unavailable;
the live viewer interaction was not verified during this build.
