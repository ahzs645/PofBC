// The atlas's explanatory cards: what happened to a body and when, why each thing on screen is
// shown, what an election is waiting on, what changed between two years, and how much of the
// record is actually known.
//
// They follow the rules the 2026-09-25 research package sets out: a date is shown at the precision
// its source gives; a scheduled event is labelled as scheduled; every claim links to its source,
// and what only the present records says when it was checked; an unknown is reported as unknown.

import { useMemo, useState } from 'react'
import { compareYears } from './compare.js'
import { EVENT_SOURCES, formatEventDate, isAhead, typeOf } from './events.js'
import { MINISTRY_EPISODES, standsIn } from './episodes.js'
import { governmentIn, PRESENT_YEAR, FIRST_YEAR } from './snapshot.js'
import { HISTORICAL_BODIES, MINISTERS, SUB_AGENCIES } from './historyData.js'

const hostOf = (url) => {
  try { return new URL(url).hostname.replace(/^www\d?\./, '') } catch { return url }
}

const SourceLink = ({ source }) => source?.url
  ? <a className="gov-source-link" href={source.url} target="_blank" rel="noreferrer">{source.title ?? hostOf(source.url)}</a>
  : null

// ── Origins and changes ──────────────────────────────────────────────────────────────────────────

/**
 * A body's dated events, oldest first: where its function began, when it was established, what it
 * was called, what it looked like, who led it. Each is its own kind of event, so a 1912 origin is
 * never mistaken for the date of today's name or logo.
 */
export const EventsCard = ({ events, day, title = 'Origins and changes' }) => {
  if (!events?.length) return null
  return (
    <section className="gov-card">
      <h2 className="gov-card__heading">{title} <span className="gov-muted">{events.length}</span></h2>
      <ol className="gov-events">
        {events.map((event) => {
          const type = typeOf(event)
          const ahead = isAhead(event, day)
          return (
            <li key={event.id} className="gov-events__item" data-kind={type.kind} data-ahead={ahead || undefined}>
              <span className="gov-events__date">{formatEventDate(event.date)}</span>
              <span className="gov-events__body">
                <span className="gov-events__type">
                  {type.label}
                  {event.status !== 'source_reported_past' && <span className="gov-chip" data-type="scheduled">{event.status === 'planned' ? 'Planned' : 'Scheduled'}</span>}
                </span>
                <span className="gov-events__title">{event.title}</span>
                {event.notes && <span className="gov-events__note">{event.notes}</span>}
                <span className="gov-events__sources">
                  {event.sources.map((index) => <SourceLink key={index} source={EVENT_SOURCES[index]} />)}
                  {event.locator && <span className="gov-muted"> · {String(event.locator)}</span>}
                </span>
              </span>
            </li>
          )
        })}
      </ol>
    </section>
  )
}

// ── Evidence ─────────────────────────────────────────────────────────────────────────────────────

/** Why this body is drawn as it is: each claim, the source that makes it, and when it was checked. */
export const EvidenceCard = ({ node }) => {
  const [open, setOpen] = useState(false)
  const claims = node.evidence ?? []
  const caveats = [
    node.unattached && !node.uncertain && 'Existed in this period — its responsible ministry is not yet established in the sources.',
    node.uncertain && 'Existence in this year is unknown: no source gives when it began. Shown because “Undated bodies” is on.'
  ].filter(Boolean)
  if (!claims.length && !caveats.length) return null
  return (
    <section className="gov-card gov-evidence">
      <button type="button" className="gov-evidence__toggle" aria-expanded={open} onClick={() => setOpen((value) => !value)}>
        <span className="gov-card__heading">Evidence <span className="gov-muted">{claims.length} {claims.length === 1 ? 'claim' : 'claims'}</span></span>
        <span aria-hidden="true">{open ? '−' : '+'}</span>
      </button>
      {caveats.map((text) => <p key={text} className="gov-notice">{text}</p>)}
      {open && (
        <ul className="gov-evidence__list">
          {claims.map((entry, index) => (
            <li key={index}>
              <span>{entry.claim}</span>
              <span className="gov-muted">
                <SourceLink source={entry.source} />
                {entry.checked && ` · checked ${entry.checked}`}
                {entry.note && ` · ${entry.note}`}
              </span>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

// ── An election, stage by stage ─────────────────────────────────────────────────────────────────

/**
 * The election's milestones on the day shown: which have passed and which is next. Results are not
 * shown until they are published, and a new cabinet is not assumed on voting day.
 */
export const ElectionStages = ({ stages }) => {
  if (!stages?.length) return null
  return (
    <div className="gov-stages">
      <h3 className="gov-card__subheading">2026 general election</h3>
      <ol>
        {stages.map((stage) => (
          <li key={stage.id} data-state={stage.next ? 'next' : stage.ahead ? 'ahead' : 'done'}>
            <span className="gov-stages__dot" aria-hidden="true" />
            <span className="gov-stages__label">{typeOf(stage).label}</span>
            <span className="gov-muted">{formatEventDate(stage.date)}{stage.ahead ? (stage.status === 'planned' ? ' · planned' : ' · scheduled') : ''}</span>
          </li>
        ))}
      </ol>
      <p className="gov-muted gov-stages__note">Results will be added when Elections BC publishes them, and a new cabinet only when it is sworn in.</p>
    </div>
  )
}

// ── Compare two years ────────────────────────────────────────────────────────────────────────────

const Names = ({ nodes, onPick }) => (
  <ul className="gov-compare__names">
    {nodes.map((node) => (
      <li key={node.id}><button type="button" className="gov-link-button" onClick={() => onPick(node)}>{node.shortName ?? node.name}</button></li>
    ))}
  </ul>
)

/**
 * Two years side by side, as an account of what changed. Choosing a name goes to it in the year it
 * stood.
 */
export const CompareView = ({ year, other, onOther, onPick }) => {
  const result = useMemo(() => compareYears(other, year), [other, year])
  const { from, to } = result
  const pick = (node, at) => onPick(node, at)
  const years = []
  for (let value = PRESENT_YEAR; value >= FIRST_YEAR; value -= 1) years.push(value)

  return (
    <div className="gov-compare">
      <section className="gov-list__section gov-compare__head">
        <h2 className="gov-list__title">Compare</h2>
        <p className="gov-compare__pick">
          <label>
            <span className="gov-muted">From </span>
            <select value={other} onChange={(event) => onOther(Number(event.target.value))}>
              {years.map((value) => <option key={value} value={value}>{value}</option>)}
            </select>
          </label>
          <span className="gov-muted"> to the year on the timeline, </span><strong>{year}</strong>
        </p>
        <p className="gov-muted">
          {result.ministries.before} ministries in {from}, {result.ministries.after} in {to} · {result.ministries.continuing} unchanged ·
          {' '}{result.bodies.before} other bodies then, {result.bodies.after} now · {result.subAgencies.before} → {result.subAgencies.after} sub-agencies on record
        </p>
      </section>

      {result.offices.length > 0 && (
        <section className="gov-list__section">
          <h3 className="gov-list__title">Office-holders</h3>
          <ul className="gov-compare__rows">
            {result.offices.map((office) => (
              <li key={office.label}><span>{office.label}</span><span className="gov-muted">{office.a ?? 'vacant or unknown'} → {office.b ?? 'vacant or unknown'}</span></li>
            ))}
            {result.ministers.map(({ node, a, b }) => (
              <li key={node.id}><span>{node.name.replace(/^Ministry of /, '')}</span><span className="gov-muted">{a} → {b}</span></li>
            ))}
          </ul>
        </section>
      )}

      <section className="gov-list__section">
        <h3 className="gov-list__title">Ministries that became others <span className="gov-muted">{result.ministries.transformed.length}</span></h3>
        <ul className="gov-compare__rows">
          {result.ministries.transformed.map(({ from: node, into, byName }) => (
            <li key={node.id}>
              <button type="button" className="gov-link-button" onClick={() => pick(node, from)}>{node.name.replace(/^Ministry of /, '')}</button>
              <span className="gov-muted"> → {into.map((episode) => episode.name.replace(/^Ministry of /, '')).join(', ')}{byName ? ' · a similar name; lineage not recorded' : ''}</span>
            </li>
          ))}
        </ul>
      </section>

      <div className="gov-compare__pair">
        <section className="gov-list__section">
          <h3 className="gov-list__title">Began after {from} <span className="gov-muted">{result.ministries.created.length}</span></h3>
          <Names nodes={result.ministries.created} onPick={(node) => pick(node, to)} />
        </section>
        <section className="gov-list__section">
          <h3 className="gov-list__title">Ended by {to} <span className="gov-muted">{result.ministries.ended.length}</span></h3>
          <Names nodes={result.ministries.ended} onPick={(node) => pick(node, from)} />
        </section>
      </div>

      <div className="gov-compare__pair">
        <section className="gov-list__section">
          <h3 className="gov-list__title">Bodies that appeared <span className="gov-muted">{result.bodies.appeared.length}</span></h3>
          <Names nodes={result.bodies.appeared} onPick={(node) => pick(node, to)} />
        </section>
        <section className="gov-list__section">
          <h3 className="gov-list__title">Bodies that closed <span className="gov-muted">{result.bodies.closed.length}</span></h3>
          <Names nodes={result.bodies.closed} onPick={(node) => pick(node, from)} />
        </section>
      </div>

      {result.bodies.moved.length > 0 && (
        <section className="gov-list__section">
          <h3 className="gov-list__title">Answered to a different ministry <span className="gov-muted">{result.bodies.moved.length}</span></h3>
          <ul className="gov-compare__rows">
            {result.bodies.moved.map(({ node, from: was, to: now }) => (
              <li key={node.id}>
                <button type="button" className="gov-link-button" onClick={() => pick(node, to)}>{node.shortName ?? node.name}</button>
                <span className="gov-muted"> {was?.replace(/^Ministry of /, '')} → {now?.replace(/^Ministry of /, '')}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {result.events.length > 0 && (
        <EventsCard events={result.events} day={`${to}-12-31`} title={`Dated events, ${from + 1}–${to}`} />
      )}
    </div>
  )
}

// ── Coverage ─────────────────────────────────────────────────────────────────────────────────────

/**
 * How much of the record is known, each figure with its denominator. Organizations are counted apart
 * from their episodes, and people apart from their terms; a year-sampled figure says so.
 */
const measureCoverage = () => {
  let ministryYears = 0
  let ministryYearsLed = 0
  let bodyYears = 0
  let bodyYearsStated = 0
  let bodyYearsInferred = 0
  for (let year = FIRST_YEAR + 1; year < PRESENT_YEAR; year += 1) {
    const government = governmentIn(year)
    for (const node of government.nodes) {
      if (node.kind === 'ministry') {
        ministryYears += 1
        if (node.head?.person) ministryYearsLed += 1
      } else if (node.ring === 'outer' && node.kind !== 'court') {
        bodyYears += 1
        if (node.group && !node.inferredGroup) bodyYearsStated += 1
        else if (node.group) bodyYearsInferred += 1
      }
    }
  }
  const bodies = HISTORICAL_BODIES.filter((body) => body.name)
  const terms = Object.values(MINISTERS).flat()
  return [
    { label: 'Ministry-years with a minister on record', value: ministryYearsLed, of: ministryYears, note: 'each ministry counted once for each year it stood, 1872–2025' },
    { label: 'Body-years with a responsible ministry stated by a source', value: bodyYearsStated, of: bodyYears, note: `and ${bodyYearsInferred} more placed by inference` },
    { label: 'Bodies with a known start', value: bodies.filter((body) => body.established).length, of: bodies.length, note: 'unique bodies, not episodes' },
    { label: 'Sub-agencies with a known start', value: SUB_AGENCIES.filter((entry) => entry.established).length, of: SUB_AGENCIES.length, note: 'the rest appear only in the present' },
    { label: 'Ministry episodes with at least one minister matched', value: MINISTRY_EPISODES.filter((episode) => MINISTERS[episode.id]?.length).length, of: MINISTRY_EPISODES.length, note: `${terms.length} minister terms in all` },
    { label: 'Ministry episodes standing today', value: MINISTRY_EPISODES.filter((episode) => standsIn(episode, PRESENT_YEAR)).length, of: MINISTRY_EPISODES.length, note: 'for scale' }
  ]
}

export const CoverageCard = () => {
  const [rows, setRows] = useState(null)
  return (
    <div className="gov-coverage">
      <h3 className="gov-card__subheading">Coverage</h3>
      {!rows && <button type="button" className="gov-show-more" onClick={() => setRows(measureCoverage())}>Measure coverage</button>}
      {rows && (
        <ul>
          {rows.map((row) => (
            <li key={row.label}>
              <span className="gov-coverage__bar" style={{ '--share': `${(row.value / Math.max(1, row.of)) * 100}%` }} aria-hidden="true" />
              <span>{row.label}</span>
              <strong>{Math.round((row.value / Math.max(1, row.of)) * 100)}%</strong>
              <span className="gov-muted">{row.value.toLocaleString('en-CA')} of {row.of.toLocaleString('en-CA')} · {row.note}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

// ── Staffing ─────────────────────────────────────────────────────────────────────────────────────

/**
 * Full-time equivalents by fiscal year, as the Public Accounts' Statement of Staff Utilization gives
 * them: actual as bars, the budgeted figure as a tick where there is one. A ministry that was renamed
 * or reorganised has its figures under the name the statement printed, which the panel says, since
 * a reorganisation can break comparability even when a row keeps its name.
 */
export const StaffingCard = ({ rows, year }) => {
  const actual = (rows ?? []).filter((row) => row.basis === 'actual')
  if (!actual.length) return null
  const budget = new Map((rows ?? []).filter((row) => row.basis !== 'actual').map((row) => [row.fiscalYear, row.value]))
  const max = Math.max(...actual.map((row) => row.value), ...budget.values())
  const names = [...new Set(actual.map((row) => row.printedAs))]
  const latest = actual.at(-1)
  return (
    <section className="gov-card">
      <h2 className="gov-card__heading">Staff <span className="gov-muted">FTE, actual</span></h2>
      <div className="gov-staffing" role="img" aria-label={actual.map((row) => `${row.fiscalYear}: ${row.value}`).join(', ')}>
        {actual.map((row) => (
          <span
            key={row.fiscalYear}
            className="gov-staffing__bar"
            data-current={Number(row.fiscalYear.slice(0, 4)) === year || undefined}
            style={{ '--h': `${(row.value / max) * 100}%` }}
            title={`${row.fiscalYear}: ${row.value.toLocaleString('en-CA')} FTE actual${budget.has(row.fiscalYear) ? `, ${budget.get(row.fiscalYear).toLocaleString('en-CA')} budgeted` : ''} — as “${row.printedAs}”`}
          >
            {budget.has(row.fiscalYear) && <span className="gov-staffing__budget" style={{ '--r': budget.get(row.fiscalYear) / row.value }} />}
          </span>
        ))}
      </div>
      <p className="gov-muted gov-staffing__axis">
        <span>{actual[0].fiscalYear}</span>
        <span>{latest.fiscalYear}: {latest.value.toLocaleString('en-CA')} FTE</span>
      </p>
      <p className="gov-muted gov-staffing__note">
        Full-time equivalents paid directly from the Consolidated Revenue (later General) Fund, from the
        Public Accounts; not a headcount. {names.length > 1 ? `Printed under ${names.length} names over these years.` : ''}
        {' '}<SourceLink source={{ url: latest.source, title: 'Statement of Staff Utilization' }} />
      </p>
    </section>
  )
}

// ── The 43rd Parliament ─────────────────────────────────────────────────────────────────────────

const PARTY_SHORT = {
  'BC NDP': 'NDP',
  'Conservative Party of British Columbia': 'Conservative',
  'BC Green Party': 'Green'
}

/**
 * The Assembly's members as elected in 2024, with every later change dated. A member's party at
 * election is kept apart from where they sat later; where the Assembly's records and announced
 * affiliations differ (the Assembly lists OneBC and CentreBC members as Independent), both are shown.
 */
export const ParliamentCard = ({ parliament }) => {
  const [open, setOpen] = useState(false)
  if (!parliament?.seats?.length) return null
  const changed = parliament.seats.filter((seat) => seat.changes.length)
  const shown = open ? parliament.seats : changed
  const standings = parliament.standings?.assembly ?? {}
  return (
    <section className="gov-card">
      <h2 className="gov-card__heading">43rd Parliament <span className="gov-muted">{parliament.seats.length} seats</span></h2>
      <p className="gov-muted">Elected {parliament.elected}; dissolved {parliament.dissolved}. At dissolution, by the Assembly’s records:</p>
      <ul className="gov-standings">
        {Object.entries(standings).filter(([party]) => !['total_seats', 'members'].includes(party)).map(([party, count]) => (
          <li key={party}><strong>{count}</strong> {PARTY_SHORT[party] ?? party}</li>
        ))}
      </ul>
      <p className="gov-muted gov-standings__note">{parliament.standings?.note}</p>
      <h3 className="gov-card__subheading">{open ? 'Every seat' : `Seats that changed after the election`} <span className="gov-muted">{shown.length}</span></h3>
      <ul className="gov-seats-list">
        {shown.map((seat) => (
          <li key={seat.district}>
            <span className="gov-seats-list__who">
              <strong>{seat.member}</strong>
              <span className="gov-muted"> · {seat.district}</span>
            </span>
            <span className="gov-muted">Elected as {PARTY_SHORT[seat.partyAtElection] ?? seat.partyAtElection}{seat.share ? ` with ${seat.share}%` : ''}</span>
            {seat.changes.map((change, index) => (
              <span key={index} className="gov-seats-list__change">
                {change.date} · {change.change.replace(/_/g, ' ')}{change.to ? ` → ${change.to}` : ''}
                {change.status === 'conflicting' ? ' (sources conflict)' : ''}
                {change.source && <> · <SourceLink source={{ url: change.source }} /></>}
              </span>
            ))}
          </li>
        ))}
      </ul>
      <button type="button" className="gov-show-more" onClick={() => setOpen((value) => !value)}>{open ? 'Only seats that changed' : 'Every seat'}</button>
    </section>
  )
}

// ── Typed relations ─────────────────────────────────────────────────────────────────────────────

const RELATION_LABELS = {
  appoints_to: 'Appointed members',
  funded_by: 'Funded by',
  report_tabled_by: 'Report tabled by',
  regulated_by: 'Regulated by',
  statutory_reporting_to: 'Reports by statute to',
  budget_approval_recommended_by: 'Budget approval recommended by',
  audit_appointment_recommended_by: 'Auditor’s appointment recommended by',
  not_minister_responsible_for: 'Explicitly not responsible',
  designation_basis_statement: 'Basis of designation',
  complaints_and_referrals_via: 'Complaints and referrals via'
}

/**
 * Relations that are not "answers to": who appointed its members, funded it, or tabled its report.
 * Each is its own kind, so a report tabled by a minister is never drawn as that minister's ministry
 * being responsible for it.
 */
export const RelationsCard = ({ relations }) => {
  const [open, setOpen] = useState(false)
  if (!relations?.length) return null
  const shown = open ? relations : relations.slice(0, 5)
  return (
    <section className="gov-card">
      <h2 className="gov-card__heading">Other relationships <span className="gov-muted">{relations.length}</span></h2>
      <p className="gov-muted">Dated observations that do not by themselves say which ministry answered for it.</p>
      <ul className="gov-evidence__list">
        {shown.map((entry, index) => (
          <li key={index}>
            <span>{RELATION_LABELS[entry.relation] ?? entry.relation.replace(/_/g, ' ')}: {entry.office ?? 'office not stated'}{entry.holder ? ` (${entry.holder})` : ''}</span>
            <span className="gov-muted">{entry.from}{entry.to && entry.to !== entry.from ? `–${entry.to}` : ''} · <SourceLink source={entry.source} /></span>
          </li>
        ))}
      </ul>
      {relations.length > 5 && <button type="button" className="gov-show-more" onClick={() => setOpen((value) => !value)}>{open ? 'Fewer' : `All ${relations.length}`}</button>}
    </section>
  )
}
