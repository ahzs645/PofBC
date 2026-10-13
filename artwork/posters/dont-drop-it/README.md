# DON'T DROP IT! — B. C. Forest Service

Clean vector reconstruction from the image supplied in the conversation.
This is a newly rebuilt artwork file, not an official archival master.

## Main files

- `dont-drop-it-forest-service.svg`: recommended master. All lettering is outlined; no installed font is needed to display it. Includes six named layers and individually named illustration parts and letters.
- `dont-drop-it-forest-service.pdf`: vector-only export on a 12 × 12 inch page. Verified to contain no raster images or font dependencies.
- `dont-drop-it-forest-service.png`: 3762 × 3762 pixel raster export, transparent outside the circular badge.
- `preview.png`: smaller 1254 × 1254 pixel preview.
- `reference-comparison.png`: supplied reference and rebuilt artwork side by side, on white.

## Optional editing resources

- `dont-drop-it-forest-service-live-footer.svg`: keeps the small footer as live text on a circular baseline. It uses Lato Heavy (weight 800) and will fall back to another sans serif when Lato is absent. This version uses regular arc spacing rather than the optically positioned individual letters of the main master, so its footer layout differs slightly. All main display lettering remains hand-built paths.
- `build_vector.py`: regeneration source. Requires Python, lxml, fonttools, and cairosvg. Supply a locally installed Lato Heavy font using `--font /path/to/Lato-Heavy.ttf`; no font files are included.

Example:

```sh
python build_vector.py --out ./exports --font /path/to/Lato-Heavy.ttf
```

## Construction

The field and double borders are true circle primitives. The main display letters, cigarette wrapper, end details, lower smoke flourish and exclamation mark are hand-authored line and cubic-Bezier paths. The upper smoke consists of two smooth stroked Bezier paths. Main letter counters are compound-path openings, not green patches.

No bitmap contours were automatically traced, and no raster image is embedded in either SVG or the vector PDF. Reference measurements were used for proportions, placement and optical alignment.

The small curved credit is re-typeset using Lato Heavy outlines as a close substitute; the exact historical footer typeface has not been identified. The original photographic texture, irregular edge, tonal variation and very small ash details have deliberately been cleaned up or simplified. The circular geometry is regularized rather than reproducing photographic distortion.

## Palette

- Forest green: `#003E2D`
- Main cream: `#F8E3BB`
- Footer ivory: `#F1F0DE`

These are reconstruction colours chosen from the supplied image, not verified historical ink specifications. Colour values and geometry are directly editable in the SVG or regeneration source.

## Layers

1. Circular field
2. Double circular border
3. Smoke flourishes
4. Hand-built display lettering
5. Cigarette and end details
6. Curved Forest Service credit

The transparency is outside the badge only; its green field is part of the artwork.
