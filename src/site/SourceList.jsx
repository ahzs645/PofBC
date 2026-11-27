// The sources a record rests on, listed the same way at the foot of every detail page that has
// them: the parties, the school districts and the coats of arms. Each is a link out (marked ↗), with
// where in it to look and what it supports, where the record says.

/** A link to a page outside the site, opened in a new tab and marked as such. */
export const ExternalLink = ({ href, className, children }) => (
  <a className={className} href={href} target="_blank" rel="noreferrer">{children}<span aria-hidden="true"> ↗</span></a>
)

/**
 * @param {object} props
 * @param {{ key?: string, url: string, title?: string, id?: string, locator?: string, note?: import('react').ReactNode }[]} props.sources
 */
export const SourceList = ({ sources }) => (
  <ol className="source-list">
    {sources.map((source, at) => (
      <li key={source.key ?? `${source.id ?? ''}-${source.url}-${at}`}>
        {source.id && <span className="source-list__id">{source.id}</span>}
        <div className="source-list__text">
          <ExternalLink href={source.url}>{source.title ?? source.url}</ExternalLink>
          {source.locator && <span className="source-list__locator">{source.locator}</span>}
          {source.note && <p className="source-list__note">{source.note}</p>}
        </div>
      </li>
    ))}
  </ol>
)
