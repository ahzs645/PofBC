// The year slider, and the century and a half behind it.
//
// Four strips read off the same axis: the identity the Province's lockups took (the generator's
// own four eras), the premier and their party, each general election, and how much the ministries
// were reorganised each year — which is what makes the years worth stopping at easy to find.
//
// With a body chosen, a fifth strip follows it: when it stood (dashed where its start is unknown)
// and a mark for each dated event in its history, and the arrows step through that history rather
// than through the whole government's.

import { useMemo, useRef } from 'react'
import { changesIn } from './episodes.js'
import { FIRST_YEAR, PRESENT_YEAR } from './snapshot.js'
import { ELECTIONS, IDENTITY_ERAS, PENDING_ELECTION, PREMIERS } from './timelineData.js'
import { partyColour } from './theme.js'

const WIDTH = 1000
const PAD = 8
const x = (year) => PAD + ((year - FIRST_YEAR) / (PRESENT_YEAR + 1 - FIRST_YEAR)) * (WIDTH - PAD * 2)
const yearOf = (day) => Number(String(day).slice(0, 4)) + (Number(String(day).slice(5, 7) || 7) - 1) / 12

/** How many ministries began or ended in each year: the bar under the axis. */
const CHURN = (() => {
  const counts = {}
  for (let year = FIRST_YEAR; year <= PRESENT_YEAR; year += 1) {
    counts[year] = changesIn(year).reduce((sum, change) => sum + change.predecessors.length + change.successors.length, 0)
  }
  return counts
})()

/** The years anything happened: a reorganisation, a new premier, or an election. */
export const EVENT_YEARS = (() => {
  const years = new Set()
  for (const [year, count] of Object.entries(CHURN)) if (count) years.add(Number(year))
  for (const premier of PREMIERS) years.add(Number(premier.from.slice(0, 4)))
  for (const election of ELECTIONS) years.add(Number(String(election.date).slice(0, 4)))
  return [...years].filter((year) => year >= FIRST_YEAR && year <= PRESENT_YEAR).sort((a, b) => a - b)
})()

const ERA_SHADES = { historical: '#6b8f71', flag: '#c8411f', crest: '#57534e', current: '#2f5f9e' }

/** The years in a body's life worth stopping at, each with what happened then. */
const stopsOf = (life) => {
  const stops = new Map()
  const note = (value, label) => {
    const at = Number(String(value).slice(0, 4))
    if (!Number.isFinite(at) || at < FIRST_YEAR || at > PRESENT_YEAR) return
    stops.set(at, [...(stops.get(at) ?? []), label])
  }
  if (life.from) note(life.from, 'began')
  if (life.to) note(life.to, 'ended')
  for (const event of life.events) note(event.date.start, event.title)
  return [...stops.entries()].sort((a, b) => a[0] - b[0])
}

/**
 * @param {object} props
 * @param {object|null} [props.life]  The chosen body's life (snapshot.js lifeOf), to follow.
 */
export const TimelineBar = ({ year, onYear, playing, onPlay, life = null }) => {
  const maxChurn = useMemo(() => Math.max(...Object.values(CHURN)), [])
  const stops = useMemo(() => (life ? stopsOf(life) : []), [life])
  // A body is followed once chosen; the arrows step through its history when it has one.
  const following = Boolean(life)
  const stepping = stops.length > 0
  const stepYears = stepping ? stops.map(([at]) => at) : EVENT_YEARS
  const previous = [...stepYears].reverse().find((candidate) => candidate < year)
  const next = stepYears.find((candidate) => candidate > year)
  const whatIn = (at) => (stepping ? stops.find(([candidate]) => candidate === at)?.[1].join('; ') : null)
  const stepTitle = (at, word) => at && `${word} ${at}${whatIn(at) ? ` — ${whatIn(at)}` : ''}`
  const height = following ? 90 : 78
  const start = life?.from ? yearOf(life.from) : null
  const end = life?.to ? yearOf(life.to) : PRESENT_YEAR + 1
  const decades = []
  const track = useRef(null)
  const input = useRef(null)
  const drag = useRef(null)

  // The track is scrubbed by pointer rather than by the range input under it: iOS moves a range only
  // by its thumb, and this thumb is invisible. A mouse sets the year where it presses; a finger only
  // once it moves sideways or lifts without moving, so a swipe up the page does not change the year.
  const scrub = (event) => {
    const box = track.current.getBoundingClientRect()
    const units = ((event.clientX - box.left) / box.width) * WIDTH
    const at = FIRST_YEAR + Math.floor(((units - PAD) / (WIDTH - PAD * 2)) * (PRESENT_YEAR + 1 - FIRST_YEAR))
    onYear(Math.min(PRESENT_YEAR, Math.max(FIRST_YEAR, at)))
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
  for (let decade = Math.ceil(FIRST_YEAR / 10) * 10; decade <= PRESENT_YEAR; decade += 10) decades.push(decade)

  return (
    <div className="gov-timeline">
      <div className="gov-timeline__controls">
        <button type="button" className="gov-button" onClick={onPlay} aria-label={playing ? 'Pause' : 'Play through the years'} title={playing ? 'Pause' : 'Play through the years'}>
          {playing ? '❚❚' : '▶'}
        </button>
        <button type="button" className="gov-button" disabled={!previous} onClick={() => onYear(previous)} title={stepTitle(previous, 'Back to')} aria-label={stepping ? `Previous in ${life.name ?? 'its'} history` : 'Previous change'}>‹</button>
        {/* Announced when it settles, not on every step of playback. */}
        <output className="gov-timeline__year" aria-live={playing ? 'off' : 'polite'}>{year}</output>
        <button type="button" className="gov-button" disabled={!next} onClick={() => onYear(next)} title={stepTitle(next, 'On to')} aria-label={stepping ? `Next in ${life.name ?? 'its'} history` : 'Next change'}>›</button>
        <button type="button" className="gov-button gov-button--text" disabled={year === PRESENT_YEAR} onClick={() => onYear(PRESENT_YEAR)}>Today</button>
      </div>

      <div
        ref={track}
        className="gov-timeline__track"
        data-following={following || undefined}
        onPointerDown={press}
        onPointerMove={slide}
        onPointerUp={release}
        onPointerCancel={() => { drag.current = null }}
      >
        <svg viewBox={`0 0 ${WIDTH} ${height}`} preserveAspectRatio="none" aria-hidden="true">
          {/* The identity of the day, which is the lockup a ministry chosen that year is shown in. */}
          {IDENTITY_ERAS.map((era) => (
            <g key={era.era}>
              <rect x={x(era.from)} y={2} width={x(era.to ?? PRESENT_YEAR + 1) - x(era.from)} height={10} fill={ERA_SHADES[era.era]} fillOpacity={era.confidence === 'low' ? 0.35 : 0.8} rx={2}>
                <title>{era.label} identity, {era.from}–{era.to ?? 'today'}</title>
              </rect>
            </g>
          ))}
          {/* Premiers, by party. */}
          {PREMIERS.map((premier) => (
            <rect
              key={`${premier.name}-${premier.from}`}
              x={x(yearOf(premier.from))}
              y={16}
              width={Math.max(1.2, x(premier.to ? yearOf(premier.to) : PRESENT_YEAR + 0.75) - x(yearOf(premier.from)) - 0.8)}
              height={12}
              fill={partyColour(premier.party)}
              rx={1.5}
            >
              <title>{premier.name} ({premier.party})</title>
            </rect>
          ))}
          {/* Elections, and the one under way. */}
          {ELECTIONS.map((election) => (
            <rect key={election.parliament} x={x(yearOf(election.date)) - 0.8} y={32} width={1.6} height={8} className="gov-timeline__tick" />
          ))}
          {PENDING_ELECTION && (
            <rect x={x(yearOf(PENDING_ELECTION.date)) - 0.8} y={32} width={1.6} height={8} className="gov-timeline__tick" strokeDasharray="1 1" opacity={0.5} />
          )}
          {/* How much the ministries changed. */}
          {Object.entries(CHURN).map(([churnYear, count]) => count > 0 && (
            <rect
              key={churnYear}
              x={x(Number(churnYear)) + 0.3}
              y={62 - (count / maxChurn) * 18}
              width={Math.max(1, x(1) - x(0) - 0.6)}
              height={(count / maxChurn) * 18}
              className="gov-timeline__churn"
            />
          ))}
          <line x1={PAD} x2={WIDTH - PAD} y1={62.5} y2={62.5} className="gov-timeline__axis" />
          {/* The chosen body: when it stood, and each dated event in its history. */}
          {following && (
            <g>
              {start !== null
                ? <rect x={x(start)} y={71} width={Math.max(1.5, x(end) - x(start))} height={6} rx={1.5} className="gov-timeline__life" />
                : <line x1={PAD} x2={x(end)} y1={74} y2={74} className="gov-timeline__life-unknown" />}
              {stops.map(([at, labels]) => (
                <rect key={at} x={x(at) + 0.2} y={67} width={Math.max(1.4, x(1) - x(0) - 0.4)} height={14} rx={0.8} className="gov-timeline__stop">
                  <title>{at}: {labels.join('; ')}</title>
                </rect>
              ))}
            </g>
          )}
          {/* The year shown. */}
          <rect x={x(year) - 1} y={0} width={Math.max(2, x(1) - x(0))} height={following ? height - 2 : 64} className="gov-timeline__cursor" />
        </svg>
        <div className="gov-timeline__decades" aria-hidden="true">
          {decades.filter((decade) => decade % 20 === 0).map((decade) => (
            <span key={decade} style={{ left: `${(x(decade) / WIDTH) * 100}%` }}>{decade}</span>
          ))}
        </div>
        <input
          ref={input}
          type="range"
          className="gov-timeline__range"
          min={FIRST_YEAR}
          max={PRESENT_YEAR}
          step={1}
          value={year}
          onChange={(event) => onYear(Number(event.target.value))}
          aria-label="Year"
          aria-valuetext={`${year}`}
        />
      </div>

      <ul className="gov-timeline__key" aria-label="What the strips show">
        <li>
          <span className="gov-timeline__swatch" style={{ background: `linear-gradient(90deg, ${IDENTITY_ERAS.map((era) => ERA_SHADES[era.era]).join(', ')})` }} />
          Identity in use: {IDENTITY_ERAS.map((era) => era.label).join(', ')}
        </li>
        <li><span className="gov-timeline__swatch" style={{ background: partyColour('NDP') }} />Premier, by party</li>
        <li><span className="gov-timeline__swatch gov-timeline__swatch--tick" />Election</li>
        <li><span className="gov-timeline__swatch gov-timeline__swatch--churn" />Ministries reorganised</li>
        {following && (
          <li>
            <span className="gov-timeline__swatch gov-timeline__swatch--life" />
            {life.name ?? 'The chosen body'}: {life.from ? 'when it stood' : 'start unknown'}
            {stepping
              ? <>, and {stops.length} {stops.length === 1 ? 'year' : 'years'} with a dated event — the arrows step through them</>
              : <>; no dated events yet</>}
          </li>
        )}
      </ul>
    </div>
  )
}
