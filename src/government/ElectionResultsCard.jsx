import { useState } from 'react'

/** New election evidence can be displayed without relabelling an older government snapshot. */
export const ElectionResultsCard = ({ results, snapshotDate }) => {
  const [expanded, setExpanded] = useState(false)
  if (!results) return null
  const recounts = results.candidates.filter((candidate) => candidate.judicialRecountRequired)
  const shown = expanded ? results.candidates : recounts
  return (
    <section className="gov-card" aria-labelledby="election-results-heading">
      <h2 id="election-results-heading" className="gov-card__heading">2026 election results</h2>
      <p className="gov-muted">Final count published {results.publishedOn} · checked {results.checkedOn}</p>
      <ul className="gov-standings">
        {Object.entries(results.parties).map(([party, count]) => <li key={party}><strong>{count}</strong> {party}</li>)}
      </ul>
      <p>{results.totalSeats} candidates declared elected on Elections BC’s final-count list. Kelowna Centre and Ladysmith-Oceanside are subject to judicial recounts.</p>
      <p className="gov-muted">Government offices shown in this view were checked on {snapshotDate}. These election results do not establish appointments or swearing-in dates.</p>
      <h3 className="gov-card__subheading">{expanded ? 'Declared elected candidates' : 'Districts requiring recounts'}</h3>
      <ul className="gov-seats-list">
        {shown.map((candidate) => (
          <li key={candidate.district}>
            <span className="gov-seats-list__who"><strong>{candidate.candidate}</strong> · {candidate.district}</span>
            <span className="gov-muted">{candidate.party}{candidate.judicialRecountRequired ? ' · Judicial recount required' : ''}</span>
          </li>
        ))}
      </ul>
      <button type="button" className="gov-show-more" aria-expanded={expanded} onClick={() => setExpanded((value) => !value)}>
        {expanded ? 'Show recount districts' : `Show all ${results.totalSeats} declared candidates`}
      </button>
      <p className="gov-links"><a href={results.source.url} target="_blank" rel="noreferrer">Elections BC final-count source</a></p>
      <p className="gov-muted">{results.assemblySource.note} <a href={results.assemblySource.url} target="_blank" rel="noreferrer">Assembly source</a></p>
    </section>
  )
}
