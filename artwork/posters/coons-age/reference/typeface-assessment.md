# Typeface assessment

**Best historical-family hypothesis:** Futura oblique in a medium/demi or bold print weight. This remains an identification from letterforms, not documented identification of the original typesetting face or foundry.

The scan has a single-storey a, single-storey g with a curved descender, nearly circular o, geometric capitals, oblique stems and the straight-footed t associated with the Futura family. The visible features favor that family over an ordinary Helvetica/Arial italic. Related period geometric sans families cannot be excluded at this scan resolution. Invisible OCR font labels in the PDF do not identify the printed type.

**Working substitute:** Jost Italic weight 600 with its default single-storey a, used through the renamed static Forest Ad Sans SemiBold Italic. The derivative retains that default and disables the ss01 double-storey alternative so editable SVG and desktop imports do not accidentally switch to a two-storey a. This current italic file behaves differently from the upright family, whose feature descriptions can be misleading here. No letters were traced from the scan.

Jost is a modern interpretation of Futura. Its author explicitly says its x-height and capital forms depart from Futura. It should not be labelled as the historical font. Local URW Gothic Demi Oblique has a substantially higher x-height and different geometry; League Spartan has a curved t foot that mismatches this ad. Jost still differs in the W and r, some spacing, and oblique angle.

## Measured target on the 565 x 1044 reference

|Line|Ink x interval|Ink width|Ink y interval|Approx baseline|
|---|---:|---:|---:|---:|
|With proper management|81-490|409|720-752|745|
|British Columbia’s forests|81-485|404|758-784|782|
|will last a coon’s age.|81-432|351|794-824|818|
|British Columbia|214-473|259|885-912|910|
|Forest Service|239-453|214|923-948|946|

Intervals are exclusive at the right/bottom edge, taken at grayscale threshold 145. Scanned ink and paper are soft; these are placement guides, not exact glyph boundaries.

At 34 user units Jost 600 ink widths are 389,378,320,248,212 respectively. Starting tracking values 0.95,1.04,1.41,0.73,0.15 per letter interval approximately meet those target lengths; individually fitting final vector ink bounds is preferable. Its tall ascenders are around27 vs25 scan pixels; vertical scale around0.93 brings them closer. Actual stem slant is about9.7 degrees in the Jost l, while this scan appears roughly4-8 degrees after accounting for print distortion. These modifications are optical reconstruction choices, not historical font metrics.

## Sources

- Original newspaper: https://saltspringarchives.com/driftwood/1971/v12n47Dec2-1971.pdf (page11).
- Jost author: https://indestructibletype.com/Jost
- Source distribution and license: https://github.com/google/fonts/tree/main/ofl/jost
- Futura PT modern family/styles for comparison: https://fonts.adobe.com/fonts/futura-pt

Font-source-comparison.png is a visual working comparison. Do not report it as a numeric font-match accuracy test.
