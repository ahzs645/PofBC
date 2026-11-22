# Report lettering outlines

This is a restricted, fixed-wording vector reconstruction for the British Columbia Recreation and Conservation branding study. It is not an installable font, does not contain font software, and does not claim to reproduce recovered original production outlines.

## Method

The user-selected modern comparison face is Corporatus. Official public raster specimens were requested at the endpoint recorded in `specimen_manifest.json`, at the largest observed effective size (`rs=256`, approximately341.33 raster pixels per em). No font binary was downloaded.

For this typography layer, glyph contours were measured at the antialias midline, divided at hard corners, and reconstructed as straight segments and smooth cubic Bezier curves. The same reusable glyph component is used in every word. This is an analytical reconstruction from the public type specimen, not a manual reconstruction of the entire typeface or an automatic trace of the scanned report lockups. The emblems elsewhere in the package use their own geometric construction.

Thirty-six glyphs cover the fifteen documented report phrases in `specimen_manifest.json`. Source geometry and advance rounding are retained in `glyph_geometry.json`. The small glyph set is intended only for these branding applications.

## API

```python
from type_engine import text_group, measure_text

metrics = measure_text(
    'General Administration', font_size=100,
    tracking=-50, word_space=-220, horizontal_scale=1
)

svg_group = text_group(
    'General Administration', font_size=100,
    tracking=-50, word_space=-220, color='#163c36',
    horizontal_scale=1, x=100, y=200, anchor='start'
)
```

- `tracking` and `word_space` are added in **thousandths of an em**. Thus `-50` is `-0.05em`; `-220` is an additional `-0.22em` beyond the nominal625-unit space.
- Tracking also applies to spaces.
- `x,y` specify the baseline position. Positive y points down.
- `anchor='start'`, `'middle'`, or `'end'` anchors the visible ink, avoiding unequal first-letter sidebearings.
- `measure_text` returns the advance, visible ink bounding box, nominal cap height, and glyph count.
- Unsupported characters raise an exception. The limited repertoire should not be presented as a complete font.

## Outputs and validation

`wordmarks/` contains fifteen self-contained SVG specimens with path lettering. The two main lines use the measured prior presets; other specimens use a provisional tight setting and are construction components, not claims of independently recovered original spacing. Final report layouts should fit their own source line bounds and preserve the source capitalization.

The mean black-ink intersection-over-union against the public type raster is0.99896; the lowest glyph is0.99630. This measures fidelity to that modern raster specimen, **not historical authenticity**. The comparison is recorded in `outline_metrics.json` and shown in `Glyph_Outline_Comparison.png`.

All fifteen SVGs were parsed successfully and checked for absence of `<text>` and `<image>` elements. Their lettering remains visible without Corporatus installed.

The modern revival and the printed historical artwork retain small differences. Follow the report source for unusual line treatments, including the lowercase-style initial m and reduced R/B forms in the Marine Resources arrangement.
