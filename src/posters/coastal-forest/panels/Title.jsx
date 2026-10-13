import { Facts, Item, Reveal } from '../../ui/Reveal.jsx'
import { GlyphRow } from '../../ui/GlyphRow.jsx'

export function Title({ glyphs, highlight, onHighlight }) {
  return (
    <Reveal>
      <Item as="p" className="pv-eyebrow">Part 2 of 5 · The title</Item>
      <Item as="h2">Fourteen letters, <em>four of them alternates</em></Item>
      <Item as="p" className="pv-lede">The title is set in Bookman JF Pro, a digital revival of the swash-heavy Bookman that was everywhere in the 1970s and 80s. The flourishes are not drawn by hand: they are the font's own alternate glyphs, chosen one letter at a time.</Item>
      <Item as="label" className="pv-toggle"><input type="checkbox" id="hl-title" checked={highlight} onChange={(e) => onHighlight(e.target.checked)} /> Highlight the alternates on the poster</Item>
      <GlyphRow glyphs={glyphs} />
      <Item as="p">The long <b>r</b> is what creates the flourish over the <b>e</b> in <i>Forest</i>. The <b>e</b> itself is an ordinary letter. None of these alternates has a Unicode code point in the font, so the layout stores plain text plus a glyph name per letter, and the renderer picks the outline directly.</Item>
      <Facts rows={[
        ['Ink box', '808 × 129 units, matched to the original'],
        ['Size', '126.3 units, glyphs scaled uniformly'],
        ['Tracking', '−36.8 font units, to fit the box'],
        ['Word space', 'tightened to 100 font units']
      ]} />
      <Item as="h3">How it got here</Item>
      <Item as="p">The first rebuild traced the title from the photograph, and tentatively identified the face as ITC Tiffany. Both were set aside once a Bookman file was supplied. The lettering is now typeset from real outlines and then converted to paths, so no application can substitute a font or lose an alternate.</Item>
    </Reveal>
  )
}
