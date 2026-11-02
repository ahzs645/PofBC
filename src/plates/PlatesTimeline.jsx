// The plates' timelines, after the government view's year bar (src/government/TimelineBar.jsx).
//
// YearTimeline is the index's "By year" mode: one strip per family on a shared axis from the first
// bicycle plate to today, each design a bar across the years it was issued or valid, with a cursor
// that is scrubbed, played or stepped from one change to the next. With one family chosen, its
// designs get a lane each, so the strip reads design by design. The plates in use in the chosen
// year are listed under it (PlatesView).
//
// FamilyStrip is the viewer's: the open plate's family in lanes, the open plate marked, and any
// other bar a click away.

import { useEffect, useMemo, useRef } from 'react'
import { changeYears, inUse, lanesOf, spanOf } from './timeline.js'

const WIDTH = 1000
const PAD = 6

const axis = ([first, last]) => (year) => PAD + ((year - first) / (last + 1 - first)) * (WIDTH - PAD * 2)

const Decades = ({ span, x, every }) => {
  const decades = []
  for (let decade = Math.ceil(span[0] / every) * every; decade <= span[1]; decade += every) decades.push(decade)
  return (
    <div className="plates-timeline__decades" aria-hidden="true">
      {decades.map((decade) => <span key={decade} style={{ left: `${(x(decade) / WIDTH) * 100}%` }}>{decade}</span>)}
    </div>
  )
}

const Bar = ({ x, format, y, height, className, onClick }) => (
  <rect
    x={x(format.period[0]) + 0.4}
    y={y}
    width={Math.max(2, x(format.period[1] + 1) - x(format.period[0]) - 0.8)}
    height={height}
    rx={Math.min(2, height / 2)}
    className={className}
    onClick={onClick}
  >
    <title>{format.label}, {format.period[0] === format.period[1] ? format.period[0] : `${format.period[0]}–${format.period[1]}`}</title>
  </rect>
)

/**
 * @param {object} props
 * @param {Array<{ id: string, label: string, formats: object[] }>} props.rows  A strip each: the families,
 *        or one family's lanes.
 * @param {[number, number]} props.span
 * @param {number} props.year
 * @param {(year: number) => void} props.onYear
 * @param {boolean} props.playing
 * @param {() => void} props.onPlay
 * @param {(id: string) => void} [props.onRow]  A row's label, chosen (the family, to follow it).
 * @param {string} [props.note]  What the strips show, under them.
 */
export const YearTimeline = ({ rows, span, year, onYear, playing, onPlay, onRow, note }) => {
  const x = useMemo(() => axis(span), [span])
  const ROW = 14
  const height = rows.length * ROW + 2
  const stops = useMemo(() => changeYears(rows.flatMap((row) => row.formats), span), [rows, span])
  const previous = [...stops].reverse().find((candidate) => candidate < year)
  const next = stops.find((candidate) => candidate > year)
  const track = useRef(null)
  const input = useRef(null)
  const drag = useRef(null)

  // Scrubbed by pointer, as the government's bar is: a mouse sets the year where it presses, a finger
  // only once it moves sideways, so a swipe up the page does not change the year.
  const scrub = (event) => {
    const box = track.current.getBoundingClientRect()
    const units = ((event.clientX - box.left) / box.width) * WIDTH
    const at = span[0] + Math.floor(((units - PAD) / (WIDTH - PAD * 2)) * (span[1] + 1 - span[0]))
    onYear(Math.min(span[1], Math.max(span[0], at)))
  }
  const press = (event) => {
    if (event.button !== 0) return
    drag.current = { id: event.pointerId, x: event.clientX, y: event.clientY, sliding: event.pointerType === 'mouse' }
    if (event.pointerType === 'mouse') {
      event.preventDefault()
      input.current?.focus({ preventScroll: true })
      event.currentTarget.setPointerCapture(event.pointerId)
      scrub(event)
    }
  }
  const slide = (event) => {
    const current = drag.current
    if (current?.id !== event.pointerId) return
    if (!current.sliding) {
      const dx = Math.abs(event.clientX - current.x)
      if (dx < 6 || dx < Math.abs(event.clientY - current.y)) return
      current.sliding = true
      event.currentTarget.setPointerCapture(event.pointerId)
    }
    scrub(event)
  }
  const release = (event) => {
    if (drag.current?.id === event.pointerId) scrub(event)
    drag.current = null
  }

  return (
    <div className="plates-timeline">
      <div className="plates-timeline__controls">
        <button type="button" className="button plates-timeline__button" onClick={onPlay} aria-label={playing ? 'Pause' : 'Play through the years'} title={playing ? 'Pause' : 'Play through the years'}>
          {playing ? '❚❚' : '▶'}
        </button>
        <button type="button" className="button plates-timeline__button" disabled={previous === undefined} onClick={() => onYear(previous)} title={previous && `Back to ${previous}`} aria-label="Previous change">‹</button>
        <output className="plates-timeline__year" aria-live={playing ? 'off' : 'polite'}>{year}</output>
        <button type="button" className="button plates-timeline__button" disabled={next === undefined} onClick={() => onYear(next)} title={next && `On to ${next}`} aria-label="Next change">›</button>
        <button type="button" className="button plates-timeline__button plates-timeline__button--text" disabled={year === span[1]} onClick={() => onYear(span[1])}>Today</button>
      </div>

      <div className="plates-timeline__body" data-labelled={rows.some((row) => row.label) || undefined} style={{ '--row': `${ROW}px` }}>
        <ul className="plates-timeline__labels" hidden={!rows.some((row) => row.label)}>
          {rows.map((row) => (
            <li key={row.id}>
              {onRow && row.label
                ? <button type="button" onClick={() => onRow(row.id)} title={`Follow ${row.label}`}>{row.label}</button>
                : <span>{row.label}</span>}
            </li>
          ))}
        </ul>
        <div
          ref={track}
          className="plates-timeline__track"
          onPointerDown={press}
          onPointerMove={slide}
          onPointerUp={release}
          onPointerCancel={() => { drag.current = null }}
        >
          <svg viewBox={`0 0 ${WIDTH} ${height}`} preserveAspectRatio="none" style={{ height }} aria-hidden="true">
            {rows.map((row, index) => (
              <g key={row.id}>
                {index > 0 && <line x1={PAD} x2={WIDTH - PAD} y1={index * ROW + 0.5} y2={index * ROW + 0.5} className="plates-timeline__rule" />}
                {row.formats.map((format) => (
                  <Bar key={format.id} x={x} format={format} y={index * ROW + 3} height={ROW - 5}
                    className={inUse(format, year) ? 'plates-timeline__bar plates-timeline__bar--on' : 'plates-timeline__bar'} />
                ))}
              </g>
            ))}
            <rect x={x(year)} y={0} width={Math.max(2, x(span[0] + 1) - x(span[0]))} height={height} className="plates-timeline__cursor" />
          </svg>
          <Decades span={span} x={x} every={20} />
          <input
            ref={input}
            type="range"
            className="plates-timeline__range"
            min={span[0]}
            max={span[1]}
            step={1}
            value={year}
            onChange={(event) => onYear(Number(event.target.value))}
            aria-label="Year"
            aria-valuetext={`${year}`}
          />
        </div>
      </div>
      {note && <p className="plates-timeline__note">{note}</p>}
    </div>
  )
}

/**
 * The open plate's family as lanes, the plate itself marked; another bar opens that plate.
 *
 * @param {object} props
 * @param {object[]} props.formats  The family's designs.
 * @param {object} props.current    The open design.
 * @param {(format: object) => void} props.onOpen
 */
export const FamilyStrip = ({ formats, current, onOpen }) => {
  const span = useMemo(() => spanOf(formats), [formats])
  const lanes = useMemo(() => lanesOf(formats), [formats])
  const x = useMemo(() => axis(span), [span])
  const LANE = 10
  const height = lanes.length * LANE + 2
  const strip = useRef(null)
  // The open plate's bar stays in view when the strip scrolls (a phone, a long family).
  useEffect(() => { strip.current?.querySelector('[data-current]')?.scrollIntoView?.({ block: 'nearest', inline: 'center' }) }, [current])
  return (
    <div className="plates-strip" ref={strip}>
      <div className="plates-strip__track">
        <svg viewBox={`0 0 ${WIDTH} ${height}`} preserveAspectRatio="none" style={{ height }} aria-hidden="true">
          {lanes.map((lane, index) => lane.map((format) => (
            <g key={format.id} data-current={format === current || undefined}>
              <Bar x={x} format={format} y={index * LANE + 2} height={LANE - 3}
                className={format === current ? 'plates-strip__bar plates-strip__bar--current' : 'plates-strip__bar'}
                onClick={format === current ? undefined : () => onOpen(format)} />
            </g>
          )))}
        </svg>
        <Decades span={span} x={x} every={span[1] - span[0] > 60 ? 20 : 10} />
      </div>
    </div>
  )
}
