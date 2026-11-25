// What the patch and badge viewers both show beside a design: where it was seen, and its history.

import { SiteLink } from '../site/navigation.jsx'
import { FOREST_SERVICE_TIMELINE, historyOf } from './patchHistory.js'
import { CERTAINTY, postersForPatch } from '../posters/connections.js'

/** The images a design was seen in: one per source (S27-O01 and S27-O03 are both source S27). */
export const photosOf = (patch) => {
  const photos = new Map()
  for (const { id, sourceUrl } of patch.sightings ?? []) {
    const photo = id.replace(/-O\d+$/, '')
    if (!photos.has(photo)) photos.set(photo, { photo, sourceUrl, ids: [] })
    photos.get(photo).ids.push(id)
  }
  return [...photos.values()]
}

/** What the BC Forest Service timeline says about the patch's wording, and a Forest Oval's own history. */
export function PatchHistory({ patch }) {
  const { notes, logo } = historyOf(patch)
  // The printed pieces tied to this patch, read back from the posters' connection registry.
  const printed = postersForPatch(patch.id)
  if (!notes.length && !logo && !printed.length) return null
  return (
    <section className="patch__history" aria-label="History">
      <h3>History</h3>
      {notes.length > 0 && (
        <ul>
          {notes.map((note) => (
            <li key={note.id}><span className="patch__era">{note.era}</span> {note.text}</li>
          ))}
        </ul>
      )}
      {notes.length > 0 && (
        <p className="patch__source">
          From the <a href={FOREST_SERVICE_TIMELINE.url} target="_blank" rel="noreferrer">BC Forest Service timeline</a>: the dates
          bound the wording, not the {patch.collection === 'badges' ? 'badge' : 'patch'} itself.
        </p>
      )}
      {logo && (
        <p className="patch__source">
          {logo.evidence}. <SiteLink to={{ view: 'internal', internal: 'forests', 'internal-logo': logo.id }}>{logo.name} in Departmental Logos</SiteLink> has
          its dated research.
        </p>
      )}
      {printed.length > 0 && (
        <>
          <h3>In print</h3>
          <ul>
            {printed.map((entry) => (
              <li key={entry.poster + entry.rel}>
                <span className="patch__era">{CERTAINTY[entry.certainty]}</span> <SiteLink to={entry.to}>{entry.title}</SiteLink>, in Posters: {entry.rel.toLowerCase()}.
              </li>
            ))}
          </ul>
        </>
      )}
    </section>
  )
}
