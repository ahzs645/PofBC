import { ORDER, PARTS } from '../parts.js'
import { Facts, Item, Reveal } from '../../ui/Reveal.jsx'
import referencePoster from '../reference_poster.jpg'

export function Overview({ onSelect, onTour, touring }) {
  return (
    <Reveal>
      <Item as="p" className="pv-eyebrow">About this piece</Item>
      <Item as="h2">A poster, and where each piece came from</Item>
      <Item as="p" className="pv-lede">A vector reconstruction of a framed print, made from one photograph of it. Every part of the page has its own history: the crest the Province used before its rising-sun mark, a swash-alphabet Bookman rebuilt letter by letter, a transcription of copy too small to read with certainty.</Item>
      <Item as="div" className="pv-row">
        <button type="button" className="pv-ghost pv-solid" onClick={onTour}>{touring ? 'Stop the tour' : 'Play the tour'}</button>
        <span className="pv-muted">12 seconds a part, hands free</span>
      </Item>
      <Item as="p" className="pv-eyebrow" style={{ marginTop: 22 }}>Contents</Item>
      <Item as="ol" className="pv-contents">
        {ORDER.filter((id) => id !== 'overview').map((id, i) => (
          <li key={id}>
            <button type="button" onClick={() => onSelect(id)}>
              <span className="pv-num">{String(i + 1).padStart(2, '0')}</span>
              <span className="pv-name">{PARTS[id].label}</span>
              <span className="pv-hint">{PARTS[id].hint}</span>
            </button>
          </li>
        ))}
      </Item>
      <Facts rows={[
        ['Page', '24 × 36 in, assumed'],
        ['Units', '2400 × 3600'],
        ['Ink', '#eee3c0 on #121411'],
        ['Dated by its logo', '1979 – 1986']
      ]} />
      <Item as="figure" className="pv-figure">
        <img src={referencePoster} alt="The framed original poster, photographed under glass with reflections of ceiling lights" width="1000" height="1333" loading="lazy" />
        <figcaption>The framed original, and the source for everything but the photo credit, which only became readable from a separate close-up. Reflections, perspective and small print are why some readings are still marked tentative.</figcaption>
      </Item>
    </Reveal>
  )
}
