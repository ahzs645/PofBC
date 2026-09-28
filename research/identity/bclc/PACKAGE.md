# BCLC logo history — vector reference package

Research checked 27 September 2026. This is an independent editorial reference, not an official BCLC brand manual or an exhaustive catalogue of every historic application.

## Start here

Open **bclc-logo-timeline.svg** for the editable reference sheet. Its dates, annotations, source labels and connecting lines are separate editable SVG objects. The logo lettering is vector artwork, not live typography.

**bclc-logo-timeline-outlined.svg** is the font-independent version: the timeline's annotation text has also been converted to paths. Use this version when consistent appearance matters more than editing text.

**bclc-logo-timeline.pdf** is the scalable print/share version. **previews/bclc-logo-timeline.png** is a raster preview only.

## The history in this edition

The legacy full-name sun-and-waves emblem is verified in a 2006/07 annual report and the early-2008 service plan. Its first introduction date is not yet verified.

The major change to the lowercase `bclc` identity was reported by Canadian Press on **13 August 2008**. This supports an **August 2008** transition, not an assertion that the exact launch day was August 13. The original launch used the tagline “playing it right.” Red/orange/green inset circles are visible in the following service plan and remain visible on the 2022 ESG report cover.

A purple/coral/yellow colour family is visible in the official **2025/26 Prince George Community Impact Report**. The timeline uses “By 2025/26” as a dated-use label, not a launch date. Its exact introduction date remains open. An old-palette example in 2022 is not, by itself, proof that refreshed artwork could not already have existed in another application.

The 2011 REBRAND award recognizes the earlier transformation; it is not a new logo launch. BCLC's operating history goes back to 1985, but that date has not been verified as the debut of the supplied legacy emblem.

## Individual vector assets

| File | What it contains |
| --- | --- |
| `logos/bclc-legacy-monochrome.svg` | Supplied full-name lockup, isolated, tightly cropped and displayed in one colour. |
| `logos/bclc-legacy-reversed.svg` | The same supplied geometry in white on transparency. View against a dark background. |
| `logos/bclc-legacy-symbol.svg` | Sun-and-waves emblem alone, isolated from existing paths. |
| `logos/bclc-2008-family-palette-reconstruction.svg` | **Reconstruction:** supplied lowercase contours recoloured using BCLC's older digital palette. Not an original 2008 master. |
| `logos/bclc-contemporary-supplied.svg` | Supplied contemporary logo contours and colours; rectangular masks normalized to equivalent clips for vector-only export. |

The two source SVGs from your ZIP are preserved unchanged in `source-artwork/`. The photographs in your ZIP were considered as references but are not embedded in the timeline. Nothing was raster-traced.

## Colour and geometry fidelity

The legacy SVG contained a lilac page background and an oversized page clip. Those were removed for the isolated assets; the existing logo paths were retained. The timeline uses monochrome to avoid mistaking that particular background treatment for a separately dated logo era. This package does **not** establish a historical full-colour legacy specification.

The intermediate specimen uses the supplied contemporary letter contours and the older official digital guide's values: grey `#414B56`, red `#9B1831`, orange `#E86A10`, green `#7DBC13`. These are not claimed to be original 2008 print standards. Historical letter contours have not been independently checked against an original 2008 vector master. A purported authentic tagline lockup has deliberately not been fabricated using an assumed font.

The contemporary specimen retains your SVG's values: lettering `#28222A`, purple `#9936D2`, coral `#FF8F68`, yellow `#F4C221`. The official 2025/26 PDF corroborates the colour family, not those exact RGB values or the supplied file's master-artwork provenance. The small differences between print/PDF colours and supplied RGB artwork should not be treated as a newly established redesign.

The normalized contemporary asset substitutes equivalent vector clipping rectangles for three solid rectangular SVG masks. This preserves the visible geometric bounds and avoids Inkscape rasterizing masked letters in PDF exports. Original masks remain in `source-artwork/contemporary-as-supplied.svg`.

## Editable data and reproducible build

`research/timeline.json` stores the three displayed states, their dates, uncertainty, asset names, palettes and construction provenance. `research/sources.json` stores the source URLs, page numbers, publishers and the exact claim each source supports. `research/README.md` explains the evidence and remaining gaps.

The build script uses the two supplied SVGs and these JSON files. It does not download anything.

```sh
python -m pip install lxml
python build_timeline.py
```

For the outlined SVG, PDF and PNG, install the Inkscape command-line application and run:

```sh
python build_timeline.py --export
```

Timeline annotations use **Inter** with Arial/sans-serif fallbacks. This is an editorial layout font, not a claim about BCLC's original logo typography. No font files are included. Open the outlined SVG for font-independent viewing.

## Attribution and use

BCLC's marks remain the property of their rights holder. This package provides historical analysis and technical vector preparation; it does not grant a trademark licence, imply affiliation, or authorize official-looking communications. Source references are clickable in the timeline SVG and PDF, and are also provided in the research files.
