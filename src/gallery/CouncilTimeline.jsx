import { findGalleryEntry } from './collections.js'
import { tileArt } from './tileArt.js'
import { ASI_ID } from './advancedSystemsInstitute.js'
import { COUNCIL_TIMELINE } from './scienceCouncilHistory.js'
import './councilTimeline.css'

const names = {
  'science-council-of-bc': 'Science Council',
  [ASI_ID]: 'Advanced Systems Institute',
  'bc-innovation-council': 'BC Innovation Council',
  'innovate-bc': 'Innovate BC'
}

export const CouncilTimeline = ({ theme, onChooseCollection }) => {
  const linkProps = (owner, mark) => {
    const collection = `collected-${owner}`
    const params = new URLSearchParams({ view: 'gallery', logos: collection })
    if (mark) params.set('mark', mark)
    return {
      href: `?${params}`,
      onClick(event) {
        if (event.button || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return
        event.preventDefault()
        onChooseCollection(collection, undefined, mark)
      }
    }
  }

  return <section className="gallery__shelf council-timeline" aria-labelledby="council-timeline-heading">
    <h2 className="gallery__shelf-title" id="council-timeline-heading">From the two merger partners to Innovate BC</h2>
    <ol>{COUNCIL_TIMELINE.map(({ date, title, owner, marks, note, source }) =>
      <li key={date}>
        <span className="council-timeline__date">{date}</span>
        <div>
          <h3>{title}</h3>
          {note && <p>{note}</p>}
          {marks && <div className="council-timeline__marks">{marks.map((id) => {
            const entry = findGalleryEntry(id)
            return <a key={id} {...linkProps(owner, id)}>
              <span aria-hidden="true" dangerouslySetInnerHTML={{ __html: tileArt(entry, theme) }} />
              {entry.label}
            </a>
          })}</div>}
          <div className="council-timeline__links">
            <a {...linkProps(owner)}>{names[owner]}</a>
            <a href={source.url} target="_blank" rel="noreferrer">{source.title}</a>
          </div>
        </div>
      </li>
    )}</ol>
  </section>
}
