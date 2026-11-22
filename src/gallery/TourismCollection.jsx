import { useEffect, useMemo, useRef, useState } from 'react'
import { TOURISM_COLLECTION } from './tourismData.js'
import { assetUrl } from './collectedCollections.js'
import './tourismCollection.css'

const TABS = [
  { id: 'websites', label: 'Websites & apps' },
  { id: 'marks', label: 'Logos & signs' },
  { id: 'timeline', label: 'Timeline' },
  { id: 'publications', label: 'Publications' },
  { id: 'sources', label: 'Sources & domains' }
]
const DATA = TOURISM_COLLECTION
const SOURCES = new Map(DATA.sources.map((source) => [source.id, source]))
const fileOf = (image) => typeof image === 'string' ? image : image?.file
const imagesOf = (item) => [...new Map([item.image, ...(item.images ?? []), ...(item.specimens ?? []), ...(item.variants ?? [])]
  .filter((image) => fileOf(image)).map((image) => [fileOf(image), image])).values()]
const sourceUrl = (source, reference) => {
  const url = new URL(reference.url ?? source.url)
  if (reference.page && (/\.pdf$/i.test(url.pathname) || url.pathname.includes('/hmo/'))) url.hash = `page=${reference.page}`
  return url.href
}
const readPlace = () => {
  const [tab, item] = (globalThis.location?.hash ?? '').replace(/^#tourism-/, '').split('/')
  return { tab: TABS.some((entry) => entry.id === tab) ? tab : 'websites', item: item ?? null }
}

const Arrow = () => <svg className="tourism__link-icon" aria-hidden="true" width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M2 10 10 2M3 2h7v7" stroke="currentColor" strokeWidth="1.2" /></svg>
const Sources = ({ references = [], className = '', label = 'Sources' }) => references.length > 0 && (
  <ul className={`tourism__references ${className}`} aria-label={label}>
    {references.map((reference, index) => {
      const source = SOURCES.get(reference.sourceId)
      if (!source) return null
      return <li key={`${reference.sourceId}-${reference.page ?? index}`}>
        <a href={sourceUrl(source, reference)} target="_blank" rel="noreferrer">{source.shortTitle ?? source.title}<Arrow /></a>
        {(reference.page || reference.locator) && <span>{reference.locator ?? `PDF page ${reference.page}`}</span>}
      </li>
    })}
  </ul>
)
const SPECIMEN_TYPES = {
  'native-pdf-vector-extraction': 'Native vector from publication',
  'printed-source-crop': 'Crop from the printed source',
  'original-published-image': 'Original publisher image',
  'official-published-website-screenshot': 'Published website screenshot',
  'official-published-website-image': 'Published website image'
}
const SpecimenProvenance = ({ image }) => image && typeof image !== 'string' && (
  <section className="tourism__specimen-provenance" aria-label="Selected specimen provenance">
    <p className="tourism__small"><strong>{SPECIMEN_TYPES[image.evidenceType] ?? 'Published specimen'}</strong>
      {image.date && <><br /><time dateTime={image.date}>{image.date}</time>{image.dateLabel && <> · {image.dateLabel}</>}</>}
      {!image.date && image.dateLabel && <><br />{image.dateLabel}</>}
    </p>
    <Sources label="Selected specimen source" references={[{
      sourceId: image.sourceId,
      url: image.sourceUrl,
      page: image.sourcePage,
      locator: image.sourceLocator
    }]} />
    {image.sourceImageUrl && <p className="tourism__small"><a href={image.sourceImageUrl} target="_blank" rel="noreferrer">Original image at the publisher<Arrow /></a></p>}
  </section>
)
const Status = ({ item }) => <span className={`tourism__status ${imagesOf(item).length ? 'tourism__status--visual' : ''}`}>
  <span aria-hidden="true" />{imagesOf(item).length ? 'Visual specimen' : item.statusLabel ?? 'Documented · image sought'}
</span>

const Visual = ({ item, image = imagesOf(item)[0], large = false }) => image
  ? <figure className={`tourism__visual ${large ? 'tourism__visual--large' : ''} ${image.darkBackground ? 'tourism__visual--dark' : ''}`}>
      <img src={assetUrl(fileOf(image))} alt={image.alt ?? item.title} width={image.width} height={image.height} loading="lazy" />
      {large && <figcaption>{image.caption ?? image.label ?? 'Published specimen; see the source record below.'}</figcaption>}
    </figure>
  : <div className="tourism__unrecovered">
      <svg width="48" height="42" viewBox="0 0 48 42" fill="none" aria-hidden="true"><rect x="2" y="3" width="44" height="33" rx="3" stroke="currentColor" strokeWidth="1.5" /><path d="M2 11h44M9 7h1m4 0h1m4 0h1M15 23h18M19 28h10" stroke="currentColor" strokeWidth="1.5" /></svg>
      <span>{item.kind?.includes('app') ? 'App imagery sought' : 'Visual specimen sought'}</span>
      <small>Documentary evidence is available</small>
    </div>

const Links = ({ links = [] }) => links.length > 0 && <ul className="tourism__links">{links.map((link, index) =>
  <li key={`${link.url}-${index}`}><a href={link.url} target={link.url.startsWith('#') || link.url.startsWith('?') ? undefined : '_blank'} rel="noreferrer">{link.label}<Arrow /></a>{link.note && <small>{link.note}</small>}</li>
)}</ul>

const SpecimenDialog = ({ item, onClose }) => {
  const dialog = useRef(null)
  const [selected, setSelected] = useState(0)
  const images = imagesOf(item)
  useEffect(() => {
    const element = dialog.current
    element?.showModal()
    return () => { if (element?.open) element.close() }
  }, [])
  useEffect(() => { setSelected(0) }, [item.id])
  const image = images[selected] ?? images[0]
  return <dialog ref={dialog} className="tourism__dialog" aria-labelledby="tourism-dialog-title" onCancel={onClose}
    onClick={(event) => { if (event.target === event.currentTarget) onClose() }}>
    <div className="tourism__dialog-inner">
      <header className="tourism__dialog-head"><div><p className="tourism__eyebrow">Tourism collection</p><h2 id="tourism-dialog-title">{item.title}</h2></div><button type="button" className="tourism__close" onClick={onClose} aria-label="Close record">×</button></header>
      <Status item={item} />
      <Visual item={item} image={image} large />
      <SpecimenProvenance image={image} />
      {images.length > 1 && <div className="tourism__specimen-picker" role="group" aria-label="Choose a specimen">{images.map((specimen, index) =>
        <button key={fileOf(specimen)} type="button" aria-pressed={selected === index} title={specimen.title} onClick={() => setSelected(index)}>{(specimen.label ?? specimen.title ?? specimen.date ?? `Specimen ${index + 1}`).replace(/^Super, Natural British Columbia — /, '').replace(' with Canada', '')}</button>
      )}</div>}
      <p className="tourism__dialog-description">{item.description}</p>
      {item.dateNote && <p className="tourism__date-note">{item.dateNote}</p>}
      {item.domains?.length > 0 && <section><h3>Documented addresses</h3><ul className="tourism__domain-chips">{item.domains.map((domain) => <li key={domain}><code>{domain}</code></li>)}</ul><p className="tourism__small">A listed address documents the name held in 2013; it does not establish a separate website or its launch date.</p></section>}
      {item.registrations?.length > 0 && <details className="tourism__record-details"><summary>Trademark and registration evidence</summary><ul>{item.registrations.map((entry, index) => <li key={`${entry.number}-${index}`}>{entry.territory} · {entry.type} {entry.number}{entry.page ? ` · PDF page ${entry.page}` : ''}</li>)}</ul></details>}
      <Sources references={item.sourceRefs} />
      <Links links={item.links} />
      {image && <a className="tourism__download" href={assetUrl(fileOf(image))} download>Download {fileOf(image).endsWith('.svg') ? 'source vector' : 'source image'}<span aria-hidden="true">↓</span></a>}
    </div>
  </dialog>
}

const RecordCard = ({ item, onOpen, mark = false, featured = false }) => <article className={`tourism__card ${mark ? 'tourism__card--mark' : ''} ${featured ? 'tourism__card--featured' : ''}`}>
  <button type="button" className="tourism__card-image" onClick={() => onOpen(item)} aria-label={`Explore ${item.title}`}><Visual item={item} /></button>
  <div className="tourism__card-copy"><div className="tourism__card-meta"><span>{item.kind?.replaceAll('-', ' ') ?? (mark ? 'Identity' : 'Digital service')}</span><Status item={item} /></div>
    <h3><button type="button" onClick={() => onOpen(item)}>{item.title}<Arrow /></button></h3>
    <p>{item.description}</p>
    {item.domains?.[0] && <code className="tourism__card-domain">{item.domains[0]}</code>}
    {mark && <span className="tourism__small">{imagesOf(item).length > 1 ? `${imagesOf(item).length} published specimens` : item.artworkStatus === 'native-vector-held' ? 'Original vector paths' : 'Source and date documented'}</span>}
  </div>
</article>

const Websites = ({ onOpen }) => {
  const [filter, setFilter] = useState('all')
  const [query, setQuery] = useState('')
  const records = DATA.digitalRecords.filter((item) => (filter === 'all' || (filter === 'visual') === Boolean(imagesOf(item).length)) && `${item.title} ${item.description} ${(item.domains ?? []).join(' ')}`.toLowerCase().includes(query.trim().toLowerCase()))
  return <><div className="tourism__section-heading"><div><p className="tourism__eyebrow">Digital collection</p><h3>Websites, apps & campaigns</h3><p>How British Columbia welcomed visitors online. Open a record for its specimens, dates and sources.</p></div></div>
    <div className="tourism__toolbar"><div className="tourism__filter" role="group" aria-label="Website evidence filter">{[['all', 'All records'], ['visual', 'With images'], ['pending', 'Images sought']].map(([id, label]) => <button type="button" key={id} aria-pressed={filter === id} onClick={() => setFilter(id)}>{label}</button>)}</div><label className="tourism__search"><span className="tourism__sr-only">Search websites and apps</span><input type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search names or domains" /></label></div>
    <p className="tourism__small tourism__result-count" aria-live="polite">{records.length} {records.length === 1 ? 'record' : 'records'}</p>
    <div className="tourism__cards">{records.map((item) => <RecordCard key={item.id} item={item} onOpen={onOpen} featured={item.id === 'hellobc' && filter === 'all' && !query} />)}</div>
    {!records.length && <p className="tourism__empty">No records match. Try another name or show all records.</p>}
  </>
}

const Marks = ({ onOpen }) => <><div className="tourism__section-heading"><div><p className="tourism__eyebrow">Visual identity</p><h3>One family, many applications</h3><p>Original vector specimens and printed references, connected to the services that used them.</p></div></div>
  <div className="tourism__notice"><strong>Read the specimen’s label.</strong> Native vector artwork, scanned source crops and names awaiting artwork retain their own evidence. A 2013 listing is not a design’s creation date.</div>
  <div className="tourism__cards tourism__cards--marks">{DATA.marks.map((item) => <RecordCard key={item.id} item={item} onOpen={onOpen} mark />)}</div>
</>

const Timeline = () => <><div className="tourism__section-heading"><div><p className="tourism__eyebrow">Continuity & change</p><h3>The brands and their custodians</h3><p>Website launches, published specimens and organizational changes are different kinds of dates.</p></div></div>
  <ol className="tourism__timeline">{DATA.timeline.map((item) => <li key={item.id}><div className="tourism__timeline-date"><strong>{item.date}</strong><span>{item.dateRole?.replaceAll('-', ' ')}</span></div><div className="tourism__timeline-copy"><h4>{item.title}</h4><p>{item.description}</p><Sources references={item.sourceRefs} /></div></li>)}</ol>
</>

const Publications = ({ onOpen }) => <><div className="tourism__section-heading"><div><p className="tourism__eyebrow">Printed & moving images</p><h3>Publications and creative work</h3><p>Standards, guides and commissioning records connect the digital collection to its printed history.</p></div></div>
  <div className="tourism__publication-grid">{DATA.publications.map((item) => <article key={item.id} className="tourism__publication"><p className="tourism__eyebrow">{item.kind?.replaceAll('-', ' ') ?? 'Publication'}</p><h4>{item.title}</h4><p>{item.description}</p><Sources references={item.sourceRefs} /><Links links={item.links} />{imagesOf(item).length > 0 && <button type="button" className="tourism__text-button" onClick={() => onOpen(item)}>View specimen →</button>}</article>)}</div>
  {DATA.leads?.length > 0 && <section className="tourism__leads"><h4>Further research</h4><p>Names and commissioning records to follow up; artwork is not inferred from a name.</p>{DATA.leads.map((item) => <details key={item.id}><summary>{item.title}</summary><p>{item.description}</p><Sources references={item.sourceRefs} /></details>)}</section>}
</>

const downloadInventory = () => {
  const blob = new Blob([JSON.stringify({ title: 'Tourism BC 2013 address inventory', source: SOURCES.get('mo-68-2013'), entries: DATA.domains }, null, 2) + '\n'], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = 'tourism-bc-2013-address-inventory.json'
  anchor.click()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}

const SourceRegister = () => {
  const [query, setQuery] = useState('')
  const [kind, setKind] = useState('all')
  const rows = useMemo(() => DATA.domains.filter((entry) => (kind === 'all' || entry.kind === kind) && `${entry.value} ${entry.family} ${entry.note ?? ''}`.toLowerCase().includes(query.trim().toLowerCase())), [query, kind])
  return <><div className="tourism__section-heading"><div><p className="tourism__eyebrow">The evidence</p><h3>A source for every record</h3><p>The 2013 transfer order anchors this collection; later sources document the services and their changing appearance.</p></div></div>
    <details className="tourism__source-list"><summary>Source library · {DATA.sources.length} references</summary><ol>{DATA.sources.map((source) => <li key={source.id}><a href={source.url} target="_blank" rel="noreferrer">{source.title}<Arrow /></a>{source.date && <span>{source.date}</span>}{(source.description || source.note) && <p>{source.description ?? source.note}</p>}</li>)}</ol></details>
    <div className="tourism__register-heading"><div><h4>The 2013 address inventory</h4><p>{DATA.domains.length} listed entries, including aliases, technical hosts, duplicates and email addresses.</p></div><button type="button" className="tourism__download" onClick={downloadInventory}>Download inventory <span aria-hidden="true">↓</span></button></div>
    <div className="tourism__toolbar"><label className="tourism__search"><span className="tourism__sr-only">Search the address inventory</span><input type="search" placeholder="Search the original inventory" value={query} onChange={(event) => setQuery(event.target.value)} /></label><label className="tourism__select">Type<select value={kind} onChange={(event) => setKind(event.target.value)}><option value="all">All entries</option><option value="domain">Domains</option><option value="subdomain">Subdomains</option><option value="email">Email addresses</option></select></label></div>
    <p className="tourism__small" aria-live="polite">{rows.length} matching entries · spelling retained from the printed schedule</p>
    <div className="tourism__table-wrap" role="region" aria-label="2013 address inventory" tabIndex={0}><table><thead><tr><th scope="col">As listed in 2013</th><th scope="col">Type</th><th scope="col">Source page</th><th scope="col">Context</th></tr></thead><tbody>{rows.map((entry) => <tr key={entry.id}><td><code>{entry.printedValue ?? entry.value}</code>{entry.duplicateOf && <small>Repeated in source</small>}</td><td>{entry.kind}</td><td>{entry.page}</td><td>{entry.note || entry.family}</td></tr>)}</tbody></table>{!rows.length && <p className="tourism__empty">No matching inventory entries.</p>}</div>
  </>
}

/** The catalogue lives inside the existing tourism logo collection, with shareable sections. */
export const TourismCollection = () => {
  const [place, setPlace] = useState(readPlace)
  const tabs = useRef(null)
  const allItems = [...DATA.digitalRecords, ...DATA.marks, ...DATA.publications]
  const selected = allItems.find((item) => item.id === place.item)
  const hero = DATA.marks.flatMap(imagesOf).find((item) => item.id === 'super-natural-canada-stacked-spot-2005')
  useEffect(() => {
    const read = () => setPlace(readPlace())
    globalThis.addEventListener('hashchange', read)
    globalThis.addEventListener('popstate', read)
    return () => { globalThis.removeEventListener('hashchange', read); globalThis.removeEventListener('popstate', read) }
  }, [])
  const change = (tab, item = null) => {
    setPlace({ tab, item })
    const url = new URL(globalThis.location.href)
    url.hash = `tourism-${tab}${item ? `/${item}` : ''}`
    globalThis.history.replaceState(globalThis.history.state, '', url)
  }
  const onTabKey = (event) => {
    const index = TABS.findIndex((tab) => tab.id === place.tab)
    const next = event.key === 'ArrowRight' ? (index + 1) % TABS.length : event.key === 'ArrowLeft' ? (index + TABS.length - 1) % TABS.length : event.key === 'Home' ? 0 : event.key === 'End' ? TABS.length - 1 : null
    if (next === null) return
    event.preventDefault()
    change(TABS[next].id)
    tabs.current?.querySelectorAll('[role="tab"]')[next]?.focus()
  }
  return <section className="tourism" aria-label="Tourism websites and visual history">
    <div className="tourism__hero"><div className="tourism__hero-copy"><p className="tourism__eyebrow">Tourism BC & Destination BC</p><h2>Tourism, on screen<br />and in print.</h2><p>Explore the websites, identities and campaigns that introduced British Columbia to the world, with the original artwork and records behind them.</p><div className="tourism__hero-stats"><span><strong>{DATA.digitalRecords.length}</strong> digital records</span><span><strong>{DATA.marks.length}</strong> identity records</span><span><strong>{DATA.domains.length}</strong> listed addresses</span></div></div><div className="tourism__hero-art">{hero && <img src={assetUrl(fileOf(hero))} alt="Super, Natural British Columbia Canada — published 2005 identity" />}<span>From the published 2005 graphic standards</span></div></div>
    <div ref={tabs} className="tourism__tabs" role="tablist" aria-label="Tourism collection sections" onKeyDown={onTabKey}>{TABS.map((tab) => <button type="button" role="tab" id={`tourism-tab-${tab.id}`} aria-controls={`tourism-panel-${tab.id}`} aria-selected={place.tab === tab.id} tabIndex={place.tab === tab.id ? 0 : -1} key={tab.id} onClick={() => change(tab.id)}>{tab.label}</button>)}</div>
    {TABS.map((tab) => <div key={tab.id} className="tourism__panel" role="tabpanel" id={`tourism-panel-${tab.id}`} aria-labelledby={`tourism-tab-${tab.id}`} tabIndex={0} hidden={place.tab !== tab.id}>
      {place.tab === tab.id && <>
        {tab.id === 'websites' && <Websites onOpen={(item) => change(tab.id, item.id)} />}
        {tab.id === 'marks' && <Marks onOpen={(item) => change(tab.id, item.id)} />}
        {tab.id === 'timeline' && <Timeline />}
        {tab.id === 'publications' && <Publications onOpen={(item) => change(tab.id, item.id)} />}
        {tab.id === 'sources' && <SourceRegister />}
      </>}
    </div>)}
    <div className="tourism__related"><span>Continue exploring</span><a href="?view=signs&sign=super-natural">Super, Natural welcome sign<Arrow /></a><a href="?view=government&node=tourism-bc">Tourism BC in government<Arrow /></a><a href="?view=government&node=destination-bc">Destination BC in government<Arrow /></a></div>
    {selected && <SpecimenDialog key={selected.id} item={selected} onClose={() => change(place.tab)} />}
  </section>
}

export const TourismCollectionTeaser = () => <a className="tourism__teaser" href="?view=gallery&logos=tourism-bc-destination-bc#tourism-websites"><span>Tourism BC & Destination BC</span><strong>Explore websites, campaigns and the wider identity family →</strong></a>
