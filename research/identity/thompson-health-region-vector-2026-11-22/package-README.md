# Thompson Health Region — vector reconstruction

Reconstruction prepared 22 November 2026 for the PofBC research project.

## What this is

This package combines the complete symbol/name/tagline arrangement from surviving 1999–2001 letterheads with the authentic two-colour symbol recovered from a government-hosted 2003 publication. It supplies newly drawn, editable vector artwork and the primary references used to make it.

**Status: reconstruction from historical raster sources. The original production vector has not been recovered.** The reconstructed colour symbol is well supported by the sources. The complete colour arrangement is a composite reconstruction: the source colour specimen contains the symbol alone, so it does not establish the historical colours of the name or tagline. Both are retained in black.

## Start here

- `thompson-health-region-colour.svg` — complete colour logo, with outlined lettering. Recommended editable master.
- `thompson-health-region-monochrome.svg` — complete black logo, with outlined lettering.
- `thompson-health-region-symbol-colour.svg` — two-colour symbol alone.
- `thompson-health-region-symbol-monochrome.svg` — black symbol alone.
- `Thompson_Health_Region_Vector.pdf` — complete colour logo as vector PDF.
- `Thompson_Health_Region_Symbol_Vector.pdf` — colour symbol as vector PDF.
- `Thompson_Health_Region_Vector.eps` — complete colour logo as EPS.
- `thompson-health-region-transparent.png` — large transparent raster export for applications that do not accept SVG.
- `thompson-health-region-preview.png` — white-background preview of the complete colour logo.
- `thompson-health-region-symbol-preview.png` — white-background preview of the colour symbol.
- `Thompson_Health_Region_Reconstruction_Review.pdf` — visual comparison, reconstruction decisions and source locations.
- `thompson-health-region-editable-text.svg` — supplementary live-text version; see the font notes below.

The SVGs use ordinary filled paths. The symbol has two paths, one ochre and one teal; the main outlined logo also contains individual letter outlines. There are no embedded bitmap images in the SVG masters, no external linked assets and no font dependency in the outlined versions. Groups are named `symbol`, `wordmark` and `tagline` for editing.

SVG artwork has a transparent background. The internal path and pointed details are transparent knockouts and appear white on white paper. The supplied white-background previews show that intended presentation. The symbol-only SVG uses a 1000 × 1000 viewBox; the combined logo uses a 1129 × 290 viewBox, including clear space around the reference arrangement.

## Source-supported colour

| Element | Sampled sRGB value |
| --- | --- |
| Arms and lower upright | Teal `#00687A` — RGB 0, 104, 122 |
| Upper upright | Ochre `#C47900` — RGB 196, 121, 0 |
| Name and tagline in this reconstruction | Black `#000000` |

The teal and ochre values are sampled from the flat-colour pixels of the historical raster. They are **not recovered Pantone, CMYK or official brand specifications**. The vector files and exports retain the RGB interpretation.

## How the symbol was reconstructed

The outline was rebuilt as a nominal square cross, with the stem and bar approximately one third of its width. Slight external corner rounding, five outward-leaning pointed white cutouts, a white separator at the colour junction and a distinct widening winding path follow the surviving specimens. The winding path is a variable-width silhouette with sparse cubic Bézier segments, not a constant-width stroke.

The upper-left edge of the 1999 upright is visibly damaged. The 2000 and 2001 letters and the colour specimen confirm a normal vertical edge, so the reconstruction restores it. Small scan rotation, dropout, speckles and stair-step pixel edges were not retained. The 1999 image appears high resolution at first, but its 336-pixel symbol largely repeats in 3 × 3 blocks: its independent detail is about 112 pixels square. Later monochrome specimens offer similar effective detail. Exact original control points and corner radii cannot be recovered from that resolution.

Source-aligned overlays were used to refine the drawing. The historical symbol is asymmetric in its winding path; the outer cross and central crown are regularized where source variations are consistent with scanning. Reconstruction geometry and measured reference notes are included under `construction/`.

## Lettering and layout

The organization name and the exact tagline, **A Path to Better Health**, are reconstructed from the monochrome letterhead arrangement. Candidate serif fonts were compared at the source dimensions. A fitted **EB Garamond, weight 500**, gave the closest defensible name shape among the tested candidates; **Nimbus Roman Italic** best matched the tagline. These are modern substitute fonts used for the reconstruction. The original typefaces have not been conclusively identified.

The name and tagline were fitted to their source ink bounds and converted to individual editable paths. Their original relative size, line separation and large gap from the symbol are retained. The horizontal fit adjusts the name by approximately +3.1% and the tagline by approximately −9.0% relative to their vertical scale. These adjustments follow the raster arrangement and should not be treated as recovered original typesetting instructions.

The optional live-text SVG requires EB Garamond with weight 500 and Nimbus Roman Italic installed. Font substitution will change its appearance. Explicit character positions preserve the measured typesetting; the outlined masters are the reliable exchange files. Fonts are not bundled. Font project links and licence notices are provided in `font-notices/`.

- [EB Garamond project](https://github.com/octaviopardo/EBGaramond12)
- [EB Garamond in Google Fonts](https://github.com/google/fonts/tree/main/ofl/ebgaramond)
- [Nimbus Roman / URW Base 35](https://github.com/ArtifexSoftware/urw-base35-fonts)

## Primary references

### Colour specimen

*Proceedings of the Risk Assessment Workshop*, compiled by Chris Garrett, Environment Canada, Pacific and Yukon Region, [2003]. Catalogue number **En40-240-1/03-00E-PDF**.

- [Government of Canada catalogue](https://publications.gc.ca/site/eng/9.882150/publication.html)
- [Original PDF](https://publications.gc.ca/collections/collection_2019/eccc/en40-240-1/En40-240-1-03-00-eng.pdf)
- **PDF page 71 of 154; printed page 63; slides 38 and 39.**
- Barry Boettger presentation, *Risk Assessment in Drinking Water Quality Programs: The Provincial perspective*.
- Two instances of the symbol on an order/template addressed to the City of Kamloops; surrounding text explicitly names Thompson Health Region.
- The native 59 × 56 image is stored as two adjacent 59 × 28 bitmap strips. `references/thompson-health-region-symbol-colour-2003.png` preserves the recovered pixels and source sRGB profile.
- `references/Thompson_Health_Region_Colour_Source_2003.pdf` contains original PDF pages 1, 3, 52 and 71. The logo is on page 4 of this extract.

If an archived-information notice appears before the government PDF, choose **Continue to publication**. The proceedings reproduce earlier regional material; the publication date does not establish the logo's introduction date. The colour source has the symbol alone, not the name/tagline.

### Monochrome letterheads

| Letter date | Council agenda | Logo page in original PDF |
| --- | --- | --- |
| 9 September 1999 | [Merritt, 12 October 1999](https://old.merritt.ca/wp-content/uploads/archives/meetings/1999/1999-10-12%20RC%20agenda.pdf) | 118 of 132 |
| 9 June 2000 | [Merritt, 27 June 2000](https://old.merritt.ca/wp-content/uploads/archives/meetings/2000/2000-06-27%20RC%20agenda.pdf) | 110 of 135 |
| 1 November 2001 | [Merritt, 13 November 2001](https://old.merritt.ca/wp-content/uploads/archives/meetings/2001/2001-11-13%20RC%20agenda.pdf) | 53 of 74 |

These three letters, in order, are preserved in `references/Thompson_Health_Region_Source_Letters_1999-2001.pdf`. Header crops and source manifests are included beside it.

[Original PofBC catalogue entry](https://projects.ahmadjalil.com/PofBC/?view=gallery&logos=collected-thompson-health-region&mark=thompson-health-region-1999-letterhead)

## Confidence and catalogue treatment

- Strong evidence: organization identity, cross/path motif, five pointed white cutouts, two-colour split, teal/ochre raster values, name/tagline wording and general arrangement.
- Reconstructed: smooth curves, exact corner radii, normalized geometry, font substitutes and spacing refinements.
- Unresolved: original vector master, precise original typefaces, official print colour specifications and colours of the name/tagline in a historical full-colour lockup.

Suggested catalogue label: **“Thompson Health Region — vector reconstruction from 1999–2001 letterheads; symbol colours sampled from a historical raster reproduced in 2003.”** Keep the authentic historical specimens alongside the reconstruction so their status remains clear.

The combined earlier research and remaining archival leads are retained in `references/colour-research-findings.md`. No new physical archive material was inspected and no archival enquiry was sent during this reconstruction phase.
