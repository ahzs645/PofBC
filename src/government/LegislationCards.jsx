// A body's legislation and policy, and each instrument's own page: the bodies it established,
// continued, reorganized or ended, and the dated events that cite it. A relationship is shown only as
// its evidence states it; today's legal basis is never presented as a founding.

import { formatEventDate } from './events.js'
import { bodiesOfInstrument, instrumentsOfBody, TYPES } from './instruments.js'
import { FIRST_YEAR, lifeOf, PRESENT_YEAR } from './snapshot.js'
import { SourceLink } from './AtlasCards.jsx'
import { AdministeredByCard } from './AmrCards.jsx'

const dateOf = (value) => (value ? formatEventDate({ start: String(value) }) : null)
const clampYear = (year) => Math.min(PRESENT_YEAR, Math.max(FIRST_YEAR, year))

/** The year to open a body in from an instrument: the relationship's own date, else a year it stood. */
const yearFor = (id, from) => {
  if (from) return clampYear(Number(String(from).slice(0, 4)))
  const life = lifeOf(id)
  if (!life || life.toKind === 'open') return PRESENT_YEAR
  return clampYear(Number(String(life.from ?? life.firstSeen ?? PRESENT_YEAR).slice(0, 4)))
}

const Provisions = ({ provisions }) => (provisions?.length ? <span className="gov-muted"> · {provisions.join(', ')}</span> : null)

/** Each dated event a relationship rests on, or the citation it was read from. */
// A relationship from a body's record has its note shown once, above; event evidence keeps each note.
const Evidence = ({ relation }) => (relation.evidence ?? [{ ...relation, note: null }]).map((entry, index) => (
  <span key={index} className="gov-events__sources">
    {entry.source && <SourceLink source={entry.source} />}
    {(entry.date ?? relation.from) && relation.evidence && <span className="gov-muted"> · {dateOf(entry.date)}</span>}
    {entry.locator && <span className="gov-muted"> · {String(entry.locator)}</span>}
    {entry.note && <span className="gov-muted"> · {entry.note}</span>}
  </span>
))

/** On a body's panel: the instruments it stands in a stated relationship to, and those its history cites. */
export const LegislationCard = ({ node, onOpen }) => {
  const { groups, cited } = instrumentsOfBody(node.id)
  if (!groups.length && !cited.length) return null
  const count = groups.reduce((total, group) => total + group.rows.length, 0) + cited.length
  return (
    <section className="gov-card">
      <h2 className="gov-card__heading">Legislation and policy <span className="gov-muted">{count}</span></h2>
      {groups.map((group) => (
        <div key={group.kind}>
          <h3 className="gov-card__subheading">{group.label}</h3>
          {group.note && <p className="gov-muted">{group.note}</p>}
          <ul className="gov-events">
            {group.rows.map(({ instrument, relation }, index) => (
              <li key={`${instrument.id}-${index}`} className="gov-events__item">
                <span className="gov-events__date">{relation.from ? dateOf(relation.from) : relation.asOf ? 'Today' : ''}</span>
                <span className="gov-events__body">
                  <span className="gov-events__title">
                    <button type="button" className="gov-link-button" onClick={() => onOpen(instrument.id)}>{instrument.title}</button>
                    <Provisions provisions={relation.provisions} />
                    <span className="gov-muted"> · {TYPES[instrument.type]}</span>
                  </span>
                  {relation.note && !relation.evidence && <span className="gov-events__note">{relation.note}</span>}
                  <Evidence relation={relation} />
                </span>
              </li>
            ))}
          </ul>
        </div>
      ))}
      {cited.length > 0 && (
        <>
          <h3 className="gov-card__subheading">Also cited in its history</h3>
          <p className="gov-muted">Instruments its dated events cite, where the event does not say what the instrument did for this body.</p>
          <ul className="gov-list-inline">
            {cited.map((instrument) => (
              <li key={instrument.id}><button type="button" className="gov-link-button" onClick={() => onOpen(instrument.id)}>{instrument.title}</button></li>
            ))}
          </ul>
        </>
      )}
    </section>
  )
}

/** An instrument's own page: what it is, the bodies it stands in a relationship to, and its dated events. */
export const InstrumentCard = ({ instrument, onGo, onClose }) => {
  const groups = bodiesOfInstrument(instrument)
  const name = (id) => lifeOf(id)?.name ?? id
  return (
    <>
    <section className="gov-card">
      <p className="gov-muted">{TYPES[instrument.type]}{instrument.citations.length ? ` · ${instrument.citations.join('; ')}` : ''}</p>
      <h2 className="gov-card__heading">{instrument.title}</h2>
      <button type="button" className="gov-link-button" onClick={onClose}>Close</button>
      {groups.map((group) => (
        <div key={group.kind}>
          <h3 className="gov-card__subheading">{group.reverse} <span className="gov-muted">{group.rows.length}</span></h3>
          {group.note && <p className="gov-muted">{group.note}</p>}
          <ul className="gov-events">
            {group.rows.map((relation, index) => (
              <li key={`${relation.body}-${index}`} className="gov-events__item">
                <span className="gov-events__date">{relation.from ? dateOf(relation.from) : relation.asOf ? 'Today' : ''}</span>
                <span className="gov-events__body">
                  <span className="gov-events__title">
                    <button type="button" className="gov-link-button" onClick={() => onGo(yearFor(relation.body, relation.from), relation.body)}>{name(relation.body)}</button>
                    <Provisions provisions={relation.provisions} />
                  </span>
                  {relation.note && !relation.evidence && <span className="gov-events__note">{relation.note}</span>}
                  <Evidence relation={relation} />
                </span>
              </li>
            ))}
          </ul>
        </div>
      ))}
      {instrument.milestones.length > 0 && (
        <>
          <h3 className="gov-card__subheading">Dated events citing it <span className="gov-muted">{instrument.milestones.length}</span></h3>
          <ul className="gov-events">
            {instrument.milestones.map((milestone) => (
              <li key={`${milestone.event}-${milestone.subject}`} className="gov-events__item">
                <span className="gov-events__date">{formatEventDate(milestone.date)}</span>
                <span className="gov-events__body">
                  <span className="gov-events__title">{milestone.title}</span>
                  <span className="gov-events__sources">
                    <button type="button" className="gov-link-button" onClick={() => onGo(yearFor(milestone.subject, milestone.date.start), milestone.subject)}>{name(milestone.subject)}</button>
                    {milestone.related.length > 0 && <span className="gov-muted"> · also {milestone.related.map(name).join(', ')}</span>}
                  </span>
                </span>
              </li>
            ))}
          </ul>
        </>
      )}
      {!groups.length && !instrument.milestones.length && <p className="gov-muted">No relationship or dated event is recorded for it yet.</p>}
    </section>
    <AdministeredByCard instrument={instrument} onGo={onGo} />
    </>
  )
}
