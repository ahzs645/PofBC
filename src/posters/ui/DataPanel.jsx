// A part's panel, drawn from data: the same voice as the coastal poster's hand-written panels,
// for posters whose parts are described in a data file (see forest-service/posters.js).

import { useState } from 'react'
import { SiteLink } from '../../site/navigation.jsx'
import { Facts, Item, Reveal } from './Reveal.jsx'
import { Connections } from './Connections.jsx'
import { Segmented } from './Segmented.jsx'
import { glance } from './glance.js'
import { Slider } from '../../site/ui/Slider.jsx'

const Links = ({ links, brief }) => (
  <Item as="ul" className="pv-links">
    {links.map((link) => (
      <li key={link.label + (link.note ?? '')}>
        <SiteLink to={link.to} className="pv-link-card">
          <b>{link.label} <span aria-hidden="true">→</span></b>
          {link.note && !brief && <span>{link.note}</span>}
        </SiteLink>
      </li>
    ))}
  </Item>
)

const Downloads = ({ files }) => (
  <Item as="ul" className="pv-links">
    {files.map(({ label, file }) => (
      <li key={file}>
        <a href={`${import.meta.env.BASE_URL}${file}`} className="pv-link-card" download>
          <b>{label} <span aria-hidden="true">↓</span></b>
        </a>
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
    {/* A source named without a link (a printed article, a catalogue entry) is cited by its title. */}
    <ul>{sources.map((s) => <li key={s.href ?? s.label}>{s.href ? <a href={s.href} target="_blank" rel="noopener noreferrer">{s.label}</a> : s.label}</li>)}</ul>
  </Item>
)

const PhotoOverlay = ({ photo, overlay, alt, caption }) => {
  const [opacity, setOpacity] = useState(60)
  return (
    <Item as="figure" className="pv-figure">
      <a className="pv-photo-overlay" href={overlay} target="_blank" rel="noopener noreferrer" aria-label="Open the full overlay">
        <img src={photo} alt={alt} />
        <img src={overlay} alt="" style={{ opacity: opacity / 100 }} />
      </a>
      <label className="pv-range">
        <span>Overlay opacity</span>
        <Slider value={opacity} onChange={setOpacity} aria-label="Overlay opacity on the original photograph" />
        <span>{opacity}%</span>
      </label>
      <figcaption>{caption}</figcaption>
    </Item>
  )
}

const Block = ({ block, figures, brief }) => {
  if (typeof block === 'string') return <Item as="p">{block}</Item>
  if (block.h) return <Item as="h3">{block.h}</Item>
  if (block.facts) return <Facts rows={block.facts} />
  if (block.note) return <Item as="div" className="pv-note"><p>{block.note}</p></Item>
  if (block.palette) return <Palette colours={block.palette} />
  if (block.links) return <Links links={block.links} brief={brief} />
  if (block.downloads) return <Downloads files={block.downloads} />
  if (block.sources) return <Sources sources={block.sources} />
  if (block.figure) {
    // The picture itself is attached by the poster's loader; the data only names it.
    const src = figures?.[block.figure]
    if (!src) return null
    if (block.basePhoto && figures[block.basePhoto]) return (
      <PhotoOverlay photo={figures[block.basePhoto]} overlay={src} alt={block.alt} caption={block.caption} />
    )
    return (
      <Item as="figure" className="pv-figure">
        <a href={src} target="_blank" rel="noopener noreferrer"><img src={src} alt={block.alt} loading="lazy" /></a>
        <figcaption>{block.caption}</figcaption>
      </Item>
    )
  }
  return null
}

// A panel opens at a glance: its heading and lede, then what can be scanned (the first table of
// facts, the colours, a picture, links). The paragraphs, caveats and sources are one press away, and
// the choice is kept, so a reader who wants every panel in full asks once.
const FULL_KEY = 'pofbc-panel-full'
let full = (() => { try { return localStorage.getItem(FULL_KEY) === '1' } catch { return false } })()
const keepFull = (on) => { full = on; try { localStorage.setItem(FULL_KEY, on ? '1' : '0') } catch { /* private window */ } }

/**
 * One part's panel. On the overview it also lists the parts, as a table of contents, offers the
 * tour and any named recolouring (`variation`), and ends with the piece's connections from the
 * registry (`poster` is its id there).
 */
export function DataPanel({ partId, parts, order, onSelect, tour, story, poster, variation, compare, pages, figures, noun = 'poster' }) {
  const part = parts[partId]
  const { panel } = part
  const steps = order.filter((id) => id !== 'overview')
  const index = steps.indexOf(partId)
  const eyebrow = index >= 0 ? `Part ${index + 1} of ${steps.length} · ${panel.eyebrow}` : panel.eyebrow
  const [open, setOpen] = useState(full)
  const toggle = () => { keepFull(!open); setOpen(!open) }
  const all = panel.blocks ?? []
  const brief = glance(all)
  const blocks = open ? all : brief.kept
  // On the overview the contents come before the series links, which are the panel's last block.
  const tail = partId === 'overview' && blocks.findIndex((b) => b.h) >= 0 ? blocks.findIndex((b) => b.h) : blocks.length
  return (
    <Reveal>
      <Item as="p" className="pv-eyebrow">{eyebrow}</Item>
      <Item as="h2">{panel.heading}{panel.em && <>, <em>{panel.em}</em></>}</Item>
      <Item as="p" className="pv-lede">{panel.lede}</Item>
      {blocks.slice(0, tail).map((block, i) => <Block key={i} block={block} figures={figures} brief={!open} />)}
      {brief.held > 0 && (
        <Item as="div" className="pv-row pv-more">
          <button type="button" className="pv-ghost" aria-expanded={open} onClick={toggle}>{open ? 'Show less' : 'Read more'}</button>
        </Item>
      )}
      {partId === 'overview' && (
        <>
          {variation && (
            <Item as="div" className="pv-variation">
              <Segmented label={variation.label} options={variation.options.map(({ id, label }) => ({ value: id, label }))} value={variation.value} onChange={variation.onChange} />
              <p className="pv-muted">{variation.options.find(({ id }) => id === variation.value)?.note}</p>
            </Item>
          )}
          {compare && (
            <Item as="div" className="pv-variation">
              <Segmented
                label="Compare with the original"
                value={compare.mode}
                onChange={compare.onMode}
                options={[{ value: 'reconstruction', label: 'Reconstruction' }, { value: 'original', label: 'Original' }, { value: 'overlay', label: 'Overlay' }]}
              />
              {compare.mode === 'overlay' && (
                <label className="pv-range">
                  <span>Original</span>
                  <Slider min="0" max="1" step="0.05" value={compare.opacity} onChange={(value) => compare.onOpacity(value)} aria-label="How strongly the original shows over the reconstruction" />
                  <span>{Math.round(compare.opacity * 100)}%</span>
                </label>
              )}
              <p className="pv-muted">{compare.reference.caption} The two share one frame: open any part, and both zoom to it.</p>
            </Item>
          )}
          {pages && (
            <Item as="div" className="pv-row">
              <button type="button" className="pv-ghost pv-solid" onClick={pages.open}>Read it page by page</button>
              <span className="pv-muted">{pages.count} pages, with Home, Back and Next</span>
            </Item>
          )}
          {story && (
            <Item as="div" className="pv-row">
              <button type="button" className="pv-ghost pv-solid" onClick={story}>Read it as a story</button>
              <span className="pv-muted">Scroll, and the {noun} follows</span>
            </Item>
          )}
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
      {blocks.slice(tail).map((block, i) => <Block key={tail + i} block={block} figures={figures} brief={!open} />)}
      {partId === 'overview' && poster && <Connections poster={poster} brief={!open} />}
    </Reveal>
  )
}
