// A body's dated events, oldest first, drawn the same way in every section that keeps a history:
// the school districts, the political parties and the initiatives.
//
// Each event has its date on the left, with a short line saying what kind of date it is ("Year
// recorded", "Logo seen in use"), and on the right its title, what happened, and its sources.

/**
 * @typedef {object} TimelineEvent
 * @property {string} key
 * @property {string} date  Already formatted.
 * @property {string} [dateTime]  A machine-readable date, where the date is exact enough for one.
 * @property {string} [dateNote]
 * @property {boolean} [quiet]  An observation rather than an event (a logo seen in use): drawn lighter.
 * @property {import('react').ReactNode} [title]
 * @property {import('react').ReactNode} [body]
 * @property {import('react').ReactNode} [sources]
 */

/**
 * @param {object} props
 * @param {TimelineEvent[]} props.events
 * @param {number} [props.level] The heading level of each event's title.
 */
export const HistoryTimeline = ({ events, level = 4 }) => {
  const Heading = `h${level}`
  return (
    <ol className="history-timeline">
      {events.map((event) => (
        <li key={event.key} data-quiet={event.quiet || undefined}>
          <div className="history-timeline__date">
            <time dateTime={event.dateTime}>{event.date}</time>
            {event.dateNote && <span>{event.dateNote}</span>}
          </div>
          <div className="history-timeline__event">
            {event.title && <Heading className="history-timeline__title">{event.title}</Heading>}
            {event.body}
            {event.sources && <div className="history-timeline__sources">{event.sources}</div>}
          </div>
        </li>
      ))}
    </ol>
  )
}
