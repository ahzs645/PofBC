# BC Ferries — logo-history research and vector timeline

Research checked: **27 September 2026**.

## Start here

- `bc-ferries-logo-timeline.svg`: editable timeline with live text, vector logo artwork and clickable source links.
- `bc-ferries-logo-timeline.outlined.svg`: the same layout with lettering converted to paths for portable rendering.
- `bc-ferries-logo-timeline.pdf`: scalable vector PDF.
- `bc-ferries-logo-timeline.png`: large preview; this is the raster export, not the source artwork.
- `assets/`: seven separate, reusable logo/symbol SVG files.
- `timeline.json`: dates, confidence, source records and artwork provenance.
- `SOURCE-NOTES.md`: evidence and limits of the chronology.
- `references/user-supplied/`: the five files from your original ZIP, preserved without macOS metadata.
- `reference-manifest.json`: original file inventory and SHA-256 checksums.
- `build.py`: rebuilds the timeline from its data and local assets.

## What the chronology means

The defensible broad sequence is **dogwood identity, 1960–2003 → wave identity, from 2 April 2003**. Within the dogwood era, the timeline distinguishes a soft, outlined flower visible in a 1963 brochure from the later geometric flower and uppercase wordmark in your archive.

**c.1978 is an inference, not a newly discovered exact launch date.** The contemporary 2003 announcement describes its outgoing logo as unchanged for 25 years. That points to approximately 1978. It does not prove that every geometric dogwood flag, patch or wordmark drawing first appeared in that year. Accordingly, the first panel is a dated *example* from the 1960s, not a claim that its precise artwork lasted until 1978. See S1 and S2 in the source notes.

The official September 2026 investor presentation still displays the wave-and-wordmark identity (S3). “Present” in this package therefore means checked through September 2026, not a promise about future use.

## Artwork provenance

| Asset | Method and limitations |
|---|---|
| `1963-dogwood-flag-interpretation.svg` | A simplified, normalized interpretation of the illustrated flag in the original 1963 brochure. Not a facsimile, not a recovered master, and not an assertion of exact original colour. |
| `legacy-geometric-dogwood.svg` | Smooth hand-reconstructed flower contour from your `ca~bcf2.gif`; transparent background. |
| `legacy-geometric-flag.svg` | Same flower on the flat green flag. Green and yellow are sampled from the supplied GIF. |
| `legacy-wordmark-reconstruction.svg` | Custom path lettering rebuilt from your small raster. No lookalike system font was substituted, but subtle contour/spacing differences may remain. |
| `legacy-lockup-reconstruction.svg` | Reconstructed waving flag and uppercase wordmark. The raster drop shadow is deliberately omitted; this is not a recovered original vector. |
| `current-blue.svg` | Original contours retained from your supplied SVG; background, page-coordinate clips and excess margins removed. Blue sampled from your current-logo PNG. |
| `current-white.svg` | The same existing contours in white, on a transparent background. View against a dark background. |

The patches remain reference material. Their photograph does not establish issue dates or justify additional sequential corporate-logo eras. The two supplied modern-logo files are treated as colour/background applications of one identity, not different redesigns.

No official Pantone/CMYK specification or designer attribution has been verified. Logos and historical source material remain associated with their respective rights holders; this is an independent reference/reconstruction package, not an official brand manual or authorization to imply endorsement.

## Editing and rebuilding

Edit the individual SVG asset once to update its appearance everywhere the builder uses it. Edit text and dates in `timeline.json`. Layout geometry and presentation colours are defined in `build.py`.

```sh
python build.py
```

For PNG and vector PDF exports:

```sh
python -m pip install cairosvg
python build.py --render
```

For an outlined SVG as well, install Inkscape and run:

```sh
python build.py --render --outline
```

The live-text version requests Inter with Arial/sans-serif fallback. **No font files are included.** Use the outlined SVG for a fixed appearance without installing fonts. All logo assets are path-based and do not require fonts.

## Quality checks

The editable timeline contains no embedded raster images. The outlined timeline contains neither live `<text>` elements nor raster `<image>` elements. The PDF has been rendered and visually inspected. These checks address file structure and layout, not historical authenticity: the qualifications above remain important.
