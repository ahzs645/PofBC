// The panel beside the diagram: what the chosen body is, who leads it, where it came from — and,
// for a ministry, its mark as it would have been set in the year on screen.

import { useMemo, useState } from 'react'
import { CURRENT_AS_OF } from './currentData.js'
import { changesIn, predecessorsOf, successorsOf } from './episodes.js'
import { currentMarkFor, identityFor, renderEraMark } from './eraMark.js'
import { KINDS, RELATIONS } from './GovernmentGraph.jsx'
import { officeHoldersTo, PEOPLE_ID, PRESENT_YEAR } from './snapshot.js'
import { ElectionStages, EventsCard, EvidenceCard, ParliamentCard, RelationsCard, StaffingCard } from './AtlasCards.jsx'
import { electionStages, eventsInYear, formatEventDate, typeOf } from './events.js'
import { PENDING_ELECTION, PREMIERS } from './timelineData.js'
import { partyColour } from './theme.js'

const BRANCH_LABELS = { legislative: 'Legislative', executive: 'Executive', judicial: 'Judicial' }

const years = (episode) => (episode.to ? `${episode.from}–${episode.to}` : `${episode.from}–`)

const formatDate = (day) => {
  if (!day) return null
  const [y, m, d] = String(day).split('-').map(Number)
  if (!m) return String(y)
  const month = new Date(Date.UTC(y, m - 1, d || 1)).toLocaleString('en-CA', { month: 'long', timeZone: 'UTC' })
  return d ? `${d} ${month} ${y}` : `${month} ${y}`
}

const PersonCard = ({ role, person, since, note, party, acting }) => (
  <div className="gov-person">
    <span className="gov-person__initials" style={party ? { borderColor: partyColour(party) } : undefined} aria-hidden="true">
      {person ? person.split(/\s+/).filter((word) => /^[A-Z]/.test(word)).slice(0, 2).map((word) => word[0]).join('') : '—'}
    </span>
    <span>
      <span className="gov-person__name">{person ?? 'Not recorded'}</span>
      <span className="gov-person__role">{role}</span>
      {(since || party || note) && (
        <span className="gov-person__since">
          {[party, acting && 'Acting', since && `Since ${formatDate(since)}`, note].filter(Boolean).join(' · ')}
        </span>
      )}
    </span>
  </div>
)

/** The ministry's lockup in the identity of the year on screen, and a way into the generator. */
const MarkCard = ({ node, year, theme, onOpenInGenerator }) => {
  const identity = identityFor(year)
  const svg = useMemo(() => (identity ? renderEraMark({ era: identity.era, name: node.name, theme }) : null), [identity, node.name, theme])
  if (!identity) {
    return (
      <section className="gov-card gov-card--mark">
        <h2 className="gov-card__heading">Mark</h2>
        <p className="gov-muted">
          The earliest identity this generator draws is dated to about 1976, so there is no lockup
          to show for {year}.
        </p>
      </section>
    )
  }
  const published = identity.era === 'current' && currentMarkFor(node.name)
  return (
    <section className="gov-card gov-card--mark">
      <h2 className="gov-card__heading">
        Mark in {year}: <span className="gov-chip">{identity.label}</span>
        {/* Only a published current mark is a documented logo; every other rendering here is this
            generator setting the name in that identity's rules. */}
        <span className="gov-chip" data-type={published ? 'event' : 'scheduled'}>{published ? 'Published mark' : 'Generated interpretation'}</span>
      </h2>
      <div className="gov-mark" data-era={identity.era} dangerouslySetInnerHTML={{ __html: svg }} />
      <p className="gov-muted">
        {identity.era === 'current'
          ? (published
              ? 'The Province’s published mark, with its wording set in the marks’ own alphabet.'
              : 'Set in the current identity’s alphabet. This generator holds published marks only for today’s ministries, so this one is typeset.')
          : `As a ${identity.label.toLowerCase()} lockup would have set it. ${identity.note}`}
        {identity.confidence === 'low' && ' When this identity was in use is only loosely known.'}
      </p>
      <button type="button" className="gov-button gov-button--primary" onClick={() => onOpenInGenerator({ era: identity.era, name: node.name })}>
        Open in the generator
      </button>
    </section>
  )
}

/** A span of dates as precise as each end is known: "1986–1988", "May 1945 – 1962", "1973–". */
const span = (from, to) => {
  const a = from ? formatDate(from) : '?'
  const b = to ? formatDate(to) : ''
  return /\s/.test(a + b) ? `${a} – ${b}`.trim() : `${a}–${b}`
}

/**
 * One person's unbroken tenure as one row. The records split a holding wherever a new premier
 * reappointed the cabinet, which is how the Executive Council records it but not how anyone
 * remembers it.
 */
const joinTenures = (holders) => holders.reduce((joined, holder) => {
  const last = joined.at(-1)
  // Newest first: `last` is the later term, `holder` the one before it.
  if (last && last.person === holder.person && last.title === holder.title && !last.acting && !holder.acting && holder.to && last.from && holder.to.slice(0, 10) === last.from.slice(0, 10)) {
    joined[joined.length - 1] = { ...last, from: holder.from, joinedFrom: [...(last.joinedFrom ?? [last.from]), holder.from] }
    return joined
  }
  joined.push(holder)
  return joined
}, [])

/** Everyone who held a post, newest first, with the one in office on the day shown picked out. */
const Holders = ({ label, holders: all, current, limit = 5 }) => {
  const [expanded, setExpanded] = useState(false)
  const holders = joinTenures(all)
  if (!holders.length) return null
  const shown = expanded ? holders : holders.slice(0, limit)
  return (
    <div className="gov-lineage">
      <h3 className="gov-card__subheading">{label} <span className="gov-muted">{holders.length}</span></h3>
      <ul className="gov-holders">
        {shown.map((holder, index) => (
          <li key={`${holder.person}-${holder.from}-${index}`} aria-current={current && holder.person === current.person && (holder.joinedFrom ?? [holder.from]).includes(current.since) ? 'true' : undefined}>
            <span>
              {holder.person}
              {holder.acting ? <span className="gov-muted"> (acting)</span> : null}
              {holder.title && label === 'Ministers' ? <span className="gov-holders__title">{holder.title}</span> : null}
            </span>
            <span className="gov-muted">{span(holder.from, holder.to)}</span>
          </li>
        ))}
      </ul>
      {holders.length > limit && (
        <button type="button" className="gov-show-more" aria-expanded={expanded} onClick={() => setExpanded((value) => !value)}>
          {expanded ? 'Show fewer' : `Show all ${holders.length}`}
        </button>
      )}
    </div>
  )
}

/** Bodies this one came from, or became: each a way to the years it stood. */
const BodyLineage = ({ label, bodies, onJump, end }) => bodies.length > 0 && (
  <div className="gov-lineage">
    <h3 className="gov-card__subheading">{label}</h3>
    <ul>
      {bodies.map((body) => (
        <li key={body.id}>
          <button type="button" className="gov-link-card" onClick={() => onJump(body, end)}>
            <span>{body.name}</span>
            {body.established && <span className="gov-muted">{span(body.established, body.ended)}</span>}
          </button>
        </li>
      ))}
    </ul>
  </div>
)

/**
 * A ministry's family, as rows through time: two generations of forerunners, the ministry itself,
 * and two generations of what it became. A merger or a split can fan out, so the walk stops at a
 * dozen rows, nearest first.
 */
const lineageRows = (episode) => {
  const rows = [{ episode, generation: 0 }]
  const seen = new Set([episode.id])
  const walk = (step, generation, next) => {
    for (const other of next) {
      if (!other || seen.has(other.id) || rows.length >= 12) continue
      seen.add(other.id)
      rows.push({ episode: other, generation })
    }
    return generation
  }
  let back = [episode]
  let forward = [episode]
  for (let depth = 1; depth <= 2; depth += 1) {
    back = back.flatMap((entry) => predecessorsOf(entry.id))
    walk('back', -depth, back)
    forward = forward.flatMap((entry) => successorsOf(entry.id))
    walk('forward', depth, forward)
  }
  return rows.sort((a, b) => a.episode.from - b.episode.from || a.generation - b.generation)
}

const shortMinistry = (name) => name.replace(/^Ministry (of|for) (the )?/, '').replace(/^Department of (the )?/, 'Dept. of ')

/**
 * The ministry's lineage as a small chart: each episode a bar across the years, its ministers as a
 * strip of party colours beneath its own bar, and a rule at the year on screen. Every row is a way
 * to that ministry in a year it stood.
 */
const MinistryTimeline = ({ node, year, onJump }) => {
  const rows = useMemo(() => lineageRows(node.episode), [node.episode])
  const start = Math.min(...rows.map(({ episode }) => episode.from))
  const end = Math.max(...rows.map(({ episode }) => (episode.to ?? PRESENT_YEAR) + 1))
  const span = Math.max(1, end - start)
  const at = (value) => `${((value - start) / span) * 100}%`
  const width = (from, to) => `${Math.max(0.8, ((to - from) / span) * 100)}%`
  const step = span > 60 ? 20 : span > 30 ? 10 : span > 12 ? 5 : 2
  const ticks = []
  for (let tick = Math.ceil(start / step) * step; tick < end; tick += step) ticks.push(tick)
  const decimal = (value) => {
    const [y, m] = String(value).split('-').map(Number)
    return y + ((m || 7) - 1) / 12
  }

  return (
    <section className="gov-card gov-timeline-card">
      <h2 className="gov-card__heading">Lineage <span className="gov-muted">{start}–{end - 1 >= PRESENT_YEAR ? 'today' : end - 1}</span></h2>
      <div className="gov-lineage-chart">
        <div className="gov-lineage-chart__axis" aria-hidden="true">
          {ticks.map((tick) => <span key={tick} style={{ left: at(tick) }}>{tick}</span>)}
        </div>
        {rows.map(({ episode, generation }) => {
          const self = generation === 0
          const to = episode.to ?? PRESENT_YEAR + 1
          return (
            <button
              key={episode.id}
              type="button"
              className="gov-lineage-chart__row"
              data-self={self || undefined}
              aria-current={self ? 'true' : undefined}
              disabled={self}
              onClick={() => onJump(episode, generation < 0 ? 'end' : 'start')}
              title={self ? undefined : `Go to ${episode.name}`}
            >
              <span className="gov-lineage-chart__label">
                {shortMinistry(episode.name)}
                <span className="gov-muted"> {years(episode)}</span>
              </span>
              <span className="gov-lineage-chart__track">
                <span className="gov-lineage-chart__bar" style={{ left: at(episode.from), width: width(episode.from, to) }} />
              </span>
              {self && node.ministers?.length > 0 && (
                <span className="gov-lineage-chart__ministers" aria-label="Ministers, by party">
                  {node.ministers.map((minister, index) => {
                    const from = Math.max(decimal(minister.from), episode.from)
                    const until = minister.to ? decimal(minister.to) : to
                    return (
                      <span
                        key={`${minister.person}-${index}`}
                        className="gov-lineage-chart__minister"
                        style={{ left: at(from), width: width(from, until), background: partyColour(minister.party) }}
                        title={`${minister.person}${minister.party ? ` (${minister.party})` : ''}, ${span2(minister.from, minister.to)}`}
                      />
                    )
                  })}
                </span>
              )}
            </button>
          )
        })}
        <span className="gov-lineage-chart__cursor" style={{ left: at(year + 0.5) }} aria-hidden="true" />
      </div>
    </section>
  )
}

const span2 = (from, to) => `${String(from).slice(0, 4)}–${to ? String(to).slice(0, 4) : ''}`

const Lineage = ({ label, episodes, onJump }) => episodes.length > 0 && (
  <div className="gov-lineage">
    <h3 className="gov-card__subheading">{label}</h3>
    <ul>
      {episodes.map((episode) => (
        <li key={episode.id}>
          <button type="button" className="gov-link-card" onClick={() => onJump(episode)}>
            <span>{episode.name}</span>
            <span className="gov-muted">{years(episode)}</span>
          </button>
        </li>
      ))}
    </ul>
  </div>
)

const Connections = ({ node, government, onSelect }) => {
  const byId = new Map(government.nodes.map((entry) => [entry.id, entry]))
  const groups = {}
  for (const edge of government.edges) {
    if (edge.from !== node.id && edge.to !== node.id) continue
    const outgoing = edge.from === node.id
    const other = byId.get(outgoing ? edge.to : edge.from)
    if (!other) continue
    const relation = RELATIONS[edge.kind]
    const label = outgoing ? relation.label : { elects: 'Elected by', appoints: 'Appointed by', confidence: 'Needs the confidence of', responsible: 'Answers to', part: 'Part of' }[edge.kind]
    ;(groups[label] ??= []).push(other)
  }
  const entries = Object.entries(groups)
  if (!entries.length) return null
  return (
    <section className="gov-card">
      <h2 className="gov-card__heading">Who’s connected?</h2>
      {entries.map(([label, others]) => (
        <div key={label} className="gov-connections">
          <h3 className="gov-card__subheading">{label} <span className="gov-muted">{others.length}</span></h3>
          <ul className="gov-connections__grid">
            {others.map((other) => (
              <li key={other.id}>
                <button type="button" className="gov-link-card" onClick={() => onSelect(other.id)}>
                  <span className="gov-kind-dot" data-branch={other.branch ?? 'people'} />
                  <span>{other.shortName ?? other.name}</span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </section>
  )
}

export const EntityCard = ({ node, government, theme, onSelect, onJump, onJumpBody, onOpenInGenerator }) => {
  const { year, present, day } = government
  const isBody = !['ministry', 'assembly', 'crown', 'premier', 'people'].includes(node.kind)
  const officeId = node.kind === 'assembly' ? 'speaker' : node.id
  const holders = ['officer', 'court', 'assembly'].includes(node.kind) ? officeHoldersTo(officeId, day) : []
  const isMinistry = node.kind === 'ministry'
  const breadcrumb = node.branch ? BRANCH_LABELS[node.branch] : 'Everyone'
  const kindLabel = KINDS[node.kind]?.label

  return (
    <>
      <section className="gov-card">
        <p className="gov-eyebrow">{breadcrumb}{kindLabel ? ` · ${kindLabel}` : ''}</p>
        <h1 className="gov-title">{node.name}</h1>
        {isMinistry && (
          <p className="gov-muted">
            {years(node.episode)}
            {node.episode.inferredEnd ? ' (end inferred from what it became)' : ''}
            {node.employees ? ` · ${node.employees.toLocaleString('en-CA')} FTE staff, 2025/26` : ''}
          </p>
        )}
        {node.description && <p className="gov-description">{node.description}</p>}
        {node.operatingName && (
          <p className="gov-muted">
            Operating as {node.operatingName.name} since {node.operatingName.from} · legal name {node.name}
          </p>
        )}
        {isBody && node.established && (
          <p className="gov-muted">
            {node.ended ? `${span(node.established, node.ended)}` : `Since ${formatDate(node.established)}`}
          </p>
        )}
        {!node.description && isMinistry && !present && (
          <p className="gov-description gov-muted">
            A ministry of the {year} government, from the BC Archives’ ministry history, with its
            ministers from the Legislative Library’s Executive Council records.
          </p>
        )}
        {node.officialUrl && (
          <p className="gov-links"><a href={node.officialUrl} target="_blank" rel="noreferrer">Official website</a></p>
        )}

        {node.kind === 'assembly' && (
          <div className="gov-stats">
            {node.election && (
              <p>
                <strong>{node.seats} seats</strong>
                {' '}· {ordinal(node.election.parliament)} Parliament, elected {formatDate(node.election.date)}
                {governingParty(government) ? ` · ${governingParty(government)} government` : ''}
              </p>
            )}
            {node.election && Object.keys(node.election.seats).length > 0 && (
              <SeatBar seats={node.election.seats} total={node.election.totalSeats} />
            )}
            {present && <ElectionStages stages={electionStages(day)} />}
            {node.dissolved && PENDING_ELECTION && (
              <p className="gov-notice">
                Dissolved on {formatDate(PENDING_ELECTION.dissolved)}. The {ordinal(PENDING_ELECTION.parliament)} Legislature
                will be elected on {formatDate(PENDING_ELECTION.date)}.
              </p>
            )}
            <div className="gov-people">
              {node.head
                ? <PersonCard role="Speaker" person={node.head.person} since={node.head.since} acting={node.head.acting} />
                : <PersonCard role="Speaker" person={null} note="Vacant at the year’s end, between Legislatures" />}
              {node.clerk && <PersonCard role={node.clerk.title} person={node.clerk.person} since={node.clerk.since} acting={node.clerk.acting} />}
            </div>
          </div>
        )}

        {node.head && node.kind !== 'assembly' && (
          <div className="gov-people">
            <PersonCard role={node.head.title} person={node.head.person} since={node.head.since} party={node.head.party} acting={node.head.acting} />
            {node.deputy && <PersonCard role={node.deputy.title} person={node.deputy.person} />}
            {node.ministersOfState?.map((minister) => (
              <PersonCard key={minister.title} role={minister.title} person={minister.person} since={minister.since} />
            ))}
            {node.chair && <PersonCard role="Board chair" person={node.chair} />}
          </div>
        )}

        {node.inferredParent && (
          <p className="gov-notice">
            Part of {node.parentName} in {year} by inference: it belongs to that ministry’s successor
            today, and when it moved between ministries is not recorded here.
          </p>
        )}

        {node.inferredGroup && (
          <p className="gov-notice">
            Shown beside the {year} forerunner of the ministry that answers for it today; which
            ministry answered for it in {year} is not recorded here.
          </p>
        )}

        {isMinistry && (
          <>
          </>
        )}

        {isBody && (
          <>
            <BodyLineage label="Came from" bodies={node.cameFrom ?? []} onJump={onJumpBody} end="end" />
            <BodyLineage label="Became" bodies={node.became ? [node.became] : []} onJump={onJumpBody} end="start" />
          </>
        )}

        {holders.length > 0 && <Holders label={node.kind === 'assembly' ? 'Speakers' : 'Holders'} holders={holders} current={node.head} />}

        {node.kind === 'premier' && <PremierList year={year} />}
      </section>

      <EventsCard events={node.events} day={day} />
      {isMinistry && <MinistryTimeline node={node} year={year} onJump={onJump} />}
      {isMinistry && node.ministers?.length > 0 && (
        <section className="gov-card">
          <Holders label="Ministers" holders={[...node.ministers].reverse()} current={node.head} />
        </section>
      )}
      {isMinistry && <MarkCard node={node} year={year} theme={theme} onOpenInGenerator={onOpenInGenerator} />}
      <StaffingCard rows={node.staffing} year={year} />
      {node.kind === 'assembly' && <ParliamentCard parliament={node.parliament} />}
      <Connections node={node} government={government} onSelect={onSelect} />
      <RelationsCard relations={node.relations} />
      <EvidenceCard node={node} />
    </>
  )
}

/**
 * The party in government — the premier's, not the election's largest. They differ: the Liberals
 * won the most seats in 2017 but the NDP governed from July, and a Coalition governed from 1941.
 */
const governingParty = ({ premier }) => (premier && premier.party !== 'Non-partisan' ? premier.party : null)

/** White or near-black, whichever reads better on a fill. */
const inkOn = (hex) => {
  const [r, g, b] = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255)
    .map((c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4))
  return 0.2126 * r + 0.7152 * g + 0.0722 * b > 0.23 ? '#1c1917' : '#ffffff'
}

const ordinal = (n) => {
  const suffix = ['th', 'st', 'nd', 'rd'][((n % 100) - 20) % 10] || ['th', 'st', 'nd', 'rd'][n % 100] || 'th'
  return `${n}${suffix}`
}

const SeatBar = ({ seats, total }) => (
  <div className="gov-seats" role="img" aria-label={Object.entries(seats).map(([party, count]) => `${party} ${count}`).join(', ')}>
    {Object.entries(seats).map(([party, count]) => (
      <span key={party} style={{ flexGrow: count, background: partyColour(party), color: inkOn(partyColour(party)) }} title={`${party}: ${count}`}>
        {count / total > 0.08 ? `${party} ${count}` : ''}
      </span>
    ))}
  </div>
)

const PremierList = ({ year }) => {
  const recent = PREMIERS.filter((premier) => Number(premier.from.slice(0, 4)) <= year).slice(-6).reverse()
  return (
    <div className="gov-lineage">
      <h3 className="gov-card__subheading">Premiers up to {year}</h3>
      <ul className="gov-plain-list">
        {recent.map((premier) => (
          <li key={`${premier.name}-${premier.from}`}>
            <span className="gov-kind-dot" style={{ background: partyColour(premier.party) }} />
            {premier.name} <span className="gov-muted">{premier.party} · {premier.from.slice(0, 4)}–{premier.to ? premier.to.slice(0, 4) : ''}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

// ── Nothing chosen: the year at a glance, and what changed in it ─────────────────────────────────

export const OverviewCard = ({ government, onSelect }) => {
  const { year, premier, lieutenantGovernor, election, present, nodes } = government
  const count = (kind) => nodes.filter((node) => node.kind === kind).length
  const ministries = count('ministry')
  return (
    <section className="gov-card">
      <p className="gov-eyebrow">{present ? `As at ${formatDate(CURRENT_AS_OF)}` : `At the end of ${year}`}</p>
      <h1 className="gov-title">The Government of British Columbia{present ? '' : ` in ${year}`}</h1>
      <div className="gov-people">
        {premier && <PersonCard role="Premier" person={premier.name} since={premier.from} party={premier.party} />}
        {lieutenantGovernor && <PersonCard role="Lieutenant Governor" person={lieutenantGovernor.name} since={lieutenantGovernor.from} />}
      </div>
      <dl className="gov-tiles">
        <div><dt>{year < 1976 ? 'Departments' : 'Ministries'}</dt><dd>{ministries}</dd></div>
        <div><dt>Seats</dt><dd>{election?.totalSeats ?? '—'}</dd></div>
        <div><dt>Parliament</dt><dd>{election ? ordinal(election.parliament) : '—'}</dd></div>
      </dl>
      {government.dissolved && PENDING_ELECTION && (
        <p className="gov-notice">
          The Legislature was dissolved on {formatDate(PENDING_ELECTION.dissolved)}; British Columbians
          vote on {formatDate(PENDING_ELECTION.date)}. Ministers stay in office until a new cabinet is sworn in.
        </p>
      )}
      <p className="gov-description gov-muted">
        {present
          ? 'Choose any body to see who leads it and what it answers to. Move the timeline to watch the ministries reorganise, back to Confederation in 1871.'
          : `The government as ${year} ended, plus any ministry that came and went within the year: its ministries and who held them, the Crown corporations and agencies that stood, and the Speaker, officers and chief justices then in office. Where no source says which ministry answered for a body, it is placed by inference and the panel says so.`}
      </p>
      <p><button type="button" className="gov-link-button" onClick={() => onSelect(PEOPLE_ID)}>Start with the people →</button></p>
    </section>
  )
}

const CHANGE_LABELS = { established: 'Established', renamed: 'Renamed', merged: 'Merged', split: 'Split', dissolved: 'Ended' }

export const ChangesCard = ({ year, onSelect, onJump }) => {
  const changes = changesIn(year)
  const premiers = PREMIERS.filter((premier) => premier.from.startsWith(String(year)))
  // Dated events of the year — origins, renamings, new logos, appointments, the election's stages —
  // each at the precision its source gives.
  const events = eventsInYear(year)
  const shortName = (name) => name.replace(/^Ministry of (the )?/, '').replace(/^Department of (the )?/, 'Dept. of ')
  return (
    <section className="gov-card">
      <h2 className="gov-card__heading">What changed in {year}</h2>
      {!changes.length && !premiers.length && !events.length && <p className="gov-muted">No change to the ministries, and no new premier.</p>}
      <ul className="gov-feed">
        {premiers.map((premier) => (
          <li key={premier.name} className="gov-feed__item">
            <span className="gov-chip" data-type="premier">Premier</span>
            <span><strong>{premier.name}</strong> <span className="gov-muted">({premier.party})</span> took office on {formatDate(premier.from)}.</span>
          </li>
        ))}
        {changes.map((change, index) => (
          <li key={index} className="gov-feed__item">
            <span className="gov-chip" data-type={change.type}>{CHANGE_LABELS[change.type]}</span>
            <span className="gov-feed__names">
              {change.predecessors.length > 0 && (
                <span className="gov-feed__out">
                  {change.predecessors.map((episode) => (
                    <button key={episode.id} type="button" className="gov-link-button" onClick={() => onJump(episode, 'end')}>{shortName(episode.name)}</button>
                  ))}
                </span>
              )}
              {change.predecessors.length > 0 && change.successors.length > 0 && <span aria-hidden="true"> → </span>}
              {change.successors.length > 0 && (
                <span className="gov-feed__in">
                  {change.successors.map((episode) => (
                    <button key={episode.id} type="button" className="gov-link-button" onClick={() => onSelect(episode.id)}>{shortName(episode.name)}</button>
                  ))}
                </span>
              )}
            </span>
          </li>
        ))}
        {events.map((event) => (
          <li key={event.id} className="gov-feed__item">
            <span className="gov-chip" data-type={typeOf(event).kind === 'election' && event.status !== 'source_reported_past' ? 'scheduled' : 'event'}>{typeOf(event).label}</span>
            <span className="gov-feed__names">
              {event.subject.startsWith('symbol:')
                ? <span>{event.title}</span>
                : <button type="button" className="gov-link-button" onClick={() => onSelect(event.subject)}>{event.title}</button>}
              <span className="gov-muted"> · {formatEventDate(event.date)}</span>
            </span>
          </li>
        ))}
      </ul>
    </section>
  )
}
