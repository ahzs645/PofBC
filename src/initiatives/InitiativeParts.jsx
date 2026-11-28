import { SiteLink } from '../site/navigation.jsx'
import { VIEWS } from '../site/ViewSwitcher.jsx'
import { COLLECTED_DISPLAY } from '../gallery/collectedDisplay.js'

// The pieces every initiative page and the index share: a program's parts, and the links that
// leave an initiative for another section of the site ("Open in Logos →").
export const coverUrl = (file) => `${import.meta.env.BASE_URL}${file.replace(/^\//, '')}`
export const coverFile = (cover, theme) => COLLECTED_DISPLAY[cover?.displayId]?.[theme]?.file ?? cover?.file
const SECTION_NAMES = Object.fromEntries(VIEWS.map((view) => [view.id, view.label]))

/** "Open in Logos" for another section; within Initiatives, what the link opens. */
export const openLabel = (to) => to.view !== 'initiatives' ? `Open in ${SECTION_NAMES[to.view] ?? 'this section'}`
  : to.record ? 'Open record' : to.section ? 'Open section' : 'Open initiative'

const Forward = () => <span aria-hidden="true"> →</span>

/** A program's parts as a row of small linked cards, each with the part's own cover. */
export const InitiativeParts = ({ program, parts, theme, headingLevel = 3, onOpen, linkRef }) => {
  if (!parts.length) return null
  const Heading = `h${headingLevel}`
  const meta = program.parts ?? {}
  return <section className="initiatives__parts" aria-label={meta.label ?? `Parts of ${program.title}`}>
    <div className="initiatives__parts-head">
      <Heading>{meta.label ?? `Within ${program.title}`}</Heading>
      {meta.note && <p>{meta.note}{meta.source && <> <a href={meta.source.url} target="_blank" rel="noreferrer">{meta.source.title}<span aria-hidden="true"> ↗</span></a></>}</p>}
    </div>
    <ul>
      {parts.map((part) => <li key={part.id}>
        <SiteLink ref={linkRef?.(part.id)} className="initiatives__part" to={{ view: 'initiatives', initiative: part.id }}
          onClick={onOpen ? (event) => onOpen(event, part.id) : undefined}>
          <span className="initiatives__part-art" data-themed={COLLECTED_DISPLAY[part.cover?.displayId]?.[theme] ? true : undefined}
            data-dark={part.cover?.darkBackground ? true : undefined} data-empty={part.cover ? undefined : true}>
            {/* A part with no artwork held says so, rather than showing an empty panel. */}
            {part.cover ? <img src={coverUrl(coverFile(part.cover, theme))} alt="" loading="lazy" /> : 'No logo held'}
          </span>
          <span className="initiatives__part-copy">
            <strong>{part.title}</strong>
            <span>{openLabel({ view: 'initiatives' })}<Forward /></span>
          </span>
        </SiteLink>
      </li>)}
    </ul>
  </section>
}

/** Where an initiative leads elsewhere on the site, each link named for the section it opens. */
export const RelatedLinks = ({ links = [], label = 'Related pages', title = 'Continue exploring' }) => links.length > 0 &&
  <nav className="initiative__related" aria-label={label}>
    {title && <h3>{title}</h3>}
    <ul>{links.map((link) => <li key={`${link.label}-${link.to.view}`}>
      <SiteLink to={link.to}><strong>{link.label}</strong><span>{openLabel(link.to)}<Forward /></span></SiteLink>
    </li>)}</ul>
  </nav>
