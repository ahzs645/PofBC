// What a body came from and what it went on to, drawn the same way on every page that has them:
// the gallery's collections and marks, Departmental Logos, the school districts.
//
// Two columns, Predecessors and Successors, each a list of records. A record names the other body
// (a link to its page), says how the two are joined and when, and cites the source that says so.
// The page around it supplies the section and its heading ("Predecessors and successors").

/**
 * @typedef {object} LineageRecord
 * @property {string} key
 * @property {import('react').ReactNode} name  The other body, as a link to its page.
 * @property {string} [eyebrow]  A short line above the name ("SD 57").
 * @property {string} relation  How the two are joined, from this page's side ("Merged into this district").
 * @property {string} [date]  When, already formatted.
 * @property {string} [note]
 * @property {{ title: string, url: string, locator?: string }} [source]
 * @property {import('react').ReactNode} [preview]  The other body's card, where the page shows one.
 */

const Record = ({ record }) => (
  <li className="lineage__record">
    {record.preview}
    <div className="lineage__text">
      {record.eyebrow && <span className="lineage__eyebrow">{record.eyebrow}</span>}
      <strong className="lineage__name">{record.name}</strong>
      <span className="lineage__relation">{record.relation}{record.date && <> · {record.date}</>}</span>
      {record.note && <p className="lineage__note">{record.note}</p>}
      {record.source && (
        <a className="lineage__source" href={record.source.url} target="_blank" rel="noreferrer">
          {record.source.title}{record.source.locator ? ` · ${record.source.locator}` : ''}
        </a>
      )}
    </div>
  </li>
)

const Column = ({ title, records, empty, Heading }) => (records.length > 0 || empty) ? (
  <div className="lineage__column">
    <Heading className="lineage__heading">{title}</Heading>
    {records.length
      ? <ul className="lineage__records">{records.map((record) => <Record key={record.key} record={record} />)}</ul>
      : <p className="lineage__empty">{empty}</p>}
  </div>
) : null

/**
 * @param {object} props
 * @param {LineageRecord[]} [props.predecessors]
 * @param {LineageRecord[]} [props.successors]
 * @param {string} [props.emptyPredecessors] Said when there are none; without it the column is left out.
 * @param {string} [props.emptySuccessors]
 * @param {number} [props.level] The heading level of the two columns, one below the section's.
 */
export const Lineage = ({ predecessors = [], successors = [], emptyPredecessors, emptySuccessors, level = 3 }) => {
  const Heading = `h${level}`
  return (
    <div className="lineage">
      <Column title="Predecessors" records={predecessors} empty={emptyPredecessors} Heading={Heading} />
      <Column title="Successors" records={successors} empty={emptySuccessors} Heading={Heading} />
    </div>
  )
}
