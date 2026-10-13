import { Facts, Item, Reveal } from '../../ui/Reveal.jsx'
import { GlyphRow } from '../../ui/GlyphRow.jsx'
import sloganPreview from '../slogan_preview.png'

export function Slogan({ glyphs, highlight, onHighlight }) {
  return (
    <Reveal>
      <Item as="p" className="pv-eyebrow">Part 5 of 5 · The slogan</Item>
      <Item as="h2">The Environment ~ <em>It’s Your Home!</em></Item>
      <Item as="p" className="pv-lede">The ministry's line of the period, set full width in the same Bookman as the title. Two swash capitals, and one small mark that took its own correction.</Item>
      <Item as="label" className="pv-toggle"><input type="checkbox" id="hl-slogan" checked={highlight} onChange={(e) => onHighlight(e.target.checked)} /> Highlight the alternates and the tilde</Item>
      <GlyphRow glyphs={glyphs} />
      <Item as="h3">The tilde</Item>
      <Item as="p">The separator in the original is short, heavy and sits mid-line. The first Bookman rebuild used the font's ordinary ASCII tilde, shrunk to 70 percent and lowered, and it came out thin. The correction switched to the font's heavier spacing tilde, the accent glyph, scaled to 86 percent and nudged into place.</Item>
      <Facts rows={[
        ['Glyph', 'asciitilde → tilde (U+02DC)'],
        ['Scale', '0.70 → 0.86'],
        ['Offset', 'dx 45, dy −331 font units'],
        ['Advance', 'kept at 452.9, so no other letter moved'],
        ['Pixels changed', '601, all inside a 65 × 31 pixel box at 100 dpi']
      ]} />
      <Item as="figure" className="pv-figure">
        <img src={sloganPreview} alt="Enlarged crop of the corrected slogan showing the heavier tilde" loading="lazy" />
        <figcaption>The corrected separator, enlarged from the vector master.</figcaption>
      </Item>
      <Facts rows={[
        ['Ink box', '2074 × 104 units'],
        ['Size', '127.4 units'],
        ['Alternates', 'E.swsh in Environment, H.swsh in Home']
      ]} />
    </Reveal>
  )
}
