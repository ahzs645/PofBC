// A piece's connections to the rest of the site, from the registry (../connections.js): who issued
// it, the marks on it, the objects it is tied to and its historical setting, each with what the
// connection rests on.

import { SiteLink } from '../../site/navigation.jsx'
import { CERTAINTY, groupedConnections } from '../connections.js'
import { Item } from './Reveal.jsx'

const Card = ({ entry }) => {
  const body = (
    <>
      <span className="pv-connection-rel">{entry.rel} <i data-certainty={entry.certainty}>{CERTAINTY[entry.certainty]}</i></span>
      <b>{entry.label}{(entry.to || entry.href) && <> <span aria-hidden="true">{entry.href ? '↗' : '→'}</span></>}</b>
      {entry.note && <span>{entry.note}</span>}
    </>
  )
  if (entry.to) return <SiteLink to={entry.to} className="pv-link-card">{body}</SiteLink>
  if (entry.href) return <a href={entry.href} target="_blank" rel="noopener noreferrer" className="pv-link-card">{body}</a>
  return <div className="pv-link-card pv-link-plain">{body}</div>
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
