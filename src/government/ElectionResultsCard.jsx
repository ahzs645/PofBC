import { useState } from 'react'
import { SiteLink } from '../site/navigation.jsx'
import { partyPlaceFor } from '../parties/partyLinks.js'

/** New election evidence can be displayed without relabelling an older government snapshot. */
export const ElectionResultsCard = ({ results }) => {
  const [expanded, setExpanded] = useState(false)
  if (!results) return null
  const recounts = results.candidates.filter((candidate) => candidate.judicialRecountRequired)
  const shown = expanded ? results.candidates : recounts
  return (
    <section className="gov-card" aria-labelledby="election-results-heading">
      <h2 id="election-results-heading" className="gov-card__heading">2026 election results</h2>
      <p className="gov-muted">Final count published {results.publishedOn} · checked {results.checkedOn}</p>
      <ul className="gov-standings">
        {Object.entries(results.parties).map(([party, count]) => {
          const place = partyPlaceFor(party)
          return <li key={party}><strong>{count}</strong> {place ? <SiteLink to={place}>{party}</SiteLink> : party}</li>
        })}
      </ul>
      <p>Judicial recounts confirmed both district winners on {results.recountSource.publishedOn}. The final count returned {results.totalSeats} members.</p>
      <h3 className="gov-card__subheading">{expanded ? 'Declared elected candidates' : 'Recounted districts'}</h3>
      <ul className="gov-seats-list">
        {shown.map((candidate) => (
          <li key={candidate.district}>
            <span className="gov-seats-list__who"><strong>{candidate.candidate}</strong> · {candidate.district}</span>
            <span className="gov-muted">{candidate.party}{candidate.judicialRecountRequired ? ' · Confirmed by recount' : ''}</span>
          </li>
        ))}
      </ul>
      <button type="button" className="gov-show-more" aria-expanded={expanded} onClick={() => setExpanded((value) => !value)}>
        {expanded ? 'Show recount districts' : `Show all ${results.totalSeats} declared candidates`}
      </button>
      <p className="gov-links"><a href={results.source.url} target="_blank" rel="noreferrer">Elections BC final-count source</a></p>
      <p className="gov-links"><a href={results.recountSource.url} target="_blank" rel="noreferrer">Elections BC judicial recount results</a></p>
    </section>
  )
}
