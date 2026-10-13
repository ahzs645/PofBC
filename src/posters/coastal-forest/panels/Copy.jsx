import { COPY_TEXT } from '../copyText.jsx'
import { SECTIONS } from '../parts.js'
import { Facts, Item, Reveal } from '../../ui/Reveal.jsx'

export function Copy({ focus, zoom, onFocus, onZoom }) {
  const dim = (key) => (focus && focus !== key ? { opacity: 0.45 } : undefined)
  return (
    <Reveal>
      <Item as="p" className="pv-eyebrow">Part 3 of 5 · The copy</Item>
      <Item as="h2">Six million hectares, <em>in four columns</em></Item>
      <Item as="p" className="pv-lede">The text is a period argument for "integrated management": the coastal forest as the most productive in Canada, its early clearing, and a province where, as it says, half of every dollar depends on wood products.</Item>
      <Item as="p">Hover a section to find it on the poster; click to zoom in on it.</Item>
      <Item as="div" className="pv-text-sections">
        {Object.entries(SECTIONS).map(([key, { label }]) => (
          <button
            key={key}
            type="button"
            className="pv-section-btn"
            aria-pressed={zoom === key}
            onMouseEnter={() => onFocus(key)}
            onMouseLeave={() => { if (zoom !== key) onFocus(zoom) }}
            onClick={() => { const next = zoom === key ? null : key; onZoom(next); onFocus(next) }}
          >{label}</button>
        ))}
      </Item>
      <Facts rows={[
        ['Faces', 'Bookman BT Roman; the introduction in Bookman Italic'],
        ['Sizes', 'headings 27 · introduction 24 · body 20.1 units'],
        ['Columns', 'x = 164, 584, 1001, 1431, 1857'],
        ['Transcription', 'manual, from the photograph']
      ]} />
      <Item as="div" className="pv-note"><p>Two readings are tentative and are marked below: <mark>goldback fern</mark> and <mark>25-storey</mark>. The historical wording is kept as poster copy and has not been updated or fact-checked as current science.</p></Item>
      <Item as="h3">How it got here</Item>
      <Item as="p">Until the matching text faces were supplied, this block stood in Nimbus Roman Bold: close enough in colour and width to hold the columns, but not the face on the print. It is now set in the supplied Bookman BT Roman, with the five-line introduction in the supplied Bookman Italic rather than a slanted Roman, and the headings in the Roman rather than a synthetic bold. Wording and line breaks did not move; the sizes shifted a little so the same lines still fill the same columns, and no glyph is squeezed horizontally to make them fit.</Item>
      <Item as="div" className="pv-copy-text">
        {COPY_TEXT.map(({ key, heading, paragraphs }) => (
          <div key={key} style={dim(key)} onMouseEnter={() => onFocus(key)} onMouseLeave={() => onFocus(zoom)}>
            {heading && <h4>{heading}</h4>}
            {paragraphs.map((p, i) => <p key={i} className={key === 'intro' ? 'pv-intro' : undefined}>{p}</p>)}
          </div>
        ))}
      </Item>
    </Reveal>
  )
}
