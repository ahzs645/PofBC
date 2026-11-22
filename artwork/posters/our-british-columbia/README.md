# Our British Columbia - vector reconstruction

**Version 1.0 | 21 November 2026**

This package reconstructs the supplied photograph of the *Our British Columbia* / British Columbia Pavilion Expo 86 film poster as a clean, editable vector. It is a reconstruction of the printed design, not an original historical production master. The paper curl, reflections, holders, magnets, age tint and surrounding board are excluded.

## Start here

| File | Purpose |
| --- | --- |
| `Our_British_Columbia_1986.svg` | Main vector master. All lettering is outlined. No installed fonts or linked images are required. Five named layers separate geometry, handwritten Our, title, billing and footer emblems. |
| `Our_British_Columbia_1986.pdf` | One-page vector PDF export. No raster artwork is embedded in this poster PDF. |
| `Our_British_Columbia_1986.png` | 2400 x 3480 preview. Use the SVG or PDF for scalable artwork. |
| `Our_British_Columbia_1986_editable-text.svg` | Same design with live billing text for revisions. Install the supplied Six Caps and Oswald fonts first. The large title remains editable custom paths. |
| `Our_British_Columbia_Overlay.html` | Self-contained comparison viewer: opacity blend, vertical wipe, photograph, reconstruction, colour boundaries and lettering edges. Open the file in a browser; no network connection is needed. |
| `Our_British_Columbia_Comparison.png` | Corrected photograph, reconstruction and 50% blend, together. |
| `Reconstruction_Notes.pdf` | Illustrated construction, comparison and uncertainty record. |
| `assets/` | Separate title, Pavilion, Industrial Showmanship and Bob Rogers vectors, plus the reused PofBC flag source. |
| `source/` | Reproducible poster construction and registration/comparison scripts. |
| `review/` | Edge comparisons, perspective transform, 27 measured anchors, validation record and font comparisons. |
| `references/` | Supplied photograph, recovered logo close-ups and research notes. |

## What was rebuilt

The red/blue rays, white separators, yellow sunburst panel and lower border are a small set of intentionally constructed polygons. Bilateral geometry and straight printed baselines replace the bends introduced by the photographed sheet. The yellow panel is one continuous 27-vertex shape with a 7-unit white separator.

The large **BRITISH COLUMBIA** wordmark is a set of authored Bezier letterforms. It preserves the large B/C relationship, the R/I connection, the C/O crossing and the I/A baseline connection seen in the photograph. The R bowl, C curve, counters, serifs and inter-letter gaps were reviewed against the source. The handwritten **OUR** is reconstructed from five editable pen-stroke paths. No automatic contour tracing was used.

The uppercase film billing is reconstructed with outlined **Six Caps**; mixed-case fine print uses **Oswald Light 300**, with an optical slant for the two lower credit lines. These are visual substitutes. The original historical typeface has not been conclusively identified. The large title is custom artwork rather than a claim that an available font is exact.

## Reuse from PofBC

The Pavilion badge reuses the **12 native flag paths** in PofBC's `src/assets/flagMark.js`. Their path geometry is retained, with colours adjusted for the poster and a white support silhouette. The badge's frame and captions were rebuilt, and its BRITISH COLUMBIA title uses the same custom lettering as the main poster.

- Requested poster page: https://projects.ahmadjalil.com/PofBC/?view=posters&poster=expo-86-davidson
- Reused component, pinned source: https://raw.githubusercontent.com/ahzs645/PofBC/bb468bc78bbc81d214477293934e0a8e3d4977d7/src/assets/flagMark.js
- Repository snapshot: `bb468bc78bbc81d214477293934e0a8e3d4977d7`
- Source flag blob: `50be0e64651e66809102f48e5491fecf7ea0cd3d`

The Davidson poster's general EXPO / three-ring 86 mark is a different mark from this poster's British Columbia Pavilion badge, so that particular symbol was not inserted. The later crest wordmark in the repository also has different lettering.

The production emblems were constructed using clearer photographs of the same physical poster. Industrial Showmanship uses a constructed gear, rings, wings, lightning, camera, globe and tripod with an outlined Stardos Stencil substitute. Bob Rogers & Company, Inc. uses outlined Alfa Slab One lettering and a constructed filmstrip. The small emblem letterfaces and fine linework are approximations, not recovered original masters.

## Overlay review

The supplied 1200 x 1600 photograph was registered to a **1000 x 1450 working frame** using four manually selected sheet points. The forward/inverse transform and source landmarks are saved in `review/registration.json`. One projective transform cannot fully flatten a curled sheet.

The coloured-shape comparison is separated from the dark-lettering comparison. Physical holders and magnets are excluded from both edge layers. Reflected lettering is retained for inspection, with its lower reliability stated. The complete review is in the HTML viewer and PNG edge sheets.

For **27 manually paired yellow-panel boundary vertices**, the final construction has a **median displacement of 2.123 units** and a **maximum of 7.016 units** on the 1000-unit-wide frame. These are selected-anchor residuals only. They include registration, manual measurement and paper-curl uncertainty and are **not an overall fidelity percentage**.

Two visual refinement passes corrected unintended I/T, U/M, M/B and L/U joins, unified the B/C cusp, narrowed the R bowl, refined the large C, and removed small blue notches beside the upright sunburst shoulders. Remaining contour differences are visible in the title-edge review, especially small counter and shoulder details.

## Editorial restoration record

All main credit names and roles are readable. Some very small text is hidden by opaque holders in every available full-poster photograph. The clean design includes documented editorial restorations so the footer reads continuously; do not treat these words as verified original transcription.

| Text | Evidence and treatment |
| --- | --- |
| `For Lisa, Tyler and Jordy` | Best visual reading. The intermediate r is visible; the final letters are partly shadowed. |
| `Equipment by` and the repeated `Vancouver` ending | Restored from the visible surrounding words and the production-credit sentence structure. |
| `with special thanks to` | Editorial expansion of the hidden connective phrase before George Chapman. |
| `B.C. Film Production Office` | The photograph shows `B.C. Film Production`; `Office` is hidden. The term is corroborated in period production records, but its presence on this exact poster is not directly verified. |
| `Sound Track distributed` | Hidden middle words restored from the visible distribution-credit sentence. |
| `Burbank, CA 91502` | The photograph shows `915`; `02` is an address-based reconstruction. Any additional original ending after the ZIP is unknown and has not been added. |

`credit-transcription.json` records the printed reconstruction and confidence note for each text group. `references/typography-and-transcription.md` preserves the readable fragments separately from editorial expansions. The uncertain groups also carry descriptions inside the SVG.

## Dimensions and colour

The 1000:1450 aspect ratio is a photo-derived working choice, not a verified original sheet size. The seller's listing title describes a different-sounding poster and is insufficient to establish the artist or exact dimensions here. No artist attribution is assigned.

The SVG and PDF can be scaled. The PDF's export page is 750 x 1087.5 points (1000 x 1450 SVG units at 96 units per inch); that export scale is **not** a statement of historical print dimensions. Set the intended physical size when placing it for printing.

The main design uses white, blue `#143799`, red `#e51d30`, yellow `#ffc000` and dark lettering `#24231b`. These are clean reconstruction colours. The source is not colour calibrated and shows strong variations from shadow, ageing and glare. No spot-colour or CMYK match is claimed.

## Source photographs and corroboration

1. User-supplied poster photograph, retained in `references/supplied-poster.webp`.
2. Same physical poster listing and two detail photographs: https://www.ebay.com/itm/397627062142
3. Pavilion detail: https://i.ebayimg.com/images/g/MawAAeSwl~Zplo8T/s-l1600.webp
4. Industrial Showmanship / Bob Rogers detail: https://i.ebayimg.com/images/g/YIEAAeSwWLhplo8j/s-l1600.webp
5. AFI production-note transcription for *The Golden Seal* (1983), corroborating the period term Film Production Office: https://catalog.afi.com/Film/57980-THE-GOLDEN-SEAL
6. Contemporary *Cinema Canada*, July/August 1986, printed pages 43 and 45: https://cinemacanada.athabascau.ca/index.php/cinema/article/download/3253/3293.pdf

No higher-resolution full-poster original was recovered. The apparent 2000px eBay URL returns the same 1200 x 1600 source image. The useful additions are the two independent close-ups.

## Editing and rebuilding

Use the main outlined SVG for ordinary editing in a vector editor. Each major component is grouped and named. Use the editable-text SVG when changing credits; install the two supplied open fonts first. Font licences are in `fonts/`.

To regenerate the poster from the supplied construction files, install the Python packages in `source/requirements.txt`, then run from this directory:

```bash
python3 source/build_poster.py
inkscape Our_British_Columbia_1986.svg --export-filename=Our_British_Columbia_1986.pdf
inkscape Our_British_Columbia_1986.svg --export-filename=review/vector-1000.png --export-width=1000
python3 source/compare_reconstruction.py review/vector-1000.png --landmarks source/vector-landmarks.json
```

The builder reads the reusable emblem SVGs in `assets/` and the two billing fonts in `fonts/`. It refreshes the Pavilion title from the same custom letterform source. Re-running the comparison writes review output under `review/`; copy its updated `interactive-review.html` to the top-level overlay filename when distributing a new version. The reference-registration and comparison scripts use DejaVu Sans for review labels; supply an equivalent font path on systems where its Linux path is absent.

## Validation

The main SVG parses as XML, contains **1,126 paths**, **zero image elements**, **zero live text elements**, and no duplicate IDs. Its five named layers remain editable. The separate text-editable version intentionally retains live billing text.

The poster PDF contains one page, **zero raster image objects**, and native vector drawing operations. SVG and PDF renders were visually inspected. The comparison viewer is self-contained; JavaScript syntax, all six modes and the three region buttons passed isolated DOM logic checks. A browser screenshot check could not run because local browser startup is restricted in this environment. Details are in `review/validation.json`.

## In this repository

Kept, each byte for byte as supplied except this README, which has this section added: the outlined
master and the editable-text SVG, `assets/` less `pofbc-flagMark.js` (a copy of this repo's own
`src/assets/flagMark.js` at the commit named above), `source/`, `credit-transcription.json`,
`manifest.json`, the two Markdown notes in `references/`, the fonts' licences, and `review/`'s
registration, comparison and validation records (its JSON).

Left out: the photographs (`references/*.webp`), the PNG preview, comparison and every review PNG
and JPEG, the PDF, the reconstruction notes PDF (it carries the photographs), the overlay page
(2.2 MB, it embeds the photograph) and the two font files, Six Caps and Oswald Light (both under the
SIL Open Font License, licences kept in `fonts/`, the fonts available from Google Fonts). Without
them, the scripts in `source/` will not run here; they are kept as the record of how the drawing was
made. `manifest.json` still lists the files left out.

The Posters view (`?view=posters&poster=our-british-columbia`) shows
`src/posters/expo-86/our-british-columbia.svg`, made from `Our_British_Columbia_1986.svg` by
`web_copy.py`: every id prefixed `obc-`, the emblems written without their `ns0:` prefixes (an HTML
parser does not draw them otherwise), the Inkscape layer labels kept as `data-label`, the metadata
dropped, the title and description reworded and the em dashes in the emblems' own titles made
commas. The white paper moves out of the first layer, and the fine print out of the billing layer,
each to a layer of its own in the same place, so the Posters view can dim each layer as one; drawn,
nothing changes. The shelf card is `our-british-columbia.thumb.jpg`, 480 × 696. The poster is
unlisted, with the other Expo 86 posters.
