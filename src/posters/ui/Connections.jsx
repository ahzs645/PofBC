// A piece's connections to the rest of the site, from the registry (../connections.js): who issued
// it, the marks on it, the objects it is tied to and its historical setting, each with what the
// connection rests on. A connection to one of the collection's own records (../records.js) opens
// the record in place.

import { SiteLink } from '../../site/navigation.jsx'
import { POSTERS } from '../catalogue.js'
import { CERTAINTY, groupedConnections } from '../connections.js'
import { RECORDS } from '../records.js'
import { Item } from './Reveal.jsx'

const Head = ({ entry, mark }) => (
  <>
    <span className="pv-connection-rel">{entry.rel} <i data-certainty={entry.certainty}>{CERTAINTY[entry.certainty]}</i></span>
    <b>{entry.label}{mark && <> <span aria-hidden="true">{mark}</span></>}</b>
    {entry.note && <span>{entry.note}</span>}
  </>
)

/** One of the collection's records, folded under its connection. */
const Record = ({ entry }) => {
  const record = RECORDS[entry.record]
  return (
    <details className="pv-link-card pv-record">
      <summary><Head entry={entry} mark="+" /></summary>
      <div className="pv-record-body">
        <p className="pv-eyebrow">{record.kind}</p>
        <p>{record.summary}</p>
        <dl className="pv-facts">
          {record.facts.map(([k, v]) => [<dt key={`${k}-k`}>{k}</dt>, <dd key={`${k}-v`}>{v}</dd>])}
        </dl>
        <div className="pv-note"><p>{record.limits}</p></div>
        <p className="pv-eyebrow">Where it is printed</p>
        <ul className="pv-record-seen">
          {record.seenOn.map(({ poster, part, note }) => (
            <li key={poster + part}>
              <SiteLink to={{ view: 'posters', poster, part }}>{POSTERS[poster].title} <span aria-hidden="true">→</span></SiteLink>
              <span>{note}</span>
            </li>
          ))}
        </ul>
        {record.sources.length > 0 && (
          <div className="pv-sources">
            Sources:
            <ul>{record.sources.map((s) => <li key={s.href}><a href={s.href} target="_blank" rel="noopener noreferrer">{s.label}</a></li>)}</ul>
          </div>
        )}
      </div>
    </details>
  )
}

const Card = ({ entry }) => {
  if (entry.record) return <Record entry={entry} />
  if (entry.to) return <SiteLink to={entry.to} className="pv-link-card"><Head entry={entry} mark="→" /></SiteLink>
  if (entry.href) return <a href={entry.href} target="_blank" rel="noopener noreferrer" className="pv-link-card"><Head entry={entry} mark="↗" /></a>
  return <div className="pv-link-card pv-link-plain"><Head entry={entry} /></div>
}

/** Nothing at all for a piece the registry does not know (the signs, say). */
export function Connections({ poster }) {
  const groups = groupedConnections(poster)
  if (!groups.length) return null
  return (
    <>
      <Item as="h3">Connections</Item>
      <Item as="p" className="pv-muted pv-connections-key">Each link says what it rests on: printed on the piece, documented elsewhere, inferred, or a comparison of theme only.</Item>
      {groups.map((group) => (
        <Item as="section" key={group.id} className="pv-connections" aria-label={group.title}>
          <h4>{group.title}</h4>
          <ul className="pv-links">
            {group.entries.map((entry) => <li key={entry.rel + entry.label}><Card entry={entry} /></li>)}
          </ul>
        </Item>
      ))}
    </>
  )
}
