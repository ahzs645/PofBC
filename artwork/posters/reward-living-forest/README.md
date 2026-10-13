# British Columbia Forest Service — REWARD / A Living Forest

Clean, editable vector reconstruction of the poster supplied in this conversation.

## Start here

Open `forest-service-poster.svg` for the self-contained vector master. All lettering in this version is paths, so no fonts need to be installed to display it. Open `forest-service-poster.png` to preview the actual vector artwork before editing.

The image-generation preview displayed earlier in the conversation is a separate raster interpretation. It is included as `reference/generated-raster-preview.png`, but it is not the vector master and was not embedded in any SVG or PDF.

## Files

| File | Purpose |
| --- | --- |
| `forest-service-poster.svg` | Primary vector master, with outlined lettering and named editable layers/groups. |
| `forest-service-poster-live-text.svg` | Same illustration, with four editable supporting text lines. The custom REWARD headline remains paths. |
| `forest-service-poster.pdf` | One-page vector print export, 297 × 417.72 mm. This preserves the reconstruction's proportions; it is not exactly standard A3. |
| `forest-illustration.svg` | Separate central bird, bear, tree, frame and foliage illustration, with transparent surroundings. |
| `forest-service-emblem.svg` | Separate corner emblem, with transparent surroundings. The emblem is the shared BC evergreen artwork from `bc-evergreen-vector`, also used in `forest-sign-rebuild`. |
| `forest-service-poster.png` | 3508 × 4934 pixel, 300 dpi raster export of the actual vector master. |
| `reference-comparison.jpg` | Labelled comparison between the supplied original and the vector reconstruction. |
| `palette.json` | Named colour values used by the artwork. |
| `vector-validation.json` | SVG and PDF structural validation results. |
| `reference/supplied-reference.png` | Original input image, preserved for comparison. |
| `reference/generated-raster-preview.png` | Separate image-generation preview from the conversation; not a vector. |
| `source/rebuild_poster.py` | Hand-authored geometry and SVG reconstruction script. |
| `source/export_and_validate.py` | PDF/PNG export and structural validation script. |
| `source/requirements.txt` | Python dependencies for the included scripts. |

## Reconstruction approach and limits

The illustration uses deliberately authored Bézier curves, separate plumage and foliage panels, geometric eyes, designed bark ribbons, paths, and editable strokes. No automatic raster tracing, edge-contour extraction, or raster-image embedding was used.

REWARD is custom-drawn lettering. Supporting lettering is a fitted, slightly emboldened sans-serif substitute, converted to independent glyph paths in the primary master. The optional live-text SVG leaves those four supporting lines editable.

Paper damage, uneven illumination, edge remnants and print noise were not reproduced. This is an interpretive reconstruction from a photographic reference, not an original Forest Service production master or a claim of exact historical typography or geometry. Fine feather, bark, face and province-silhouette details have been simplified or interpreted. Consult `reference-comparison.jpg` for those differences.

## Editing

Named layers/groups separate the paper, headline, supporting text, illustration, bird, blue boughs, trunk, bear, foreground foliage, paw and emblem. The pale paper rectangle may be hidden or removed for transparent surroundings. Fills use flat colours; a few branch facets use partial opacity. There are no gradients or raster effects. Strokes and clipping paths remain editable where used.

The primary SVG and PDF have no external asset or font dependencies. The live-text version uses Nimbus Sans Bold, with Helvetica and Arial fallbacks. Different installed fonts can change the live-text spacing. No font files are included.

## Rebuilding and exporting

Python 3 and the packages in `source/requirements.txt` are needed to run the scripts. The export script also requires the Inkscape command-line application. The delivered SVG/PDF/PNG files do not require these scripts.

```sh
python -m pip install -r source/requirements.txt
python source/rebuild_poster.py
python source/export_and_validate.py
```

The reconstruction script looks for NimbusSans-Bold.otf at a conventional Linux path. On another system, set `POSTER_FONT` to the path of your own compatible local bold font before running it. Using another typeface will change the supporting lettering. Outputs are written to the package root; running the scripts replaces the corresponding generated files.

## Validation

The primary SVG contains 347 path elements and no image elements. The live-text SVG contains 279 paths and four text elements. The standalone illustration contains 265 paths, and the emblem contains five paths (badge, mainland and three islands) plus a rectangle and polygon for the evergreen. The PDF and PNG were re-exported with CairoSVG after the emblem swap. The PDF was rendered for visual checking and contains no embedded images or font resources. Details are recorded in `vector-validation.json`.

No affiliation, official approval, or ownership transfer in the underlying historical poster design is implied.
