import { createContext, useContext, useEffect, useMemo, useRef, useState } from 'react'
import { SiteLink } from '../site/navigation.jsx'
import { fileOf, imagesOf, resolveInitiativeSelection } from './initiativeModel.js'
import './initiativeDetail.css'

const InitiativeContext = createContext(null)
const useInitiative = () => useContext(InitiativeContext)
const assetUrl = (file) => `${import.meta.env.BASE_URL}${file.replace(/^\//, '')}`
const sourceUrl = (source, reference) => {
  const url = new URL(reference.url ?? source.url)
  if (reference.page && (/\.pdf$/i.test(url.pathname) || url.pathname.includes('/hmo/'))) url.hash = `page=${reference.page}`
  return url.href
}
const Arrow = () => <svg className="initiative__link-icon" aria-hidden="true" width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M2 10 10 2M3 2h7v7" stroke="currentColor" strokeWidth="1.2" /></svg>
const Sources = ({ references = [], className = '', label = 'Sources' }) => {
  const { sourceMap } = useInitiative()
  return references.length > 0 && (
  <ul className={`initiative__references ${className}`} aria-label={label}>
    {references.map((reference, index) => {
      const source = sourceMap.get(reference.sourceId)
      if (!source) return null
      return <li key={`${reference.sourceId}-${reference.page ?? index}`}>
        {source.url || reference.url
          ? <a href={sourceUrl(source, reference)} target="_blank" rel="noreferrer">{source.shortTitle ?? source.title}<Arrow /></a>
          : <span>{source.title}</span>}
        {(reference.page || reference.locator) && <span>{reference.locator ?? `PDF page ${reference.page}`}</span>}
      </li>
    })}
  </ul>
  )
}
const SPECIMEN_TYPES = {
  'vector-reconstruction': 'Vector reconstruction',
  'native-pdf-vector-extraction': 'Native vector from publication',
  'printed-source-crop': 'Crop from the printed source',
  'original-published-image': 'Original publisher image',
  'official-published-website-screenshot': 'Published website screenshot',
  'official-published-website-image': 'Published website image'
}
const SpecimenProvenance = ({ image }) => image && typeof image !== 'string' && (
  <section className="initiative__specimen-provenance" aria-label="Selected specimen provenance">
    <p className="initiative__small"><strong>{SPECIMEN_TYPES[image.evidenceType] ?? 'Published specimen'}</strong>
      {image.date && <><br /><time dateTime={image.date}>{image.date}</time>{image.dateLabel && <> · {image.dateLabel}</>}</>}
      {!image.date && image.dateLabel && <><br />{image.dateLabel}</>}
    </p>
    <Sources label="Selected specimen source" references={[{
      sourceId: image.sourceId,
      url: image.sourceUrl,
      page: image.sourcePage,
      locator: image.sourceLocator
    }]} />
    {image.sourceImageUrl && <p className="initiative__small"><a href={image.sourceImageUrl} target="_blank" rel="noreferrer">Original image at the publisher<Arrow /></a></p>}
  </section>
)
const Status = ({ item }) => <span className={`initiative__status ${imagesOf(item).length ? 'initiative__status--visual' : ''}`}>
  <span aria-hidden="true" />{imagesOf(item).length ? 'Visual specimen' : item.statusLabel ?? 'Documented · image sought'}
</span>

const Visual = ({ item, image = imagesOf(item)[0], large = false }) => image
  ? <figure className={`initiative__visual ${large ? 'initiative__visual--large' : ''} ${image.darkBackground ? 'initiative__visual--dark' : ''}`}>
      <img src={assetUrl(fileOf(image))} alt={image.alt ?? item.title} width={image.width} height={image.height} loading="lazy" />
      {large && <figcaption>{image.caption ?? image.label ?? 'Published specimen; see the source record below.'}</figcaption>}
    </figure>
  : <div className="initiative__unrecovered">
      <svg width="48" height="42" viewBox="0 0 48 42" fill="none" aria-hidden="true"><rect x="2" y="3" width="44" height="33" rx="3" stroke="currentColor" strokeWidth="1.5" /><path d="M2 11h44M9 7h1m4 0h1m4 0h1M15 23h18M19 28h10" stroke="currentColor" strokeWidth="1.5" /></svg>
      <span>{item.kind?.includes('app') ? 'App imagery sought' : 'Visual specimen sought'}</span>
      <small>Documentary evidence is available</small>
    </div>

const Links = ({ links = [] }) => links.length > 0 && <ul className="initiative__links">{links.map((link, index) =>
  <li key={`${link.url}-${index}`}><a href={link.url} target={link.url.startsWith('#') || link.url.startsWith('?') ? undefined : '_blank'} rel="noreferrer">{link.label}<Arrow /></a>{link.note && <small>{link.note}</small>}</li>
)}</ul>

const SpecimenDialog = ({ item, onClose }) => {
  const { initiative } = useInitiative()
  const dialog = useRef(null)
  const [selected, setSelected] = useState(0)
  const images = imagesOf(item)
  // Repeated collection names add no distinction to a specimen chooser. The full label remains
  // in each button's title and in the selected image caption.
  const firstLabel = images[0]?.label ?? images[0]?.title ?? ''
  const prefix = firstLabel.match(/^.+? — /)?.[0]
  const commonPrefix = prefix && images.every((image) => (image.label ?? image.title ?? '').startsWith(prefix)) ? prefix : ''
  useEffect(() => {
    const element = dialog.current
    element?.showModal()
    return () => { if (element?.open) element.close() }
  }, [])
  useEffect(() => { setSelected(0) }, [item.id])
  const image = images[selected] ?? images[0]
  return <dialog ref={dialog} className="initiative__dialog" aria-labelledby="initiative-dialog-title" onCancel={onClose}
    onClick={(event) => { if (event.target === event.currentTarget) onClose() }}>
    <div className="initiative__dialog-inner">
      <header className="initiative__dialog-head"><div><p className="initiative__eyebrow">{initiative.title} initiative</p><h2 id="initiative-dialog-title">{item.title}</h2></div><button type="button" className="initiative__close" onClick={onClose} aria-label="Close record">×</button></header>
      <Status item={item} />
      <Visual item={item} image={image} large />
      <SpecimenProvenance image={image} />
      {images.length > 1 && <div className="initiative__specimen-picker" role="group" aria-label="Choose a specimen">{images.map((specimen, index) =>
        <button key={fileOf(specimen)} type="button" aria-pressed={selected === index} title={specimen.title ?? specimen.label} onClick={() => setSelected(index)}>{specimen.shortLabel ?? (specimen.label ?? specimen.title ?? specimen.date ?? `Specimen ${index + 1}`).slice(commonPrefix.length)}</button>
      )}</div>}
      <p className="initiative__dialog-description">{item.description}</p>
      {item.dateNote && <p className="initiative__date-note">{item.dateNote}</p>}
      {item.domains?.length > 0 && <section><h3>Documented addresses</h3><ul className="initiative__domain-chips">{item.domains.map((domain) => <li key={domain}><code>{domain}</code></li>)}</ul>{initiative.domainNote && <p className="initiative__small">{initiative.domainNote}</p>}</section>}
      {item.registrations?.length > 0 && <details className="initiative__record-details"><summary>Trademark and registration evidence</summary><ul>{item.registrations.map((entry, index) => <li key={`${entry.number}-${index}`}>{entry.territory} · {entry.type} {entry.number}{entry.page ? ` · PDF page ${entry.page}` : ''}</li>)}</ul></details>}
      <Sources references={item.sourceRefs} />
      <Links links={item.links} />
      {image && <a className="initiative__download" href={assetUrl(fileOf(image))} download>Download {fileOf(image).endsWith('.svg') ? (image.evidenceType === 'vector-reconstruction' ? 'reconstructed SVG' : 'source vector') : 'source image'}<span aria-hidden="true">↓</span></a>}
    </div>
  </dialog>
}

const RecordCard = ({ item, onOpen, mark = false, featured = false }) => <article className={`initiative__card ${mark ? 'initiative__card--mark' : ''} ${featured ? 'initiative__card--featured' : ''}`}>
  <button type="button" className="initiative__card-image" onClick={() => onOpen(item)} aria-label={`Explore ${item.title}`}><Visual item={item} /></button>
  <div className="initiative__card-copy"><div className="initiative__card-meta"><span>{item.kind?.replaceAll('-', ' ') ?? (mark ? 'Identity' : 'Record')}</span><Status item={item} /></div>
    <h3><button type="button" onClick={() => onOpen(item)}>{item.title}<Arrow /></button></h3>
    <p>{item.description}</p>
    {item.domains?.[0] && <code className="initiative__card-domain">{item.domains[0]}</code>}
    {mark && <span className="initiative__small">{item.artworkNote ?? (imagesOf(item).length > 1 ? `${imagesOf(item).length} published specimens` : item.artworkStatus === 'native-vector-held' ? 'Original vector paths' : 'Source and date documented')}</span>}
  </div>
</article>

const SectionHeading = ({ section }) => <div className="initiative__section-heading"><div>
  {section.eyebrow && <p className="initiative__eyebrow">{section.eyebrow}</p>}
  <h3>{section.title ?? section.label}</h3>
  {section.description && <p>{section.description}</p>}
</div></div>

const Records = ({ section, onOpen }) => {
  const [filter, setFilter] = useState('all')
  const [query, setQuery] = useState('')
  const records = (section.records ?? []).filter((item) =>
    (filter === 'all' || (filter === 'visual') === Boolean(imagesOf(item).length)) &&
    `${item.title} ${item.description} ${(item.domains ?? []).join(' ')}`.toLowerCase().includes(query.trim().toLowerCase()))
  return <>
    {section.notice && <div className="initiative__notice">{section.notice}</div>}
    {section.searchable && <div className="initiative__toolbar">
      <div className="initiative__filter" role="group" aria-label={`${section.label} evidence filter`}>
        {[['all', 'All records'], ['visual', 'With images'], ['pending', 'Images sought']].map(([id, label]) => <button type="button" key={id} aria-pressed={filter === id} onClick={() => setFilter(id)}>{label}</button>)}
      </div>
      <label className="initiative__search"><span className="initiative__sr-only">Search {section.label.toLowerCase()}</span><input type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search names or domains" /></label>
    </div>}
    {section.searchable && <p className="initiative__small initiative__result-count" aria-live="polite">{records.length} {records.length === 1 ? 'record' : 'records'}</p>}
    <div className={`initiative__cards ${section.layout === 'marks' ? 'initiative__cards--marks' : ''}`}>
      {records.map((item) => <RecordCard key={item.id} item={item} onOpen={onOpen} mark={section.layout === 'marks'} featured={item.id === section.featuredId && filter === 'all' && !query} />)}
    </div>
    {!records.length && <p className="initiative__empty">No records match. Try another name or show all records.</p>}
  </>
}

const Timeline = ({ section }) => <ol className="initiative__timeline">{(section.records ?? []).map((item) =>
  <li key={item.id}><div className="initiative__timeline-date"><strong>{item.date}</strong><span>{item.dateRole?.replaceAll('-', ' ')}</span></div><div className="initiative__timeline-copy"><h4>{item.title}</h4><p>{item.description}</p><Sources references={item.sourceRefs} /></div></li>
)}</ol>

const Publications = ({ section, onOpen }) => <>
  <div className="initiative__publication-grid">{(section.records ?? []).map((item) => <article key={item.id} className="initiative__publication"><p className="initiative__eyebrow">{item.kind?.replaceAll('-', ' ') ?? 'Publication'}</p><h4>{item.title}</h4><p>{item.description}</p><Sources references={item.sourceRefs} /><Links links={item.links} />{imagesOf(item).length > 0 && <button type="button" className="initiative__text-button" onClick={() => onOpen(item)}>View specimen <Arrow /></button>}</article>)}</div>
  {section.leads?.length > 0 && <section className="initiative__leads"><h4>Further research</h4><p>Names and commissioning records to follow up; artwork is not inferred from a name.</p>{section.leads.map((item) => <details key={item.id}><summary>{item.title}</summary><p>{item.description}</p><Sources references={item.sourceRefs} /></details>)}</section>}
</>

const downloadInventory = (inventory, sourceMap) => {
  const blob = new Blob([JSON.stringify({ title: inventory.downloadTitle ?? inventory.title, source: sourceMap.get(inventory.sourceId), entries: inventory.entries }, null, 2) + '\n'], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = inventory.filename ?? 'address-inventory.json'
  anchor.click()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}

const AddressInventory = ({ inventory }) => {
  const { sourceMap } = useInitiative()
  const [query, setQuery] = useState('')
  const [kind, setKind] = useState('all')
  const rows = useMemo(() => inventory.entries.filter((entry) => (kind === 'all' || entry.kind === kind) && `${entry.value} ${entry.family ?? ''} ${entry.note ?? ''}`.toLowerCase().includes(query.trim().toLowerCase())), [inventory, query, kind])
  return <>
    <div className="initiative__register-heading"><div><h4>{inventory.title}</h4><p>{inventory.description}</p></div><button type="button" className="initiative__download" onClick={() => downloadInventory(inventory, sourceMap)}>Download inventory <span aria-hidden="true">↓</span></button></div>
    <div className="initiative__toolbar"><label className="initiative__search"><span className="initiative__sr-only">Search the address inventory</span><input type="search" placeholder="Search the original inventory" value={query} onChange={(event) => setQuery(event.target.value)} /></label><label className="initiative__select">Type<select value={kind} onChange={(event) => setKind(event.target.value)}><option value="all">All entries</option><option value="domain">Domains</option><option value="subdomain">Subdomains</option><option value="email">Email addresses</option></select></label></div>
    <p className="initiative__small" aria-live="polite">{rows.length} matching entries{inventory.matchingNote && ` · ${inventory.matchingNote}`}</p>
    <div className="initiative__table-wrap" role="region" aria-label={inventory.title} tabIndex={0}><table><thead><tr><th scope="col">{inventory.dateLabel ?? 'Listed address'}</th><th scope="col">Type</th><th scope="col">Source page</th><th scope="col">Context</th></tr></thead><tbody>{rows.map((entry) => <tr key={entry.id}><td><code>{entry.printedValue ?? entry.value}</code>{entry.duplicateOf && <small>Repeated in source</small>}</td><td>{entry.kind}</td><td>{entry.page}</td><td>{entry.note || entry.family}</td></tr>)}</tbody></table>{!rows.length && <p className="initiative__empty">No matching inventory entries.</p>}</div>
  </>
}

const SourceRegister = ({ section }) => {
  const { initiative } = useInitiative()
  return <>
    <details className="initiative__source-list"><summary>Source library · {initiative.sources.length} references</summary><ol>{initiative.sources.map((source) => <li key={source.id}>{source.url ? <a href={source.url} target="_blank" rel="noreferrer">{source.title}<Arrow /></a> : <strong>{source.title}</strong>}{source.date && <span>{source.date}</span>}{(source.description || source.note || source.citation) && <p>{source.description ?? source.note ?? source.citation}</p>}</li>)}</ol></details>
    {section.inventory && <AddressInventory inventory={section.inventory} />}
  </>
}

/** A shared explorer; each initiative supplies its own sections, evidence and related pages. */
export const InitiativeDetail = ({ initiative, place, onChange }) => {
  const tabs = useRef(null)
  const { section: current, record: selected, missingRecord } = resolveInitiativeSelection(initiative, place)
  const context = useMemo(() => ({ initiative, sourceMap: new Map(initiative.sources.map((source) => [source.id, source])) }), [initiative])
  const sections = initiative.sections
  const hero = initiative.hero
  const onTabKey = (event) => {
    const index = sections.findIndex((section) => section.id === current?.id)
    const next = event.key === 'ArrowRight' ? (index + 1) % sections.length : event.key === 'ArrowLeft' ? (index + sections.length - 1) % sections.length : event.key === 'Home' ? 0 : event.key === 'End' ? sections.length - 1 : null
    if (next === null) return
    event.preventDefault()
    onChange(sections[next].id)
    tabs.current?.querySelectorAll('[role="tab"]')[next]?.focus()
  }
  return <InitiativeContext.Provider value={context}><section className="initiative-detail" aria-label={`${initiative.title} initiative`}>
    <div className={`initiative__hero ${!hero.image ? 'initiative__hero--text' : ''}`}>
      <div className="initiative__hero-copy"><p className="initiative__eyebrow">{hero.eyebrow}</p><h2>{hero.title}</h2><p>{hero.description}</p>
        {initiative.stats?.length > 0 && <div className="initiative__hero-stats">{initiative.stats.map((stat) => <span key={stat.label}><strong>{stat.value}</strong>{stat.label}</span>)}</div>}
      </div>
      {hero.image && <div className={`initiative__hero-art ${hero.image.darkBackground ? 'initiative__hero-art--dark' : ''}`}><img src={assetUrl(fileOf(hero.image))} alt={hero.image.alt ?? initiative.title} />{hero.caption && <span>{hero.caption}</span>}</div>}
    </div>
    <div ref={tabs} className="initiative__tabs" role="tablist" aria-label={`${initiative.title} initiative sections`} onKeyDown={onTabKey}>{sections.map((section) => <button type="button" role="tab" id={`initiative-tab-${section.id}`} aria-controls={`initiative-panel-${section.id}`} aria-selected={current?.id === section.id} tabIndex={current?.id === section.id ? 0 : -1} key={section.id} onClick={() => onChange(section.id)}>{section.label}</button>)}</div>
    {missingRecord && <p className="initiative__notice" role="status">That record is not in this initiative. <button className="initiative__text-button" type="button" onClick={() => onChange(current?.id)}>Browse the available records</button></p>}
    {sections.map((section) => <div key={section.id} className="initiative__panel" role="tabpanel" id={`initiative-panel-${section.id}`} aria-labelledby={`initiative-tab-${section.id}`} tabIndex={0} hidden={current?.id !== section.id}>
      {current?.id === section.id && <>
        <SectionHeading section={section} />
        {section.type === 'records' && <Records section={section} onOpen={(item) => onChange(section.id, item.id)} />}
        {section.type === 'timeline' && <Timeline section={section} />}
        {section.type === 'publications' && <Publications section={section} onOpen={(item) => onChange(section.id, item.id)} />}
        {section.type === 'sources' && <SourceRegister section={section} />}
      </>}
    </div>)}
    {initiative.relatedLinks?.length > 0 && <nav className="initiative__related" aria-label="Related pages"><span>Continue exploring</span>{initiative.relatedLinks.map((link) => <SiteLink key={link.label} to={link.to}>{link.label}<Arrow /></SiteLink>)}</nav>}
    {selected && <SpecimenDialog key={selected.id} item={selected} onClose={() => onChange(current?.id)} />}
  </section></InitiativeContext.Provider>
}
