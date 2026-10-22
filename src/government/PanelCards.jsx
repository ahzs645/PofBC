// The panel's lists as cards, the way the model sets a department's sub-agencies, its appointments
// and who appoints it: a title with its count to the right, then a grid of bordered cards, each led
// by the body's own glyph in its branch's colour — a white ground, the colour at half strength over
// it, and an outline.

import { GLYPHS, KINDS } from './GovernmentGraph.jsx'

const BRANCH_INK = { legislative: 'var(--gov-legislative)', executive: 'var(--gov-executive)', judicial: 'var(--gov-judicial)' }

/** A body's glyph at text size, or a person's head and shoulders for `person`. */
export const KindIcon = ({ kind, branch = 'executive', person = false }) => {
  const ink = BRANCH_INK[branch] ?? BRANCH_INK.executive
  const layers = [
    { fill: 'var(--gov-surface)' },
    { fill: ink, fillOpacity: 0.5 },
    { fill: 'none', stroke: ink, strokeWidth: 1 }
  ]
  const glyph = KINDS[kind]?.glyph === 'dot' ? 'circle' : KINDS[kind]?.glyph ?? 'octagon'
  const size = glyph === 'circle' && kind === 'sub' ? 4.5 : 6.6
  return (
    <svg className="gov-cards__icon" viewBox="-10.5 -11 21 22" aria-hidden="true">
      {person
        ? layers.map((layer, index) => (
          <g key={index}>
            <rect x={-6.25} y={-3} width={12.5} height={10} rx={2.6} {...layer} />
            <circle cx={0} cy={-3} r={3.75} {...layer} />
          </g>
        ))
        : layers.map((layer, index) => <g key={index}>{GLYPHS[glyph](size, layer)}</g>)}
    </svg>
  )
}

/** A titled grid of cards, its count or other figure set to the right of the title. */
export const CardSection = ({ title, meta, children, footer }) => (
  <div className="gov-cards">
    <div className="gov-cards__head">
      <p className="gov-cards__title">{title}</p>
      {meta !== undefined && meta !== null && <p className="gov-cards__meta">{meta}</p>}
    </div>
    <div className="gov-cards__grid">{children}</div>
    {footer}
  </div>
)

/** One card: an icon, a name, and a line or two under it. A card with nowhere to go is not a button. */
export const Card = ({ icon, title, lines = [], onClick, aside, current }) => {
  const body = (
    <>
      <span className="gov-cards__lead">{icon}</span>
      <span className="gov-cards__text">
        <span className="gov-cards__name">{title}</span>
        {lines.filter(Boolean).map((line, index) => <span key={index} className="gov-cards__line">{line}</span>)}
      </span>
      {aside && <span className="gov-cards__aside">{aside}</span>}
    </>
  )
  return onClick
    ? <button type="button" className="gov-cards__card" aria-current={current ? 'true' : undefined} onClick={onClick}>{body}</button>
    : <div className="gov-cards__card gov-cards__card--still">{body}</div>
}
