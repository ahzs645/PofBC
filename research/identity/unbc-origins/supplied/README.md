# Interior University Society - Vector Brand Kit

Historical identity reconstruction prepared for Ahmad Jalil, version 1.2 (Northern capital-N correction).

## Start here

- Open `IUS_Font_Review.pdf` for the font audit, original-photo comparisons and corrections. `FONT_NOTES.md` records exact reconstruction fonts and remaining uncertainties.

- Open `IUS_Brand_Guide.pdf` for the 13-page visual guide, source comparisons, reconstruction decisions, palette and editing notes.
- Open `index.html` in a browser for the searchable offline catalogue. It works without a server or internet connection. Preview assets on light, paper or dark backgrounds, enlarge them, and download individual SVGs.
- Open `IUS_Brand_Board.pdf` for a single-sheet visual overview. Its editable all-vector source is `guide/IUS_Brand_Board.svg`.
- Use `svg/ius-print-colour.svg` as the primary source-print master.

## What is included

There are **26 production artwork assets**, each supplied in four formats:

| Folder | Contents | Best use |
| --- | --- | --- |
| `svg/` | 26 native vector masters | Editing individual paths, recolouring, web use |
| `pdf/` | 26 single-page vector exports | Placing artwork into print and document layouts |
| `eps/` | 26 vector exchange exports | Older illustration and page-layout workflows |
| `png/` | 26 rendered copies | Quick use where a raster image is needed |

The identity marks have transparent backgrounds unless a panel or physical stock colour is part of the artwork. The white master is intentionally white on transparency; preview it on a dark background.

### Artwork families

1. Source-print mark: colour, black, white, reversed panel and vertical orientation.
2. Compact and extended supplied-reference alternatives, labelled as contemporary reconstruction variants.
3. Enamel pin, one-colour pin adaptation and separate pin silhouette.
4. Northern U button and the I SAY YES TO / NORTHERN / INTERIOR / YES / UNIVERSITY button.
5. Supporter bumper sticker and historical toll-free sticker.
6. Optional interpretive sweatshirt lettering.
7. Letterhead template, re-typeset 8 June 1988 invitation and re-typeset business fundraising letter.
8. Membership card, supporter-only card and supporter petition spread.
9. Support Campaign wording, interpretive graduate illustration and reconstructed brochure cover.
10. Separate three-bar component and the campaign headline for a university in Prince George.

`asset-manifest.json` lists each master, its reconstruction status and matching exports.

## Genuine vector construction

These are not photographs wrapped in SVG containers. The main mark is built from fitted font outlines and independently constructed quadrilateral bars. The pin uses separate shape/material areas. Buttons and stickers use vector circles, frames, custom geometric/collegiate letterforms and actual outlined lettering. The graduate illustration is manually constructed from curves and linework.

Production SVGs contain no embedded raster images, no live text, no external font references and no scripts. Typography is directly editable as shape geometry. The pin, forms and illustration intentionally retain some editable vector strokes; SVG strokes are genuine scalable vector content. Reproduction PDFs preserve these as vector drawing operations.

`vector-validation.json` records the final structural and bounds checks, including matching SVG/PDF files and per-file hashes. The production SVGs contain editable path geometry; their matching PDFs contain zero raster images and zero text-show operations. The validation report records the current path count. Source photographs appear only in the reference material and the guide, where they are explicitly labelled.

## What is confirmed, reconstructed and interpretive

**Confirmed by the supplied photographs:** the wording and principal arrangements; the three-line print identity with projecting orange bars; the rotated stationery mark; clipped-corner pin; metal surrounds on the pin lettering and bars; round campaign buttons; supporter and toll-free sticker structures.

**Reconstructed:** exact letterforms, spacing, proportions and colours. Nimbus Sans, Nimbus Roman, Nimbus Sans Narrow and URW Bookman outlines are working substitutes, not identified original typefaces. The orange Northern U button combines a custom capital **N**, fitted Bookman-derived **“orthern”** and a separately drawn large **U**. The YES button’s rounded geometric NORTHERN and collegiate letters are also constructed separately. The pin has a separate optical weight adjustment.

**Interpretive:** the graduate illustration and sweatshirt treatment. The photograph supports their broad structure, but not every facial detail, fold, letterform or obscured area. Those assets are explicitly labelled interpretive; the graduate drawing is not the recovered original artist's artwork.

**Document layouts:** the invitation, business appeal and petition are re-typeset studies. Line breaks and punctuation are reconstruction choices. Dense statement-of-support microcopy on the forms is unreadable and its area remains blank. Uncertain small letterhead address details, handwritten marks, signatures and serial numbers are omitted. Historical addresses, telephone numbers and donation amounts are documentary content.

The invitation visibly carries the date **8 June 1988**. This documents an observed use date, not the creation date of the identity. The archive accession **1992.2** visible in a display caption is not treated as a design date. No original standards manual, master vector, physical measurement scale or measured colour targets were supplied.

## Palette

`palette/` contains approximate sRGB values in Adobe ASE, GIMP GPL, CSS and JSON formats. The print orange, pin enamel, button orange, yellow sticker stock and rose-red letterhead band are kept distinct. These colours are visual reconstruction choices; no Pantone match or colour-managed CMYK specification is asserted.

## Editing

Open a production SVG in a vector editor. Named groups expose words, individual letters, bars, material regions, figures or form sections. No fonts need to be installed to open, scale or recolour the final masters. Type is outlined rather than editable with a text cursor. Use the authoring scripts or re-typeset a line if its wording must change.

Scale the complete logo uniformly. As a new working recommendation, leave one capital height of clear space around the outermost bars. A useful first proof size for the complete print mark is 200 px wide on screen or 35 mm in print. These are new reconstruction guidelines, not historic specifications.

## Rebuilding from source

The supplied `source/` scripts regenerate the geometry and exports without tracing or reading source pixels. Editing the scripts can change colours, dimensions, wording or arrangement. The reference photographs are used for documentation, not as production artwork.

Authoring dependencies are Python 3, the packages in `source/requirements.txt`, Inkscape, URW Base35 OTF fonts and Open Sans TTF fonts. Font paths are declared in the scripts and can be adapted to another installation. The guide and font report use Open Sans for explanatory text; that is not part of the reconstructed historic identity. Font software is not bundled.

```bash
python3 -m pip install -r source/requirements.txt
python3 source/build_all.py
```

Only the build environment needs those fonts and tools. The delivered SVG/PDF/EPS masters remain self-contained.

## References and attribution

All ten supplied files are preserved in `reference/supplied/`. `reference/source-inventory.json` assigns P01-P06 to original photographs and R01-R04 to prior raster reconstructions. `reference/source-audit.md` describes the evidence and differences. Inspection crops and perspective-corrected views in that folder are analysis aids, not vector masters or metrically calibrated scans.

The kit reconstructs the historical Interior University Society identity. It does not claim authorship of the original identity, original lettering designs, campaign wording or archival illustration, and does not purport to grant rights to those historical materials.

## Version 1.2 Northern capital-N correction

The capital N on the orange Northern U button is now independently constructed vector geometry. The correction follows the original photograph’s thinner tapered serifs, lighter diagonal and mainly left-projecting top-right serif. The fitted Bookman-derived **“orthern”** and the custom large **U** retain their v1.1 treatment. The exact historical font remains unconfirmed; no automatic tracing is used.

`reference/font-audit/northern-n/Northern_N_Detail.png` records the focused v1.1-to-v1.2 proof, which is also included as the final page of `IUS_Font_Review.pdf`. The earlier campaign comparison remains labelled **v1.0 to v1.1**; it is preserved as review history.

## Version 1.1 font review

The review uses the original artifact photographs as primary evidence. It retains the main print font, revises the toll-free serif lettering and numerals, restores italic fundraising headings, refines the YES button typography and Northern U shape, increases the pin’s apparent black weight, and brings CAMPAIGN to 82.5% of SUPPORT’s cap height. It also corrects the re-typeset invitation to the photographed DAHLLOFF/Dahlloff spelling. All affected SVG, PDF, EPS and PNG assets are regenerated. `reference/font-audit/` holds source/candidate boards, measurements and selected v1.0 artwork for comparison; those comparison files are not additional production masters.
