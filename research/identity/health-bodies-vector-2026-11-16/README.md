# Health bodies: vector search, 16 November 2026

The targets were 17 raster logos for current health bodies (Interior Health, FNHA, BC Women's, BCCDC and BCEHS) and seven historic regional health bodies (1997–2003). This package adds **nine SVGs**: five extracted from official PDFs and four vector reconstructions. Each new SVG is listed in `proposed-assets.json`, and every source tried is in `source-register.json`.

## Results

| Target raster | New SVG | Kind |
|---|---|---|
| Interior Health symbol (JPG) | `identity-collected/interior-health/interior-health-symbol-2024-strategic-direction.svg` | Original vector: *Our Strategic Direction 2024-2027*, p. 1 |
| Interior Health stacked (JPG) | `identity-collected/interior-health/interior-health-stacked-rebuilt.svg` | Reconstruction from original parts |
| FNHA white (PNG) | `identity-collected/first-nations-health-authority/fnha-white-stacked-2026-pdf.svg` | Original vector: *Indigenous End-of-Life Guide* brochure, p. 1 |
| FNHA horizontal (PNG) | `identity-collected/first-nations-health-authority/fnha-horizontal-colour-rebuilt.svg` | Reconstruction from original parts |
| BCCDC website logo | `identity-expanded/sub-bc-centre-for-disease-control/bccdc-2021-research-report.svg` | Original vector: Annual Research Report 2020/2021, cover |
| BCEHS website logo | `identity-expanded/bc-emergency-health-services/bcehs-2024-progress-report-endorsed.svg` | Original vector of a **related version** (with the PHSA line) |
| BCEHS website logo | `identity-expanded/bc-emergency-health-services/bcehs-website-layout-rebuilt.svg` | Reconstruction from original parts |
| BC Women's website logo | `identity-expanded/sub-bc-womens-hospital/bc-womens-2024-foundation-impact-report.svg` | Original vector paths; the W's gradients were rewritten (see below) |
| CVIHR grayscale emblem, 1999 | `identity-collected/central-vancouver-island-health-region/central-vancouver-island-health-region-1999-emblem-rebuilt.svg` | Hand-fitted reconstruction |

### Not done

- **Okanagan Similkameen Health Region, 1999:** no vector source was found. The logo is three detailed figure silhouettes with a hand in the foreground. An honest rebuild would need bitmap tracing, which the brief does not prefer, and installing a tracer was not permitted in this session.
- **Campbell River/Nootka CHC, 2000 and 2002:** the Northwest Coast formline fish over a map of Vancouver Island is too detailed to redraw by hand. No PDFs or vectors were found in the Wayback captures of crncare.org.
- **South Cariboo CHC, 1999 and 2000:** the trees are ragged, irregular silhouettes, which also counts as detailed illustration. The 1999 health plan and five 1999 minutes PDFs in the Wayback captures contain no vector logo.
- **Kootenay Boundary CHSS, 1998:** only fax and photocopy scans are known. The outlines of the figures and the lettering are too degraded to rebuild honestly.
- **Greater Trail CHC, 2001:** the only source is a 205 × 105 GIF. The figures are about 70 px tall, and the serif used for GREATER TRAIL cannot be identified at about 15 px. The archived site has no PDFs.
- **North Okanagan HR, 2000:** the emblem is already in the gallery as a vector. The NOHR wordmark survives only at 46 × 22 px, which is too small to identify the typeface or the letter spacing (the earlier package declined for the same reason).

## Extraction notes

- **Interior Health symbol:** these are the PDF's three paths. Their colour converts to #005ba2, while the website JPG uses #2f5088. IH's own 2024 wayfinding guideline gives Pantone 653 C as both hex 005AA2 and RGB 47/79/136, so both colours are official.
- **FNHA white:** these are the PDF's own 55 white fills and 2 zero-width hairline strokes. The strokes are written at 0.35 pt, their width in another FNHA PDF. The white logo in *A Guide to Your Baby's First Foods* sets the tagline flush right, so it is a different arrangement from the target.
- **BCCDC:** the cover includes a "Provincial Health Services Authority" line under the name. It is left out, as on the website logo. The symbol and name are otherwise the PDF's own paths; aligned overlay IoU against the website PNG is 0.84, with the difference mostly anti-aliasing.
- **BCEHS (endorsed):** this is complete as published, including the PHSA line. Its name is larger relative to the letters than on the website logo, so it is not the same artwork.
- **BC Women's:** the lettering (30 glyphs) and the W's 11 clipping shapes are the PDF's own paths. In the PDF, each W shape is filled with about 800 thin horizontal strips, a gradient that the publishing software broke into bands. Three folds are painted with 34 × 43 px CMYK images whose rows are uniform. Each shape is now filled with an SVG linear gradient through its strips' or image rows' own colours, at their own heights. The result matches a MuPDF render of the page, without the render's striping. The PDF is the BC Women's Health Foundation's impact report, which shows the hospital's logo.

## Reconstruction notes

- **Interior Health stacked and BCEHS website layout:** no original vector in these layouts was found. Each part (symbol, wordmark, rule) is an original PDF path set, scaled uniformly and placed on the box it occupies in the official raster. The fitted heights agree with the raster within 1–2%, which confirms that the same artwork was rearranged. The IH layout is filled with IH Blue #2f4f88 (IH's RGB 47/79/136). BCEHS keeps the PDF colours.
- **FNHA horizontal colour:** the lettering comes from the white horizontal logo in *Caregiving*, filled navy #091631 as in FNHA's colour logos. The symbol is the 30 full-colour paths of the stacked logo in the Daily Movement Guide, scaled onto the white logo's symbol box; the two boxes have the same proportions to 0.01%. The aligned overlay with the PNG matches closely.
- **CVIHR emblem:** the four peaks are triangles with 45° sides. Every apex and edge on the 232 × 112 px scan fits that slope. They are clipped along the wave's top edge. The wave is one hand-placed path smoothed with Catmull-Rom curves. No bitmap tracing was used. The greys are averages of a halftoned photocopy, and the original colours are unknown. Silhouette IoU against the scan is 0.95.

## Review images (`review/`)

Each sheet shows the source raster, the vector, and an ink overlay (red: source only; cyan: vector only; dark: both). `overlay.py` fits the vector to the raster's ink box. `overlay_frame.py` is used for SVGs drawn in the raster's own pixel coordinates.

## Reproduce

The source PDFs are not kept here because they total over 300 MB. Download them from the URLs in `source-register.json`; the sha256 of each PDF used is recorded there. Then run the following with PyMuPDF 1.28 (MuPDF 1.28.6), NumPy and Pillow:

```
python -I scripts/interior_health.py DIR_WITH(strategic-priorities.pdf, deciding-to-move-into-long-term-care.pdf)
python -I scripts/fnha.py DIR_WITH(the three FNHA PDFs, original filenames)
python -I scripts/bccdc.py DIR_WITH(bccdc-research-2021.pdf)
python -I scripts/bcehs.py DIR_WITH(bcehs_progress_report_2023-24.pdf)
python -I scripts/bcehs_web_layout.py DIR_WITH(bcehs_progress_report_2023-24.pdf)
python -I scripts/bc_womens.py DIR_WITH(bcwhf-BCWHF-Impact-Report-2024-Single-Pages.pdf)
python -I scripts/cvihr_emblem.py
python -I scripts/proposed_assets.py
```

All of the scripts above were re-run from the downloaded files and reproduced the SVGs byte for byte. `pdfvec.py` holds the shared path and clip writers. `scan.py`, `findblue.py`, `fnha_find.py` and `firstpages.py` are the survey helpers used during the search. Rendering uses `render.cjs` (resvg-js from the repo's `node_modules`).
