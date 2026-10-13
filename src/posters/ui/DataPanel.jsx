// A part's panel, drawn from data: the same voice as the coastal poster's hand-written panels,
// for posters whose parts are described in a data file (see forest-service/posters.js).

import { SiteLink } from '../../site/navigation.jsx'
import { Facts, Item, Reveal } from './Reveal.jsx'

const Links = ({ links }) => (
  <Item as="ul" className="pv-links">
    {links.map((link) => (
      <li key={link.label + (link.note ?? '')}>
        <SiteLink to={link.to} className="pv-link-card">
          <b>{link.label} <span aria-hidden="true">→</span></b>
          {link.note && <span>{link.note}</span>}
        </SiteLink>
      </li>
    ))}
  </Item>
)

const Palette = ({ colours }) => (
  <Item as="ul" className="pv-palette" aria-label="Colours">
    {colours.map(({ name, value }) => (
      <li key={value}>
        <span className="pv-palette-chip" style={{ background: value }} aria-hidden="true" />
        <span>{name}</span>
        <code>{value}</code>
      </li>
    ))}
  </Item>
)

const Sources = ({ sources }) => (
  <Item as="div" className="pv-sources">
    Sources:
    <ul>{sources.map((s) => <li key={s.href}><a href={s.href} target="_blank" rel="noopener noreferrer">{s.label}</a></li>)}</ul>
  </Item>
)

const Block = ({ block }) => {
  if (typeof block === 'string') return <Item as="p">{block}</Item>
  if (block.h) return <Item as="h3">{block.h}</Item>
  if (block.facts) return <Facts rows={block.facts} />
  if (block.note) return <Item as="div" className="pv-note"><p>{block.note}</p></Item>
  if (block.palette) return <Palette colours={block.palette} />
  if (block.links) return <Links links={block.links} />
  if (block.sources) return <Sources sources={block.sources} />
  return null
}

/**
 * One part's panel. On the overview it also lists the parts, as a table of contents, and offers
 * the tour.
 */
export function DataPanel({ partId, parts, order, onSelect, tour }) {
  const part = parts[partId]
  const { panel } = part
  const steps = order.filter((id) => id !== 'overview')
  const index = steps.indexOf(partId)
  const eyebrow = index >= 0 ? `Part ${index + 1} of ${steps.length} · ${panel.eyebrow}` : panel.eyebrow
  const blocks = panel.blocks ?? []
  // On the overview the contents come before the series links, which are the panel's last block.
  const tail = partId === 'overview' && blocks.findIndex((b) => b.h) >= 0 ? blocks.findIndex((b) => b.h) : blocks.length
  return (
    <Reveal>
      <Item as="p" className="pv-eyebrow">{eyebrow}</Item>
      <Item as="h2">{panel.heading}{panel.em && <>, <em>{panel.em}</em></>}</Item>
      <Item as="p" className="pv-lede">{panel.lede}</Item>
      {blocks.slice(0, tail).map((block, i) => <Block key={i} block={block} />)}
      {partId === 'overview' && (
        <>
          {tour && (
            <Item as="div" className="pv-row">
              <button type="button" className="pv-ghost pv-solid" onClick={tour.toggle}>{tour.playing ? 'Stop the tour' : 'Play the tour'}</button>
              <span className="pv-muted">{tour.seconds} seconds a part, hands free</span>
            </Item>
          )}
          <Item as="p" className="pv-eyebrow" style={{ marginTop: 22 }}>Contents</Item>
          <Item as="ol" className="pv-contents">
            {steps.map((id, i) => (
              <li key={id}>
                <button type="button" onClick={() => onSelect(id)}>
                  <span className="pv-num">{String(i + 1).padStart(2, '0')}</span>
                  <span className="pv-name">{parts[id].label}</span>
                  <span className="pv-hint">{parts[id].hint}</span>
                </button>
              </li>
            ))}
          </Item>
        </>
      )}
      {blocks.slice(tail).map((block, i) => <Block key={tail + i} block={block} />)}
    </Reveal>
  )
}
