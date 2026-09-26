// The year slider, and the century and a half behind it.
//
// Four strips read off the same axis: the identity the Province's lockups took (the generator's
// own four eras), the premier and their party, each general election, and how much the ministries
// were reorganised each year — which is what makes the years worth stopping at easy to find.

import { useMemo } from 'react'
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

export const TimelineBar = ({ year, onYear, playing, onPlay }) => {
  const maxChurn = useMemo(() => Math.max(...Object.values(CHURN)), [])
  const previous = [...EVENT_YEARS].reverse().find((candidate) => candidate < year)
  const next = EVENT_YEARS.find((candidate) => candidate > year)
  const decades = []
  for (let decade = Math.ceil(FIRST_YEAR / 10) * 10; decade <= PRESENT_YEAR; decade += 10) decades.push(decade)

  return (
    <div className="gov-timeline">
      <div className="gov-timeline__controls">
        <button type="button" className="gov-button" onClick={onPlay} aria-label={playing ? 'Pause' : 'Play through the years'} title={playing ? 'Pause' : 'Play through the years'}>
          {playing ? '❚❚' : '▶'}
        </button>
        <button type="button" className="gov-button" disabled={!previous} onClick={() => onYear(previous)} title={previous ? `Back to ${previous}` : undefined} aria-label="Previous change">‹</button>
        {/* Announced when it settles, not on every step of playback. */}
        <output className="gov-timeline__year" aria-live={playing ? 'off' : 'polite'}>{year}</output>
        <button type="button" className="gov-button" disabled={!next} onClick={() => onYear(next)} title={next ? `On to ${next}` : undefined} aria-label="Next change">›</button>
        <button type="button" className="gov-button gov-button--text" disabled={year === PRESENT_YEAR} onClick={() => onYear(PRESENT_YEAR)}>Today</button>
      </div>

      <div className="gov-timeline__track">
        <svg viewBox={`0 0 ${WIDTH} 78`} preserveAspectRatio="none" aria-hidden="true">
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
          {/* The year shown. */}
          <rect x={x(year) - 1} y={0} width={Math.max(2, x(1) - x(0))} height={64} className="gov-timeline__cursor" />
        </svg>
        <div className="gov-timeline__decades" aria-hidden="true">
          {decades.filter((decade) => decade % 20 === 0).map((decade) => (
            <span key={decade} style={{ left: `${(x(decade) / WIDTH) * 100}%` }}>{decade}</span>
          ))}
        </div>
        <input
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
      </ul>
    </div>
  )
}
