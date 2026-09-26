// The legend: what each shape and each line means, and a way to hide any of them.
//
// Built to the model's own legend — a 246px panel opening upwards from a "Legend" trigger, two
// groups under small capitals, each row a 16px swatch and a name, a click hiding that kind (the
// row fades, the trigger counts what is hidden, and a last row shows everything again). The
// swatches are the model's too: white shapes with a grey outline, not the branch colours, so the
// legend reads as a key to shape and line alone.

import { useEffect, useRef, useState } from 'react'

/** The rows, and which node kinds (or relations) each stands for. */
export const ENTITY_ROWS = [
  { id: 'offices', label: 'Offices of state', kinds: ['assembly', 'crown', 'premier'], swatch: 'circle' },
  { id: 'ministries', label: 'Ministries', kinds: ['ministry', 'central-agency'], swatch: 'square' },
  { id: 'heads', label: 'Ministers & heads', kinds: ['heads'], swatch: 'head' },
  { id: 'officers', label: 'Officers of the Legislature', kinds: ['officer'], swatch: 'diamond' },
  { id: 'crowns', label: 'Crown corporations', kinds: ['crown-corporation'], swatch: 'double' },
  { id: 'agencies', label: 'Agencies & boards', kinds: ['agency'], swatch: 'octagon' },
  { id: 'health', label: 'Health authorities', kinds: ['health-authority'], swatch: 'hexagon' },
  { id: 'courts', label: 'Courts & tribunals', kinds: ['court', 'tribunal'], swatch: 'pentagon' },
  { id: 'subs', label: 'Sub-agencies', kinds: ['sub'], swatch: 'subs' }
]

export const RELATION_ROWS = [
  { id: 'elects', label: 'Elects', swatch: 'elects' },
  { id: 'appoints', label: 'Appoints', swatch: 'appoints' },
  { id: 'confidence', label: 'Confidence', swatch: 'confidence' },
  { id: 'responsible', label: 'Answers for', swatch: 'responsible' },
  { id: 'part', label: 'Part of', swatch: 'part' },
  { id: 'partner', label: 'Partner of', swatch: 'partner' }
]

/** The model's legend inks, per theme. */
const CHROME = {
  light: { ink: '#6F6F7A', fill: '#FFFFFF' },
  dark: { ink: '#9B97A2', fill: '#211E1A' }
}

/** A 16×16 swatch for a kind of body, drawn as the model draws its own. */
const EntitySwatch = ({ shape, ink, fill, dashed = false }) => {
  const stroke = { fill, stroke: ink, strokeWidth: 1.2, ...(dashed ? { strokeDasharray: '2 1.6', opacity: 0.7 } : {}) }
  const shapes = {
    circle: <circle cx="8" cy="8" r="5.5" {...stroke} />,
    square: <rect x="2.5" y="2.5" width="11" height="11" rx="2.5" {...stroke} />,
    head: (
      <>
        <rect x="3" y="5.6" width="10" height="8.4" rx="2" {...stroke} />
        <circle cx="8" cy="5.6" r="3" {...stroke} />
      </>
    ),
    diamond: <rect x="4" y="4" width="8" height="8" rx="2" transform="rotate(45 8 8)" {...stroke} />,
    hexagon: <polygon points="8.00,2.00 13.20,5.00 13.20,11.00 8.00,14.00 2.80,11.00 2.80,5.00" {...stroke} />,
    pentagon: <polygon points="8.00,2.50 13.71,6.65 11.53,13.35 4.47,13.35 2.29,6.65" {...stroke} />,
    double: (
      <>
        <rect x="2.5" y="2.5" width="11" height="11" rx="2.5" {...stroke} />
        <rect x="5.2" y="5.2" width="5.6" height="5.6" rx="1.4" fill="none" stroke={ink} strokeWidth="1" />
      </>
    ),
    octagon: <polygon points="10.45,2.09 13.91,5.55 13.91,10.45 10.45,13.91 5.55,13.91 2.09,10.45 2.09,5.55 5.55,2.09" {...stroke} />,
    subs: (
      <>
        <rect x="2.2" y="8.2" width="4.4" height="4.4" rx="1.2" {...stroke} />
        <rect x="9.4" y="8.2" width="4.4" height="4.4" rx="1.2" {...stroke} />
        <rect x="5.8" y="2.8" width="4.4" height="4.4" rx="1.2" {...stroke} />
      </>
    )
  }
  return <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true">{shapes[shape]}</svg>
}

/** A 26×12 swatch for a kind of line, with its mark at the middle. */
const RelationSwatch = ({ shape, ink, fill }) => {
  const straight = <line x1="1" y1="6" x2="25" y2="6" stroke={ink} strokeWidth="1.2" />
  const curve = <path d="M1,8.5 Q13,2.5 25,8.5" fill="none" stroke={ink} strokeWidth="1.2" />
  const shapes = {
    elects: <>{straight}<path d="M9,2.8 L12.2,6 L9,9.2 Z M13,2.8 L16.2,6 L13,9.2 Z" fill={ink} /></>,
    appoints: <>{straight}<path d="M10.5,2.8 L16,6 L10.5,9.2 Z" fill={ink} /></>,
    confidence: <>{curve}<path d="M10.5,1.8 L16,5 L10.5,8.2 Z" fill={fill} stroke={ink} strokeWidth="1.1" /></>,
    responsible: <>{curve}<path d="M9.5,2.2 L12.3,5 L9.5,7.8 M13.5,2.2 L16.3,5 L13.5,7.8" fill="none" stroke={ink} strokeWidth="1.1" /></>,
    part: <line x1="1" y1="6" x2="25" y2="6" stroke={ink} strokeWidth="1.2" strokeDasharray="4 2" />,
    partner: <path d="M1,8.5 Q13,2.5 25,8.5" fill="none" stroke={ink} strokeWidth="1.2" strokeDasharray="1.5 3" />
  }
  return <svg width="26" height="12" viewBox="0 0 26 12" aria-hidden="true">{shapes[shape]}</svg>
}

const Row = ({ label, shown, onToggle, children }) => (
  <button
    type="button"
    className="gov-legend__row"
    aria-pressed={shown}
    title={`${shown ? 'Hide' : 'Show'} ${label.toLowerCase()}`}
    onClick={onToggle}
  >
    {children}
    <span>{label}</span>
  </button>
)

/**
 * @param {object} props
 * @param {Set<string>} props.hiddenKinds       Node kinds hidden, plus 'heads' for the head circles.
 * @param {Set<string>} props.hiddenRelations   Relation kinds whose lines are not drawn.
 * @param {(kinds: string[]) => void} props.onToggleKinds
 * @param {(relation: string) => void} props.onToggleRelation
 * @param {() => void} props.onReset
 * @param {string[]} props.present              Node kinds on the diagram this year.
 * @param {'light'|'dark'} props.themeName
 */
export const Legend = ({ hiddenKinds, hiddenRelations, onToggleKinds, onToggleRelation, onReset, present, themeName, includeUndated, onToggleUndated }) => {
  const [open, setOpen] = useState(false)
  const root = useRef(null)
  const { ink, fill } = CHROME[themeName] ?? CHROME.light

  // Closes on Escape, or a click anywhere else.
  useEffect(() => {
    if (!open) return undefined
    const away = (event) => { if (!root.current?.contains(event.target)) setOpen(false) }
    const escape = (event) => { if (event.key === 'Escape') setOpen(false) }
    document.addEventListener('pointerdown', away)
    document.addEventListener('keydown', escape)
    return () => {
      document.removeEventListener('pointerdown', away)
      document.removeEventListener('keydown', escape)
    }
  }, [open])

  const rows = ENTITY_ROWS.filter((row) => row.kinds.some((kind) => kind === 'heads' || present.includes(kind)))
  const hiddenRows = rows.filter((row) => row.kinds.every((kind) => hiddenKinds.has(kind))).length + hiddenRelations.size

  return (
    <div className="gov-legend" ref={root}>
      {open && (
        <div className="gov-legend__panel" role="group" aria-label="Legend">
          <p className="gov-legend__heading">Bodies</p>
          {rows.map((row) => (
            <Row
              key={row.id}
              label={row.label}
              shown={!row.kinds.every((kind) => hiddenKinds.has(kind))}
              onToggle={() => onToggleKinds(row.kinds)}
            >
              <EntitySwatch shape={row.swatch} ink={ink} fill={fill} />
            </Row>
          ))}
          <p className="gov-legend__heading">Relationships</p>
          {RELATION_ROWS.map((row) => (
            <Row key={row.id} label={row.label} shown={!hiddenRelations.has(row.id)} onToggle={() => onToggleRelation(row.id)}>
              <RelationSwatch shape={row.swatch} ink={ink} fill={fill} />
            </Row>
          ))}
          <p className="gov-legend__heading">Evidence</p>
          <Row label="Undated bodies" shown={Boolean(includeUndated)} onToggle={onToggleUndated}>
            <EntitySwatch shape="square" ink={ink} fill={fill} dashed />
          </Row>
          <p className="gov-legend__hint">
            Bodies whose start no source gives, drawn faint before today: an unknown start is not a
            sign they did not exist.
          </p>
          {hiddenRows > 0 && (
            <button type="button" className="gov-legend__reset" onClick={onReset}>Show all</button>
          )}
        </div>
      )}
      <button type="button" className="gov-button gov-legend__trigger" aria-expanded={open} onClick={() => setOpen((value) => !value)}>
        Legend{hiddenRows ? <span className="gov-muted"> · {hiddenRows} hidden</span> : null}
        <svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true" style={{ transform: open ? 'rotate(180deg)' : undefined }}>
          <path d="M2.5 4.5 6 8l3.5-3.5" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>
    </div>
  )
}
